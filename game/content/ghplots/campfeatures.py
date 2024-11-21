from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag, Offer
from game.content import plotutility, GHNarrativeRequest, PLOT_LIST, ghwaypoints
import game.content.gharchitecture
from . import missionbuilder
from game.content.plotutility import LMSkillsSelfIntro
import pygame


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

    def can_load_lancedev_plot(self, camp: gears.GearHeadCampaign):
        return not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT) and not camp.has_a_destination()

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
                elif npc.relationship.data.get("LANCEMATE_TIME_OFF", 0) <= camp.time:
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

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        # Combat happens right here in the city? Do recovery right away.
        camp.bring_out_your_dead(True, True)
        self.METROSCENE_ENTER(camp)


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

    def generate_world_map_encounter(self, camp: gears.GearHeadCampaign, metroscene, return_wp, dest_scene, dest_wp,
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

    def t_START(self, camp: gears.GearHeadCampaign):
        # Attempt to load at least one challenge plot, then load some more plots.
        tries = random.randint(2, 5)
        while self.should_load_challenge(camp) and tries > 0:
            myplot = game.content.load_dynamic_plot(
                camp, self.CHALLENGE_LABEL, pstate=PlotState(
                    rank=self.calc_rank(camp)
                ).based_on(self)
            )
            tries -= 1
            if not myplot:
                break
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

        # Attempt to load the test plot.
        if self.should_load_test(camp):
            myplot = game.content.load_dynamic_plot(
                camp, "TEST_RANDOM_PLOT", pstate=PlotState(
                    rank=self.calc_rank(camp)
                ).based_on(self)
            )

    def _resolve_unfound_plot(self, camp):
        # Do whatever needs to be done when a plot could not be found. Not used here, but might get used in subclasses.
        pass

    def should_load_challenge(self, camp):
        mymetro: gears.MetroData = self.elements["METRO"]
        lp = len([p for p in mymetro.scripts if p.LABEL == self.CHALLENGE_LABEL])
        return lp < self.MAX_PLOTS

    def should_load_plot(self, camp):
        mymetro: gears.MetroData = self.elements["METRO"]
        lp = len([p for p in mymetro.scripts if p.LABEL in self.ALL_RANDOM_PLOT_TYPES])
        return lp < self.MAX_PLOTS

    def should_load_test(self, camp):
        mymetro: gears.MetroData = self.elements["METRO"]
        lp = len([p for p in mymetro.scripts if p.LABEL == "TEST_RANDOM_PLOT"])
        return lp < 1

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
                 scenegen=gharchitecture.DeadZoneHighwaySceneGen,
                 architecture=gharchitecture.MechaScaleSemiDeadzone, style=1, encounter_chance=50):
        self.start_node = start_node
        self.end_node = end_node
        self.visible = visible
        self.discoverable = discoverable
        self.scenegen = scenegen
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


class EdgeTravel:
    def __init__(self, edge: WorldMapEdge, start_point: WorldMapNode):
        self.edge = edge
        self.start_point = start_point

    def __call__(self, camp: gears.GearHeadCampaign):
        dest_node = self.edge.get_link(self.start_point)
        if self.edge.architecture and camp.has_mecha_party(enviro=self.edge.architecture.ENV):
            wmehandler = camp.campdata.get(WORLD_MAP_ENCOUNTERS)
            if wmehandler:
                wme = wmehandler(
                    camp, self.start_point.destination, self.start_point.entrance, self.edge.encounter_chance,
                    dest_node.destination, dest_node.entrance, camp.renown,
                    scenegen=self.edge.scenegen,
                    architecture=self.edge.architecture,
                )
                if wme:
                    if not wme(camp):
                        camp.go(dest_node.entrance)
                else:
                    camp.go(dest_node.entrance)
            else:
                camp.go(dest_node.entrance)
        else:
            camp.go(dest_node.entrance)


