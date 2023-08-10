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
from . import missionbuilder, rwme_objectives, campfeatures, multimission
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
                self._add_stage(nart, "WMW_BATTLE_STAGE")
                recovery_time = -25
                hard_battle += 30
            elif random.randint(1,100) <= hard_battle:
                self._add_stage(nart, "WMW_BATTLE_STAGE")
                hard_battle = 0
            else:
                self._add_stage(nart, "WMW_BATTLE_STAGE")
                hard_battle += 10
            recovery_time += 50
            num_stages -= 1

        self._add_stage(nart, "WMW_BATTLE_STAGE")

    def can_do_mission(self, camp):
        return bool(camp.get_usable_party(gears.scale.MechaScale, just_checking=True,
                                          enviro=self.elements["ARCHITECTURE"].ENV))


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

    def create_mission(self, camp):
        return missionbuilder.BuildAMissionSeed(
            camp, self.NAME_PATTERN.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            self.elements.get("ENEMY_FACTION"), self.elements.get("ALLIED_FACTION"), self.rank,
            self.OBJECTIVES,
            custom_elements=self.elements.get("CUSTOM_ELEMENTS", None),
            scenegen=self.elements["SCENE_GENERATOR"], architecture=self.elements["ARCHITECTURE"],
            on_win=self._on_win, on_loss=self._on_loss,
            combat_music=self.elements.get("COMBAT_MUSIC"), exploration_music=self.elements.get("EXPLORATION_MUSIC"),
            data=self.elements.get("MISSION_DATA", {}),
            mission_grammar=self.elements.get("MISSION_GRAMMAR", {}),
            restore_at_end=False, auto_exit=True,
            call_win_loss_funs_after_card=True
        )

