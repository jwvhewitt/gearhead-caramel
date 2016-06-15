""" Barebones scene handling for an isometric RPG. For game-specific data,
    either subclass the Scene or just declare whatever extra bits are needed.
"""

import engine

class Tile( object ):
    def __init__(self, floor=None, wall=None, decor=None, visible=False):
        self.floor = floor
        self.wall = wall
        self.decor = decor
        self.visible = visible

    def blocks_vision( self ):
        return ( self.floor and self.floor.block_vision ) or (self.wall and self.wall.block_vision ) or ( self.decor and self.decor.block_vision )

    def blocks_walking( self ):
        return ( self.floor and self.floor.block_walk ) or (self.wall and ( self.wall is True or self.wall.block_walk )) or ( self.decor and self.decor.block_walk )


class Scene( object ):
    DELTA8 = ( (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1) )
    ANGDIR = ( (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0) )
    def __init__(self,width=128,height=128,terrainlist=[],name=""):
        self.name = name
        self.width = width
        self.height = height
        self.terrainlist = terrainlist
        self.scripts = container.ContainerList()
        self.in_sight = set()

        self.last_updated = 0

        # Fill the map with empty tiles
        self._contents = engine.container.ContainerList(owner=self)
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

