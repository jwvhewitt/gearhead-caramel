# Module created by GearHead Caramel Scenario Creator
# Do not look at this file to try and figure out how to program a GearHead adventure!
# Look at the hand-coded adventures instead. The Scenario Creator does things in a
# very particular way to make things easy to deal with in the editor. The code below
# is not designed to be human-readable, just computer-writable. You can download the
# source code of GearHead Caramel from GitHub; see www.gearheadrpg.com for details.
import gears
from gears import personality, tags
from pbge.plots import Plot, Adventure, PlotState
import pbge
from pbge.dialogue import Offer, ContextTag
from game import teams, ghdialogue, services
from game.ghdialogue import context
import pygame
import random
from game.content.ghwaypoints import Exit
from game.content.plotutility import AdventureModuleData
import game
from game.content import plotutility, ghwaypoints, gharchitecture, GHNarrativeRequest, ghterrain, ghrooms, dungeonmaker, scutils
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
from pbge.memos import Memo
from game.content.ghplots import missionbuilder, campfeatures
#: includes
THE_WORLD = "SCENARIO_ELEMENT_UIDS"
CUSTOM_FACTIONS = "CUSTOM_FACTIONS"
LOCAL_PROBLEMS_SOLVED = "LOCAL_PROBLEMS_SOLVED"


