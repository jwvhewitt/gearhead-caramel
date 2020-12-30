from .. import container
import random
import pygame
import math
from ..scenes import animobs,terrain
import inspect

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

    def __init__( self, width=None, height=None, tags=(), anchor=None, parent=None, archi=None, decorate=None ):
        self.width = width or random.randint(7,12)
        self.height = height or random.randint(7,12)
        self.tags = tags
        self.anchor = anchor
        self.archi = archi
        self.area = None
        self.contents = container.ContainerList(owner=self)
        if parent:
            parent.contents.append( self )
        self.DECORATE = decorate or self.DECORATE

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
            self.DECORATE( gb, self )
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
        #old_closed = list(closed_area)
        # Assign areas for unplaced rooms.
        for r in self.contents:
            if hasattr( r, "area" ) and not r.area:
                myrect = pygame.Rect( 0, 0, r.width, r.height )
                count = 0
                while ( count < 1000 ) and not r.area:
                    myrect.x = random.choice( list(range( self.area.x , self.area.x + self.area.width - r.width)) )
                    myrect.y = random.choice( list(range( self.area.y , self.area.y + self.area.height - r.height)) )
                    if self.ON_THE_EDGE and count < 500:
                        if random.randint(1,2) == 1:
                            myrect.x = random.choice(( self.area.x, self.area.x + self.area.width - r.width ))
                        else:
                            myrect.y = random.choice(( self.area.y, self.area.y + self.area.height - r.height ))
                    if myrect.inflate(6,6).collidelist( closed_area ) == -1:
                        r.area = myrect
                        closed_area.append( myrect )
                    elif count > 200 and myrect.collidelist( closed_area ) == -1:
                        r.area = myrect
                        closed_area.append(myrect)
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

    def dont_touch_edge(self, gb):
        if self.area.x == 0:
            self.area.x += 1
            self.area.width -= 1
        elif self.area.x+self.area.width >= gb.width:
            self.area.x -= 1
            self.area.width -= 1
        if self.area.y == 0:
            self.area.y += 1
            self.area.height -= 1
        elif self.area.y+self.area.height >= gb.height:
            self.area.y -= 1
            self.area.height -= 1

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

        # Find a list of good walls for stuff that must be mounted on a wall.
        good_walls = [p for p in self.get_west_north_wall_points(gb) if self.is_good_spot_for_wall_decor(gb,p)]

        # First pass- execute any deploy methods in any contents.
        for i in list(self.contents):
            if hasattr( i, "predeploy" ):
                i.predeploy( gb, self )
            # Remove the spaces occupied by map contents from the good spots lists.
            if hasattr(i,"pos") and i.pos:
                if i.pos in good_walls:
                    good_walls.remove(i.pos)
                if i.pos in good_spots:
                    good_spots.remove(i.pos)

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
        elif inspect.isclass(gb.get_wall(x,y)) and issubclass(gb.get_wall(x,y),terrain.DoorTerrain):
            return False
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

    def is_basic_wall(self,gb,x,y):
        wall = gb.get_wall(x,y)
        if inspect.isclass(wall):
            return issubclass(wall,terrain.WallTerrain) and not issubclass(wall,terrain.DoorTerrain)
        elif wall is True:
            return True

    def is_good_spot_for_wall_decor( self, gb, pos ):
        # This is a good spot for wall decor if we have three basic walls in a
        # row, a space out front, and nothing else here.
        x,y = pos
        #if gb.get_bumpable_at_spot(pos) or not gb._map.get_wall(x,y) == maps.BASIC_WALL:
        #    return False
        wall = gb.get_wall(x,y)
        if x >= gb.width-1 or y >= gb.height - 1:
            return False
        elif inspect.isclass(wall) and issubclass(wall,terrain.DoorTerrain):
            return False
        elif ( self.is_basic_wall(gb,x-1,y) and
          self.is_basic_wall(gb,x+1,y) and
          not gb.tile_blocks_walking(x,y+1) ):
            return True
        elif ( self.is_basic_wall(gb,x,y-1) and
          self.is_basic_wall(gb,x,y+1) and
          not gb.tile_blocks_walking(x+1,y) ):
            return True

    def get_west_north_wall_points(self, gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x,self.area.y) for x in range( self.area.x + 1, self.area.x + self.area.width - 2 )]
        mylist += [(self.area.x,y) for y in range( self.area.y + 1, self.area.y + self.area.height - 2 )]
        for m in [m for m in gb.contents if hasattr(m,"pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist


class FuzzyRoom( Room ):
    """A room without hard walls, with default ground floors."""
    def build( self, gb, archi ):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        archi = self.archi or archi
        for x in range( self.area.x+1, self.area.x + self.area.width-1 ):
            for y in range( self.area.y+1, self.area.y + self.area.height-1 ):
                archi.draw_fuzzy_ground( gb, x, y )


class NoWallRoom( Room ):
    """A room that doesn't change the floor but gets rid of the walls."""
    def build( self, gb, archi ):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        archi = self.archi or archi
        for x in range( self.area.x+1, self.area.x + self.area.width-1 ):
            for y in range( self.area.y+1, self.area.y + self.area.height-1 ):
                gb.set_wall(x,y,None)


class OpenRoom( Room ):
    """A room with floor and no walls."""
    def build( self, gb, archi ):
        # Verify the area.
        self.dont_touch_edge(gb)
        archi = self.archi or archi
        gb.fill(self.area,floor=archi.floor_terrain,wall=None)
    def get_west_north_wall_points(self,gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x,self.area.y-1) for x in range( self.area.x, self.area.x + self.area.width - 1 )]
        mylist += [(self.area.x-1,y) for y in range( self.area.y, self.area.y + self.area.height - 1 )]
        for m in [m for m in gb.contents if hasattr(m,"pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist

class MostlyOpenRoom( OpenRoom ):
    """A room with floor and no walls unless it's on the edge, in which case it gets walls."""
    def build( self, gb, archi ):
        archi = self.archi or archi
        gb.fill(self.area,floor=archi.floor_terrain,wall=None)
        if self.area.x == 0:
            # Draw a west wall.
            gb.fill(pygame.Rect(0,self.area.y,0,self.area.y+self.area.height-1),wall=archi.wall_terrain)
        elif self.area.right == gb.width:
            # Draw an east wall.
            gb.fill(pygame.Rect(self.area.right-1, self.area.y, self.area.right-1, self.area.y + self.area.height - 1), wall=archi.wall_terrain)

        if self.area.y == 0:
            # Draw a north wall.
            gb.fill(pygame.Rect(self.area.x,0,self.area.x+self.area.width-1,0),wall=archi.wall_terrain)
        elif self.area.bottom == gb.width:
            # Draw an south wall.
            gb.fill(pygame.Rect(self.area.x, self.area.bottom-1, self.area.right-1, self.area.bottom - 1), wall=archi.wall_terrain)

    def get_west_north_wall_points(self,gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x,max(self.area.y-1,0)) for x in range( self.area.x, self.area.x + self.area.width - 1 )]
        mylist += [(max(self.area.x-1,0),y) for y in range( self.area.y, self.area.y + self.area.height - 1 )]
        for m in [m for m in gb.contents if hasattr(m,"pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist


class OldClosedRoom( Room ):
    """A room with hard walls."""
    def deal_with_empties( self, gb, empties, archi ):
        """Fill this line with a wall, leaving at least one door or opening."""
        p2 = random.choice( empties )
        empties.remove( p2 )
        archi.place_a_door(gb,p2[0],p2[1])
        if len( empties ) > random.randint(1,6):
            p2 = random.choice( empties )
            if self.no_door_nearby(gb,p2):

                empties.remove( p2 )
                archi.place_a_door(gb, p2[0], p2[1])
        for pp in empties:
            gb.set_wall(pp[0], pp[1], archi.wall_terrain)
        del empties[:]
    def no_door_nearby(self,gb,p):
        door_found = False
        x,y = p
        for vec in gb.DELTA8:
            dx,dy = vec
            wall = gb.get_wall(x+dx,y+dy)
            if wall and wall is not True and issubclass(wall,terrain.DoorTerrain):
                door_found = True
                break
        return not door_found
    def probably_an_entrance( self, gb, p, vec ):
        return not self.probably_blocks_movement(gb,*p) and not self.probably_blocks_movement(gb,p[0]+vec[0],p[1]+vec[1])
    def draw_wall( self, gb, points, vec, archi ):
        empties = list()
        for p in points:
            if self.probably_an_entrance(gb,p,vec):
                empties.append( p )
            else:
                gb.set_wall(p[0], p[1], archi.wall_terrain)
                if empties:
                    self.deal_with_empties(gb, empties, archi )
        if empties:
            self.deal_with_empties(gb, empties, archi )

    def build( self, gb, archi ):
        if not self.area:
            raise RoomError( "ROOM ERROR: No area found for {} in {}".format(self,gb) )
        archi = self.archi or archi

        # Fill the floor with BASIC_FLOOR, and clear room interior
        self.fill( gb, self.area, floor=archi.floor_terrain )
        self.fill( gb, self.area.inflate(-2,-2), wall=None )
        # Set the four corners to basic walls
        gb.set_wall(self.area.x,self.area.y, archi.wall_terrain)
        gb.set_wall(self.area.x+self.area.width-1,self.area.y, archi.wall_terrain)
        gb.set_wall(self.area.x,self.area.y+self.area.height-1, archi.wall_terrain)
        gb.set_wall(self.area.x+self.area.width-1, self.area.y+self.area.height-1, archi.wall_terrain)

        # Draw each wall. Harder than it sounds.
        self.draw_wall( gb, animobs.get_line( self.area.x+1,self.area.y,self.area.x+self.area.width-2,self.area.y ), (0,-1), archi )
        self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y+1,self.area.x,self.area.y+self.area.height-2 ), (-1,0), archi )
        self.draw_wall( gb, animobs.get_line( self.area.x+1,self.area.y+self.area.height-1,self.area.x+self.area.width-2,self.area.y+self.area.height-1 ), (0,1), archi )
        self.draw_wall( gb, animobs.get_line( self.area.x+self.area.width-1,self.area.y+1,self.area.x+self.area.width-1,self.area.y+self.area.height-2 ), (1,0), archi )

    def list_good_deploy_spots( self, gb ):
        good_spots = list()
        for x in range( self.area.x+2, self.area.x + self.area.width-2, 2 ):
            for y in range( self.area.y+2, self.area.y + self.area.height-2, 2 ):
                if not gb._map[x][y].blocks_walking():
                    good_spots.append( (x,y) )
        return good_spots

class ClosedRoom( Room ):
    """A room with hard walls."""
    def deal_with_empties( self, gb, empties, archi ):
        """Fill this line with a wall, leaving at least one door or opening."""
        p2 = random.choice( empties )
        empties.remove( p2 )
        archi.place_a_door(gb,p2[0],p2[1])
        if len( empties ) > random.randint(1,6):
            p2 = random.choice( empties )
            if self.no_door_nearby(gb,p2):

                empties.remove( p2 )
                archi.place_a_door(gb, p2[0], p2[1])
        for pp in empties:
            gb.set_wall(pp[0], pp[1], archi.wall_terrain)
        del empties[:]
    def no_door_nearby(self,gb,p):
        door_found = False
        x,y = p
        for vec in gb.DELTA8:
            dx,dy = vec
            wall = gb.get_wall(x+dx,y+dy)
            if wall and wall is not True and issubclass(wall,terrain.DoorTerrain):
                door_found = True
                break
        return not door_found
    def probably_an_entrance( self, gb, p, vec ):
        return not self.probably_blocks_movement(gb,*p) and not self.probably_blocks_movement(gb,p[0]+vec[0],p[1]+vec[1])
    def draw_wall( self, gb, points, vec, archi ):
        empties = list()
        for p in points:
            if not gb.on_the_map(p[0]+vec[0],p[1]+vec[1]):
                gb.set_wall(p[0], p[1], archi.wall_terrain)
            elif self.probably_an_entrance(gb,p,vec):
                empties.append( p )
            else:
                gb.set_wall(p[0], p[1], archi.wall_terrain)
                if empties:
                    self.deal_with_empties(gb, empties, archi )
        if empties:
            self.deal_with_empties(gb, empties, archi )

    def build( self, gb, archi ):
        if not self.area:
            raise RoomError( "ROOM ERROR: No area found for {} in {}".format(self,gb) )
        archi = self.archi or archi
        self.dont_touch_edge(gb)

        # Fill the floor with BASIC_FLOOR, and clear room interior
        self.fill( gb, self.area, floor=archi.floor_terrain )
        self.fill( gb, self.area, wall=None )
        # Set the four corners to basic walls
        gb.set_wall(self.area.x-1,self.area.y-1, archi.wall_terrain)
        gb.set_wall(self.area.x+self.area.width,self.area.y-1, archi.wall_terrain)
        gb.set_wall(self.area.x-1,self.area.y+self.area.height, archi.wall_terrain)
        gb.set_wall(self.area.x+self.area.width, self.area.y+self.area.height, archi.wall_terrain)

        # Draw each wall. Harder than it sounds.
        if gb.on_the_map(self.area.x-1,self.area.y):
            self.draw_wall( gb, animobs.get_line( self.area.x-1,self.area.y,self.area.x-1,self.area.y+self.area.height-1 ), (-1,0), archi )
        else:
            self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y,self.area.x,self.area.y+self.area.height-1 ), (-1,0), archi )
        if gb.on_the_map(self.area.x+self.area.width, self.area.y):
            self.draw_wall( gb, animobs.get_line( self.area.x+self.area.width,self.area.y,self.area.x+self.area.width,self.area.y+self.area.height-1 ), (1,0), archi )
        else:
            self.draw_wall(gb,
                           animobs.get_line(self.area.x + self.area.width-1, self.area.y, self.area.x + self.area.width-1,
                                            self.area.y + self.area.height - 1), (1, 0), archi)
        if gb.on_the_map(self.area.x,self.area.y-1):
            self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y-1,self.area.x+self.area.width-1,self.area.y-1 ), (0,-1), archi )
        else:
            self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y,self.area.x+self.area.width-1,self.area.y ), (0,-1), archi )
        if gb.on_the_map(self.area.x,self.area.y+self.area.height):
            self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y+self.area.height,self.area.x+self.area.width-1,self.area.y+self.area.height ), (0,1), archi )
        else:
            self.draw_wall( gb, animobs.get_line( self.area.x,self.area.y+self.area.height-1,self.area.x+self.area.width-1,self.area.y+self.area.height-1 ), (0,1), archi )


    def list_good_deploy_spots( self, gb ):
        good_spots = list()
        for x in range( self.area.x+2, self.area.x + self.area.width-2, 2 ):
            for y in range( self.area.y+2, self.area.y + self.area.height-2, 2 ):
                if not gb._map[x][y].blocks_walking():
                    good_spots.append( (x,y) )
        return good_spots

    def get_west_north_wall_points(self,gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x,self.area.y-1) for x in range( self.area.x, self.area.x + self.area.width - 1 )]
        mylist += [(self.area.x-1,y) for y in range( self.area.y, self.area.y + self.area.height - 1 )]
        for m in [m for m in gb.contents if hasattr(m,"pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist

