from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from game.content.ghplots import dd_main
import game.content.plotutility
import game.content.gharchitecture

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
        destscene = self.seek_element(nart,"_DEST",self._is_best_scene,scope=myscene,must_find=False)
        if not destscene:
            destscene = self.seek_element(nart,"_DEST",self._is_good_scene,scope=myscene)
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
