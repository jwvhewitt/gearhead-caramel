# RANDOM WORLD MAP ENCOUNTER PLOTS
from pbge.plots import Plot,PlotState
import gears
import pbge
import random
from game.content import gharchitecture, plotutility
from . import missionbuilder, rwme_objectives


#   **********************
#   ***  RWMENCOUNTER  ***
#   **********************

class DefaultRandomWorldMapEncounter(Plot):
    LABEL = "RWMENCOUNTER"
    active = False
    scope = None

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
            camp, "Mecha Assault", metroscene, return_wp,
            enemy_faction = None, rank=self.rank,
            objectives = (rwme_objectives.RWMO_FIGHT_RANDOS, rwme_objectives.RWMO_MAYBE_AVOID_FIGHT,),
            adv_type = "BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": dest_wp, "ENTRANCE_ANCHOR": myanchor},
            scenegen=scenegen,
            architecture=architecture(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            environment=environment,
            cash_reward=0,
        )
        return myadv

