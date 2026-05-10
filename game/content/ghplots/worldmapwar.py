import random

import game.content
from game import content
import gears
import pbge
from game.content import gharchitecture
from pbge.plots import Plot, PlotState
from . import missionbuilder, campfeatures, wmw_occupation
import collections
from collections.abc import Callable


# Elements passed to the world map handler plot.
WORLD_MAP_IDENTIFIER = "WORLD_MAP_IDENTIFIER"
WORLD_MAP_TEAMS = "WORLD_MAP_TEAMS"
WORLD_MAP_LEGEND = "WORLD_MAP_LEGEND"
WORLD_MAP_WAR = "WORLD_MAP_WAR"


type WarCallback = Callable[[pbge.campaign.Campaign, missionbuilder.BuildAMissionSeed|None], None]


class WarStats:
    def __init__(self, home_base=None, aggression=75, loyalty=95, color=0, unpopular=False, occtype=wmw_occupation.WMWO_DEFENDER):
        # home_base is the city where this team's HQ is located. Capture it, and that team is eliminated.
        # aggression is how likely they are to attack instead of turtle
        # loyalty is the % chance this faction will honor a peace treaty. Lower loyalty = more backstabbing.
        # unpopular marks a faction that you can organize insurrection against.
        self.home_base = home_base
        self.aggression = aggression
        self.loyalty = loyalty
        self.color = color
        self.unpopular = unpopular
        self.boosted = False
        self.occtype = occtype

    def __setstate__(self, state):
        # For v0.946 and earlier: get rid of obsolete properties.
        if "strength" in state:
            del state["strength"]
        if "resources" in state:
            del state["resources"]
        if "boosted" not in state:
            state["boosted"] = False
        if "occtype" not in state:
            state["occtype"] = wmw_occupation.WMWO_DEFENDER
        self.__dict__.update(state)


class NodeStats:
    def __init__(self, fortified=False):
        self.fortified = fortified


class WarWorldMapLegend:
    def __init__(self, image_name="wm_legend_war.png", num_icons=7, num_colors=8, hq_frames=(0, 3), city_frames=(1, 4),
                 fortress_frames=(2, 5), mecha_frame=6):
        self.image_name = image_name
        self.num_icons = num_icons
        self.num_colors = num_colors
        self.hq_frames = hq_frames
        self.city_frames = city_frames
        self.fortress_frames = fortress_frames
        self.mecha_frame = mecha_frame
        self.standard_frames = city_frames + fortress_frames + hq_frames

    def auto_apply(self, world_map: campfeatures.WorldMap, world_map_war):
        for node in world_map.nodes:
            node.image_file = self.image_name
            if node.destination.faction and node.destination.faction in world_map_war.war_teams:
                mycolor = world_map_war.war_teams[node.destination.faction].color
                myfac = node.destination.faction
            else:
                mycolor = 0
                myfac = None
            if myfac and node.destination is world_map_war.war_teams[node.destination.faction].home_base:
                node.on_frame, node.off_frame = self.hq_frames
            elif world_map_war.node_stats[node].fortified:
                node.on_frame, node.off_frame = self.fortress_frames
            else:
                node.on_frame, node.off_frame = self.city_frames
            node.on_frame += self.num_icons * mycolor
            node.off_frame += self.num_icons * mycolor

    def set_color(self, node: campfeatures.WorldMapNode, new_color):
        node.on_frame = node.on_frame % self.num_icons + self.num_icons * new_color
        node.off_frame = node.off_frame % self.num_icons + self.num_icons * new_color

    def get_mecha_frame(self, color):
        return self.mecha_frame + color * self.num_icons


class AttackerWinsEffect:
    def __init__(self, attack_team, target_node, world_map_war, attacker_is_pc):
        # attack_ante and target_ante are the number of troops committed by both sides.
        self.attack_team = attack_team
        self.target_node = target_node
        self.world_map_war = world_map_war
        self.attacker_is_pc = attacker_is_pc

    def __call__(self, camp: gears.GearHeadCampaign):
        self.world_map_war.capture(camp, self.attack_team, self.target_node)
        if self.attacker_is_pc:
            camp.go(self.target_node.entrance)


