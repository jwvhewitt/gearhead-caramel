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
# - The calling plot must pass a LOCALE scene and a METRO. This is where the business will be placed.
# - The SHOP_* plot will include an INTERIOR scene and a SHOPKEEPER character.
# There are some optional elements:
# - An INTERIOR_TAGS element may be passed; this value defaults to (SCENE_PUBLIC,).
# - NPC_NAME and SHOP_NAME may be passed, and will be used instead of the randomly generated ones.
# - SHOP_FACTION may be passed to give the shop a faction. If None, it may be chosen randomly.
# - A CITY_COLORS element may be passed; if it exists, a custom palette will be used for building exteriors.
# If METROSCENE or MISSION_GATE might be needed, check for them in the matches class method. LOCALE and METRO are the
# only passed elements you can depend on.

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


#   ************************
#   ***  EMPTY_BUILDING  ***
#   ************************
#
#   Want to build your own shop or service? You can use this to start with. Generates an INTERIOR scene but not
#   a SHOPKEEPER. The building is, alas, empty.
#
#   Elements:
#       LOCALE
#   Optional:
#       INTERIOR_NAME, INTERIOR_TAGS, CITY_COLORS, INTERIOR_FACTION, DOOR_TYPE, DOOR_SIGN, EXTERIOR_TERRSET,
#       INTERIOR_ARCHITECTURE, INTERIOR_DECOR
#

