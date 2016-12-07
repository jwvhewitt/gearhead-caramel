import pygame
from . import my_state

ANCHOR_UPPERLEFT = (0,0)
ANCHOR_CENTER = (1,1)
ANCHOR_LOWERRIGHT = (2,2)

class Frect( object ):
    """Floating rect- changes position depending on the screen dimensions."""
    def __init__(self, dx, dy, w, h, anchor=ANCHOR_CENTER ):
        self.dx = dx
        self.dy = dy
        self.w = w
        self.h = h
        self.anchor = anchor

    def get_rect( self ):
        x0 = ( my_state.screen.get_width() // 2 ) * self.anchor[0]
        y0 = ( my_state.screen.get_height() // 2 ) * self.anchor[1]
        return pygame.Rect(self.dx+x0,self.dy+y0,self.w,self.h)


