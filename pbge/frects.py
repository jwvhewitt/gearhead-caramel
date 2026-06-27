from . import my_state
import sdl2

ANCHOR_UPPERLEFT = (0,0)
ANCHOR_UPPERRIGHT = (2,0)
ANCHOR_CENTER = (1,1)
ANCHOR_LOWERLEFT = (0,2)
ANCHOR_LOWERRIGHT = (2,2)
ANCHOR_TOP = (1,0)
ANCHOR_LEFT = (0,1)
ANCHOR_RIGHT = (2,1)
ANCHOR_BOTTOM = (1,2)


class PyRect(sdl2.SDL_Rect):
    # Recreate as much PyGame functionality as I use down here.
    def copy(self):
        """copy the rectangle"""
        return PyRect(self.x, self.y, self.w, self.h)

    def inflate_ip(self, x, y):
        """grow or shrink the rectangle size, in place"""
        self.x -= x//2
        self.w += x
        self.y -= y//2
        self.h += y

    def inflate(self, x , y):
        """grow or shrink the rectangle size"""
        nurect = self.copy()
        nurect.inflate_ip(x,y)
        return nurect

    def clamp_ip(self, other_r: sdl2.SDL_Rect):
        """moves the rectangle inside another, in place"""
        # Note: Don't expect good behaviour if you try to shove a big rect into a small one.
        if self.x < other_r.x:
            self.x = other_r.x
        elif self.x + self.w > other_r.x + other_r.w:
            self.x = other_r.x + other_r.w - self.w
        if self.y < other_r.y:
            self.y = other_r.y
        elif self.y + self.h > other_r.y + other_r.h:
            self.y = other_r.y + other_r.h - self.h

    def clamp(self, other_r: sdl2.SDL_Rect):
        """moves the rectangle inside another"""
        nurect = self.copy()
        nurect.clamp_ip(other_r)
        return nurect

    def contains(self, other_r: sdl2.SDL_Rect):
        """test if one rectangle is inside another"""
        return (
            self.right >= other_r.right and
            self.left <= other_r.left and
            self.top >= other_r.top and
            self.bottom <= other_r.bottom
        )

    def collidepoint(self, point):
        """test if a point is inside a rectangle"""
        return (
            self.left <= point[0] < self.right and
            self.top <= point[1] < self.bottom
        )

    def colliderect(self, other_r: sdl2.SDL_Rect):
        """test if two rectangles overlap"""
        return not (self.right < other_r.left
                or self.left > other_r.right
                or self.bottom < other_r.top
                or self.top > other_r.bottom)

    def collidelist(self, mylist):
        """test if at least one rectangle in a list intersects"""
        return any([self.colliderect(r) for r in mylist])

    # Needed properties:
    # Note that "right", "bottom", and all associated values point to one tile outside
    # the actual bounds of the rect. That's because this is how PyGame does it.
    # top, left, bottom, right
    # topleft, bottomleft, topright, bottomright
    # midtop, midleft, midbottom, midright
    # center, centerx, centery
    # size, width, height

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, nuval):
        self.y = nuval

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, nuval):
        self.x = nuval

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, nuval):
        self.y = nuval - self.h

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, nuval):
        self.x = nuval - self.w

    @property
    def topleft(self):
        return self.x, self.y

    @topleft.setter
    def topleft(self, nuval):
        self.x, self.y = nuval

    @property
    def bottomleft(self):
        return self.x, self.y + self.h

    @bottomleft.setter
    def bottomleft(self, nuval):
        self.x = nuval[0]
        self.y = nuval[1] - self.h

    @property
    def topright(self):
        return self.x + self.w, self.y

    @topright.setter
    def topright(self, nuval):
        self.x = nuval[0] - self.w
        self.y = nuval[1]

    @property
    def bottomright(self):
        return self.x + self.w, self.y + self.h

    @bottomright.setter
    def bottomright(self, nuval):
        self.x = nuval[0] - self.w
        self.y = nuval[1] - self.h

    @property
    def midtop(self):
        return self.x + self.w//2, self.y

    @midtop.setter
    def midtop(self, nuval):
        self.x = nuval[0] - self.w//2
        self.y = nuval[1]

    @property
    def midleft(self):
        return self.x, self.y + self.h//2

    @midleft.setter
    def midleft(self, nuval):
        self.x = nuval[0]
        self.y = nuval[1] - self.h//2

    @property
    def midbottom(self):
        return self.x + self.w//2, self.y + self.h

    @midbottom.setter
    def midbottom(self, nuval):
        self.x = nuval[0] - self.w//2
        self.y = nuval[1] - self.h

    @property
    def midright(self):
        return self.x + self.w, self.y + self.h//2

    @midright.setter
    def midright(self, nuval):
        self.x = nuval[0] - self.w
        self.y = nuval[1] - self.h//2

    @property
    def center(self):
        return self.x + self.w//2, self.y + self.h//2

    @center.setter
    def center(self, nuval):
        self.x = nuval[0] - self.w//2
        self.y = nuval[1] - self.h//2

    @property
    def centerx(self):
        return self.x + self.w//2

    @centerx.setter
    def centerx(self, nuval):
        self.x = nuval - self.w//2

    @property
    def centery(self):
        return self.y + self.h//2

    @centery.setter
    def centery(self, nuval):
        self.y = nuval - self.h//2

    @property
    def size(self):
        return self.w, self.h

    @size.setter
    def size(self, nuval):
        self.w, self.h = nuval

    @property
    def width(self):
        return self.w

    @width.setter
    def width(self, nuval):
        self.w = nuval

    @property
    def height(self):
        return self.h

    @height.setter
    def height(self, nuval):
        self.h = nuval



class Frect( object ):
    """Floating rect- changes position depending on the screen dimensions."""
    def __init__(self, dx, dy, w, h, anchor=ANCHOR_CENTER, parent=None ):
        self.dx = dx
        self.dy = dy
        self.w = w
        self.h = h
        self.anchor = anchor
        self.parent = parent

    def get_dict(self):
        return {
            "dx": self.dx, "dy": self.dy, "w": self.w, "h": self.h,
            "anchor": self.anchor, "parent": self.parent
        }

    def get_rect( self ):
        if self.parent:
            prect = self.parent.get_rect()
            x0 = prect.left + ( prect.w // 2 ) * self.anchor[0]
            y0 = prect.top + ( prect.h // 2 ) * self.anchor[1]
        else:
            x0 = ( my_state.screen.logical_size[0] // 2 ) * self.anchor[0]
            y0 = ( my_state.screen.logical_size[1] // 2 ) * self.anchor[1]
        return PyRect(self.dx+x0,self.dy+y0,self.w,self.h)


