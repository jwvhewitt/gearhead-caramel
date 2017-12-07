import pbge
from gears import info

class TargetingWidget( pbge.widgets.Widget ):
    def __init__( self, camp, attacker, **kwargs ):
        super(TargetingWidget, self).__init__(-383,-5,383,57,anchor=pbge.frects.ANCHOR_UPPERRIGHT,**kwargs)
        self.camp = camp
        self.attacker = attacker

        self.sprite = pbge.image.Image('sys_tacticsinterface_attackwidget.png',383,57)


    def open_dropdown_menu( self ):
        mymenu = pbge.rpgmenu.Menu(-130,32,100,200,anchor=pbge.frects.ANCHOR_UPPERRIGHT)
        return mymenu

    def render( self ):
        if self.active:
            self.sprite.render(self.get_rect(),0)

            for c in self.children:
                c.render()



class TargetingUI( object ):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    def __init__(self, camp, attacker, invo):
        self.camp = camp
        self.attacker = attacker
        self.origin = attacker.pos
        self.targets = list()
        self.invo = invo
        self.area = invo.area
        self.legal_tiles = invo.area.get_targets(camp,attacker.pos)
        self.num_targets = invo.targets

        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png',64,64)

    def render( self ):
        pbge.my_state.view.overlays.clear()
        pbge.my_state.view.overlays[ self.origin ] = (self.cursor_sprite,self.SC_ORIGIN)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            aoe = self.area.get_area( self.camp, self.origin, pbge.my_state.view.mouse_tile )
            for p in aoe:
                pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_AOE)
        if self.targets:
            for t in self.targets:
                aoe = self.area.get_area( self.camp, self.origin, t )
                for p in aoe:
                    pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_AOE)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_CURSOR)
        else:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_VOIDCURSOR)

        pbge.my_state.view()

        mmecha = pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile)
        if mmecha:
            x,y = pygame.mouse.get_pos()
            y -= 64
            info.MechaStatusDisplay((x,y),mmecha[0])

            if hasattr(self.invo.fx,"get_odds"):
                pbge.draw_text(pbge.ANIMFONT, str(int(self.invo.fx.get_odds(self.camp,self.attacker,mmecha[0])*100))+'%', pygame.Rect(x-32,y+2,64,32))

        #if caption:
        #    pygwrap.default_border.render( self.screen, self.SELECT_AREA_CAPTION_ZONE )
        #    pygwrap.draw_text( self.screen, pygwrap.SMALLFONT, caption, self.SELECT_AREA_CAPTION_ZONE )

    def select_area( self ):
        # Start by determining the possible target tiles.
        # Keep processing until a target is selected.
        while len(self.targets) < self.num_targets:
            # Get input and process it.
            gdi = pbge.wait_event()

            if gdi.type == pbge.TIMEREVENT:
                # Set the mouse cursor on the map.
                self.render()
                pygame.display.flip()
            elif gdi.type == pygame.QUIT:
                break
            elif gdi.type == pygame.MOUSEBUTTONUP:
                if gdi.button == 1 and pbge.my_state.view.mouse_tile in self.legal_tiles:
                    self.targets.append( pbge.my_state.view.mouse_tile )
                else:
                    break
        pbge.my_state.view.overlays.clear()
        return self.targets

    def update( self, ev ):
        # We just got an event. Deal with it.
        #if self.needs_tile_update:
        #    self.update_tiles()
        #    self.needs_tile_update = False

        if ev.type == pbge.TIMEREVENT:
            self.render()
            pbge.my_state.do_flip()

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and pbge.my_state.view.mouse_tile in self.legal_tiles:
            self.targets.append( pbge.my_state.view.mouse_tile )
            if len(self.targets) >= self.num_targets:
                pbge.my_state.view.overlays.clear()
                # Launch the effect.

