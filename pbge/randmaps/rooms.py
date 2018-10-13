from .. import container
import random
import pygame
import math
from ..scenes import animobs

class RoomError( Exception ):
    """Something went wrong during room construction."""
    pass


#  *****************
#  ***   ROOMS   ***
#  *****************

class Room( object ):
    """A Room is an area on the map. This room is nothing but an area."""
    GAPFILL = None
    MUTATE = None
    DECORATE = None
    DO_DIRECT_CONNECTIONS = False
    ON_THE_EDGE = False

    def __init__( self, width=None, height=None, tags=(), anchor=None, parent=None, archi=None ):
        self.width = width or random.randint(7,12)
        self.height = height or random.randint(7,12)
        self.tags = tags
        self.anchor = anchor
        self.archi = archi
        self.area = None
        self.contents = container.ContainerList(owner=self)
        if parent:
            parent.contents.append( self )

    def step_two( self, gb ):
        self.arrange_contents( gb )
        if self.GAPFILL:
            self.GAPFILL( gb, self )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_two( gb )
    def step_three( self, gb, archi ):
        # Determine what architect we're going to use- if this room has a
        # custom architect defined, use that instead of the default architecture.
        archi = self.archi or archi
        self.connect_contents( gb, archi )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_three( gb, archi )
    def step_four( self, gb ):
        if self.archi and self.archi.mutate:
            self.archi.mutate( gb, self.area )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_four( gb )
    def step_five( self, gb, archi ):
        self.build( gb, archi )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_five( gb, archi )
    def step_six( self, gb ):
        self.deploy( gb )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_six( gb )
    def step_seven( self, gb ):
        if self.DECORATE:
            self.DECORATE( gb, self.area )
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance( r, Room ):
                r.step_seven( gb )

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
        old_closed = list(closed_area)
        # Assign areas for unplaced rooms.
        for r in self.contents:
            if hasattr( r, "area" ) and not r.area:
                myrect = pygame.Rect( 0, 0, r.width, r.height )
                count = 0
                while ( count < 1000 ) and not r.area:
                    myrect.x = random.choice( range( self.area.x , self.area.x + self.area.width - r.width ) )
                    myrect.y = random.choice( range( self.area.y , self.area.y + self.area.height - r.height ) )
                    if self.ON_THE_EDGE and count < 500:
                        if random.randint(1,2) == 1:
                            myrect.x = random.choice(( self.area.x, self.area.x + self.area.width - r.width ))
                        else:
                            myrect.y = random.choice(( self.area.y, self.area.y + self.area.height - r.height ))
                    if myrect.collidelist( closed_area ) == -1:
                        r.area = myrect
                        closed_area.append( myrect )
                    count += 1
                if not r.area:
                    raise RoomError( "ROOM ERROR: {}:{} cannot place {}".format(str(self),str( self.__class__ ),str(r)) )


    def connect_contents( self, gb, archi ):
        # Step Three: Connect all rooms in contents, making trails on map.

        # Generate list of rooms.
        myrooms = [r for r in self.contents if hasattr(r,"area")]

        # Process them
        if myrooms:
            prev = myrooms[-1]
            for r in myrooms:
                # Connect r to prev
                if self.DO_DIRECT_CONNECTIONS:
                    self.draw_direct_connection( gb, r.area.centerx, r.area.centery, prev.area.centerx, prev.area.centery, archi )
                else:
                    self.draw_L_connection( gb, r.area.centerx, r.area.centery, prev.area.centerx, prev.area.centery, archi )

                # r becomes the new prev
                prev = r

    def build( self, gb, archi ):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        pass

    def list_good_deploy_spots( self, gb ):
        good_spots = list()
        for x in range( self.area.x+1, self.area.x + self.area.width-1 ):
            for y in range( self.area.y+1, self.area.y + self.area.height-1 ):
                if ((( x + y ) % 2 ) == 1 ) and not gb._map[x][y].blocks_walking():
                    good_spots.append( (x,y) )
        return good_spots

    def deploy( self, gb ):
        # Step Six: Move items and monsters onto the map.
        # Find a list of good spots for stuff that goes in the open.
        good_spots = self.list_good_deploy_spots( gb )

        # First pass- execute any deploy methods in any contents.
        for i in list(self.contents):
            if hasattr( i, "predeploy" ):
                i.predeploy( gb, self )

        # Find a list of good walls for stuff that must be mounted on a wall.
        good_walls = list()
        for x in range( self.area.x + 1, self.area.x + self.area.width - 1 ):
            if gb.get_wall(x,self.area.y-1) and gb.get_wall(x-1,self.area.y-1) and gb.get_wall(x+1,self.area.y-1) and not gb._map[x][self.area.y+1].blocks_walking():
                good_walls.append((x,self.area.y-1 ))
        for y in range( self.area.y + 1, self.area.y + self.area.height - 1 ):
            if gb.get_wall(self.area.x-1,y) and gb.get_wall(self.area.x-1,y-1) and gb.get_wall(self.area.x-1,y+1) and not gb._map[self.area.x+1][y].blocks_walking():
                good_walls.append((self.area.x-1,y ))

        for i in list(self.contents):
            # Only place contents which can be placed, but haven't yet.
            if hasattr( i, "place" ) and not ( hasattr(i,"pos") and i.pos ):
                if hasattr( i, "anchor" ):
                    myrect = pygame.Rect(0,0,1,1)
                    i.anchor( self.area, myrect )
                    i.place( gb, (myrect.x,myrect.y) )
                    if (myrect.x,myrect.y) in good_walls:
                        good_walls.remove( (myrect.x,myrect.y) )
                    if (myrect.x,myrect.y) in good_spots:
                        good_spots.remove( (myrect.x,myrect.y) )
                elif hasattr( i, "ATTACH_TO_WALL" ) and i.ATTACH_TO_WALL and good_walls:
                    p = random.choice( good_walls )
                    good_walls.remove( p )
                    i.place( gb, p )
                elif good_spots:
                    p = random.choice( good_spots )
                    good_spots.remove( p )
                    i.place( gb, p )


    def fill( self, gb, dest, floor=-1, wall=-1, decor=-1 ):
        # Fill the provided area with the provided terrain.
        for x in range( dest.x, dest.x + dest.width ):
            for y in range( dest.y, dest.y + dest.height ):
                if gb.on_the_map(x,y):
                    if floor != -1:
                        gb._map[x][y].floor = floor
                    if wall != -1:
                        gb._map[x][y].wall = wall
                    if decor != -1:
                        gb._map[x][y].decor = decor

    def probably_blocks_movement( self, gb, x, y ):
        if not gb.on_the_map(x,y):
            return True
        elif gb._map[x][y].wall is True:
            return True
        else:
            return gb._map[x][y].blocks_walking()

    def draw_direct_connection( self, gb, x1,y1,x2,y2, archi ):
        path = animobs.get_line( x1,y1,x2,y2 )
        for p in path:
            for x in range( p[0]-1, p[0]+2 ):
                for y in range( p[1]-1, p[1]+2 ):
                    archi.draw_fuzzy_ground( gb, x, y )

    def draw_L_connection( self, gb, x1,y1,x2,y2, archi ):
        if random.randint(1,2) == 1:
            cx,cy = x1,y2
        else:
            cx,cy = x2,y1
        self.draw_direct_connection( gb, x1, y1, cx, cy, archi )
        self.draw_direct_connection( gb, x2, y2, cx, cy, archi )

    def find_distance_to( self, oroom ):
        return round( math.sqrt( ( self.area.centerx-oroom.area.centerx )**2 + ( self.area.centery-oroom.area.centery )**2 ) )

class FuzzyRoom( Room ):
    """A room without hard walls, with default ground floors."""
    def build( self, gb, archi ):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        archi = self.archi or archi
        for x in range( self.area.x+1, self.area.x + self.area.width-1 ):
            for y in range( self.area.y+1, self.area.y + self.area.height-1 ):
                archi.draw_fuzzy_ground( gb, x, y )

class OpenRoom( Room ):
    """A room with floor and no walls."""
    def build( self, gb, archi ):
        archi = self.archi or archi
        gb.fill(self.area,floor=archi.floor_terrain,wall=None)