class DefenderWinsEffect:
    def __init__(self, attack_team, target_node, world_map_war, attacker_is_pc):
        # attack_ante and target_ante are the number of troops committed by both sides.
        self.attack_team = attack_team
        self.target_node = target_node
        self.world_map_war = world_map_war
        self.attacker_is_pc = attacker_is_pc

    def __call__(self, camp):
        pass


class WorldMapWar:
    def __init__(self, rank, world_map: campfeatures.WorldMap, war_teams: dict, legend=None):
        # war_teams is a dictionary of Faction:WarStats items.
        self.rank = rank
        self.world_map = world_map
        self.war_teams = dict()
        if war_teams:
            self.war_teams.update(war_teams)
        self.node_stats = collections.defaultdict(NodeStats)
        self.player_can_act = True
        self.consolidation_scene = None

        # All home bases start out fortified.
        for wt in self.war_teams.values():
            hqnode = world_map.get_node_with_destination(wt.home_base)
            if hqnode:
                self.node_stats[hqnode].fortified = True

        self.player_team = None

        if not legend:
            legend = WarWorldMapLegend()
            legend.auto_apply(world_map, self)
        self.legend = legend
        self.ready_for_next_round = False
        self.just_captured = None

    def get_number_of_territories(self, fac):
        n = 0
        for node in self.world_map.nodes:
            if node.destination.faction is fac:
                n += 1
        return n

    def get_total_defense(self, fac):
        n = 0
        for node in self.world_map.nodes:
            if node.destination.faction is fac:
                n += node.destination.metrodat.get_quality_of_life().defense
        return n

    def get_defense_strength(self, node):
        fac = node.destination.faction
        str = 4
        dfn = self.get_total_defense(fac)
        if dfn > 0:
            str += 1
        elif dfn < 0:
            str -= 1
        if fac in self.war_teams and self.war_teams[fac].boosted:
            str += 1
        if self.get_number_of_territories(fac) < 3:
            str -= 1
        if fac and fac in self.war_teams and node.destination is self.war_teams[fac].home_base:
            return str + 4
        elif self.node_stats[node].fortified:
            return str + 2
        else:
            return str

    def get_attack_strength(self, fac):
        str = 4
        dfn = self.get_total_defense(fac)
        if dfn > 0:
            str += 1
        elif dfn < 0:
            str -= 1
        if fac in self.war_teams and self.war_teams[fac].boosted:
            str += 1
        if self.get_number_of_territories(fac) < 3:
            str -= 1
        return str

    def get_node_income(self, node):
        dest = node.destination
        if hasattr(dest, "metro") and dest.metro:
            return max( + 2, 1)
        else:
            return 3

    def remove_team(self, camp, losing_fac):
        for node in self.world_map.nodes:
            if node.destination.faction is losing_fac:
                node.destination.faction = None
                node.destination.purge_faction(camp, losing_fac)
                self.legend.set_color(node, 0)
        del self.war_teams[losing_fac]

    def get_enemy_faction(self, camp:gears.GearHeadCampaign, faca):
        candidates = [fac for fac in self.war_teams.keys() if fac is not faca and camp.are_faction_enemies(faca, fac)]
        if candidates:
            return random.choice(candidates)
        else:
            return camp.get_enemy_faction(faca)

    WAR_WON = "WIN!"
    WAR_LOST = "LOSE!"

    def get_war_status(self, camp: gears.GearHeadCampaign):
        # Returns WAR_WON, WAR_LOST, or None depending on whether the player team has been eliminated or all non allied
        # teams have been eliminated.
        if not self.player_team:
            return None
        elif self.player_team not in self.war_teams:
            return self.WAR_LOST
        else:
            for fac in self.war_teams.keys():
                if not (fac is self.player_team or camp.are_faction_allies(fac, self.player_team)):
                    return None
            return self.WAR_WON

    def capture(self, camp, attacking_fac, node):
        former_faction = None
        if node.destination.faction:
            former_faction = node.destination.faction
            node.destination.purge_faction(camp, node.destination.faction)
        node.destination.faction = attacking_fac

        metroscene: gears.GearHeadScene = node.destination.get_metro_scene()
        if metroscene:
            # Purge any occupation plots in this metro area.
            for myplot in metroscene.metrodat.scripts:
                if hasattr(myplot, "IS_OCCUPATION_PLOT") and myplot.IS_OCCUPATION_PLOT:
                    myplot.end_plot(camp, True)

        for fac in self.war_teams.keys():
            if self.war_teams[fac].home_base is node.destination:
                # If your home base is captured, you are eliminated from the game.
                self.remove_team(camp, fac)
                node.on_frame, node.off_frame = self.legend.city_frames
                break
        if attacking_fac in self.war_teams:
            self.legend.set_color(node, self.war_teams[attacking_fac].color)
        else:
            self.legend.set_color(node, 0)

        if attacking_fac is self.player_team and not self.get_war_status(camp):
            self.just_captured = node.destination
            if metroscene and game.content.load_dynamic_plot(
                camp, "WMW_CONSOLIDATION", PlotState(elements={
                        "METROSCENE": node.destination, "METRO": metroscene.metrodat, "MISSION_GATE": node.entrance,
                        WORLD_MAP_WAR: self, "FORMER_FACTION": former_faction
                    }
                )
            ):
                self.player_can_act = False
                self.consolidation_scene = node.destination

    ATTACK_OBJECTIVES = (
        missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_AID_ALLIED_FORCES,
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_CAPTURE_BUILDINGS,
        missionbuilder.BAMO_SURVIVE_THE_AMBUSH
    )

    def get_attack_missionseed(self, camp, attacking_team, start_node, target_node: campfeatures.WorldMapNode):
        mission_grammar = missionbuilder.MissionGrammar(
            "capture {} for {}".format(target_node, attacking_team),
            "defend {} from {}".format(target_node, attacking_team),
            "I captured {} from you.".format(target_node),
            "you defeated me in {}".format(target_node),
            "I captured {}".format(target_node),
            "you captured {} from me".format(target_node)
        )

        mybattle = content.load_dynamic_plot(
            camp, "WMW_MISSION", PlotState(
                rank=self.rank, elements={
                    "METROSCENE": start_node.destination, "MISSION_GATE": start_node.entrance,
                    "WIN_FUN": AttackerWinsEffect(attacking_team, target_node, self, True),
                    "LOSS_FUN": DefenderWinsEffect(attacking_team, target_node, self, True),
                    "TARGET_GATE": target_node.entrance, "TARGET_SCENE": target_node.destination,
                    "ENEMY_FACTION": target_node.destination.faction, "ALLIED_FACTION": attacking_team,
                    "NUM_STAGES": min(max(self.get_defense_strength(target_node)//2 + 2, 2), 5),
                    "MISSION_GRAMMAR": mission_grammar
                })
        )

        return mybattle

    def get_memo(self):
        if self.player_team:
            if self.player_can_act:
                return "You are fighting for {} in the current conflict. Attempt to capture territories for them on the world map.".format(self.player_team)
            else:
                return "You must consolidate your victory in {} before attempting to capture another territory for {}.".format(self.consolidation_scene, self.player_team)

    def __setstate__(self, state):
        # For saves from V0.946 or earlier, make sure there's a just_captured property.
        self.__dict__.update(state)
        if "just_captured" not in state:
            self.just_captured = None
        # For saves from v0.962 or earlier, make sure there's a player_can_act property.
        if "player_can_act" not in state:
            self.player_can_act = True
        if "consolidation_scene" not in state:
            self.consolidation_scene = None

    def set_player_team(self, camp: gears.GearHeadCampaign, team):
        if self.player_team and camp.are_faction_enemies(self.player_team, team):
            camp.faction_relations[self.player_team].pc_relation = gears.factions.FactionRelations.ENEMY
        if team in self.war_teams:
            self.player_team = team
            camp.faction_relations[team].pc_relation = gears.factions.FactionRelations.ALLY

    def faction_is_active(self, fac):
        return fac in self.war_teams

    def pick_a_winner(self):
        # Choose a winner, or the team most likely to win.
        my_teams = list(self.war_teams.keys())
        random.shuffle(my_teams)
        my_teams.sort(key=lambda a: (self.get_number_of_territories(a), self.get_attack_strength(a)))
        return my_teams[-1]


class WorldMapAlert(pbge.alerts.AbstractAlert):
    def __init__(self, message, visualizer, target_waypoint, on_close: pbge.widgets.On_Click, **kwargs):
        super().__init__(on_close=on_close, **kwargs)
        self.message = message
        self.visualizer = visualizer
        self.target_waypoint = target_waypoint

    def _render(self, delta):
        self.visualizer.render(waypoint=self.target_waypoint)
        myrect = campfeatures.WorldMapMenu.MENU_AREA.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(pbge.MEDIUMFONT, self.message, myrect, justify=0)


class WorldMapBattleAlert(WorldMapAlert):
    DEFENDER_POSITIONS = [(-6, -16), (6, -16), (-12, -8), (-4, -8), (4, -8), (12, -8),
                          (-12, 8), (-4, 8), (4, 8), (12, 8), (-6, 16), (6, 16)]
    ATTACKER_POSITIONS = [(-8, -20), (8, -20), (15, -15), (20, -8), (20, 8), (15, 15),
                          (8, 20), (-8, 20), (-15, 15), (-20, 8), (-20, -8), (-15, -15)]
    MECHA_WIGGLE = (-1, -1, 0, 0, 0, 1, 1, 0, 0, 0)

    def __init__(
        self, message, visualizer, target_node, on_close: pbge.widgets.On_Click,
        num_attackers, num_defenders, world_map_war, 
        attacker_casulties=0, defender_casulties=0,
        attack_frame=1, defense_frame=0, **kwargs
    ):
        # If casulties are given, the battle will be animated over however many seconds it takes.
        super().__init__(message, visualizer, target_node.entrance, on_close, **kwargs)
        self.num_attackers = num_attackers
        self.num_defenders = num_defenders
        self.target_node = target_node
        self.attacker_casulties = attacker_casulties
        self.defender_casulties = defender_casulties
        self.attack_frame = attack_frame
        self.defense_frame = defense_frame
        self.kill_counter = 0
        self.defender_positions = self.DEFENDER_POSITIONS.copy()
        random.shuffle(self.defender_positions)
        self.attacker_positions = self.ATTACKER_POSITIONS.copy()
        random.shuffle(self.attacker_positions)
        self.mecha_sprite = pbge.image.Image(world_map_war.legend.image_name, 20, 20)

        # Make sure the last casualty is the losing team.
        if attacker_casulties >= num_attackers:
            self.casulties = [-1] * (attacker_casulties-1) + [1] * defender_casulties
            random.shuffle(self.casulties)
            self.casulties.append(-1)
        else:
            self.casulties = [-1] * attacker_casulties + [1] * (defender_casulties-1)
            random.shuffle(self.casulties)
            self.casulties.append(1)
        self.small_boom_sprite = pbge.image.Image("anim_smallboom.png", 64, 64)

    def _render(self, delta):
        super()._render(delta)

        map_rect = self.visualizer.map_area.get_rect()
        for n in range(self.num_attackers):
            x, y = self.attacker_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x +
                                        self.MECHA_WIGGLE[(pbge.my_state.anim_phase + n * 3) % 10],
                                        self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                       self.attack_frame)


        for n in range(self.num_defenders):
            x, y = self.defender_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x +
                                        self.MECHA_WIGGLE[(pbge.my_state.anim_phase + n * 3) % 10],
                                        self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                       self.defense_frame)

        if self.kill_counter != 0:
            if self.kill_counter < 0:
                x, y = self.attacker_positions[self.num_attackers - 1]
                self.small_boom_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x,
                                                 self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                                8 + self.kill_counter)
                self.kill_counter += 1
                if self.kill_counter == 0:
                    self.num_attackers -= 1
            else:
                x, y = self.defender_positions[self.num_defenders - 1]
                self.small_boom_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x,
                                                 self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                                8 - self.kill_counter)
                self.kill_counter -= 1
                if self.kill_counter == 0:
                    self.num_defenders -= 1

        elif self.casulties:
            self.kill_counter = self.casulties.pop(0) * 8