class BasicEmptyBuilding(Plot):
    LABEL = "EMPTY_BUILDING"

    def custom_init(self, nart):
        self.interiorname = self.elements.get("INTERIOR_NAME", "") or "Building"

        # Create a building within the town.
        mydoor = self.elements.get("DOOR_TYPE") or ghwaypoints.GlassDoor
        mybuilding = self.elements.get("EXTERIOR_TERRSET") or ghterrain.BrickBuilding
        building = self.register_element("_EXTERIOR", get_building(
            self, mybuilding,
            waypoints={"DOOR": mydoor(name=self.interiorname)},
            door_sign=self.elements.get("DOOR_SIGN"),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            60, 60, self.interiorname, player_team=team1, civilian_team=team2, faction=self.elements.get("INTERIOR_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING,),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        myarchi = self.elements.get("INTERIOR_ARCHITECTURE") or gharchitecture.IndustrialBuilding
        mydecor = self.elements.get("INTERIOR_DECOR")
        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, myarchi(decorate=mydecor))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        return True


class BasicOfficeBuilding(Plot):
    LABEL = "OFFICE_BUILDING"

    def custom_init(self, nart):
        self.interiorname = self.elements.get("INTERIOR_NAME", "") or "Building"

        # Create a building within the town.
        mydoor = self.elements.get("DOOR_TYPE") or ghwaypoints.GlassDoor
        mybuilding = self.elements.get("EXTERIOR_TERRSET") or ghterrain.BrickBuilding
        building = self.register_element("_EXTERIOR", get_building(
            self, mybuilding,
            waypoints={"DOOR": mydoor(name=self.interiorname)},
            door_sign=self.elements.get("DOOR_SIGN"),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            60, 60, self.interiorname, player_team=team1, civilian_team=team2, faction=self.elements.get("INTERIOR_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING,),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        myarchi = self.elements.get("INTERIOR_ARCHITECTURE") or gharchitecture.IndustrialBuilding
        mydecor = self.elements.get("INTERIOR_DECOR")
        intscenegen = pbge.randmaps.SceneGenerator(intscene, myarchi(decorate=mydecor))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        return True


#   *********************
#   ***  RANDOM_SHOP  ***
#   *********************
#
#   To spice up a random place, add a random shop.
#   Elements:
#       LOCALE
#   Optional:
#       CITY_COLORS
#

class RandomShop(Plot):
    LABEL = "RANDOM_SHOP"

    SHOP_TYPES = (
        "SHOP_ARMORSTORE", "SHOP_WEAPONSTORE", "SHOP_MECHA",
        "SHOP_BLACKMARKET", "SHOP_GENERALSTORE", "SHOP_TAVERN", "SHOP_GARAGE"
    )

    def custom_init(self, nart):
        self.add_sub_plot(nart, random.choice(self.SHOP_TYPES))
        return True


#   *************************
#   ***  SHOP_ARMORSTORE  ***
#   *************************
#
#   This shop sells armor. That's it.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
#

class BasicArmorStore(Plot):
    LABEL = "SHOP_ARMORSTORE"
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
            self, ghterrain.CommercialBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.ShieldSignEast, ghterrain.ShieldSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        #if "CITY_COLORS" in self.elements:
        #    wall_terrain =

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(
            random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south,
            decorate=gharchitecture.ArmorShopDecor()
        ),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        mycounter = ghrooms.ShopCounterArea(random.randint(4, 6), random.randint(3, 5), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mycounter)
        salesteam = self.register_element("SALES_TEAM", teams.Team(name="Sales Team", allies=[team2]))
        mycounter.contents.append(salesteam)

        npc1.place(intscene, team=salesteam)

        self.shop = services.Shop(npc=npc1, ware_types=services.ARMOR_STORE, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Armor", "{SHOPKEEPER}'s Armor", "{LOCALE} Clothing", "{SHOPKEEPER}'s Combat Fashion",
        "{adjective} Armor", "{adjective} Clothing",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] This is {}; we have a good selection of armor.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "armor"},
                            ))

        return mylist


#   **************************
#   ***  SHOP_BLACKMARKET  ***
#   **************************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
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
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.SkullWallSignEast, ghterrain.SkullWallSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(
            random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south,
            decorate=gharchitecture.BlackMarketDecor()
        ), dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        mycounter = ghrooms.ShopCounterArea(random.randint(4, 6), random.randint(3, 5), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mycounter)
        salesteam = self.register_element("SALES_TEAM", teams.Team(name="Sales Team", allies=[team2]))
        mycounter.contents.append(salesteam)

        npc1.place(intscene, team=salesteam)

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


#   **************************
#   ***  SHOP_CYBERCLINIC  ***
#   **************************
#
#   A cyberclinic sells cyberware; it may offer other medical services.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
#

class BasicCyberclinic(Plot):
    LABEL = "SHOP_CYBERCLINIC"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Cyberdoc"]))
        npc1.name = self.elements.get("NPC_NAME", "") or npc1.name

        self.shopname = self.elements.get("SHOP_NAME", "") or self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.CommercialBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.CyberSignEast, ghterrain.CyberSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_HOSPITAL, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.CommercialBuilding(floor_terrain=ghterrain.WhiteTileFloor))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.PHARMACY, rank=self.rank + random.randint(0, 5),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        foyer.contents.append(ghwaypoints.Bunk())
        if random.randint(1,5) == 3:
            foyer.contents.append(ghwaypoints.EmptyBiotank())

        cybershop = services.Shop(npc=None, rank=self.rank + random.randint(10, 30),
                                  ware_types=services.CYBERWARE_STORE)
        foyer.contents.append(ghwaypoints.CyberdocTerminal(shop=cybershop))

        return True

    TITLE_PATTERNS = (
        "{LOCALE} {tech}", "{SHOPKEEPER}'s Cyberclinic", "{LOCALE} Cybershop", "{SHOPKEEPER}'s {tech}",
        "{adjective} {tech}", "{LOCALE} {adjective} {tech}", "{adjective} Cyberdoc", "{LOCALE} Body Modification",
        "{adjective} Cybershop"
    )
    TECH_WORDS = ("Cyberware", "Cybertech", "Molybdenum", "Bodymods", "Bodytech")

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]),
            tech=random.choice(self.TECH_WORDS), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Remember, at {INTERIOR} your [body_part] is in good hands.".format(**self.elements),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "drugs"},
                            ))

        mylist.append(Offer("You can use the cyberterminal over there to design your ideal body. Remember, all of our implants come with a lifetime guarantee.",
                            context=ContextTag([context.INFO]),
                            data={"subject": "cyberware"}, no_repeats=True
                            ))

        return mylist


