from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,GHNarrativeRequest,PLOT_LIST,mechtarot, dungeonmaker, ghrooms
from . import lancemates, shops_plus


#   **********************
#   ***  HIVE_OF_SCUM  ***
#   **********************
#
#   Create a town/neighborhood of ill repute. The HoS will be placed as a child of METROSCENE but no connection
#   will be made; that's up to the parent plot to handle.
#
#   Needed Elements:
#   METROSCENE, METRO, ENTRANCE
#   LOCALE_NAME: Optional; gives a name for this location
#   LOCALE_FACTION: The faction that runs this place
#
#   Generated Elements:
#   LOCALE: The hive of scum scene
#   FOYER: An empty room on one of the edges.
#   EXIT: An exit leading back to ENTRANCE
#

class BanditsDen(Plot):
    LABEL = "HIVE_OF_SCUM"
    active = True
    scope = "METRO"

    def custom_init( self, nart ):
        # Step One: Create the scene
        town_name = self.elements.get("LOCALE_NAME") or self._generate_locale_name()
        town_fac = self.elements.get("LOCALE_FACTION") or plotutility.RandomBanditCircle(nart.camp)
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,), faction=town_fac)

        myscene = gears.GearHeadScene(50, 50, town_name, player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale,
                                      faction=town_fac,
                                      attributes=(
                                      gears.tags.Criminal, gears.tags.SCENE_OUTDOORS, gears.tags.SCENE_SEMIPUBLIC))
        myscene.exploration_music = 'Komiku_-_06_-_Friendss_theme.ogg'

        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.HumanScaleDeadzone(),)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE", dident="METROSCENE")

        # Add some NPCs to the scene.
        for t in range(random.randint(2,4)):
            npc = gears.selector.random_character(50, local_tags=myscene.attributes, needed_tags=(gears.tags.Criminal,))
            npc.place(myscene, team=team2)

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["METROSCENE"].attributes, faction=town_fac, combatant=True
        ))
        defender.place(myscene, team=team2)

        # Add the services.
        self.add_sub_plot(nart, "SHOP_BLACKMARKET", elements={"INTERIOR_TAGS": (gears.tags.SCENE_SEMIPUBLIC,)})
        self.add_sub_plot(nart, "HOS_SERVICES", elements={"INTERIOR_TAGS": (gears.tags.SCENE_SEMIPUBLIC,)})

        myroom2 = self.register_element(
            "FOYER", pbge.randmaps.rooms.Room(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)),
            dident="LOCALE")
        towngate = self.register_element(
            "EXIT", ghwaypoints.Exit(name="Back to {}".format(self.elements["METROSCENE"]),
                                     dest_wp=self.elements["ENTRANCE"]), dident="FOYER")

        return True

    LOCALE_NAME_PATTERNS = ("{} Den", "{} Hive")

    def _generate_locale_name(self):
        return random.choice(self.LOCALE_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())


#   ********************
#   ***  HOS_THREAT  ***
#   ********************
#
#   This hive of scum and villany would be no fun without some kind of threat.
#
#   Needed Elements:
#   METROSCENE, METRO, ENTRANCE
#   LOCALE_NAME: Optional; gives a name for this location
#   LOCALE_FACTION: The faction that runs this place
#   LOCALE: The hive of scum scene
#


#   **********************
#   ***  HOS_SERVICES  ***
#   **********************
#
#   Shops and other services for the Hive of Scum.
#
#   Needed Elements:
#   METROSCENE, METRO, ENTRANCE
#   LOCALE_NAME: Optional; gives a name for this location
#   LOCALE_FACTION: The faction that runs this place
#   LOCALE: The hive of scum scene
#

class ScumHiveWeapons(Plot):
    LABEL = "HOS_SERVICES"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Trader"]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", shops_plus.get_building(
            self, ghterrain.ScrapIronBuilding,
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=self.shopname)},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["METROSCENE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.WEAPON_STORE, rank=self.rank+15,
                                  shop_faction=self.elements.get("LOCALE").faction)

        return True

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Armaments", "{SHOPKEEPER}'s Weapons", "{SHOPKEEPER}'s Munitions"
    )
    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(**self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Around here, you're going to need something to protect yourself; take a look around and see what you like.",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "weapons"},
                            ))

        return mylist


