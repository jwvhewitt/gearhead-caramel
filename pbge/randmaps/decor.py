import random
import pygame
from .. import scenes

#  ********************************
#  ***   INTERIOR  DECORATORS   ***
#  ********************************
# Not to be confused with Python function decorators... these add decor and
# props to a scene.

class OmniDec( object ):
    """Add windows, wall decor, and floor decor to an area."""
    WALL_DECOR = ()
    WALL_FILL_FACTOR = 0.3
    WIN_DECOR = None
    FLOOR_DECOR = ()
    FLOOR_FILL_FACTOR = 0.007
    def __init__( self, win=True, wall_fill_factor=None, floor_fill_factor=None ):
        if win is not True:
            self.WIN_DECOR = win
        self.WALL_FILL_FACTOR = wall_fill_factor or self.WALL_FILL_FACTOR
        self.FLOOR_FILL_FACTOR = floor_fill_factor or self.FLOOR_FILL_FACTOR
    def is_basic_wall(self,gb,x,y):
        return gb.get_wall(x,y)
    def windowize( self, gb, area ):
        y1 = area.y-1
        for x in range( area.x+1, area.x + area.width-1, 3 ):
            if self.is_basic_wall(gb,x,y1) and not gb._map[x][y1].decor:
                gb._map[x][y1].decor = self.WIN_DECOR
        x1 = area.x-1
        for y in range( area.y+1, area.y + area.height-1, 3 ):
            if self.is_basic_wall(gb,x1,y) and not gb._map[x1][y].decor:
                gb._map[x1][y].decor = self.WIN_DECOR
    def is_good_spot_for_wall_decor( self, gb, pos ):
        # This is a good spot for wall decor if we have three basic walls in a
        # row, a space out front, and nothing else here.
        x,y = pos
        #if gb.get_bumpable_at_spot(pos) or not gb._map.get_wall(x,y) == maps.BASIC_WALL:
        #    return False
        if x >= gb.width-1 or y >= gb.height - 1:
            return False
        elif ( self.is_basic_wall(gb,x-1,y) and
          self.is_basic_wall(gb,x+1,y) and
          not gb.tile_blocks_walking(x,y+1) ):
            return True
        elif ( self.is_basic_wall(gb,x,y-1) and
          self.is_basic_wall(gb,x,y+1) and
          not gb.tile_blocks_walking(x+1,y) ):
            return True
    def draw_wall_decor( self, gb, x, y ):
        gb._map[x][y].decor = random.choice(self.WALL_DECOR)
    def draw_floor_decor( self, gb, x, y ):
        gb._map[x][y].decor = random.choice(self.FLOOR_DECOR)

    def __call__( self, gb, area ):
        good_wall_spots = list()
        good_floor_spots = list()
        for x in range(area.x, area.x + area.width-1):
            for y in range(area.y, area.y + area.height-1):
                pos = (x,y)
                if self.is_basic_wall(gb,x,y) and self.is_good_spot_for_wall_decor(gb,pos):
                    good_wall_spots.append( pos )
                elif x > 0 and y > 0 and \
                  not gb._map[x][y].blocks_walking() and not gb._map[x][y].wall \
                  and not gb._map[x][y].decor and gb.wall_wont_block(x,y):
                    good_floor_spots.append( pos )
        for m in gb.contents:
            if hasattr(m,"pos"):
                if m.pos in good_wall_spots:
                    good_wall_spots.remove( m.pos )
                elif m.pos in good_floor_spots:
                    good_floor_spots.remove( m.pos )

        if self.FLOOR_DECOR:
            for t in range(int(len(good_floor_spots) * self.FLOOR_FILL_FACTOR)):
                x,y = random.choice( good_floor_spots )
                if gb.wall_wont_block(x,y):
                    self.draw_floor_decor(gb,x,y)
        if self.WALL_DECOR:
            for t in range( int( len(good_wall_spots) * self.WALL_FILL_FACTOR)):
                x,y = random.choice( good_wall_spots )
                if self.is_good_spot_for_wall_decor( gb,(x,y) ):
                    self.draw_wall_decor(gb,x,y)

        if self.WIN_DECOR:
            self.windowize(gb,area)