#   *********************
#   ***  SHOP_GARAGE  ***
#   *********************
#
#   A garage is guaranteed to sell mecha and have a mecha engineering terminal. It may sell more, but that part at
#   least is guaranteed.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN (must be a tuple of (East, South).
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
            door_sign=self.elements.get("DOOR_SIGN") or self._generate_shop_sign(),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.IndustrialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south,
                                                                              decorate=gharchitecture.FactoryDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        wares = random.choice((services.MECHA_STORE, services.MEXTRA_STORE, services.GENERAL_STORE_PLUS_MECHA,
                               services.GENERAL_STORE_PLUS_MECHA, services.MEXTRA_STORE))
        self.shop = services.Shop(npc=npc1, ware_types=wares, rank=self.rank + random.randint(0, 10),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        foyer.contents.append(ghwaypoints.MechEngTerminal())

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Garage", "{LOCALE} Service Center", "{SHOPKEEPER}'s Mecha", "{SHOPKEEPER}'s Garage",
        "{SHOPKEEPER}'s {adjective} Bots", "{LOCALE} Heavy Machinery", "{SHOPKEEPER} Robotics",
        "{SHOPKEEPER}'s Combat Vehicles", "{LOCALE} Battlemovers", "{adjective} Service", "{adjective} Garage",
        "{SHOPKEEPER}'s {adjective} Machines",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def _generate_shop_sign(self):
        candidates = list()
        mycity: gears.GearHeadScene = self.elements["LOCALE"]
        candidates.append((ghterrain.FixitShopSignEast, ghterrain.FixitShopSignSouth))
        if gears.personality.DeadZone in mycity.attributes:
            candidates.append((ghterrain.RustyFixitShopSignEast, ghterrain.RustyFixitShopSignSouth))
        if gears.tags.City in mycity.attributes:
            candidates.append((ghterrain.MechaModelSignEast, ghterrain.MechaModelSignSouth))
        return random.choice(candidates)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Here at {}, [shop_slogan]!".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "stuff"},
                            ))

        return mylist


#   ***************************
#   ***  SHOP_GENERALSTORE  ***
#   ***************************
#
#   A general store is guaranteed to sell everything you need for personal scale exploration. It may sell more, but
#   that part at least is guaranteed.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
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
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.GeneralStoreSign1East, ghterrain.GeneralStoreSign1South),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding(
            wall_terrain=ghterrain.DefaultWall))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south,
                                                                              decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        mycounter = ghrooms.ShopCounterArea(random.randint(4, 6), random.randint(3, 5), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mycounter)
        salesteam = self.register_element("SALES_TEAM", teams.Team(name="Sales Team", allies=[team2]))
        mycounter.contents.append(salesteam)

        npc1.place(intscene, team=salesteam)

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
#   A hospital is guaranteed to sell medicine. It may offer other services, but that much is guaranteed.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
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
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.HospitalSignEast, ghterrain.HospitalSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_HOSPITAL),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.HospitalBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.PHARMACY, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        room2 = self.register_element('_room2', pbge.randmaps.rooms.ClosedRoom(), dident="INTERIOR")
        room2.contents.append(ghwaypoints.RecoveryBed())
        room2.contents.append(ghwaypoints.RecoveryBed())

        if random.randint(1, 10) == 5:
            cybershop = services.Shop(npc=None, rank=self.rank + random.randint(1, 25),
                                      ware_types=services.CYBERWARE_STORE)
            room2.contents.append(ghwaypoints.CyberdocTerminal(shop=cybershop))

        if random.randint(1, 3) == 2:
            self.add_sub_plot(nart, "HOSPITAL_BONUS")

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


