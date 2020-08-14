from pbge.plots import Plot
from game import teams
import gears
import pbge
from game.content import ghwaypoints, gharchitecture, plotutility, dungeonmaker
import random
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, DG_PARENT_SCENE


class GenericDungeonLevel(Plot):
    LABEL = "DUNGEON_GENERIC"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        intscene = gears.GearHeadScene(50, 50, self.elements[DG_NAME], player_team=team1,
                                       attributes=self.elements[DG_SCENE_TAGS],
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, self.elements[DG_ARCHITECTURE],
                                                   decorate=gharchitecture.DungeonDecor())
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident=DG_PARENT_SCENE,
                            temporary=self.elements[DG_TEMPORARY])

        self.last_update = 0

        for t in range(random.randint(3,5)):
            self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"TYPE_TAGS": self.elements[DG_MONSTER_TAGS]})

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if camp.day > self.last_update:
            dungeonmaker.dungeon_cleaner(camp.scene)
            self.last_update = camp.day


class TestDungeon(Plot):
    LABEL = "TEST_DUNGEON"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Test Dungeon", gharchitecture.StoneBuilding(), 10,
            monster_tags = ("ANIMAL", "CITY", "VERMIN")
        )
        self.elements["LOCALE"] = mydungeon.entry_level
        print(mydungeon.entry_level)

        myanchor = random.choice(pbge.randmaps.anchors.EDGES)
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=myanchor, ),
                                      dident="LOCALE")

        mycon2 = plotutility.TownBuildingConnection(self, self.elements["METROSCENE"], mydungeon.entry_level,
                                                    room2=foyer,
                                                    door1=ghwaypoints.UndergroundEntrance(name="The Ruins"),
                                                    door2=ghwaypoints.StoneStairsUp(
                                                        anchor=pbge.randmaps.anchors.middle))

        return True

