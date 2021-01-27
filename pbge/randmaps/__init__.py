import pygame
import random
from .. import scenes
import math
from .. import container

from . import plasma
from . import anchors
from . import mutator
from . import decor
from . import gapfiller
from . import converter
from . import prep
from . import rooms
from .rooms import Room
from . import architect
from . import terrset


# A scene is constructed in the following steps:
# - The scene calls its PREPARE to initialize the map.
# - The child rooms are arranged; descendants are handled recursively
# - The child rooms are connected; descendants are handled recursively
# - The MUTATE attribute is called; descendants are mutated recursively
# - The render method is called; descendants are handled recursively
# - The WALL_FILTER attribute is called
# - The terrain is validated
# - Map contents are deployed; descendants are handled recursively
# - The DECORATE attribute is called; descendants are handled recursively
# - The contents of the map are cleaned

# Scene/Room options
#  GAPFILL*
#  MUTATE*
#  DECORATE*
#  DEFAULT_ROOM*
#  WALL_FILTER*
#  PREPARE*


#  *****************************
#  ***   SCENE  GENERATORS   ***
#  *****************************

class SceneGenerator( Room ):
    """The blueprint for a scene."""
    #DEFAULT_ROOM = rooms.FuzzyRoom
    def __init__( self, myscene, archi, default_room=None, gapfill=None, mutate=None, decorate=None ):
        super(SceneGenerator,self).__init__( myscene.width, myscene.height )
        self.gb = myscene
        self.area = pygame.Rect(0,0,myscene.width,myscene.height)
        self.archi = archi
        self.contents = myscene.contents
        if default_room:
            self.DEFAULT_ROOM = default_room
        if gapfill:
            self.GAPFILL = gapfill
        if mutate:
            self.MUTATE = mutate
        if decorate:
            self.DECORATE = decorate
        self.edge_positions = list(anchors.EDGES)
        random.shuffle((self.edge_positions))


    def make( self ):
        """Assemble this stuff into a real map."""
        # Conduct the five steps of building a level.
        self.archi.prepare( self ) # Only the scene generator gets to prepare
        self.step_two( self.gb ) # Arrange contents for self, then children
        self.step_three( self.gb, self.archi ) # Connect contents for self, then children
        self.step_four( self.gb ) # Mutate for self, then children
        self.step_five( self.gb, self.archi ) # Render for self, then children

        # Convert undefined walls to real walls.
        self.archi.wall_converter( self )
        #self.gb.validate_terrain()

        self.step_six( self.gb ) # Deploy for self, then children

        # Decorate for self, then children
        if self.archi and self.archi.decorate:
            self.archi.decorate(self.gb,self)
        self.step_seven( self.gb )

        self.clean_contents()

        return self.gb

    def clean_contents( self ):
        # Remove unimportant things from the contents.
        for t in self.gb.contents[:]:
            if not hasattr( t, "pos" ):
                self.gb.contents.remove( t )
                if isinstance( t, scenes.Scene ):
                    self.gb.sub_scenes.append( t )
                #elif isinstance( t, Room ):
                #    self.gb.sub_scenes.append( t )
        if self.gb.container and isinstance(self.gb.container,scenes.Scene) and self.gb in self.gb.container.contents:
            myscene = self.gb.container
            myscene.contents.remove(self.gb)
            myscene.sub_scenes.append(self.gb)

CITY_GRID_ROAD_OVERLAP = "Overlap the Road, Y'All!"

