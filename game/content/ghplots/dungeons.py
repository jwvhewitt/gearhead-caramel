from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services
from game.ghdialogue import context, OneShotInfoBlast
import gears
from gears import factions, personality
import game.content.gharchitecture
import pbge
import game.content.plotutility
from game.content import ghwaypoints, gharchitecture, plotutility, ghrooms
import game.content.ghterrain
from game.content.ghplots.dd_combatmission import CombatMissionSeed
import random
from .dd_main import DZDRoadMapExit
from . import missionbuilder
import collections


class TestDungeon(Plot):
    LABEL = "TEST_DUNGEON"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        intscene = gears.GearHeadScene(50, 50, "Test Dungeon", player_team=team1,
                                       attributes=(
                                       gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_RUINS),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.StoneBuilding(),
                                                   decorate=gharchitecture.DungeonDecor())
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident="METROSCENE")
        myanchor = random.choice(pbge.randmaps.anchors.EDGES)
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=myanchor, ),
                                      dident="LOCALE")

        mycon2 = plotutility.TownBuildingConnection(self, self.elements["METROSCENE"], intscene,
                                                    room2=foyer,
                                                    door1=ghwaypoints.UndergroundEntrance(name="The Ruins"),
                                                    door2=ghwaypoints.StoneStairsUp(anchor=pbge.randmaps.anchors.middle))

        self.rank = 15
        self.last_update = 0

        self.add_sub_plot(nart,"MONSTER_ENCOUNTER",elements={"TYPE_TAGS": ("ANIMAL", "VERMIN")})

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if camp.day > self.last_update:
            plotutility.dungeon_cleaner(camp.scene)
            self.last_update = camp.day

