import pbge.memos
from game.content.plotutility import LMSkillsSelfIntro
from game.content import backstory
from pbge.plots import Plot, Rumor
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
import gears
import game.content.gharchitecture
import game.content.ghterrain
import random

Memo = pbge.memos.Memo


#   *******************
#   ***  UTILITIES  ***
#   *******************


def get_hire_cost(camp, npc):
    return (npc.renown * npc.renown * (200 - npc.get_reaction_score(camp.pc, camp))) // 10


#   **************************
#   ***  RANDOM_LANCEMATE  ***
#   **************************

class UtterlyRandomLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(10, 50), random.randint(10, 50)),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        specialties = [sk for sk in gears.stats.NONCOMBAT_SKILLS if sk in npc.statline]
        if random.randint(-12, 3) > len(specialties):
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class UtterlyGenericLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mecha Pilot", "Arena Pilot", "Recon Pilot", "Mercenary", "Bounty Hunter")

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(10, 50), random.randint(10, 50)),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)

        if random.randint(1, 20) == 1:
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)

        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class GiftedNewbieLancemate(Plot):
    # Amazing stats, amazingly crap skills.
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mecha Pilot", "Arena Pilot", "Citizen", "Explorer", "Factory Worker")
    UNIQUE = True

    def custom_init(self, nart):
        npc = gears.selector.random_character(statline=gears.base.Being.random_stats(random.randint(100, 110)),
                                              rank=random.randint(5, 15),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True, birth_year=nart.camp.year - random.randint(18, 23))
        if random.randint(1, 10) == 1:
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class OlderMentorLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(41, 85),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True, birth_year=nart.camp.year - random.randint(32, 50))
        npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class DeadzonerInGreenZoneLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mercenary", "Bandit", "Scavenger", "Aristo", "Tekno", "Sheriff")
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(20, 55), random.randint(20, 55)),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=(gears.personality.DeadZone,),
                                              combatant=True)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class GladiatorLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(25, 65), random.randint(25, 65)),
                                              can_cyberize=True,
                                              job=gears.jobs.ALL_JOBS["Gladiator"],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=(gears.personality.DeadZone,),
                                              combatant=True)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate: gears.GearHeadScene):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class MutantLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return {gears.personality.GreenZone, gears.personality.DeadZone}.intersection(
            pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(20, 45),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])
        mutation = random.choice(gears.personality.MUTATIONS)
        mutation.apply(npc)
        npc.personality.add(mutation)

        specialties = [sk for sk in gears.stats.NONCOMBAT_SKILLS if sk in npc.statline]
        if random.randint(-12, 3) > len(specialties):
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class FormerLancemateReturns(Plot):
    # Please note this plot will never load a major NPC- they have to be added to the scenario by hand.
    LABEL = "RANDOM_LANCEMATE"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        npc: gears.base.Character = nart.camp.egg.seek_dramatis_person(nart.camp, self._is_good_npc, self)
        if npc:
            scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])
            self.register_element("NPC", npc, dident="NPC_SCENE")
            # print(npc,scene)
            self.bs = backstory.Backstory(("LONGTIMENOSEE",), keywords=[str(t).upper() for t in npc.get_tags()])
        return npc

    def _is_good_npc(self, nart, candidate):
        return isinstance(candidate,
                          gears.base.Character) and candidate.relationship and gears.relationships.RT_LANCEMATE in candidate.relationship.tags and not candidate.mnpcid

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is self.elements["NPC"]:
            for k in self.bs.results.keys():
                mygram[k] = [self.bs.get_one(k), ]
        else:
            mygram["[News]"] = ["{NPC} has been hanging out at {NPC_SCENE}".format(**self.elements), ]
        return mygram

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[INFO_PERSONAL]",
                            context=ContextTag([context.PERSONAL]),
                            no_repeats=True, effect=self.end_plot))
        return mylist

    def t_START(self, camp):
        if self.elements["NPC"] in camp.party:
            self.end_plot(camp)


class BountyHunterLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=min(random.randint(10, 50), random.randint(10, 50)),
                                              job=gears.jobs.ALL_JOBS["Bounty Hunter"],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)

        npc.personality.add(gears.personality.Justice)

        if random.randint(1, 4) != 1:
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)

        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="NPC_SCENE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#   **************************