class WorldMapWarTurn:
    def __init__(self, world_map_war: WorldMapWar, camp: gears.GearHeadCampaign, fac, callback: WarCallback):
        # callback is used to call back to the handler plot when this turn has been resolved.
        self.world_map_war = world_map_war
        self.world_map = world_map_war.world_map
        self.camp = camp
        self.visualizer = campfeatures.WorldMapViewer(world_map_war.world_map)
        self.fac = fac
        self.message = ""
        self.target_waypoint = None
        self.target_node = None
        self.callback = callback

    def _close_turn_alert(self, _wid, _ev):
        self.callback(self.camp, None)

    def prepare_for_war(self):
        if not self.world_map_war.war_teams[self.fac].boosted:
            self.world_map_war.war_teams[self.fac].boosted = True
        elif self.world_map_war.player_team and self.camp.are_faction_enemies(self.fac, self.world_map_war.player_team):
            self.world_map_war.war_teams[self.world_map_war.player_team].boosted = False
        _=WorldMapAlert(
            "{} prepares for war.".format(self.fac),
            self.visualizer, self.world_map.get_node_with_destination(self.world_map_war.war_teams[self.fac].home_base).entrance,
            self._close_turn_alert
        )

    def attack_desirability(self, target_node: campfeatures.WorldMapNode):
        fac = target_node.destination.faction
        if fac and self.world_map_war.war_teams[fac].home_base is target_node.destination:
            desirability = self.world_map_war.get_defense_strength(target_node)
        elif not fac:
            desirability = 6
        else:
            desirability = self.world_map_war.get_defense_strength(target_node) + 12
        return desirability

    DEFENSE_OBJECTIVES = (
        missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_AID_ALLIED_FORCES,
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DESTROY_ARTILLERY,
        missionbuilder.BAMO_EXTRACT_ALLIED_FORCES
    )

    def get_defense_missionseed(self, target_node):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(target_node.destination)
        my_adv = missionbuilder.BuildAMissionSeed(
            self.camp, "Defend {}".format(target_node), target_node.destination, target_node.entrance,
            self.fac, target_node.destination.faction,
            self.world_map_war.rank + self.num_attackers * 3 - self.num_defenders * 3,
            objectives=random.sample(self.DEFENSE_OBJECTIVES, 2), scenegen=sgen, architecture=archi,
            on_win=DefenderWinsEffect(self.fac, target_node, self.world_map_war,
                                      False),
            on_loss=AttackerWinsEffect(self.fac, target_node,
                                       self.world_map_war, False),
            auto_exit=True,
            mission_grammar=missionbuilder.MissionGrammar(
                "defend {} from {}".format(target_node, self.fac),
                "capture {} for {}".format(target_node, self.fac),
                "I defended {} from you.".format(target_node),
                "you defeated me in {}".format(target_node),
                "you invaded {}".format(target_node),
                "I captured {}".format(target_node)
            ),
            win_message="{} has been repelled!".format(self.fac),
            loss_message="{} has been captured by {}!".format(target_node, self.fac)
        )
        return my_adv

    def go_to_war(self, target_node):
        # Perform a war action. If the war is targeting the metroscene that the PC is in, the PC might take part
        # in the defense. This is the function that potentially returns the adventure seed.
        num_attackers = self.world_map_war.get_attack_strength(self.fac)
        num_defenders = self.world_map_war.get_defense_strength(target_node)
        spend_boost = True

        attack_frame = self.world_map_war.legend.get_mecha_frame(self.world_map_war.war_teams[self.fac].color)
        if target_node.destination.faction:
            defense_frame = self.world_map_war.legend.get_mecha_frame(
                self.world_map_war.war_teams[target_node.destination.faction].color)
        else:
            defense_frame = self.world_map_war.legend.get_mecha_frame(0)

        if not target_node.destination.faction:
            msg = "{} occupies {}.".format(self.fac, target_node)
            num_defenders = 0
            spend_boost = False
        elif self.camp.are_faction_enemies(self.fac, target_node.destination):
            msg = "{} attacks {}.".format(self.fac, target_node)
        else:
            msg = "{} launches surprise attack on {}!".format(self.fac, target_node)
            self.camp.set_faction_enemies(self.fac, target_node.destination)

        # Set the initial alert.
        _=WorldMapBattleAlert(
            msg, self.visualizer, target_node, self.war_phase_two,
            num_attackers, 0, self.world_map_war,
            data=(target_node, num_attackers, num_defenders, spend_boost, attack_frame, defense_frame),
            attack_frame=attack_frame, defense_frame=defense_frame
        )

    def _start_player_mission(self, wid, _ev):
        target_node, _num_attackers, _num_defenders, _spend_boost, _attack_frame, _defense_frame = wid.data
        self.callback(self.camp, self.get_defense_missionseed(target_node))

    def war_phase_two(self, wid, _ev):
        target_node, num_attackers, num_defenders, spend_boost, attack_frame, defense_frame = wid.data

        # Next, we branch depending on whether the PC gets to defend or not.
        pc_metro_scene = self.camp.scene.get_metro_scene()
        if pc_metro_scene is target_node.destination:
            if self.world_map_war.player_team and self.world_map_war.player_team is target_node.destination.faction:
                self.callback(self.camp, self.get_defense_missionseed(target_node))
                return
            elif self.fac != self.world_map_war.player_team:
                mymenu = campfeatures.WorldMapMenu(
                    self.camp, target_node.entrance
                )
                _=mymenu.add_item("Aid the defense of {}.".format(target_node), self._start_player_mission)
                _=mymenu.add_item("Don't get involved in the fighting.", self._do_war_auto_fighting, data=wid.data)
                mymenu.push_and_deploy()
                return
        self._do_war_auto_fighting(wid, None)

    def _do_war_auto_fighting(self, wid, _ev):
        target_node, num_attackers, num_defenders, spend_boost, attack_frame, defense_frame = wid.data
        # Show the results of the fighting.
        if num_defenders > 0:
            attacker_casulties = 0
            defender_casulties = 0
            while num_attackers - attacker_casulties > 0 and num_defenders - defender_casulties > 0:
                if random.randint(1, 2) == 1:
                    attacker_casulties += 1
                else:
                    defender_casulties += 1
            attacker_won = num_attackers - attacker_casulties > 0
            _=WorldMapBattleAlert(
                "The fighting begins...", self.visualizer, target_node, None,
                num_attackers, num_defenders, self.world_map_war,
                attacker_casulties=attacker_casulties, defender_casulties=defender_casulties,
                attack_frame=attack_frame, defense_frame=defense_frame
            )
        else:
            attacker_won = True
            attacker_casulties = 0
            defender_casulties = 0

        if attacker_won:
            self.world_map_war.capture(self.camp, self.fac, target_node)
            _=WorldMapBattleAlert(
                "{} has captured {}.".format(self.fac, target_node),
                self.visualizer, target_node, self._close_turn_alert,
                num_attackers - attacker_casulties, 0, self.world_map_war,
                attack_frame=attack_frame, defense_frame=defense_frame
            )
        else:
            _=WorldMapBattleAlert(
                "{} have been defeated.".format(self.fac),
                self.visualizer, target_node, self._close_turn_alert,
                0, num_defenders - defender_casulties, self.world_map_war,
                attack_frame=attack_frame, defense_frame=defense_frame
            )

        if spend_boost:
            self.world_map_war.war_teams[self.fac].boosted = False

    def __call__(self):
        # Step One: See if the faction is a valid war faction.
        if self.fac not in self.world_map_war.war_teams:
            # Error check- if this team has already been defeated, they don't get a turn.
            self.callback(self.camp, None)
        elif self.fac is self.world_map_war.player_team:
            self.callback(self.camp, None)
        else:
            # Step Two: check to see if the hqnode is in mortal danger.
            attack_candidates = set()
            if self.world_map_war.war_teams[self.fac].home_base:
                hqnode = self.world_map.get_node_with_destination(self.world_map_war.war_teams[self.fac].home_base)
                for edge in self.world_map.edges:
                    if edge.connects_to_node(hqnode):
                        far_node = edge.get_link(hqnode)
                        if self.camp.are_faction_enemies(hqnode.destination, far_node.destination) and far_node.destination is not self.world_map_war.just_captured:
                            attack_candidates.add(far_node)
            # If no mortal danger, check other nodes to possibly invade.
            if not attack_candidates:
                # Check for other nodes to attack.
                for node in self.world_map.nodes:
                    if node.destination and node.destination.faction is self.fac:
                        for edge in self.world_map.edges:
                            if edge.connects_to_node(node):
                                far_node = edge.get_link(node)
                                if self.camp.are_faction_enemies(self.fac, far_node.destination) and far_node.destination is not self.world_map_war.just_captured:
                                    attack_candidates.add(far_node)
                                elif not far_node.destination.faction:
                                    attack_candidates.add(far_node)
                                elif (
                                        far_node.destination.faction is not self.fac and
                                        random.randint(1, 100) > self.world_map_war.war_teams[self.fac].loyalty and
                                        (
                                                far_node.destination.faction is not self.world_map_war.player_team or
                                                self.world_map_war.war_teams[far_node.destination.faction].home_base is not
                                                far_node.destination
                                        )
                                ):
                                    attack_candidates.add(far_node)

            if random.randint(1, 100) > self.world_map_war.war_teams[self.fac].aggression and not self.world_map_war.war_teams[self.fac].boosted:
                self.prepare_for_war()
            elif not attack_candidates:
                self.prepare_for_war()
            else:
                # Attack!
                attack_candidates = sorted(attack_candidates, key=self.attack_desirability)
                i = min(random.randint(0, len(attack_candidates) - 1), random.randint(0, len(attack_candidates) - 1))
                self.go_to_war(attack_candidates[i])


