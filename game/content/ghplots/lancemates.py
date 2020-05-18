import pbge
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
import gears
import game.content.gharchitecture
import game.content.plotutility
import game.content.ghterrain
import random

#   **************************
#   ***  RANDOM_LANCEMATE  ***
#   **************************

class UtterlyRandomLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(10, 50),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class UtterlyGenericLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mecha Pilot","Arena Pilot","Recon Pilot","Mercenary","Bounty Hunter")

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(10, 50),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class GiftedNewbieLancemate(Plot):
    # Amazing stats, amazingly crap skills.
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mecha Pilot","Arena Pilot","Citizen","Explorer","Factory Worker")
    UNIQUE = True

    def custom_init(self, nart):
        npc = gears.selector.random_character(statline=gears.base.Being.random_stats(random.randint(100, 110)),
                                              rank=random.randint(5, 15),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True, birth_year=nart.camp.year - random.randint(18,23))
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class OlderMentorLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(45, 75),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True, birth_year=nart.camp.year - random.randint(32,50))
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class DeadzonerInGreenZoneLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    JOBS = ("Mercenary","Bandit","Scavenger","Aristo","Tekno","Sheriff")
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(20, 55),
                                              job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=(gears.personality.DeadZone,),
                                              combatant=True)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class GladiatorLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(25, 65),can_cyberize=True,
                                              job=gears.jobs.ALL_JOBS["Gladiator"],
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=(gears.personality.DeadZone,),
                                              combatant=True)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class MutantLancemate(Plot):
    LABEL = "RANDOM_LANCEMATE"
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return {gears.personality.GreenZone,gears.personality.DeadZone}.intersection(pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=random.randint(20, 45),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              combatant=True)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        mutation = random.choice(gears.personality.MUTATIONS)
        mutation.apply(npc)
        npc.personality.add(mutation)

        self.register_element("NPC", npc, dident="LOCALE")
        self.add_sub_plot(nart, "RLM_Relationship")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#   **************************
#   ***  RLM_Relationship  ***
#   **************************
#  Elements:
#   NPC: The NPC who needs a personality
#   METROSCENE: The city or whatever that the NPC calls home
#
# These subplots contain a personality for a random (potential) lancemate.
# Also include a means for the lancemate to gain the "RT_LANCEMATE" tag.

class RLM_Beginner(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].renown < 25

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_JUNIOR)
        # This character gets fewer mecha points.
        npc.relationship.data["mecha_level_bonus"] = -10
        self._got_rumor = False
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
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{} has dreams of someday becoming a cavalier".format(self.elements["NPC"]), ]
        return mygram

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="As far as I know {} usually hangs out at {}.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} dreams of becoming a cavalier.".format(mynpc,mynpc.get_scene())


class RLM_Friendly(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(attitude=gears.relationships.A_FRIENDLY)
        self._got_rumor = False
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
        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{} is looking for a lance to join".format(self.elements["NPC"]), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can usually find {} at {}, if you're planning to invite {} to join your lance.".format(mynpc,mynpc.get_scene(),mynpc.gender.object_pronoun),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} is looking for a lance to join.".format(mynpc,mynpc.get_scene())


class RLM_Medic(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True
    UNIQUE = True
    VIRTUES = (gears.personality.Peace,gears.personality.Fellowship)

    @classmethod
    def matches( self, pstate ):
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
                mylist.append(Offer("You've got a full crew right now, but if you ever find yourself in need of a qualified medic come back and find me.",
                                    context=ContextTag((context.JOIN,)),
                                    effect=self._defer_join
                                    ))
        mylist.append(Offer(
            "[HELLO] Lately I've been spending too much time here, when I'd rather be out in the danger zone saving lives.", context=ContextTag((context.HELLO,))
        ))
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{} wants to leave {} so {} can make a positive difference in the world".format(self.elements["NPC"],self.elements["NPC"].get_scene(),self.elements["NPC"].gender.subject_pronoun), ]
        return mygram

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
    scope = True
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].job and {gears.tags.Adventurer,gears.tags.Military}.intersection(pstate.elements["NPC"].job.tags)

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_MERCENARY)
        # This character gets extra mecha points, showing their good investment sense.
        npc.relationship.data["mecha_level_bonus"] = 10
        self._got_rumor = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = npc.renown * (200 - npc.get_reaction_score(camp.pc, camp))
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
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{} is hoping to make some quick cash".format(self.elements["NPC"]), ]
        return mygram

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.credits -= self.hire_cost
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="As far as I know {}  can usually be found at {}.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} is a mercenary pilot looking for a job.".format(mynpc,mynpc.get_scene())



