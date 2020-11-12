import random

import game.content
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints
from game import teams
from game.content.ghplots import missionbuilder
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, PlotState
from . import dd_customobjectives
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery
from .dd_roadedge import DZDREBasicPlotWithEncounterStuff, DeadZoneHighwaySceneGen


#   *********************************
#   ***   DZD_ROADEDGE_KERBEROS   ***
#   *********************************
#

class KerberosEncounterPlot(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_KERBEROS"

    active = True
    scope = True
    UNIQUE = True
    BASE_RANK = 10
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.add_sub_plot(nart, "DZRE_KERBEROS_ATTACKS", ident="MISSION", spstate=PlotState(
            elements={"METRO": myedge.start_node.destination.metrodat, "METROSCENE": myedge.start_node.destination,
                      "MISSION_GATE": myedge.start_node.entrance}).based_on(self))
        return True

    def get_enemy_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, "Kerberos Attacks", (start_node.destination, start_node.entrance),
            enemy_faction=None, rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_KERBEROS,),
            adv_type="DZD_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": (dest_node.destination, dest_node.entrance), "ENTRANCE_ANCHOR": myanchor,
                             missionbuilder.BAME_MONSTER_TAGS: ("ZOMBOT",)},
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            cash_reward=0,
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg"
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and camp.has_mecha_party():
            if random.randint(1, 100) <= self.ENCOUNTER_CHANCE and not self.road_cleared:
                return self.get_enemy_encounter(camp, dest_node)
            elif random.randint(1, 100) <= 15:
                return self.get_random_encounter(camp, dest_node)

    def MISSION_WIN(self, camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["the road to {} is known as the mecha graveyard".format(
                self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram


class KerberosAttacks(Plot):
    LABEL = "DZRE_KERBEROS_ATTACKS"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        self.kerberos_active = True

        # Add the Kerberos interior dungeon
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Kerberos Facility", gharchitecture.OrganicBuilding(),
            self.rank,
            monster_tags=("MUTANT", "VERMIN", "SYNTH", "CREEPY"),
            explo_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            connector=plotutility.StairsDownToStairsUpConnector,
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS,),
            decor=gharchitecture.OrganicStructureDecor()
        )
        self.register_element("DUNGEON_ENTRANCE", mydungeon.entry_level)
        d_entrance_room = self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_entrance_room)

        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.StairsUp(
                anchor=pbge.randmaps.anchors.middle,
                dest_scene=self.elements["METROSCENE"],
                dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Add the kidnap room and kidnap room waypoint.
        d_kidnap_room = self.register_element("KIDNAP_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_kidnap_room)
        self.register_element("KIDNAP_ROOM_WP", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="KIDNAP_ROOM")
        self.register_element("KIDNAP_TEAM", game.teams.Team(), dident="KIDNAP_ROOM")
        self.kidnapped_pilots = list()

        nart.camp.campdata["KERBEROS_GRAB_FUN"] = self._get_grabbed_by_kerberos
        nart.camp.campdata["KERBEROS_DUNGEON_OPEN"] = False

        return True

    def _get_grabbed_by_kerberos(self, camp: gears.GearHeadCampaign, pc):
        camp.scene.contents.remove(pc)
        pilot = pc.get_pilot()
        if pilot is camp.pc:
            camp.destination, camp.entrance = self.elements["DUNGEON_ENTRANCE"], self.elements["KIDNAP_ROOM_WP"]
            camp.campdata["KERBEROS_DUNGEON_OPEN"] = True
        else:
            plotutility.AutoLeaver(pilot)(camp)
            self.elements["DUNGEON_ENTRANCE"].deploy_team([pilot,],self.elements["KIDNAP_TEAM"])
            self.kidnapped_pilots.append(pilot)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if camp.campdata["KERBEROS_DUNGEON_OPEN"]:
            thingmenu.add_item("Go to the Kerberos Facility.", self.go_to_locale)

    def go_to_locale(self, camp):
        camp.destination, camp.entrance = self.elements["DUNGEON_ENTRANCE"], self.elements["ENTRANCE"]