class RoundAnnouncer:
    def __init__(self):
        self.bitmap = pbge.my_state.huge_font.render("War Update", True, pbge.TEXT_COLOR)
        _=pbge.alerts.FunAlert(self)

    def __call__(self):
        screen_rect = pbge.my_state.screen.get_rect()
        myrect = self.bitmap.get_rect(center=screen_rect.center)
        pbge.default_border.render(myrect)
        _=pbge.my_state.screen.blit(self.bitmap, myrect)


class WorldMapWarRound:
    # Treating this as a board game, here we have the effects of one round.
    def __init__(self, world_map_war: WorldMapWar, camp: gears.GearHeadCampaign):
        self.world_map_war = world_map_war
        self.camp = camp
        self.actors = list(world_map_war.war_teams.keys())
        self.actors.sort(key=self._sort_teams)
        _=RoundAnnouncer()

    def _sort_teams(self, fac):
        if fac is self.world_map_war.player_team:
            return 0
        else:
            return 99

    def keep_going(self):
        return bool(self.actors)

    def perform_turn(self, callback: WarCallback):
        # This function may return a mission seed. If so, perform that mission seed before proceeding with the next
        # turn.
        myfac = self.actors.pop()
        _=WorldMapWarTurn(self.world_map_war, self.camp, myfac, callback)()


