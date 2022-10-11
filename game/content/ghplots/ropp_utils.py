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
        self.world_map_war = self.register_element("WORLD_MAP_WAR", sp.world_map_war)

        if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
            self.register_element("_ROOM", pbge.randmaps.rooms.FuzzyRoom(5,5), dident="LOCALE")
            self.register_element("COMPY", ghwaypoints.OldTerminal(
                plot_locked=True, anchor=pbge.randmaps.anchors.middle, name="War Simulator",
                desc="This is a computer terminal to test the world map war system. Yay!"
            ), dident="_ROOM")

        # Locate the major NPCs.
        self.seek_element(nart, "NPC_CHARLA", self._seek_charla, lock=True)
        self.seek_element(nart, "NPC_BRITAINE", self._seek_britaine, lock=True)
        self.seek_element(nart, "NPC_PINSENT", self._seek_pinsent, lock=True)
        self.seek_element(nart, "NPC_BOGO", self._seek_bogo, lock=True)
        self.seek_element(nart, "NPC_AEGIS", self._seek_aegis, lock=True)

        self.add_sub_plot(nart, "ROPP_SOLAR_NAVY_JOINER")

        return True

    def _seek_charla(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Admiral Charla"

    def _seek_britaine(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Britaine"

    def _seek_pinsent(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "General Pinsent"

    def _seek_bogo(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Jjang Bogo"

    def _seek_aegis(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.job.name == "Diplomat" and
                candidate.faction is gears.factions.AegisOverlord)

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.add_item("Start the next round", self.start_war_round)

    def start_war_round(self, camp):
        myround = worldmapwar.WorldMapWarRound(self.world_map_war, camp)
        while myround.keep_going():
            result = myround.perform_turn()


class SolarNavyJoinerPlot(Plot):
    LABEL = "ROPP_SOLAR_NAVY_JOINER"
    scope = True
    active = True

    RUMOR = Rumor(
        "Admiral Charla is recruiting cavaliers for the Pirate Point operation",
        offer_msg="The Solar Navy's goal is to remove the Aegis Consulate from Pirate's Point. Should be a lot of good missions in it for you. If you want the job, you can speak to her at the Field HQ.",
        offer_subject="Admiral Charla is recruiting cavaliers",
        offer_subject_data="the Pirate Point operation",
        memo="Admiral Charla is recruiting cavaliers for the Pirate Point operation. You should speak to her if you want to aid the Solar Navy.",
        prohibited_npcs=("NPC_CHARLA",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000018']

        self.signing_bonus = gears.selector.calc_mission_reward(self.rank+10, 500)
        self.got_starter_kit = False
        return True

    def NPC_CHARLA_offers(self, camp):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team:
            mylist.append(Offer(
                "[THATS_GOOD] Here is a signing bonus of ${:,}; you can use it to get some equipment from the supply depot. General Pinsent can fill you in on how the ground operations are proceeding.".format(self.signing_bonus),
                ContextTag([context.CUSTOM]), effect=self._join_team,
                data={"reply": "I want to help the Solar Navy."}
            ))

        return mylist

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].player_team = gears.factions.TheSolarNavy
        camp.credits += self.signing_bonus
        pbge.BasicNotification("You receive ${:,}.".format(self.signing_bonus))

