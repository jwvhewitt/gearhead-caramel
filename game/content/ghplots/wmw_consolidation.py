import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge import stories, quests
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, ghquests
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


WMW_CONSOLIDATION = "WMW_CONSOLIDATION"


# A consolidation plot gets the following elements:
# METROSCENE, METRO, MISSION_GATE, WORLD_MAP_WAR
# FORMER_FACTION: The faction you just kicked out. May be None.


class EliminateScoutsConsolidation(Plot):
    LABEL = WMW_CONSOLIDATION
    scope = "METRO"
    active = True

    intro_ready = True

    def custom_init(self, nart):
        self.elements["ALLIED_FACTION"] = self.elements["WORLD_MAP_WAR"].player_team
        self.elements["ENEMY_FACTION"] = self.elements["WORLD_MAP_WAR"].get_enemy_faction(nart.camp, self.elements["WORLD_MAP_WAR"].player_team)

        _ = self.register_element("CHALLENGE", Challenge(
            "Fight {ENEMY_FACTION} in {METROSCENE}".format(**self.elements),
            ghchallenges.FIGHT_CHALLENGE, [self.elements["ENEMY_FACTION"]],
            involvement=ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], self.elements["ALLIED_FACTION"]),
            active=False,
            data={
                "challenge_objectives": [
                    "defend {METROSCENE}".format(**self.elements),
                    "keep {ENEMY_FACTION} out of {METROSCENE}".format(**self.elements),
                ],
                "challenge_fears": [
                    "attack {METROSCENE}".format(**self.elements),
                    "attack {ALLIED_FACTION}".format(**self.elements)
                ],
                "enemy_objectives": [
                    "take control of {METROSCENE}".format(**self.elements),
                    "drive {ALLIED_FACTION} from {METROSCENE}".format(**self.elements),
                ],
                "mission_intros": [
                    "Agents of {ENEMY_FACTION} have been spotted near {METROSCENE}.".format(**self.elements),
                    "Mecha belonging to {ENEMY_FACTION} are operating in the area.".format(**self.elements),
                ],
                "mission_objectives": [
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_AID_ALLIED_FORCES,
                        "Enemy forces have been skirmishing against {ALLIED_FACTION}.".format(**self.elements),
                        "aid {ALLIED_FACTION}".format(**self.elements),
                        "end {ALLIED_FACTION}'s occupation of {METROSCENE}".format(**self.elements),
                        "I defeated you and {ENEMY_FACTION}".format(**self.elements),
                        "you led {ALLIED_FACTION} to victory against {ENEMY_FACTION}".format(**self.elements),
                        "you defeated a patrol belonging to {ALLIED_FACTION}".format(**self.elements),
                        "I defeated the aggression of {ALLIED_FACTION}".format(**self.elements)
                    ),
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_CAPTURE_BUILDINGS,
                        "It's thought that {ENEMY_FACTION} must have a base of operations nearby.".format(**self.elements),
                        "destroy your base".format(**self.elements),
                        "protect {ENEMY_FACTION}'s presence in {METROSCENE}".format(**self.elements),
                        "I captured {ENEMY_FACTION}'s base near {METROSCENE}".format(**self.elements),
                        "you destroyed my secret base".format(**self.elements),
                        "you scored a victory for {ENEMY_FACTION}".format(**self.elements),
                        "I showed you that {ENEMY_FACTION} is not easily removed".format(**self.elements)
                    ),
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_SURVIVE_THE_AMBUSH,
                        "Several of our patrols have been ambushed by {ENEMY_FACTION}.".format(**self.elements),
                        "put a halt to your operations in {METROSCENE}".format(**self.elements),
                        "cause as much trouble as possible for {ALLIED_FACTION}".format(**self.elements),
                        win_pp="I survived your ambush".format(**self.elements),
                        win_ep="you proved to be more resilient than I thought".format(**self.elements),
                        lose_pp="you caught me off-guard".format(**self.elements),
                        lose_ep="you wandered straight into my ambush".format(**self.elements)
                    ),
                ]
            },
            memo=pbge.challenges.ChallengeMemo(
                "You must eliminate the scout team from {ENEMY_FACTION} who have been spotted near {METROSCENE}.".format(**self.elements)
            ), memo_active=True, deactivate_on_win=True, num_simultaneous_plots=2
        ))

        return True

    def CHALLENGE_WIN(self, camp):
        pbge.BasicNotification("Consolidation complete!", count=160)
        camp.check_trigger("WIN", self)
        self.elements["WORLD_MAP_WAR"].player_can_act = True
        self.end_plot(camp)

    def METROSCENE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert("The next step is to consolidate your victory in {METROSCENE}. There have been reports of scouts from {ENEMY_FACTION} operating nearby.".format(**self.elements))
            self.elements["CHALLENGE"].activate(camp)
            self.intro_ready = False


