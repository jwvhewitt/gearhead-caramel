import frects
from . import my_state,render_text
import pygame

# respond_event: Receives an event.
#   If the widget has a method corresponding to the event,
#   that method will be called.

class Widget( frects.Frect ):
    def __init__( self, dx, dy, w, h, data=None, on_click=None, **kwargs ):
        super(Widget, self).__init__(dx,dy,w,h,**kwargs)
        self.data = data
        self.active = True
        self.tooltip = tooltip
        self.on_click = on_click
        my_state.widgets.append(self)
    def respond_event( self, ev ):
        if self.on_click and (ev.type == pygame.MOUSEBUTTONUP) and (ev.button == 1) and self.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.on_click(self,ev)
    def render( self ):
        pass
    def remove( self ):
        # No real cleanup needed; just remove the widget from the state list.
        my_state.widgets.remove(self)



