import pbge
import gears
import pygame


# The color selector for the GearHead games has been called Cosplay since forever.

class ColorButtonWidget(pbge.widgets.ButtonWidget):
    def __init__(self, dx, dy, w, h, color_edit, **kwargs):
        # call_fun is a function to call with the color of the swatch clicked.
        super(ColorButtonWidget, self).__init__(dx, dy, w, h, **kwargs)
        self.color_edit = color_edit
    def render( self ):
        if self.color_edit and self.data is self.color_edit.colors[self.color_edit.active_menu]:
            self.sprite.render(self.get_rect(), 1)
        else:
            self.sprite.render(self.get_rect(), 0)

class ColorMenu(pbge.widgets.Widget):
    def __init__(self, dx, dy, w, h, call_fun, colorset=None, color_edit=None, **kwargs):
        # call_fun is a function to call with the color of the swatch clicked.
        super(ColorMenu, self).__init__(dx, dy, w, h, **kwargs)
        self.color_sprites = dict()
        self.call_fun = call_fun
        self.buttons = list()
        x, y = 0, 0
        for color in gears.ALL_COLORS:
            if colorset in color.SETS or colorset is None:
                sprite = pbge.image.Image("sys_color_menu_swatch.png", 24, 36, color=[color, color, color, color, color])
                self.color_sprites[color] = sprite

                self.children.append(ColorButtonWidget(x, y, sprite.frame_width, sprite.frame_height,color_edit=color_edit, sprite=sprite,
                                                               on_click=self.click_swatch, data=color,
                                                               tooltip=color.NAME, parent=self,
                                                               anchor=pbge.frects.ANCHOR_UPPERLEFT))
                x += sprite.frame_width
                if x > self.w:
                    x = 0
                    y += sprite.frame_height
                    if y > self.h:
                        break

    def click_swatch(self, button, ev):
        self.call_fun(button.data)


class ColorEditor(pbge.widgets.Widget):
    def __init__(self, proto_sprite, sprite_frame, channel_filters, colors=None, **kwargs):
        super(ColorEditor, self).__init__(20, -200, 239, 400, **kwargs)
        self.proto_sprite = proto_sprite
        self.sprite_frame = sprite_frame
        myrect = proto_sprite.get_rect(sprite_frame)
        self.display_sprite = pbge.image.Image(frame_width=myrect.width, frame_height=myrect.height)
        self.display_dest = pbge.frects.Frect(-20-myrect.width,-myrect.height//2,myrect.width,myrect.height)
        self.channel_filters = channel_filters
        self.channel_menus = dict()
        for t in range(5):
            chanmenu = self.create_menu(channel_filters[t])
            chanmenu.active = False
            self.channel_menus[t] = chanmenu
        self.active_menu = 0
        self.channel_menus[0].active = True
        self.radio_pages = pbge.widgets.RadioButtonWidget(0,0,200,20,sprite=pbge.image.Image("sys_color_editor_tabs.png",40,20),buttons=((0,1,self.click_radio,"Red Channel"),(2,3,self.click_radio,"Yellow Channel"),(4,5,self.click_radio,"Green Channel"),(6,7,self.click_radio,"Cyan Channel"),(8,9,self.click_radio,"Magenta Channel")),spacing=0,anchor=pbge.frects.ANCHOR_UPPERLEFT,parent=self)
        self.children.append(self.radio_pages)
        if not colors or len(colors) < 5:
            colors = (gears.color.ChannelRed,gears.color.ChannelYellow,gears.color.ChannelGreen,gears.color.ChannelCyan,gears.color.ChannelMagenta)
        self.colors = list(colors)
        self.recolor_sprite()

    def click_swatch(self,new_color):
        if new_color != self.colors[self.active_menu]:
            self.colors[self.active_menu] = new_color
            self.recolor_sprite()

    def click_radio(self,button,ev):
        # A radio button has been clicked. Switch the page.
        nu_menu = self.channel_menus[button.on_frame // 2]
        self.channel_menus[self.active_menu].active = False
        self.active_menu = button.on_frame // 2
        nu_menu.active = True

    def recolor_sprite(self):
        # Copy proto_sprite to display_sprite
        self.proto_sprite.render(frame=self.sprite_frame,dest_surface=self.display_sprite.bitmap)
        # Recolor the display sprite.
        self.display_sprite.recolor(self.colors)

    def create_menu(self,colorset):
        cm = ColorMenu(0,25,self.w,self.h-25,self.click_swatch,colorset,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT,color_edit=self)
        self.children.append(cm)
        return cm

    def render(self):
        pbge.default_border.render(self.get_rect())
        self.display_sprite.render(self.display_dest.get_rect())

    @classmethod
    def explo_invoke(cls, redraw):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(pbge.image.Image("mecha_buruburu.png",400,600),0,channel_filters=gears.color.MECHA_COLOR_CHANNELS,colors=list(gears.factions.TerranDefenseForce.mecha_colors))
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
                elif ev.key == pygame.K_F1:
                    pygame.image.save(myui.display_sprite.bitmap, pbge.util.user_dir("out.png"))

        pbge.my_state.widgets.remove(myui)
        return myui.colors