class ScumHiveMecha(Plot):
    LABEL = "HOS_SERVICES"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Mechanic"]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", shops_plus.get_building(
            self, ghterrain.IndustrialBuilding,
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=self.shopname)},
            door_sign=(ghterrain.RustyFixitShopSignEast, ghterrain.RustyFixitShopSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2, faction=self.elements.get("SHOP_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (gears.tags.SCENE_BUILDING, gears.tags.SCENE_SHOP),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["METROSCENE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.MEXTRA_STORE, rank=self.rank+15,
                                  shop_faction=random.choice(self.FACTIONS))

        return True

    FACTIONS = (gears.factions.BladesOfCrihna, gears.factions.BoneDevils, gears.factions.DeadzoneFederation,
                gears.factions.ClanIronwind, gears.factions.BoneDevils)

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Mecha", "{SHOPKEEPER}'s Salvage", "{SHOPKEEPER}'s Warbots", "Honest {SHOPKEEPER}'s"
    )
    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(**self.elements)

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] I've got a good selection of second hand meks, hardly used, mostly in working order.",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "meks"},
                            ))

        return mylist



#   **************************
#   ***   MECHA_WORKSHOP   ***
#   **************************
#
# OWNER_NAME: The name of the NPC or faction that owns this factory
# BUILDING_NAME: The name of this factory

class SmallMechaFactory(Plot):
    LABEL = "MECHA_WORKSHOP"
    active = True
    scope = "LOCALE"
    additional_waypoints = (ghwaypoints.MechEngTerminal, ghwaypoints.MechaPoster)

    def custom_init(self, nart):
        npc_name,garage_name = self.generate_npc_and_building_name()

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = self.register_element("CIVILIAN_TEAM", teams.Team(name="Civilian Team"))
        intscene = gears.GearHeadScene(50, 50, garage_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale, exploration_music="AlexBeroza_-_Kalte_Ohren.ogg")
        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.FactoryBuilding(),
                                                            decorate=gharchitecture.FactoryDecor())
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident="METROSCENE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(10,10,anchor=pbge.randmaps.anchors.south,),
                                    dident="LOCALE")
        foyer.contents.append(team2)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name, local_tags=self.elements["METROSCENE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mechanic"]
                                    ))
        npc.place(intscene, team=team2)

        for item in self.additional_waypoints:
            foyer.contents.append(item())

        self.shop = services.Shop(npc=npc, shop_faction=self.elements["METROSCENE"].faction,
                                  ware_types=services.MECHA_PARTS_STORE, rank=self.rank)

        # Add some details and complications.
        if random.randint(1,8) != 4:
            self.add_sub_plot(nart, "MEKWORK_PROBLEM", necessary=False)
        if random.randint(1,6) != 4:
            self.add_sub_plot(nart, "MEKWORK_FEATURE", necessary=False)
        if random.randint(1,4) != 4:
            self.add_sub_plot(nart, "MEKWORK_MISC", necessary=False)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "custom built mecha parts"}
                            ))

        return mylist

    NAME_PATTERNS = ("{npc} Mecha Works", "{town} Mecha Works")

    def generate_npc_and_building_name(self):
        npc_name = gears.selector.GENERIC_NAMES.gen_word()
        if "BUILDING_NAME" in self.elements:
            return npc_name, self.elements["BUILDING_NAME"]
        if "OWNER_NAME" in self.elements:
            owner_name = self.elements.get("OWNER_NAME") or gears.selector.EARTH_NAMES.gen_word()
        else:
            owner_name = npc_name
        building_name = random.choice(self.NAME_PATTERNS).format(npc=owner_name,town=str(self.elements["METROSCENE"]))
        return npc_name, building_name


#   ***************************
#   ***   MEKWORK_PROBLEM   ***
#   ***************************
#
#  LOCALE: The mecha workshop
#  METROSCENE: The city the workshop is in
#  METRO: The scope of the city

