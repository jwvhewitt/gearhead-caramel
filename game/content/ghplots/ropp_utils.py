# Utility plots for Raid on Pirate's Point, since I am still working on the scenario editor.

import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, worldmapwar
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


class ROPP_WarStarter(Plot):
    LABEL = "ROPP_WAR_STARTER"
    scope = True
    active = True

    def custom_init(self, nart):
        self.elements[worldmapwar.WORLD_MAP_IDENTIFIER] = "WORLDMAP_6"
        world_map = nart.camp.campdata["WORLDMAP_6"]
        for node in world_map.nodes:
            node.visible = True

        war_teams = dict()
        war_teams[gears.factions.TheSolarNavy] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'],
            color=1, unpopular=True
        )

        war_teams[gears.factions.TreasureHunters] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'],
            color=2, unpopular=False
        )

        war_teams[gears.factions.AegisOverlord] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000005'],
            color=3, unpopular=True, loyalty=50
        )

        nart.camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.AegisOverlord)
        nart.camp.set_faction_enemies(gears.factions.TreasureHunters, gears.factions.TheSolarNavy)
        nart.camp.set_faction_enemies(gears.factions.AegisOverlord, gears.factions.TheSolarNavy)

        self.elements[worldmapwar.WORLD_MAP_TEAMS] = war_teams
        sp = self.add_sub_plot(nart, "WORLD_MAP_WAR", ident="ROPPWAR")
        self.world_map_war = sp.world_map_war

        self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
        self.register_element("_ROOM", pbge.randmaps.rooms.FuzzyRoom(5,5), dident="LOCALE")
        self.register_element("COMPY", ghwaypoints.OldTerminal(
            plot_locked=True, anchor=pbge.randmaps.anchors.middle, name="War Simulator",
            desc="This is a computer terminal to test the world map war system. Yay!"
        ), dident="_ROOM")

        return True

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.add_item("Start the next round", self.start_war_round)

    def start_war_round(self, camp):
        myround = worldmapwar.WorldMapWarRound(self.world_map_war, camp)
        while myround.keep_going():
            result = myround.perform_turn()
