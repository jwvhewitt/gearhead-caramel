import game.ghdialogue.ghgrammar
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services
from game.ghdialogue import context
import gears
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, ghrooms


# The plots in this unit all use the same interface for easy modding of cities.
# - The calling plot must pass a LOCALE scene. This is where the business will be placed.
# - The SHOP_* plot will include an INTERIOR scene and a SHOPKEEPER character.
# There are some optional elements:
# - An INTERIOR_TAGS element may be passed; this value defaults to (SCENE_PUBLIC,).
# - NPC_NAME and SHOP_NAME may be passed, and will be used instead of the randomly generated ones.
# - SHOP_FACTION may be passed to give the shop a faction. If None, it may be chosen randomly.
# - A CITY_COLORS element may be passed; if it exists, a custom palette will be used for building exteriors.
# If METROSCENE or MISSION_GATE might be needed, check for them in the matches class method. LOCALE is the only
#  passed element you can depend on.

def get_building(plot: Plot, bclass, **kwargs):
    # Note: This function relies upon the building type being standard. Don't call this for a weird building type
    # or a building type that doesn't have a colorizable version available. How to tell? Check the image/ folder for
    # a "terrain_building_whatever_u.png" file. As long as that exists, you should be good to go.
    if "CITY_COLORS" in plot.elements:
        image_name = bclass.TERRAIN_TYPE.image_top
        image_root = image_name.partition('.')[0]
        dd = {
            "image_bottom": bclass.TERRAIN_TYPE.image_bottom, "image_top": '{}_u.png'.format(image_root),
            "blocks": bclass.TERRAIN_TYPE.blocks,
            "colors": plot.elements["CITY_COLORS"]
        }
        mybuilding = bclass(duck_dict=dd, **kwargs)

    else:
        mybuilding = bclass(**kwargs)

    return mybuilding


#   **************************
#   ***  SHOP_BLACKMARKET  ***
#   **************************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION
#

class BasicBlackMarket(Plot):
    LABEL = "SHOP_BLACKMARKET"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Smuggler"]))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.BrickBuilding,
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=self.shopname)},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.BLACK_MARKET, rank=self.rank + 25,
                                  shop_faction=self.elements.get("SHOP_FACTION"), buy_stolen_items=True)

        return True

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Black Market", "{SHOPKEEPER}'s Goods", "{SHOPKEEPER}'s Contraband"
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(**self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] This is {}; remember, anything you buy here, you didn't get it from me.".format(self.shopname),
            context=ContextTag([context.HELLO]),
        ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "gear"},
                            ))

        return mylist


#   *********************
#   ***  SHOP_GARAGE  ***
#   *********************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION
#

class BasicGarage(Plot):
    LABEL = "SHOP_GARAGE"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Mechanic"]))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.IndustrialBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=(ghterrain.FixitShopSignEast, ghterrain.FixitShopSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.IndustrialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.FactoryDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.MECHA_STORE, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        foyer.contents.append(ghwaypoints.MechEngTerminal())

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Garage", "{LOCALE} Service Center", "{SHOPKEEPER}'s Mecha", "{SHOPKEEPER}'s Garage",
        "{SHOPKEEPER}'s {adjective} Bots", "{LOCALE} Heavy Machinery", "{SHOPKEEPER} Robotics",
        "{SHOPKEEPER}'s Combat Vehicles", "{LOCALE} Battlemovers", "{adjective} Mecha", "{adjective} Garage",
        "{SHOPKEEPER}'s {adjective} Machines",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Here at {}, [shop_slogan]!".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "mecha"},
                            ))

        return mylist


#   ***************************
#   ***  SHOP_GENERALSTORE  ***
#   ***************************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION
#

class BasicGeneralStore(Plot):
    LABEL = "SHOP_GENERALSTORE"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.BrickBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding(
            wall_terrain=ghterrain.DefaultWall))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.GENERAL_STORE, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        return True

    TITLE_PATTERNS = (
        "{LOCALE} General Store", "{SHOPKEEPER}'s Shop", "{LOCALE} Equipment", "{SHOPKEEPER}'s Gear",
        "{SHOPKEEPER}'s {adjective} Goods", "{adjective} Adventuring Supplies", "{LOCALE} {adjective} Shop",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] This is {}; we should have most anything you need.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "gear"},
                            ))

        return mylist


#   ***********************
#   ***  SHOP_HOSPITAL  ***
#   ***********************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION
#

class BasicHospital(Plot):
    LABEL = "SHOP_HOSPITAL"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        myjob = gears.jobs.choose_random_job((gears.tags.Medic,), self.elements["LOCALE"].attributes)
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=myjob))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.BrickBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=(ghterrain.HospitalSignEast, ghterrain.HospitalSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_HOSPITAL),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.HospitalBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.PHARMACY, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        room2 = self.register_element('_room2', pbge.randmaps.rooms.ClosedRoom(),dident="INTERIOR")
        room2.contents.append(ghwaypoints.RecoveryBed())
        room2.contents.append(ghwaypoints.RecoveryBed())

        if random.randint(1,10) == 5:
            cybershop = services.Shop(npc=None, rank=self.rank+random.randint(1,25),
                                      ware_types=services.CYBERWARE_STORE)
            room2.contents.append(ghwaypoints.CyberdocTerminal(shop=cybershop))

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Clinic", "{SHOPKEEPER}'s Clinic", "{LOCALE} Hospital", "{SHOPKEEPER}'s Medical Services",
        "{adjective} Medical", "{LOCALE} {adjective} Hospital", "{adjective} Hospital", "{LOCALE} Medical",
        "{adjective} Medicine"
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] [MEDICAL_GREETING]",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "medicine"},
                            ))

        return mylist


#   *********************
#   ***  SHOP_TAVERN  ***
#   *********************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION
#

class BasicTavern(Plot):
    LABEL = "SHOP_TAVERN"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Bartender"]))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element(
            "_EXTERIOR", get_building(self, ghterrain.ResidentialBuilding,
                waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
                door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
                tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM,
                      pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_MEETING, gears.tags.SCENE_CULTURE),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.ResidentialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(width=random.randint(20, 25),
                                                                                 height=random.randint(11, 15),
                                                                                 anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mybar = ghrooms.BarArea(random.randint(5, 10), random.randint(2, 3), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mybar)

        barteam = self.register_element("BAR_TEAM", teams.Team(name="Bar Team", allies=[team2]))
        mybar.contents.append(barteam)
        npc1.place(intscene, team=barteam)

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        self.add_sub_plot(nart, "TAVERN_BONUS", necessary=False)

        return True

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Tavern", "The {LOCALE} Tavern", "{SHOPKEEPER}'s Pub", "The {monster1} and {monster2}",
        "The {adjective} {monster1}", "{adjective} Tavern", "{adjective} Bar", "The {adjective} Pub"
    )

    def _generate_shop_name(self):
        monster1, monster2 = random.sample(gears.selector.MONSTER_LIST, 2)
        return random.choice(self.TITLE_PATTERNS).format(monster1=monster1, monster2=monster2, adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Welcome to {}.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        return mylist
