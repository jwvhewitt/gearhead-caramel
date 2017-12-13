
# A Waypoint is a special effect waiting on a tile. It is normally invisible,
# but can affect the terrain of the tile it is placed in. Walking onto the tile
# or bumping it will activate its effect.

import pbge
import ghterrain

class PuzzleMenu( pbge.rpgmenu.Menu ):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75

    def __init__( self, explo, wp ):
        x = explo.screen.get_width() // 2 - self.WIDTH // 2
        y = explo.screen.get_height() // 2 - self.HEIGHT // 2
        super(PuzzleMenu, self).__init__(explo.screen,x,y+self.HEIGHT-self.MENU_HEIGHT,self.WIDTH,self.MENU_HEIGHT,border=None,predraw=self.pre)
        self.full_rect = pygame.Rect( x,y,self.WIDTH,self.HEIGHT )
        self.text_rect = pygame.Rect( x, y, self.WIDTH, self.HEIGHT - self.MENU_HEIGHT - 16 )
        self.explo = explo
        self.desc = wp.desc

    def pre( self, screen ):
        self.explo.view( screen )
        pbge.default_border.render( self.full_rect )
        pbge.draw_text( pbge.SMALLFONT, self.desc, self.text_rect, justify = 0 )


class Waypoint( object ):
    TILE = None
    ATTACH_TO_WALL = False
    name = "Waypoint"
    desc = ""
    desctags = tuple()
    def __init__( self, scene=None, pos=(0,0), plot_locked=False, desc=None, anchor=None ):
        """Place this waypoint in a scene."""
        if scene:
            self.place( scene, pos )
        self.contents = pbge.container.ContainerList(owner=self)
        self.plot_locked = plot_locked
        if desc:
            self.desc = desc
        if anchor:
            self.anchor = anchor

    def place( self, scene, pos=None ):
        if hasattr( self, "container" ) and self.container:
            self.container.remove( self )
        self.scene = scene
        scene.contents.append( self )
        if pos and scene.on_the_map( *pos ):
            self.pos = pos
            if self.TILE:
                if self.TILE.floor:
                    scene._map[pos[0]][pos[1]].floor = self.TILE.floor
                if self.TILE.wall:
                    scene._map[pos[0]][pos[1]].wall = self.TILE.wall
                if self.TILE.decor:
                    scene._map[pos[0]][pos[1]].decor = self.TILE.decor
        else:
            self.pos = (0,0)

    def unlocked_use( self, explo ):
        # Perform this waypoint's special action.
        if self.desc:
            explo.alert( self.desc )

    def bump( self, explo ):
        # If plot_locked, check plots for possible actions.
        # Otherwise, use the normal unlocked_use.
        if self.plot_locked:
            rpm = PuzzleMenu( explo, self )
            explo.expand_puzzle_menu( self, rpm )
            fx = rpm.query()
            if fx:
                fx( explo )
        else:
            self.unlocked_use( explo )


class VendingMachine( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.VendingMachineTerrain )
    desc = "You stand before a vending machine."


