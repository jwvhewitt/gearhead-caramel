import pygame
import math

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

def get_fline( x1, y1, x2, y2, speed):
    # Generate a line, but of floats, ending with the ints x2,y2.
    points = list()
    rng = math.sqrt( ( x1-x2 )**2 + ( y1-y2 )**2 )
    steps = int(rng/speed)
    fsteps = float(rng/speed)
    for t in range( 1, steps ):
        x = x1 + float( (x2-x1) * t )/fsteps
        y = y1 + float( (y2-y1) * t )/fsteps
        points.append((x,y))
    points.append((x2,y2))
    return points

class AnimOb( object ):
    """An animation for the map."""
    def __init__( self, sprite_name, width=54, height=54, pos=(0,0), start_frame=0, end_frame=0, ticks_per_frame=1, loop=0, y_off=0, delay=1 ):
        self.sprite = image.Image( sprite_name, width, height )
        self.start_frame = start_frame
        self.frame = start_frame
        self.end_frame = end_frame
        self.ticks_per_frame = ticks_per_frame
        self.counter = 0
        self.loop = loop
        self.y_off = y_off
        self.needs_deletion = False
        self.pos = pos
        self.delay = delay
        self.children = list()

    def update( self, view ):

        view.anims[self.pos].append( self )

        if self.delay > 0:
            self.delay += -1
        else:
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


    def render( self, view, screen, dest ):
        if not self.delay:
            mydest = pygame.Rect( dest )
            mydest.y += self.y_off
            self.sprite.render( screen, mydest, self.frame )

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
        self.itinerary = get_fline(start[0],start[1],dest[0],dest[1],speed)

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


