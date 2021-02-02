from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,GHNarrativeRequest,PLOT_LIST,mechtarot, dungeonmaker
from . import tarot_cards, missionbuilder
from game.memobrowser import Memo



class DZD_DeadZoneTown(Plot):
    LABEL = "DZD_ROADSTOP"
    active = True
    scope = True

    def custom_init(self, nart):
        town_name = self._generate_town_name()
        town_fac = self.register_element( "METRO_FACTION",
            gears.factions.Circle(nart.camp,parent_faction=gears.factions.DeadzoneFederation,name="the {} Council".format(town_name))
        )
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,), faction=town_fac)

        myscene = gears.GearHeadScene(50, 50, town_name, player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=town_fac,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.City, gears.tags.SCENE_PUBLIC))
        myscene.exploration_music = 'Komiku_-_06_-_Friendss_theme.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        npc2 = gears.selector.random_character(50, local_tags=myscene.attributes,job=gears.jobs.choose_random_job((gears.tags.Laborer,),self.elements["LOCALE"].attributes))
        npc2.place(myscene, team=team2)

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Police,),self.elements["LOCALE"].attributes),
                faction=town_fac
        ))
        defender.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, gharchitecture.HumanScaleGreenzone(),
                                                     road_terrain=ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        mystory = self.register_element("BACKSTORY",backstory.Backstory(commands=("DZTOWN_FOUNDING",),elements={"LOCALE":self.elements["LOCALE"]}))

        self.register_element("METRO", myscene.metrodat)
        self.register_element("METROSCENE", myscene)
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
        tplot = self.add_sub_plot(nart, "QOL_REPORTER")

        self.add_sub_plot(nart, "RANDOM_LANCEMATE")
        self.add_sub_plot(nart, "DZRS_FEATURE")

        # Add the local tarot.
        threat_card = nart.add_tarot_card(self, (tarot_cards.MT_THREAT,))
        mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0])

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","Mount {}", "{}",
                          "Castle {}", "{} Ruins", "{} Spire", "{} Village", "{} Town")
    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def METROSCENE_ENTER(self, camp):
        # Upon entering this scene, deal with any dead or incapacitated party members.
        # Also, deal with party members who have lost their mecha. This may include the PC.
        camp.home_base = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        etlr = plotutility.EnterTownLanceRecovery(camp, self.elements["METROSCENE"], self.elements["METRO"])
        if not etlr.did_recovery:
            # We can maybe load a lancemate scene here. Yay!
            if not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT):
                nart = GHNarrativeRequest(camp, pbge.plots.PlotState().based_on(self), adv_type="DZD_LANCEDEV", plot_list=PLOT_LIST)
                if nart.story:
                    nart.build()

