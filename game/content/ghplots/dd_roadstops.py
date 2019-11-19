from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import game.content.gharchitecture
import pbge
import game.content.plotutility
import game.content.ghterrain
from dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints




class DZD_DeadZoneTown(Plot):
    LABEL = "DZD_ROADSTOP"
    active = True
    scope = True

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))

        myscene = gears.GearHeadScene(50, 50, self._generate_town_name(), player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=gears.factions.TerranFederation,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.City, gears.tags.SCENE_PUBLIC))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        npc2 = gears.selector.random_character(50, local_tags=myscene.attributes,job=gears.jobs.choose_random_job((gears.tags.Laborer,),self.elements["LOCALE"].attributes))
        npc2.place(myscene, team=team2)

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Police,),self.elements["LOCALE"].attributes)
        ))
        defender.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, game.content.gharchitecture.HumanScaleGreenzone(),
                                                     road_terrain=game.content.ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        mystory = self.register_element("BACKSTORY",game.content.backstory.Backstory(commands=("DZTOWN_FOUNDING",),elements={"LOCALE":self.elements["LOCALE"]},keywords=("DEMOCRACY",)))
        print " ".join(mystory.results["text"])

        self.register_element("METRO", myscene.metrodat)
        self.register_element("DZ_NODE_FRAME",RoadNode.FRAME_TOWN)

        myroom2 = self.register_element("_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.east),
                                        dident="LOCALE")
        towngate = self.register_element("ENTRANCE", DZDRoadMapExit(roadmap=self.elements["DZ_ROADMAP"],
                                                                    node=self.elements["DZ_NODE"],name="The Highway",
                                                                    desc="The highway stretches far beyond the horizon, all the way back to the green zone.",
                                                                    anchor=pbge.randmaps.anchors.east,
                                                                    plot_locked=True), dident="_ROOM2")
        # Gonna register the entrance under another name for the subplots.
        self.register_element("MISSION_GATE", towngate)

        # Add the order. This subplot will add a leader, guards, police, and backstory to the town.
        tplot = self.add_sub_plot(nart, "DZRS_ORDER")

        # Add the services.
        tplot = self.add_sub_plot(nart, "DZRS_GARAGE")
        tplot = self.add_sub_plot(nart, "DZRS_HOSPITAL")
        #tplot = self.add_sub_plot(nart, "DZDHB_EliteEquipment")
        #tplot = self.add_sub_plot(nart, "DZDHB_BlueFortress")
        #tplot = self.add_sub_plot(nart, "DZDHB_BronzeHorseInn")
        #tplot = self.add_sub_plot(nart, "DZDHB_LongRoadLogistics")
        # Black Isle Pub
        # Wujung Tires - Conversion supplies
        # Hwang-Sa Mission
        # Reconstruction Site

        # Add the local tarot.
        #threat_card = nart.add_tarot_card(self, (game.content.ghplots.dd_tarot.MT_THREAT,), )
        #game.content.mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0], steps=3)

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","Mount {}", "{}",
                          "Castle {}", "{} Ruins", "{} Spire")
    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

class DZD_DeadZoneVillage(Plot):
    LABEL = "DZD_ROADSTOP"
    active = True
    scope = True

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))

        myscene = gears.GearHeadScene(50, 50, self._generate_town_name(), player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=gears.factions.TerranFederation,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.Village, gears.tags.SCENE_PUBLIC))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Police,),self.elements["LOCALE"].attributes)
        ))
        defender.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, game.content.gharchitecture.HumanScaleDeadzone(),
                                                     road_terrain=game.content.ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        self.register_element("METRO", myscene.metrodat)
        self.register_element("DZ_NODE_FRAME",RoadNode.FRAME_VILLAGE)

        mystory = self.register_element("BACKSTORY",game.content.backstory.Backstory(commands=("DZTOWN_FOUNDING",),elements={"LOCALE":self.elements["LOCALE"]},keywords=("DEMOCRACY",)))
        print " ".join(mystory.results["text"])


        myroom2 = self.register_element("_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.east),
                                        dident="LOCALE")
        towngate = self.register_element("ENTRANCE", DZDRoadMapExit(roadmap=self.elements["DZ_ROADMAP"],
                                                                    node=self.elements["DZ_NODE"],name="The Highway",
                                                                    desc="The highway stretches far beyond the horizon, all the way back to the green zone.",
                                                                    anchor=pbge.randmaps.anchors.east,
                                                                    plot_locked=True), dident="_ROOM2")
        # Gonna register the entrance under another name for the subplots.
        self.register_element("MISSION_GATE", towngate)

        # Add the order. This subplot will add a leader, guards, police, and backstory to the town.
        tplot = self.add_sub_plot(nart, "DZRS_ORDER")

        # Add the services.
        tplot = self.add_sub_plot(nart, "DZRS_GARAGE")
        tplot = self.add_sub_plot(nart, "DZRS_HOSPITAL")
        #tplot = self.add_sub_plot(nart, "DZDHB_EliteEquipment")
        #tplot = self.add_sub_plot(nart, "DZDHB_BlueFortress")
        #tplot = self.add_sub_plot(nart, "DZDHB_BronzeHorseInn")
        #tplot = self.add_sub_plot(nart, "DZDHB_LongRoadLogistics")
        # Black Isle Pub
        # Wujung Tires - Conversion supplies
        # Hwang-Sa Mission
        # Reconstruction Site

        # Add the local tarot.
        #threat_card = nart.add_tarot_card(self, (game.content.ghplots.dd_tarot.MT_THREAT,), )
        #game.content.mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0], steps=3)

        return True

    TOWN_NAME_PATTERNS = ("{} Village","{} Hamlet","Camp {}","Mount {}", "{}", "{} Ruins" )
    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

