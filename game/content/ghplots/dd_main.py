import gears
from pbge.plots import Plot, Adventure, NarrativeRequest, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import pbge
from pbge.dialogue import Offer,ContextTag
from game import teams,ghdialogue
from game.ghdialogue import context
import pygame
import random
import game.content.ghplots.tarot_cards
import game.content.mechtarot
import game.content.plotutility
import game.content.gharchitecture
from game.content.ghwaypoints import Exit
from game.content import PLOT_LIST

# Room tags
ON_THE_ROAD = "ON_THE_ROAD" # This location is connected to the highway, if appropriate.

class DeadzoneDrifterStub( Plot ):
    LABEL = "SCENARIO_DEADZONEDRIFTER"
    active = True
    scope = True
    # Creates a DeadZone Drifter adventure.
    # - Start by creating the "home base" city that the player character will leave from.

    def custom_init( self, nart ):
        """Create the intro/tutorial."""
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_INTRO", ident="INTRO" )

        # Copy over the sheriff and the name of the town
        self.register_element("DZ_CONTACT",wplot.elements["SHERIFF"])
        self.register_element("DZ_TOWN_NAME",wplot.elements["DZ_TOWN_NAME"])

        mymap = self.register_element("DZ_ROADMAP",RoadMap())
        mymap.initialize_plots(self,nart)

        # Add Wujung and the rest of the world.
        #self.add_sub_plot(nart,"DZD_HOME_BASE",ident="HOMEBASE")

        return True

    def _get_generic_offers( self, npc, camp ):
        """

        :type camp: gears.GearHeadCampaign
        :type npc: gears.base.Character
        """
        mylist = list()
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            if camp.can_add_lancemate() and npc not in camp.party:
                # If the NPC has the lancemate tag, they might join the party.
                if npc.relationship.data.get("DZD_LANCEMATE_TIME_OFF",0) <= camp.day:
                    mylist.append(Offer("[JOIN]",
                                        context=ContextTag([context.JOIN]), effect=game.content.plotutility.AutoJoiner(npc)))
                else:
                    # This NPC is taking some time off. Come back tomorrow.
                    mylist.append(Offer("[COMEBACKTOMORROW_JOIN]",
                                        context=ContextTag([context.JOIN])))
            elif npc in camp.party and gears.tags.SCENE_PUBLIC in camp.scene.attributes:
                mylist.append(Offer("[LEAVEPARTY]",
                                    context=ContextTag([context.LEAVEPARTY]), effect=game.content.plotutility.AutoLeaver(npc)))

        return mylist

    def t_INTRO_END(self, camp):
        # Wujung should be registered as the home base, so send the player there.
        camp.destination,camp.entrance = camp.home_base
        npc = self.elements["DZ_CONTACT"]
        npc.place(camp.campdata["DISTANT_TOWN"],team=camp.campdata["DISTANT_TEAM"])

        del self.subplots["INTRO"]

    def t_START(self,camp):
        camp.check_trigger("UPDATE")


class RoadNode(object):
    # A node in the RoadMap graph; represents a town or other visitable location.
    # The sub plot loaded by a node gets the DZ_ROADMAP and DZ_NODE elements, and must define
    # its own LOCALE and ENTRANCE elements.
    FRAME_WUJUNG = 0
    FRAME_TOWN = 1
    FRAME_VILLAGE = 2
    FRAME_DISTANT_TOWN = 3
    FRAME_MINE = 4
    FRAME_DANGER = 5
    def __init__(self, sub_plot_label,sub_plot_ident=None,pos=(0,0),visible=False,discoverable=True,frame=1):
        self.sub_plot_label = sub_plot_label
        self.sub_plot_ident = sub_plot_ident
        self.pos = pos
        self.visible=visible
        self.discoverable = discoverable
        self.frame = frame
        self.destination = None
        self.entrance = None
    def __str__(self):
        return str(self.destination)


