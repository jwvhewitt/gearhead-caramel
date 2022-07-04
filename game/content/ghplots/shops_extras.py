import game.ghdialogue.ghgrammar
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services
from game.ghdialogue import context
import gears
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, ghrooms

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

