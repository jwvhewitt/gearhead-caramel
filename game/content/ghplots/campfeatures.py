import pbge.memos
from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams, ghdialogue
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag, Offer
from game.content import plotutility, GHNarrativeRequest, PLOT_LIST
import game.content.gharchitecture
from . import missionbuilder
import collections
from game.content.plotutility import LMSkillsSelfIntro

from pbge import memos

Memo = pbge.memos.Memo

# This unit contains plots that handle standard features you may want to add to a campaign or a scene in that campaign.

# Some constants for camp.campdata to let other plots know what features are present in this campaign.
LANCE_HANDLER_ENABLED = "LANCE_HANDLER_ENABLED"  # If True, the standard lancemate handler is in effect.
LANCEDEV_ENABLED = "LANCEDEV_ENABLED"  # If this value exists, it will be a function with signature fun(camp)
# that returns True if a lancemate development plot can be loaded now.
WORLD_MAP_ENCOUNTERS = "WORLD_MAP_ENCOUNTERS"  # If exists, this will be a function that returns a MissionSeed.


# See below for the signature; always send named parameters.
# May return None.


class StandardLancemateHandler(Plot):
    LABEL = "CF_STANDARD_LANCEMATE_HANDLER"
    active = True
    scope = True

    def custom_init(self, nart):
        nart.camp.campdata[LANCE_HANDLER_ENABLED] = True
        nart.camp.campdata[LANCEDEV_ENABLED] = self.can_load_lancedev_plot
        return True

    def can_load_lancedev_plot(self, camp):
        return not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT)

    def _get_generic_offers(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        """
        :type camp: gears.GearHeadCampaign
        :type npc: gears.base.Character
        """
        mylist = list()
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            if camp.can_add_lancemate() and npc not in camp.party:
                # If the NPC has the lancemate tag, they might join the party.
                if npc.get_reaction_score(camp.pc, camp) < -20:
                    # A lancemate who is currently upset with the PC will not join the party.
                    mylist.append(Offer("[JOIN_REFUSAL]", is_generic=True,
                                        context=ContextTag([context.JOIN])))
                elif npc.relationship.data.get("LANCEMATE_TIME_OFF", 0) <= camp.day:
                    mylist.append(Offer("[JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN]),
                                        effect=game.content.plotutility.AutoJoiner(npc)))
                else:
                    # This NPC is taking some time off. Come back tomorrow.
                    mylist.append(Offer("[COMEBACKTOMORROW_JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN])))
            elif npc in camp.party and gears.tags.SCENE_PUBLIC in camp.scene.attributes:
                mylist.append(Offer("[LEAVEPARTY]", is_generic=True,
                                    context=ContextTag([context.LEAVEPARTY]),
                                    effect=game.content.plotutility.AutoLeaver(npc)))
            mylist.append(LMSkillsSelfIntro(npc))
        return mylist


class MetrosceneRecoveryHandler(Plot):
    LABEL = "CF_METROSCENE_RECOVERY_HANDLER"
    active = True
    scope = "METROSCENE"

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        # Upon entering this scene, deal with any dead or incapacitated party members.
        # Also, deal with party members who have lost their mecha. This may include the PC.
        etlr = plotutility.EnterTownLanceRecovery(camp, self.elements["METROSCENE"], self.elements["METRO"])
        if not camp.is_unfavorable_to_pc(self.elements["METROSCENE"]):
            camp.home_base = self.elements["MISSION_GATE"]

            if camp.campdata.get(LANCEDEV_ENABLED, False) and random.randint(1, 3) == 2 and not etlr.did_recovery:
                # We can maybe load a lancemate scene here. Yay!
                if camp.campdata[LANCEDEV_ENABLED](camp):
                    nart = GHNarrativeRequest(camp, pbge.plots.PlotState().based_on(self), adv_type="LANCEDEV",
                                              plot_list=PLOT_LIST)
                    if nart.story:
                        nart.build()


class WorldMapEncounterHandler(Plot):
    LABEL = "CF_WORLD_MAP_ENCOUNTER_HANDLER"
    active = True
    scope = True

    def custom_init(self, nart):
        nart.camp.campdata[WORLD_MAP_ENCOUNTERS] = self.choose_world_map_encounter
        return True

    def choose_world_map_encounter(
            self, camp: gears.GearHeadCampaign, metroscene, return_wp, encounter_chance=25, dest_scene=None,
            dest_wp=None,
            rank=None, scenegen=pbge.randmaps.SceneGenerator, architecture=gharchitecture.MechaScaleDeadzone,
            **kwargs
    ):
        candidate_seeds = list()
        # Step one: harvest any world map encounters that may exist within this adventure already.
        for p in camp.active_plots():
            if p is not self and hasattr(p, "generate_world_map_encounter"):
                myseed = p.generate_world_map_encounter(camp, metroscene, return_wp, dest_scene=dest_scene,
                                                        dest_wp=dest_wp,
                                                        rank=rank, scenegen=scenegen, architecture=architecture,
                                                        **kwargs)

                if myseed:
                    if hasattr(myseed, "priority"):
                        candidate_seeds += [myseed, ] * myseed.priority
                    else:
                        candidate_seeds.append(myseed)

                    if hasattr(myseed, "mandatory") and myseed.mandatory:
                        encounter_chance = 100

        # Step two: Attempt to load a generic world map encounter plot.
        for t in range(random.randint(2, 6)):
            myplotstate = PlotState(
                rank=rank, elements={"METROSCENE": metroscene, "DEST_SCENE": dest_scene, "KWARGS": kwargs.copy()}
            )
            myplot = game.content.load_dynamic_plot(camp, "RWMENCOUNTER", myplotstate)
            if myplot:
                myseed = myplot.generate_world_map_encounter(
                    camp, metroscene, return_wp, dest_scene=dest_scene, dest_wp=dest_wp,
                    rank=rank, scenegen=scenegen, architecture=architecture,
                    **kwargs
                )
                if myseed:
                    if hasattr(myseed, "priority"):
                        candidate_seeds += [myseed, ] * myseed.priority
                    else:
                        candidate_seeds.append(myseed)

                    if hasattr(myseed, "mandatory") and myseed.mandatory:
                        encounter_chance = 100

        if candidate_seeds and random.randint(1, 100) <= encounter_chance:
            return random.choice(candidate_seeds)


class MetrosceneWMEDefenseHandler(Plot):
    # This plot works with the above plot
    LABEL = "CF_METROSCENE_WME_DEFENSE_HANDLER"
    active = True
    scope = True

    def generate_world_map_encounter(self, camp: gears.GearHeadCampaign, metroscene, return_wp,
                                     dest_scene: gears.GearHeadScene, dest_wp,
                                     scenegen=gharchitecture.DeadZoneHighwaySceneGen,
                                     architecture=gharchitecture.MechaScaleSemiDeadzone,
                                     **kwargs):
        if camp.is_unfavorable_to_pc(dest_scene):
            myanchor = kwargs.get("entrance_anchor", None)
            if not myanchor:
                myanchor = pbge.randmaps.anchors.east
            myrank = self.rank
            dest_metro = dest_scene.get_metro_scene()
            if dest_metro and dest_metro.metrodat:
                myqol = dest_metro.metrodat.get_quality_of_life()
                myrank += myqol.defense * 10
            myadv = missionbuilder.BuildAMissionSeed(
                camp, "{} Militia".format(dest_scene), metroscene, return_wp,
                enemy_faction=dest_scene.faction, rank=myrank,
                objectives=(missionbuilder.BAMO_DEFEAT_COMMANDER,),
                adv_type="BAM_ROAD_MISSION",
                custom_elements={"ADVENTURE_GOAL": dest_wp, "DEST_SCENE": dest_scene, "ENTRANCE_ANCHOR": myanchor},
                scenegen=scenegen,
                architecture=architecture(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
                cash_reward=0,
                mission_grammar=missionbuilder.MissionGrammar(
                    objective_ep="keep you out of {}".format(dest_scene),
                    win_pp="I got past your militia",
                    win_ep="you fought your way into {}".format(dest_scene),
                    lose_pp="you stopped me from entering {}".format(dest_scene),
                    lose_ep="I drove you out of {}".format(dest_scene)
                )
            )
            myadv.priority = 50
            myadv.mandatory = True
            return myadv


class MetrosceneRandomPlotHandler(Plot):
    # Keep this metro area stocked with random plots.
    # Set the element "USE_PLOT_RANK" to True to keep the rank of local plots tied to the plot rank
    LABEL = "CF_METROSCENE_RANDOM_PLOT_HANDLER"
    active = True
    scope = "METRO"

    MAX_PLOTS = 5
    SUBPLOT_LABEL = "RANDOM_PLOT"
    CHALLENGE_LABEL = "CHALLENGE_PLOT"
    ALL_RANDOM_PLOT_TYPES = (SUBPLOT_LABEL, CHALLENGE_LABEL)

    def custom_init(self, nart):
        self.adv = pbge.plots.Adventure(name="Plot Handler")
        return True

    def t_START(self, camp):
        # Attempt to load at least one challenge plot, then load some more plots.
        if self.should_load_plot(camp):
            game.content.load_dynamic_plot(
                camp, self.CHALLENGE_LABEL, pstate=PlotState(
                    rank=self.calc_rank(camp)
                ).based_on(self)
            )
        tries = 10
        while self.should_load_plot(camp) and tries > 0:
            myplot = game.content.load_dynamic_plot(
                camp, self.SUBPLOT_LABEL, pstate=PlotState(
                    rank=self.calc_rank(camp)
                ).based_on(self)
            )
            tries -= 1
            if not myplot:
                print("Warning: No plot found for {}".format(self.SUBPLOT_LABEL))
                self._resolve_unfound_plot(camp)
                break

    def _resolve_unfound_plot(self, camp):
        # Do whatever needs to be done when a plot could not be found. Not used here, but might get used in subclasses.
        pass

    def should_load_plot(self, camp):
        mymetro: gears.MetroData = self.elements["METRO"]
        lp = len([p for p in mymetro.scripts if p.LABEL in self.ALL_RANDOM_PLOT_TYPES])
        return lp < self.MAX_PLOTS

    def calc_rank(self, camp: gears.GearHeadCampaign):
        if self.elements.get("USE_PLOT_RANK", False):
            # If the player's renown is higher than this plot rank, adjust things upward, but not all the way.
            return max(self.rank, (camp.renown + self.rank) // 2)
        else:
            return camp.renown


#  *****************************
#  ***   WORLD  MAP  STUFF   ***
#  *****************************

class WorldMapNode:
    def __init__(self, pos=(0, 0), visible=False, discoverable=True, image_file="wm_legend_default.png", on_frame=1,
                 off_frame=11, destination=None, entrance=None):
        self.pos = pos
        self.visible = visible
        self.discoverable = discoverable
        self.image_file = image_file
        self.on_frame = on_frame
        self.off_frame = off_frame
        self.destination = destination
        self.entrance = entrance

    def __str__(self):
        return str(self.destination)


class WorldMapEdge:
    STYLE_SAFE = 1
    STYLE_RED = 2
    STYLE_ORANGE = 3
    STYLE_YELLOW = 4
    STYLE_BLOCKED = 5

    def __init__(self, start_node=None, end_node=None, visible=False, discoverable=True,
                 architecture=gharchitecture.MechaScaleSemiDeadzone, style=1, encounter_chance=50):
        self.start_node = start_node
        self.end_node = end_node
        self.visible = visible
        self.discoverable = discoverable
        self.path = list()
        self.architecture = architecture
        self.style = style
        self.encounter_chance = encounter_chance

    def get_link(self, node_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if node_a is self.start_node:
            return self.end_node
        elif node_a is self.end_node:
            return self.start_node

    def get_city_link(self, city_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if city_a is self.start_node.destination:
            return self.end_node.destination
        elif city_a is self.end_node.destination:
            return self.start_node.destination

    def connects_to_node(self, some_node):
        return some_node is self.start_node or some_node is self.end_node

    def connects_to_city(self, some_city):
        return some_city is self.start_node.destination or some_city is self.end_node.destination

    def connects_to_entrance(self, some_entrance):
        return some_entrance is self.start_node.entrance or some_entrance is self.end_node.entrance

    def go_to_end_node(self, camp):
        camp.go(self.end_node.entrance)

    def go_to_start_node(self, camp):
        camp.go(self.start_node.entrance)


class EdgeTravel():
    def __init__(self, edge: WorldMapEdge, start_point: WorldMapNode):
        self.edge = edge
        self.start_point = start_point

    def __call__(self, camp: gears.GearHeadCampaign):
        if self.edge.architecture and camp.has_mecha_party(enviro=self.edge.architecture.ENV):
            dest_node = self.edge.get_link(self.start_point)
            wmehandler = camp.campdata.get(WORLD_MAP_ENCOUNTERS)

        else:
            pass

class WorldMap(object):
    def __init__(self, image_file):
        self.nodes = list()
        self.edges = list()

        myimage = pbge.image.Image(image_file)
        self.px_width = myimage.frame_width
        self.px_height = myimage.frame_height
        self.width = myimage.frame_width // 32
        self.height = myimage.frame_height // 32

    def add_node(self, node_to_add, x, y):
        self.nodes.append(node_to_add)
        node_to_add.pos = (min(max(0, x), self.width - 1), min(max(0, y), self.height - 1))

    def connect_nodes(self, start_node, end_node, edge_to_use):
        self.edges.append(edge_to_use)
        edge_to_use.start_node = start_node
        edge_to_use.end_node = end_node
        edge_to_use.path = pbge.scenes.animobs.get_line(start_node.pos[0], start_node.pos[1], end_node.pos[0],
                                                        end_node.pos[1])

    def expand_roadmap_menu(self, camp, mymenu):
        # Determine which edges connect here.
        my_edges = [e for e in self.edges if e.get_link(mymenu.waypoint.node) and (e.visible or e.discoverable)]
        for e in my_edges:
            mydest = e.get_link(mymenu.waypoint.node)
            e.visible = True
            mydest.visible = True
            mymenu.add_item("Go to {}".format(mydest), e.get_menu_fun(camp, mydest), e)


class WorldMapMenu(pbge.rpgmenu.Menu):
    WIDTH = 640
    HEIGHT = 320
    MAP_AREA = pbge.frects.Frect(-320, -210, 640, 320)
    MENU_AREA = pbge.frects.Frect(-200, 130, 400, 80)

    def __init__(self, camp, wp):
        super().__init__(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h, border=None,
                         predraw=self.pre)
        self.desc = wp.desc
        self.waypoint = wp
        self.map_sprite = pbge.image.Image("dzd_roadmap.png")
        self.legend_sprite = pbge.image.Image("dzd_roadmap_legend.png", 20, 20)
        self.road_sprite = pbge.image.Image("dzd_roadmap_roads.png", 34, 34)
        self.text_labels = dict()

    def _calc_map_x(self, x, map_rect):
        return x * 32 + 16 + map_rect.x

    def _calc_map_y(self, y, map_rect):
        return y * 32 + 16 + map_rect.y

    def _get_text_label(self, mynode):
        if mynode in self.text_labels:
            return self.text_labels[mynode]
        else:
            mylabel = pbge.SMALLFONT.render(str(mynode), True, (0, 0, 0))
            self.text_labels[mynode] = mylabel
            return mylabel

    EDGEDIR = {
        (-1, -1): 0, (0, -1): 1, (1, -1): 2,
        (-1, 0): 3, (1, 0): 4,
        (-1, 1): 5, (0, 1): 6, (1, 1): 7
    }

    def _draw_edge(self, myedge, map_rect, hilight=False):
        a = myedge.path[0]
        if hilight:
            style = 0
        else:
            style = myedge.style
        for b in myedge.path[1:]:
            center_x = (self._calc_map_x(a[0], map_rect) + self._calc_map_x(b[0], map_rect)) // 2
            center_y = (self._calc_map_y(a[1], map_rect) + self._calc_map_y(b[1], map_rect)) // 2
            frame = self.EDGEDIR.get((b[0] - a[0], b[1] - a[1]), 0) + style * 8
            self.road_sprite.render_c((center_x, center_y), frame)
            a = b

    def pre(self):
        if pbge.my_state.view:
            pbge.my_state.view()
        pbge.default_border.render(self.MENU_AREA.get_rect())
        my_map_rect = self.MAP_AREA.get_rect()
        self.map_sprite.render(my_map_rect, 0)
        active_item_edge = self.get_current_item().desc

        for myedge in self.waypoint.roadmap.edges:
            if myedge.visible and myedge is not active_item_edge:
                self._draw_edge(myedge, my_map_rect)
        if active_item_edge:
            self._draw_edge(active_item_edge, my_map_rect, True)

        for mynode in self.waypoint.roadmap.nodes:
            dest = (self._calc_map_x(mynode.pos[0], my_map_rect), self._calc_map_y(mynode.pos[1], my_map_rect))
            if mynode.visible:
                if (active_item_edge and active_item_edge.connects_to(mynode)) or (mynode.entrance is self.waypoint):
                    self.legend_sprite.render_c(dest, mynode.frame)
                else:
                    self.legend_sprite.render_c(dest, mynode.frame + 10)
                mylabel = self._get_text_label(mynode)
                texdest = mylabel.get_rect(center=(dest[0], dest[1] + 16))
                pbge.my_state.screen.blit(mylabel, texdest.clamp(my_map_rect))

        pbge.notex_border.render(self.MAP_AREA.get_rect())
        # pbge.draw_text( pbge.my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify = 0 )


class WorldMapHandler(Plot):
    LABEL = "CF_WORLD_MAP_HANDLER"
    active = True
    scope = True

    def custom_init(self, nart):
        return True

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        super().modify_puzzle_menu(camp, thing, thingmenu)
