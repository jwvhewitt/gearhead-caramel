from pbge.plots import Plot, Adventure, PlotState
import ghwaypoints
import ghterrain
import gharchitecture
import gears
import pbge
import pygame
from .. import teams,ghdialogue
from ..ghdialogue import context
from pbge.scenes.movement import Walking, Flying, Vision
from gears.geffects import Skimming, Rolling
import random
import copy
import os
from pbge.dialogue import Cue,ContextTag,Offer,Reply
from gears import personality,color,stats
import ghcutscene

class DeadZoneCombatMission( Plot ):
    # Go fight mecha. Repeatedly.
    LABEL = "DZD_COMBAT_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """The mission leadup will be two highway scenes with an intro, two
           encounters, a recharge, and two choices at the end. The choices
           will handle their own scenes."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)
        self.adv.world = myscene

        mygoal = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene))
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,100,None,myscene.environment).mecha_list
        print self.rank

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.FuzzyRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "_ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        self.mission_entrance = (myscene,myent)
        self.started_mission = False

        return True

    def t_UPDATE(self,camp):
        if not self.started_mission:
            camp.destination,camp.entrance = self.mission_entrance
            self.started_mission = True

    def t_ENDCOMBAT(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        self.adv.end_adventure(camp)