class DZD_DeadZoneVillage(Plot):
    LABEL = "DZD_ROADSTOP"
    active = True
    scope = True

    def custom_init(self, nart):
        town_name = self._generate_town_name()
        town_fac = self.register_element( "METRO_FACTION",
            gears.factions.Circle(nart.camp,parent_faction=gears.factions.DeadzoneFederation,name="the {} Council".format(town_name))
        )
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,), faction=town_fac)

        myscene = gears.GearHeadScene(50, 50, town_name, player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=town_fac,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.Village, gears.tags.SCENE_PUBLIC))
        myscene.exploration_music = 'Komiku_-_06_-_Friendss_theme.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Police,),self.elements["LOCALE"].attributes),
                faction=town_fac
        ))
        defender.place(myscene, team=team2)

        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.HumanScaleDeadzone(),)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        self.register_element("METRO", myscene.metrodat)
        self.register_element("METROSCENE", myscene)
        self.register_element("DZ_NODE_FRAME",RoadNode.FRAME_VILLAGE)

        mystory = self.register_element("BACKSTORY",backstory.Backstory(commands=("DZTOWN_FOUNDING",),elements={"LOCALE":self.elements["LOCALE"]}))

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
        tplot = self.add_sub_plot(nart, "QOL_REPORTER")

        self.add_sub_plot(nart, "RANDOM_LANCEMATE")
        self.add_sub_plot(nart, "DZRS_FEATURE")

        # Add the local tarot.
        threat_card = nart.add_tarot_card(self, (tarot_cards.MT_THREAT,))
        mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0])

        return True

    TOWN_NAME_PATTERNS = ("{} Village","{} Hamlet","Camp {}","Mount {}", "{}", "{} Ruins" )
    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def METROSCENE_ENTER(self, camp):
        # Upon entering this scene, deal with any dead or incapacitated party members.
        # Also, deal with party members who have lost their mecha. This may include the PC.
        camp.home_base = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        etlr = plotutility.EnterTownLanceRecovery(camp, self.elements["METROSCENE"], self.elements["METRO"])
        if not etlr.did_recovery:
            # We can maybe load a lancemate scene here. Yay!
            if not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT):
                nart = GHNarrativeRequest(camp, pbge.plots.PlotState().based_on(self), adv_type="DZD_LANCEDEV", plot_list=PLOT_LIST)
                if nart.story:
                    nart.build()


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
        building = self.register_element("_EXTERIOR", ghterrain.ResidentialBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Town Hall")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",faction=self.elements["METRO_FACTION"])
        intscene = gears.GearHeadScene(35, 35, "Town Hall", player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC,gears.tags.SCENE_BUILDING, gears.tags.SCENE_GOVERNMENT),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.ResidentialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)


        npc = self.register_element("LEADER",
                                    gears.selector.random_character(
                                        self.rank, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mayor"],
                                        faction = self.elements["METRO_FACTION"]
                                    ))
        npc.place(intscene, team=team2)

        self.town_origin_ready = True

        bodyguard = self.register_element(
            "BODYGUARD", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Military,),self.elements["LOCALE"].attributes),
                faction = self.elements["METRO_FACTION"]
        ))
        bodyguard.place(intscene, team=team2)

        return True

    def _tell_town_origin(self,camp):
        self.town_origin_ready = False

    def LEADER_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HELLO] Welcome to {}.".format(str(self.elements["LOCALE"])),
                            context=ContextTag([context.HELLO]),
                            ))

        if self.town_origin_ready:
            mylist.append(Offer(" ".join(self.elements["BACKSTORY"].results["text"]),
                                context=ContextTag([context.INFO]),effect=self._tell_town_origin,
                                data={"subject":"this place"}, no_repeats=True
                                ))

        return mylist

class MilitaryOrder(Plot):
    # This town is governed by a warlord.
    LABEL = "DZRS_ORDER"

    active = True
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        """Returns True if this town has a CONFLICT background."""
        return pstate.elements["BACKSTORY"] and "CONFLICT" in pstate.elements["BACKSTORY"].generated_state.keywords

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.ScrapIronBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Town Hall")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",faction=self.elements["METRO_FACTION"])
        intscene = gears.GearHeadScene(35, 35, "Town Hall", player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GOVERNMENT),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.FortressBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)


        npc = self.register_element("LEADER",
                                    gears.selector.random_character(
                                        self.rank, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Warlord"],
                                        faction = self.elements["METRO_FACTION"]
                                    ))
        npc.place(intscene, team=team2)

        self.town_origin_ready = True

        bodyguard = self.register_element(
            "BODYGUARD", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Military,),self.elements["LOCALE"].attributes),
                faction = self.elements["METRO_FACTION"]
        ))
        bodyguard.place(intscene, team=team2)

        return True

    def _tell_town_origin(self,camp):
        self.town_origin_ready = False

    def LEADER_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HELLO] This is {}.".format(str(self.elements["LOCALE"])),
                            context=ContextTag([context.HELLO]),
                            ))

        if self.town_origin_ready:
            mylist.append(Offer(" ".join(self.elements["BACKSTORY"].results["text"]),
                                context=ContextTag([context.INFO]),effect=self._tell_town_origin,
                                data={"subject":"this place"}, no_repeats=True
                                ))

        return mylist


