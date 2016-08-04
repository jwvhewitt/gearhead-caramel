
class TerrainList( list ):
    """ The append method returns the index of the newly added terrain.
        So, you can create a terrain list as follows:
            FLOOR = TL.append( SingTerrain() )
            WALL = TL.append( WallTerrain() )
            ...
    """
    def append(self, item):
        list.append(self,item)
        return len(self) - 1

class Terrain( object ):
    def __init__( self, imagename, block_vision = False, block_walk = False, block_fly = False, frame = 0 ):
        self.imagename = imagename
        self.block_vision = block_vision
        self.block_walk = block_walk
        self.block_fly = block_fly
        self.frame = frame
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
        return self.ident
    def __reduce__( self ):
        return self.ident

class WallTerrain( Terrain ):
    def __init__( self, imagename, block_vision = True, block_walk = True, block_fly = True ):
        self.imagename = imagename
        self.block_vision = block_vision
        self.block_walk = block_walk
        self.block_fly = block_fly

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

