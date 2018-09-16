import pbge
import gears
import pygame

# The color selector for the GearHead games has been called Cosplay since forever.

class ColorMenu(pbge.widgets.Widget):
    def __init__(self,dx, dy, w, h, colorset=None, **kwargs):
        super(ColorMenu,self).__init__(dx,dy,w,h,**kwargs)
        self.color_sprites = dict()
        self.buttons = list()
        x,y = 0,0
        for color in gears.ALL_COLORS:
            if colorset in color.SETS or colorset is None:
                sprite = pbge.image.Image("sys_color_menu_swatch.png",color=[color,color,color,color,color])
                self.color_sprites[color] = sprite

                self.children.append(pbge.widgets.ButtonWidget(x,y,sprite.frame_width,sprite.frame_height,sprite,on_click=self.click_swatch,data=color,tooltip=color.NAME,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT))
                x += sprite.frame_width
                if x > self.w:
                    x = 0
                    y += sprite.frame_height
                    if y > self.h:
                        break

    def click_swatch( self, button, ev ):
        pass


    @classmethod
    def explo_invoke(self,redraw):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = self(-200,-100,400,200)
        pbge.my_state.widgets.append(myui)
        keepgoing = True
        while keepgoing:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                redraw()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False

        pbge.my_state.widgets.remove(myui)

class ColorEditor(object):
    def __init__(self,proto_sprite,sprite_frame,channels):
        self.proto_sprite = proto_sprite
        self.sprite_frame = sprite_frame
        myrect = proto_sprite.get_rect(sprite_frame)
        self.display_sprite = pbge.image.Image(frame_width=myrect.width,frame_height=myrect.height)
        self.channels = channels