class TechnocraticOrder(Plot):
    # This town is governed by a technocrat.
    LABEL = "DZRS_ORDER"

    active = True
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        """Returns True if this town has a SPACE background."""
        return pstate.elements["BACKSTORY"] and "SPACE" in pstate.elements["BACKSTORY"].generated_state.keywords

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Town Hall")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",faction=self.elements["METRO_FACTION"])
        intscene = gears.GearHeadScene(35, 35, "Town Hall", player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GOVERNMENT),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding(floor_terrain=ghterrain.WhiteTileFloor))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc = self.register_element("LEADER",
                                    gears.selector.random_character(
                                        self.rank, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Technocrat"],
                                        faction = self.elements["METRO_FACTION"]
                                    ))
        npc.place(intscene, team=team2)

        self.town_origin_ready = True

        bodyguard = self.register_element(
            "BODYGUARD", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Adventurer,),self.elements["LOCALE"].attributes),
                faction = self.elements["METRO_FACTION"]
        ))
        bodyguard.place(intscene, team=team2)

        return True

    def _tell_town_origin(self,camp):
        self.town_origin_ready = False

    def LEADER_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HELLO] You are in {}.".format(str(self.elements["LOCALE"])),
                            context=ContextTag([context.HELLO]),
                            ))

        if self.town_origin_ready:
            mylist.append(Offer(" ".join(self.elements["BACKSTORY"].results["text"]),
                                context=ContextTag([context.INFO]),effect=self._tell_town_origin,
                                data={"subject":"this place"}, no_repeats=True
                                ))

        return mylist

class VaultOrder(Plot):
    LABEL = "DZRS_ORDER"

    active = True
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        """Returns True if this town has a FALLOUT_SHELTER background."""
        return pstate.elements["BACKSTORY"] and "FALLOUT_SHELTER" in pstate.elements["BACKSTORY"].generated_state.keywords

    def custom_init(self, nart):
        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",faction=self.elements["METRO_FACTION"])
        intscene = gears.GearHeadScene(35, 35, "Fallout Shelter", player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GOVERNMENT, gears.tags.SCENE_RUINS),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room2=foyer, door1=ghwaypoints.UndergroundEntrance(name="Fallout Shelter"))

        npc = self.register_element("LEADER",
                                    gears.selector.random_character(
                                      self.rank, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mayor"],
                                        faction = self.elements["METRO_FACTION"]
                                    ))
        npc.place(intscene, team=team2)

        self.town_origin_ready = True

        bodyguard = self.register_element(
            "BODYGUARD", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Adventurer,),self.elements["LOCALE"].attributes),
                faction = self.elements["METRO_FACTION"]
        ))
        bodyguard.place(intscene, team=team2)

        return True

    def _tell_town_origin(self,camp):
        self.town_origin_ready = False

    def LEADER_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HELLO] Welcome to the heart of {}.".format(str(self.elements["LOCALE"])),
                            context=ContextTag([context.HELLO]),
                            ))

        if self.town_origin_ready:
            mylist.append(Offer(" ".join(self.elements["BACKSTORY"].results["text"]),
                                context=ContextTag([context.INFO]),effect=self._tell_town_origin,
                                data={"subject":"this place"}, no_repeats=True
                                ))

        return mylist


#   ***********************
#   ***   DZRS_GARAGE   ***
#   ***********************

