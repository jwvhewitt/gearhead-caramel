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
from . import missionbuilder, rwme_objectives, campfeatures
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections

# Elements passed to the world map handler plot.
WORLD_MAP_IDENTIFIER = "WORLD_MAP_IDENTIFIER"
WORLD_MAP_TEAMS = "WORLD_MAP_TEAMS"
WORLD_MAP_LEGEND = "WORLD_MAP_LEGEND"
WORLD_MAP_WAR = "WORLD_MAP_WAR"


class WarStats:
    def __init__(self, home_base=None, strength=5, resources=0, aggression=50, loyalty=90, color=0, unpopular=False):
        # home_base is the city where this team's HQ is located. Capture it, and that team is eliminated.
        # strength reflects the number/quality of troops present; it's divided among all territories.
        # resources is basically cash. May be spent to get more strength or to build fortifications.
        # aggression is how likely they are to attack instead of turtle
        # loyalty is the % chance this faction will honor a peace treaty. Lower loyalty = more backstabbing.
        # unpopular marks a faction that you can organize insurrection against.
        self.home_base = home_base
        self.strength = strength
        self.resources = resources
        self.aggression = aggression
        self.loyalty = loyalty
        self.color = color
        self.unpopular = unpopular


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
    def __init__(self, attack_team, target_node, attack_ante, target_ante, world_map_war, attacker_is_pc):
        # attack_ante and target_ante are the number of troops committed by both sides.
        self.attack_team = attack_team
        self.target_node = target_node
        self.attack_ante = attack_ante
        self.target_ante = target_ante
        self.world_map_war = world_map_war
        self.attacker_is_pc = attacker_is_pc

    def __call__(self, camp: gears.GearHeadCampaign):
        self.world_map_war.capture(camp, self.attack_team, self.target_node)
        self.world_map_war.war_teams[self.attack_team].strength -= self.attack_ante // 2
        self.world_map_war.war_teams[self.target_node.destination.faction].strength -= self.target_ante
        if self.attacker_is_pc:
            camp.go(self.target_node.entrance)


class DefenderWinsEffect:
    def __init__(self, attack_team, target_node, attack_ante, target_ante, world_map_war, attacker_is_pc):
        # attack_ante and target_ante are the number of troops committed by both sides.
        self.attack_team = attack_team
        self.target_node = target_node
        self.attack_ante = attack_ante
        self.target_ante = target_ante
        self.world_map_war = world_map_war
        self.attacker_is_pc = attacker_is_pc

    def __call__(self, camp):
        self.world_map_war.war_teams[self.attack_team].strength -= self.attack_ante
        self.world_map_war.war_teams[self.target_node.destination.faction].strength -= self.target_ante // 2


