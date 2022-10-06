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


class EdgeAttack:
    def __init__(self, edge: campfeatures.WorldMapEdge, start_point: campfeatures.WorldMapNode):
        self.edge = edge
        self.start_point = start_point

    def __call__(self, camp: gears.GearHeadCampaign):
        dest_node = self.edge.get_link(self.start_point)
        if self.edge.architecture and camp.has_mecha_party(enviro=self.edge.architecture.ENV):
            pass
        else:
            pbge.alert("You are not equipped with mecha that can attack {}.".format(dest_node))


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
    def __init__(self, image_name="wm_legend_war.png", num_icons=7, num_colors=8, hq_frames=(0,3), city_frames=(1,4),
                 fortress_frames=(2,5), mecha_frame=6):
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


class WorldMapWar:
    def __init__(self, world_map: campfeatures.WorldMap, war_teams: dict, legend=None):
        # war_teams is a dictionary of Faction:WarStats items.
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
        d,m = self.get_faction_strength_divmod(fac)
        if fac and fac in self.war_teams and node.destination is self.war_teams[fac].home_base:
            return min(d+m, 12)
        elif self.node_stats[node].fortified:
            return min(max(d*2, d+m), 10)
        else:
            return min(d, 5)

    def get_attack_strength(self, fac):
        d,m = divmod(self.war_teams[fac].strength, self.get_number_of_territories(fac) + 1)
        return min(d+m, 10)

    def get_node_income(self, node):
        dest = node.destination
        if hasattr(dest, "metro") and dest.metro:
            return max(dest.metro.get_quality_of_life_index().prosperity + 2, 1)
        else:
            return 3



