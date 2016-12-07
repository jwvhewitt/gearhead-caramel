
""" How Terrain Works: Each terraintype is supposed to be a singleton, so
    every reference to a particular terrain type points at the same thing,
    and there will be no problems with serialization. So, to create a new
    terrain type, create a subclass of the closest match and change its
    constants.
"""
import exceptions

class Terrain( object ):
    def __init__( self ):
        raise exceptions.NotImplementedError("Terrain can't be instantiated. Use the class as a singleton.")
    name = 'Undefined Terrain'
    imagename = ''
    block_vision = False
    block_walk = False
    block_fly = False
    frame = 0

    def render( self, screen, dest, view, data ):
        view.sprites[ self.spritesheet ].render( screen, dest, self.frame )
    def prerender( self, screen, dest, view, data ):
        """Some wall types need a border that gets drawn first."""
        pass
    def get_data( self, view, x, y ):
        """Pre-generate display data for this tile."""
        return None
    def place( self, scene, pos ):
        if scene.on_the_map( *pos ):
            scene.map[pos[0]][pos[1]].decor = self
    def __str__( self ):
        return self.name

class WallTerrain( Terrain ):

    def prerender( self, screen, dest, view, data ):
        if data[0] != None:
            view.sprites[ SPRITE_BORDER ].render( screen, dest, data[0] )
    def render( self, screen, dest, view, data ):
        if data[1] != None:
            view.sprites[ self.spritesheet ].render( screen, dest, data[1] )
    def get_data( self, view, x, y ):
        """Pre-generate display data for this tile- border frame, wall frame."""
        bor = view.calc_border_score( x, y )
        if bor == -1:
            bor = None
        if bor == 14:
            wal = None
        else:
            wal = view.calc_wall_score( x, y )

        return (bor,wal)

