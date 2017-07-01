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