#   ***  RLM_Relationship  ***
#   **************************
#  Elements:
#   NPC: The NPC who needs a personality
#   METRO: The scope of the current city
#   METROSCENE: The city or whatever that the NPC calls home
#   NPC_SCENE: The exact scene where the NPC is.
#
# These subplots contain a personality for a random (potential) lancemate.
# Also include a means for the lancemate to gain the "RT_LANCEMATE" tag.

class RLM_Beginner(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} has dreams of someday becoming a cavalier",
        offer_msg="As far as I know {NPC} usually hangs out at {NPC_SCENE}.",
        memo="{NPC} dreams of becoming a cavalier.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].renown < 25

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_JUNIOR)
        # This character gets fewer mecha points.
        npc.relationship.data["mecha_level_bonus"] = -10
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("I can't believe you asked me... [LETSGO]",
                                    context=ContextTag((context.JOIN,)),
                                    effect=self._join_lance
                                    ))
            mylist.append(Offer(
                "[HELLO] Some day I want to become a cavalier like you.", context=ContextTag((context.HELLO,))
            ))
        mylist.append(LMSkillsSelfIntro(npc))
        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class RLM_Friendly(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is looking for a lance to join",
        offer_msg="You can usually find {NPC} at {NPC_SCENE}, if you're planning to invite {NPC.gender.object_pronoun} to join your lance.",
        memo="{NPC} is looking for a lance to join.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_FRIENDLY)
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate() and npc.get_reaction_score(camp.pc, camp) > 0:
                mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                    context=ContextTag((context.JOIN,)),
                                    effect=self._join_lance
                                    ))
            mylist.append(Offer(
                "[HELLO] [WAITINGFORMISSION]", context=ContextTag((context.HELLO,))
            ))
        mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class RLM_Medic(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True
    VIRTUES = (gears.personality.Peace, gears.personality.Fellowship)

    RUMOR = Rumor(
        rumor="{NPC} wants to leave {NPC.scene} so {NPC.gender.subject_pronoun} can make a positive difference in the world",
        offer_msg="{NPC} is a {NPC.job}; {NPC.gender.subject_pronoun} has been working at {NPC_SCENE} but is hoping to get back behind the seat of a mech.",
        memo="{NPC} is a {NPC.job} who wants to join a lance.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].job and gears.tags.Medic in pstate.elements["NPC"].job.tags

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_GREATERGOOD)
        new_virtue = random.choice(self.VIRTUES)
        if new_virtue not in npc.personality:
            npc.personality.add(new_virtue)
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                    context=ContextTag((context.JOIN,)),
                                    effect=self._join_lance
                                    ))
            else:
                mylist.append(Offer(
                    "You've got a full crew right now, but if you ever find yourself in need of a qualified medic come back and find me.",
                    context=ContextTag((context.JOIN,)),
                    effect=self._defer_join
                ))
        mylist.append(Offer(
            "[HELLO] Lately I've been spending too much time here, when I'd rather be out in the danger zone saving lives.",
            context=ContextTag((context.HELLO,))
        ))
        mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _defer_join(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.end_plot(camp)


class RLM_Mercenary(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is hoping to make some quick cash",
        offer_msg="As far as I know {NPC} can usually be found at {NPC_SCENE}.",
        memo="{NPC} is a mercenary pilot looking for a job.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].job and {gears.tags.Adventurer, gears.tags.Military}.intersection(
            pstate.elements["NPC"].job.tags)

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_MERCENARY)
        # This character gets extra mecha points, showing their good investment sense.
        npc.relationship.data["mecha_level_bonus"] = 10
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
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
            mylist.append(Offer(
                "[HELLO] I am a mercenary pilot, looking for my next contract.", context=ContextTag((context.HELLO,))
            ))
            mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.credits -= self.hire_cost
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class RLM_Professional(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is an experienced pilot looking for work",
        offer_msg="You can usually find {NPC} at {NPC_SCENE}. Bring cash if you're planning to hire {NPC.gender.object_pronoun}.",
        memo="{NPC}  is an experienced pilot looking for work.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].renown > 35

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_PROFESSIONAL)
        # This character gets 10 extra stat points, showing their elite nature.
        npc.roll_stats(10, clear_first=False)
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer(
                    "[NOEXPOSURE] I think ${:,} is a fair signing price. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                    context=ContextTag((context.PROPOSAL, context.JOIN)), data={"subject": "joining my lance"},
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
            mylist.append(Offer(
                "[HELLO] I see you are also a cavalier.", context=ContextTag((context.HELLO,))
            ))
            mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.credits -= self.hire_cost
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class RLM_RatherGeneric(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        rumor="{NPC} is looking for a new lance to join",
        offer_msg="You can find {NPC} at {NPC_SCENE}.",
        memo="{NPC} is looking for a new lance.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship()
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
                    "[HELLO] [WAITINGFORMISSION]", context=ContextTag((context.HELLO,))
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] Must be nice going off, having adventures with your lancemates. I'd like to do that again someday.",
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


class RLM_PersonForHire(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        rumor="{NPC} is a {NPC.job} for hire",
        offer_msg="If you want a {NPC.jpb} on your team, you can find {NPC} at {NPC_SCENE}.",
        memo="{NPC} is a {NPC.job} for hire.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship()
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("My signing rate is ${:,}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
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
                    "[HELLO] [WAITINGFORMISSION]", context=ContextTag((context.HELLO,))
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


class RLM_StraightOutOfWork(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        rumor="{NPC} is an unemployed cavalier",
        offer_msg="You can find {NPC} at {NPC_SCENE}. I'm sure {NPC.gender.subject_pronoun} would be happy to embark on a new adventure.",
        memo="{NPC}  is an unemployed cavalier looking for a new lance to join.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship()
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                if npc.get_reaction_score(camp.pc, camp) > 20:
                    mylist.append(Offer("[IWOULDLOVETO] [THANKS_FOR_CHOOSING_ME]",
                                        context=ContextTag((context.PROPOSAL, context.JOIN)),
                                        data={"subject": "joining my lance"},
                                        effect=self._join_lance
                                        ))
                else:
                    mylist.append(Offer("Normally I charge ${:,} up front. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
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
                    "[HELLO] [WAITINGFORMISSION]", context=ContextTag((context.HELLO,))
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


class RLM_DamagedGoodsSale(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is a down on {NPC.gender.possessive_determiner} luck cavalier looking for another chance",
        offer_msg="You can find {NPC} at {NPC_SCENE}. Don't say that you weren't warned.",
        memo="{NPC} is an out of work pilot with a questionable past.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_IMPROVER)
        # This NPC gets a stat bonus but a crappy mech to show their history.
        npc.relationship.data["mecha_level_bonus"] = -15
        npc.roll_stats(5, clear_first=False)
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc) // 2
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                if npc.get_reaction_score(camp.pc, camp) > 20:
                    mylist.append(Offer("[IWOULDLOVETO] I'll do my best to not let you down.",
                                        context=ContextTag((context.PROPOSAL, context.JOIN)),
                                        data={"subject": "joining my lance"},
                                        effect=self._join_lance
                                        ))
                else:
                    mylist.append(
                        Offer("I'll sign up with you for just ${}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                              context=ContextTag((context.PROPOSAL, context.JOIN)),
                              data={"subject": "joining my lance"},
                              subject=self, subject_start=True,
                              ))
                    mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                        context=ContextTag((context.DENY, context.JOIN)), subject=self
                                        ))
                    if camp.credits >= self.hire_cost:
                        mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] I'll do my best to not let you down.",
                                            context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                            effect=self._pay_to_join
                                            ))
                mylist.append(Offer(
                    "[HELLO] The life of a cavalier is full of ups and downs... right now I'm in one of those downs.",
                    context=ContextTag((context.HELLO,))
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] Be careful out there... all it takes is one little mistake to cost you everything.",
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


class RLM_HauntedByTyphon(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is one of the pilots who fought against Typhon, and lost",
        offer_msg="{NPC.gender.subject_pronoun} hasn't piloted a mek since {NPC.gender.possessive_determiner} defeat. You can usually find {NPC} at {NPC_SCENE}; maybe speaking to another cavalier will improve {NPC.gender.possessive_determiner} mood.",
        memo="{NPC} is a cavalier who was defeated by Typhon and hasn't piloted a mek since.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.GreenZone in pstate.elements["NPC"].personality

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_DESPAIR)
        npc.statline[gears.stats.Cybertech] += random.randint(1, 5)
        if gears.personality.Grim not in npc.personality:
            npc.personality.add(gears.personality.Grim)
        if gears.personality.Cheerful in npc.personality:
            npc.personality.remove(gears.personality.Cheerful)
        return nart.camp.year > 157

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc) * 2
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if self._rumor_memo_delivered:
                if camp.can_add_lancemate():
                    if npc.get_reaction_score(camp.pc, camp) > 60:
                        mylist.append(Offer("[IWOULDLOVETO] It's about time for me to get back in the saddle.",
                                            context=ContextTag((context.PROPOSAL, context.JOIN)),
                                            data={"subject": "joining my lance"},
                                            effect=self._join_lance
                                            ))
                    else:
                        mylist.append(
                            Offer("It'd take ${:,} to get me in the seat of a mech again. [DOYOUACCEPTMYOFFER]".format(
                                self.hire_cost),
                                  context=ContextTag((context.PROPOSAL, context.JOIN)),
                                  data={"subject": "joining my lance"},
                                  subject=self, subject_start=True,
                                  ))
                        mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                            context=ContextTag((context.DENY, context.JOIN)), subject=self
                                            ))
                        if camp.credits >= self.hire_cost:
                            mylist.append(Offer("Huh, I really didn't expect you to pony up that much cash... [LETSGO]",
                                                context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                                effect=self._pay_to_join
                                                ))
            elif camp.pc.has_badge(gears.oldghloader.TYPHON_SLAYER.name):
                mylist.append(Offer(
                    "[HELLO] You're one of the cavaliers who defeated Typhon, aren't you?",
                    context=ContextTag([context.HELLO, ]), subject=npc, subject_start=True
                ))
                mylist.append(Offer(
                    "You probably don't remember me... I'm one of the pilots who also took part in the battle of Snake Lake, but just for a minute. Literally just a minute. Never even saw Typhon itself. Haven't piloted a mecha since.",
                    context=ContextTag([context.CUSTOM, ]), subject=npc,
                    data={"reply": "Yes, I am."}
                ))
                if npc.get_reaction_score(camp.pc, camp) > 20:
                    mylist.append(Offer("[IWOULDLOVETO] [LETSGO]",
                                        context=ContextTag((context.CUSTOMREPLY,)),
                                        data={"reply": "[INFO_PERSONAL:JOIN]"}, subject=npc,
                                        effect=self._join_lance
                                        ))
                else:
                    mylist.append(Offer("Nah, adventuring is a mug's game. I'm staying right here.",
                                        context=ContextTag((context.CUSTOMREPLY,)),
                                        data={"reply": "[INFO_PERSONAL:JOIN]"}, subject=npc,
                                        effect=self.end_plot
                                        ))
            mylist.append(LMSkillsSelfIntro(npc))

        else:
            mylist.append(Offer(
                "[HELLO] Be careful out there... all it takes is one little mistake to cost you everything.",
                context=ContextTag((context.HELLO,))
            ))
            self.end_plot(camp)

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