class WorldMap(object):
    def __init__(self, image_file):
        self.nodes = list()
        self.edges = list()
        self.image_file = image_file

        myimage = pbge.image.Image(image_file)
        self.px_width = myimage.frame_width
        self.px_height = myimage.frame_height
        self.width = myimage.frame_width // 32
        self.height = myimage.frame_height // 32

    def on_the_world_map(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    def add_node(self, node_to_add, x, y):
        self.nodes.append(node_to_add)
        node_to_add.pos = (min(max(0, x), self.width - 1), min(max(0, y), self.height - 1))

    def connect_nodes(self, start_node, end_node, edge_to_use):
        self.edges.append(edge_to_use)
        edge_to_use.start_node = start_node
        edge_to_use.end_node = end_node

    def get_node_with_entrance(self, entrance):
        for n in self.nodes:
            if n.entrance is entrance:
                return n

    def get_node_with_destination(self, destination):
        for n in self.nodes:
            if n.destination is destination:
                return n

    def connect_entrance_to_entrance(self, start_entrance, end_entrance, **kwargs):
        start_node = self.get_node_with_entrance(start_entrance)
        end_node = self.get_node_with_entrance(end_entrance)
        if start_node and end_node:
            self.connect_nodes(start_node, end_node, WorldMapEdge(**kwargs))

    def move_node(self, node, new_pos):
        if node in self.nodes and self.on_the_world_map(new_pos):
            node.pos = new_pos

    def expand_roadmap_menu(self, camp, mymenu):
        # Determine which edges connect here.
        my_edges = [e for e in self.edges if e.get_link(mymenu.waypoint.node) and (e.visible or e.discoverable)]
        for e in my_edges:
            mydest = e.get_link(mymenu.waypoint.node)
            e.visible = True
            mydest.visible = True
            mymenu.add_item("Go to {}".format(mydest), e.get_menu_fun(camp, mydest), e)

    def associate_gate_with_map(self, gate: ghwaypoints.Exit):
        gate.MENU_CLASS = WorldMapMenu
        gate.world_map = self

    def get_node_at_pos(self, pos):
        for node in self.nodes:
            if node.pos == pos:
                return node


class WorldMapViewer:
    def __init__(self, world: WorldMap):
        self.world = world
        self.map_sprite = pbge.image.Image(world.image_file)
        self.legend_sprites = dict()
        self.text_labels = dict()

        self.refresh_node_images()

        self.map_area = pbge.frects.Frect(-world.px_width//2, -world.px_height//2-50, world.px_width, world.px_height)

    def calc_map_x(self, x, map_rect):
        return x * 32 + 16 + map_rect.x

    def calc_map_y(self, y, map_rect):
        return y * 32 + 16 + map_rect.y

    def _draw_edge(self, myedge: WorldMapEdge, map_rect, hilight=False):
        start_x = self.calc_map_x(myedge.start_node.pos[0], map_rect)
        start_y = self.calc_map_y(myedge.start_node.pos[1], map_rect)
        end_x = self.calc_map_x(myedge.end_node.pos[0], map_rect)
        end_y = self.calc_map_y(myedge.end_node.pos[1], map_rect)
        if hilight:
            color = pbge.TEXT_COLOR
        else:
            color = (128, 128, 128)
        pygame.draw.line(pbge.my_state.screen, color, (start_x,start_y), (end_x, end_y), 5)

    def refresh_node_images(self):
        for node in self.world.nodes:
            self.legend_sprites[node] = pbge.image.Image(node.image_file, 20, 20)
            self.text_labels[node] = pbge.SMALLFONT.render(str(node), True, (0, 0, 0))

    def render(self, waypoint=None, active_item_edge=None):
        my_map_rect = self.map_area.get_rect()
        self.map_sprite.render(my_map_rect, 0)

        for myedge in self.world.edges:
            if myedge.visible and myedge is not active_item_edge:
                self._draw_edge(myedge, my_map_rect)
        if active_item_edge:
            self._draw_edge(active_item_edge, my_map_rect, True)

        for mynode in self.world.nodes:
            dest = (self.calc_map_x(mynode.pos[0], my_map_rect), self.calc_map_y(mynode.pos[1], my_map_rect))
            if mynode.visible:
                if (active_item_edge and active_item_edge.connects_to_node(mynode)) or (mynode.entrance is waypoint):
                    self.legend_sprites[mynode].render_c(dest, mynode.on_frame)
                else:
                    self.legend_sprites[mynode].render_c(dest, mynode.off_frame)
                mylabel = self.text_labels[mynode]
                texdest = mylabel.get_rect(center=(dest[0], dest[1] + 16))
                pbge.my_state.screen.blit(mylabel, texdest.clamp(my_map_rect))

        pbge.notex_border.render(my_map_rect)
        # pbge.draw_text( pbge.my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify = 0 )


class WorldMapMenu(pbge.rpgmenu.Menu):
    WIDTH = 640
    HEIGHT = 320
    MENU_AREA = pbge.frects.Frect(-200, 130, 400, 150)

    def __init__(self, camp, wp):
        super().__init__(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h, border=None,
                         predraw=self.pre)
        self.desc = wp.desc
        self.waypoint = wp
        self.map_viewer = WorldMapViewer(self.waypoint.world_map)

    def pre(self):
        if pbge.my_state.view:
            pbge.my_state.view()
        pbge.default_border.render(self.MENU_AREA.get_rect())
        active_item_edge = self.get_current_item().desc

        self.map_viewer.render(self.waypoint, active_item_edge)


class WorldMapHandler(Plot):
    # Elements:
    #   WM_IMAGE_FILE:  The image file to be used for the world map.
    #   WM_IDENTIFIER:  The identifier to be used for this world map in the camp.campdata dict
    LABEL = "CF_WORLD_MAP_HANDLER"
    active = True
    scope = True

    def custom_init(self, nart):
        self.world_map = WorldMap(self.elements["WM_IMAGE_FILE"])
        nart.camp.campdata[self.elements["WM_IDENTIFIER"]] = self.world_map
        return True

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        super().modify_puzzle_menu(camp, thing, thingmenu)
        for node in self.world_map.nodes:
            if node.entrance is thing:
                node.visible = True
                my_edges = [e for e in self.world_map.edges if
                            e.connects_to_node(node) and (e.visible or e.discoverable)]
                for e in my_edges:
                    mydest = e.get_link(node)
                    e.visible = True
                    mydest.visible = True
                    thingmenu.add_item("Go to {}".format(mydest), EdgeTravel(e, node), e)