class SleeperCellConsolidation(Plot):
    # The enemy have left behind some operatives to cause problems later.
    LABEL = WMW_CONSOLIDATION
    scope = "METRO"
    active = True

    @classmethod
    def matches(cls, pstate: PlotState):
        # Former Faction is needed.
        return pstate.elements.get("FORMER_FACTION")

    def custom_init(self, nart):
        self.elements["ALLIED_FACTION"] = self.elements["WORLD_MAP_WAR"].player_team

        _ = self.register_element("CHALLENGE", Challenge(
            "Locate {FORMER_FACTION} Sleeper Cell".format(**self.elements),
            ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE,
            (self.elements["FORMER_FACTION"],),
            involvement=ghchallenges.InvolvedMetroFactionNPCs(
                self.elements["METROSCENE"], self.elements["ALLIED_FACTION"]
            ),
            data={
                "base_name": "sleeper cell"
            },
            memo=pbge.challenges.ChallengeMemo(
                "You should locate and destroy {FORMER_FACTION}'s sleeper cell in {METROSCENE}.".format(**self.elements)
            ), active=True, memo_active=True, deactivate_on_win=True, num_simultaneous_plots=3,
        ))

        self.intro_ready = True
        self.finished_challenge = False
        self.mission_name = "Attack {FORMER_FACTION}'s sleeper cell".format(**self.elements)
        return True

    def CHALLENGE_WIN(self, camp):
        missionbuilder.NewMissionNotification(self.mission_name, mission_gate=self.elements["MISSION_GATE"])
        self.finished_challenge = True
        self.memo = Memo("You have located {FORMER_FACTION}'s sleeper cell in {METROSCENE} and can attack them at any time from {MISSION_GATE}.".format(**self.elements), location=self.elements["METROSCENE"])

    EXTRA_OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_CAPTURE_BUILDINGS)

    def get_mission(self, camp):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        return missionbuilder.BuildAMissionSeed(
            camp, self.mission_name,
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=self.elements["ALLIED_FACTION"],
            enemy_faction=self.elements["FORMER_FACTION"], rank=self.rank,
            objectives=[missionbuilder.BAMO_DEFEAT_COMMANDER, ] + [random.choice(self.EXTRA_OBJECTIVES)],
            one_chance=True,
            scenegen=sgen, architecture=archi,
            cash_reward=120,
            on_win=self._win_da_mission
        )

    def _win_da_mission(self, camp):
        camp.check_trigger("WIN", self)
        pbge.BasicNotification("Consolidation complete!", count=160)
        self.elements["WORLD_MAP_WAR"].player_can_act = True
        self.end_plot(camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.finished_challenge:
            thingmenu.add_item(self.mission_name, self.get_mission(camp))

    def METROSCENE_ENTER(self, camp):
        #mychallenge = self.elements["CHALLENGE"]
        #print(mychallenge.active)
        #print(self.elements["METROSCENE"])
        if self.intro_ready:
            pbge.alert("The next step is to consolidate your victory in {METROSCENE}. Headquarters reports that {FORMER_FACTION} may have left behind a sleeper cell mecha team to cause problems for {ALLIED_FACTION}.".format(**self.elements))
            self.elements["CHALLENGE"].activate(camp)
            self.intro_ready = False


class DiplomaticConsolidation(Plot):
    # Talk to residents and try to convince them that the occupation is OK.
    LABEL = WMW_CONSOLIDATION
    scope = "METRO"
    active = True

    intro_ready = True

    DEFAULT_CHALLENGE_STEP = 1

    @classmethod
    def matches(cls, pstate: PlotState):
        wmw = pstate.elements.get("WORLD_MAP_WAR")
        return wmw and wmw.player_team and not wmw.war_teams[wmw.player_team].unpopular

    def custom_init(self, nart):
        self.elements["ALLIED_FACTION"] = self.elements["WORLD_MAP_WAR"].player_team

        _ = self.register_element("CHALLENGE", Challenge(
            "Promote {ALLIED_FACTION} in {METROSCENE}".format(**self.elements),
            ghchallenges.PR_CHALLENGE, [self.elements["WORLD_MAP_WAR"].player_team],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"]), active=False,
            data={
                "challenge_subject": "{ALLIED_FACTION} in {METROSCENE}".format(**self.elements),
                "pc_promotions": (
                    "{ALLIED_FACTION} will bring peace to {METROSCENE}".format(**self.elements),
                    "{ALLIED_FACTION} will bring stability to {METROSCENE}".format(**self.elements),
                    "{ALLIED_FACTION} will bring prosperity to {METROSCENE}".format(**self.elements),
                    "{ALLIED_FACTION} will protect {METROSCENE}".format(**self.elements),
                ),
                "npc_opinions": (
                    "{ALLIED_FACTION} doesn't belong in {METROSCENE}".format(**self.elements),
                ),
                "npc_agreement": (
                    "{ALLIED_FACTION} might not be so bad".format(**self.elements),
                ),
                "npc_disagreement": (
                    "{METROSCENE} is better off without {ALLIED_FACTION}".format(**self.elements),
                )
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[THINK_ABOUT_THIS] [IT_IS_OK_OR_BETTER]",
                        context=ContextTag([context.CUSTOM,]), effect=self._advance_challenge,
                        data={
                            "reply": "How do you feel about {ALLIED_FACTION}?".format(**self.elements),
                            "it": "{ALLIED_FACTION} being in {METROSCENE}".format(**self.elements)
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True,
                        difficulty=gears.stats.DIFFICULTY_HARD
                    )
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "You should ensure that the residents of {METROSCENE} are okay with the presence of {ALLIED_FACTION}.".format(**self.elements)
            ), memo_active=True, deactivate_on_win=True, num_simultaneous_plots=1
        ))

        return True

    def CHALLENGE_WIN(self, camp):
        pbge.BasicNotification("Consolidation complete!", count=160)
        camp.check_trigger("WIN", self)
        self.elements["WORLD_MAP_WAR"].player_can_act = True
        self.end_plot(camp)

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, self.DEFAULT_CHALLENGE_STEP)

    def METROSCENE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert("The next step is to consolidate your victory in {METROSCENE}. Check the area for signs of potential insurgency.".format(**self.elements))
            self.elements["CHALLENGE"].activate(camp)
            self.intro_ready = False

