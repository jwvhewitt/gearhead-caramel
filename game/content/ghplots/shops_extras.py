import game.ghdialogue.ghgrammar
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, ghrooms, ghcutscene
from .lancemates import LMSkillsSelfIntro, get_hire_cost


#   ************************
#   ***  HOSPITAL_BONUS  ***
#   ************************
#
# Some kind of extra content that can be found in a tavern.
#
# Elements: LOCALE, INTERIOR, SHOPKEEPER
#

class RecoveringCavalier(Plot):
    LABEL = "HOSPITAL_BONUS"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(10, 40),random.randint(10, 40)),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["LOCALE"].attributes),
                                              combatant=True, can_cyberize=True)

        # This person gets a bonus to cyberware, vitality, or dodge.
        npc.statline[random.choice([gears.stats.Cybertech, gears.stats.Vitality, gears.stats.Dodge])] += random.randint(1,6)

        self.register_element("NPC", npc, dident="INTERIOR")
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                if npc.get_reaction_score(camp.pc, camp) > 60:
                    mylist.append(Offer("[IWOULDLOVETO] [THANKS_FOR_CHOOSING_ME]",
                                        context=ContextTag((context.PROPOSAL, context.JOIN)),
                                        data={"subject": "joining my lance"},
                                        effect=self._join_lance
                                        ))
                else:
                    mylist.append(Offer("My regular signing rate is ${}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                                        context=ContextTag((context.PROPOSAL, context.JOIN)),
                                        data={"subject": "joining my lance"},
                                        subject=self, subject_start=True,
                                        ))
                    mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                        context=ContextTag((context.DENY, context.JOIN)), subject=self
                                        ))
                    if camp.credits >= self.hire_cost:
                        mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                            context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                            effect=self._pay_to_join
                                            ))
                mylist.append(Offer(
                    "[HELLO] I got pretty badly messed up on my last mission, so now I'm here.", context=ContextTag((context.HELLO,))
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] Be careful out there... I wouldn't be in this hospital if I had been.",
                    context=ContextTag((context.HELLO,))
                ))
            mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _pay_to_join(self, camp):
        camp.credits -= self.hire_cost
        self._join_lance(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class HospitalHopelessCase(Plot):
    LABEL = "HOSPITAL_BONUS"
    active = True
    scope = "INTERIOR"
    UNIQUE = True

    def custom_init(self, nart):
        patient_room = self.register_element('ROOM', pbge.randmaps.rooms.ClosedRoom(),
                                      dident="INTERIOR")

        patient = self.register_element("PATIENT", gears.selector.random_character(rank=self.rank, local_tags=self.elements["LOCALE"].attributes))

        patient_bed = self.register_element('PATIENT_BED', ghwaypoints.OccupiedBed(name="{}'s Bed".format(patient), plot_locked=True, anchor=pbge.randmaps.anchors.middle), dident="ROOM")

        nurse = self.register_element("NURSE", gears.selector.random_character(rank=self.rank, local_tags=self.elements["LOCALE"].attributes, job=gears.jobs.ALL_JOBS["Nurse"]), dident="ROOM")

        self.cured_patient = False
        self.party_doctor = None
        self.register_element("DISEASE", plotutility.random_disease_name())
        self.got_reward = False
        return True

    def PATIENT_BED_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if not self.cured_patient:
            thingmenu.desc = "{PATIENT} lies unconscious in this bed, a victim of {DISEASE}. It is unknown how much time {PATIENT.gender.subject_pronoun} has left.".format(**self.elements)
            lm = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Medicine, gears.stats.DIFFICULTY_LEGENDARY, no_random=True)
            if lm:
                self.party_doctor = lm
                if lm is camp.pc:
                    thingmenu.add_item("You believe {PATIENT} can be saved. Offer the doctors a second opinion.".format(**self.elements), self._cure_disease)
                else:
                    thingmenu.items.append(
                        ghdialogue.ghdview.LancemateConvoItem("This is the wrong treatment for {DISEASE}... Let's talk to the doctors, I can save {PATIENT.gender.object_pronoun}.".format(**self.elements), self._cure_disease, desc=None, menu=thingmenu, npc=lm))
            thingmenu.add_item("Leave {PATIENT} in peace.".format(**self.elements), None)
        else:
            thingmenu.desc = "The bed is empty now. Maybe someone else will need it later."

    def _cure_disease(self, camp: gears.GearHeadCampaign):
        nurse = self.elements["NURSE"]
        if nurse in camp.scene.contents:
            ghcutscene.SimpleMonologueDisplay("We have tried all we can here. If you know of another treatment, then please do what you can.", nurse)(camp)
        if self.party_doctor is camp.pc:
            pbge.alert("You attempt emergency treatment for {PATIENT}'s {DISEASE}.".format(**self.elements))
        else:
            pbge.alert("{LM} attempts emergency treatment for {PATIENT}'s {DISEASE}.".format(LM=self.party_doctor, **self.elements))
        pbge.alert("The treatment is successful!")
        self.cured_patient = True
        mybed = self.elements["PATIENT_BED"]
        mybed.get_out_of_bed()
        camp.scene.place_gears_near_spot(*mybed.pos, camp.scene.civilian_team, self.elements["PATIENT"])
        camp.dole_xp(200)

    def NURSE_offers(self, camp):
        mylist = list()

        if not self.cured_patient:
            mylist.append(Offer("[HELLO] {PATIENT} is being treated for {DISEASE}, but the case seems hopeless.".format(**self.elements),
                                context=ContextTag([context.HELLO]),
                                ))
            mylist.append(Offer("We've tried all the treatments we know here... maybe if you could find a medical expert with knowledge of this disease.".format(**self.elements),
                                context=ContextTag([context.CUSTOM]), subject=str(self.elements["PATIENT"]),
                                data={"reply": "Is there anything I could do to help?"}
                                ))
        elif not self.got_reward and self.elements["NURSE"].combatant and not self.elements["PATIENT"].combatant:
            mylist.append(Offer("You did it- you saved {PATIENT}! I don't have much to do around here anymore, so if you ever need a nurse on your team just ask.".format(**self.elements),
                                context=ContextTag([context.HELLO]), effect=self._nurse_joins
                                ))
        else:
            mylist.append(Offer("[HELLO] Thank you so much for saving {PATIENT}!".format(**self.elements),
                                context=ContextTag([context.HELLO])
                                ))

        return mylist

    def _nurse_joins(self, camp: gears.GearHeadCampaign):
        nurse = self.elements["NURSE"]
        nurse_r = camp.get_relationship(nurse)
        nurse_r.tags.add(gears.relationships.RT_LANCEMATE)
        nurse_r.reaction_mod += 15
        self.got_reward = True

    def PATIENT_offers(self, camp):
        mylist = list()
        if not self.got_reward:
            if self.elements["PATIENT"].combatant:
                mylist.append(Offer("I heard that you're responsible for curing my {DISEASE}. After I'm feeling better, if you need a {PATIENT.job} on your lance, come back and ask.".format(**self.elements),
                                    context=ContextTag([context.HELLO]), effect=self._patient_joins
                                    ))

            else:
                mylist.append(Offer("I heard that you're responsible for curing my {DISEASE}. I'll let everyone know about the wonderful thing you did!".format(**self.elements),
                                    context=ContextTag([context.HELLO]), effect=self._patient_thanks
                                    ))

        else:
            mylist.append(Offer("[HELLO] I'll never forget what you did for me!".format(**self.elements),
                                context=ContextTag([context.HELLO])
                                ))

        return mylist

    def _patient_joins(self, camp: gears.GearHeadCampaign):
        patient = self.elements["PATIENT"]
        patient_r = camp.get_relationship(patient)
        patient_r.tags.add(gears.relationships.RT_LANCEMATE)
        patient_r.history.append(gears.relationships.Memory(
            "you cured me of {DISEASE}".format(**self.elements),
            "I cured you of {DISEASE}".format(**self.elements),
            25, (gears.relationships.MEM_AidedByPC,)
        ))
        patient_r.attitude = gears.relationships.A_THANKFUL
        camp.egg.dramatis_personae.add(patient)
        self.got_reward = True

    def _patient_thanks(self, camp: gears.GearHeadCampaign):
        metro = camp.scene.get_metro_scene()
        if metro and metro.metrodat:
            metro.metrodat.local_reputation += 25
        self.got_reward = True



