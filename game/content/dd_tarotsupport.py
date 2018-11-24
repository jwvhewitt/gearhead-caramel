# This unit contains support plots for tarot cards.
import game.content.ghwaypoints
from pbge.plots import Plot, Chapter, PlotState
import ghwaypoints
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
import gharchitecture


#  **************************
#  ***   DZD_LostPerson   ***
#  **************************
#
#  Elements:
#   PERSON: The NPC or prop who is lost. This element should be placed.
#   GOALSCENE: The scene where the NPC can be found.

class LostPersonRadioTower( Plot ):
    LABEL = "DZD_LostPerson"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Radio Tower Area",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.middle))

        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(10,10,"Radio Tower Interior",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene,gharchitecture.DefaultBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="GOALSCENE" )

        introom = self.register_element('_introom',pbge.randmaps.rooms.OpenRoom(7,7,anchor=pbge.randmaps.anchors.middle,decorate=pbge.randmaps.decor.OmniDec(win=ghterrain.Window)),dident="GOALSCENE")
        self.move_element(self.elements["PERSON"],introom)
        intscene.local_teams[self.elements["PERSON"]] = team2
        self.register_element('WAYPOINT', ghwaypoints.RetroComputer(), dident="_introom")

        world_scene = self.elements["WORLD"]

        wm_con = plotutility.WMCommTowerConnection(self,world_scene,myscene)
        if random.randint(1,3) != 1:
            wm_con.room1.tags = (dd_main.ON_THE_ROAD,)
        int_con = plotutility.IntCommTowerConnection(self,myscene,intscene,room1=mygoal,room2=introom)

        tplot = self.add_sub_plot(nart, "DZD_MECHA_ENCOUNTER", spstate=PlotState().based_on(self,{"ROOM":mygoal}), necessary=False)
        return True

#  *******************************
#  ***   DZD_MECHA_ENCOUNTER   ***
#  *******************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   ROOM: The room where the encounter will take place
#

class RandoMechaEncounter( Plot ):
    # Fight some factionless mecha. What do they want? To pad the adventure.
    LABEL = "DZD_MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.elements["ROOM"]
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,100,None,myscene.environment).mecha_list
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
        mybandits = plotutility.RandomBanditCircle()
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Bandit Base Area",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        # Add the connection to the world map.
        mycon = plotutility.WMConcreteBuildingConnection(self,self.elements["WORLD"],myscene,door2_id="_exit")
        if random.randint(1,10) == 1:
            mycon.room1.tags = (dd_main.ON_THE_ROAD,)

        # Add the goal room and the bandits guarding it.
        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene))
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,),faction=mybandits),dident="_goalroom")
        my_unit = gears.selector.RandomMechaUnit(self.rank,100,mybandits,myscene.environment,add_commander=True)
        team2.contents += my_unit.mecha_list
        self.register_element("_commander",my_unit.commander)
        self.intro_ready = True

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        dimdiff = max(random.randint(0,4),random.randint(0,4))
        if random.randint(1,2) == 1:
            dimdiff = -dimdiff
        intscene = gears.GearHeadScene(35,35,"Bandit Base",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene,gharchitecture.DefaultBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="_interior" )
        introom = self.register_element('_introom',pbge.randmaps.rooms.ClosedRoom(10+dimdiff,10-dimdiff,anchor=pbge.randmaps.anchors.south,decorate=pbge.randmaps.decor.OmniDec(win=ghterrain.Window)),dident="_interior")

        mycon2 = plotutility.IntConcreteBuildingConnection(self,myscene,intscene,room1=mygoal,room2=introom)

        introom2 = self.register_element('OFFICE',pbge.randmaps.rooms.ClosedRoom(random.randint(7,10),random.randint(7,10),decorate=pbge.randmaps.decor.OmniDec(win=ghterrain.Window)),dident="_interior")

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False
    def _commander_offers(self,camp):
        mylist = list()
        mylist.append(Offer("This area is under the control of {}. Leave now or we'll [threat].".format(str(self.elements["_eteam"].faction)),
            context=ContextTag([context.ATTACK,])))
        mylist.append(Offer("[CHALLENGE]",
            context=ContextTag([context.CHALLENGE,]),  ))
        mylist.append(Offer("[WITHDRAW]",
            context=ContextTag([context.WITHDRAW,]), effect=self._withdraw ))
        return mylist
    def _withdraw(self,camp):
        myexit = self.elements["_exit"]
        myexit.unlocked_use(camp)

#  ***************************
#  ***   DZD_RevealBadge   ***
#  ***************************

class RB_CatchTheRaiders( Plot ):
    LABEL = "DZD_RevealBadge"
    active = True
    scope = True
    def custom_init( self, nart ):
        # Add an NPC to the town that needs a sheriff. This NPC will offer the mission.

        # Generate a criminal enterprise of some kind.
        #cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

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
        my_item = self.register_element("PUZZLEITEM", ghwaypoints.RetroComputer(plot_locked=True))

        # Generate a criminal enterprise of some kind.
        cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        # Seek the OFFICE, and stick the filing thing in there.
        self.elements["_room"] = cplot.elements["OFFICE"]
        self.move_element(my_item,self.elements["_room"])

        return True
    def PUZZLEITEM_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)
    def PUZZLEITEM_menu(self,camp,thingmenu):
        thingmenu.desc = "{} It seems to contain records belonging to {}.".format(thingmenu.desc,self.elements.get("PERSON"))


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
        mycorpse = self.register_element('PERSON', ghwaypoints.Victim(plot_locked=True, name=mynpc.name))
        self.register_element('_the_deceased',mynpc)
        tplot = self.add_sub_plot(nart, "DZD_LostPerson")
        self.elements["GOALSCENE"] = tplot.elements.get("GOALSCENE")
        self.intro_ready = True
        return True
    def PERSON_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)
        self.elements["PERSON"].remove(self.elements["GOALSCENE"])
    def PERSON_menu(self,camp,thingmenu):
        thingmenu.desc = "You find the body of {}, obviously murdered.".format(self.elements["_the_deceased"])
    def GOALSCENE_ENTER(self,camp):
        if self.intro_ready:
            #pbge.alert("You found the goalscene.")
            self.intro_ready = False