import converter
import mutator
import prep
import random
import decor

# An Architecture defines a style for a random map. The same architecture can
# be shared across several scenes, ensuring a consistent style throughout.
#

class Architecture( object ):
    def __init__( self, floor_terrain, wall_filter, prepare=None, biome=None, desctags=None, gapfill=None,
      mutate=None, decorate=None ):
        self.biome = biome
        if not desctags:
            desctags = list()
        self.desctags = desctags
        self.gapfill = gapfill
        self.mutate = mutate
        self.decorate = decorate
        self.wall_filter = wall_filter
        if not prepare:
            prepare = prep.BasicPrep( floor_terrain )
        self.prepare = prepare
        self.floor_terrain = floor_terrain

    def draw_fuzzy_ground( self, gb, x, y ):
        # In general, just erase the wall to expose the floor underneath,
        # adding a floor if need be.
        if gb.on_the_map(x,y):
            gb._map[x][y].wall = None
            if gb._map[x][y].blocks_walking():
                gb._map[x][y].floor = self.ground_terrain

