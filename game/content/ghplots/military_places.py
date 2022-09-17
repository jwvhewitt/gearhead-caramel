import game.ghdialogue.ghgrammar
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services
from game.ghdialogue import context
import gears
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, ghrooms

# Much like the shops_plus module, this module contains prefab places you can add to an adventure. In this case,
# these are miltary-themed places. Most of these will just add an empty building; it's up to the parent plot to fill
# them.

#   **********************
#   ***  MILTARY_TENT  ***
#   **********************
#
#   Just a tent with an interior.
#
#   Elements:
#       LOCALE
#   Optional:
#       TENT_NAME, INTERIOR_TAGS, TENT_FACTION
#

class BasicTent(Plot):
    LABEL = "MILITARY_TENT"

    def custom_init(self, nart):
        self.tentname = self.elements.get("TENT_NAME", "") or self._generate_tent_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.TentTerrset(
            waypoints={"DOOR": ghwaypoints.InvisibleExit(name=self.tentname,)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM],
            border=3
        ), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.tentname, player_team=team1, civilian_team=team2, faction=self.elements.get("TENT_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_BASE),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.TentArchitecture())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(8,12,anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        return True

    TITLE_PATTERNS = (
        "Tent {adjective} {number}", "Tent {letter}{number}"
    )
    LETTERS = (
        'A','B',"C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
        "Alpha", "Beta", "Gamma", "Delta"
    )
    NUMBERS = (
        "1","2","3","4","5","78","79","23","42","99"
    )

    def _generate_tent_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]),
            letter=random.choice(self.LETTERS), number=random.choice(self.NUMBERS)
        )


#   *******************
#   ***  MOBILE_HQ  ***
#   *******************
#
#   Just a mobile HQ with an interior.
#
#   Elements:
#       LOCALE
#   Optional:
#       HQ_NAME, INTERIOR_TAGS, HQ_FACTION
#

class BasicMobileHQ(Plot):
    LABEL = "MOBILE_HQ"

    def custom_init(self, nart):
        self.hqname = self.elements.get("HQ_NAME", "") or self._generate_hq_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.MobileHQTerrset(
            waypoints={"DOOR": ghwaypoints.InvisibleExit(name=self.hqname,)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM],
            border=3
        ), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.hqname, player_team=team1, civilian_team=team2, faction=self.elements.get("HQ_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_BASE),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.VehicleArchitecture())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', ghrooms.MobileHQRoom(20,9,anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        return True

    TITLE_PATTERNS = (
        "Mobile HQ {longnumber}", "Mobile HQ {letter}{number}", "Mobile HQ {letter}", "Mobile HQ {adjective}"
    )
    LETTERS = (
        "Alpha", "Beta", "Gamma", "Delta", "Omicron", "Omega", "Zeta", "Whiskey", "Tango", "Foxtrot"
    )
    NUMBERS = tuple(str(n) for n in range(10))
    LONGNUMBER = tuple("{:02d}".format(n) for n in range(100))

    def _generate_hq_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]),
            letter=random.choice(self.LETTERS), number=random.choice(self.NUMBERS),
            longnumber=random.choice(self.LONGNUMBER)
        )
