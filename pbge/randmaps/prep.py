import plasma

#   ******************
#   ***  PREPPERS  ***
#   ******************
#
# Before map generation proper takes place, the grid must be prepared.
# Generally this will involve setting a terrain for the floor of each tile
# and setting the wall values to True. Note that "True" is not a valid terrain
# type- it will be converted to proper walls later on in the generation process.
#
# The prepper may also set the map generator's plasma attribute.

class BasicPrep( object ):
    """Fill map with True walls and basic floors."""
    def __init__( self, terr ):
        self.terr = terr

    def __call__( self, mapgen ):
        mapgen.fill( mapgen.gb, mapgen.area, floor=self.terr, wall=True )

class HeightfieldPrep( object ):
    """Use a plasma map to fill with three levels of terrain"""
    def __init__( self, loterr, medterr, hiterr, loground=0.2, higround=0.5 ):
        self.loterr = loterr
        self.medterr = medterr
        self.hiterr = hiterr
        self.loground = loground
        self.higround = higround
    def __call__( self, mapgen ):
        mapgen.plasma = plasma.Plasma()
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.plasma.map[x][y] < self.loground:
                    mapgen.gb._map[x][y].floor = self.loterr
                elif mapgen.plasma.map[x][y] < self.higround:
                    mapgen.gb._map[x][y].floor = self.medterr
                    mapgen.gb._map[x][y].wall = True
                else:
                    mapgen.gb._map[x][y].floor = self.hiterr
                    mapgen.gb._map[x][y].wall = True

