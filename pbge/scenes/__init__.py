""" Barebones scene handling for an isometric RPG. For game-specific data,
    either subclass the Scene or just declare whatever extra bits are needed.
"""

    # I feel like this unit isn't very Pythonic, since it's full of setters
    # and getters and various other walls to keep the user away from the
    # data.


from .. import container,image,KeyObject
import pygame

class Tile( object ):
    def __init__(self, floor=None, wall=None, decor=None, visible=True):
        self.floor = floor
        self.wall = wall
        self.decor = decor
        self.visible = visible

    def blocks_vision( self ):
        return ( self.floor and self.floor.block_vision ) or (self.wall and self.wall.block_vision ) or (self.decor and self.decor.block_vision )

    def blocks_walking( self ):
        return (self.floor and self.floor.block_walk) or (self.wall is True) or (self.wall and self.wall.block_walk) or (self.decor and self.decor.block_walk)

    def prerender( self, dest, view, x, y ):
        if self.floor:
            self.floor.prerender( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.prerender( dest, view, x, y )
        if self.decor:
            self.decor.prerender( dest, view, x, y )

    def render( self, dest, view, x, y ):
        if self.floor:
            self.floor.render( dest, view, x, y )
        if self.wall and self.wall is not True:
            self.wall.render( dest, view, x, y )
        if self.decor:
            self.decor.render( dest, view, x, y )



class PlaceableThing( KeyObject ):
    """A thing that can be placed on the map."""
    def __init__(self, **keywords ):
        super(PlaceableThing, self).__init__(**keywords)

    def place( self, scene, pos=None, team=None ):
        if hasattr( self, "container" ) and self.container:
            self.container.remove( self )
        scene._contents.append( self )
        self.pos = pos
        if team:
            scene.local_teams[self] = team
    imagename = ""
    colors = None
    imageheight = 64
    imagewidth = 64
    frame = 0
    def get_sprite(self):
        """Generate the sprite for this thing."""
        return image.Image(self.imagename,self.imagewidth,self.imageheight,self.colors)
    def render( self, foot_pos, view ):
        spr = view.get_sprite(self)
        mydest = pygame.Rect(0,0,spr.frame_width,spr.frame_height)
        mydest.midbottom = foot_pos
        spr.render( mydest, self.frame )
    def move( self, dest, view, speed=0.25 ):
        view.anim_list.append( animobs.MoveModel( self, dest=dest, speed=speed))



import pathfinding
import pfov
import terrain
import viewer
import animobs


class Scene( object ):
    DELTA8 = ( (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1) )
    ANGDIR = ( (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0) )
    def __init__(self,width=128,height=128,name=""):
        self.name = name
        self.width = width
        self.height = height
        self.scripts = container.ContainerList()
        self.in_sight = set()

        self.last_updated = 0

        # Fill the map with empty tiles
        self._contents = container.ContainerList(owner=self)
        self._map = [[ Tile()
            for y in xrange(height) ]
                for x in xrange(width) ]

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

    def get_decor( self, x, y ):
        """Safely return decor of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].decor
        else:
            return None

    def get_visible( self, x, y ):
        """Safely return visibility status of tile x,y, or None if off map."""
        if self.on_the_map(x,y):
            return self._map[x][y].visible
        else:
            return False

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