# Prototypical road stop Garage.
class SomewhatOkayGarage(Plot):
    LABEL = "DZRS_GARAGE"

    active = True
    scope = "INTERIOR"

    # Settings
    GarageBuilding = ghterrain.ScrapIronBuilding
    GarageDoor = ghwaypoints.ScrapIronDoor
    door_sign = (ghterrain.RustyFixitShopSignEast, ghterrain.RustyFixitShopSignSouth)
    GarageArchitecture = gharchitecture.ScrapIronWorkshop
    additional_waypoints = (ghwaypoints.MechEngTerminal, ghwaypoints.MechaPoster)
    SHOPKEEPER_JOBS = ("Mechanic",)
    SHOPKEEPER_GREETING = "[HELLO] Welcome to {}, where [shop_slogan]!"
    shop_faction = None
    shop_ware_types = services.GENERAL_STORE_PLUS_MECHA
    shop_wares = "good stuff"
    @property
    def shop_rank(self):
        return self.rank // 2
    NAME_PATTERNS = ("{npc}'s Service","{town} Garage", "{npc}'s Sales & Service", "{npc}'s Mechastop")

    def custom_init(self, nart):
        # Create a building within the town.
        npc_name,garage_name = self.generate_npc_and_building_name()
        building = self.register_element("_EXTERIOR", self.GarageBuilding(
            waypoints={"DOOR": self.GarageDoor(name=garage_name)},
            door_sign=self.door_sign,
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, garage_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, self.GarageArchitecture())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")
        for item in self.additional_waypoints:
            foyer.contents.append(item())

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        job = random.choice(self.SHOPKEEPER_JOBS)
        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name, local_tags=self.elements["LOCALE"].attributes,
                                        job=gears.jobs.ALL_JOBS[job]
                                    ))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=self.shop_faction,
                                  ware_types=self.shop_ware_types, rank=self.shop_rank)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer(self.SHOPKEEPER_GREETING.format(str(self.elements["INTERIOR"])),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["INTERIOR"]), "wares": self.shop_wares}
                            ))

        return mylist

    def generate_npc_and_building_name(self):
        npc_name = gears.selector.EARTH_NAMES.gen_word()
        building_name = random.choice(self.NAME_PATTERNS).format(npc=npc_name,town=str(self.elements["LOCALE"]))
        return npc_name,building_name


class FranklyBoringGarage(SomewhatOkayGarage):
    active = True

    NAME_PATTERNS = ("{npc}'s Garage","{town} Garage","{town} Repairs", "{town} Service Center", "{town} Fixit Shop")
    SHOPKEEPER_GREETING = "[HELLO]"
    shop_ware_types = services.BARE_ESSENTIALS_STORE
    shop_wares = "essentials"

    @property
    def shop_rank(self):
        return self.rank // 4


class ScavengerGarage(SomewhatOkayGarage):
    active = True

    NAME_PATTERNS = ("{npc}'s Salvage Shop", "{town} Recycling Center", "{npc}'s Spare Parts", "{town} Mecha Accessories")
    SHOPKEEPER_GREETING = "[HELLO]"
    shop_ware_types = services.MECHA_PARTS_STORE + services.TIRE_STORE + services.ARMOR_STORE + services.WEAPON_STORE
    shop_wares = "parts"


class DeadzoneMechaShop(SomewhatOkayGarage):
    active = True
    UNIQUE = True

    NAME_PATTERNS = ("{npc}'s Chop Shop", "{town} Mecha Trading Post", "{npc}'s Redesigned Mecha", "{npc}'s Design Center")
    door_sign = (ghterrain.FixitShopSignEast, ghterrain.FixitShopSignSouth)
    SHOPKEEPER_GREETING = "[HELLO] Please be reminded, this is a mecha designer's workshop, not a salvage operation."
    additional_waypoints = (ghwaypoints.MechEngTerminal, ghwaypoints.MechaPoster, ghwaypoints.MechaModel, ghwaypoints.GoldPlaque)
    shop_faction = gears.factions.DeadzoneFederation
    shop_ware_types = services.MECHA_STORE
    show_wares = "mecha"

    @property
    def shop_rank(self):
        return self.rank


class GeneralStore(SomewhatOkayGarage):
    active = True

    NAME_PATTERNS = ("Trader {npc}'s", "{town} Buy&Sell", "{town} Trading Post", "{town} Shopping Boulevard", "{town} Mall")
    SHOPKEEPER_GREETING = "[HELLO] Welcome to {}! Enjoy our newly refurbished Mecha Engineering Terminal! Hasn't exploded in the past year!"
    shop_ware_types = services.GENERAL_STORE
    shop_wares = "equipment"
    SHOPKEEPER_JOBS = ("Shopkeeper", "Trader")
    additional_waypoints = (ghwaypoints.MechEngTerminal, ghwaypoints.VendingMachine)

    @property
    def shop_rank(self):
        return self.rank // 4


