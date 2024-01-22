# bigobs are Big Objectives.
# These are not normally combined with other objectives, but form a complete mission in themselves.

from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed, ghcutscene, ghrooms
from .missionbuilder import MAIN_OBJECTIVE_VALUE, BAMO_TEST_MISSION, CONVO_CANT_WITHDRAW
from gears import champions
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
import copy

BAMO_BREAK_THROUGH = "BAMO_BREAK_THROUGH"


class BAM_ToTheOtherSide(Plot):
    LABEL = BAMO_BREAK_THROUGH
    active = True
    scope = "LOCALE"

    DEST_ANCHORS = {
        pbge.randmaps.anchors.north: (
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.southeast, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.east, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.southeast, pbge.randmaps.anchors.west),
        ),
        pbge.randmaps.anchors.south: (
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.northwest),
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.east, pbge.randmaps.anchors.northwest),
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.west),
        ),
        pbge.randmaps.anchors.east: (
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.north, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.south),
        ),
        pbge.randmaps.anchors.west: (
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.southeast),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.north, pbge.randmaps.anchors.southeast),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.south),
        ),
        pbge.randmaps.anchors.northeast: (
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.southeast, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.southeast, pbge.randmaps.anchors.west),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.south),
        ),
        pbge.randmaps.anchors.northwest: (
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.southeast, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.south, pbge.randmaps.anchors.east, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.southeast),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.south),
        ),
        pbge.randmaps.anchors.southeast: (
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.northwest),
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.west),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.southwest),
            (pbge.randmaps.anchors.west, pbge.randmaps.anchors.north, pbge.randmaps.anchors.southwest),
        ),
        pbge.randmaps.anchors.southwest: (
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.northwest),
            (pbge.randmaps.anchors.north, pbge.randmaps.anchors.east, pbge.randmaps.anchors.northwest),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.northeast, pbge.randmaps.anchors.southeast),
            (pbge.randmaps.anchors.east, pbge.randmaps.anchors.north, pbge.randmaps.anchors.southeast),
        ),
    }

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        entry_room: pbge.randmaps.rooms.Room = self.elements.get("ENTRANCE_ROOM")
        entry_anchor = entry_room.anchor
        dest_anchors = random.choice(self.DEST_ANCHORS[entry_anchor])

        destroom = self.register_element("DESTINATION", ghrooms.IndicatedRoom(5, 5, anchor=dest_anchors[0]),
                                         dident="LOCALE")
        team2: teams.Team = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)))

        self.reinforcement_rooms = list()
        for t in range(1, 3):
            roomtype = self.elements["ARCHITECTURE"].get_a_room()
            myroom = self.register_element("CORNER_ROOM_{}".format(t), roomtype(10, 10, anchor=dest_anchors[t]),
                                           dident="LOCALE")
            self.reinforcement_rooms.append(myroom)
            myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=False)
            team2.deploy_in_room(myscene, myroom, myunit.mecha_list)

        if random.randint(1, 3) != 3:
            for t in range(random.randint(1, 2)):
                roomtype = self.elements["ARCHITECTURE"].get_a_room()
                self.register_element("DUD_ROOM_{}".format(t), roomtype(5, 5), dident="LOCALE")

        myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
        myroom = self.register_element("CENTER_ROOM",
                                       pbge.randmaps.rooms.FuzzyRoom(10, 10, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2.deploy_in_room(myscene, myroom, myunit.mecha_list)
        if myfac:
            commander = self.register_element(
                "_commander", nart.camp.cast_a_combatant(myfac, self.rank + 20, allow_allies=True, myplot=self),
                lock=True
            )
            plotutility.CharacterMover(nart.camp, self, commander, myscene, team2)
        else:
            self.register_element("_commander", myunit.commander)

        self.obj = adventureseed.MissionObjective("Guide lance to end zone", MAIN_OBJECTIVE_VALUE * 3)
        self.adv.objectives.append(self.obj)
        self.obj2 = adventureseed.MissionObjective("Avoid taking damage", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj2)

        self.intro_ready = True
        self.init_ready = True
        self.party_size = 1
        self.reinforcements_counter = 2

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[HALT] [THIS_AREA_IS_UNDER_OUR_CONTROL] [LEAVE_THIS_BATTLE]",
                            context=ContextTag([context.ATTACK, ])))
        mylist.append(Offer("I must [objective_ep]. [CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        if not self.elements.get(CONVO_CANT_WITHDRAW, False):
            mylist.append(Offer("[WITHDRAW]", effect=camp.scene.player_team.retreat,
                                context=ContextTag([context.WITHDRAW, ])))

        return mylist

    def t_START(self, camp: gears.GearHeadCampaign):
        if self.init_ready:
            myroom = self.elements["DESTINATION"]
            for x in range(myroom.area.x, myroom.area.x + myroom.area.width):
                for y in range(myroom.area.y, myroom.area.y + myroom.area.height):
                    camp.scene.set_visible(x, y, True)

            self.party_size = len(camp.get_active_party())
            self.init_ready = False

    def t_PCMOVE(self, camp: gears.GearHeadCampaign):
        in_end_zone = list()
        outta_end_zone = list()
        end_zone: pygame.Rect = self.elements["DESTINATION"].area
        for pc in camp.get_active_party():
            if end_zone.collidepoint(*pc.pos):
                in_end_zone.append(pc)
            else:
                outta_end_zone.append(pc)
        # Remove mobility kills from the list of mecha that haven't made it to the end zone. They aren't making it.
        # Because this check is expensive, only do it if at least some mecha are in the end zone.
        if in_end_zone:
            for pc in list(outta_end_zone):
                if pc.get_current_speed() < 10:
                    pc.gear_up(camp.scene)
                    if pc.get_current_speed() < 10:
                        outta_end_zone.remove(pc)

        if in_end_zone and not outta_end_zone:
            self.obj.win(camp, len(in_end_zone) * 100 / self.party_size)
            self.obj2.win(camp, sum([100 - pc.get_percent_damage_over_health() for pc in in_end_zone]
                                    ) // self.party_size)
            camp.check_trigger("FORCE_EXIT")

    def t_COMBATROUND(self, camp):
        if self.reinforcements_counter > 0:
            self.reinforcements_counter -= 1
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 50, self.elements.get("ENEMY_FACTION"),
                                                    camp.scene.environment, add_commander=False)
            team2 = self.elements["_eteam"]
            team2.deploy_in_room(camp.scene, random.choice(self.reinforcement_rooms), myunit.mecha_list)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
            self.obj2.win(camp, sum([100 - pc.get_percent_damage_over_health() for pc in camp.get_active_party()]
                                    ) // self.party_size)
