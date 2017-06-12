
""" How Terrain Works: Each terraintype is supposed to be a singleton, so
    every reference to a particular terrain type points at the same thing,
    and there will be no problems with serialization. So, to create a new
    terrain type, create a subclass of the closest match and change its
    constants.
"""
import exceptions
from .. import image

class Terrain( object ):
    def __init__( self ):
        raise exceptions.NotImplementedError("Terrain can't be instantiated. Use the class as a singleton.")
    name = 'Undefined Terrain'
    imagename = ''
    block_vision = False
    block_walk = False
    block_fly = False
    frame = 0

    @classmethod
    def render( self, dest, view, x, y ):
        spr = view.get_sprite(self)
        spr.render( dest, self.frame )
    @classmethod
    def prerender( self, dest, view, x, y ):
        """Some wall types need a border that gets drawn first."""
        pass
    @classmethod
    def place( self, scene, pos ):
        if scene.on_the_map( *pos ):
            scene.map[pos[0]][pos[1]].decor = self
    @classmethod
    def __str__( self ):
        return self.name
    @classmethod
    def get_sprite( self ):
        """Generate the sprite for this terrain."""
        return image.Image(self.imagename,54,54)

class WallTerrain( Terrain ):
    block_vision = True
    block_walk = True
    block_fly = True

    @classmethod
    def prerender( self, dest, view, x, y ):
        pass
    @classmethod
    def render( self, dest, view, x,y ):
        bor = view.calc_border_score( x, y )
        if bor == -1:
            bor = None
        if bor == 14:
            wal = None
        else:
            wal = view.calc_wall_score( x, y, WallTerrain )

        if wal:
            spr = view.get_sprite(self)
            spr.render( dest, wal )

