import pbge
import pygame
from pbge import my_state,draw_text,default_border,anim_delay

import gears

class LancemateConvoItem(pbge.widgets.LabelWidget):
    PORTRAIT_AREA = (-120,50,100,100)
    SORT_LAYER = -1
    def __init__(self,msg,data,npc,msg_form = '{} says "{}"', **kwargs):
        msg = msg_form.format(npc,msg)
        super().__init__(0,0,0,0,msg,data=data,**kwargs)
        self.npc = npc
        self.portrait = npc.get_portrait()
        
    def _render(self,delta):
        super().render(delta)
        if self.should_hilight(self):
            mydest = self.get_rect()
            mydest.x -= 125
            mydest.w = 100
            mydest.h = 100
            pbge.default_border.render(mydest)
            self.portrait.render(mydest,1)


class ConvoVisualizer(object):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu_frect" methods.
    TEXT_AREA = pbge.frects.Frect(0,-125,350,180)
    MENU_AREA = pbge.frects.Frect(0,80,350,174)
    NAME_AREA = pbge.frects.Frect(25,-185,300,35)
    REACT_AREA = pbge.frects.Frect(290,-185,35,35)
    PORTRAIT_AREA = pbge.frects.Frect(-370,-300,400,600)
    PILOT_AREA = pbge.frects.Frect(-350,-250,100,100)
    
    def __init__(self,npc,camp,pc=None, do_rollout=True):
        pilot = npc.get_pilot()
        npc = npc.get_root()
        self.npc = pilot
        if hasattr(npc, "get_portrait"):
            self.npc_sprite: gears.image.Image = npc.get_portrait()  # pyright: ignore[reportRedeclaration]
        else:
            self.npc_sprite: gears.image.Image = None
        if pilot is not npc and hasattr(pilot, "get_portrait"):
            self.pilot_sprite: gears.image.Image = pilot.get_portrait()  # pyright: ignore[reportRedeclaration]
        else:
            self.pilot_sprite: gears.image.Image = None
        self.npc_desc = self.npc.get_text_desc(camp)
        self.camp = camp
        self.bottom_sprite = pbge.image.Image(camp.convoborder)
        self.react_sprite = pbge.image.Image('sys_reaction_emoji.png',35,35)
        self.text = ''
        if pc:
            self.pc = pc.get_pilot()
        else:
            self.pc = None
        self.sl = pbge.StretchyLayer()

        self.is_rolling_out = do_rollout
        self.rollout_timer = 0
    
    def get_portrait_area(self):
        if self.npc_sprite:
            mydest = self.npc_sprite.get_rect(0)
            mydest.midbottom = (self.sl.surf.get_width()//2-170,self.sl.surf.get_height())
        else:
            return pygame.Rect(self.sl.surf.get_width()//2-370,0,400,600)
        return mydest
    
    def get_pilot_area(self):
        return pygame.Rect(self.sl.surf.get_width()//2-350,50,100,100)

    def render(self, delta):
        self.sl.clear()

        self.bottom_sprite.tile(pygame.Rect(0,self.sl.surf.get_height()-200,self.sl.surf.get_width(),200), dest_surface=self.sl.surf)
        if self.npc_sprite:
            self.npc_sprite.render(self.get_portrait_area(), dest_surface=self.sl.surf)
        if self.pilot_sprite:
            myrect = self.get_pilot_area()
            default_border.render(myrect, dest_surface=self.sl.surf)
            self.pilot_sprite.render(myrect, 1, dest_surface=self.sl.surf)
        self.sl.render()

        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(my_state.medium_font,self.text,text_rect)

        default_border.render(self.MENU_AREA.get_rect())

        name_rect = self.NAME_AREA.get_rect()
        default_border.render(name_rect)
        draw_text(my_state.big_font,str(self.npc),name_rect,color=pbge.WHITE,justify=0)
        name_rect.y += my_state.big_font.get_linesize()
        draw_text(my_state.small_font,self.npc_desc,name_rect,color=pbge.GREY,justify=0)

        if self.pc:
            react_level = min(max(( self.npc.get_reaction_score(self.pc,self.camp) + 99 )//40, 0), 4)
            self.react_sprite.render(self.REACT_AREA.get_rect(),react_level)

    def rollout(self):
        bx = self.sl.get_width()
        pxspeed = bx//15
        t = 0
        myrect = self.get_portrait_area()
        myrect.x = -400
        while (myrect.x < self.get_portrait_area().x):
            if my_state.view:
                my_state.view()
            self.sl.clear()
            self.bottom_sprite.tile(pygame.Rect(max(0,bx-t*pxspeed),self.sl.get_height()//2+100,self.sl.get_width(),200), dest_surface=self.sl.surf)
            if self.npc_sprite:
                self.npc_sprite.render(myrect, dest_surface=self.sl.surf)

            self.sl.render()
            my_state.do_flip()
            myrect.x += pxspeed//2
            anim_delay()
            t += 1

    def get_menu_frect(self):
        return self.MENU_AREA

