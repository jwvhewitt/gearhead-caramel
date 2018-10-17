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
import plotutility


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
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.SmallDeadZoneGround,myfilter,mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'

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
        self.register_element('WAYPOINT',waypoints.RetroComputer(),dident="_introom")

        world_scene = self.elements["WORLD"]

        wm_con = plotutility.WMCommTowerConnection(self,world_scene,myscene)
        if random.randint(1,3) != 1:
            wm_con.room1.tags = (dd_main.ON_THE_ROAD,)
        int_con = plotutility.IntCommTowerConnection(self,myscene,intscene,room1=mygoal,room2=introom)

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

#  **********************************
#  ***   DZD_CriminalEnterprise   ***
#  **********************************
#
# Add a hive of scum and villany to the game world.
# This place should include an OFFICE, where secret stuff might be hidden.
#

class BanditBase( Plot ):
    LABEL = "DZD_CriminalEnterprise"
    active = True
    scope = True

    def custom_init(self, nart):
        # Create the outer grounds with the bandits and their leader.
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Bandit Base Area",player_team=team1,scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.SmallDeadZoneGround,myfilter,mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        # Add the connection to the world map.
        mycon = plotutility.WMConcreteBuildingConnection(self,self.elements["WORLD"],myscene)
        if random.randint(1,10) == 1:
            mycon.room1.tags = (dd_main.ON_THE_ROAD,)

        # Add the goal room.
        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene))


        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        dimdiff = max(random.randint(1,5),random.randint(1,5))
        if random.randint(1,2) == 1:
            dimdiff = -dimdiff
        intscene = gears.GearHeadScene(35,35,"Bandit Base",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.DefaultWall)
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.OldTilesFloor,myfilter,mutate=None)
        intscenegen = pbge.randmaps.SceneGenerator(intscene,myarchi)
        self.register_scene( nart, intscene, intscenegen, ident="_interior" )
        introom = self.register_element('_introom',pbge.randmaps.rooms.OpenRoom(10+dimdiff,10-dimdiff,anchor=pbge.randmaps.anchors.south),dident="_interior")
        introom.DECORATE = pbge.randmaps.decor.OmniDec(win=ghterrain.Window)

        mycon2 = plotutility.IntConcreteBuildingConnection(self,myscene,intscene,room2=introom)

        self.register_element('WAYPOINT',waypoints.RetroComputer(),dident="_introom")


        introom2 = self.register_element('OFFICE',pbge.randmaps.rooms.OpenRoom(random.randint(5,8),random.randint(5,8)),dident="_interior")
        introom2.DECORATE = pbge.randmaps.decor.OmniDec(win=ghterrain.Window)


        return True


#  **************************
#  ***   DZD_RevealClue   ***
#  **************************

class SubcontractedCrime( Plot ):
    LABEL = "DZD_RevealClue"
    active = True
    scope = True
    def custom_init( self, nart ):
        # Create a filing cabinet or records computer for the PUZZLEITEM
        self.register_element("PUZZLEITEM",waypoints.RetroComputer(plot_locked=True))

        # Generate a criminal enterprise of some kind.
        cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        # Seek the OFFICE, and stick the filing thing in there.

        return True
    def PUZZLEITEM_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)


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