class RLM_MechaOtaku(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} is obsessed with mecha; maybe someday {NPC.gender.subject_pronoun} will become a cavalier",
        offer_msg="{NPC} usually hangs out at {NPC_SCENE}. Since you're a mecha pilot yourself, I'm sure {NPC.gender.subject_pronoun}'d be thrilled to talk with you.",
        memo="{NPC} is obsessed with mecha.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].statline[gears.stats.Knowledge] > 12

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_MECHANIAC)
        npc.statline[gears.stats.Repair] += random.randint(1, 5)
        npc.statline[gears.stats.Science] += random.randint(1, 5)
        self._did_mecha_chat = False
        return True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc: gears.base.Character = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            mylist.append(LMSkillsSelfIntro(npc))
            if not self._did_mecha_chat:
                mylist.append(Offer(
                    "[HELLO] I just checked cav-net and it says you are a cavalier?",
                    context=ContextTag((context.HELLO,)), subject=npc, subject_start=True
                ))

                pcmek: gears.base.Mecha = camp.get_pc_mecha(camp.pc)
                if pcmek:
                    engine, gyro = pcmek.get_engine_rating_and_gyro_status()
                    if engine > 1700:
                        opinion = "That makes it one of the most powerful mecha out there. When an engine that size blows up, it's really something."
                    elif engine > 1100:
                        opinion = "That makes it a powerful mecha. You could probably be an arena contender with something like that."
                    elif engine > 750:
                        opinion = "That makes it solidly above average. A good mecha, but maybe not a great one."
                    elif engine > 450:
                        opinion = "That is enough power to get by, I guess. If I were you I'd consider upgrading to a bigger engine."
                    elif engine > 0:
                        opinion = "That's a really tiny engine. Like, barely enough to move with. I'm not sure you could run a metro bus on that."
                    else:
                        opinion = "I don't know why you'd pilot a mecha without an engine in it, but I'll assume you have your reasons."
                    mylist.append(Offer(
                        "Did you know that the {} you pilot has a class {} engine? {}".format(pcmek.get_full_name(), engine, opinion),
                        context=ContextTag((context.CUSTOM,)), subject=npc,
                        data={"reply": "Yes, I am. Would you like to talk about mecha?"},
                        effect=self._complete_mecha_chat
                    ))

                else:
                    mylist.append(Offer(
                        "Well, it also says here that you are currently dispossessed, so I don't know what we would have to talk about. I have a {}.".format(npc.mecha_pref),
                        context=ContextTag((context.CUSTOM,)), subject=npc,
                        data={"reply": "Yes, I am. Would you like to talk about mecha?"},
                        effect=self._complete_mecha_chat
                    ))

                mylist.append(Offer(
                    "Mine is a {}. I'm hoping to get a better one someday but to do that I'd have to become a cavalier and go on missions.".format(npc.mecha_pref),
                    context=ContextTag((context.CUSTOMREPLY,)), subject=npc,
                    data={"subject": "your mecha", "reply": "[HELLO:INFO]"},
                    effect=self._complete_mecha_chat
                ))

            else:
                mylist.append(Offer(
                    "[HELLO] I have a {} and someday I will get the chance to use it.".format(npc.mecha_pref),
                    context=ContextTag((context.HELLO,))
                ))

                mylist.append(Offer(
                    "I would love to be a cavalier someday. First I'd need a lance to join. Trying to do that job by yourself is a quick path to an early grave. Or at least you could lose your mecha. I don't want to lose my mecha.",
                    context=ContextTag((context.INFO,context.PERSONAL)), subject=npc,
                    data={"subject": "cavaliers"}, no_repeats=True
                ))

                if camp.can_add_lancemate():
                    if camp.renown > npc.renown:
                        mylist.append(Offer("[IWOULDLOVETO] [THANKS_FOR_CHOOSING_ME]",
                                            context=ContextTag((context.PROPOSAL, context.JOIN)),
                                            data={"subject": "joining my lance"},
                                            effect=self._join_lance
                                            ))
                    else:
                        mylist.append(
                            Offer("I would love to join your lance but the standard rate for a pilot of my ranking is ${:,}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
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
        else:
            self.end_plot(camp)

        return mylist

    def _complete_mecha_chat(self, camp):
        self._did_mecha_chat = True

    def _pay_to_join(self, camp):
        camp.credits -= self.hire_cost
        self._join_lance(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class RLM_FarmKid(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = "METRO"
    UNIQUE = True

    RUMOR = Rumor(
        rumor="{NPC} wants to get out of {METROSCENE}",
        offer_msg="I think {NPC.gender.subject_pronoun} is just tired of small town life. You should be able to find {NPC} at {NPC_SCENE}.",
        memo="{NPC} is bored with small town life and wants to get out of {METROSCENE}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.tags.Village in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_JUNIOR,
                                                            expectation=gears.relationships.E_ADVENTURE)
        npc.relationship.data["mecha_level_bonus"] = -15
        npc.statline[gears.stats.Wildcraft] += random.randint(1,5)
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate() and npc.get_reaction_score(camp.pc, camp) > 0:
                mylist.append(Offer("And there's my way out of {METROSCENE}! [LETSGO]".format(**self.elements),
                                    context=ContextTag((context.JOIN,)),
                                    effect=self._join_lance
                                    ))
            mylist.append(Offer(
                "[HELLO] This town is boring... if I had a way out, I'd take it in a second.", context=ContextTag((context.HELLO,))
            ))
        mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)
