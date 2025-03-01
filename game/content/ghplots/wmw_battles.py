import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, multimission, mission_bigobs
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections

class WMWMission(multimission.MultiMission):
    # Required Elements:
    #   METROSCENE, MISSION_GATE, WIN_FUN, LOSS_FUN
    #   TARGET_GATE, TARGET_SCENE
    #   ENEMY_FACTION, ALLIED_FACTION
    #   NUM_STAGES: The number of stages for this battle. Should be between 2 (hard) and 5 (hubris-destroying).
    # Optional Elements:
    #   COMBAT_MUSIC, EXPLORATION_MUSIC
    #   MISSION_GRAMMAR
    LABEL = "WMW_MISSION"

    def custom_init(self, nart):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["TARGET_SCENE"])
        self.elements["SCENE_GENERATOR"] = sgen
        self.elements["ARCHITECTURE"] = archi
        return super().custom_init(nart)

    def _build_mission_graph(self, nart):
        num_stages = self.elements.get("NUM_STAGES", 3)
        recovery_time = -25
        hard_battle = 0
        while num_stages > 1:
            if random.randint(1,100) <= recovery_time:
                self._add_stage(nart, "WMW_REPAIR_STAGE")
                recovery_time = -25
                hard_battle += 50
            elif random.randint(1,100) <= hard_battle:
                self._add_stage(nart, "WMW_HARD_STAGE")
                hard_battle = 0
            else:
                self._add_stage(nart, "WMW_BATTLE_STAGE")
                hard_battle += 20
            recovery_time += 50
            num_stages -= 1

        self._add_stage(nart, "WMW_FINAL_STAGE")

    def can_do_mission(self, camp):
        return bool(camp.get_usable_party(gears.scale.MechaScale, just_checking=True,
                                          enviro=self.elements["ARCHITECTURE"].ENV))


#   **************************
#   ***  WMW_BATTLE_STAGE  ***
#   **************************

class WMWBattleStage(multimission.MultiMissionStagePlot):
    LABEL = "WMW_BATTLE_STAGE"

    DESC_PATTERNS = (
        "You need to battle through the forces of {ENEMY_FACTION} to reach your destination.",
        "The battle to capture {TARGET_SCENE} from {ENEMY_FACTION} will be a long one."
    )

    def _build_stage(self, nart):
        self.DESC_PATTERN = random.choice(self.DESC_PATTERNS)
        self._add_stage_node(nart, "WMW_BATTLE_NODE")


class WMWDefaultBattleNode(multimission.MultiMissionNodePlot):
    LABEL = "WMW_BATTLE_NODE"
    NAME_PATTERN = "Capture territory held by {ENEMY_FACTION}"

    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_BUILDINGS)


#   **************************
#   ***  WMW_REPAIR_STAGE  ***
#   **************************

class WMWRepairStage(multimission.MultiMissionStagePlot):
    LABEL = "WMW_REPAIR_STAGE"

    DESC_PATTERNS = (
        "An opportunity presents itself to restore your equipment.",
        "The battle has begun to take its toll. Your lance is in need of rest, repair, and resupply."
    )

    stage_frame = multimission.MultiMissionStagePlot.STAGE_RESTORE

    def _build_stage(self, nart):
        self.DESC_PATTERN = random.choice(self.DESC_PATTERNS)
        self._add_stage_node(nart, "WMW_REPAIR_NODE")


class WMWDefaultRepairNode(multimission.MultiMissionNodePlot):
    LABEL = "WMW_REPAIR_NODE"
    NAME_PATTERN = "Acquire repair supplies currently held by {ENEMY_FACTION}"

    OBJECTIVES = (missionbuilder.BAMO_RECOVER_CARGO, missionbuilder.BAMO_CAPTURE_BUILDINGS)

    def _on_win(self, camp: gears.GearHeadCampaign):
        pbge.alert("Using the captured supplies, you are able to return your mecha to full fighting strength.")
        camp.totally_restore_party()
        super()._on_win(camp)


#   ************************
#   ***  WMW_HARD_STAGE  ***
#   ************************

class WMWHardContestedArea(multimission.MultiMissionStagePlot):
    LABEL = "WMW_HARD_STAGE"

    DESC_PATTERNS = (
        "This section of {TARGET_SCENE} is being fiercely contested by {ENEMY_FACTION} and {ALLIED_FACTION}. To proceed, you will need to secure a path through the fighting.",
    )

    stage_frame = multimission.MultiMissionStagePlot.STAGE_HARD

    def _build_stage(self, nart):
        self.DESC_PATTERN = random.choice(self.DESC_PATTERNS)
        self._add_stage_node(nart, "WMW_HARD_CAPTURE_TERRITORY")
        self._add_stage_node(nart, "WMW_HARD_SNEAK_THROUGH")
        self._add_stage_node(nart, "WMW_HARD_DEFAULT")


class WMWCaptureTerritory(multimission.MultiMissionNodePlot):
    LABEL = "WMW_HARD_CAPTURE_TERRITORY"
    NAME_PATTERN = "Capture and secure a beachhead for {ALLIED_FACTION}"

    OBJECTIVES = (mission_bigobs.BAMO_DEFEND_FORTRESS,)
    CASH_REWARD = 50


class WMWSneakThrough(multimission.MultiMissionNodePlot):
    LABEL = "WMW_HARD_SNEAK_THROUGH"
    NAME_PATTERN = "Attempt to sneak past {ENEMY_FACTION}"

    OBJECTIVES = (mission_bigobs.BAMO_BREAK_THROUGH,)
    CASH_REWARD = 50


class WMWDefaultHard(multimission.MultiMissionNodePlot):
    LABEL = "WMW_HARD_DEFAULT"
    NAME_PATTERN = "Leap straight into the thickest combat"

    OBJECTIVES = (missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_DEFEAT_ARMY)
    CASH_REWARD = 50



#   *************************
#   ***  WMW_FINAL_STAGE  ***
#   *************************

class WMWFinalStage(multimission.MultiMissionStagePlot):
    LABEL = "WMW_FINAL_STAGE"

    DESC_PATTERNS = (
        "The end of the mission is finally in sight; all that remains is to destroy the stronghold of {ENEMY_FACTION}.",
    )

    stage_frame = multimission.MultiMissionStagePlot.STAGE_CONCLUSION

    def _build_stage(self, nart):
        self.DESC_PATTERN = random.choice(self.DESC_PATTERNS)
        self._add_stage_node(nart, "WMW_FINAL_NODE")


class WMWDefaultFinalNode(multimission.MultiMissionNodePlot):
    LABEL = "WMW_FINAL_NODE"
    NAME_PATTERN = "Capture {TARGET_SCENE}"

    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_STORM_THE_CASTLE)

    CASH_REWARD = 150
    AUTO_RESTORE_AT_END = True

