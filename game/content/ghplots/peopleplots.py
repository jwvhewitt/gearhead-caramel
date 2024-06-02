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
from . import missionbuilder
import collections



#  **********************
#  ***   ADD_EXPERT   ***
#  **********************
# Add an elder or a professor or some other trove of local knowledge, presumably to give some local knowledge.

class RandomExpertNPC(Plot):
    LABEL = "ADD_EXPERT"
    JOB_NAMES = ("Scavenger", "Teacher", "Aristo", "Citizen", "Tekno", "Doctor", "Researcher")

    def custom_init(self, nart):
        npc = gears.selector.random_character(
            job = gears.jobs.ALL_JOBS[random.choice(self.JOB_NAMES)],
            age=random.randint(50,90),
            local_tags=tuple(self.elements["METROSCENE"].attributes)
        )
        self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_good_scene)
        self.register_element("NPC", npc, dident="LOCALE")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.SCENE_CULTURE in candidate.attributes

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  ***************************
#  ***   ADD_FAITHWORKER   ***
#  ***************************
# Add a faithworker of some type.

class RandomFaithworker(Plot):
    LABEL = "ADD_FAITHWORKER"
    JOB_NAMES = ("Priest", "Monk", "Warrior Monk", "Neodruid", "Technoshaman")

    def custom_init(self, nart):
        npc = gears.selector.random_character(
            job = gears.jobs.ALL_JOBS[random.choice(self.JOB_NAMES)],
            age=random.randint(50,90),
            local_tags=tuple(self.elements["METROSCENE"].attributes)
        )
        self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_good_scene)
        self.register_element("NPC", npc, dident="LOCALE")
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes and candidate.attributes.intersection({gears.tags.SCENE_CULTURE, gears.tags.SCENE_TEMPLE})

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