class ropp_Scenario(Plot):
    LABEL = "SCENARIO_ropp"
    active = True
    scope = True
    #: plot_properties
    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Raid on Pirate's Point",
        "The Solar Navy has decided to remove the Aegis Consulate from Pirate's Point... and if they can get rid of the pirates at the same time, so much the better.",
        (158, 4, 13),
        "VHS_RaidOnPiratesPoint.png",
        convoborder="ropp_convoborder.png")

    def custom_init(self, nart):
        self.ADVENTURE_MODULE_DATA.apply(nart.camp)
        self.elements[CUSTOM_FACTIONS] = dict()
        nart.camp.campdata[
            gears.
            CAMPDATA_DEFAULT_MISSION_COMBAT_MUSIC] = 'UltraCat - Disco High.ogg'
        nart.camp.campdata[
            gears.
            CAMPDATA_DEFAULT_MISSION_EXPLO_MUSIC] = 'Monkey Warhol - Boots and Pants Instrumental Mix.ogg'
        nart.camp.campdata[LOCAL_PROBLEMS_SOLVED] = 0
        if 0 > 0:
            self.rank = 0
        else:
            self.rank = nart.camp.renown
        element_alias_list = []

        self.add_sub_plot(nart,
                          "CF_WORLD_MAP_HANDLER",
                          elements=dict(
                              WM_IMAGE_FILE="wm_map_piratespoint.png",
                              WM_IDENTIFIER="WORLDMAP_6"))
        nart.camp.campdata['lets_get_tattoos'] = 0
        nart.camp.campdata['hero_points'] = 0
        #:scenario_init
        self.build_world(nart)
        unique_id = "ropp"

        nart.camp.num_lancemates = 3
        self.add_sub_plot(nart,
                          "CF_STANDARD_LANCEMATE_HANDLER",
                          elements=dict(LANCEDEV_ENABLED=True))

        self.add_sub_plot(nart,
                          'CITY_ropp_2',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_3',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_7',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_8',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_9',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_10',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_11',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_12',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_13',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CITY_ropp_14',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart, 'ROPP_WAR_STARTER')
        # Handle the entry and lancemate stuff here.
        self.add_sub_plot(nart, "START_PLOT_{}".format(unique_id))
        if True:
            self.add_sub_plot(nart,
                              "ADD_INSTANT_EGG_LANCEMATE",
                              necessary=False)
        if True:
            self.add_sub_plot(nart, "CF_WORLD_MAP_ENCOUNTER_HANDLER")
        return True

    #: world_methods
    #: plot_methods
    def build_world(self, nart):
        # When adding physical things to the world, do that here instead of inside your individual plots. That way,
        # all the physical objects in the world get defined before individual plots get loaded and the elements they
        # define can be grabbed from THE_WORLD campaign variable.
        the_world = dict()
        nart.camp.campdata[THE_WORLD] = the_world

        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "The Solar Navy Base",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=gears.factions.TheSolarNavy,
            attributes=[
                personality.GreenZone, gears.tags.SCENE_PUBLIC,
                gears.tags.SCENE_OUTDOORS
            ],
            exploration_music='Origami Repetika - Saxophonian March.ogg',
            combat_music='Late.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.SceneGenerator(
            myscene,
            gharchitecture.HumanScaleForest(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.Pavement,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_2")
        the_world['00000001'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_2",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.south,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_2")
        mygate = self.register_element("_MISSION_GATE_2",
                                       Exit(
                                           name="To the War Zone",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_2")
        the_world['00000002'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 8, 0)

        splot = self.add_sub_plot(
            nart,
            "MILITARY_TENT",
            elements=dict(LOCALE=the_world['00000001'],
                          METROSCENE=the_world['00000001'],
                          METRO=the_world['00000001'].metrodat,
                          MISSION_GATE=the_world['00000002'],
                          TENT_NAME='The Supply Depot',
                          TENT_FACTION=gears.factions.TheSolarNavy,
                          INTERIOR_TAGS=[
                              gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GARAGE,
                              gears.tags.SCENE_SHOP
                          ]))
        the_world['00000016'] = splot.elements["INTERIOR"]
        the_world['00000017'] = splot.elements["FOYER"]

        the_world['0000001D'] = ghwaypoints.KenneyCratesWP(name='',
                                                           desc='',
                                                           anchor=None)
        the_world['00000017'].contents.append(the_world['0000001D'])
        the_world['0000001E'] = ghwaypoints.KenneyWoodenTableWP(
            name='', desc='', anchor=pbge.randmaps.anchors.middle)
        the_world['00000017'].contents.append(the_world['0000001E'])
        the_world['0000001F'] = ghwaypoints.KenneyCratesWP(name='',
                                                           desc='',
                                                           anchor=None)
        the_world['00000017'].contents.append(the_world['0000001F'])
        the_world['00000020'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Shopkeeper'],
            faction=gears.factions.KettelIndustries,
            combatant=False)
        the_world['00000017'].contents.append(the_world['00000020'])
        the_world['00000021'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Mechanic'],
            faction=gears.factions.TheSolarNavy,
            combatant=False)
        the_world['00000017'].contents.append(the_world['00000021'])
        splot = self.add_sub_plot(nart,
                                  "MOBILE_HQ",
                                  elements=dict(
                                      LOCALE=the_world['00000001'],
                                      METROSCENE=the_world['00000001'],
                                      METRO=the_world['00000001'].metrodat,
                                      MISSION_GATE=the_world['00000002'],
                                      HQ_NAME='',
                                      HQ_FACTION=gears.factions.TheSolarNavy))
        the_world['00000018'] = splot.elements["INTERIOR"]
        the_world['00000019'] = splot.elements["FOYER"]

        the_world['00000022'] = nart.camp.get_major_npc('Admiral Charla')
        the_world['00000019'].contents.append(the_world['00000022'])
        the_world['00000023'] = nart.camp.get_major_npc('General Pinsent')
        the_world['00000019'].contents.append(the_world['00000023'])
        the_world['00000024'] = nart.camp.get_major_npc('Britaine')
        the_world['00000019'].contents.append(the_world['00000024'])
        splot = self.add_sub_plot(nart,
                                  "FIELD_HOSPITAL",
                                  elements=dict(
                                      LOCALE=the_world['00000001'],
                                      METROSCENE=the_world['00000001'],
                                      METRO=the_world['00000001'].metrodat,
                                      MISSION_GATE=the_world['00000002'],
                                      HQ_NAME='',
                                      HQ_FACTION=gears.factions.TheSolarNavy,
                                      NPC_NAME='Owleer'))
        the_world['0000001A'] = splot.elements["INTERIOR"]
        the_world['0000001B'] = splot.elements["FOYER"]
        the_world['0000001C'] = splot.elements["MEDIC"]
        splot = self.add_sub_plot(
            nart,
            "EMPTY_BUILDING",
            elements=dict(LOCALE=the_world['00000001'],
                          METROSCENE=the_world['00000001'],
                          METRO=the_world['00000001'].metrodat,
                          MISSION_GATE=the_world['00000002'],
                          CITY_COLORS=(gears.color.SteelBlue,
                                       gears.color.BugBlue,
                                       gears.color.Saffron, gears.color.Ebony,
                                       gears.color.AeroBlue),
                          INTERIOR_NAME='The Barracks',
                          INTERIOR_TAGS=[
                              gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BASE,
                              gears.tags.SCENE_MEETING,
                              gears.tags.SCENE_BUILDING
                          ],
                          DOOR_SIGN=(ghterrain.SolarNavyLogoSignEast,
                                     ghterrain.SolarNavyLogoSignSouth),
                          DOOR_TYPE=ghwaypoints.ScrapIronDoor,
                          INTERIOR_FACTION=gears.factions.TheSolarNavy,
                          EXTERIOR_TERRSET=ghterrain.ConcreteBuilding,
                          INTERIOR_ARCHITECTURE=gharchitecture.
                          WarmColorsWallArchitecture,
                          INTERIOR_DECOR=gharchitecture.BunkerDecor()))
        the_world['00000025'] = splot.elements["INTERIOR"]
        the_world['00000026'] = splot.elements["FOYER"]

        the_world['00000027'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Soldier'],
            faction=gears.factions.TerranDefenseForce,
            combatant=False)
        the_world['00000026'].contents.append(the_world['00000027'])
        the_world['00000028'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Recon Pilot'],
            faction=gears.factions.TheSolarNavy,
            combatant=False)
        the_world['00000026'].contents.append(the_world['00000028'])
        the_world['00000029'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Police Officer'],
            faction=gears.factions.Guardians,
            combatant=False)
        the_world['00000026'].contents.append(the_world['00000029'])
        the_world['0000002A'] = pbge.randmaps.rooms.FuzzyRoom(
            name='NPC Holder', anchor=None, decorate=None)
        the_world['00000001'].contents.append(the_world['0000002A'])

        the_world['0000002B'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Mecha Pilot'],
            faction=gears.factions.TheSolarNavy,
            combatant=False)
        the_world['0000002A'].contents.append(the_world['0000002B'])
        the_world['0000008F'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000001'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Commander'],
            faction=gears.factions.TheSolarNavy,
            combatant=True)
        the_world['0000002A'].contents.append(the_world['0000008F'])
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "Uptown District",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=gears.factions.TreasureHunters,
            attributes=[
                gears.tags.City, personality.GreenZone,
                gears.tags.SCENE_OUTDOORS, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='Mr Smith - Poor Mans Groove.ogg',
            combat_music='Late.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_3")
        the_world['00000003'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_3",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.east,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_3")
        mygate = self.register_element("_MISSION_GATE_3",
                                       Exit(
                                           name="Uptown Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_3")
        the_world['00000004'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 0, 5)

        splot = self.add_sub_plot(
            nart,
            "TOWNHALL",
            elements=dict(LOCALE=the_world['00000003'],
                          METROSCENE=the_world['00000003'],
                          METRO=the_world['00000003'].metrodat,
                          MISSION_GATE=the_world['00000004'],
                          CITY_COLORS=(gears.color.RosyBrown,
                                       gears.color.Ebony, gears.color.DimGrey,
                                       gears.color.NobleGold,
                                       gears.color.CeramicColor),
                          LEADER_NAME='',
                          LEADER_JOB=None,
                          HALL_NAME="Pirate's Point Guild Hall",
                          DOOR_SIGN=(ghterrain.JollyRogerSignEast,
                                     ghterrain.JollyRogerSignSouth),
                          HALL_FACTION=gears.factions.TreasureHunters,
                          HALL_ARCHITECTURE=gharchitecture.DefaultBuilding))
        the_world['0000002C'] = splot.elements["INTERIOR"]
        the_world['0000002D'] = splot.elements["FOYER"]
        the_world['0000002E'] = splot.elements["LEADER"]

        the_world['0000007E'] = nart.camp.get_major_npc('Jjang Bogo')
        the_world['0000002D'].contents.append(the_world['0000007E'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_HOSPITAL",
            elements=dict(LOCALE=the_world['00000003'],
                          METROSCENE=the_world['00000003'],
                          METRO=the_world['00000003'].metrodat,
                          MISSION_GATE=the_world['00000004'],
                          CITY_COLORS=(gears.color.RosyBrown,
                                       gears.color.Ebony, gears.color.DimGrey,
                                       gears.color.NobleGold,
                                       gears.color.CeramicColor),
                          SHOP_NAME="The Doctor's Lair",
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.HospitalSignEast,
                                     ghterrain.HospitalSignSouth),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000035'] = splot.elements["INTERIOR"]
        the_world['00000037'] = splot.elements["SHOPKEEPER"]
        the_world['00000036'] = splot.elements["FOYER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_MECHA",
            elements=dict(LOCALE=the_world['00000003'],
                          METROSCENE=the_world['00000003'],
                          METRO=the_world['00000003'].metrodat,
                          MISSION_GATE=the_world['00000004'],
                          CITY_COLORS=(gears.color.RosyBrown,
                                       gears.color.Ebony, gears.color.DimGrey,
                                       gears.color.NobleGold,
                                       gears.color.CeramicColor),
                          SHOP_NAME='Armor Forge',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.MechaModelSignEast,
                                     ghterrain.MechaModelSignSouth),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000004E'] = splot.elements["INTERIOR"]
        the_world['00000050'] = splot.elements["SHOPKEEPER"]
        the_world['0000004F'] = splot.elements["FOYER"]
        the_world['0000008A'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Combatants Room', anchor=None, decorate=None)
        the_world['00000003'].contents.append(the_world['0000008A'])

        the_world['0000008B'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000003'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Assassin'],
            faction=gears.factions.TreasureHunters,
            combatant=True)
        the_world['0000008A'].contents.append(the_world['0000008B'])
        the_world['0000008C'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000003'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Pirate Captain'],
            faction=gears.factions.TreasureHunters,
            combatant=True)
        the_world['0000008A'].contents.append(the_world['0000008C'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_BLACKMARKET",
            elements=dict(LOCALE=the_world['00000003'],
                          METROSCENE=the_world['00000003'],
                          METRO=the_world['00000003'].metrodat,
                          MISSION_GATE=the_world['00000004'],
                          CITY_COLORS=(gears.color.RosyBrown,
                                       gears.color.Ebony, gears.color.DimGrey,
                                       gears.color.NobleGold,
                                       gears.color.CeramicColor),
                          SHOP_NAME='Needful Gear',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.GeneralStoreSign1East,
                                     ghterrain.GeneralStoreSign1South),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000090'] = splot.elements["INTERIOR"]
        the_world['00000091'] = splot.elements["FOYER"]
        the_world['00000092'] = splot.elements["SHOPKEEPER"]
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "Lunar District",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=gears.factions.AegisOverlord,
            attributes=[
                gears.tags.City, personality.GreenZone,
                gears.tags.SCENE_OUTDOORS, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='Alena Smirnova - Hopeless waltz.ogg',
            combat_music='Late.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.WhiteTileFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_7")
        the_world['00000005'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_7",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.northwest,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_7")
        mygate = self.register_element("_MISSION_GATE_7",
                                       Exit(
                                           name="To Pirate's Point",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_7")
        the_world['00000006'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 8, 8)

        splot = self.add_sub_plot(
            nart,
            "TOWNHALL",
            elements=dict(
                LOCALE=the_world['00000005'],
                METROSCENE=the_world['00000005'],
                METRO=the_world['00000005'].metrodat,
                MISSION_GATE=the_world['00000006'],
                CITY_COLORS=(gears.color.LunarGrey, gears.color.AegisCrimson,
                             gears.color.GhostGrey, gears.color.CeramicColor,
                             gears.color.Ebony),
                LEADER_NAME='',
                LEADER_JOB=gears.jobs.ALL_JOBS['Diplomat'],
                HALL_NAME='The Aegis Consulate',
                DOOR_SIGN=(ghterrain.AegisLogoSignEast,
                           ghterrain.AegisLogoSignSouth),
                HALL_FACTION=gears.factions.AegisOverlord,
                HALL_ARCHITECTURE=gharchitecture.AegisArchitecture))
        the_world['0000002F'] = splot.elements["INTERIOR"]
        the_world['00000030'] = splot.elements["FOYER"]
        the_world['00000031'] = splot.elements["LEADER"]

        the_world['0000008E'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000005'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Commander'],
            faction=gears.factions.AegisOverlord,
            combatant=True)
        the_world['00000030'].contents.append(the_world['0000008E'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_HOSPITAL",
            elements=dict(
                LOCALE=the_world['00000005'],
                METROSCENE=the_world['00000005'],
                METRO=the_world['00000005'].metrodat,
                MISSION_GATE=the_world['00000006'],
                CITY_COLORS=(gears.color.LunarGrey, gears.color.AegisCrimson,
                             gears.color.GhostGrey, gears.color.CeramicColor,
                             gears.color.Ebony),
                SHOP_NAME='Europa Health',
                NPC_NAME='',
                DOOR_SIGN=(ghterrain.HospitalSignEast,
                           ghterrain.HospitalSignSouth),
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000003B'] = splot.elements["INTERIOR"]
        the_world['0000003D'] = splot.elements["SHOPKEEPER"]
        the_world['0000003C'] = splot.elements["FOYER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_GARAGE",
            elements=dict(
                LOCALE=the_world['00000005'],
                METROSCENE=the_world['00000005'],
                METRO=the_world['00000005'].metrodat,
                MISSION_GATE=the_world['00000006'],
                CITY_COLORS=(gears.color.LunarGrey, gears.color.AegisCrimson,
                             gears.color.GhostGrey, gears.color.CeramicColor,
                             gears.color.Ebony),
                SHOP_NAME='A.E.S. Mechanics',
                NPC_NAME='',
                DOOR_SIGN=(ghterrain.FixitShopSignEast,
                           ghterrain.FixitShopSignSouth),
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000003E'] = splot.elements["INTERIOR"]
        the_world['00000040'] = splot.elements["SHOPKEEPER"]
        the_world['0000003F'] = splot.elements["FOYER"]

        the_world['0000008D'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000005'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Test Pilot'],
            faction=gears.factions.AegisOverlord,
            combatant=True)
        the_world['0000003F'].contents.append(the_world['0000008D'])
        splot = self.add_sub_plot(
            nart,
            "EMPTY_BUILDING",
            elements=dict(
                LOCALE=the_world['00000005'],
                METROSCENE=the_world['00000005'],
                METRO=the_world['00000005'].metrodat,
                MISSION_GATE=the_world['00000006'],
                CITY_COLORS=(gears.color.LunarGrey, gears.color.AegisCrimson,
                             gears.color.GhostGrey, gears.color.CeramicColor,
                             gears.color.Ebony),
                INTERIOR_NAME='The Museum of Terra',
                INTERIOR_TAGS=[
                    gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING,
                    gears.tags.SCENE_CULTURE, gears.tags.SCENE_MEETING
                ],
                DOOR_SIGN=None,
                DOOR_TYPE=ghwaypoints.GlassDoor,
                INTERIOR_FACTION=None,
                EXTERIOR_TERRSET=ghterrain.ConcreteBuilding,
                INTERIOR_ARCHITECTURE=gharchitecture.
                CoolColorsWallArchitecture,
                INTERIOR_DECOR=None))
        the_world['00000093'] = splot.elements["INTERIOR"]
        the_world['00000094'] = splot.elements["FOYER"]

        the_world['00000095'] = ghwaypoints.WallMap(
            name='Map of Terra',
            desc=
            "The majority of Terra's surface is uninhabitable, covered with a layer of dihydrogen monoxide that can be kilometers deep in places. The people of Terra wage endless war over the tiny scraps of inhabitable land.",
            anchor=None)
        the_world['00000094'].contents.append(the_world['00000095'])
        the_world['00000096'] = ghwaypoints.ClaymoreModel(
            name='Terran Mecha',
            desc=
            'Mecha technology on Terra has not progressed since the fall of the superpowers. Ancient designs such as the Claymore are still in common use. Even though the Terrans have lost all knowledge of how these machines work, they are able to build facsimiles in primitive workshops using blueprints passed down through the generations.',
            anchor=None)
        the_world['00000094'].contents.append(the_world['00000096'])
        the_world['00000097'] = ghwaypoints.ParkStatueSynth(
            name='Mutant Monster',
            desc=
            'The habitable areas of Terra are plagued by mutant monstrosities. It can be dangerous to go outside, even in ostensibly civilized areas such as the Lunar District.',
            anchor=None)
        the_world['00000094'].contents.append(the_world['00000097'])
        the_world['00000098'] = ghwaypoints.StatueF(
            name='Terran Ravager',
            desc=
            "The majority of Terra's population consists of wandering barbarian hordes known as ravagers. The ravagers steal what they want from an area before moving on to their next target. They obey no laws and have no knowledge of humanity's glorious past.",
            anchor=None)
        the_world['00000094'].contents.append(the_world['00000098'])
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "The Nogos",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, personality.GreenZone,
                gears.tags.SCENE_PUBLIC
            ],
            exploration_music=
            'Anthem of Rain - Rock This House (Instrumental).ogg',
            combat_music='HoliznaCC0 - Punk.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.CrackedEarth),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_8")
        the_world['00000007'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_8",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.west,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_8")
        mygate = self.register_element("_MISSION_GATE_8",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_8")
        the_world['00000008'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 6, 3)

        splot = self.add_sub_plot(
            nart,
            "EMPTY_BUILDING",
            elements=dict(LOCALE=the_world['00000007'],
                          METROSCENE=the_world['00000007'],
                          METRO=the_world['00000007'].metrodat,
                          MISSION_GATE=the_world['00000008'],
                          CITY_COLORS=(gears.color.BattleshipGrey,
                                       gears.color.Straw, gears.color.Beige,
                                       gears.color.Celadon,
                                       gears.color.DimGrey),
                          INTERIOR_NAME="Kira's Tattoos",
                          INTERIOR_TAGS=[
                              gears.tags.SCENE_PUBLIC,
                              gears.tags.SCENE_HOSPITAL, gears.tags.SCENE_SHOP
                          ],
                          DOOR_SIGN=(ghterrain.KirasTattoosSignEast,
                                     ghterrain.KirasTattoosSignSouth),
                          DOOR_TYPE=ghwaypoints.ScrapIronDoor,
                          INTERIOR_FACTION=None,
                          EXTERIOR_TERRSET=ghterrain.BrickBuilding,
                          INTERIOR_ARCHITECTURE=gharchitecture.DefaultBuilding,
                          INTERIOR_DECOR=gharchitecture.RundownFactoryDecor()))
        the_world['00000032'] = splot.elements["INTERIOR"]
        the_world['00000033'] = splot.elements["FOYER"]

        the_world['00000034'] = nart.camp.get_major_npc('GH1 Kira')
        the_world['00000033'].contents.append(the_world['00000034'])
        the_world['00000044'] = ghwaypoints.TattooChair(
            name='Tattoo Chair',
            desc=
            "You stand before Kira's tattoo chair. It looks more like a PreZero torture device.",
            anchor=pbge.randmaps.anchors.middle)
        the_world['00000033'].contents.append(the_world['00000044'])
        splot = self.add_sub_plot(
            nart,
            "OFFICE_BUILDING",
            elements=dict(LOCALE=the_world['00000007'],
                          METROSCENE=the_world['00000007'],
                          METRO=the_world['00000007'].metrodat,
                          MISSION_GATE=the_world['00000008'],
                          CITY_COLORS=(gears.color.BattleshipGrey,
                                       gears.color.Straw, gears.color.Beige,
                                       gears.color.Celadon,
                                       gears.color.DimGrey),
                          INTERIOR_NAME='Pitt Flophouse',
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC],
                          DOOR_SIGN=None,
                          DOOR_TYPE=ghwaypoints.ScrapIronDoor,
                          INTERIOR_FACTION=None,
                          EXTERIOR_TERRSET=ghterrain.ResidentialBuilding,
                          INTERIOR_ARCHITECTURE=gharchitecture.
                          DingyResidentialArchitecture,
                          INTERIOR_DECOR=gharchitecture.ResidentialDecor()))
        the_world['00000048'] = splot.elements["INTERIOR"]
        the_world['00000049'] = splot.elements["FOYER"]

        the_world['0000005F'] = pbge.randmaps.rooms.ClosedRoom(
            name='Monster Room 1', anchor=None, decorate=None)
        the_world['00000048'].contents.append(the_world['0000005F'])
        the_world['00000060'] = pbge.randmaps.rooms.ClosedRoom(
            name='Monster Room 2', anchor=None, decorate=None)
        the_world['00000048'].contents.append(the_world['00000060'])
        the_world['00000061'] = pbge.randmaps.rooms.ClosedRoom(
            name='Apartment', anchor=None, decorate=None)
        the_world['00000048'].contents.append(the_world['00000061'])

        the_world['00000062'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000007'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Citizen'],
            faction=None,
            combatant=False)
        the_world['00000061'].contents.append(the_world['00000062'])
        the_world['00000063'] = ghwaypoints.Bookshelf(
            name='Bookshelf',
            desc='You stand before a bookshelf  filled with romance novels.',
            anchor=None)
        the_world['00000061'].contents.append(the_world['00000063'])
        the_world['00000064'] = ghwaypoints.Bunk(name='', desc='', anchor=None)
        the_world['00000061'].contents.append(the_world['00000064'])
        the_world['00000065'] = pbge.randmaps.rooms.ClosedRoom(
            name='Empty Room', anchor=None, decorate=None)
        the_world['00000048'].contents.append(the_world['00000065'])
        the_world['00000066'] = pbge.randmaps.rooms.ClosedRoom(
            name='Treasure Room', anchor=None, decorate=None)
        the_world['00000048'].contents.append(the_world['00000066'])

        the_world['00000067'] = ghwaypoints.Skeleton(
            desc='',
            anchor=pbge.randmaps.anchors.middle,
            treasure_rank=self.rank + random.randint(-10, 10),
            treasure_amount=35)
        the_world['00000066'].contents.append(the_world['00000067'])
        the_world['0000004A'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Monster Room', anchor=None, decorate=None)
        the_world['00000007'].contents.append(the_world['0000004A'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_GENERALSTORE",
            elements=dict(LOCALE=the_world['00000007'],
                          METROSCENE=the_world['00000007'],
                          METRO=the_world['00000007'].metrodat,
                          MISSION_GATE=the_world['00000008'],
                          CITY_COLORS=(gears.color.BattleshipGrey,
                                       gears.color.Straw, gears.color.Beige,
                                       gears.color.Celadon,
                                       gears.color.DimGrey),
                          SHOP_NAME='Murder is Fun',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.GunShopSignEast,
                                     ghterrain.GunShopSignSouth),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000054'] = splot.elements["INTERIOR"]
        the_world['00000055'] = splot.elements["FOYER"]
        the_world['00000056'] = splot.elements["SHOPKEEPER"]
        splot = self.add_sub_plot(
            nart,
            "DUNGEON_GENERIC",
            elements=dict(
                METROSCENE=the_world['00000007'],
                METRO=the_world['00000007'].metrodat,
                MISSION_GATE=the_world['00000008'],
                DG_NAME='Abandoned Building',
                DG_ARCHITECTURE=gharchitecture.DefaultBuilding(),
                DG_SCENE_TAGS=[
                    gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS
                ],
                DG_MONSTER_TAGS=['ANIMAL', 'DEVO', 'CITY', 'VERMIN'],
                DG_PARENT_SCENE=the_world['00000007'],
                DG_EXPLO_MUSIC=
                'Anthem of Rain - Rock This House (Instrumental).ogg',
                DG_COMBAT_MUSIC='HoliznaCC0 - Punk.ogg',
                DG_DECOR=gharchitecture.ResidentialDecor()))
        the_world['0000009A'] = splot.elements["LOCALE"]
        scutils.SCSceneConnection(the_world['00000007'],
                                  splot.elements["LOCALE"],
                                  room1=ghterrain.BrickBuilding(tags=[
                                      pbge.randmaps.CITY_GRID_ROAD_OVERLAP,
                                      pbge.randmaps.IS_CITY_ROOM,
                                      pbge.randmaps.IS_CONNECTED_ROOM
                                  ],
                                                                door_sign=None,
                                                                anchor=None),
                                  door1=ghwaypoints.ScrapIronDoor(
                                      name='Abandoned Building',
                                      anchor=pbge.randmaps.anchors.middle),
                                  room2=pbge.randmaps.rooms.OpenRoom(
                                      width=3,
                                      height=3,
                                      anchor=pbge.randmaps.anchors.south),
                                  door2=ghwaypoints.Exit(
                                      name='Exit',
                                      anchor=pbge.randmaps.anchors.south))
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "The Scrapyard",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='Anthem of Rain - Adaptation (Instrumental).ogg',
            combat_music='HoliznaCC0 - Punk.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.PartlyUrbanGenerator(
            myscene,
            gharchitecture.HumanScaleJunkyard(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_9")
        the_world['00000009'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_9",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.south,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_9")
        mygate = self.register_element("_MISSION_GATE_9",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_9")
        the_world['0000000A'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 4, 1)

        splot = self.add_sub_plot(
            nart,
            "SHOP_GARAGE",
            elements=dict(LOCALE=the_world['00000009'],
                          METROSCENE=the_world['00000009'],
                          METRO=the_world['00000009'].metrodat,
                          MISSION_GATE=the_world['0000000A'],
                          CITY_COLORS=(gears.color.TannedSkin,
                                       gears.color.AeroBlue, gears.color.Straw,
                                       gears.color.Charcoal,
                                       gears.color.Cream),
                          SHOP_NAME='Rowdy Repairs',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.RustyFixitShopSignEast,
                                     ghterrain.RustyFixitShopSignSouth),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000004B'] = splot.elements["INTERIOR"]
        the_world['0000004D'] = splot.elements["SHOPKEEPER"]
        the_world['0000004C'] = splot.elements["FOYER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_HOSPITAL",
            elements=dict(LOCALE=the_world['00000009'],
                          METROSCENE=the_world['00000009'],
                          METRO=the_world['00000009'].metrodat,
                          MISSION_GATE=the_world['0000000A'],
                          CITY_COLORS=(gears.color.TannedSkin,
                                       gears.color.AeroBlue, gears.color.Straw,
                                       gears.color.Charcoal,
                                       gears.color.Cream),
                          SHOP_NAME='The Health and Safety Office',
                          NPC_NAME='',
                          DOOR_SIGN=None,
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000069'] = splot.elements["INTERIOR"]
        the_world['0000006B'] = splot.elements["SHOPKEEPER"]
        the_world['0000006A'] = splot.elements["FOYER"]
        the_world['0000006C'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Empty Room 1', anchor=None, decorate=None)
        the_world['00000009'].contents.append(the_world['0000006C'])
        the_world['0000006D'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Empty Room 2', anchor=None, decorate=None)
        the_world['00000009'].contents.append(the_world['0000006D'])
        splot = self.add_sub_plot(
            nart,
            "DUNGEON_GENERIC",
            elements=dict(
                METROSCENE=the_world['00000009'],
                METRO=the_world['00000009'].metrodat,
                MISSION_GATE=the_world['0000000A'],
                DG_NAME='The Scrap Maze',
                DG_ARCHITECTURE=gharchitecture.HumanScaleJunkyard(),
                DG_SCENE_TAGS=[
                    gears.tags.SCENE_DUNGEON, gears.tags.SCENE_OUTDOORS
                ],
                DG_MONSTER_TAGS=['BUG', 'CITY', 'MUTANT', 'VERMIN'],
                DG_PARENT_SCENE=the_world['00000009'],
                DG_EXPLO_MUSIC='Anthem of Rain - Adaptation (Instrumental).ogg',
                DG_COMBAT_MUSIC='HoliznaCC0 - Punk.ogg',
                DG_DECOR=None))
        the_world['0000006F'] = splot.elements["LOCALE"]
        scutils.SCSceneConnection(
            the_world['00000009'],
            splot.elements["LOCALE"],
            room1=pbge.randmaps.rooms.OpenRoom(
                width=3, height=3, anchor=pbge.randmaps.anchors.north),
            door1=ghwaypoints.Exit(name='To the Crash Site',
                                   anchor=pbge.randmaps.anchors.north),
            room2=pbge.randmaps.rooms.OpenRoom(
                width=3, height=3, anchor=pbge.randmaps.anchors.south),
            door2=ghwaypoints.Exit(name='To the Scrapyard',
                                   anchor=pbge.randmaps.anchors.south))

        mydungeon = dungeonmaker.DungeonMaker(
            nart,
            self,
            name='Crashed Spaceship',
            architecture=gharchitecture.DerelictArchitecture(),
            rank=self.rank,
            scene_tags=[
                gears.tags.SCENE_DUNGEON, gears.tags.SCENE_VEHICLE,
                gears.tags.SCENE_RUINS
            ],
            monster_tags=['BUG', 'DEVO', 'MUTANT', 'ROBOT', 'RUINS'],
            parent_scene=the_world['0000006F'],
            explo_music='HoliznaCC0 - SomeWhere In The Dark.ogg',
            combat_music='Komiku_-_09_-_This_one_is_tough.ogg',
            decor=gharchitecture.TechDungeonDecor())
        the_world['00000071'] = mydungeon
        scutils.SCSceneConnection(
            the_world['0000006F'],
            mydungeon.entry_level,
            room1=pbge.randmaps.rooms.FuzzyRoom(anchor=None),
            door1=ghwaypoints.UndergroundEntrance(
                name='Mysterious Hatch', anchor=pbge.randmaps.anchors.middle),
            room2=pbge.randmaps.rooms.OpenRoom(width=3, height=3, anchor=None),
            door2=ghwaypoints.StairsUp(name='Exit',
                                       anchor=pbge.randmaps.anchors.middle))

        the_world['00000075'] = the_world['00000071'].entry_level
        the_world['00000078'] = the_world['00000071'].goal_level

        the_world['000000A2'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Engineering Room', anchor=None, decorate=None)
        the_world['00000078'].contents.append(the_world['000000A2'])

        the_world['000000A3'] = ghwaypoints.OldMainframe(
            name='Fusion Control Core', desc='', anchor=None)
        the_world['000000A2'].contents.append(the_world['000000A3'])
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "Shopping District",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='Anthem of Rain - So My Love - Instrumental.ogg',
            combat_music='Late.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_10")
        the_world['0000000B'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_10",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.southeast,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_10")
        mygate = self.register_element("_MISSION_GATE_10",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_10")
        the_world['0000000C'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 1, 2)

        splot = self.add_sub_plot(
            nart,
            "SHOP_WEAPONSTORE",
            elements=dict(
                LOCALE=the_world['0000000B'],
                METROSCENE=the_world['0000000B'],
                METRO=the_world['0000000B'].metrodat,
                MISSION_GATE=the_world['0000000C'],
                CITY_COLORS=(gears.color.FieldGrey, gears.color.BugBlue,
                             gears.color.BattleshipGrey, gears.color.Twilight,
                             gears.color.Aquamarine),
                SHOP_NAME='Ye Olde Bazooka',
                NPC_NAME='',
                DOOR_SIGN=(ghterrain.YeOldeShopSignEast,
                           ghterrain.YeOldeShopSignSouth),
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000041'] = splot.elements["INTERIOR"]
        the_world['00000042'] = splot.elements["FOYER"]
        the_world['00000043'] = splot.elements["SHOPKEEPER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_ARMORSTORE",
            elements=dict(
                LOCALE=the_world['0000000B'],
                METROSCENE=the_world['0000000B'],
                METRO=the_world['0000000B'].metrodat,
                MISSION_GATE=the_world['0000000C'],
                CITY_COLORS=(gears.color.FieldGrey, gears.color.BugBlue,
                             gears.color.BattleshipGrey, gears.color.Twilight,
                             gears.color.Aquamarine),
                SHOP_NAME='Look Like a Pirate',
                NPC_NAME='',
                DOOR_SIGN=None,
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000045'] = splot.elements["INTERIOR"]
        the_world['00000046'] = splot.elements["FOYER"]
        the_world['00000047'] = splot.elements["SHOPKEEPER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_GENERALSTORE",
            elements=dict(
                LOCALE=the_world['0000000B'],
                METROSCENE=the_world['0000000B'],
                METRO=the_world['0000000B'].metrodat,
                MISSION_GATE=the_world['0000000C'],
                CITY_COLORS=(gears.color.FieldGrey, gears.color.BugBlue,
                             gears.color.BattleshipGrey, gears.color.Twilight,
                             gears.color.Aquamarine),
                SHOP_NAME='',
                NPC_NAME='',
                DOOR_SIGN=None,
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000051'] = splot.elements["INTERIOR"]
        the_world['00000052'] = splot.elements["FOYER"]
        the_world['00000053'] = splot.elements["SHOPKEEPER"]

        the_world['00000079'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['0000000B'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Trader'],
            faction=None,
            combatant=True)
        the_world['00000052'].contents.append(the_world['00000079'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_CYBERCLINIC",
            elements=dict(
                LOCALE=the_world['0000000B'],
                METROSCENE=the_world['0000000B'],
                METRO=the_world['0000000B'].metrodat,
                MISSION_GATE=the_world['0000000C'],
                CITY_COLORS=(gears.color.FieldGrey, gears.color.BugBlue,
                             gears.color.BattleshipGrey, gears.color.Twilight,
                             gears.color.Aquamarine),
                SHOP_NAME='',
                NPC_NAME='',
                DOOR_SIGN=None,
                INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000007B'] = splot.elements["INTERIOR"]
        the_world['0000007D'] = splot.elements["SHOPKEEPER"]
        the_world['0000007C'] = splot.elements["FOYER"]
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "Warehouse District",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='HoliznaCC0 - Anxiety.ogg',
            combat_music='HoliznaCC0 - Punk.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_11")
        the_world['0000000D'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_11",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.northeast,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_11")
        mygate = self.register_element("_MISSION_GATE_11",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_11")
        the_world['0000000E'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 2, 7)

        splot = self.add_sub_plot(
            nart,
            "DUNGEON_GENERIC",
            elements=dict(METROSCENE=the_world['0000000D'],
                          METRO=the_world['0000000D'].metrodat,
                          MISSION_GATE=the_world['0000000E'],
                          DG_NAME='Warehouse 4',
                          DG_ARCHITECTURE=gharchitecture.IndustrialBuilding(),
                          DG_SCENE_TAGS=[
                              gears.tags.SCENE_DUNGEON,
                              gears.tags.SCENE_BUILDING,
                              gears.tags.SCENE_WAREHOUSE
                          ],
                          DG_MONSTER_TAGS=['GUARD', 'SYNTH', 'ROBOT'],
                          DG_PARENT_SCENE=the_world['0000000D'],
                          DG_EXPLO_MUSIC='HoliznaCC0 - Anxiety.ogg',
                          DG_COMBAT_MUSIC='HoliznaCC0 - Punk.ogg',
                          DG_DECOR=None))
        the_world['00000077'] = splot.elements["LOCALE"]
        scutils.SCSceneConnection(
            the_world['0000000D'],
            splot.elements["LOCALE"],
            room1=ghterrain.IndustrialBuilding(tags=[
                pbge.randmaps.CITY_GRID_ROAD_OVERLAP,
                pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM
            ],
                                               door_sign=None,
                                               anchor=None),
            door1=ghwaypoints.LockedReinforcedDoor(
                name='Warehouse 4', anchor=pbge.randmaps.anchors.middle),
            room2=pbge.randmaps.rooms.FuzzyRoom(
                width=3, height=3, anchor=pbge.randmaps.anchors.south),
            door2=ghwaypoints.Exit(name='Exit',
                                   anchor=pbge.randmaps.anchors.south))
        splot = self.add_sub_plot(
            nart,
            "DUNGEON_GENERIC",
            elements=dict(METROSCENE=the_world['0000000D'],
                          METRO=the_world['0000000D'].metrodat,
                          MISSION_GATE=the_world['0000000E'],
                          DG_NAME='Warehouse 13',
                          DG_ARCHITECTURE=gharchitecture.IndustrialBuilding(),
                          DG_SCENE_TAGS=[
                              gears.tags.SCENE_DUNGEON,
                              gears.tags.SCENE_WAREHOUSE,
                              gears.tags.SCENE_BUILDING
                          ],
                          DG_MONSTER_TAGS=['GUARD', 'SYNTH', 'ROBOT'],
                          DG_PARENT_SCENE=the_world['0000000D'],
                          DG_EXPLO_MUSIC='HoliznaCC0 - Anxiety.ogg',
                          DG_COMBAT_MUSIC='HoliznaCC0 - Punk.ogg',
                          DG_DECOR=None))
        the_world['0000009B'] = splot.elements["LOCALE"]
        scutils.SCSceneConnection(
            the_world['0000000D'],
            splot.elements["LOCALE"],
            room1=ghterrain.IndustrialBuilding(tags=[
                pbge.randmaps.CITY_GRID_ROAD_OVERLAP,
                pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM
            ],
                                               door_sign=None,
                                               anchor=None),
            door1=ghwaypoints.ReinforcedDoor(
                name='Warehouse 13', anchor=pbge.randmaps.anchors.middle),
            room2=pbge.randmaps.rooms.ClosedRoom(
                width=3, height=3, anchor=pbge.randmaps.anchors.south),
            door2=ghwaypoints.Exit(name='Exit',
                                   anchor=pbge.randmaps.anchors.south))
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "Residential District",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='Anthem of Rain - So My Love - Instrumental.ogg',
            combat_music='Late.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_12")
        the_world['0000000F'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_12",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.north,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_12")
        mygate = self.register_element("_MISSION_GATE_12",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_12")
        the_world['00000010'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 5, 6)

        splot = self.add_sub_plot(
            nart,
            "SHOP_TAVERN",
            elements=dict(LOCALE=the_world['0000000F'],
                          METROSCENE=the_world['0000000F'],
                          METRO=the_world['0000000F'].metrodat,
                          MISSION_GATE=the_world['00000010'],
                          CITY_COLORS=(gears.color.GothSkin,
                                       gears.color.FreedomBlue,
                                       gears.color.Ebony, gears.color.Charcoal,
                                       gears.color.PlasmaBlue),
                          SHOP_NAME='Contraband Coffee',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.CafeSign1East,
                                     ghterrain.CafeSign1South),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000057'] = splot.elements["INTERIOR"]
        the_world['00000059'] = splot.elements["SHOPKEEPER"]
        the_world['00000058'] = splot.elements["FOYER"]

        the_world['0000007A'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['0000000F'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Hacker'],
            faction=None,
            combatant=True)
        the_world['00000058'].contents.append(the_world['0000007A'])
        the_world['00000068'] = ghrooms.BushesRoom(name='Park',
                                                   anchor=None,
                                                   decorate=None)
        the_world['0000000F'].contents.append(the_world['00000068'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_HOSPITAL",
            elements=dict(LOCALE=the_world['0000000F'],
                          METROSCENE=the_world['0000000F'],
                          METRO=the_world['0000000F'].metrodat,
                          MISSION_GATE=the_world['00000010'],
                          CITY_COLORS=(gears.color.GothSkin,
                                       gears.color.FreedomBlue,
                                       gears.color.Ebony, gears.color.Charcoal,
                                       gears.color.PlasmaBlue),
                          SHOP_NAME='',
                          NPC_NAME='',
                          DOOR_SIGN=None,
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000009C'] = splot.elements["INTERIOR"]
        the_world['0000009E'] = splot.elements["SHOPKEEPER"]
        the_world['0000009D'] = splot.elements["FOYER"]
        splot = self.add_sub_plot(
            nart,
            "SHOP_GENERALSTORE",
            elements=dict(LOCALE=the_world['0000000F'],
                          METROSCENE=the_world['0000000F'],
                          METRO=the_world['0000000F'].metrodat,
                          MISSION_GATE=the_world['00000010'],
                          CITY_COLORS=(gears.color.GothSkin,
                                       gears.color.FreedomBlue,
                                       gears.color.Ebony, gears.color.Charcoal,
                                       gears.color.PlasmaBlue),
                          SHOP_NAME='',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.CrossedSwordsTerrainEast,
                                     ghterrain.CrossedSwordsTerrainSouth),
                          INTERIOR_TAGS=[
                              gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GARAGE
                          ]))
        the_world['0000009F'] = splot.elements["INTERIOR"]
        the_world['000000A0'] = splot.elements["FOYER"]
        the_world['000000A1'] = splot.elements["SHOPKEEPER"]
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            60,
            "The Dockyards",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC,
                gears.tags.CITY_NAUTICAL
            ],
            exploration_music='Anthem of Rain - Adaptation (Instrumental).ogg',
            combat_music='HoliznaCC0 - Punk.ogg')
        # Create a scene generator
        myroom = pbge.randmaps.rooms.Room(40,
                                          25,
                                          anchor=pbge.randmaps.anchors.north)
        myscenegen = pbge.randmaps.PartlyUrbanGenerator(
            myscene,
            game.content.gharchitecture.HumanScaleGreenzone(
                prepare=pbge.randmaps.prep.GradientPrep(
                    [[ghterrain.GreenZoneGrass, 0.69], [ghterrain.Sand, 0.94],
                     [ghterrain.Water, 1.0]]),
                mutate=pbge.randmaps.mutator.CellMutator(),
                wall_converter=pbge.randmaps.converter.
                WallOnlyOnFloorConverter(ghterrain.Bushes,
                                         ghterrain.GreenZoneGrass)),
            road_terrain=ghterrain.GravelFloor,
            urban_area=myroom)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_13")
        the_world['00000011'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_13",
            pbge.randmaps.rooms.Room(50,
                                     10,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_13")
        myscenegen.archi.prepare.band_rooms[1] = myroom
        the_world['00000012'] = myroom
        mygate = self.register_element("_MISSION_GATE_13",
                                       Exit(
                                           name="To The Docks",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_13")
        the_world['00000013'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 7, 5)

        splot = self.add_sub_plot(
            nart,
            "SHOP_GARAGE",
            elements=dict(
                LOCALE=the_world['00000011'],
                METROSCENE=the_world['00000011'],
                METRO=the_world['00000011'].metrodat,
                MISSION_GATE=the_world['00000013'],
                CITY_COLORS=(gears.color.Burlywood, gears.color.FreedomBlue,
                             gears.color.LunarGrey, gears.color.Cobalt,
                             gears.color.OrangeRed),
                SHOP_NAME='Search & Rescue HQ',
                NPC_NAME='',
                DOOR_SIGN=(ghterrain.RustyFixitShopSignEast,
                           ghterrain.RustyFixitShopSignSouth),
                INTERIOR_TAGS=[
                    gears.tags.SCENE_PUBLIC, gears.tags.SCENE_HOSPITAL
                ]))
        the_world['00000083'] = splot.elements["INTERIOR"]
        the_world['00000085'] = splot.elements["SHOPKEEPER"]
        the_world['00000084'] = splot.elements["FOYER"]

        the_world['00000086'] = pbge.randmaps.rooms.ClosedRoom(
            name='Clinic', anchor=None, decorate=gharchitecture.BunkerDecor())
        the_world['00000083'].contents.append(the_world['00000086'])

        the_world['00000087'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000011'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Paramedic'],
            faction=None,
            combatant=False)
        the_world['00000086'].contents.append(the_world['00000087'])
        the_world['00000088'] = ghwaypoints.RecoveryBed(
            name='', desc='', anchor=pbge.randmaps.anchors.middle)
        the_world['00000086'].contents.append(the_world['00000088'])
        the_world['00000089'] = gears.selector.random_character(
            self.rank,
            local_tags=the_world['00000011'].attributes,
            camp=nart.camp,
            name='',
            job=gears.jobs.ALL_JOBS['Firefighter'],
            faction=None,
            combatant=True)
        the_world['00000084'].contents.append(the_world['00000089'])
        splot = self.add_sub_plot(
            nart,
            "EMPTY_BUILDING",
            elements=dict(
                LOCALE=the_world['00000011'],
                METROSCENE=the_world['00000011'],
                METRO=the_world['00000011'].metrodat,
                MISSION_GATE=the_world['00000013'],
                CITY_COLORS=(gears.color.Burlywood, gears.color.FreedomBlue,
                             gears.color.LunarGrey, gears.color.Cobalt,
                             gears.color.OrangeRed),
                INTERIOR_NAME='The House of Blades',
                INTERIOR_TAGS=[
                    gears.tags.SCENE_PUBLIC, gears.tags.SCENE_GARAGE,
                    gears.tags.SCENE_SHOP
                ],
                DOOR_SIGN=(ghterrain.BladesOfCrihnaSignEast,
                           ghterrain.BladesOfCrihnaSignSouth),
                DOOR_TYPE=ghwaypoints.ScrapIronDoor,
                INTERIOR_FACTION=gears.factions.BladesOfCrihna,
                EXTERIOR_TERRSET=ghterrain.ScrapIronBuilding,
                INTERIOR_ARCHITECTURE=gharchitecture.FortressBuilding,
                INTERIOR_DECOR=gharchitecture.FactoryDecor()))
        the_world['000000A7'] = splot.elements["INTERIOR"]
        the_world['000000A8'] = splot.elements["FOYER"]
        # Build the city here, store it in the_world
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1, ))
        myscene = gears.GearHeadScene(
            50,
            50,
            "The Spaceport",
            player_team=team1,
            civilian_team=team2,
            scale=gears.scale.HumanScale,
            is_metro=True,
            faction=None,
            attributes=[
                gears.tags.SCENE_OUTDOORS, gears.tags.City,
                personality.GreenZone, gears.tags.SCENE_PUBLIC
            ],
            exploration_music='HoliznaCC0 - Lost In Space.ogg',
            combat_music='HoliznaCC0 - Punk.ogg')
        # Create a scene generator
        myscenegen = pbge.randmaps.CityGridGenerator(
            myscene,
            gharchitecture.HumanScaleGreenzone(
                floor_terrain=ghterrain.GreenZoneGrass),
            road_terrain=ghterrain.GravelFloor,
            road_thickness=3)
        # Register the city scene and the metro data
        self.register_scene(nart, myscene, myscenegen, ident="_CITY_14")
        the_world['00000014'] = myscene
        # Create the entry/exit point.
        myroom = self.register_element(
            "_ENTRY_ROOM_14",
            pbge.randmaps.rooms.Room(3,
                                     3,
                                     anchor=pbge.randmaps.anchors.south,
                                     tags=[pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="_CITY_14")
        mygate = self.register_element("_MISSION_GATE_14",
                                       Exit(
                                           name="Exit",
                                           desc='Where do you want to go?',
                                           anchor=pbge.randmaps.anchors.middle,
                                           plot_locked=True),
                                       dident="_ENTRY_ROOM_14")
        the_world['00000015'] = mygate
        if 'WORLDMAP_6':
            nart.camp.campdata['WORLDMAP_6'].associate_gate_with_map(mygate)
            mynode = campfeatures.WorldMapNode(
                destination=myscene,
                entrance=mygate,
            )
            nart.camp.campdata['WORLDMAP_6'].add_node(mynode, 4, 4)

        splot = self.add_sub_plot(
            nart,
            "SHOP_TAVERN",
            elements=dict(LOCALE=the_world['00000014'],
                          METROSCENE=the_world['00000014'],
                          METRO=the_world['00000014'].metrodat,
                          MISSION_GATE=the_world['00000015'],
                          CITY_COLORS=(gears.color.White,
                                       gears.color.KettelPurple,
                                       gears.color.DeepGrey, gears.color.Black,
                                       gears.color.Celadon),
                          SHOP_NAME='Fafnir Pub',
                          NPC_NAME='',
                          DOOR_SIGN=(ghterrain.DragonSignEast,
                                     ghterrain.DragonSignSouth),
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['00000038'] = splot.elements["INTERIOR"]
        the_world['0000003A'] = splot.elements["SHOPKEEPER"]
        the_world['00000039'] = splot.elements["FOYER"]
        the_world['0000005A'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Guards Room', anchor=None, decorate=None)
        the_world['00000014'].contents.append(the_world['0000005A'])
        the_world['0000005B'] = pbge.randmaps.rooms.FuzzyRoom(
            name='Guards Room 2', anchor=None, decorate=None)
        the_world['00000014'].contents.append(the_world['0000005B'])
        splot = self.add_sub_plot(
            nart,
            "SHOP_BLACKMARKET",
            elements=dict(LOCALE=the_world['00000014'],
                          METROSCENE=the_world['00000014'],
                          METRO=the_world['00000014'].metrodat,
                          MISSION_GATE=the_world['00000015'],
                          CITY_COLORS=(gears.color.White,
                                       gears.color.KettelPurple,
                                       gears.color.DeepGrey, gears.color.Black,
                                       gears.color.Celadon),
                          SHOP_NAME='Gifts from Away',
                          NPC_NAME='',
                          DOOR_SIGN=None,
                          INTERIOR_TAGS=[gears.tags.SCENE_PUBLIC]))
        the_world['0000005C'] = splot.elements["INTERIOR"]
        the_world['0000005D'] = splot.elements["FOYER"]
        the_world['0000005E'] = splot.elements["SHOPKEEPER"]


class City_ropp_2(Plot):
    LABEL = "CITY_ropp_2"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000002']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000001']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '0000000A')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000008'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'MILTENT_ropp_15',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'MOBILEHQ_ropp_16',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.elements["LOCALE"].contents.append(ghterrain.CorsairTerrset())
        self.add_sub_plot(nart,
                          'FIELDHOSPITAL_ropp_18',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'EMPTYBUILDING_ropp_29',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_36',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class MilitaryTent_ropp_15(Plot):
    LABEL = "MILTENT_ropp_15"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000017']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000016']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_19',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_20',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_21',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_22',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_23',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Waypoint_ropp_19(Plot):
    LABEL = "WAYPOINT_ropp_19"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['0000001D']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_20(Plot):
    LABEL = "WAYPOINT_ropp_20"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['0000001E']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_21(Plot):
    LABEL = "WAYPOINT_ropp_21"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['0000001F']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class NonPlayerCharacter_ropp_22(Plot):
    LABEL = "NPC_ropp_22"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000020']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init

        if 'the Supply Depot':
            self.shop_name_24 = 'the Supply Depot'
        else:
            self.shop_name_24 = str(self.elements["NPC"]) + "'s Shop"
        self.shop_24 = services.Shop(
            npc=self.elements["NPC"],
            ware_types=game.services.GENERAL_STORE_PLUS_MECHA,
            rank=self.rank + random.randint(0, 15),
            shop_faction=self.elements["NPC"].faction,
            buy_stolen_items=False)
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(
            Offer("[OPENSHOP]",
                  context=ContextTag([context.OPEN_SHOP]),
                  data=dict(shop_name=self.shop_name_24, wares='wares'),
                  effect=self.shop_24))
        return mylist


class NonPlayerCharacter_ropp_23(Plot):
    LABEL = "NPC_ropp_23"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000021']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init

        if 'the Supply Depot':
            self.shop_name_25 = 'the Supply Depot'
        else:
            self.shop_name_25 = str(self.elements["NPC"]) + "'s Shop"
        self.shop_25 = services.Shop(npc=self.elements["NPC"],
                                     ware_types=game.services.MECHA_STORE,
                                     rank=self.rank + random.randint(0, 15),
                                     shop_faction=self.elements["NPC"].faction,
                                     buy_stolen_items=False)
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(
            Offer("[OPENSHOP]",
                  context=ContextTag([context.OPEN_SHOP]),
                  data=dict(shop_name=self.shop_name_25, wares='mecha'),
                  effect=self.shop_25))
        return mylist


class MobileHQ_ropp_16(Plot):
    LABEL = "MOBILEHQ_ropp_16"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000019']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000018']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'MNPC_ropp_26',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'MNPC_ropp_27',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'MNPC_ropp_28',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class MajorNonPlayerCharacter_ropp_26(Plot):
    LABEL = "MNPC_ropp_26"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000022']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class MajorNonPlayerCharacter_ropp_27(Plot):
    LABEL = "MNPC_ropp_27"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000023']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]

        self._offer163 = scutils.DialogueOfferHandler(163, single_use=False)
        self._offer164 = scutils.DialogueOfferHandler(164, single_use=False)
        self._offer165 = scutils.DialogueOfferHandler(165, single_use=False)
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()

        if self._offer163.can_add_offer():
            mylist.append(
                Offer(
                    "We are here to get rid of the Aegis Consulate, but the rulers of Pirate's Point aren't going to be happy about us barging in, so we'll probably have to fight them as well.",
                    context=ContextTag(["INFO"]),
                    data={'subject': 'fighting the war'},
                    subject='',
                    subject_start=True,
                    effect=self._offer163.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if self._offer164.can_add_offer():
            mylist.append(
                Offer(
                    "Your job will be to capture territories one at a time. You can only attack from a territory we already control. Once a faction's home base has been captured, that faction will be eliminated. The Aegis Consulate is due south from here, along the coastline.",
                    context=ContextTag(["CUSTOM"]),
                    data={'reply': 'So how do we proceed?'},
                    subject='get rid of the Aegis Consulate',
                    subject_start=False,
                    effect=self._offer164.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if self._offer165.can_add_offer():
            mylist.append(
                Offer(
                    "That thing I said about capturing a home base? It also applies to us. During the operation, you have to make sure that enemy troops don't get too close to the Solar Navy camp. If this base is captured, we'll have no choice but to abort the operation.",
                    context=ContextTag(["CUSTOMREPLY"]),
                    data={'reply': 'Is there anything else I need to know?'},
                    subject='The Aegis Consulate is due south from here',
                    subject_start=False,
                    effect=self._offer165.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=True))
        return mylist


class MajorNonPlayerCharacter_ropp_28(Plot):
    LABEL = "MNPC_ropp_28"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000024']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class MobileHQ_ropp_18(Plot):
    LABEL = "FIELDHOSPITAL_ropp_18"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000001C']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000001B']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000001A']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class EmptyBuilding_ropp_29(Plot):
    LABEL = "EMPTYBUILDING_ropp_29"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000026']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000025']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_30',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_31',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_32',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class NonPlayerCharacter_ropp_30(Plot):
    LABEL = "NPC_ropp_30"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000027']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'RLM_Relationship',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class NonPlayerCharacter_ropp_31(Plot):
    LABEL = "NPC_ropp_31"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000028']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'RLM_Relationship',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class NonPlayerCharacter_ropp_32(Plot):
    LABEL = "NPC_ropp_32"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000029']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'RLM_Relationship',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class Room_ropp_36(Plot):
    LABEL = "ROOM_ropp_36"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000002A']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_37',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_153',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class NonPlayerCharacter_ropp_37(Plot):
    LABEL = "NPC_ropp_37"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000002B']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class NonPlayerCharacter_ropp_153(Plot):
    LABEL = "NPC_ropp_153"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000008F']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class City_ropp_3(Plot):
    LABEL = "CITY_ropp_3"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000004']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000003']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('0000000E'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'TOWNHALL_ropp_38',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'HOSPITAL_ropp_43',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'MECHASHOP_ropp_57',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        for t in range(3):
            self.add_sub_plot(nart,
                              'ADD_BORING_NPC',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'BLACKMARKET_ropp_154',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        for t in range(3):
            self.add_sub_plot(nart,
                              'RANDOM_LANCEMATE',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_148',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class TownHall_ropp_38(Plot):
    LABEL = "TOWNHALL_ropp_38"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000002E']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000002D']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000002C']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        self._offer166 = scutils.DialogueOfferHandler(166, single_use=False)
        #: plot_actions

        self.add_sub_plot(nart,
                          'MNPC_ropp_139',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()

        if self._offer166.can_add_offer():
            mylist.append(
                Offer(
                    "Your mission will be to move troops into unguarded territories, and take back any territory captured by our enemies. Capturing an enemy's home base will remove them from the battle. But be careful- if the uptown district gets captured, we'll be the ones who lose.",
                    context=ContextTag(["INFO"]),
                    data={'subject': "the defence of Pirate's Point"},
                    subject='',
                    subject_start=True,
                    effect=self._offer166.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        return mylist

    #: plot_methods


class MajorNonPlayerCharacter_ropp_139(Plot):
    LABEL = "MNPC_ropp_139"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000007E']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class Hospital_ropp_43(Plot):
    LABEL = "HOSPITAL_ropp_43"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000037']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000036']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000035']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class MechaShop_ropp_57(Plot):
    LABEL = "MECHASHOP_ropp_57"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000050']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000004F']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000004E']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class Room_ropp_148(Plot):
    LABEL = "ROOM_ropp_148"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000008A']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_149',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_150',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class NonPlayerCharacter_ropp_149(Plot):
    LABEL = "NPC_ropp_149"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000008B']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class NonPlayerCharacter_ropp_150(Plot):
    LABEL = "NPC_ropp_150"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000008C']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class BlackMarket_ropp_154(Plot):
    LABEL = "BLACKMARKET_ropp_154"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000092']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000091']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000090']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class StartingPlot_ropp_4(Plot):
    LABEL = "START_PLOT_ropp"
    active = True
    scope = True

    #: plot_properties
    def custom_init(self, nart):
        pc_tags = nart.camp.pc.get_tags()
        if pc_tags.issuperset([]) and pc_tags.isdisjoint(['tags.Criminal']):
            element_alias_list = []

            self.elements["ENTRANACE"] = nart.camp.campdata[THE_WORLD].get(
                '00000002')
            nart.camp.go(self.elements["ENTRANACE"])
            self.did_cutscene = False
            #: plot_init
            #: plot_actions
            #: plot_subplots
            return True

    #: plot_methods
    def t_START(self, camp):
        if not self.did_cutscene:

            pbge.alert(
                "The Solar Navy has declared that it is going to remove the Aegis Consulate from Pirate's Point. You arrive at the military camp they have set up just north of the city. There should be plenty of opportunities to find good work here."
            )
            self.did_cutscene = True


class StartingPlot_ropp_5(Plot):
    LABEL = "START_PLOT_ropp"
    active = True
    scope = True

    #: plot_properties
    def custom_init(self, nart):
        pc_tags = nart.camp.pc.get_tags()
        if pc_tags.issuperset(['tags.Criminal']) and pc_tags.isdisjoint([]):
            element_alias_list = []

            self.elements["ENTRANACE"] = nart.camp.campdata[THE_WORLD].get(
                '00000004')
            nart.camp.go(self.elements["ENTRANACE"])
            self.did_cutscene = False
            #: plot_init
            #: plot_actions
            #: plot_subplots
            return True

    #: plot_methods
    def t_START(self, camp):
        if not self.did_cutscene:

            pbge.alert(
                "You are in Pirate's Point to do some shopping and visit some old friends when suddenly the air raid siren goes off. You quickly learn that the Solar Navy has attacked, intending to destroy the Aegis Consulate in the southern part of town."
            )
            pbge.alert(
                "As a freelance mecha pilot, you're not sure whether to be glad about all the missions that are likely to be available or terrified because you are standing in the middle of a bona fide war zone."
            )
            self.did_cutscene = True


class City_ropp_7(Plot):
    LABEL = "CITY_ropp_7"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000006']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000005']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000010'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'TOWNHALL_ropp_39',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'HOSPITAL_ropp_45',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'GARAGE_ropp_46',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        for t in range(3):
            self.add_sub_plot(nart,
                              'ADD_BORING_NPC',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'EMPTYBUILDING_ropp_155',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        for t in range(3):
            self.add_sub_plot(nart,
                              'RANDOM_LANCEMATE',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class TownHall_ropp_39(Plot):
    LABEL = "TOWNHALL_ropp_39"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000031']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000030']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000002F']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        self._offer167 = scutils.DialogueOfferHandler(167, single_use=False)
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_152',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()

        if self._offer167.can_add_offer():
            mylist.append(
                Offer(
                    "Our objective is to capture the Solar Navy's base. When a faction's home base is captured, that faction loses the war. We must also defend the Lunar district. The pirate scum who run this city will also try to fight, but they may end up getting in our way.",
                    context=ContextTag(["INFO"]),
                    data={'subject': "the battle for Pirate's Point"},
                    subject='',
                    subject_start=True,
                    effect=self._offer167.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        return mylist

    #: plot_methods


class NonPlayerCharacter_ropp_152(Plot):
    LABEL = "NPC_ropp_152"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000008E']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class Hospital_ropp_45(Plot):
    LABEL = "HOSPITAL_ropp_45"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000003D']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000003C']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000003B']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class Garage_ropp_46(Plot):
    LABEL = "GARAGE_ropp_46"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000040']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000003F']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000003E']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_151',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist

    #: plot_methods


class NonPlayerCharacter_ropp_151(Plot):
    LABEL = "NPC_ropp_151"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000008D']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class EmptyBuilding_ropp_155(Plot):
    LABEL = "EMPTYBUILDING_ropp_155"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000094']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000093']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_156',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_157',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_158',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_159',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Waypoint_ropp_156(Plot):
    LABEL = "WAYPOINT_ropp_156"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000095']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_157(Plot):
    LABEL = "WAYPOINT_ropp_157"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000096']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_158(Plot):
    LABEL = "WAYPOINT_ropp_158"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000097']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_159(Plot):
    LABEL = "WAYPOINT_ropp_159"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000098']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class City_ropp_8(Plot):
    LABEL = "CITY_ropp_8"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000008']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000007']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '0000000A')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000013'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'EMPTYBUILDING_ropp_40',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'OFFICEBUILDING_ropp_52',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'GENERALSTORE_ropp_85',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        for t in range(3):
            self.add_sub_plot(nart,
                              'ADD_BORING_NPC',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'LOCAL_PROBLEM',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="PROBLEM87")
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_53',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        for t in range(1):
            self.add_sub_plot(nart,
                              'RANDOM_LANCEMATE',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'DUNGEONLEVEL_ropp_162',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    def PROBLEM87_WIN(self, camp):
        camp.campdata[LOCAL_PROBLEMS_SOLVED] += 1


class EmptyBuilding_ropp_40(Plot):
    LABEL = "EMPTYBUILDING_ropp_40"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000033']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000032']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        self.elements["ROOM"].contents.append(
            ghwaypoints.CyberdocTerminal(
                shop=services.Shop(npc=None,
                                   rank=self.rank + random.randint(1, 25),
                                   ware_types=services.CYBERWARE_STORE)))
        #: plot_actions

        self.add_sub_plot(nart,
                          'MNPC_ropp_41',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_49',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class MajorNonPlayerCharacter_ropp_41(Plot):
    LABEL = "MNPC_ropp_41"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000034']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]

        self._offer59 = scutils.DialogueOfferHandler(59, single_use=False)

        self._offer62 = scutils.DialogueOfferHandler(62, single_use=True)
        self._offer60 = scutils.DialogueOfferHandler(60, single_use=False)
        self._offer61 = scutils.DialogueOfferHandler(61, single_use=True)
        self._offer63 = scutils.DialogueOfferHandler(63, single_use=False)
        self._offer68 = scutils.DialogueOfferHandler(68, single_use=False)
        self._offer73 = scutils.DialogueOfferHandler(73, single_use=False)
        self._offer74 = scutils.DialogueOfferHandler(74, single_use=False)
        #: plot_actions
        #: plot_subplots
        return True

    def _ropp64_effect(self, camp):

        camp.campdata['lets_get_tattoos'] = 1
        camp.credits += -80000
        camp.dole_xp(50)
        camp.pc.add_badge(
            gears.meritbadges.TagReactionBadge(
                'Inked', 'You received a basic tattoo from Kira.',
                dict([(personality.Passionate, 5)]), []))
        pbge.alert(
            "You lie on the tattoo bench and the process begins. It is a little uncomfortable, but nothing you can't handle."
        )

    def _ropp69_effect(self, camp):

        camp.campdata['lets_get_tattoos'] = 1
        camp.credits += -200000
        camp.dole_xp(100)
        camp.pc.add_badge(
            gears.meritbadges.TagReactionBadge(
                'Inked',
                'You received a deluxe tattoo from Kira. Now everyone can see your adventurous spirit.',
                dict([(personality.Passionate, 10)]), []))
        pbge.alert(
            "You lie on the tattoo bench and the process begins. Kira was wrong; you don't feel a bit of discomfort. You feel a great deal of discomfort, as though you were being attacked by a swarm of artistic hornets."
        )

    def _ropp75_effect(self, camp):

        camp.campdata['lets_get_tattoos'] = 1
        camp.credits += -650000
        camp.dole_xp(200)
        camp.pc.add_badge(
            gears.meritbadges.TagReactionBadge(
                'Inked',
                'You received a masterpiece tattoo from Kira. Annyone who knows the value of such things will now recognize both your adventurous spirit and your good taste.',
                dict([(personality.Passionate, 15)]), []))
        pbge.alert(
            'You lie on the tattoo bench and the process begins. Kira brings you to the edge of hell. Just when you think you cannot stand any more, the tattoo is finished and you have become a living work of art.'
        )

    def NPC_offers(self, camp):
        mylist = list()

        if camp.campdata.get('lets_get_tattoos', 0) == 0:
            if self._offer59.can_add_offer():
                mylist.append(
                    Offer(
                        "That's what I like to hear. I offer artwork for all budgets and pain thresholds. You can get a basic tattoo for $80,000, a deluxe tattoo for $200,000, or a masterpiece for $650,000.",
                        context=ContextTag(["CUSTOM"]),
                        data={'reply': "I'd like to get a tattoo, please."},
                        subject='kira_tattoo_1234567890',
                        subject_start=True,
                        effect=self._offer59.get_effect(
                            #: dialogue_effect
                        ),
                        no_repeats=True,
                        dead_end=False))
            #: dialogue_also
        #: dialogue_elif
        #: dialogue_else

        else:
            if self._offer62.can_add_offer():
                mylist.append(
                    Offer(
                        "You've already gotten a tattoo, and thanks to the war happening outside I've run out of needles. Sorry.",
                        context=ContextTag(["CUSTOM"]),
                        data={'reply': "I'd like to get a tattoo, please."},
                        subject='',
                        subject_start=True,
                        effect=self._offer62.get_effect(
                            #: dialogue_effect
                        ),
                        no_repeats=True,
                        dead_end=False))
            #: dialogue_also
        if self._offer60.can_add_offer():
            mylist.append(
                Offer(
                    "[HELLO] Welcome to Kira's Tattoos and Body Moodification.",
                    context=ContextTag(["HELLO"]),
                    data={},
                    subject='',
                    subject_start=True,
                    effect=self._offer60.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if self._offer61.can_add_offer():
            mylist.append(
                Offer(
                    "For that, you can use the cyber terminal over there. My robotic surgical bench will install any parts you want. It's probably safer and more hygenic than when I used to do things by hand, but not nearly as much fun.",
                    context=ContextTag(["INFO"]),
                    data={'subject': 'body modification'},
                    subject='',
                    subject_start=True,
                    effect=self._offer61.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if camp.credits >= 80000:
            if self._offer63.can_add_offer():
                mylist.append(
                    Offer(
                        'A good choice for a beginner. This design may be small, but the quality is unsurpassed. Just lie back and try to think happy thoughts.',
                        context=ContextTag(["CUSTOMREPLY"]),
                        data={
                            'reply': 'I would like the basic tattoo, please.'
                        },
                        subject='kira_tattoo_1234567890',
                        subject_start=False,
                        effect=self._offer63.get_effect(
                            effect=self._ropp64_effect, ),
                        no_repeats=True,
                        dead_end=True))
            #: dialogue_also
        #: dialogue_elif
        #: dialogue_else
        if camp.credits >= 200000:
            if self._offer68.can_add_offer():
                mylist.append(
                    Offer(
                        'The most popular choice. Choose your design, then lie back and relax. You may feel a bit of discomfort.',
                        context=ContextTag(["CUSTOMREPLY"]),
                        data={'reply': "I'm interested in the deluxe tattoo."},
                        subject='kira_tattoo_1234567890',
                        subject_start=False,
                        effect=self._offer68.get_effect(
                            effect=self._ropp69_effect, ),
                        no_repeats=True,
                        dead_end=True))
            #: dialogue_also
        #: dialogue_elif
        #: dialogue_else
        if self._offer73.can_add_offer():
            mylist.append(
                Offer(
                    '[UNDERSTOOD] If you ever change your mind, you know where to come.',
                    context=ContextTag(["CUSTOMREPLY"]),
                    data={
                        'reply':
                        "On second thought, maybe I don't want a tattoo right now."
                    },
                    subject='kira_tattoo_1234567890',
                    subject_start=False,
                    effect=self._offer73.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if camp.credits >= 650000:
            if self._offer74.can_add_offer():
                mylist.append(
                    Offer(
                        "Wow, it's rare that I get the chance to meet someone with such passion for art. Lie down on the tattoo bench and we'll get started right away. By the way, this is going to hurt a lot.",
                        context=ContextTag(["CUSTOMREPLY"]),
                        data={
                            'reply':
                            "I can't settle for less than the masterpiece."
                        },
                        subject='kira_tattoo_1234567890',
                        subject_start=False,
                        effect=self._offer74.get_effect(
                            effect=self._ropp75_effect, ),
                        no_repeats=True,
                        dead_end=True))
            #: dialogue_also
        #: dialogue_elif
        #: dialogue_else
        return mylist


class Waypoint_ropp_49(Plot):
    LABEL = "WAYPOINT_ropp_49"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000044']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class OfficeBuilding_ropp_52(Plot):
    LABEL = "OFFICEBUILDING_ropp_52"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000049']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000048']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_102',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_104',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_106',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_112',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_113',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Room_ropp_102(Plot):
    LABEL = "ROOM_ropp_102"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000005F']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(
            nart,
            "MONSTER_ENCOUNTER",
            elements=dict(TYPE_TAGS=['ANIMAL', 'BUG', 'CITY', 'VERMIN']))
        return True


    #: plot_methods
class Room_ropp_104(Plot):
    LABEL = "ROOM_ropp_104"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000060']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(
            nart,
            "MONSTER_ENCOUNTER",
            elements=dict(TYPE_TAGS=['ANIMAL', 'BUG', 'CITY', 'VERMIN']))
        return True


    #: plot_methods
class Room_ropp_106(Plot):
    LABEL = "ROOM_ropp_106"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000061']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_107',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_110',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_111',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class NonPlayerCharacter_ropp_107(Plot):
    LABEL = "NPC_ropp_107"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000062']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]

        self._offer108 = scutils.DialogueOfferHandler(108, single_use=False)
        self._offer109 = scutils.DialogueOfferHandler(109, single_use=True)
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()

        if self._offer108.can_add_offer():
            mylist.append(
                Offer(
                    '[HELLO] The Nogos is the rowdiest part of town... Or at least it was until the war started.',
                    context=ContextTag(["HELLO"]),
                    data={},
                    subject='',
                    subject_start=True,
                    effect=self._offer108.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        if self._offer109.can_add_offer():
            mylist.append(
                Offer(
                    "It wouldn't be a bad neighborhood if not for the street gangs. And the monsters wandering in from the dead zone. Plus the lack of infrastruucture, security, hope...",
                    context=ContextTag(["INFO"]),
                    data={'subject': 'the Nogos'},
                    subject='',
                    subject_start=True,
                    effect=self._offer109.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        return mylist


class Waypoint_ropp_110(Plot):
    LABEL = "WAYPOINT_ropp_110"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000063']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Waypoint_ropp_111(Plot):
    LABEL = "WAYPOINT_ropp_111"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000064']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Room_ropp_112(Plot):
    LABEL = "ROOM_ropp_112"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000065']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Room_ropp_113(Plot):
    LABEL = "ROOM_ropp_113"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000066']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(
            nart,
            "MONSTER_ENCOUNTER",
            elements=dict(TYPE_TAGS=['ANIMAL', 'BUG', 'CITY', 'VERMIN']))
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_115',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Waypoint_ropp_115(Plot):
    LABEL = "WAYPOINT_ropp_115"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000067']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Room_ropp_53(Plot):
    LABEL = "ROOM_ropp_53"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000004A']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          "ONE_SHOT_MONSTER_ENCOUNTER",
                          elements=dict(TYPE_TAGS=['CITY', 'DEVO', 'VERMIN']))
        return True


    #: plot_methods
class GeneralStore_ropp_85(Plot):
    LABEL = "GENERALSTORE_ropp_85"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000056']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000055']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000054']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class DungeonLevel_ropp_162(Plot):
    LABEL = "DUNGEONLEVEL_ropp_162"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000009A']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        # Do the connection here.
        #scutils.SCSceneConnection(self.elements["PARENT_SCENE"], self.elements["LOCALE"], room1=ghterrain.BrickBuilding(tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM], door_sign=None, anchor=None), door1=ghwaypoints.ScrapIronDoor(name='Abandoned Building', anchor=pbge.randmaps.anchors.middle), room2=pbge.randmaps.rooms.OpenRoom(width=3, height=3, anchor=pbge.randmaps.anchors.south), door2=ghwaypoints.Exit(name='Exit', anchor=pbge.randmaps.anchors.south))
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class City_ropp_9(Plot):
    LABEL = "CITY_ropp_9"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '0000000A']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000009']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('0000000C'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'GARAGE_ropp_56',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'HOSPITAL_ropp_117',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_118',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_120',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'DUNGEONLEVEL_ropp_122',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class Garage_ropp_56(Plot):
    LABEL = "GARAGE_ropp_56"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000004D']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000004C']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000004B']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class Hospital_ropp_117(Plot):
    LABEL = "HOSPITAL_ropp_117"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000006B']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000006A']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000069']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class Room_ropp_118(Plot):
    LABEL = "ROOM_ropp_118"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000006C']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Room_ropp_120(Plot):
    LABEL = "ROOM_ropp_120"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000006D']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class DungeonLevel_ropp_122(Plot):
    LABEL = "DUNGEONLEVEL_ropp_122"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000006F']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        # Do the connection here.
        #scutils.SCSceneConnection(self.elements["PARENT_SCENE"], self.elements["LOCALE"], room1=pbge.randmaps.rooms.OpenRoom(width=3, height=3, anchor=pbge.randmaps.anchors.north), door1=ghwaypoints.Exit(name='To the Crash Site', anchor=pbge.randmaps.anchors.north), room2=pbge.randmaps.rooms.OpenRoom(width=3, height=3, anchor=pbge.randmaps.anchors.south), door2=ghwaypoints.Exit(name='To the Scrapyard', anchor=pbge.randmaps.anchors.south))
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'DUNGEON_ropp_123',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Dungeon_ropp_123(Plot):
    LABEL = "DUNGEON_ropp_123"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['DUNGEON'] = nart.camp.campdata[THE_WORLD]['00000071']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'DUNGEON_ENTRY_ropp_125',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'DUNGEON_GOAL_ropp_131',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class DungeonEntry_ropp_125(Plot):
    LABEL = "DUNGEON_ENTRY_ropp_125"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000075']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init

        self.one_time_effect_127_ready = True
        #: plot_subplots
        return True

    def LOCALE_ENTER(self, camp):

        if self.one_time_effect_127_ready:

            pbge.alert(
                'This appears to be the wreckage of the spaceship which crashed, creating the scrapyard in the first place.'
            )
            self.one_time_effect_127_ready = False


class DungeonGoal_ropp_131(Plot):
    LABEL = "DUNGEON_GOAL_ropp_131"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000078']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_177',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Room_ropp_177(Plot):
    LABEL = "ROOM_ropp_177"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['000000A2']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_178',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class Waypoint_ropp_178(Plot):
    LABEL = "WAYPOINT_ropp_178"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['000000A3']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class City_ropp_10(Plot):
    LABEL = "CITY_ropp_10"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '0000000C']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000000B']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '00000004')),
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '00000008')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000010'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'WEAPONSTORE_ropp_48',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ARMORSTORE_ropp_51',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'GENERALSTORE_ropp_58',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'LOCAL_PROBLEM',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="PROBLEM92")
        for t in range(3):
            self.add_sub_plot(nart,
                              'ADD_BORING_NPC',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'CYBERCLINIC_ropp_137',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions
        #: plot_subplots
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    def PROBLEM92_WIN(self, camp):
        camp.campdata[LOCAL_PROBLEMS_SOLVED] += 1


class WeaponStore_ropp_48(Plot):
    LABEL = "WEAPONSTORE_ropp_48"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000043']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000042']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000041']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class ArmorStore_ropp_51(Plot):
    LABEL = "ARMORSTORE_ropp_51"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000047']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000046']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000045']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class GeneralStore_ropp_58(Plot):
    LABEL = "GENERALSTORE_ropp_58"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000053']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000052']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000051']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_132',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist

    #: plot_methods


class NonPlayerCharacter_ropp_132(Plot):
    LABEL = "NPC_ropp_132"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000079']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]

        self._offer134 = scutils.DialogueOfferHandler(134, single_use=False)
        #: plot_actions

        self.add_sub_plot(nart,
                          'RLM_Relationship',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()

        if self._offer134.can_add_offer():
            mylist.append(
                Offer(
                    "[HELLO] I've been stuck here because of the fighting, and haven't even been able to make any money off of it.",
                    context=ContextTag(["HELLO"]),
                    data={},
                    subject='',
                    subject_start=True,
                    effect=self._offer134.get_effect(
                        #: dialogue_effect
                    ),
                    no_repeats=True,
                    dead_end=False))
        return mylist


class Cyberclinic_ropp_137(Plot):
    LABEL = "CYBERCLINIC_ropp_137"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000007D']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000007C']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000007B']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class City_ropp_11(Plot):
    LABEL = "CITY_ropp_11"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '0000000E']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000000D']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '0000000C')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000015'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'DUNGEONLEVEL_ropp_130',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'DUNGEONLEVEL_ropp_168',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class DungeonLevel_ropp_130(Plot):
    LABEL = "DUNGEONLEVEL_ropp_130"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000077']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        # Do the connection here.
        #scutils.SCSceneConnection(self.elements["PARENT_SCENE"], self.elements["LOCALE"], room1=ghterrain.IndustrialBuilding(tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM], door_sign=None, anchor=None), door1=ghwaypoints.LockedReinforcedDoor(name='Warehouse 4', anchor=pbge.randmaps.anchors.middle), room2=pbge.randmaps.rooms.FuzzyRoom(width=3, height=3, anchor=pbge.randmaps.anchors.south), door2=ghwaypoints.Exit(name='Exit', anchor=pbge.randmaps.anchors.south))
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class DungeonLevel_ropp_168(Plot):
    LABEL = "DUNGEONLEVEL_ropp_168"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000009B']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        # Do the connection here.
        #scutils.SCSceneConnection(self.elements["PARENT_SCENE"], self.elements["LOCALE"], room1=ghterrain.IndustrialBuilding(tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM], door_sign=None, anchor=None), door1=ghwaypoints.ReinforcedDoor(name='Warehouse 13', anchor=pbge.randmaps.anchors.middle), room2=pbge.randmaps.rooms.ClosedRoom(width=3, height=3, anchor=pbge.randmaps.anchors.south), door2=ghwaypoints.Exit(name='Exit', anchor=pbge.randmaps.anchors.south))
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class City_ropp_12(Plot):
    LABEL = "CITY_ropp_12"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000010']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000000F']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '0000000E')),
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '00000013')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000008'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        for t in range(5):
            self.add_sub_plot(nart,
                              'ADD_BORING_NPC',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        self.add_sub_plot(nart,
                          'LOCAL_PROBLEM',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="PROBLEM95")
        self.add_sub_plot(nart,
                          'TAVERN_ropp_96',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'HOSPITAL_ropp_169',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'GENERALSTORE_ropp_170',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_116',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    def PROBLEM95_WIN(self, camp):
        camp.campdata[LOCAL_PROBLEMS_SOLVED] += 1


class Tavern_ropp_96(Plot):
    LABEL = "TAVERN_ropp_96"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000059']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000058']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000057']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_135',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist

    #: plot_methods


class NonPlayerCharacter_ropp_135(Plot):
    LABEL = "NPC_ropp_135"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000007A']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'RLM_Relationship',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class Room_ropp_116(Plot):
    LABEL = "ROOM_ropp_116"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000068']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class Hospital_ropp_169(Plot):
    LABEL = "HOSPITAL_ropp_169"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000009E']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000009D']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000009C']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class GeneralStore_ropp_170(Plot):
    LABEL = "GENERALSTORE_ropp_170"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['000000A1']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['000000A0']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000009F']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class City_ropp_13(Plot):
    LABEL = "CITY_ropp_13"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000013']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000012']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000011']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(end_entrance=nart.camp.campdata[THE_WORLD].get(
                    '00000006')),
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('00000015'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'GARAGE_ropp_142',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'EMPTYBUILDING_ropp_180',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        self.add_sub_plot(nart, 'ROPP_DOCKYARDS_PLOT')
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class Garage_ropp_142(Plot):
    LABEL = "GARAGE_ropp_142"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000085']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000084']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000083']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_143',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'NPC_ropp_147',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist

    #: plot_methods


class Room_ropp_143(Plot):
    LABEL = "ROOM_ropp_143"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000086']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          'NPC_ropp_144',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'WAYPOINT_ropp_145',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        return True

    #: plot_methods


class NonPlayerCharacter_ropp_144(Plot):
    LABEL = "NPC_ropp_144"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000087']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class Waypoint_ropp_145(Plot):
    LABEL = "WAYPOINT_ropp_145"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['WAYPOINT'] = nart.camp.campdata[THE_WORLD]['00000088']
        element_alias_list = []

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class NonPlayerCharacter_ropp_147(Plot):
    LABEL = "NPC_ropp_147"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['00000089']
        element_alias_list = []

        self.elements["NPC_SCENE"] = self.elements["LOCALE"]
        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    #: plot_methods
    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


class EmptyBuilding_ropp_180(Plot):
    LABEL = "EMPTYBUILDING_ropp_180"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['000000A8']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['000000A7']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True


    #: plot_methods
class City_ropp_14(Plot):
    LABEL = "CITY_ropp_14"
    active = True
    scope = "METRO"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['MISSION_GATE'] = nart.camp.campdata[THE_WORLD][
            '00000015']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000014']
        element_alias_list = [('METROSCENE', 'LOCALE'), ('CITY', 'LOCALE'),
                              ('PARENT_SCENE', 'LOCALE'),
                              ('ENTRANCE', 'MISSION_GATE')]

        self.elements["METRO"] = self.elements["LOCALE"].metrodat
        if 'WORLDMAP_6':
            edge_params = [
                dict(
                    end_entrance=nart.camp.campdata[THE_WORLD].get('0000000A'))
            ]
            for e in edge_params:
                nart.camp.campdata['WORLDMAP_6'].connect_entrance_to_entrance(
                    self.elements["MISSION_GATE"], **e)

        self.add_sub_plot(nart,
                          'TAVERN_ropp_44',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'BLACKMARKET_ropp_101',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        #: plot_actions

        self.add_sub_plot(nart,
                          'ROOM_ropp_97',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'ROOM_ropp_99',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_RECOVERY_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        self.add_sub_plot(nart,
                          'CF_METROSCENE_WME_DEFENSE_HANDLER',
                          elements=dict([(a, self.elements[b])
                                         for a, b in element_alias_list]),
                          ident="")
        if True:
            self.add_sub_plot(nart,
                              'CF_METROSCENE_RANDOM_PLOT_HANDLER',
                              elements=dict([(a, self.elements[b])
                                             for a, b in element_alias_list]),
                              ident="")
        return True

    #: plot_methods


class Tavern_ropp_44(Plot):
    LABEL = "TAVERN_ropp_44"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000003A']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['00000039']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['00000038']
        element_alias_list = [('PARENT_SCENE', 'LOCALE')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist


    #: plot_methods
class Room_ropp_97(Plot):
    LABEL = "ROOM_ropp_97"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000005A']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          "MONSTER_ENCOUNTER",
                          elements=dict(TYPE_TAGS=['GUARD', 'CITY', 'ROBOT']))
        return True


    #: plot_methods
class Room_ropp_99(Plot):
    LABEL = "ROOM_ropp_99"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000005B']
        element_alias_list = []

        #: plot_init
        #: plot_actions

        self.add_sub_plot(nart,
                          "MONSTER_ENCOUNTER",
                          elements=dict(TYPE_TAGS=['GUARD', 'CITY', 'ROBOT']))
        return True


    #: plot_methods
class BlackMarket_ropp_101(Plot):
    LABEL = "BLACKMARKET_ropp_101"
    active = True
    scope = "LOCALE"

    #: plot_properties
    def custom_init(self, nart):
        self.elements['NPC'] = nart.camp.campdata[THE_WORLD]['0000005E']
        self.elements['ROOM'] = nart.camp.campdata[THE_WORLD]['0000005D']
        self.elements['LOCALE'] = nart.camp.campdata[THE_WORLD]['0000005C']
        element_alias_list = [('PARENT_SCENE', 'LOCALE'), ('NPC', 'NPC')]

        #: plot_init
        #: plot_actions
        #: plot_subplots
        return True

    def NPC_offers(self, camp):
        mylist = list()
        #: npc_offers
        return mylist

    #: plot_methods
