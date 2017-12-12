import pbge
import gears
from gears import info
import pygame

class MoveWidget( pbge.widgets.Widget ):
    def __init__( self, camp, mover, **kwargs ):
        # buttons is a list of tuples of (on_frame,off_frame,on_click)
        super(MoveWidget, self).__init__(-383,-5,383,57,anchor=pbge.frects.ANCHOR_UPPERRIGHT,**kwargs)
        self.camp = camp
        self.mover = mover

        self.sprite = pbge.image.Image('sys_tacticsinterface_movewidget.png',383,57)
        self.counter_sprite = pbge.image.Image('sys_tacticsinterface_actioncounter.png',32,12)

        pilot = self.mover.get_pilot()
        pilot_name = pbge.widgets.LabelWidget(12,15,208,21,str(pilot),font=pbge.BIGFONT,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT)
        self.children.append(pilot_name)
        if pilot is not mover:
            mecha_name = pbge.widgets.LabelWidget(26,37,212,14,str(mover),color=pbge.WHITE,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT)
            self.children.append(mecha_name)
        self.mm_label = pbge.widgets.LabelWidget(253,37,100,14,mover.mmode.NAME,color=pbge.WHITE,parent=self,justify=0,anchor=pbge.frects.ANCHOR_UPPERLEFT)
        self.children.append(self.mm_label)

    def open_dropdown_menu( self ):
        mymenu = pbge.rpgmenu.Menu(-130,32,100,200,anchor=pbge.frects.ANCHOR_UPPERRIGHT)
        return mymenu

    def render( self ):
        if self.active:
            self.sprite.render(self.get_rect(),0)

            # Draw the action point counters
            dest = self.get_rect()
            dest.left += 231
            dest.top += 18
            num_ap = min( self.camp.fight.cstat[self.mover].action_points, 4)
            for t in range( num_ap ):
                self.counter_sprite.render(dest,0)
                dest.left += 37

            if num_ap < 4 and self.camp.fight.cstat[self.mover].mp_remaining > 0:
                self.counter_sprite.render(dest,1)


class MovementUI( object ):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    SC_TRAILMARKER = 6
    SC_ZEROCURSOR = 7
    def __init__(self, camp, mover):
        self.camp = camp
        self.mover = mover
        self.origin = mover.pos
        self.needs_tile_update = True

        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png',64,64)
        self.my_widget = MoveWidget(camp,mover,on_click=self.open_movemode_menu)
        pbge.my_state.widgets.append(self.my_widget)

    def render( self ):
        pbge.my_state.view.overlays.clear()
        pbge.my_state.view.overlays[ self.origin ] = (self.cursor_sprite,self.SC_ORIGIN)

        if pbge.my_state.view.mouse_tile in self.nav.cost_to_tile:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (
              self.cursor_sprite,self.SC_ZEROCURSOR+min(4,self.camp.fight.ap_needed(self.mover,self.nav,pbge.my_state.view.mouse_tile)))
            mypath = self.nav.get_path(pbge.my_state.view.mouse_tile)
            for p in mypath[1:-1]:
                pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_TRAILMARKER)
        else:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_VOIDCURSOR)

        pbge.my_state.view()

        mmecha = pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile)
        if mmecha:
            x,y = pygame.mouse.get_pos()
            y -= 64
            info.MechaStatusDisplay((x,y),mmecha[0])

        #pbge.draw_text(pbge.SMALLFONT,'This is an example\n of an overly long line that I intend to split into multiple lines using this function.',pygame.rect.Rect(50,50,200,100))

        pbge.my_state.do_flip()

    def change_movemode( self, new_mm ):
        self.mover.mmode = new_mm
        self.camp.fight.cstat[self.mover].mp_remaining = 0
        self.my_widget.mm_label.text = new_mm.NAME
        self.needs_tile_update = True

    def open_movemode_menu( self, button, ev ):
        original_mm = self.mover.mmode
        mymenu = self.my_widget.open_dropdown_menu()
        for mm in gears.geffects.MOVEMODE_LIST:
            if self.mover.get_speed(mm) > 0:
                mymenu.add_item('{} ({}dpr)'.format(mm.NAME,self.mover.get_speed(mm)),mm)
        mymenu.set_item_by_value(original_mm)
        new_mm = mymenu.query()
        if new_mm in gears.geffects.MOVEMODE_LIST and new_mm != original_mm:
            self.change_movemode( new_mm )

    def update_tiles( self ):
        # Step one: figure out which tiles can be reached from here.
        self.origin = self.mover.pos
        self.nav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene,self.origin,self.camp.fight.cstat[self.mover].action_points*self.mover.get_current_speed()+self.camp.fight.cstat[self.mover].mp_remaining,self.mover.mmode,self.camp.scene.get_blocked_tiles())

    def update( self, ev ):
        # We just got an event. Deal with it.
        if self.needs_tile_update:
            self.update_tiles()
            self.needs_tile_update = False

        if self.camp.fight.cstat[self.mover].action_points < 1 and self.camp.fight.cstat[self.mover].mp_remaining < self.nav.cheapest_move:
            self.camp.fight.cstat[self.mover].mp_remaining = 0
        elif ev.type == pbge.TIMEREVENT:
            self.render()
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and pbge.my_state.view.mouse_tile in self.nav.cost_to_tile and not pbge.my_state.widget_clicked:
            # Move!
            dest = self.camp.fight.move_model_to(self.mover,self.nav,pbge.my_state.view.mouse_tile)
            self.needs_tile_update = True

    def dispose( self ):
        # Get rid of the widgets and shut down.
        pbge.my_state.widgets.remove(self.my_widget)

    def activate( self ):
        self.my_widget.active = True
        self.needs_tile_update = True

    def deactivate( self ):
        self.my_widget.active = False