class WorldMapWarTurn:
    DEFENDER_POSITIONS = [(-6,-16), (6,-16), (-12, -8), (-4, -8), (4, -8), (12, -8),
                          (-12, 8), (-4, 8), (4, 8), (12, 8), (-6, 16), (6, 16)]
    ATTACKER_POSITIONS = [(-8,-20),(8,-20),(15,-15),(20,-8),(20,8),(15,15),
                          (8,20),(-8,20),(-15,15),(-20,8),(-20,-8),(-15,-15)]
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

    def show_turn_progress(self, msg):
        self.message = msg
        if self.world_map_war.war_teams[self.fac].home_base:
            self.target_waypoint = self.world_map.get_node_with_destination(self.world_map_war.war_teams[self.fac].home_base).entrance
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

    MECHA_WIGGLE = (-1,-1,0,0,0,1,1,0,0,0)

    def render_war_alert(self):
        pbge.my_state.view()
        self.visualizer.render(waypoint=self.target_waypoint)
        myrect = campfeatures.WorldMapMenu.MENU_AREA.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(pbge.MEDIUMFONT, self.message, myrect, justify=0)
        num_attackers = self.world_map_war.get_attack_strength(self.fac)
        num_defenders = self.world_map_war.get_defense_strength(self.target_node)
        attack_frame = self.world_map_war.legend.get_mecha_frame(self.world_map_war.war_teams[self.fac].color)
        map_rect = self.visualizer.map_area.get_rect()
        for n in range(num_attackers):
            x,y = self.attacker_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect)+x + self.MECHA_WIGGLE[(pbge.my_state.anim_phase+n*3)%10],
                                      self.visualizer.calc_map_y(self.target_node.pos[1], map_rect)+y), attack_frame)

        if self.target_node.destination.faction:
            defence_frame = self.world_map_war.legend.get_mecha_frame(self.world_map_war.war_teams[self.target_node.destination.faction].color)
        else:
            defence_frame = self.world_map_war.legend.get_mecha_frame(0)

        for n in range(num_defenders):
            x,y = self.attacker_positions[n]
            self.mecha_sprite.render_c((self.visualizer.calc_map_x(self.target_node.pos[0], map_rect)+x + self.MECHA_WIGGLE[(pbge.my_state.anim_phase+n*3)%10],
                                        self.visualizer.calc_map_y(self.target_node.pos[1], map_rect)+y), defence_frame)


    def update(self):
        income = 2
        for node in self.world_map.nodes:
            if node.destination.faction is self.fac:
                income += self.world_map_war.get_node_income(node)
        self.world_map_war.war_teams[self.fac].resources += income
        self.show_turn_progress("{} collects {} resources.".format(self.fac, income))

    def prepare_for_war(self):
        self.show_turn_progress("{} prepares for war.".format(self.fac))
        meks, change = divmod(self.world_map_war.war_teams[self.fac].resources, 5)
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

    def got_to_war(self, target_node):
        # Perform a war action. If the war is targeting the metroscene that the PC is in, the PC might take part
        # in the defense. This is the function that potentially returns the adventure seed.
        pc_metro_scene = self.camp.scene.get_metro_scene()
        #if pc_metro_scene is target_node.destination:
        #    pass
        if not target_node.destination.faction:
            msg = "{} occupies {}.".format(self.fac, target_node)
        elif self.camp.are_faction_enemies(self.fac, target_node.destination):
            msg = "{} attacks {}.".format(self.fac, target_node)
        else:
            msg = "{} launches surprise attack on {}!".format(self.fac, target_node)
        self.show_war_progress(msg, target_node)

    def __call__(self):
        # Return a mission seed if the player is going to have to fight, or nothing otherwise.
        # Step One: See if the faction is severely depleted. If it is, prepare for war. Also, the player team always
        # prepares for war because it's expected that the player will be out there attacking for them.
        self.update()
        d, m = self.world_map_war.get_faction_strength_divmod(self.fac)
        if d < random.randint(2,3) or self.fac is self.world_map_war.player_team:
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
                            elif far_node.destination.faction is not self.fac and random.randint(1,100) > self.world_map_war.war_teams[self.fac].loyalty:
                                attack_candidates.add(far_node)

        if random.randint(1,100) > self.world_map_war.war_teams[self.fac].aggression and d < random.randint(4,6):
            self.prepare_for_war()
            return None
        elif not attack_candidates:
            self.prepare_for_war()
            return None
        else:
            # Attack!
            attack_candidates = sorted(attack_candidates, key=self.attack_desirability)
            i = min(random.randint(0,len(attack_candidates)-1), random.randint(0,len(attack_candidates)-1))
            return self.got_to_war(attack_candidates[i])


class WorldMapWarRound:
    # Treating this as a board game, here we have the effects of one round.
    def __init__(self, world_map_war: WorldMapWar, camp: gears.GearHeadCampaign):
        self.world_map_war = world_map_war
        self.camp = camp
        self.actors = list(world_map_war.war_teams.keys())
        self.actors.sort(key=self._sort_teams)

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



class WorldMapWarHandler(Plot):
    LABEL = "WORLD_MAP_WAR"
    scope = True
    active = True

    def custom_init(self, nart):
        self.world_map = nart.camp.campdata[self.elements[WORLD_MAP_IDENTIFIER]]
        self.current_round = None
        world_map_teams = self.elements.get(WORLD_MAP_TEAMS, dict())
        world_map_legend = self.elements.get(WORLD_MAP_LEGEND, None)
        self.world_map_war = self.register_element(WORLD_MAP_WAR, WorldMapWar(self.world_map, world_map_teams,
                                                                              world_map_legend))

        return True

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        super().modify_puzzle_menu(camp, thing, thingmenu)
        """for node in self.world_map.nodes:
            if node.entrance is thing:
                node.visible = True
                my_edges = [e for e in self.world_map.edges if
                            e.connects_to_node(node) and (e.visible or e.discoverable)]
                for e in my_edges:
                    mydest = e.get_link(node)
                    e.visible = True
                    mydest.visible = True
                    thingmenu.add_item("Capture {}".format(mydest), EdgeAttack(e, node), e)
                break"""