class MWP_ComputerProblem(Plot):
    LABEL = "MEKWORK_PROBLEM"

    active = True
    scope = "METRO"
    UNIQUE = True

    def custom_init(self, nart):
        # Create a room for the engineer.
        myroom = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(),
                                      dident="LOCALE")

        npc = self.register_element("ENGINEER",
                                    gears.selector.random_character(local_tags=self.elements["METROSCENE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Factory Worker"]),
                                    dident="_introom")

        computer = self.register_element(
            "_computer", ghwaypoints.RetroComputer(
                name="Computer", desc="You stand before {}'s work terminal.".format(npc),
                plot_locked=True
            ), dident="_introom"
        )

        self.fixed_computer = False
        return True

    def _computer_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if not self.fixed_computer:
            thingmenu.desc = "{} It is locked up in a magenta screen of death.".format(thingmenu.desc)
            pc1 = camp.make_skill_roll(gears.stats.Craft, gears.stats.Computers, self.rank, gears.stats.DIFFICULTY_AVERAGE,
                                       untrained_ok=False, no_random=True)
            if pc1:
                if pc1 is camp.pc:
                    thingmenu.add_item("Reset the terminal.", self._fix_generator)
                else:
                    thingmenu.add_item("Ask {} to fix the problem.".format(pc1), self._fix_generator)

            pc2 = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Repair, self.rank, gears.stats.DIFFICULTY_HARD,
                                       untrained_ok=True, no_random=True)
            if pc2 and pc2 is not pc1:
                if pc2 is camp.pc:
                    thingmenu.add_item("Activate the autodiagnostic.", self._fix_generator)
                else:
                    thingmenu.add_item("Ask {} to fix the problem.".format(pc2), self._fix_generator)

            if not (pc1 or pc2):
                thingmenu.add_item("Try to fix it.", self._fix_failed)
            thingmenu.add_item("Leave it alone.", None)

    def _fix_generator(self, camp: gears.GearHeadCampaign):
        pbge.alert("You identify and solve the system error. The computer reboots without a hitch.")
        self.fixed_computer = True
        camp.dole_xp(100, gears.stats.Repair)
        camp.dole_xp(100, gears.stats.Computers)

    def _fix_failed(self, camp):
        pbge.alert("You attempt to fix things but can't even get the terminal to respond.")

    def ENGINEER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] I'm having an easy day today because my computer is on the blink.",
                        context=ContextTag([context.HELLO]),
                        ))


        if self.fixed_computer:
            mylist.append(Offer("You did WHAT?! I suppose I ought to thank you... I don't want to, but I ought to.",
                            context=ContextTag([context.CUSTOM]), effect=self._win_mission,
                            data={"reply": "I fixed your computer."},
                            ))

        return mylist

    def _win_mission(self, camp: gears.GearHeadCampaign):
        camp.dole_xp(100)
        self.end_plot(camp)


