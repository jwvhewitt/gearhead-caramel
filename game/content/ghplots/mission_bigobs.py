# bigobs are Big Objectives.
# These are not normally combined with other objectives, but form a complete mission in themselves.

from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility, megaprops
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
BAMO_DEFEND_FORTRESS = "BAMO_DEFEND_FORTRESS"
BAMO_ESCORT_SHIP = "BAMO_ESCORT_SHIP"

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
            myunit = gears.selector.RandomMechaUnit(self.rank, 50, myfac, myscene.environment, add_commander=False)
            team2.deploy_in_room(myscene, myroom, myunit.mecha_list)

        if random.randint(1, 3) != 3:
            for t in range(random.randint(1, 2)):
                roomtype = self.elements["ARCHITECTURE"].get_a_room()
                self.register_element("DUD_ROOM_{}".format(t), roomtype(5, 5), dident="LOCALE")

        myunit = gears.selector.RandomMechaUnit(self.rank, 75, myfac, myscene.environment, add_commander=True)
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
            myunit = gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("ENEMY_FACTION"),
                                                    camp.scene.environment, add_commander=False)
            team2 = self.elements["_eteam"]
            camp.scene.deploy_team(myunit.mecha_list, team2, random.choice(self.reinforcement_rooms).area)
            # team2.deploy_in_room(camp.scene, random.choice(self.reinforcement_rooms), myunit.mecha_list)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
            self.obj2.win(camp, sum([100 - pc.get_percent_damage_over_health() for pc in camp.get_active_party()]
                                    ) // self.party_size)


class BAM_TimedDefense(Plot):
    LABEL = BAMO_DEFEND_FORTRESS
    active = True
    scope = "LOCALE"

    first_room = None

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        allyfac = self.elements.get("ALLIED_FACTION")
        myfac = self.elements.get("ENEMY_FACTION")
        entry_room: pbge.randmaps.rooms.Room = self.elements.get("ENTRANCE_ROOM")
        entry_anchor = entry_room.anchor

        self.reinforcement_rooms = list()
        for t, anc in enumerate(pbge.randmaps.anchors.EDGES):
            if anc is not entry_anchor:
                roomtype = self.elements["ARCHITECTURBAME_ME"].get_a_room()
                myroom = self.register_element("CORNER_ROOM_{}".format(t), roomtype(10, 10, anchor=anc), dident="LOCALE")
                self.reinforcement_rooms.append(myroom)
                if anc is pbge.randmaps.anchors.OPPOSITE_EDGE[entry_anchor]:
                    self.first_room = myroom

        if not self.first_room:
            self.first_room = random.choice(self.reinforcement_rooms)

        team2: teams.Team = self.register_element("_eteam", teams.Team(faction=myfac, enemies=(myscene.player_team,)))

        myroom = self.register_element("CENTER_ROOM",
                                       ghrooms.IndicatedRoom(16, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")

        myroom2 = self.register_element("URBAN_ROOM",
                                       ghrooms.MechaScaleResidentialArea(12, 12, anchor=pbge.randmaps.anchors.middle),
                                       dident="CENTER_ROOM")

        bunker_team = self.register_element("_bunkerteam", teams.Team(faction=allyfac, enemies=(team2,), allies=(myscene.player_team,)), dident="URBAN_ROOM")
        myfort = self.register_element("_bunker", gears.selector.generate_fortification(self.rank, myfac, myscene.environment))
        bunker_team.contents.append(myfort)

        self.round_counter = 0
        self.round_target = max(5, self.rank//10 + 2)

        self.obj0 = adventureseed.MissionObjective("Proceed to indicated area", 1)
        self.adv.objectives.append(self.obj0)
        self.obj = adventureseed.MissionObjective("Defend buildings for {} rounds".format(self.round_target), MAIN_OBJECTIVE_VALUE * 3)
        self.adv.objectives.append(self.obj)

        self.init_ready = True
        self.combat_started = False

        return True

    def t_START(self, camp: gears.GearHeadCampaign):
        if self.init_ready:
            myroom = self.elements["CENTER_ROOM"]
            for x in range(myroom.area.x, myroom.area.x + myroom.area.width):
                for y in range(myroom.area.y, myroom.area.y + myroom.area.height):
                    camp.scene.set_visible(x, y, True)

            self.init_ready = False

    def t_PCMOVE(self, camp: gears.GearHeadCampaign):
        if not self.combat_started:
            in_dest_zone = list()
            outta_dest_zone = list()
            dest_zone: pygame.Rect = self.elements["CENTER_ROOM"].area
            for pc in camp.get_active_party():
                if dest_zone.collidepoint(*pc.pos):
                    in_dest_zone.append(pc)
                else:
                    outta_dest_zone.append(pc)
            # Remove mobility kills from the list of mecha that haven't made it to the end zone. They aren't making it.
            # Because this check is expensive, only do it if at least some mecha are in the end zone.
            if in_dest_zone:
                for pc in list(outta_dest_zone):
                    if pc.get_current_speed() < 10:
                        pc.gear_up(camp.scene)
                        if pc.get_current_speed() < 10:
                            outta_dest_zone.remove(pc)

            if in_dest_zone and not outta_dest_zone:
                self.obj0.win(camp, 100)
                self.combat_started = True
                self._add_reinforcements(camp)

    def _add_reinforcements(self, camp: gears.GearHeadCampaign):
        myunit = gears.selector.RandomMechaUnit(self.rank, 75, self.elements.get("ENEMY_FACTION"),
                                                camp.scene.environment, add_commander=False)
        team2 = self.elements["_eteam"]
        #print(myunit.mecha_list)
        mek1 = myunit.mecha_list[0]
        camp.scene.deploy_team(myunit.mecha_list, team2, random.choice(self.reinforcement_rooms).area)
        game.combat.enter_combat(camp, mek1)
        game.combat.enter_combat(camp, self.elements["_bunker"])

    def t_COMBATROUND(self, camp):
        if self.combat_started:
            myteam = self.elements["_bunkerteam"]
            if len(myteam.get_members_in_play(camp)) < 1:
                pbge.alert("Buildings Destroyed".format(self.round_counter), font=pbge.HUGEFONT, justify=0)
                self.obj.failed = True
                camp.check_trigger("FORCE_EXIT")

            else:
                self.round_counter += 1
                pbge.alert("Survived Round {}".format(self.round_counter), font=pbge.HUGEFONT, justify=0)
                if self.round_counter >= self.round_target:
                    # Victory!
                    self.obj.win(camp, 100)
                    camp.check_trigger("FORCE_EXIT")
                else:
                    self._add_reinforcements(camp)

    def t_ENDCOMBAT(self, camp):
        if self.combat_started:
            myteam = self.elements["_eteam"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.round_counter += 1
                self._add_reinforcements(camp)


class BAM_EscortShip(Plot):
    LABEL = BAMO_ESCORT_SHIP
    LABEL = BAMO_TEST_MISSION
    active = True
    scope = "LOCALE"

    DIRECTION_BY_ANCHOR = {
        pbge.randmaps.anchors.north: megaprops.SOUTHWARD, pbge.randmaps.anchors.northeast: megaprops.SOUTHWARD,
        pbge.randmaps.anchors.east: megaprops.WESTWARD, pbge.randmaps.anchors.southeast: megaprops.WESTWARD,
        pbge.randmaps.anchors.south: megaprops.NORTHWARD, pbge.randmaps.anchors.southwest: megaprops.NORTHWARD,
        pbge.randmaps.anchors.west: megaprops.EASTWARD, pbge.randmaps.anchors.northwest: megaprops.EASTWARD,
        pbge.randmaps.anchors.middle: megaprops.NORTHWARD, None: megaprops.SOUTHWARD
    }

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        allyfac = self.elements.get("ALLIED_FACTION")
        myfac = self.elements.get("ENEMY_FACTION")
        if "ESCORT_PATH" in self.elements and self.elements["ESCORT_PATH"]:
            std_dident = "ESCORT_PATH"
        else:
            std_dident = "LOCALE"

        if not ("ESCORT_ROOM" in self.elements and self.elements["ESCORT_ROOM"]):
            self.register_element(
                "ESCORT_ROOM", ghrooms.OpenRoom(12, 12), dident=std_dident
            )
        entry_anchor = self.elements["ENTRANCE_ANCHOR"]

        my_facing = self.register_element("_facing", self.DIRECTION_BY_ANCHOR.get(entry_anchor, megaprops.EASTWARD))

        myship = self.register_element("SHIP", megaprops.CivilianWaterShip(rank=self.rank), dident="ESCORT_ROOM")

        troom = self.register_element(
            "TARGET_ROOM", ghrooms.IndicatedRoom(
                12, 12, anchor=pbge.randmaps.anchors.OPPOSITE_EDGE[entry_anchor]
            ), dident=std_dident
        )

        reinforcement_rooms = list()
        for n, anc in enumerate(pbge.randmaps.anchors.EDGES):
            if anc is not entry_anchor and anc is not pbge.randmaps.anchors.OPPOSITE_EDGE[entry_anchor]:
                roomtype = self.elements["ARCHITECTURE"].get_a_room()
                rroom = self.register_element("_rroom_{}".format(n), roomtype(10, 10), dident="LOCALE")
                reinforcement_rooms.append(rroom)
        self.elements[CTE_REINFORCEMENT_ROOMS] = reinforcement_rooms

        team2: teams.Team = self.register_element(
            CTE_ENEMY_TEAM, teams.Team(faction=myfac, enemies=(myscene.player_team, myship))
        )
        self.register_element(CTE_INITIAL_ROOM, ghrooms.OpenRoom(10,10, anchor=pbge.randmaps.anchors.middle),
                              dident=std_dident)
        self.add_sub_plot(nart, CTHREAT_MECHA, ident="THREAT")
        self.did_init = False

        self.obj = adventureseed.MissionObjective("Escort ship to safe zone", MAIN_OBJECTIVE_VALUE * 3)
        self.adv.objectives.append(self.obj)
        self.obj2 = adventureseed.MissionObjective("Protect ship from enemies", MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj2)

        self.initial_health = 0

        return True

    def t_START(self, camp: gears.GearHeadCampaign):
        if not self.did_init:
            self.subplots["THREAT"].activate(camp)
            myprop = self.elements["SHIP"]
            for p in myprop.get_members_in_play(camp):
                self.initial_health += p.current_health
            my_enemies = self.elements[CTE_ENEMY_TEAM].get_members_in_play(camp)
            if my_enemies:
                game.combat.enter_combat(camp, my_enemies[0])
            self.did_init = True


    def t_COMBATROUND(self, camp: gears.GearHeadCampaign):
        myprop = self.elements["SHIP"]
        if not myprop.get_members_in_play(camp):
            pbge.alert("Ship Destroyed", font=pbge.HUGEFONT, justify=0)
            self.obj.failed = True
            camp.check_trigger("FORCE_EXIT")
        else:
            facing = self.elements["_facing"]
            for t in range(5):
                myprop.move(camp, *facing)
                if self._ship_has_escaped(camp, myprop, facing):
                    pbge.alert("Ship has escaped!")
                    self.obj.win(camp)
                    self.obj2.win(camp, sum([p.current_health for p in myprop.get_members_in_play(camp)]) * 100 // self.initial_health)
                    camp.check_trigger("FORCE_EXIT")
                    break

    def _ship_has_escaped(self, camp: gears.GearHeadCampaign, ship: megaprops.MegaProp, facing):
        troom = self.elements["TARGET_ROOM"]
        all_out = True
        for ship_part in ship.get_members_including_destroyed(camp):
            if facing == megaprops.NORTHWARD:
                if ship_part.pos[1] >= troom.area.bottom:
                    all_out = False
                    break
            elif facing == megaprops.SOUTHWARD:
                if ship_part.pos[1] < troom.area.top:
                    all_out = False
                    break
            elif facing == megaprops.WESTWARD:
                if ship_part.pos[0] >= troom.area.right:
                    all_out = False
                    break
            else:
                if ship_part.pos[0] < troom.area.left:
                    all_out = False
                    break
        return all_out


# *******************************
# ***   CONTINUOUS  THREATS   ***
# *******************************
#
# Sometimes for a mission you don't want just one enemy, you want an endless supply of them!
# Needed Elements:
#   ENEMY_TEAM: The team to which to add the reinforcements; if no team is provided then a new team will be created
#       each time reinforcements are called.
#   REINFORCEMENT_ROOMS: A list of rooms in which to place reinforcements.

CTHREAT_MECHA = "CTHREAT_MECHA"
CTHREAT_MONSTERS = "CTHREAT_MONSTERS"
CTE_MONSTER_TAGS = "CTE_MONSTER_TAGS"

CTE_ENEMY_TEAM = "ENEMY_TEAM"
CTE_INITIAL_ROOM = "INITIAL_ENEMY_ROOM"             # May be None, in which case starts without enemies.
CTE_REINFORCEMENT_ROOMS = "REINFORCEMENT_ROOMS"
CTE_REINFOCEMENT_DELAY = "REINFORCEMENT_DELAY"      # Defaults to a 1 round delay between reinforcements

class CTMecha(Plot):
    LABEL = CTHREAT_MECHA
    active = False
    scope = "LOCALE"

    def custom_init(self, nart):
        if CTE_REINFORCEMENT_ROOMS not in self.elements or not self.elements[CTE_REINFORCEMENT_ROOMS]:
            roomtype = self.elements["ARCHITECTURE"].get_a_room()
            myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
            self.elements[CTE_REINFORCEMENT_ROOMS] = [myroom,]

        if CTE_INITIAL_ROOM in self.elements and self.elements[CTE_INITIAL_ROOM]:
            myteam = self.elements.get(CTE_ENEMY_TEAM, teams.Team(enemies=(self.elements["LOCALE"].player_team,),
                                                                  faction=self.elements.get("ENEMY_FACTION")))
            myunit = gears.selector.RandomMechaUnit(
                self.rank, 100, self.elements.get("ENEMY_FACTION"), self.elements["LOCALE"].environment,
                add_commander=True
            )
            myteam.deploy_in_room(self.elements["LOCALE"], self.elements[CTE_INITIAL_ROOM], myunit.mecha_list)

        self.reinforcements_counter = 1

        return True

    def t_START(self, camp: gears.GearHeadCampaign):
        game.combat.start_continuous_combat(camp)

    def activate(self, camp):
        game.combat.start_continuous_combat(camp)
        super().activate(camp)

    def deactivate(self, camp):
        if camp.fight:
            camp.fight.keep_going_without_enemies = False
        super().deactivate(camp)

    def add_reinforcements(self, camp):
        myscene = self.elements["LOCALE"]
        myrooms = self.elements[CTE_REINFORCEMENT_ROOMS]
        myunit = gears.selector.RandomMechaUnit(self.rank, 70, self.elements.get("ENEMY_FACTION"),
                                                camp.scene.environment, add_commander=False)
        mek1 = myunit.mecha_list[0]
        team2 = self.elements.get("ENEMY_TEAM", teams.Team(enemies=(myscene.player_team,)))
        camp.scene.deploy_team(myunit.mecha_list, team2, random.choice(myrooms).area)
        game.combat.enter_combat(camp, mek1)

    def t_COMBATROUND(self, camp):
        if self.reinforcements_counter > 0:
            self.reinforcements_counter -= 1
        else:
            self.add_reinforcements(camp)
            self.reinforcements_counter = self.elements.get(CTE_REINFOCEMENT_DELAY, 1)