#   **********************
#   ***   DZRS_ORDER   ***
#   **********************

class DemocraticOrder(Plot):
    # This town is governed by a mayor.
    LABEL = "DZRS_ORDER"

    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", game.content.ghterrain.ResidentialBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Town Hall")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "Town Hall", player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GOVERNMENT),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.ResidentialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")

        mycon2 = game.content.plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)


        npc = self.register_element("LEADER",
                                    gears.selector.random_character(
                                        self.rank, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mayor"]
                                    ))
        npc.place(intscene, team=team2)

        bodyguard = self.register_element(
            "BODYGUARD", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Military,),self.elements["LOCALE"].attributes)
        ))
        bodyguard.place(intscene, team=team2)

        return True

    def LEADER_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HELLO] Welcome to {}.".format(str(self.elements["LOCALE"])),
                            context=ContextTag([context.HELLO]),
                            ))

        return mylist



#   ***********************
#   ***   DZRS_GARAGE   ***
#   ***********************

class SomewhatOkayGarage(Plot):
    LABEL = "DZRS_GARAGE"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        npc_name,garage_name = self.generate_npc_and_building_name()
        building = self.register_element("_EXTERIOR", game.content.ghterrain.ScrapIronBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=garage_name)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, garage_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GARAGE, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.ScrapIronWorkshop())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")
        foyer.contents.append(ghwaypoints.MechEngTerminal())
        foyer.contents.append(ghwaypoints.MechaPoster())

        mycon2 = game.content.plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mechanic"]
                                    ))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.TerranDefenseForce,
                                  ware_types=services.GENERAL_STORE_PLUS_MECHA, rank=self.rank)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Welcome to {}, where [shop_slogan]!".format(str(self.elements["INTERIOR"])),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["INTERIOR"]), "wares": "good stuff"}
                            ))

        return mylist

    NAME_PATTERNS = ("{npc}'s Service","{town} Garage", "{npc}'s Sales & Service", "{npc}'s Mechastop")
    def generate_npc_and_building_name(self):
        npc_name = gears.selector.EARTH_NAMES.gen_word()
        building_name = random.choice(self.NAME_PATTERNS).format(npc=npc_name,town=str(self.elements["LOCALE"]))
        return npc_name,building_name


class FranklyBoringGarage(Plot):
    LABEL = "DZRS_GARAGE"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        npc_name,garage_name = self.generate_npc_and_building_name()
        building = self.register_element("_EXTERIOR", game.content.ghterrain.ScrapIronBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=garage_name)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, garage_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GARAGE),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.ScrapIronWorkshop())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")
        foyer.contents.append(ghwaypoints.MechEngTerminal())
        foyer.contents.append(ghwaypoints.MechaPoster())

        mycon2 = game.content.plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mechanic"]
                                    ))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.TerranDefenseForce,
                                  ware_types=services.BARE_ESSENTIALS_STORE, rank=self.rank - 15)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO]".format(str(self.elements["INTERIOR"])),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["INTERIOR"]), "wares": "essentials"}
                            ))

        return mylist

    NAME_PATTERNS = ("{npc}'s Garage","{town} Garage","{town} Repairs", "{town} Service Center", "{town} Fixit Shop")
    def generate_npc_and_building_name(self):
        npc_name = gears.selector.EARTH_NAMES.gen_word()
        building_name = random.choice(self.NAME_PATTERNS).format(npc=npc_name,town=str(self.elements["LOCALE"]))
        return npc_name,building_name


#   *************************
#   ***   DZRS_HOSPITAL   ***
#   *************************

class DeadzoneClinic(Plot):
    LABEL = "DZRS_HOSPITAL"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        myname = "{} Clinic".format(self.elements["LOCALE"])
        building = self.register_element("_EXTERIOR", game.content.ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.WoodenDoor(name=myname)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, myname, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_HOSPITAL),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.HospitalBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")

        mycon2 = game.content.plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc = self.register_element("DOCTOR",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Doctor"]))
        npc.place(intscene, team=team2)

        return True

    def DOCTOR_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] How are you feeling today?",
                            context=ContextTag([context.HELLO]),
                            ))

        return mylist



#   *********************
#   ***   DZRS_SHOP   ***
#   *********************