class CityGridGenerator(SceneGenerator):
    def __init__( self, myscene, archi, road_terrain, road_thickness=3, **kwargs ):
        super(CityGridGenerator,self).__init__( myscene,archi,**kwargs )
        self.road_terrain = road_terrain
        self.road_thickness = road_thickness
    def arrange_contents( self, gb ):
        # Step Two: Arrange subcomponents within this area.
        closed_area = list()
        # Add already placed rooms to the closed_area list.
        for r in self.contents:
            if hasattr( r, "area" ) and r.area:
                closed_area.append( r.area )
        # Add rooms with defined anchors next
        for r in self.contents:
            if hasattr( r, "anchor" ) and r.anchor and hasattr(r,"area"):
                myrect = pygame.Rect( 0, 0, r.width, r.height )
                r.anchor( self.area, myrect )
                if myrect.collidelist( closed_area ) == -1:
                    r.area = myrect
                    closed_area.append( myrect )

        # Next we're gonna draw the road grid. I know that drawing is usually saved for near the end, but eff
        # that, I'm the programmer. I can do whatever I like.
        blocks = list()
        column_info = list()
        x = random.randint(2,4)
        while x < (self.width - self.road_thickness):
            # Draw a N-S road here.
            self.fill(self.gb,pygame.Rect(x,0,self.road_thickness,self.height),floor=self.road_terrain)
            room_width = random.randint(7,12)
            if x + room_width + self.road_thickness < self.width:
                column_info.append((x+self.road_thickness,room_width))
            x += self.road_thickness + room_width

        y = random.randint(2,4)
        while y < (self.height - self.road_thickness - 7):
            # Draw a W-E road here.
            self.fill(self.gb,pygame.Rect(0,y,self.width,self.road_thickness),floor=self.road_terrain)
            room_height = random.randint(7,12)
            # Add the rooms.
            for col_x,col_width in column_info:
                myroom = pygame.Rect(col_x,y+self.road_thickness,col_width,room_height)
                if self.area.contains(myroom):
                    blocks.append(myroom)
            y += self.road_thickness + room_height

        # Assign areas for unplaced rooms.
        for r in self.contents:
            if hasattr( r, "area" ) and not r.area:
                if blocks:
                    myblock = random.choice(blocks)
                    blocks.remove(myblock)
                    if CITY_GRID_ROAD_OVERLAP in r.tags:
                        myblock.x -= 2
                        myblock.y -= 2
                        myblock.w += 2
                        myblock.h += 2
                    r.area = myblock
                else:
                    raise rooms.RoomError( "ROOM ERROR: {}:{} has no block for {}".format(str(self),str( self.__class__ ),str(r)) )


    def connect_contents( self, gb, archi ):
        pass


class PackedBuildingGenerator(SceneGenerator):
    def put_room_north(self,closed_room,open_room):
        open_room.midbottom = closed_room.midtop
        open_room.y -= 1
        open_room.clamp_ip(self.area)
    def put_room_south(self,closed_room,open_room):
        open_room.midtop = closed_room.midbottom
        open_room.y += 1
        open_room.clamp_ip(self.area)
    def put_room_west(self,closed_room,open_room):
        open_room.midright = closed_room.midleft
        open_room.x -= 1
        open_room.clamp_ip(self.area)
    def put_room_east(self,closed_room,open_room):
        open_room.midleft = closed_room.midright
        open_room.x += 1
        open_room.clamp_ip(self.area)

    def arrange_contents( self, gb ):
        # Step Two: Arrange subcomponents within this area.
        closed_area = list()
        # Add already placed rooms to the closed_area list.
        for r in self.contents:
            if hasattr( r, "area" ) and r.area:
                closed_area.append( r.area )
        # Add rooms with defined anchors next
        for r in self.contents:
            if hasattr( r, "anchor" ) and r.anchor and hasattr(r,"area"):
                myrect = pygame.Rect( 0, 0, r.width, r.height )
                r.anchor( self.area, myrect )
                if myrect.collidelist( closed_area ) == -1:
                    r.area = myrect
                    closed_area.append( myrect )

        # Assign areas for unplaced rooms.
        positions = (self.put_room_east,self.put_room_north,self.put_room_south,self.put_room_west)
        rooms_to_add = [r for r in self.contents if hasattr( r, "area" ) and not r.area]
        random.shuffle(rooms_to_add)
        for r in rooms_to_add:
            myrect = pygame.Rect( 0, 0, r.width, r.height )
            candidates = list()
            for croom in closed_area:
                for dirf in positions:
                    dirf(croom,myrect)
                    if myrect.inflate(2,2).collidelist( closed_area ) == -1:
                        candidates.append((dirf,croom))
            if candidates:
                dirf,croom = random.choice(candidates)
                dirf(croom,myrect)
                r.area = myrect
                closed_area.append(myrect)
            else:
                raise rooms.RoomError("ROOM ERROR: {}:{} cannot place {}".format(str(self), str(self.__class__), str(r)))

    def connect_contents( self, gb, archi ):
        # Step Three: Connect all rooms in contents, making trails on map.

        # Generate list of rooms.
        connected = list()
        unconnected = [r for r in self.contents if hasattr(r,"area")]
        if unconnected:
            room1 = random.choice(unconnected)
            unconnected.remove(room1)
            connected.append(room1)
            unconnected.sort( key=room1.find_distance_to )

        # Process them
        for r in unconnected:
            # Connect r to a connected room
            croom = min(connected,key=r.find_distance_to)
            self.draw_L_connection( gb, r.area.centerx, r.area.centery, croom.area.centerx, croom.area.centery, archi )
            connected.append(r)

    def thin_draw_direct_connection( self, gb, x1,y1,x2,y2, archi ):
        # Paths between rooms will only be one block wide.
        path = scenes.animobs.get_line( x1,y1,x2,y2 )
        for p in path:
            archi.draw_fuzzy_ground( gb, p[0], p[1] )