class RLM_Professional(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True
    UNIQUE = True

    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements["NPC"].renown > 20

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_PROFESSIONAL)
        # This character gets 10 extra stat points, showing their elite nature.
        npc.roll_stats(10, clear_first=False)
        self._got_rumor = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = npc.renown * (250 - npc.get_reaction_score(camp.pc, camp))
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer(
                    "[NOEXPOSURE] I think ${} is a fair signing price. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
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
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{} is an experienced pilot looking for work".format(self.elements["NPC"]), ]
        return mygram

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.credits -= self.hire_cost
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can usually find {} at {}. Bring cash if you're planning to hire {}.".format(mynpc,mynpc.get_scene(),mynpc.gender.object_pronoun),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} is an experienced pilot looking for work.".format(mynpc,mynpc.get_scene())


class RLM_RatherGeneric(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(role=gears.relationships.R_ACQUAINTANCE )
        self._got_rumor = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = npc.renown * (175 - npc.get_reaction_score(camp.pc, camp))
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
                    "[HELLO] Must be nice going off, having adventures with your lancemates. I'd like to do that again someday.", context=ContextTag((context.HELLO,))
                ))
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            mygram["[News]"] = ["{} is looking for a new lance to join".format(self.elements["NPC"]), ]
        return mygram

    def _pay_to_join(self,camp):
        camp.credits -= self.hire_cost
        self._join_lance(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can find {} at {}.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} is looking for a new lance.".format(mynpc,mynpc.get_scene())


class RLM_DamagedGoodsSale(Plot):
    LABEL = "RLM_Relationship"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        npc.relationship = gears.relationships.Relationship(expectation=gears.relationships.E_IMPROVER)
        # This NPC gets a stat bonus but a crappy mech to show their history.
        npc.relationship.data["mecha_level_bonus"] = -15
        npc.roll_stats(5, clear_first=False)
        self._got_rumor = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = npc.renown * (125 - npc.get_reaction_score(camp.pc, camp))
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                if npc.get_reaction_score(camp.pc, camp) > 20:
                    mylist.append(Offer("[IWOULDLOVETO] I'll do my best to not let you down.",
                                        context=ContextTag((context.PROPOSAL, context.JOIN)),
                                        data={"subject": "joining my lance"},
                                        effect=self._join_lance
                                        ))
                else:
                    mylist.append(Offer("I'll sign up with you for just ${}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
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
                    "[HELLO] The life of a cavalier is full of ups and downs... right now I'm in one of those downs.", context=ContextTag((context.HELLO,))
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] Be careful out there... all it takes is one little mistake to cost you everything.", context=ContextTag((context.HELLO,))
                ))
        return mylist

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
            mygram["[News]"] = ["{NPC} is a down on {NPC.gender.possessive_determiner} luck cavalier looking for another chance".format(**self.elements), ]
        return mygram

    def _pay_to_join(self,camp):
        camp.credits -= self.hire_cost
        self._join_lance(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self._got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can find {} at {}. Don't say that you weren't warned.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements["NPC"]
        self._got_rumor = True
        self.memo = "{} at {} is looking for a new lance.".format(mynpc,mynpc.get_scene())
