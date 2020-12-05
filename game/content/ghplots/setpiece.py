from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,GHNarrativeRequest,PLOT_LIST,mechtarot, dungeonmaker, ghrooms
from . import tarot_cards


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
            self, self.elements["LOCALE"], sp.elements["LOCALE"], room1=myroom,
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
        name = "Basic Tavern"

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.ResidentialBuilding(
            waypoints={"DOOR": ghwaypoints.ScreenDoor(name=name)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = self.register_element("FOYER_TEAM", teams.Team(name="Civilian Team"))
        intscene = gears.GearHeadScene(50, 35, name, player_team=team1, civilian_team=team2,
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
                                        self.rank, local_tags=self.elements["METROSCENE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Bartender"]
                                    ))
        npc.place(intscene, team=barteam)


        mycon = plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene,
                                                                 room1=building,
                                                                 room2=foyer, door1=building.waypoints["DOOR"],
                                                                 move_door1=False)

        return True

