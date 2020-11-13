""" Barebones scene handling for an isometric RPG. For game-specific data,
    either subclass the Scene or just declare whatever extra bits are needed.
"""

    # I feel like this unit isn't very Pythonic, since it's full of setters
    # and getters and various other walls to keep the user away from the
    # data.


from .. import container,image,KeyObject
import pygame
import math
from . import movement
import weakref

class Tile( object ):
    def __init__(self, floor=None, wall=None, decor=None, visible=False):
        self.floor = floor
        self.wall = wall
        self.decor = decor
        self.visible = visible
    def blocks_movement( self, movemode ):
        return ( self.floor and movemode in self.floor.blocks ) or (self.wall is True) or (self.wall and movemode in self.wall.blocks ) or (self.decor and movemode in self.decor.blocks )

    def blocks_vision( self ):
        return self.blocks_movement( movement.Vision )

    def blocks_walking( self ):
        return self.blocks_movement( movement.Walking )

    def render_bottom( self, dest, view, x, y ):
        if self.floor:
            self.floor.render_bottom( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.render_bottom( dest, view, x, y )
        if self.decor:
            self.decor.render_bottom( dest, view, x, y )

    def render_biddle( self, dest, view, x, y ):
        if self.floor:
            self.floor.render_biddle( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.render_biddle( dest, view, x, y )
        if self.decor:
            self.decor.render_biddle( dest, view, x, y )

    def render_middle( self, dest, view, x, y ):
        if self.floor:
            self.floor.render_middle( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.render_middle( dest, view, x, y )
        if self.decor:
            self.decor.render_middle( dest, view, x, y )

    def render_top( self, dest, view, x, y ):
        if self.floor:
            self.floor.render_top( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.render_top( dest, view, x, y )
        if self.decor:
            self.decor.render_top( dest, view, x, y )

    def altitude( self ):
        alt = 0
        if self.floor:
            alt = self.floor.altitude
        if self.wall and self.wall is not True:
            alt = max(self.wall.altitude,alt)
        if self.decor:
            alt = max(self.decor.altitude,alt)
        return alt

    def get_movement_multiplier( self, mmode ):
        it = 1.0
        if self.floor:
            it *= self.floor.movement_cost.get(mmode,1.0)
        if self.wall:
            it *= self.wall.movement_cost.get(mmode,1.0)
        if self.decor:
            it *= self.decor.movement_cost.get(mmode,1.0)
        return it

    def get_cover( self, vmode=movement.Vision ):
        it = 0
        if self.floor:
            it += self.floor.movement_cost.get(vmode,0)
        if self.wall:
            it += self.wall.movement_cost.get(vmode,0)
        if self.decor:
            it += self.decor.movement_cost.get(vmode,0)
        return it


class PlaceableThing( KeyObject ):
    """A thing that can be placed on the map."""
    # By default, a hidden thing just isn't displayed.
    def __init__(self, hidden=False, **keywords ):
        self.hidden = hidden
        self.pos = None
        self.offset_pos = None
        super(PlaceableThing, self).__init__(**keywords)
    def place( self, scene, pos=None, team=None ):
        if hasattr( self, "container" ) and self.container:
            self.container.remove( self )
        scene.contents.append( self )
        self.pos = pos
        if team:
            scene.local_teams[self] = team
    imagename = ""
    colors = None
    imageheight = 64
    imagewidth = 64
    frame = 0
    altitude = None
    def get_sprite(self):
        """Generate the sprite for this thing."""
        return image.Image(self.imagename,self.imagewidth,self.imageheight,self.colors)
    def render( self, foot_pos, view ):
        if self.hidden:
            self.render_hidden( foot_pos, view )
        else:
            self.render_visible( foot_pos, view )
    def render_visible( self, foot_pos, view ):
        spr = view.get_sprite(self)
        mydest = spr.get_rect(self.frame)
        mydest.midbottom = foot_pos
        if self.offset_pos:
            mydest.x += self.offset_pos[0]
            mydest.y += self.offset_pos[1]
        spr.render( mydest, self.frame )
    def render_hidden( self, foot_pos, view ):
        pass
    def move( self, dest, view, speed=0.25 ):
        view.anim_list.append( animobs.MoveModel( self, dest=dest, speed=speed))
    # Define an update_graphics method if you need to change this object's appearance
    # after invoking effects.



from . import pathfinding
from . import pfov
from . import terrain
from . import viewer
from . import animobs
from . import targetarea
from . import waypoints
from . import areaindicator

class TeamDictionary( weakref.WeakKeyDictionary ):
    # It's like a regular WeakKeyDictionary but it pickles.
    def __getstate__( self ):
        state = dict()
        for key,val in self.items():
            state[key] = val
        return state
    def __setstate__( self, state ):
        self.__init__()
        self.update( state )


class Scene( object ):
    DELTA8 = ( (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1) )
    ANGDIR = ( (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0) )
    def __init__(self,width=128,height=128,name="",player_team=None,exit_scene_wp=None):
        self.name = name
        self.width = width
        self.height = height
        self.player_team = player_team
        self.scripts = container.ContainerList(owner=self)
        self.sub_scenes = container.ContainerList(owner=self)

        # The data dict is primarily used to hold frames for TerrSetTerrain
        # tiles, but I guess you could put anything you want in there.
        self.data = dict()
        self.in_sight = set()

        self.last_updated = 0
        self.exit_scene_wp = exit_scene_wp

        # Fill the map with empty tiles
        self.contents = container.ContainerList(owner=self)
        self._map = [[ Tile()
            for y in range(height) ]
                for x in range(width) ]

        self.local_teams = dict()


    def on_the_map( self , x , y ):
        # Returns true if on the map, false otherwise
        return ( ( x >= 0 ) and ( x < self.width ) and ( y >= 0 ) and ( y < self.height ) )


    def get_floor( self, x, y ):
        """Safely return floor of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].floor
        else:
            return None

    def get_wall( self, x, y ):
        """Safely return wall of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].wall
        else:
            return None

    def set_wall( self, x, y, terr ):
        """Safely set wall of tile x,y."""
        if self.on_the_map(x,y):
            self._map[x][y].wall = terr

    def get_decor( self, x, y ):
        """Safely return decor of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].decor
        else:
            return None

    def set_decor( self, x, y, terr ):
        """Safely set decor of tile x,y."""
        if self.on_the_map(x,y):
            self._map[x][y].decor = terr

    def get_visible( self, x, y ):
        """Safely return visibility status of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].visible
        else:
            return False

    def set_visible( self, x, y, v=True ):
        """Safely return visibility status of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            self._map[x][y].visible = v


    def tile_blocks_vision( self, x, y ):
        if self.on_the_map(x,y):
            return self._map[x][y].blocks_vision()
        else:
            return True

    def tile_blocks_walking( self, x, y ):
        if self.on_the_map(x,y):
            return self._map[x][y].blocks_walking()
        else:
            return True

    def tile_blocks_movement( self, x, y, mmode ):
        if self.on_the_map(x,y):
            return self._map[x][y].blocks_movement(mmode)
        else:
            return True


    def distance( self, pos1, pos2 ):
        return round( math.sqrt( ( pos1[0]-pos2[0] )**2 + ( pos1[1]-pos2[1] )**2 ) )

    def __str__( self ):
        if self.name:
            return self.name
        else:
            return repr( self )

    def wall_wont_block( self, x, y ):
        """Return True if a wall placed here won't block movement."""
        if self.tile_blocks_walking(x,y):
            # This is a wall now. Changing it from a wall to a wall really won't
            # change anything, as should be self-evident.
            return True
        else:
            # Adding a wall will block a passage if there are two or more spaces
		    # in the eight surrounding tiles which are separated by walls.
            was_a_space = not self.tile_blocks_walking(x-1,y)
            n = 0
            for a in self.ANGDIR:
                is_a_space = not self.tile_blocks_walking(x+a[0],y+a[1])
                if is_a_space != was_a_space:
                    # We've gone from wall to space or vice versa.
                    was_a_space = is_a_space
                    n += 1
            return n <= 2

    def fill( self, dest, floor=-1, wall=-1, decor=-1 ):
        # Fill the provided area with the provided terrain.
        for x in range( dest.x, dest.x + dest.width ):
            for y in range( dest.y, dest.y + dest.height ):
                if self.on_the_map(x,y):
                    if floor != -1:
                        self._map[x][y].floor = floor
                    if wall != -1:
                        self._map[x][y].wall = wall
                    if decor != -1:
                        self._map[x][y].decor = decor

    def fill_blob( self, dest, floor=-1, wall=-1, decor=-1 ):
        # Fill the provided area with the provided terrain.
        midpoint = dest.center
        for x in range( dest.x, dest.x + dest.width ):
            for y in range( dest.y, dest.y + dest.height ):
                if self.on_the_map(x,y) and self.distance((x,y),midpoint) <= dest.width//2:
                    if floor != -1:
                        self._map[x][y].floor = floor
                    if wall != -1:
                        self._map[x][y].wall = wall
                    if decor != -1:
                        self._map[x][y].decor = decor

    def get_move_cost( self, a, b, movemode ):
        # a and b should be adjacent tiles.
        if self.on_the_map(b[0],b[1]) and self.on_the_map(a[0],a[1]):
            base_cost = 5 * (abs(a[0]-b[0]) + abs(a[1]-b[1]) + 1)
            # Modify by terrain.
            base_cost *= self._map[b[0]][b[1]].get_movement_multiplier(movemode)
            # Modify for climbing.
            if (movemode.climb_penalty > 1.0) and movemode.altitude is not None and (max(self._map[b[0]][b[1]].altitude(),movemode.altitude)>max(self._map[a[0]][a[1]].altitude(),movemode.altitude)):
                base_cost *= movemode.climb_penalty
            return int(base_cost)
        else:
            return 100
    def tile_altitude(self,x,y):
        if self.on_the_map(x,y):
            return self._map[int(x)][int(y)].altitude()
        else:
            return 0
    def model_altitude( self, m,x,y ):
        if not hasattr(m,"mmode") or not m.mmode or m.mmode.altitude is None:
            return self.tile_altitude(x,y)
        else:
            return max(self._map[x][y].altitude(),m.mmode.altitude)

    def get_cover(self,x1,y1,x2,y2,vmode=movement.Vision):
        # x1,y1 is the viewer, x2,y2 is the target
        my_line = animobs.get_line(x1,y1,x2,y2)
        it = 0
        for p in my_line[1:]:
            if self.on_the_map(*p):
                it += self._map[p[0]][p[1]].get_cover(vmode)
        return it

    def get_waypoint(self,pos):
        # Return the first waypoint found at this position. If more than one
        # waypoint is there, tough cookies.
        for a in self.contents:
            if a.pos == pos and isinstance(a,waypoints.Waypoint):
                return a

    def get_waypoints(self,pos):
        # Return all of the waypoints found at this position.
        return [a for a in self.contents if isinstance(a,waypoints.Waypoint) and a.pos == pos]

    def get_bumpable(self,pos):
        # Return the first bumpable found at this position. If more than one
        # bumpable is there, tough cookies.
        for a in self.contents:
            if hasattr(a,"pos") and a.pos == pos and hasattr(a,'bump'):
                return a

    def get_bumpables(self,pos):
        # Return all of the bumpables found at this position.
        return [a for a in self.contents if hasattr(a,"pos") and a.pos == pos and hasattr(a,'bump')]

    def get_root_scene(self):
        if hasattr(self, "container") and self.container and hasattr(self.container.owner, "get_root_scene"):
            return self.container.owner.get_root_scene()
        else:
            return self

    def end_scene(self,camp):
        if camp.scene is self and not camp.destination:
            # If the scene being deleted is the current scene, and we don't already have a destination
            # set, set a new destination.
            return_to = self.exit_scene_wp or camp.home_base
            if return_to:
                camp.destination, camp.entrance = return_to
        for s in list(self.sub_scenes):
            if hasattr(s, "end_scene"):
                s.end_scene(camp)
            else:
                self.sub_scenes.remove(s)
        for s in list(self.scripts):
            self.scripts.remove(s)
        for c in list(self.contents):
            self.contents.remove(c)
        if hasattr(self,"container") and self.container:
            self.container.remove(self)

    def get_rect(self):
        return pygame.Rect(0,0,self.width,self.height)
