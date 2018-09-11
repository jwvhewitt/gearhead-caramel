import pbge
import pygame
from pbge import my_state,draw_text,default_border,anim_delay

import gears

class ConvoVisualizer(object):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = pbge.frects.Frect(0,-125,350,100)
    MENU_AREA = pbge.frects.Frect(0,0,350,80)
    PORTRAIT_AREA = pbge.frects.Frect(-370,-300,400,600)
    PILOT_AREA = pbge.frects.Frect(-350,-250,100,100)
    
    def __init__(self,npc):
        pilot = npc.get_pilot()
        npc = npc.get_root()
        self.npc = pilot
        if hasattr(npc, "get_portrait"):
            #self.npc_sprite = npc.get_portrait()
            self.portrait = gears.portraits.Portrait()
            self.portrait.random_portrait()
            self.npc_sprite = self.portrait.build_portrait()
            self.npc_sprite.recolor(gears.random_character_colors())
        else:
            self.npc_sprite = None
        if pilot is not npc and hasattr(pilot, "get_portrait"):
            self.pilot_sprite = pilot.get_portrait()
        else:
            self.pilot_sprite = None
        self.bottom_sprite = pbge.image.Image('sys_wintermocha_convoborder.png',32,200)
        self.text = ''
    def get_portrait_area(self):
        if self.npc_sprite:
            mydest = self.npc_sprite.get_rect(0)
            mydest.midbottom = (my_state.screen.get_width()//2-170,my_state.screen.get_height()//2+300)
        else:
            return self.PORTRAIT_AREA.get_rect()
        return mydest
    def render(self,draw_menu_rect=True):
        if my_state.view:
            my_state.view()

        self.bottom_sprite.tile(pygame.Rect(0,my_state.screen.get_height()//2+100,my_state.screen.get_width(),200))
        if self.npc_sprite:
            self.npc_sprite.render(self.get_portrait_area())
        if self.pilot_sprite:
            default_border.render(self.PILOT_AREA.get_rect())
            self.pilot_sprite.render(self.PILOT_AREA.get_rect(),1)

        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(my_state.medium_font,self.text,text_rect)
        if draw_menu_rect:
            default_border.render(self.MENU_AREA.get_rect())

    def rollout(self):
        bx = my_state.screen.get_width()
        t = 0
        myrect = self.PORTRAIT_AREA.get_rect()
        myrect.x = -400
        while (myrect.x < self.get_portrait_area().x):
            if my_state.view:
                my_state.view()
            self.bottom_sprite.tile(pygame.Rect(max(0,bx-t*75),my_state.screen.get_height()//2+100,my_state.screen.get_width(),200))
            if self.npc_sprite:
                self.npc_sprite.render(myrect)

            my_state.do_flip()
            myrect.x += 25
            anim_delay()
            t += 1

    def get_menu(self):
        return pbge.rpgmenu.Menu(self.MENU_AREA.dx,self.MENU_AREA.dy,self.MENU_AREA.w,self.MENU_AREA.h,border=None,predraw=self.render,font=my_state.medium_font)