class EdgeAttack:
    def __init__(self, camp, edge: campfeatures.WorldMapEdge, start_point: campfeatures.WorldMapNode, war: WorldMapWar):
        self.camp = camp
        self.edge = edge
        self.start_point = start_point
        self.war = war
        self.adv = None

    def __call__(self, wid, _ev):
        camp = wid.data
        self.adv = self.war.get_attack_missionseed(
            camp, self.war.player_team, self.start_point,
            self.edge.get_link(self.start_point)  # pyright: ignore[reportArgumentType]
        )

        dest_node = self.edge.get_link(self.start_point)
        if self.adv.can_do_mission(camp):
            if dest_node.destination.faction:
                _=self.adv(camp)
            else:
                _=pbge.alerts.TextAlert("You move into {} unopposed.".format(dest_node))
                self.war.capture(camp, self.war.player_team, dest_node)

                camp.go(dest_node.entrance)
                self.adv.end_plot(camp, True)
            self.war.ready_for_next_round = True
        else:
            _=pbge.alerts.TextAlert("You are not equipped with mecha that can attack {}.".format(dest_node))
            self.adv.end_plot(camp, True)


class WorldMapWarHandler(Plot):
    LABEL = "WORLD_MAP_WAR"
    scope = True
    active = True

    @property
    def memo(self):
        wmw = self.elements.get(WORLD_MAP_WAR)
        if wmw:
            return wmw.get_memo()

    def custom_init(self, nart):
        self.world_map = nart.camp.campdata[self.elements[WORLD_MAP_IDENTIFIER]]
        self.current_round = None
        world_map_teams = self.elements.get(WORLD_MAP_TEAMS, dict())
        world_map_legend = self.elements.get(WORLD_MAP_LEGEND, None)
        self.world_map_war = self.register_element(WORLD_MAP_WAR, WorldMapWar(self.rank, self.world_map,
                                                                              world_map_teams, world_map_legend))
        self.adventure_seed = None
        return True

    def check_war_status(self, camp: gears.GearHeadCampaign):
        # If the war is won by the player team, send trigger and end plot.
        # If the war is lost by the player team, send trigger and end plot.
        # Otherwise, I guess we don't have anything to do here.
        result = self.world_map_war.get_war_status(camp)
        if result == self.world_map_war.WAR_WON:
            _=camp.check_trigger("WIN", self)
            self.end_plot(camp)
        elif result == self.world_map_war.WAR_LOST:
            _=camp.check_trigger("LOSE", self)
            self.end_plot(camp)

    def war_turn_callback(self, camp: gears.GearHeadCampaign, adventure_seed):
        self.adventure_seed = adventure_seed
        if self.adventure_seed:
            if self.adventure_seed.can_do_mission(camp):
                self.adventure_seed(camp)
            else:
                _=pbge.alerts.TextAlert("Without working mecha, you are unable to take part in the battle.")
                self.adventure_seed.on_loss(camp)
                self.adventure_seed = None
            self.check_war_status(camp)
        elif self.current_round.keep_going():
            self.handle_war_round(camp)
        if self.current_round and not self.current_round.keep_going():
            self.current_round = None
            self.world_map_war.just_captured = None
            camp.check_trigger("WARROUND", self.elements.get(WORLD_MAP_WAR))

    def handle_war_round(self, camp):
        if self.world_map_war.ready_for_next_round and not self.current_round:
            self.current_round = WorldMapWarRound(self.world_map_war, camp)
            self.world_map_war.ready_for_next_round = False
        if self.current_round and self.active and self.current_round.keep_going():
            self.current_round.perform_turn(self.war_turn_callback)


    def t_START(self, camp: gears.GearHeadCampaign):
        if self.adventure_seed and self.adventure_seed.is_completed():
            self.adventure_seed = None
            self.check_war_status(camp)
        if self.active and hasattr(camp.scene, "metrodat") and camp.scene.metrodat and not camp.has_a_destination():
            if not self.adventure_seed:
                self.handle_war_round(camp)

    def WORLD_MAP_WAR_NEXT(self, camp: gears.GearHeadCampaign):
        self.elements[WORLD_MAP_WAR].player_can_act = True

    def modify_puzzle_menu(self, camp: gears.GearHeadCampaign, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        super().modify_puzzle_menu(camp, thing, thingmenu)
        if self.world_map_war.player_team and camp.scene.faction is self.world_map_war.player_team and self.elements[WORLD_MAP_WAR].player_can_act:
            for node in self.world_map.nodes:
                if node.entrance is thing:
                    my_edges = [e for e in self.world_map.edges if
                                e.connects_to_node(node) and (e.visible or e.discoverable)]
                    for e in my_edges:
                        mydest = e.get_link(node)
                        e.visible = True
                        mydest.visible = True
                        if not mydest.destination.faction:
                            thingmenu.add_item(
                                "Capture {} for {}".format(mydest, self.world_map_war.player_team),
                                EdgeAttack(camp, e, node, self.world_map_war), desc=e, data=camp
                            )
                        elif camp.are_faction_enemies(mydest.destination, self.world_map_war.player_team):
                            thingmenu.add_item(
                                "Invade {} for {}".format(mydest, self.world_map_war.player_team),
                                EdgeAttack(camp, e, node, self.world_map_war), desc=e, data=camp
                            )
                    break
