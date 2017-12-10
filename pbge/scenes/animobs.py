import pygame
import math
from .. import image, my_state

def get_line( x1, y1, x2, y2):
    # Bresenham's line drawing algorithm, as obtained from RogueBasin.
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points

def get_fline( p1, p2, speed):
    # Generate a line, but of floats, ending with the ints x2,y2.
    points = list()
    rng = math.sqrt( ( p1[0]-p2[0] )**2 + ( p1[1]-p2[1] )**2 )
    steps = int(rng/speed)
    fsteps = float(rng/speed)
    for t in range( 0, steps ):
        newpoint = list()
        for coord in range(len(p1)):
            newpoint.append( p1[coord] + float( (p2[coord]-p1[coord]) * t )/fsteps)
        points.append(newpoint)
    points.append(p2)
    return points

class AnimOb( object ):
    """An animation for the map."""
    def __init__( self, sprite_name=None, width=64, height=64, pos=(0,0), start_frame=0, end_frame=0, ticks_per_frame=1, loop=0, x_off=0, y_off=0, delay=1 ):
        self.sprite = image.Image( sprite_name or self.DEFAULT_SPRITE_NAME, width, height )
        self.start_frame = start_frame
        self.frame = start_frame or self.DEFAULT_START_FRAME
        self.end_frame = end_frame or self.DEFAULT_END_FRAME
        self.ticks_per_frame = ticks_per_frame
        self.counter = 0
        self.loop = loop
        self.x_off = x_off
        self.y_off = y_off
        self.needs_deletion = False
        self.pos = pos
        self.delay = delay
        self.children = list()
    DEFAULT_SPRITE_NAME = ''
    DEFAULT_START_FRAME = 0
    DEFAULT_END_FRAME= 0

    def update( self, view ):
        if self.delay > 0:
            self.delay += -1
        else:
            view.anims[view.PosToKey(self.pos)].append( self )
            self.counter += 1
            if self.counter >= self.ticks_per_frame:
                self.frame += 1
                self.counter = 0

            if self.frame > self.end_frame:
                self.loop += -1
                if self.loop < 0:
                    self.frame = self.end_frame
                    self.needs_deletion = True
                else:
                    self.frame = self.start_frame
                    self.counter = 0


    def render( self, foot_pos, view ):
        if not self.delay:
            mydest = pygame.Rect(0,0,self.sprite.frame_width,self.sprite.frame_height)
            mydest.midbottom = foot_pos
            mydest.x += self.x_off
            mydest.y += self.y_off
            self.sprite.render( mydest, self.frame )

class ShotAnim( AnimOb ):
    """An AnimOb which moves along a line."""
    def __init__( self, sprite_name=None, width=64, height=64, start_pos=(0,0), end_pos=(0,0), frame=0, speed=None, set_frame_offset=True, x_off=0, y_off=0, delay=0 ):
        self.sprite = image.Image( sprite_name or self.DEFAULT_SPRITE_NAME, width, height )
        if set_frame_offset:
            self.frame = frame + self.dir_frame_offset( self.isometric_pos(*start_pos), self.isometric_pos(*end_pos) )
        else:
            self.frame = frame
        self.counter = 0
        self.x_off = x_off
        self.y_off = y_off
        self.needs_deletion = False
        self.pos = start_pos
        speed = speed or self.DEFAULT_SPEED
        self.itinerary = get_fline( start_pos, end_pos, speed )
        self.children = list()
        self.delay = delay
    DEFAULT_SPRITE_NAME = ''
    DEFAULT_SPEED = 0.5

    def relative_x( self, x, y ):
        """Return the relative x position of this tile, ignoring offset."""
        return ( x * 2 ) - ( y * 2 )

    def relative_y( self, x, y ):
        """Return the relative y position of this tile, ignoring offset."""
        return y + x

    def isometric_pos(self,x,y):
        return self.relative_x(x,y),self.relative_y(x,y)

    def dir_frame_offset( self, start_pos, end_pos ):
        # There are 8 sprites for each projectile type, one for each of 
        # the eight directions. Determine the direction which best suits 
        # this vector. 
        # Sprite 0 is pointing 12 o'clock and they go clockwise from there.
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]

        # Note that much of the following is magic translated from Pascal.
        # I must've put some thought into it, but it looks mysterious now.
        if dx == 0:
            if dy > 0:
                return 2
            else:
                return 6
        else:
            slope = float(dy)/float(dx)
            if slope > 1.73:
                tmp = 2
            elif slope > 0.27:
                tmp = 1
            elif slope > -0.27:
                tmp = 0
            elif slope > -1.73:
                tmp = 7
            else:
                tmp = 6
            if dx > 0:
                return tmp
            else:
                return ( tmp + 4 ) % 8



    def update( self, view ):
        if self.delay > 0:
            self.delay += -1
        else:
            view.anims[view.PosToKey(self.pos)].append( self )
            self.counter += 1
            if self.counter >= len( self.itinerary ):
                self.needs_deletion = True
            else:
                self.pos = self.itinerary[ self.counter ]

class Caption( AnimOb ):
    def __init__(self, txt=None, pos=(0,0), width=128, loop=16, color=None, delay=1, y_off=0 ):
        txt = txt or self.DEFAULT_TEXT
        color = color or self.DEFAULT_COLOR
        self.sprite = image.TextImage( txt, width, color=color )
        self.frame = 0
        self.counter = 0
        self.loop = loop
        self.x_off = 0
        self.y_off = 0
        self.dy_off = y_off
        self.needs_deletion = False
        self.pos = pos
        self.delay = delay
        self.children = list()
    DEFAULT_TEXT = '???'
    DEFAULT_COLOR = (250,250,250)

    def update( self, view ):
        if self.delay > 0:
            self.delay += -1
        else:
            view.anims[view.PosToKey(self.pos)].append( self )
            self.counter += 1
            self.y_off = -32 - 2*self.counter + self.dy_off
            if self.counter >= self.loop:
                self.needs_deletion = True



class MoveModel( object ):
    def __init__( self, model, start=None, dest=(0,0), speed=0.1, delay=0 ):
        self.model = model
        self.speed = speed
        self.dest = dest
        self.delay = delay
        self.step = 0
        self.needs_deletion = False
        self.children = list()
        if not start:
            start = model.pos
        self.itinerary = get_fline(start,dest,speed)

    def update( self, view ):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.itinerary:
            self.model.pos = self.itinerary.pop(0)
            if not self.itinerary:
                self.needs_deletion = True
        else:
            self.needs_deletion = True


