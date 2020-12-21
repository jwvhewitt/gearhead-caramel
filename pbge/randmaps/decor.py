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

    def windowize( self, gb, room ):
        t = 0
        for p in room.get_west_north_wall_points(gb):
            if t % 3 == 1 and room.is_basic_wall(gb,p[0],p[1]) and not gb.get_decor(p[0],p[1]):
                gb.set_decor(p[0], p[1], self.WIN_DECOR)
            t += 1

    def draw_wall_decor( self, gb, x, y ):
        gb._map[x][y].decor = random.choice(self.WALL_DECOR)

    def draw_floor_decor( self, gb, x, y ):
        gb._map[x][y].decor = random.choice(self.FLOOR_DECOR)

    def __call__( self, gb, room ):
        good_wall_spots = list()
        good_floor_spots = list()
        for x in range(room.area.x, room.area.x + room.area.width-1):
            for y in range(room.area.y, room.area.y + room.area.height-1):
                pos = (x,y)
                if room.is_basic_wall(gb,x,y) and room.is_good_spot_for_wall_decor(gb,pos):
                    good_wall_spots.append( pos )
                elif x > 0 and y > 0 and \
                  not gb._map[x][y].blocks_walking() and not gb._map[x][y].wall \
                  and not gb._map[x][y].decor and gb.wall_wont_block(x,y):
                    good_floor_spots.append( pos )
        for pos in room.get_west_north_wall_points(gb):
            if pos not in good_wall_spots:
                good_wall_spots.append(pos)
        for m in gb.contents:
            if hasattr(m,"pos"):
                if m.pos in good_wall_spots:
                    good_wall_spots.remove( m.pos )
                elif m.pos in good_floor_spots:
                    good_floor_spots.remove( m.pos )

        if self.FLOOR_DECOR:
            for t in range(max(int(len(good_floor_spots) * self.FLOOR_FILL_FACTOR),random.randint(1,10))):
                if good_floor_spots:
                    x,y = random.choice( good_floor_spots )
                    if gb.wall_wont_block(x,y):
                        self.draw_floor_decor(gb,x,y)
                else:
                    break
        if self.WALL_DECOR:
            for t in range(max(int( len(good_wall_spots) * self.WALL_FILL_FACTOR),random.randint(1,6))):
                x,y = random.choice( good_wall_spots )
                if room.is_good_spot_for_wall_decor( gb,(x,y) ):
                    self.draw_wall_decor(gb,x,y)

        if self.WIN_DECOR:
            self.windowize(gb,room)

class ColumnsDecor(OmniDec):
    FLOOR_FILL_FACTOR = 0.9
    def __call__(self, gb, room):
        good_wall_spots = list()
        for x in range(room.area.x, room.area.x + room.area.width - 1):
            for y in range(room.area.y, room.area.y + room.area.height - 1):
                pos = (x, y)
                if room.is_basic_wall(gb, x, y) and room.is_good_spot_for_wall_decor(gb, pos):
                    good_wall_spots.append(pos)
        for pos in room.get_west_north_wall_points(gb):
            if pos not in good_wall_spots:
                good_wall_spots.append(pos)
        for m in gb.contents:
            if hasattr(m, "pos"):
                if m.pos in good_wall_spots:
                    good_wall_spots.remove(m.pos)

        if self.FLOOR_DECOR:
            num_columns = ( room.area.width - 3 ) // 2
            for t in range(num_columns):
                x = t * 2 + room.area.x + 2
                for y in range(room.area.y + 2, room.area.bottom - 2):
                    if random.random() <= self.FLOOR_FILL_FACTOR:
                        self.draw_floor_decor(gb, x, y)
        if self.WALL_DECOR and good_wall_spots:
            for t in range(max(int(len(good_wall_spots) * self.WALL_FILL_FACTOR), random.randint(1, 6))):
                x, y = random.choice(good_wall_spots)
                if room.is_good_spot_for_wall_decor(gb, (x, y)):
                    self.draw_wall_decor(gb, x, y)

        if self.WIN_DECOR:
            self.windowize(gb, room)

class OfficeDecor(OmniDec):
    FLOOR_FILL_FACTOR = 0.4
    DESK_TERRAIN = ()
    CHAIR_TERRAIN = ()
    def __call__(self, gb, room):
        good_wall_spots = list()
        for x in range(room.area.x, room.area.x + room.area.width - 1):
            for y in range(room.area.y, room.area.y + room.area.height - 1):
                pos = (x, y)
                if room.is_basic_wall(gb, x, y) and room.is_good_spot_for_wall_decor(gb, pos):
                    good_wall_spots.append(pos)
        for pos in room.get_west_north_wall_points(gb):
            if pos not in good_wall_spots:
                good_wall_spots.append(pos)
        for m in gb.contents:
            if hasattr(m, "pos"):
                if m.pos in good_wall_spots:
                    good_wall_spots.remove(m.pos)

        num_columns = ( room.area.width - 3 ) // 3
        num_rows = ( room.area.height - 3 ) // 3
        for col in range(num_columns):
            x = col * 3 + room.area.x + 2
            for row in range(num_rows):
                y = row * 3 + room.area.y + 2
                if random.random() <= self.FLOOR_FILL_FACTOR:
                    if self.CHAIR_TERRAIN:
                        gb.set_decor(x,y,random.choice(self.CHAIR_TERRAIN))
                    if self.DESK_TERRAIN:
                        gb.set_decor(x,y+1,random.choice(self.DESK_TERRAIN))
        if self.WALL_DECOR and good_wall_spots:
            for t in range(max(int(len(good_wall_spots) * self.WALL_FILL_FACTOR), random.randint(1, 6))):
                x, y = random.choice(good_wall_spots)
                if room.is_good_spot_for_wall_decor(gb, (x, y)):
                    self.draw_wall_decor(gb, x, y)

        if self.WIN_DECOR:
            self.windowize(gb, room)
