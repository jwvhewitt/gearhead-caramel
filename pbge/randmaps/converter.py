import random
import plasma

#  **********************
#  ***   CONVERTERS   ***
#  **********************

class BasicConverter( object ):
    """Convert True walls to the provided terrain."""
    def __init__( self, terr ):
        self.terr = terr

    def __call__( self, mapgen ):
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.gb._map[x][y].wall is True:
                    mapgen.gb._map[x][y].wall = self.terr


class FloorConverter( object ):
    """Convert True walls to the provided terrain."""
    def __init__( self, terr ):
        self.terr = terr

    def __call__( self, mapgen ):
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.gb._map[x][y].wall is True:
                    mapgen.gb._map[x][y].wall = None
                    mapgen.gb._map[x][y].floor = self.terr


