from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from game.content.ghplots import dd_main
import game.content.plotutility
import game.content.gharchitecture

#  *****************************Town Hall
#  ***   ADD_REMOTE_OFFICE   ***
#  *****************************
#
#   We want to add some NPCs to this location, but we don't want them to be directly accessible to the PC.
#   This sticks the NPCs in a subscene that can't normally be accessed, but provides a method for providing
#   access later if you want.
#
#  FACTION: The Faction to add a remote office for
#  LOCALE:  The city in which they will be placed
#  METRO:   The scope for this plot

class BoringRemoteOffice( Plot ):
    LABEL = "ADD_REMOTE_OFFICE"
    active = True
    scope = "METRO"
    def custom_init( self, nart ):
        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "{} Base".format(self.elements["FACTION"]), player_team=team1,
                                       civilian_team=team2, scale=gears.scale.HumanScale, faction=self.elements["FACTION"])
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")

        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")
        foyer.contents.append(team2)
        # Add the NPCs.
        team2.contents.append(gears.selector.random_character(self.rank+10,job=self.elements["FACTION"].choose_job(gears.tags.Commander),combatant=True,faction=self.elements["FACTION"]))
        team2.contents.append(gears.selector.random_character(self.rank+5,job=self.elements["FACTION"].choose_job(gears.tags.Support),combatant=True,faction=self.elements["FACTION"]))
        for t in range(random.randint(1,2)):
            team2.contents.append(gears.selector.random_character(self.rank,faction=self.elements["FACTION"],
                                                                  job=self.elements["FACTION"].choose_job(
                                                                      gears.tags.Trooper), combatant=True))

        return True

#  ***************************************
#  ***   PLACE_LOCAL_REPRESENTATIVES   ***
#  ***************************************
#
#  FACTION: The faction to which the new NPCs will belong.

class PlaceACommander( Plot ):
    LABEL = "PLACE_LOCAL_REPRESENTATIVES"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        myjob = myfac.choose_job(gears.tags.Commander)
        mynpc = self.register_element("NPC",gears.selector.random_character(rank=random.randint(50,80),job=myjob,local_tags=myscene.attributes,combatant=True,faction=myfac),dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True
    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_ally_factions(candidate.faction,self.elements["FACTION"]))
    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes
