import pygame
import random

#  ********************
#  ***   MUTATORS   ***
#  ********************

class CellMutator( object ):
    """Uses cellular automata to mutate the maze."""
    def __init__( self, passes=5, do_carving=True, noise_throttle=25 ):
        self.passes = passes
        self.do_carving = do_carving
        self.noise_throttle = max( noise_throttle, 10 )

    DO_NOTHING, WALL_ON, WALL_OFF = list(range( 3))

    def num_nearby_walls( self, gb, x0, y0 ):
        n = 0
        for x in range(x0-1,x0+2):
            for y in range(y0-1,y0+2):
                if gb.on_the_map(x,y):
                    if gb._map[x][y].wall:
                        n += 1
                else:
                    n += 1
        return n



    def contains_a_space( self, gb, area ):
        for x in range( area.x, area.x + area.width ):
            for y in range( area.y, area.y + area.height ):
                if not gb._map[x][y].wall:
                    return True

    def carve_noise( self, gb, area ):
        myrect = pygame.Rect(0,0,5,5)
        for t in range( gb.width * gb.height // self.noise_throttle ):
            myrect.x = random.choice( list(range( area.x + 1 , area.x + area.width - myrect.width - 1)) )
            myrect.y = random.choice( list(range( area.y + 1 , area.y + area.height - myrect.height - 1)) )
            if self.contains_a_space( gb, myrect ):
                for x in range( myrect.x, myrect.x + myrect.width ):
                    for y in range( myrect.y, myrect.y + myrect.height ):
                        gb._map[x][y].wall = None

    def __call__( self, gb, area ):
        if self.do_carving:
            self.carve_noise( gb, area )
        temp = [[ int()
            for y in range(gb.height) ]
                for x in range(gb.width) ]
        # Perform the mutation several times in a row.
        for t in range( self.passes ):
            for x in range( area.x + 1, area.x + area.width - 1 ):
                for y in range( area.y + 1, area.y + area.height - 1 ):
                    if self.num_nearby_walls(gb,x,y) >= 5:
                        temp[x][y] = self.WALL_ON
                    else:
                        temp[x][y] = self.WALL_OFF
            for x in range( area.x + 1, area.x + area.width - 1 ):
                for y in range( area.y + 1, area.y + area.height - 1 ):
                    if temp[x][y] == self.WALL_OFF:
                        gb._map[x][y].wall = None
                    elif ( temp[x][y] == self.WALL_ON ) and gb.wall_wont_block( x, y ):
                        gb._map[x][y].wall = True