class MWP_OfflineGenerator(Plot):
    LABEL = "MEKWORK_PROBLEM"

    active = True
    scope = "METRO"
    UNIQUE = True

    def custom_init(self, nart):
        # Create a room for the engineer.
        myroom = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(),
                                      dident="LOCALE")

        npc = self.register_element("ENGINEER",
                                    gears.selector.random_character(local_tags=self.elements["METROSCENE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Factory Worker"]),
                                    dident="_introom")

        # Create the dungeon level.
        sp = self.add_sub_plot(nart, "DUNGEON_GENERIC", elements={
            dungeonmaker.DG_NAME: "{} Basement".format(self.elements["LOCALE"]),
            dungeonmaker.DG_PARENT_SCENE: self.elements["LOCALE"],
            dungeonmaker.DG_MONSTER_TAGS: ("ROBOT",), dungeonmaker.DG_ARCHITECTURE: gharchitecture.FactoryBuilding(),
            dungeonmaker.DG_DECOR: gharchitecture.RundownFactoryDecor(),
            dungeonmaker.DG_SCENE_TAGS: (gears.tags.SCENE_DUNGEON, gears.tags.SCENE_SEMIPUBLIC),
            dungeonmaker.DG_EXPLO_MUSIC: "Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            dungeonmaker.DG_COMBAT_MUSIC: "Komiku_-_03_-_Battle_Theme.ogg",
        })
        self.elements["DUNGEON"] = sp.elements["LOCALE"]

        # Connect the dungeon level.
        plotutility.StairsDownToStairsUpConnector(
            nart, self, self.elements["LOCALE"], sp.elements["LOCALE"], room1=myroom,
        )

        # Add the generator room and broken generator
        goalroom = self.register_element('_goalroom', pbge.randmaps.rooms.ClosedRoom(),
                                      dident="DUNGEON")
        generator = self.register_element(
            "_generator", ghwaypoints.OldTerminal(
                name="Generator Control", desc="You stand before the power generator control terminal.",
                plot_locked=True
            ), dident="_goalroom"
        )

        self.got_intro = False
        self.fixed_generator = False
        self.reward = gears.base.Engine(size=800+self.rank * 10, desig="MP-{} Advanced".format(800+self.rank * 10),
                                        material=gears.materials.Advanced)

        return True

    def _generator_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if not self.fixed_generator:
            thingmenu.desc = "{} The screen is blank and none of the lights are on.".format(thingmenu.desc)
            pc1 = camp.make_skill_roll(gears.stats.Craft, gears.stats.Repair, self.rank, gears.stats.DIFFICULTY_EASY,
                                       untrained_ok=False, no_random=True)
            if pc1:
                if pc1 is camp.pc:
                    thingmenu.add_item("Repair the terminal.", self._fix_generator)
                else:
                    thingmenu.add_item("Ask {} to repair the terminal.".format(pc1), self._fix_generator)

            pc2 = camp.make_skill_roll(gears.stats.Craft, gears.stats.Science, self.rank, gears.stats.DIFFICULTY_HARD,
                                       untrained_ok=True, no_random=True)
            if pc2 and pc2 is not pc1:
                if pc2 is camp.pc:
                    thingmenu.add_item("Jury rig a solution.", self._fix_generator)
                else:
                    thingmenu.add_item("Ask {} to jury rig a solution.".format(pc2), self._fix_generator)

            if not (pc1 or pc2):
                thingmenu.add_item("Repair the terminal.", self._fix_failed)

    def _fix_generator(self, camp: gears.GearHeadCampaign):
        pbge.alert("You repair the terminal. Soon the generator coils beneath your feet begin to hum with energy once more.")
        self.fixed_generator = True
        camp.dole_xp(100, gears.stats.Repair)
        camp.dole_xp(100, gears.stats.Science)

    def _fix_failed(self, camp):
        pbge.alert("You attempt to repair the terminal but quickly discover that the damage is beyond your current skill level.")

    def ENGINEER_offers(self, camp):
        mylist = list()

        if not self.fixed_generator:
            mylist.append(Offer("[HELLO] The generator downstairs has stopped working, and if we can't get it online soon we'll have to shut down.",
                            context=ContextTag([context.HELLO]),
                            ))

            mylist.append(Offer(
                "It's a pretty standard isotropic system. It wouldn't be too hard to fix, and in fact the workbots are supposed to be doing that, but they're not exactly doing their job at the moment.",
                context=ContextTag([context.INFO]), subject="generator", data={"subject": "the generator"},
                no_repeats=True
            ))

            mylist.append(Offer(
                "Here's the thing. I don't know what's going on with them, but they're not letting any of us into the basement, and I had the security override code writted down somehwere but now I can't find it.",
                context=ContextTag([context.INFO]), subject="workbots", data={"subject": "the workbots"},
                no_repeats=True
            ))

        else:
            mylist.append(Offer("[THANKS_FOR_HELP] As a reward, how would you like this {}? I was using it to keep the lights on until we could get the big generator back.".format(self.reward.get_full_name()),
                            context=ContextTag([context.CUSTOM]), effect=self._win_mission,
                            data={"reply": "I fixed your generator."},
                            ))

        return mylist

    def _win_mission(self, camp: gears.GearHeadCampaign):
        camp.party.append(self.reward)
        camp.dole_xp(100)
        self.end_plot(camp)


#   ***************************
#   ***   MEKWORK_FEATURE   ***
#   ***************************
#
#  LOCALE: The mecha workshop
#  METROSCENE: The city the workshop is in
#  METRO: The scope of the city

class MWF_Showroom(Plot):
    LABEL = "MEKWORK_FEATURE"

    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Create an office.
        myroom = self.register_element('_room', pbge.randmaps.rooms.ClosedRoom(),dident="LOCALE")
        myroom.contents.append(ghwaypoints.MechaModel())
        myroom.contents.append(ghwaypoints.MechaModel())
        myroom.contents.append(ghwaypoints.MechaModel())
        npc = self.register_element('NPC',
                                    gears.selector.random_character(50, local_tags=self.elements["METROSCENE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]),
                                    dident="_room"
                                    )

        self.shop = services.Shop(npc=npc, num_items=5,
                                  ware_types=services.MECHA_STORE, rank=self.rank)
        return True

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Would you like to see the mecha we build at {LOCALE}?".format(**self.elements),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "mecha"}
                            ))

        return mylist


class MWF_WeaponsLab(Plot):
    LABEL = "MEKWORK_FEATURE"

    active = True
    scope = "METRO"
    UNIQUE = True

    def custom_init(self, nart):
        # Create an office.
        myroom = self.register_element('_room', pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.UlsaniteOfficeDecor()),dident="LOCALE")
        npc = self.register_element('NPC',
                                    gears.selector.random_character(50, local_tags=self.elements["METROSCENE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Researcher"]),
                                    dident="_room"
                                    )

        self.shop = services.Shop(npc=npc, sell_champion_equipment=True, num_items=5,
                                  ware_types=services.MECHA_WEAPON_STORE, rank=self.rank)
        return True

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] I am in charge of weapons research and development here at {LOCALE}.".format(**self.elements),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "weapons"}
                            ))

        return mylist