class RoadEdge(object):
    # The sub plot loaded by an edge gets the DZ_ROADMAP and DZ_EDGE elements.
    STYLE_SAFE = 1
    STYLE_RED = 2
    STYLE_ORANGE = 3
    STYLE_YELLOW = 4
    STYLE_BLOCKED = 5
    def __init__(self,start_node=None,end_node=None,sub_plot_label=None,sub_plot_ident=None, visible=False, discoverable=True, style=1):
        self.start_node = start_node
        self.end_node = end_node
        self.sub_plot_label = sub_plot_label
        self.sub_plot_ident = sub_plot_ident
        self.visible = visible
        self.discoverable = discoverable
        self.path = list()
        self.style = style
        self.eplot = None
    def get_link(self,node_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if node_a is self.start_node:
            return self.end_node
        elif node_a is self.end_node:
            return self.start_node
    def get_city_link(self,city_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if city_a is self.start_node.destination:
            return self.end_node.destination
        elif city_a is self.end_node.destination:
            return self.start_node.destination
    def connects_to(self,some_node):
        return some_node is self.start_node or some_node is self.end_node
    def connects_to_city(self,some_city):
        return some_city is self.start_node.destination or some_city is self.end_node.destination
    def get_menu_fun(self,camp,node_a):
        if self.eplot:
            myadv = self.eplot.get_road_adventure(camp,node_a)
            if myadv:
                return myadv
        if node_a is self.start_node:
            return self.go_to_start_node
        else:
            return self.go_to_end_node
    def go_to_end_node(self,camp):
        camp.destination,camp.entrance = self.end_node.destination,self.end_node.entrance
    def go_to_start_node(self,camp):
        camp.destination,camp.entrance = self.start_node.destination,self.start_node.entrance

class RoadMap(object):
    MAP_WIDTH = 20
    MAP_HEIGHT = 10
    def __init__(self,):
        self.nodes = list()
        self.edges = list()
        self.start_node = RoadNode("DZD_DISTANT_TOWN","GOALTOWN",visible=True,frame=RoadNode.FRAME_DISTANT_TOWN)
        self.add_node(self.start_node,random.randint(3,4),random.randint(2,7))


        self.end_node = RoadNode("DZD_HOME_BASE","HOMEBASE",visible=True,frame=RoadNode.FRAME_WUJUNG)
        self.add_node(self.end_node,self.MAP_WIDTH-1,self.MAP_HEIGHT//2-1)

        north_road = list()
        north_edges = list()
        prev = self.start_node
        ys = list(range(0,4))
        random.shuffle(ys)
        for t in range(3):
            north_road.append(RoadNode("DZD_ROADSTOP",visible=False))
            self.add_node(north_road[-1],t*4+random.randint(5,7),ys[t])
            new_edge = RoadEdge()
            self.connect_nodes(prev,north_road[-1],new_edge)
            north_edges.append(new_edge)
            prev = north_road[-1]
        self.connect_nodes(prev,self.end_node,RoadEdge())

        south_road = list()
        south_edges = list()
        prev = self.start_node
        ys = list(range(5,9))
        random.shuffle(ys)
        for t in range(3):
            south_road.append(RoadNode("DZD_ROADSTOP",visible=False))
            self.add_node(south_road[-1],t*4+random.randint(5,7),ys[t])
            new_edge = RoadEdge()
            self.connect_nodes(prev,south_road[-1],new_edge)
            south_edges.append(new_edge)
            prev = south_road[-1]
        self.connect_nodes(prev,self.end_node,RoadEdge())

        cross_road = RoadEdge()
        self.connect_nodes(random.choice(north_road),random.choice(south_road),cross_road)

        # At this point we have all the main locations joined. Gonna sort roads according to "westerliness"
        # and assign difficulty ratings based on that.
        sorted_edges = list(self.edges)
        random.shuffle(sorted_edges)    # Why shuffle before sort? So that if two edges have identical scores, one won't be favored over the other.
        sorted_edges.sort(key=lambda e: e.start_node.pos[0] + e.end_node.pos[0])
        for edg in sorted_edges:
            if sorted_edges.index(edg) < max(len(sorted_edges)//3,2):
                edg.style = RoadEdge.STYLE_RED
                edg.sub_plot_label = "DZD_ROADEDGE_RED"
            elif sorted_edges.index(edg) < len(sorted_edges)*2//3:
                edg.style = RoadEdge.STYLE_ORANGE
                edg.sub_plot_label = "DZD_ROADEDGE_ORANGE"
            else:
                edg.style = RoadEdge.STYLE_YELLOW
                edg.sub_plot_label = "DZD_ROADEDGE_YELLOW"

        # The Kerberos plot always happens on one of the two roads leading into the goal town.
        k_edge = random.choice((north_edges[0],south_edges[0]))
        k_edge.sub_plot_label = "DZD_ROADEDGE_KERBEROS"


    def add_node(self,node_to_add,x,y):
        self.nodes.append(node_to_add)
        node_to_add.pos = (min(max(0,x),self.MAP_WIDTH-1),min(max(0,y),self.MAP_HEIGHT-1))

    def connect_nodes(self,start_node, end_node, edge_to_use):
        self.edges.append(edge_to_use)
        edge_to_use.start_node = start_node
        edge_to_use.end_node = end_node
        edge_to_use.path = pbge.scenes.animobs.get_line(start_node.pos[0],start_node.pos[1],end_node.pos[0],end_node.pos[1])

    def connection_is_made(self):
        # Sooner or later.
        # Return True if there's a STYLE_SAFE connection from self.start_node to self.end_node
        visited_nodes = set()
        frontier = [edge.end_node for edge in self.edges if edge.start_node is self.start_node and edge.style is edge.STYLE_SAFE]
        while frontier:
            nu_start = frontier.pop()
            visited_nodes.add(nu_start)
            frontier += [edge.end_node for edge in self.edges if edge.end_node not in visited_nodes and
                        edge.start_node is nu_start and edge.style is edge.STYLE_SAFE]
        return self.end_node in visited_nodes

    def initialize_plots(self,plot,nart):
        """

        :type plot: Plot
        """
        ok = True
        towns = list()
        for n in self.nodes:
            if n.sub_plot_label:
                ok = plot.add_sub_plot(nart,n.sub_plot_label,ident=n.sub_plot_ident,spstate=PlotState(rank=60-n.pos[0]*3,elements={"DZ_NODE":n}).based_on( plot ))
                if ok:
                    n.destination = ok.elements["LOCALE"]
                    n.entrance = ok.elements["ENTRANCE"]
                    if "DZ_NODE_FRAME" in ok.elements:
                        n.frame = ok.elements["DZ_NODE_FRAME"]
                    towns.append(n)
                else:
                    break
        for e in self.edges:
            if e.sub_plot_label:
                ok = plot.add_sub_plot(nart,e.sub_plot_label,ident=e.sub_plot_ident,spstate=PlotState(elements={"DZ_EDGE":e}).based_on( plot ))
                if ok:
                    e.eplot = ok
                    if "DZ_EDGE_STYLE" in ok.elements:
                        e.style = ok.elements["DZ_EDGE_STYLE"]
                else:
                    break
        if towns:
            towns.sort(key=lambda x: x.pos[0])
            mytown = towns[min(random.randint(1,len(towns)-2),random.randint(1,len(towns)-2))]
            plot.add_sub_plot(nart, "DZD_MAGNUSMECHA",
                              elements={"METROSCENE": mytown.destination, "METRO": mytown.destination.metrodat})
        return ok

    def expand_roadmap_menu(self, camp, mymenu):
        # Determine which edges connect here.
        my_edges = [e for e in self.edges if e.get_link(mymenu.waypoint.node) and (e.visible or e.discoverable)]
        for e in my_edges:
            mydest = e.get_link(mymenu.waypoint.node)
            e.visible = True
            mydest.visible = True
            mymenu.add_item("Go to {}".format(mydest),e.get_menu_fun(camp,mydest),e)

class DZDRoadMapMenu(pbge.rpgmenu.Menu):
    WIDTH = 640
    HEIGHT = 320
    MAP_AREA = pbge.frects.Frect(-320,-210,640,320)
    MENU_AREA = pbge.frects.Frect(-200,130,400,80)
    def __init__(self,camp,wp):
        super(DZDRoadMapMenu, self).__init__(self.MENU_AREA.dx,self.MENU_AREA.dy,self.MENU_AREA.w,self.MENU_AREA.h,border=None,predraw=self.pre)
        self.desc = wp.desc
        self.waypoint = wp
        self.map_sprite = pbge.image.Image("dzd_roadmap.png")
        self.legend_sprite = pbge.image.Image("dzd_roadmap_legend.png",20,20)
        self.road_sprite = pbge.image.Image("dzd_roadmap_roads.png",34,34)
        self.text_labels = dict()

    def _calc_map_x(self,x,map_rect):
        return x*32 + 16 + map_rect.x

    def _calc_map_y(self,y,map_rect):
        return y*32 + 16 + map_rect.y

    def _get_text_label(self,mynode):
        if mynode in self.text_labels:
            return self.text_labels[mynode]
        else:
            mylabel = pbge.SMALLFONT.render(str(mynode), True, (0,0,0) )
            self.text_labels[mynode] = mylabel
            return mylabel

    EDGEDIR = {
        (-1,-1):0, (0,-1): 1, (1,-1): 2,
        (-1,0): 3, (1,0): 4,
        (-1,1): 5, (0,1): 6, (1,1): 7
    }

    def _draw_edge(self,myedge,map_rect,hilight=False):
        a = myedge.path[0]
        if hilight:
            style = 0
        else:
            style = myedge.style
        for b in myedge.path[1:]:
            center_x = (self._calc_map_x(a[0],map_rect) + self._calc_map_x(b[0],map_rect))//2
            center_y = (self._calc_map_y(a[1],map_rect) + self._calc_map_y(b[1],map_rect))//2
            frame = self.EDGEDIR.get((b[0]-a[0],b[1]-a[1]),0) + style * 8
            self.road_sprite.render_c((center_x,center_y),frame)
            a = b


    def pre( self ):
        if pbge.my_state.view:
            pbge.my_state.view()
        pbge.default_border.render( self.MENU_AREA.get_rect() )
        my_map_rect = self.MAP_AREA.get_rect()
        self.map_sprite.render(my_map_rect,0)
        active_item_edge = self.get_current_item().desc

        for myedge in self.waypoint.roadmap.edges:
            if myedge.visible and myedge is not active_item_edge:
                self._draw_edge(myedge,my_map_rect)
        if active_item_edge:
            self._draw_edge(active_item_edge,my_map_rect,True)

        for mynode in self.waypoint.roadmap.nodes:
            dest = (self._calc_map_x(mynode.pos[0],my_map_rect),self._calc_map_y(mynode.pos[1],my_map_rect))
            if mynode.visible:
                if (active_item_edge and active_item_edge.connects_to(mynode)) or (mynode.entrance is self.waypoint):
                    self.legend_sprite.render_c(dest,mynode.frame)
                else:
                    self.legend_sprite.render_c(dest,mynode.frame+10)
                mylabel = self._get_text_label(mynode)
                texdest = mylabel.get_rect(center=(dest[0],dest[1]+16))
                pbge.my_state.screen.blit(mylabel,texdest.clamp(my_map_rect))

        pbge.notex_border.render( self.MAP_AREA.get_rect() )
        #pbge.draw_text( pbge.my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify = 0 )


class DZDRoadMapExit(Exit):
    MENU_CLASS = DZDRoadMapMenu
    def __init__( self, roadmap, node, **kwargs ):
        self.roadmap = roadmap
        self.node = node
        super(DZDRoadMapExit,self).__init__(**kwargs)

    def unlocked_use( self, camp ):
        rpm = self.MENU_CLASS(camp, self)

        # Add the roadmap menu items
        self.roadmap.expand_roadmap_menu(camp,rpm)

        # Add the plot-linked menu items
        camp.expand_puzzle_menu(self, rpm)
        rpm.add_item("[Cancel]",None)
        fx = rpm.query()
        if fx:
            camp.day += 1
            fx(camp)

    def bump( self, camp, pc ):
        # Send a BUMP trigger.
        camp.check_trigger("BUMP",self)
        # This waypoint doesn't care about plot locking; it's always plot locked.
        self.unlocked_use( camp )


# Stuff from older versions of the DZD setup... keeping them here because I might use them later.

class DeadzoneHighwaySceneGen( pbge.randmaps.SceneGenerator ):
    DO_DIRECT_CONNECTIONS = False
    def connect_contents( self, gb, archi ):
        # Generate list of rooms.
        all_rooms = [r for r in self.contents if hasattr(r,"area")]
        road_rooms = list()
        side_rooms = list()
        for r in all_rooms:
            if ON_THE_ROAD in r.tags:
                road_rooms.append(r)
            else:
                side_rooms.append(r)

        random.shuffle(road_rooms)
        connected = list()
        connected.append( road_rooms.pop() )
        road_rooms.sort(key=lambda r: gb.distance(r.area.center,connected[0].area.center))

        room = connected[0]
        if room.anchor:
            mydest = room.anchor(room.area,None)
            self.draw_L_connection( gb, room.area.centerx, room.area.centery, mydest[0], mydest[1], archi )

        # Process them
        for room in list(road_rooms):
            road_rooms.remove(room)
            dest = min(connected, key=lambda r: gb.distance(r.area.center,room.area.center))
            self.draw_L_connection( gb, room.area.centerx, room.area.centery, dest.area.centerx, dest.area.centery, archi )
            connected.append(room)
            if room.anchor:
                mydest = room.anchor(room.area, None)
                self.draw_L_connection(gb, room.area.centerx, room.area.centery, mydest[0], mydest[1], archi)

        for room in side_rooms:
            dest = random.choice(connected)
            self.draw_direct_connection(gb,room.area.centerx, room.area.centery, dest.area.centerx, dest.area.centery, archi )
            connected.append(room)

    def draw_L_connection( self, gb, x1,y1,x2,y2, archi ):
        if random.randint(1,2) == 1:
            cx,cy = x1,y2
        else:
            cx,cy = x2,y1
        self.draw_road_connection( gb, x1, y1, cx, cy, archi )
        self.draw_road_connection( gb, x2, y2, cx, cy, archi )

    def draw_road_connection( self, gb, x1,y1,x2,y2, archi ):
        path = pbge.scenes.animobs.get_line( x1,y1,x2,y2 )
        for p in path:
            gb.fill(pygame.Rect(p[0]-1,p[1]-1,3,3), floor=game.content.ghterrain.DeadZoneGround, wall=None)
            gb.set_decor(p[0], p[1], game.content.ghterrain.WorldMapRoad)


class SomewhereOnTheHighway( Plot ):
    LABEL = "DZD_WORLD"
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30,30,"Deadzone Highway",player_team=team1,scale=gears.scale.WorldScale)
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        anc_a,anc_b = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        myscenegen = DeadzoneHighwaySceneGen(myscene, game.content.gharchitecture.WorldScaleDeadzone())

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5,tags=(ON_THE_ROAD),anchor=anc_a),dident="LOCALE")
        mydest = self.register_element("_ROOM2",pbge.randmaps.rooms.FuzzyRoom(3,3,tags=(ON_THE_ROAD,),anchor=anc_b),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_ROOM")
        myexit = self.register_element( "EXIT", game.content.ghwaypoints.Exit(name="Exit Scenario", anchor=pbge.randmaps.anchors.middle), dident="_ROOM2")
        return True


class BasicDeadZoneHighwayTown( Plot ):
    LABEL = "DZD_VILLAGE"

    # noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",allies=(team1,))
        myscene = gears.GearHeadScene(50,50,"DZ Village",player_team=team1,civilian_team=team2,
                                      scale=gears.scale.HumanScale,
                                      attributes=(gears.personality.DeadZone,gears.tags.Village))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50,local_tags=myscene.attributes)
        npc.place(myscene,team=team2)

        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.HumanScaleDeadzone())

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        #myscene.contents.append(ghterrain.ScrapIronBuilding(waypoints={"DOOR":ghwaypoints.ScrapIronDoor(),"OTHER":ghwaypoints.RetroComputer()}))

        wm_con = game.content.plotutility.WMDZTownConnection(self, self.elements["WORLD"], myscene)
        wm_con.room1.tags = (ON_THE_ROAD,)

        return True