class WorldMapWar:
    def __init__(self, rank, world_map: campfeatures.WorldMap, war_teams: dict, legend=None):
        # war_teams is a dictionary of Faction:WarStats items.
        self.rank = rank
        self.world_map = world_map
        self.war_teams = dict()
        if war_teams:
            self.war_teams.update(war_teams)
        self.node_stats = collections.defaultdict(NodeStats)

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

    def get_number_of_territories(self, fac):
        n = 0
        for node in self.world_map.nodes:
            if node.destination.faction is fac:
                n += 1
        return n

    def get_faction_strength_divmod(self, fac):
        # Return the average strength for each territory, plus the remainder.
        if fac in self.war_teams:
            return divmod(self.war_teams[fac].strength, self.get_number_of_territories(fac))
        else:
            return (0, 0)

    def get_defense_strength(self, node):
        fac = node.destination.faction
        d, m = self.get_faction_strength_divmod(fac)
        if fac and fac in self.war_teams and node.destination is self.war_teams[fac].home_base:
            return min(d + m, 12)
        elif self.node_stats[node].fortified:
            return min(max(d * 2, d + m), 10)
        else:
            return min(d, 5)

    def get_attack_strength(self, fac):
        d, m = divmod(self.war_teams[fac].strength, self.get_number_of_territories(fac) + 1)
        return min(d + m, 10)

    def get_node_income(self, node):
        dest = node.destination
        if hasattr(dest, "metro") and dest.metro:
            return max(dest.metro.get_quality_of_life_index().prosperity + 2, 1)
        else:
            return 3

    def remove_team(self, camp, losing_fac):
        for node in self.world_map.nodes:
            if node.destination.faction is losing_fac:
                node.destination.faction = None
                node.destination.purge_faction(camp, losing_fac)
                self.legend.set_color(node, 0)
        del self.war_teams[losing_fac]

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
        if node.destination.faction:
            node.destination.purge_faction(camp, node.destination.faction)
        node.destination.faction = attacking_fac
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


    ATTACK_OBJECTIVES = (
        missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_AID_ALLIED_FORCES,
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_CAPTURE_BUILDINGS,
        missionbuilder.BAMO_SURVIVE_THE_AMBUSH
    )

    def get_attack_missionseed(self, camp, attacking_team, start_node, target_node: campfeatures.WorldMapNode):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(target_node.destination)
        num_attackers = self.get_attack_strength(attacking_team)
        num_defenders = self.get_defense_strength(target_node)
        my_adv = missionbuilder.BuildAMissionSeed(
            camp, "Capture {}".format(target_node), start_node.destination, start_node.entrance,
            target_node.destination.faction, attacking_team,
            max(self.rank + num_defenders * 3 - num_attackers * 3, self.rank),
            # adv_type="BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": target_node.entrance, "DEST_SCENE": target_node.destination,
                             "ENTRANCE_ANCHOR": random.choice(pbge.randmaps.anchors.EDGES)},
            objectives=random.sample(self.ATTACK_OBJECTIVES, 2), scenegen=sgen, architecture=archi,
            on_win=AttackerWinsEffect(attacking_team, target_node, num_attackers, num_defenders, self, True),
            on_loss=DefenderWinsEffect(attacking_team, target_node, num_attackers, num_defenders, self, True),
            auto_exit=True,
            mission_grammar=missionbuilder.MissionGrammar(
                "capture {} for {}".format(target_node, attacking_team),
                "defend {} from {}".format(target_node, attacking_team),
                "I captured {} from you.".format(target_node),
                "you defeated me in {}".format(target_node),
                "I captured {}".format(target_node),
                "you captured {} from me".format(target_node)
            ),
            win_message="{} has been captured by {}!".format(target_node, attacking_team),
            loss_message="{} has been defeated!".format(attacking_team)
        )
        return my_adv


