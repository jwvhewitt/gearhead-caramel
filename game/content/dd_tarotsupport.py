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


#  **************************
#  ***   DZD_LostPerson   ***
#  **************************
#
#  Elements:
#   PERSON: The NPC or prop who is lost. This element should be placed.
#

class LostPersonRadioTower( Plot ):
    LABEL = "DZD_LostPerson"
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

        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(10,10,"Radio Tower Interior",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.DefaultWall)
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.OldTilesFloor,myfilter,mutate=None)
        intscenegen = pbge.randmaps.SceneGenerator(intscene,myarchi)
        self.register_scene( nart, intscene, intscenegen, ident="_interior" )
        introom = self.register_element('_introom',pbge.randmaps.rooms.OpenRoom(7,7,anchor=pbge.randmaps.anchors.middle),dident="_interior")
        introom.DECORATE = pbge.randmaps.decor.OmniDec(win=ghterrain.Window)
        self.move_element(self.elements["PERSON"],introom)
        intscene.local_teams[self.elements["PERSON"]] = team2
        intexit = self.register_element( "_exit", waypoints.Exit(name="Exit",dest_scene=myscene,anchor=pbge.randmaps.anchors.south),dident="_introom")
        self.register_element('WAYPOINT',waypoints.RetroComputer(),dident="_introom")

        mytower = self.register_element("_tower",waypoints.DZDCommTower(anchor=pbge.randmaps.anchors.middle,dest_scene=intscene,dest_entrance=intexit),dident="_goalroom")
        intexit.dest_entrance = mytower

        world_scene = self.elements["WORLD"]
        wmroom = self.register_element("NEIGHBORHOOD", pbge.randmaps.rooms.FuzzyRoom(5, 5), dident="WORLD")
        if random.randint(1,3) != 1:
            wmroom.tags = (dd_main.ON_THE_ROAD,)
        mytown = self.register_element( "TOWN_ENTRANCE", game.content.waypoints.DZDWCommTower(dest_scene=myscene))
        wmroom.contents.append(mytown)

        myent = self.register_element( "ENTRANCE", waypoints.Exit(name="Exit",dest_scene=world_scene,dest_entrance=mytown,anchor=pbge.randmaps.anchors.south))
        myroom.contents.append( myent )
        mytown.dest_entrance = myent

        tplot = self.add_sub_plot(nart, "DZD_MECHA_ENCOUNTER", spstate=PlotState().based_on(self,{"ROOM":mygoal}), necessary=False)

        self.intro_ready = True

        return True
    def t_START(self,camp):
        if self.intro_ready:
            self.intro_ready = False

#  *******************************
#  ***   DZD_MECHA_ENCOUNTER   ***
#  *******************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   ROOM: The room where the encounter will take place
#

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


#  ****************************
#  ***   DZD_RevealMurder   ***
#  ****************************
#
#  Elements:
#   PERSON: The NPC being done away with.
#

class HideAndSeekWithACorpse( Plot ):
    LABEL = "DZD_RevealMurder"
    active = True
    scope = True
    def custom_init( self, nart ):
        mynpc = self.elements["PERSON"]
        mycorpse = self.register_element('PERSON',waypoints.Victim(plot_locked=True,name=mynpc.name))
        self.register_element('_the_deceased',mynpc)
        tplot = self.add_sub_plot(nart, "DZD_LostPerson")
        return True
    def PERSON_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)
    def PERSON_menu(self,thingmenu):
        pass