#   *************************
#   ***   DZRS_HOSPITAL   ***
#   *************************

class DeadzoneClinic(Plot):
    LABEL = "DZRS_HOSPITAL"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        self.myname = "{} Clinic".format(self.elements["LOCALE"])
        building = self.register_element("_EXTERIOR", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.WoodenDoor(name=self.myname)},
            door_sign=(ghterrain.HospitalSignEast, ghterrain.HospitalSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, self.myname, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_HOSPITAL),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.HospitalBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")

        foyer.contents.append(ghwaypoints.RecoveryBed())

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc = self.register_element("DOCTOR",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Doctor"]))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(services.PHARMACY, allow_misc=False, caption="Pharmacy", rank=self.rank, npc=npc)

        return True

    def DOCTOR_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] How are you feeling today?",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.myname, "wares": "medicine"}
                            ))

        return mylist


class AmateurCyberdoc(Plot):
    LABEL = "DZRS_HOSPITAL"

    active = True
    scope = "INTERIOR"
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.register_element("DOCTOR",
                                    gears.selector.random_character(50, local_tags=self.elements["METROSCENE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Tekno"]))

        # Create a building within the town.
        self.myname = "{} Medical".format(npc)
        building = self.register_element("_EXTERIOR", ghterrain.ScrapIronBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=self.myname)},
            door_sign=(ghterrain.HospitalSignEast, ghterrain.HospitalSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, self.myname, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_HOSPITAL),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.ScrapIronWorkshop())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(12,10,anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")

        foyer.contents.append(ghwaypoints.RecoveryBed())
        foyer.contents.append(ghwaypoints.RecoveryBed())
        foyer.contents.append(ghwaypoints.Biotank(name="Biotank",desc="You peer through the glass to see what's inside. This tank is being used as a storage bin for spare organs and second hand cyberware."))
        foyer.contents.append(ghwaypoints.Bookshelf(name="Bookshelf", desc="The top shelf is full of PreZero medical texts. The second shelf is full of contemporary tech magazines. The lower shelves are crammed with spare mechanical components and comic books."))
        foyer.contents.append(ghwaypoints.RetroComputer(name="Computer", desc="Someone has been playing 'Princess Wrestler Genesis'."))

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        cybershop = services.Shop( npc = None
                                 , rank = 70, num_items=5
                                 , ware_types = services.CYBERWARE_STORE
                                 )
        foyer.contents.append(ghwaypoints.CyberdocTerminal(shop = cybershop))


        npc.place(intscene, team=team2)

        myrobot = gears.selector.get_design_by_full_name("Workbot")
        myrobot.name = "A-00 Medical Bot"
        myrobot.place(intscene, team=team2)

        self.shop = services.Shop(services.PHARMACY, allow_misc=False, caption="Pharmacy", rank=self.rank, npc=npc)
        self.asked_question = False
        self.asked_other_question = False

        return True

    def DOCTOR_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Welcome to {METROSCENE}'s premiere medical establishment.".format(**self.elements),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.myname, "wares": "drugs"}
                            ))

        if not self.asked_question:
            mylist.append(Offer("Well, no, but I've read a lot of medical books, and I programmed tons of information into A-woo over there. Our village didn't have a doctor so I decided it'd be better to build one myself rather than do without.",
                                context=ContextTag([context.CUSTOM]), effect=self._ask_question,
                                data={"reply": "You're not actually a doctor, are you?"}
                                ))
        elif not self.asked_other_question:
            mylist.append(Offer("You're a curious person; I can respect that. Well, you know, it's no problem to get all kinds of organs in the dead zone if you know who to ask. The problem, usually, is getting the right ones for the job that needs doing.",
                                context=ContextTag([context.CUSTOM]), effect=self._ask_other_question,
                                data={"reply": "Where do you get all of these body parts?"}
                                ))

        return mylist

    def _ask_question(self, camp):
        self.asked_question = True

    def _ask_other_question(self, camp):
        self.asked_other_question = True