#   ********************
#   ***  SHOP_MECHA  ***
#   ********************
#
#   A mecha shop is basically a garage but they only sell mecha. No extras.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN (must be a tuple of (East, South).
#

class BasicMechaShop(Plot):
    LABEL = "SHOP_MECHA"
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
            self, ghterrain.IndustrialBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.MechaModelSignEast, ghterrain.MechaModelSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.IndustrialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south,
                                                                              decorate=gharchitecture.FactoryDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.MECHA_STORE, rank=self.rank + random.randint(5, 20),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        foyer.contents.append(ghwaypoints.MechEngTerminal())

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Mecha", "{LOCALE} Meks", "{SHOPKEEPER}'s Mecha", "{SHOPKEEPER}'s Meks",
        "{SHOPKEEPER}'s {adjective} Bots", "{LOCALE} Combat Machinery", "{SHOPKEEPER} Robotics",
        "{SHOPKEEPER}'s Combat Vehicles", "{LOCALE} Battlemovers", "{adjective} Mecha", "{adjective} Meks",
        "{SHOPKEEPER}'s {adjective} Mecha",
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


#   *********************
#   ***  SHOP_TAVERN  ***
#   *********************
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
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
                                      door_sign=self.elements.get("DOOR_SIGN") or (
                                      ghterrain.TavernSign1East, ghterrain.TavernSign1South),
                                      tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM,
                                            pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_MEETING, gears.tags.SCENE_CULTURE),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
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

        myfloor = pbge.randmaps.rooms.Room(foyer.width - 2, foyer.height - mybar.height - 2,
                                           anchor=pbge.randmaps.anchors.south,
                                           decorate=gharchitecture.RestaurantDecor())
        foyer.contents.append(myfloor)

        self.add_sub_plot(nart, "TAVERN_BONUS", necessary=False)

        return True

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Tavern", "The {LOCALE} Tavern", "{SHOPKEEPER}'s Pub", "The {monster1} and {monster2}",
        "The {adjective} {monster1}", "{adjective} Tavern", "{adjective} Bar", "The {adjective} Pub"
    )

    def _generate_shop_name(self):
        monster1, monster2 = random.sample(gears.selector.MONSTER_LIST, 2)
        return random.choice(self.TITLE_PATTERNS).format(monster1=monster1, monster2=monster2, adjective=random.choice(
            game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Welcome to {}.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        return mylist

#   ***************************
#   ***  SHOP_WEAPONSTORE  ***
#   ***************************
#
#   This shop sells weapons. That's it.
#
#   Elements:
#       LOCALE
#   Optional:
#       NPC_NAME, SHOP_NAME, INTERIOR_TAGS, CITY_COLORS, SHOP_FACTION, DOOR_SIGN
#

class BasicWeaponStore(Plot):
    LABEL = "SHOP_WEAPONSTORE"
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
            self, ghterrain.CommercialBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.GunShopSignEast, ghterrain.GunShopSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=tuple(self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,))) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            exploration_music=self.elements["LOCALE"].exploration_music,
            combat_music=self.elements["LOCALE"].combat_music,
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(random.randint(10,15), random.randint(10,15), anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        mycounter = ghrooms.ShopCounterArea(random.randint(4, 6), random.randint(3, 5), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mycounter)
        salesteam = self.register_element("SALES_TEAM", teams.Team(name="Sales Team", allies=[team2]))
        mycounter.contents.append(salesteam)

        npc1.place(intscene, team=salesteam)

        self.shop = services.Shop(npc=npc1, ware_types=services.WEAPON_STORE, rank=self.rank + random.randint(0, 15),
                                  shop_faction=self.elements.get("SHOP_FACTION"))

        return True

    TITLE_PATTERNS = (
        "{LOCALE} Weapons", "{SHOPKEEPER}'s Shop", "{LOCALE} Weapons", "{SHOPKEEPER}'s Armaments",
        "{adjective} Weapons", "{adjective} Arms",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(game.ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] This is {}; we have a good selection of weapons.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "weapons"},
                            ))

        return mylist
