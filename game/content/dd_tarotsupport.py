# This unit contains support plots for tarot cards.
import game.content.waypoints
from pbge.plots import Plot, Chapter, PlotState
import waypoints
import ghterrain
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
import dd_main


class LostPersonRadioTower( Plot ):
    LABEL = "DDTS_LostPerson"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Radio Tower Area",player_team=team1,scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.DeadZoneGround,myfilter,mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.south)
        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.middle))
        mytower = self.register_element("_tower",waypoints.DZDCommTower(anchor=pbge.randmaps.anchors.middle),dident="_goalroom")


        world_scene = self.elements["WORLD"]
        wmroom = self.register_element("NEIGHBORHOOD", pbge.randmaps.rooms.FuzzyRoom(5, 5), dident="WORLD")
        if random.randint(1,3) != 1:
            wmroom.tags = (dd_main.ON_THE_ROAD,)
        mytown = self.register_element( "TOWN_ENTRANCE", game.content.waypoints.DZDWCommTower(dest_scene=myscene))
        wmroom.contents.append(mytown)

        myent = self.register_element( "ENTRANCE", waypoints.Exit(name="Exit",dest_scene=world_scene,dest_entrance=mytown,anchor=pbge.randmaps.anchors.south))
        myroom.contents.append( myent )
        mytown.dest_entrance = myent

        tplot = self.add_sub_plot(nart, "DZD_MECHA_ENCOUNTER", spstate=PlotState(elements={"ROOM":mygoal}).based_on(self), necessary=False)

        self.intro_ready = True

        return True
    def t_START(self,camp):
        if self.intro_ready:
            self.intro_ready = False

class RandoMechaEncounter( Plot ):
    LABEL = "DZD_MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.elements["ROOM"]
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,100,gears.factions.Circle(),myscene.environment).mecha_list
        return True
