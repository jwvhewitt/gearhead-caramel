from pbge.plots import Plot, PlotState, Rumor
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder, rwme_objectives, campfeatures
from game.memobrowser import Memo

SEEK_ENEMY_BASE_MISSION = "SEEK_ENEMY_BASE_MISSION"
AUTOFIND_ENEMY_BASE_MISSION = "AUTOFIND_ENEMY_BASE_MISSION"
SEBO_SEARCH_FOR_BASE = "SEBO_SEARCH_FOR_BASE"

#   *************************
#   ***  SEEK_ENEMY_BASE  ***
#   *************************
#
# You need to find an enemy base. This plot will load subplots until the base is found or the game runs out of
# patience, whichever comes first. Note that the enemy base need not necessarily be an actual base- it's a location
# or thing that the provided enemy faction knows the location of but you don't.
#
# This plot will set a WIN trigger when the base (or whatever) is located.
#
# Needed Elements:
# METROSCENE, METRO, MISSION_GATE
# ENEMY_FACTION
# ENEMY_BASE_NAME: The name to be used for the enemy base.
#

class SeekEnemyBaseMain(campfeatures.MetrosceneRandomPlotHandler):
    LABEL = "SEEK_ENEMY_BASE"

    MAX_PLOTS = 1
    SUBPLOT_LABEL = SEEK_ENEMY_BASE_MISSION

    def custom_init( self, nart ):
        ok = super().custom_init(nart)
        if ok:
            self.mission_patience = random.randint(1,2)
            self.rank_modifier = 0
            self.ran_out_of_patience = False
            self.elements["WIN_FUN"] = self.locate_the_base
            self.elements["SEMIWIN_FUN"] = self.win_a_mission
        return ok

    def locate_the_base(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.adv.end_adventure(camp)

    def win_a_mission(self, camp):
        self.rank_modifier += random.randint(1, 3)
        self.mission_patience -= 1
        if self.active and self.mission_patience < 1 and not self.ran_out_of_patience:
            self.subplots["MISSION"] = game.content.load_dynamic_plot(
                camp, AUTOFIND_ENEMY_BASE_MISSION, PlotState(rank=self.rank + self.rank_modifier).based_on(self)
            )
            self.ran_out_of_patience = True

    def _get_dialogue_grammar(self, npc: gears.base.Character, camp):
        mygram = dict()
        if npc.faction is not self.elements.get("ENEMY_FACTION"):
            mygram["[News]"] = ["only {ENEMY_FACTION} know where {ENEMY_BASE_NAME} is".format(**self.elements), ]
        return mygram

    def calc_rank(self, camp: gears.GearHeadCampaign):
        return self.rank + self.rank_modifier


#   *********************************
#   ***  SEEK_ENEMY_BASE_MISSION  ***
#   *********************************
#
# Elements:
# WIN_FUN = A function with signature (camp) to call when the enemy base is located.
# SEMIWIN_FUN = A function with signature (camp) to call when a mission is "won", but base not located.
#

class BasicCombatBaseSearch(Plot):
    LABEL = SEEK_ENEMY_BASE_MISSION
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} lost a fight to {ENEMY_FACTION}",
        offer_msg="You can ask {NPC} about {ENEMY_FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}.",
        memo="{NPC} lost a battle against {ENEMY_FACTION}.", prohibited_npcs=("NPC",)
    )

    MISSION_NAME = "Avenge {NPC}"
    MISSION_OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES, SEBO_SEARCH_FOR_BASE)

    def custom_init( self, nart ):
        npc = self.seek_element(nart, "NPC", self.is_good_npc, scope=self.elements["METROSCENE"], lock=True)
        self.elements["NPC_SCENE"] = npc.scene
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            nart.camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            self.elements["ENEMY_FACTION"], npc.faction, self.rank,
            objectives=self.MISSION_OBJECTIVES,
            scenegen=sgen, architecture=archi, on_win=self.elements["SEMIWIN_FUN"],
            custom_elements={"FIND_BASE_FUN": self.elements["WIN_FUN"], "ENEMY_BASE_NAME": self.elements["ENEMY_BASE_NAME"]}
        )
        self.mission_active = False
        self.expiration = gears.TimeOrNPCExpiration(nart.camp, npcs=("NPC",))
        return True

    def is_good_npc(self, nart, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate.combatant and
            candidate not in nart.camp.party and
            gears.tags.SCENE_PUBLIC in candidate.scene.attributes and
            not nart.camp.are_faction_allies(candidate, self.elements["ENEMY_FACTION"])
        )

    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer(
                "[HELLO] [FACTION_MUST_BE_PUNISHED]",
                ContextTag([context.HELLO,]), data={"faction": str(self.elements["ENEMY_FACTION"])}
            ))

            mylist.append(Offer(
                "[FACTION_DEFEATED_ME] [WILL_YOU_AVENGE_ME]",
                ContextTag([context.MISSION, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[IWillSendMissionDetails]; [GOODLUCK]",
                ContextTag([context.ACCEPT, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._accept_mission, subject=self
            ))

            mylist.append(Offer(
                "[UNDERSTOOD]",
                ContextTag([context.DENY, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._deny_misssion, subject=self
            ))

            mylist.append(Offer(
                "[FACTION_DEFEATED_ME]",
                ContextTag([context.UNFAVORABLE_HELLO,]), data={"faction": str(self.elements["ENEMY_FACTION"])}
            ))

            mylist.append(Offer(
                "Well if you're so good, why don't you try beating {} yourself?!".format(self.elements["ENEMY_FACTION"]),
                ContextTag([context.UNFAVORABLE_CUSTOM,]), data={"reply": "[I_WOULD_NOT_HAVE_LOST]"},
                effect=self._accept_mission
            ))

        return mylist

    def _accept_mission(self, camp):
        self.mission_active = True
        self.RUMOR.disable_rumor(self)
        self.expiration = None
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _deny_misssion(self, camp):
        self.end_plot(camp, True)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def t_UPDATE(self, camp):
        # If the adventure has ended, get rid of it.
        if self.mission_seed.ended:
            self.end_plot(camp, True)


class TownEnemyCombatBaseSearch(BasicCombatBaseSearch):
    RUMOR = Rumor(
        "{NPC} is looking for someone to fight {ENEMY_FACTION}",
        offer_msg="If you want to get the job, you can find {NPC} at {NPC_SCENE}.",
        memo="{NPC} is looking for someone to fight {ENEMY_FACTION}.", prohibited_npcs=("NPC",)
    )

    MISSION_NAME = "{NPC}'s Mission"
    MISSION_OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES, SEBO_SEARCH_FOR_BASE)

    def is_good_npc(self, nart, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate.combatant and
            candidate not in nart.camp.party and
            gears.tags.SCENE_PUBLIC in candidate.scene.attributes and
            nart.camp.are_faction_enemies(candidate, self.elements["ENEMY_FACTION"])
        )

    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer(
                "[HELLO] [LOOKING_FOR_CAVALIER]",
                ContextTag([context.HELLO,context.MISSION]), data={"faction": str(self.elements["ENEMY_FACTION"])}
            ))

            mylist.append(Offer(
                "[MechaMissionVsEnemyFaction]; [THEYAREOURENEMY]",
                ContextTag([context.MISSION, ]), data={"enemy_faction": str(self.elements["ENEMY_FACTION"]),
                                                       "they": str(self.elements["ENEMY_FACTION"])},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[GOODLUCK] [IWillSendMissionDetails].",
                ContextTag([context.ACCEPT, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._accept_mission, subject=self
            ))

            mylist.append(Offer(
                "[UNDERSTOOD]",
                ContextTag([context.DENY, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._deny_misssion, subject=self
            ))

            mylist.append(Offer(
                "Get out of here; I've got work to do.",
                ContextTag([context.UNFAVORABLE_HELLO,]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._deny_misssion
            ))
        return mylist


class CriminalCombatBaseSearch(BasicCombatBaseSearch):
    RUMOR = Rumor(
        "{NPC} had a shipment of cargo stolen by {ENEMY_FACTION}",
        offer_msg="Go talk to {NPC} at {NPC_SCENE}; maybe you can get a mission out of it.",
        memo="{NPC} is looking for someone to recover cargo stolen by {ENEMY_FACTION}.", prohibited_npcs=("NPC",)
    )

    MISSION_NAME = "{NPC}'s Mission"
    MISSION_OBJECTIVES = (missionbuilder.BAMO_RECOVER_CARGO, SEBO_SEARCH_FOR_BASE)

    @classmethod
    def matches( self, pstate ):
        return "ENEMY_FACTION" in pstate.elements and gears.tags.Criminal in pstate.elements["ENEMY_FACTION"].factags

    def is_good_npc(self, nart, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate not in nart.camp.party and
            gears.tags.SCENE_PUBLIC in candidate.scene.attributes and
            {gears.tags.Merchant, gears.tags.CorporateWorker, gears.tags.Laborer}.intersection(candidate.get_tags())
        )

    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer(
                "[HELLO] [LOOKING_FOR_CAVALIER]",
                ContextTag([context.HELLO,context.MISSION]), data={"faction": str(self.elements["ENEMY_FACTION"])}
            ))

            mylist.append(Offer(
                "[MechaMissionVsEnemyFaction]; [THEYARETHIEVES]",
                ContextTag([context.MISSION, ]), data={"enemy_faction": str(self.elements["ENEMY_FACTION"]),
                                                       "they": str(self.elements["ENEMY_FACTION"])},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[GOODLUCK] [IWillSendMissionDetails].",
                ContextTag([context.ACCEPT, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._accept_mission, subject=self
            ))

            mylist.append(Offer(
                "[UNDERSTOOD]",
                ContextTag([context.DENY, ]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._deny_misssion, subject=self
            ))

            mylist.append(Offer(
                "You've got no business being here.",
                ContextTag([context.UNFAVORABLE_HELLO,]), data={"faction": str(self.elements["ENEMY_FACTION"])},
                effect=self._deny_misssion
            ))
        return mylist


#   *************************************
#   ***  AUTOFIND_ENEMY_BASE_MISSION  ***
#   *************************************

class InsultinglyEasyAutofindEnemyBase(Plot):
    LABEL = AUTOFIND_ENEMY_BASE_MISSION
    active = True
    scope = "METRO"

    def t_UPDATE(self, camp: gears.GearHeadCampaign):
        pbge.alert("You find a piece of paper on the ground with the location of {ENEMY_BASE_NAME} written on it.".format(**self.elements))
        self.end_plot(camp)
        self.elements["WIN_FUN"](camp)

#   ******************************
#   ***  SEBO_SEARCH_FOR_BASE  ***
#   ******************************
#
# This objective can be added to any mission to give a chance that the lance will locate the base being sought.
# The skills known by the party members will determine whether or not the base is found.
#
# Needed Elements:
# FIND_BASE_FUN: A function with signature (camp) to call if the base is found.
#

class SEBOSearchForBase( Plot ):
    LABEL = SEBO_SEARCH_FOR_BASE
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        self.intro_ready = True
        self.extro_ready = True
        return True

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.intro_ready:
            self.intro_ready = False
            candidates = list()
            if camp.party_has_skill(gears.stats.Scouting):
                candidates.append(self.attempt_scouting)
            if camp.party_has_skill(gears.stats.Stealth):
                candidates.append(self.attempt_stealth)
            if candidates:
                random.choice(candidates)(camp)

    def t_ENDCOMBAT(self, camp):
        if self.adv.is_won() and self.extro_ready:
            self.extro_ready = False
            candidates = list()
            if camp.party_has_skill(gears.stats.Wildcraft):
                candidates.append(self.attempt_wildcraft)
            if camp.party_has_skill(gears.stats.Computers):
                candidates.append(self.attempt_computers)
            if candidates:
                random.choice(candidates)(camp)

    def attempt_scouting(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Scouting,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("As you approach {ENEMY_FACTION}, you realize you could probably follow them back to their base.".format(**self.elements))
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[I_HAVE_DETECTED_ENEMIES] If we want to know where their base is, our best bet would be to stand back and follow them at a distance.",pc,camp)
            mymenu.add_item("Follow them to their base",self.find_the_base)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_stealth(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Stealth,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You encounter a group of hostile mecha, but manage to remain unseen.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[ENEMIES_HAVE_NOT_DETECTED_US] If you're interested in finding their base, we can tail them all the way back.",pc,camp)
            mymenu.add_item("Follow them to their base",self.find_the_base)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_wildcraft(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Wildcraft,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                pbge.alert("After the battle, you find tracks leading directly back to {}.".format(self.elements["ENEMY_BASE_NAME"]))
            else:
                ghcutscene.SimpleMonologueDisplay("Take a look at these tracks... I think we can trace them back to {}.".format(self.elements["ENEMY_BASE_NAME"]),pc)(camp)
            self.find_the_base(camp, True)

    def attempt_computers(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Computers,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                pbge.alert("After the battle, you hack into one of the enemy's navcomps and learn the location of {}.".format(self.elements["ENEMY_BASE_NAME"]))
            else:
                ghcutscene.SimpleMonologueDisplay("[LOOK_AT_THIS] I managed to hack into their navcomp and found out where {} is.".format(self.elements["ENEMY_BASE_NAME"]),pc)(camp)
            self.find_the_base(camp, True)

    def find_the_base(self,camp: gears.GearHeadCampaign, win_mission=False):
        self.elements["FIND_BASE_FUN"](camp)
        camp.go(self.elements["ADVENTURE_RETURN"])
        if win_mission:
            self.adv.end_adventure(camp)
        else:
            self.adv.cancel_adventure(camp)
