import pbge
from gears import info

class MovementUI( object ):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    def __init__(self, camp, mover):
        self.camp = camp
        self.mover = mover
        self.origin = attacker.pos

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
            MechaStatusDisplay((x,y),mmecha[0])

            if hasattr(self.invo.fx,"get_odds"):
                pbge.draw_text(pbge.ANIMFONT, str(int(self.invo.fx.get_odds(self.camp,self.attacker,mmecha[0])*100))+'%', pygame.Rect(x-32,y+2,64,32))


    def update( self, ev ):
        # We just got an event. Deal with it.