#   ************************
#   ***   DZRS_FEATURE   ***
#   ************************
# Weapon Shop
# Armor Shop
# Lostech Shop
# Trading Hub
# Synth Dungeon
# Lucky Crystal
# Thrunet Node
# Local Bar Needs Entertainment
# Mine Monster
# Retired Cavalier Dojo
# Abandoned video production facility- Director needs next script, which is lost in ruins.

class TreasureCave(Plot):
    LABEL = "DZRS_FEATURE"

    active = True
    scope = "METRO"
    UNIQUE = True

    def custom_init(self, nart):
        # Create the cave dungeon.
        self.area_name = '{} Caves'.format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], self.area_name,
            gharchitecture.EarthCave(), self.rank,
            monster_tags=("MUTANT", "SYNTH", "EARTH", "CAVE"),
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_SEMIPUBLIC,),
            decor=gharchitecture.CaveDecor(),
        )
        self.elements["DUNGEON"] = mydungeon.entry_level
        self.elements["DGOAL"] = mydungeon.goal_level

        # Add the dungeon entry room.
        mymapgen = nart.get_map_generator(mydungeon.entry_level)
        d_entrance_room = self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=pbge.randmaps.anchors.south))
        mydungeon.entry_level.contents.append(d_entrance_room)

        myent = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(
                anchor=pbge.randmaps.anchors.middle,
                dest_scene=self.elements["METROSCENE"],
                dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Add the treasure room.
        troom = self.register_element("TREASURE_ROOM", pbge.randmaps.rooms.OpenRoom(10, 10), dident="DGOAL")
        mychest = self.register_element("GOAL", ghwaypoints.Crate(name="Crate", anchor=pbge.randmaps.anchors.middle), dident="TREASURE_ROOM")
        mychest.contents += gears.selector.get_random_loot(self.rank+15,250,(gears.tags.ST_TREASURE, gears.tags.ST_LOSTECH, gears.tags.ST_WEAPON))

        myteam = self.register_element("_eteam", teams.Team(enemies=(mydungeon.goal_level.player_team,)), dident="TREASURE_ROOM")
        myteam.contents += gears.selector.RandomMonsterUnit(self.rank+20, 200, mydungeon.goal_level.environment,
                                                            ("ROBOT","SYNTH","GUARD"), mydungeon.goal_level.scale).contents

        # Add the unlock computer.
        compyscene = self.register_element("COMPY_SCENE", random.choice(mydungeon.levels))
        compyroom = self.register_element("COMPY_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5), dident="COMPY_SCENE")
        mycompy = self.register_element("COMPY", ghwaypoints.OldTerminal(name="Computer", plot_locked=True, anchor=pbge.randmaps.anchors.middle), dident="COMPY_ROOM")

        #print(self.elements["METROSCENE"])
        self.dungeon_unlocked = False
        self.compy_hacked = False
        return True

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.desc = "You stand before an old computer security terminal."
        if not self.compy_hacked:
            thingmenu.add_item("Leave it alone.", None)

            mypc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, no_random=True)
            if mypc:
                if mypc == camp.pc:
                    thingmenu.add_item("Disable the security protocols.", self._hack_compy)
                else:
                    thingmenu.add_item("Ask {} to disable the security protocols.".format(mypc), self._hack_compy)

    def _hack_compy(self, camp):
        self.compy_hacked = True
        self.elements["_eteam"].make_allies(self.elements["DGOAL"].player_team)
        pbge.alert("The security protocols have been disabled.")

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.dungeon_unlocked:
            thingmenu.add_item("Go to {}.".format(self.area_name), self.go_to_locale)

    def go_to_locale(self, camp):
        camp.destination, camp.entrance = self.elements["DUNGEON"], self.elements["ENTRANCE"]

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if not self.dungeon_unlocked:
            mygram["[News]"] = ["there is hidden bandit treasure in {}".format(self.area_name,), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.dungeon_unlocked:
            goffs.append(Offer(
                msg="The way the story goes, years ago there was a bandit gang around here and they amassed a huge amount of treasure. They hid it in one of the nearby caves, but for whatever reason never came back to collect it. Maybe they forgot the password?".format(
                    **self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=self.area_name, data={"subject": self.area_name}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self, camp):
        self.dungeon_unlocked = True
        missionbuilder.NewLocationNotification(self.area_name, self.elements["MISSION_GATE"])


class DZRS_LostForager(Plot):
    LABEL = "DZRS_FEATURE"

    active = True
    scope = "METRO"
    UNIQUE = True

    def custom_init(self, nart):
        # Create the NPC in town who will serve as the actual mission giver.
        npc1 = self.register_element("MISSION_GIVER",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes))

        # Create the Explorer NPC that the PC can rescue.
        npc2 = self.register_element("NPC",
                                    gears.selector.random_character(self.rank + random.randint(1,8), combatant=True,
                                                                    local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Explorer"]))
        self.npcs = (npc1,npc2)

        # Place the mission-giving NPC
        myscene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_good_scene)
        myscene.contents.append(npc1)

        # Create the desert mountain dungeon.
        self.area_name = plotutility.random_deadzone_spot_name()
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], self.area_name,
            gharchitecture.HumanScaleDeadzoneWilderness(), self.rank,
            monster_tags = ("ANIMAL", "DESERT", "MUTANT", "FIRE"),
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_OUTDOORS,),
            decor=gharchitecture.DesertDecor(),
            connector=plotutility.NatureTrailConnection
        )
        self.elements["DUNGEON"] = mydungeon.entry_level

        # Add the dungeon entry room.
        mymapgen = nart.get_map_generator(mydungeon.entry_level)
        if mymapgen and mymapgen.edge_positions:
            myanchor = mymapgen.edge_positions.pop()
        else:
            myanchor = None
        d_entrance_room = self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=myanchor))
        mydungeon.entry_level.contents.append(d_entrance_room)

        myent = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(
                anchor=pbge.randmaps.anchors.middle,
                dest_scene=self.elements["METROSCENE"],
                dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Place the explorer NPC on a random level.
        candidates = [l for l in mydungeon.levels if l is not mydungeon.entry_level]
        real_goal = random.choice(candidates)
        d_npc_room = pbge.randmaps.rooms.OpenRoom(9, 9)
        real_goal.contents.append(d_npc_room)
        myteam = teams.Team()
        d_npc_room.contents.append(myteam)
        myteam.contents.append(npc2)

        #print(self.elements["METROSCENE"])
        self.dungeon_unlocked = False
        self.got_rumor = False
        self.npc_rescued = False
        self.npc_lm = False

        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.SCENE_HOSPITAL in candidate.attributes

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.dungeon_unlocked:
            thingmenu.add_item("Go to {} on foot.".format(self.area_name), self.go_to_locale)

    def go_to_locale(self, camp):
        camp.destination, camp.entrance = self.elements["DUNGEON"], self.elements["ENTRANCE"]

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc not in self.npcs and not self.got_rumor and not self.dungeon_unlocked:
            mygram["[News]"] = ["{} hasn't returned from {}".format(self.elements["NPC"], self.area_name),]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mynpc = self.elements["NPC"]
        if npc not in self.npcs and not self.got_rumor and not self.dungeon_unlocked:
            goffs.append(Offer(
                msg="{NPC} is an explorer who goes foraging in the wastes; {MISSION_GIVER} at {LOCALE} is worried because {NPC.gender.subject_pronoun} has been gone for too long.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        self.memo = Memo( "{MISSION_GIVER} has been worried about {NPC}.".format(**self.elements)
                        , self.elements["LOCALE"]
                        )

    def MISSION_GIVER_offers(self, camp):
        myoffs = list()

        if not self.dungeon_unlocked:
            myoffs.append(Offer(
                "[HELLO] I hope that {NPC} gets back soon...".format(**self.elements),
                context=ContextTag((context.HELLO,)),
            ))

            myoffs.append(Offer(
                "{} went foraging for scrap metal in {}, but hasn't come back yet. I really hope that nothing bad has happened.".format(self.elements["NPC"], self.area_name),
                context=ContextTag((context.INFO,)), effect=self._unlock_dungeon,
                data={"subject": str(self.elements["NPC"])}, no_repeats=True
            ))

        return myoffs

    def _unlock_dungeon(self, camp):
        self.dungeon_unlocked = True
        self.memo = Memo( "{} has not returned from foraging in {}.".format(self.elements["NPC"], self.area_name)
                        , self.elements["METROSCENE"]
                        )
        missionbuilder.NewLocationNotification(self.area_name, self.elements["MISSION_GATE"])

    def NPC_offers(self, camp):
        myoffs = list()
        npc = self.elements["NPC"]

        if not self.npc_rescued:
            myoffs.append(Offer(
                "[HELLO] I wandered out too far from {METROSCENE} and got a bit lost... I don't suppose you're heading back that way soon?".format(**self.elements),
                context=ContextTag((context.HELLO,)),
            ))

            myoffs.append(Offer(
                "Thanks. Let's get going.",
                context=ContextTag((context.CUSTOM,)), effect=self._rescue_npc,
                data={"reply": "Sure, I can help you to get home."}, no_repeats=True
            ))
        elif not self.npc_lm:
            myoffs.append(Offer(
                "[HELLO] Thanks for getting me back to {METROSCENE}; if you ever need the services of an experienced explorer, just let me know!".format(**self.elements),
                context=ContextTag((context.HELLO,)), effect=self._add_lancemate
            ))

        return myoffs

    def _rescue_npc(self, camp: gears.GearHeadCampaign):
        self.npc_rescued = True
        npc = self.elements["NPC"]
        npc.place(self.elements["METROSCENE"], team=self.elements["METROSCENE"].civilian_team)
        camp.destination, camp.entrance = self.elements["METROSCENE"], self.elements["MISSION_GATE"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.dole_xp(200)

    def _add_lancemate(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.history.append(gears.relationships.Memory(
            "you rescued me from {}".format(self.area_name),
            "I rescued you from {}".format(self.area_name),
            10, [gears.relationships.MEM_AidedByPC,]
        ))
        self.npc_lm = True


class DZRS_GeneralStore(Plot):
    LABEL = "DZRS_FEATURE"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        npc1 = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.ConcreteBuilding(
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, self.shopname, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["METROSCENE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.GENERAL_STORE)

        return True

    TITLE_PATTERNS = (
        "{METROSCENE} General Shop", "{SHOPKEEPER}'s Shop",
    )
    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(**self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] This is {}; take a look around.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "gear"},
                            ))

        return mylist


class DZRS_WeaponArmorShop(Plot):
    LABEL = "DZRS_FEATURE"

    active = True
    scope = "INTERIOR"
    UNIQUE = True

    def custom_init(self, nart):
        npc1 = self.register_element("WEAPONS_S",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc2 = self.register_element("ARMOR_S",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.ConcreteBuilding(
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self.shopname)},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, self.shopname, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.IndustrialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.RundownFactoryDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["METROSCENE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        npc1.place(intscene, team=team2)
        npc2.place(intscene, team=team2)

        self.weapon_shop = services.Shop(npc=npc1, ware_types=services.WEAPON_STORE)
        self.armor_shop = services.Shop(npc=npc2, ware_types=services.ARMOR_STORE)

        return True

    TITLE_PATTERNS = (
        "{METROSCENE} Armory", "{WEAPONS_S} & {ARMOR_S}", "{WEAPONS_S} & Company", "{ARMOR_S} & Partner",
        "{METROSCENE} Combat Shop", "{METROSCENE} Outfitters", "{METROSCENE} Army Surplus"
    )
    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(**self.elements)

    def WEAPONS_S_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] You look like you could use some new weapons.",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.weapon_shop,
                            data={"shop_name": self.shopname, "wares": "weapons"},
                            ))

        return mylist

    def ARMOR_S_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] You look like you could use some new armor.",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.armor_shop,
                            data={"shop_name": self.shopname, "wares": "armor"},
                            ))

        return mylist