class WorldMapWarTurn:
    DEFENDER_POSITIONS = [(-6, -16), (6, -16), (-12, -8), (-4, -8), (4, -8), (12, -8),
                          (-12, 8), (-4, 8), (4, 8), (12, 8), (-6, 16), (6, 16)]
    ATTACKER_POSITIONS = [(-8, -20), (8, -20), (15, -15), (20, -8), (20, 8), (15, 15),
                          (8, 20), (-8, 20), (-15, 15), (-20, 8), (-20, -8), (-15, -15)]

    def __init__(self, world_map_war: WorldMapWar, camp: gears.GearHeadCampaign, fac):
        self.world_map_war = world_map_war
        self.world_map = world_map_war.world_map
        self.camp = camp
        self.visualizer = campfeatures.WorldMapViewer(world_map_war.world_map)
        self.fac = fac
        self.message = ""
        self.target_waypoint = None
        self.target_node = None
        self.defender_positions = self.DEFENDER_POSITIONS.copy()
        random.shuffle(self.defender_positions)
        self.attacker_positions = self.ATTACKER_POSITIONS.copy()
        random.shuffle(self.attacker_positions)
        self.mecha_sprite = pbge.image.Image(self.world_map_war.legend.image_name, 20, 20)
        self.small_boom_sprite = pbge.image.Image("anim_smallboom.png", 64, 64)
        self.casulties = list()
        self.num_attackers = 0
        self.num_defenders = 0
        self.kill_counter = 0  # A special counter used to show mecha being destroyed.

    def show_turn_progress(self, msg):
        self.message = msg
        if self.world_map_war.war_teams[self.fac].home_base:
            self.target_waypoint = self.world_map.get_node_with_destination(
                self.world_map_war.war_teams[self.fac].home_base).entrance
        else:
            self.target_waypoint = None
        pbge.alert_display(self.render_alert)

    def render_alert(self):
        pbge.my_state.view()
        self.visualizer.render(waypoint=self.target_waypoint)
        myrect = campfeatures.WorldMapMenu.MENU_AREA.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(pbge.MEDIUMFONT, self.message, myrect, justify=0)

    def show_war_progress(self, msg, target_node):
        self.message = msg
        self.target_node = target_node
        self.target_waypoint = target_node.entrance
        pbge.alert_display(self.render_war_alert)

    MECHA_WIGGLE = (-1, -1, 0, 0, 0, 1, 1, 0, 0, 0)

    def render_war_alert(self):
        pbge.my_state.view()
        self.visualizer.render(waypoint=self.target_waypoint)
        myrect = campfeatures.WorldMapMenu.MENU_AREA.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(pbge.MEDIUMFONT, self.message, myrect, justify=0)
        attack_frame = self.world_map_war.legend.get_mecha_frame(self.world_map_war.war_teams[self.fac].color)
        map_rect = self.visualizer.map_area.get_rect()
        for n in range(self.num_attackers):
            x, y = self.attacker_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x +
                                        self.MECHA_WIGGLE[(pbge.my_state.anim_phase + n * 3) % 10],
                                        self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                       attack_frame)

        if self.target_node.destination.faction:
            defence_frame = self.world_map_war.legend.get_mecha_frame(
                self.world_map_war.war_teams[self.target_node.destination.faction].color)
        else:
            defence_frame = self.world_map_war.legend.get_mecha_frame(0)

        for n in range(self.num_defenders):
            x, y = self.defender_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect) + x +
                                        self.MECHA_WIGGLE[(pbge.my_state.anim_phase + n * 3) % 10],
                                        self.visualizer.calc_map_y(self.target_node.pos[1], map_rect) + y),
                                       defence_frame)

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

    def update(self):
        income = 2
        for node in self.world_map.nodes:
            if node.destination.faction is self.fac:
                income += self.world_map_war.get_node_income(node)
        self.world_map_war.war_teams[self.fac].resources += income
        self.show_turn_progress("{} collects {} resources.".format(self.fac, income))

    def _mecha_cost(self):
        # The player doesn't need as much help as the NPC teams.
        if self.fac is self.world_map_war.player_team:
            return 12
        else:
            return 5

    def prepare_for_war(self):
        self.show_turn_progress("{} prepares for war.".format(self.fac))
        meks, change = divmod(self.world_map_war.war_teams[self.fac].resources, self._mecha_cost())
        self.world_map_war.war_teams[self.fac].strength += meks
        self.world_map_war.war_teams[self.fac].resources = change

    def attack_desirability(self, target_node: campfeatures.WorldMapNode):
        fac = target_node.destination.faction
        if fac and self.world_map_war.war_teams[fac].home_base is target_node.destination:
            desirability = self.world_map_war.get_defense_strength(target_node)
        elif not fac:
            desirability = 6
        else:
            desirability = self.world_map_war.get_defense_strength(target_node) + 12
        return desirability

    DEFENCE_OBJECTIVES = (
        missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_AID_ALLIED_FORCES,
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DESTROY_ARTILLERY,
        missionbuilder.BAMO_EXTRACT_ALLIED_FORCES
    )

    def get_defence_missionseed(self, target_node):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(target_node.destination)
        my_adv = missionbuilder.BuildAMissionSeed(
            self.camp, "Defend {}".format(target_node), target_node.destination, target_node.entrance,
            self.fac, target_node.destination.faction,
            self.world_map_war.rank + self.num_attackers * 3 - self.num_defenders * 3,
            objectives=random.sample(self.DEFENCE_OBJECTIVES, 2), scenegen=sgen, architecture=archi,
            on_win=DefenderWinsEffect(self.fac, target_node, self.num_attackers, self.num_defenders, self.world_map_war,
                                      False),
            on_loss=AttackerWinsEffect(self.fac, target_node, self.num_attackers, self.num_defenders,
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

    def got_to_war(self, target_node):
        # Perform a war action. If the war is targeting the metroscene that the PC is in, the PC might take part
        # in the defense. This is the function that potentially returns the adventure seed.
        self.num_attackers = self.world_map_war.get_attack_strength(self.fac)
        self.num_defenders = self.world_map_war.get_defense_strength(target_node)

        if not target_node.destination.faction:
            msg = "{} occupies {}.".format(self.fac, target_node)
        elif self.camp.are_faction_enemies(self.fac, target_node.destination):
            msg = "{} attacks {}.".format(self.fac, target_node)
        else:
            msg = "{} launches surprise attack on {}!".format(self.fac, target_node)
            self.camp.set_faction_enemies(self.fac, target_node.destination)
        self.show_war_progress(msg, target_node)

        pc_metro_scene = self.camp.scene.get_metro_scene()
        if pc_metro_scene is target_node.destination:
            if self.world_map_war.player_team and self.world_map_war.player_team is target_node.destination.faction:
                return self.get_defence_missionseed(target_node)
            elif self.fac != self.world_map_war.player_team:
                mymenu = pbge.rpgmenu.Menu(
                    campfeatures.WorldMapMenu.MENU_AREA.dx, campfeatures.WorldMapMenu.MENU_AREA.dy,
                    campfeatures.WorldMapMenu.MENU_AREA.w, campfeatures.WorldMapMenu.MENU_AREA.h,
                    predraw=self.render_war_alert
                )
                self.message = ""
                mymenu.add_item("Aid the defence of {}.".format(target_node), True)
                mymenu.add_item("Don't get involved in the fighting.", False)
                if mymenu.query():
                    return self.get_defence_missionseed(target_node)

        # Show the results of the fighting.
        if self.num_defenders > 0:
            self.casulties.clear()
            attacker_casulties = 0
            defender_casulties = 0
            while self.num_attackers - attacker_casulties > 0 and self.num_defenders - defender_casulties > 0:
                if random.randint(1, 2) == 1:
                    self.casulties.append(-1)
                    attacker_casulties += 1
                else:
                    self.casulties.append(1)
                    defender_casulties += 1
            attacker_won = self.num_attackers - attacker_casulties > 0
            self.show_war_progress("The fighting begins...", target_node)
            self.world_map_war.war_teams[self.fac].strength -= attacker_casulties
            if target_node.destination.faction and target_node.destination.faction in self.world_map_war.war_teams:
                self.world_map_war.war_teams[target_node.destination.faction].strength -= defender_casulties
        else:
            attacker_won = True

        if attacker_won:
            self.world_map_war.capture(self.camp, self.fac, target_node)
            self.show_war_progress("{} has captured {}.".format(self.fac, target_node), target_node)
        else:
            self.show_war_progress("{} have been defeated.".format(self.fac), target_node)

    def __call__(self):
        # Return a mission seed if the player is going to have to fight, or nothing otherwise.
        # Step One: See if the faction is severely depleted. If it is, prepare for war. Also, the player team always
        # prepares for war because it's expected that the player will be out there attacking for them.
        if self.fac not in self.world_map_war.war_teams:
            # Error check- if this team has already been defeated, they don't get a turn.
            return None
        self.update()
        d, m = self.world_map_war.get_faction_strength_divmod(self.fac)
        if d < random.randint(2, 3) or self.fac is self.world_map_war.player_team:
            self.prepare_for_war()
            return None

        # Step Two: check to see if the hqnode is in mortal danger.
        attack_candidates = set()
        if self.world_map_war.war_teams[self.fac].home_base:
            hqnode = self.world_map.get_node_with_destination(self.world_map_war.war_teams[self.fac].home_base)
            for edge in self.world_map.edges:
                if edge.connects_to_node(hqnode):
                    far_node = edge.get_link(hqnode)
                    if self.camp.are_faction_enemies(hqnode.destination, far_node.destination):
                        attack_candidates.add(far_node)
        # If no mortal danger, check other nodes to possibly invade.
        if not attack_candidates:
            # Check for other nodes to attack.
            for node in self.world_map.nodes:
                if node.destination and node.destination.faction is self.fac:
                    for edge in self.world_map.edges:
                        if edge.connects_to_node(node):
                            far_node = edge.get_link(node)
                            if self.camp.are_faction_enemies(self.fac, far_node.destination):
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

        if random.randint(1, 100) > self.world_map_war.war_teams[self.fac].aggression and d < random.randint(4, 6):
            self.prepare_for_war()
            return None
        elif not attack_candidates:
            self.prepare_for_war()
            return None
        else:
            # Attack!
            attack_candidates = sorted(attack_candidates, key=self.attack_desirability)
            i = min(random.randint(0, len(attack_candidates) - 1), random.randint(0, len(attack_candidates) - 1))
            return self.got_to_war(attack_candidates[i])


class RoundAnnouncer:
    def __init__(self):
        self.bitmap = pbge.my_state.huge_font.render("War Update", True, pbge.TEXT_COLOR)
        pbge.alert_display(self)

    def __call__(self):
        pbge.my_state.view()
        screen_rect = pbge.my_state.screen.get_rect()
        myrect = self.bitmap.get_rect(center=screen_rect.center)
        pbge.default_border.render(myrect)
        pbge.my_state.screen.blit(self.bitmap, myrect)


class WorldMapWarRound:
    # Treating this as a board game, here we have the effects of one round.
    def __init__(self, world_map_war: WorldMapWar, camp: gears.GearHeadCampaign):
        self.world_map_war = world_map_war
        self.camp = camp
        self.actors = list(world_map_war.war_teams.keys())
        self.actors.sort(key=self._sort_teams)
        RoundAnnouncer()

    def _sort_teams(self, fac):
        if fac is self.world_map_war.player_team:
            return 0
        else:
            return 99

    def keep_going(self):
        return bool(self.actors)

    def perform_turn(self):
        # This function may return a mission seed. If so, perform that mission seed before proceeding with the next
        # turn.
        myfac = self.actors.pop()
        myturn = WorldMapWarTurn(self.world_map_war, self.camp, myfac)
        return myturn()


class EdgeAttack:
    def __init__(self, camp, edge: campfeatures.WorldMapEdge, start_point: campfeatures.WorldMapNode, war: WorldMapWar):
        self.edge = edge
        self.start_point = start_point
        self.war = war
        self.adv = war.get_attack_missionseed(camp, war.player_team, start_point,
                                              self.edge.get_link(self.start_point))

    def __call__(self, camp: gears.GearHeadCampaign):
        dest_node = self.edge.get_link(self.start_point)
        if self.adv.can_do_mission(camp):
            if dest_node.destination.faction:
                self.adv(camp)
            else:
                pbge.alert("You move into {} unopposed.".format(dest_node))
                self.war.capture(camp, self.war.player_team, dest_node)
                camp.go(dest_node.entrance)
            self.war.ready_for_next_round = True
        else:
            pbge.alert("You are not equipped with mecha that can attack {}.".format(dest_node))


class WorldMapWarHandler(Plot):
    LABEL = "WORLD_MAP_WAR"
    scope = True
    active = True

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
            camp.check_trigger("WIN", self)
            self.end_plot(camp)
        elif result == self.world_map_war.WAR_LOST:
            camp.check_trigger("LOSE", self)
            self.end_plot(camp)

    def handle_war_round(self, camp):
        if self.world_map_war.ready_for_next_round and not self.current_round:
            self.current_round = WorldMapWarRound(self.world_map_war, camp)
            self.world_map_war.ready_for_next_round = False
        if self.current_round:
            while self.active and self.current_round.keep_going():
                self.adventure_seed = self.current_round.perform_turn()
                if self.adventure_seed:
                    if self.adventure_seed.can_do_mission(camp):
                        self.adventure_seed(camp)
                        break
                    else:
                        pbge.alert("Without working mecha, you are unable to take part in the battle.")
                        self.adventure_seed.on_loss(camp)
                        self.adventure_seed = None
                self.check_war_status(camp)
            if not self.current_round.keep_going():
                self.current_round = None

    def t_START(self, camp: gears.GearHeadCampaign):
        if self.adventure_seed and self.adventure_seed.is_completed():
            self.adventure_seed = None
            self.check_war_status(camp)
        if self.active and hasattr(camp.scene, "metrodat") and camp.scene.metrodat and not camp.has_a_destination():
            if not self.adventure_seed:
                self.handle_war_round(camp)

    def modify_puzzle_menu(self, camp: gears.GearHeadCampaign, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        super().modify_puzzle_menu(camp, thing, thingmenu)
        if self.world_map_war.player_team and camp.scene.faction is self.world_map_war.player_team:
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
                                EdgeAttack(camp, e, node, self.world_map_war), e
                            )
                        elif camp.are_faction_enemies(mydest.destination, self.world_map_war.player_team):
                            thingmenu.add_item(
                                "Capture {} for {}".format(mydest, self.world_map_war.player_team),
                                EdgeAttack(camp, e, node, self.world_map_war), e
                            )
                    break
