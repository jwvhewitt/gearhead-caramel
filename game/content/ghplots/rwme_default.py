# RANDOM WORLD MAP ENCOUNTER PLOTS
import game.content
from pbge.plots import Plot,PlotState
import gears
import pbge
import random
from game.content import gharchitecture, plotutility
from . import missionbuilder, rwme_objectives


class TestRandomWorldMapEncounterObjective(Plot):
    LABEL = "TEST_RWMO"
    active = True
    scope = True

    # Needs METROSCENE, MISSION_GATE

    def custom_init( self, nart ):
        metroscene = self.elements["METROSCENE"]
        mission_gate = self.elements["MISSION_GATE"]
        self.myadv = missionbuilder.BuildAMissionSeed(
            nart.camp, "RWMO_TEST", metroscene, mission_gate,
            allied_faction = self.elements.get("ALLIED_FACTION", None),
            enemy_faction = self.elements.get("ENEMY_FACTION", None), rank=1,
            objectives = (rwme_objectives.RWMO_TEST_OBJECTIVE,),
            adv_type = "BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": mission_gate, "ENTRANCE_ANCHOR": pbge.randmaps.anchors.east},
            scenegen=gharchitecture.DeadZoneHighwaySceneGen,
            architecture=gharchitecture.MechaScaleSemiDeadzone(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            environment=gears.tags.GroundEnv,
            cash_reward=100,
        )

        return rwme_objectives.RWMO_TEST_OBJECTIVE in game.content.PLOT_LIST

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.myadv:
            thingmenu.add_item("Do the RWME Objective test.", self.myadv)



#   **********************
#   ***  RWMENCOUNTER  ***
#   **********************

class DefaultRandomWorldMapEncounter(Plot):
    LABEL = "RWMENCOUNTER"
    active = False
    scope = None

    ENCOUNTER_NAME = "Mecha Assault"
    ENCOUNTER_OBJECTIVES = (rwme_objectives.RWMO_FIGHT_RANDOS, rwme_objectives.RWMO_MAYBE_AVOID_FIGHT,)
    ENCOUNTER_CASH_REWARD = 0
    PRIORITY = 1

    def custom_init( self, nart ):
        return True

    def generate_world_map_encounter(self, camp, metroscene, return_wp, dest_scene, dest_wp,
                                     scenegen=gharchitecture.DeadZoneHighwaySceneGen,
                                     architecture=gharchitecture.MechaScaleSemiDeadzone,
                                     environment=gears.tags.GroundEnv, **kwargs):
        myanchor = kwargs.get("entrance_anchor", None)
        if not myanchor:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, self.ENCOUNTER_NAME, metroscene, return_wp,
            allied_faction = self.elements.get("ALLIED_FACTION", None),
            enemy_faction = self.elements.get("ENEMY_FACTION", None), rank=self.rank,
            objectives = self.ENCOUNTER_OBJECTIVES,
            adv_type = "BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": dest_wp, "ENTRANCE_ANCHOR": myanchor},
            scenegen=scenegen,
            architecture=architecture(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            environment=environment,
            cash_reward=self.ENCOUNTER_CASH_REWARD,
        )
        return myadv


class DistressCallEncounter(DefaultRandomWorldMapEncounter):
    ENCOUNTER_NAME = "Distress Call"
    ENCOUNTER_OBJECTIVES = (rwme_objectives.RWMO_DISTRESS_CALL,)
    ENCOUNTER_CASH_REWARD = 50
    PRIORITY = 5