#   **********************
#   ***  TAVERN_BONUS  ***
#   **********************
#
# Some kind of resource or good thing that can be found in a tavern.
#
# Elements: INTERIOR
#

class UtterlyRandomTavernLancemate(Plot):
    LABEL = "TAVERN_BONUS"

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(10, 40),random.randint(10, 40)),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["LOCALE"].attributes),
                                              combatant=True)

        # Add a random specialty.
        npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS + gears.stats.EXTRA_COMBAT_SKILLS)] += random.randint(1,6)

        self.register_element("NPC", npc, dident="INTERIOR")
        self.add_sub_plot(nart, "RLM_Relationship", elements={"NPC_SCENE": self.elements["INTERIOR"]})
        return True


class BattleScarredVeteran(Plot):
    # An older cavalier is hanging out at the tavern.
    LABEL = "TAVERN_BONUS"

    active = True
    scope = "INTERIOR"
    UNIQUE = True

    COMBAT_STATS = (gears.stats.Reflexes, gears.stats.Body, gears.stats.Body, gears.stats.Speed)

    def custom_init(self, nart):
        # Create the veteran
        npc: gears.base.Character = self.register_element("NPC", gears.selector.random_character(
            random.randint(41, 75), local_tags=self.elements["LOCALE"].attributes, can_cyberize=True, camp=nart.camp,
            job=gears.jobs.ALL_JOBS["Mecha Pilot"], age=random.randint(42,64)), dident="INTERIOR")

        # Battle-scarred: reduce Charm to increase combat stats.
        max_charm = random.randint(2,6)
        while npc.statline[gears.stats.Charm] > max_charm:
            npc.statline[gears.stats.Charm] -= 1
            npc.statline[random.choice(self.COMBAT_STATS)] += 1
            npc.statline[random.choice(self.COMBAT_STATS)] += 1
        npc.statline[gears.stats.Cybertech] = random.randint(4,8)

        self.shop = services.SkillTrainer(gears.stats.FUNDAMENTAL_COMBATANT_SKILLS)
        self.shop_counter = 0

        return True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]

        if camp.renown > npc.renown and self.shop_counter > 2 and npc.get_reaction_score(camp.pc, camp) > 20:
            mylist.append(Offer("[HELLO] You know, I think you have learned all that it is possible for me to teach. I wish I could leave this place and return to active duty.",
                                context=ContextTag((context.HELLO,)),
                                subject=self, subject_start=True,
                                ))

            if camp.can_add_lancemate():
                mylist.append(Offer("I can't wait to be adventuring again. [LETSGO]",
                                    context=ContextTag((context.CUSTOM,)), subject=self, effect=self._join_lance,
                                    data={"reply": "It would be an honor to have you in my lance."}
                                    ))

            mylist.append(plotutility.LMSkillsSelfIntro(npc))

        mylist.append(Offer("[HELLO] I have many years of experience as a cavalier... if you want, I could help you to improve your skills.",
                            context=ContextTag((context.HELLO,)),
                            ))

        mylist.append(Offer("The secret to living a long life is to always be more prepared than your opponent.",
                            context=ContextTag((context.OPEN_SCHOOL,)), effect=self._start_training
                            ))

        return mylist

    def _start_training(self, camp):
        self.shop_counter += 1
        self.shop(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class MeanLookingMercenary(Plot):
    # A mean looking mercenary is hanging out at the tavern.
    LABEL = "TAVERN_BONUS"

    active = True
    scope = "INTERIOR"
    UNIQUE = True

    def custom_init(self, nart):
        # Create the mercenary
        npc: gears.base.Character = self.register_element("NPC", gears.selector.random_character(
            self.rank + random.randint(1,10), local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Mercenary"]), dident="INTERIOR")

        # Mean-looking: Trade Charm for Ego
        ego_shift = random.randint(3,6)
        npc.statline[gears.stats.Ego] += ego_shift
        npc.statline[gears.stats.Charm] = max(npc.statline[gears.stats.Charm]-ego_shift, random.randint(2,4))

        return True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = (npc.renown * npc.renown * (150 - npc.get_reaction_score(camp.pc, camp)))//5

        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("I'll join your lance for a mere ${}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                                    context=ContextTag((context.PROPOSAL, context.JOIN)),
                                    data={"subject": "joining my lance"},
                                    subject=self, subject_start=True,
                                    ))
                mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                    context=ContextTag((context.DENY, context.JOIN)), subject=self
                                    ))
                if camp.credits >= self.hire_cost:
                    mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                        context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                        effect=self._join_lance
                                        ))

            mylist.append(plotutility.LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class TavernSmuggler(Plot):
    # A smuggler who hangs out at the tavern, not a smuggler who smuggles taverns. Though with the right mecha that'd
    # be possible.
    LABEL = "TAVERN_BONUS"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Smuggler"]), dident="INTERIOR")

        self.shopname = "{}'s Contraband".format(npc1)
        self.shop = services.Shop(npc=npc1, ware_types=services.BLACK_MARKET, rank=self.rank + random.randint(1,50),
                                  buy_stolen_items=True)

        self.shop_unlocked = False
        self.shop_forever_locked = False

        return True

    def SHOPKEEPER_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if self.shop_unlocked:
            mylist.append(Offer("[OPENSHOP]",
                                context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                                data={"shop_name": self.shopname, "wares": "stuff"},
                                ))
        elif not self.shop_forever_locked:
            if camp.party_has_tag(gears.tags.Criminal):
                mylist.append(Offer("[HELLO] You look like the type who might be interested in some under-the-counter goods, if you catch my meaning.",
                                    context=ContextTag([context.HELLO]), subject=self, subject_start=True,
                                    allow_generics=False
                                    ))
            elif self.elements["SHOPKEEPER"].get_reaction_score(camp.pc, camp) > 40:
                mylist.append(Offer("[HELLO] I have come into the possession of a number of valuable items, and since I like you I'd be willing to let you buy them for a steal.",
                                    context=ContextTag([context.HELLO]), subject=self, subject_start=True,
                                    allow_generics=False
                                    ))

            mylist.append(Offer(
                "That would be my pleasure.",
                context=ContextTag([context.CUSTOM]), subject=self, effect=self._unlock_shop,
                data={"reply": "Show me what you've got."}
            ))

            mylist.append(Offer(
                "Come back anytime. I'm always getting new items in.",
                context=ContextTag([context.CUSTOM]), subject=self,
                data={"reply": "Not right now, thanks."}
            ))

            mylist.append(Offer(
                "That's a shame. Well, I won't bother you about it again.",
                context=ContextTag([context.CUSTOM]), subject=self, effect=self._lock_shop,
                data={"reply": "I want no part of your criminal dealings."}
            ))

        return mylist

    def _unlock_shop(self, camp):
        self.shop_unlocked = True
        self.shop(camp)

    def _lock_shop(self, camp: gears.GearHeadCampaign):
        self.shop_forever_locked = True
        for npc in camp.get_lancemates():
            mytags = npc.get_tags()
            if gears.tags.Police in mytags or gears.personality.Justice in mytags:
                npc.relationship.reaction_mod += random.randint(5,10)