#   ************************
#   ***   MEKWORK_MISC   ***
#   ************************
#
#  LOCALE: The mecha workshop
#  METROSCENE: The city the workshop is in
#  METRO: The scope of the city

class MWM_BusinessOffice(Plot):
    LABEL = "MEKWORK_MISC"

    active = False

    def custom_init(self, nart):
        # Create an office.
        self.register_element('_room', pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.UlsaniteOfficeDecor()),dident="LOCALE")
        return True

class MWM_StorageRoom(Plot):
    LABEL = "MEKWORK_MISC"

    active = False

    def custom_init(self, nart):
        # Create a storage room.
        self.register_element('_room', pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.StorageRoomDecor()),dident="LOCALE")
        return True


#   ******************
#   ***   TAVERN   ***
#   ******************
#
#  LOCALE: The tavern
#  METROSCENE: The city the building is in
#  METRO: The scope of the city


class BasicTavern(Plot):
    LABEL = "TAVERN"

    active = True
    scope = True

    def custom_init(self, nart):
        npc_name,building_name = self.generate_npc_and_building_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.ResidentialBuilding(
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=building_name)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = self.register_element("FOYER_TEAM", teams.Team(name="Civilian Team"))
        intscene = gears.GearHeadScene(50, 35, building_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_MEETING),
                                       scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.ResidentialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident="METROSCENE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(width=random.randint(20,25),
                                                                                 height=random.randint(11,15),
                                                                                 anchor=pbge.randmaps.anchors.south,),
                                      dident="LOCALE")
        foyer.contents.append(team2)

        mybar = ghrooms.BarArea(random.randint(5,10), random.randint(2,3), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mybar)

        barteam = self.register_element("BAR_TEAM", teams.Team(name="Bar Team", allies=[team2]))
        mybar.contents.append(barteam)

        npc = self.register_element("BARTENDER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name,
                                        local_tags=self.elements["METROSCENE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Bartender"]
                                    ))
        npc.place(intscene, team=barteam)


        mycon = plotutility.TownBuildingConnection(nart, self, self.elements["METROSCENE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        return True

    NAME_PATTERNS = ("{npc} Tavern", "{town} Tavern", "{npc}'s Pub", "The {monster1} and {monster2}")

    def generate_npc_and_building_name(self):
        npc_name = gears.selector.GENERIC_NAMES.gen_word()
        if "BUILDING_NAME" in self.elements:
            return npc_name, self.elements["BUILDING_NAME"]
        if "OWNER_NAME" in self.elements:
            owner_name = self.elements.get("OWNER_NAME") or gears.selector.GENERIC_NAMES.gen_word()
        else:
            owner_name = npc_name
        monster1, monster2 = random.sample(gears.selector.MONSTER_LIST, 2)
        building_name = random.choice(self.NAME_PATTERNS).format(npc=owner_name,town=str(self.elements["METROSCENE"]), monster1=monster1, monster2=monster2)
        return npc_name, building_name


#   ***********************
#   ***  THIEVES_GUILD  ***
#   ***********************
#
#   Elements:
#       LOCALE: The scene into which the Thieves Guild will be placed
#       ENTRANCE: The waypoint you go to when you leave the thieves guild
#       FACTION: The faction the guild belongs to
#   Optional:
#       INTERIOR_TAGS: Defaults to (gears.tags.SCENE_SEMIPUBLIC,)
#       GUILD_NAME: If not set, a random name will be chosen
#   Returns:
#       INTERIOR: The interior of the Thieves Guild
#       EXIT: The exit leading back to the waypoint provided
#

class BasicThievesGuild(Plot):
    LABEL = "THIEVES_GUILD"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Guild Team")
        intscene = gears.GearHeadScene(
            35, 35, self.elements.get("GUILD_NAME", self._generate_guild_name()), player_team=team1, civilian_team=team2, faction=self.elements.get("FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_SEMIPUBLIC,)) + (gears.tags.SCENE_BUILDING, gears.tags.Criminal),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(10,10,anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")
        foyer.contents.append(team2)

        exit = self.register_element("EXIT", ghwaypoints.Exit(name="Exit", dest_wp=self.elements["ENTRANCE"], anchor=pbge.randmaps.anchors.south), dident="_introom")

        # Add some ne'er do wells
        for t in range(random.randint(2,4)):
            npc = gears.selector.random_character(self.rank, combatant=True, local_tags=intscene.attributes, needed_tags=(gears.tags.Criminal,))
            npc.place(intscene, team=team2)

        self.add_sub_plot(nart, "TGUILD_SERVICE")

        return True

    def INTERIOR_ENTER(self, camp: gears.GearHeadCampaign):
        fac = self.elements["FACTION"]
        if fac and camp.is_unfavorable_to_pc(fac):
            # The guild team needs to attack...
            self.elements["INTERIOR"].civilian_team.attack(self.elements["INTERIOR"].player_team)

    ADJECTIVES = (
        "Shadow", "Sinister", "Criminal", "Crime", "Golden", "Secret", "Obscure", "Sneaky", "Illicit", "Nefarious",
        "Infamous", "Chaotic", "Silent"
    )

    ORGS = (
        "Guild", "Order", "Union", "Club", "Mafia", "Syndicate", "Cabal", "Coven", "Clique", "House", "Gang", "Society",
        "League", "Legion"
    )

    JOBS = (
        "Thieves", "Assassins", "Crooks", "Bandits", "Pirates", "Ninjas", "Gangsters", "Brigands", "Evildoers",
        "Lawbreakers", "Outlaws", "Libertines"
    )

    TITLE_PATTERNS = (
        "the {adjective} {job} {org}", "the {adjective} {org}", "the {adjective} {job}",
        "the {adjective} {org} of {job}", "the {job} {org}", "the {org} of {job}"
    )

    def _generate_guild_name(self):
        return random.choice(self.TITLE_PATTERNS).format(adjective=random.choice(self.ADJECTIVES), org=random.choice(self.ORGS), job=random.choice(self.JOBS))


#   ************************
#   ***  TGUILD_SERVICE  ***
#   ************************
#
#   Elements:
#       LOCALE: The scene into which the Thieves Guild will be placed
#       ENTRANCE: The waypoint you go to when you leave the thieves guild
#       FACTION: The faction the guild belongs to
#       INTERIOR: The interior of the Thieves Guild
#

class AssassinForHire(Plot):
    LABEL = "TGUILD_SERVICE"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        npcroom = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(6,6),
                                      dident="INTERIOR")

        myteam = teams.Team(allies=(self.elements["INTERIOR"].civilian_team,))
        npcroom.contents.append(myteam)

        # Create the shopkeeper
        npc1 = self.register_element("NPC", gears.selector.random_character(
            self.rank+20, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Assassin"], combatant=True,
            faction=self.elements.get("FACTION", gears.factions.TreasureHunters)
        ))
        myteam.contents.append(npc1)
        return True

    def NPC_offers(self, camp):
        mylist = list()

        npc = self.elements["NPC"]
        self.hire_cost = lancemates.get_hire_cost(camp,npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("You can hire me for ${}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                                    context=ContextTag((context.PROPOSAL, context.JOIN)),
                                    data={"subject": "joining my lance"},
                                    subject=self, subject_start=True,
                                    ))
                mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                    context=ContextTag((context.DENY, context.JOIN)), subject=self
                                    ))
                if camp.credits >= self.hire_cost:
                    mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                        context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                        effect=self._join_lance
                                        ))
            mylist.append(Offer(
                "[HELLO] If you're looking for a hired killer, I'm not doing much at the moment.", context=ContextTag((context.HELLO,))
            ))
            mylist.append(plotutility.LMSkillsSelfIntro(npc))

        return mylist

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.credits -= self.hire_cost
        effect = plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class GuildMarket(Plot):
    LABEL = "TGUILD_SERVICE"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        shoproom = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(8,8),
                                      dident="INTERIOR")

        myteam = teams.Team(allies=(self.elements["INTERIOR"].civilian_team,))
        shoproom.contents.append(myteam)

        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Smuggler"], combatant=False))
        myteam.contents.append(npc1)

        self.shopname = "{}'s Shop".format(npc1)

        self.shop = services.Shop(npc=npc1, ware_types=services.BLACK_MARKET, rank=self.rank+random.randint(1,50),
                                  shop_faction=self.elements.get("FACTION", gears.factions.TreasureHunters))

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO] Can I interest you in anything forbidden or dangerous?",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "gear"},
                            ))

        return mylist

