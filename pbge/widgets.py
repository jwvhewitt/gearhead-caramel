import frects
from . import my_state,render_text
import pygame

# respond_event: Receives an event.
#   If the widget has a method corresponding to the event,
#   that method will be called.

class Widget( frects.Frect ):
    def __init__( self, dx, dy, w, h, data=None, on_click=None, tooltip=None, **kwargs ):
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

class ButtonWidget( Widget ):
    def __init__( self, dx, dy, w, h, sprite=None, frame=0, on_frame=0, off_frame=0, **kwargs ):
        super(ButtonWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.sprite = sprite
        self.frame = frame
        self.on_frame = on_frame
        self.off_frame = off_frame
    def render( self ):
        if self.active:
            self.sprite.render(self.get_rect(),self.frame)

class RadioButtonWidget( Widget ):
    def __init__( self, dx, dy, w, h, sprite=None, buttons=(), spacing=2, **kwargs ):
        # buttons is a list of tuples of (on_frame,off_frame,on_click)
        super(RadioButtonWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.sprite = sprite
        self.buttons = list()
        self.spacing = spacing
        ddx = 0
        for b in buttons:
            self.buttons.append(ButtonWidget(ddx,0,sprite.frame_width,sprite.frame_height,sprite,frame=b[1],on_frame=b[0],off_frame=b[1],on_click=self.click_radio,data=b[2],parent=self,anchor=frects.ANCHOR_UPPERLEFT))
            ddx += sprite.frame_width + self.spacing
        self.buttons[0].frame = self.buttons[0].on_frame
        self.active_button = self.buttons[0]

    def click_radio( self, button, ev ):
        self.active_button.frame = self.active_button.off_frame
        self.active_button = button
        button.frame = button.on_frame
        if button.data:
            button.data(button,ev)

    def remove( self ):
        for b in self.buttons:
            b.remove()
        my_state.widgets.remove(self)



