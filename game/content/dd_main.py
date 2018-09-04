import gears
from pbge.plots import Plot, Chapter, PlotState
import waypoints
import ghterrain
import pbge
from .. import teams,ghdialogue
import pygame
import random
import dd_tarot
import mechtarot

# Room tags
ON_THE_ROAD = "ON_THE_ROAD" # This location is connected to the highway, if appropriate.

class DeadzoneDrifterStub( Plot ):
    LABEL = "SCENARIO_DEADZONEDRIFTER"
    # Creates a DeadZone Drifter adventure.
    # - Create a patch of DeadZone to act as the "world"
    # - Add a village, including random cards for village resources
    # - Add a Threat card
    # - Add the defenses and weakness to the Threat
    # -

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        self.chapter = Chapter( world=nart.camp )
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_WORLD" )
        w = wplot.elements.get("LOCALE")
        self.chapter.world = w
        self.register_element( "WORLD", w )
        threat_card = nart.add_tarot_card(self,(dd_tarot.MT_THREAT,),)
        mechtarot.Constellation(nart,self,threat_card,threat_card.get_negations()[0])

        return True


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
            gb.fill(pygame.Rect(p[0]-1,p[1]-1,3,3),floor=ghterrain.DeadZoneGround,wall=None)
            gb.set_decor(p[0],p[1],ghterrain.WorldMapRoad)


class BasicDeadZoneHighwayTown( Plot ):
    LABEL = "DZD_WORLD"
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60,60,"Mauna",player_team=team1,scale=gears.scale.MechaScale)
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        anc_a,anc_b = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        myfilter = pbge.randmaps.converter.BasicConverter(None)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myprep = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,higround=0.8,maxhiground=0.9)
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.DeadZoneGround,myfilter,mutate=mymutate,prepare=myprep)
        myscenegen = DeadzoneHighwaySceneGen(myscene,myarchi)

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5,tags=(ON_THE_ROAD),anchor=anc_a))
        myscenegen.contents.append(myroom)

        mydest = self.register_element("ROOM2",pbge.randmaps.rooms.FuzzyRoom(3,3,tags=(ON_THE_ROAD,),anchor=anc_b))
        myscenegen.contents.append(mydest)

        myent = self.register_element( "ENTRANCE", waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append( myent )

        myexit = self.register_element( "EXIT", waypoints.Exit(name="Exit Scenario",anchor=pbge.randmaps.anchors.middle))
        mydest.contents.append( myexit )
        return True

