
from .. import container,image,KeyObject,rpgmenu,frects,draw_text,default_border,my_state,alert
import pygame


class PuzzleMenu( rpgmenu.Menu ):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75

    FULL_RECT = frects.Frect(-175,-125,350,250)
    TEXT_RECT = frects.Frect(-175,-125,350,165)

    def __init__( self, camp, wp ):
        super(PuzzleMenu, self).__init__(-self.WIDTH//2,self.HEIGHT//2-self.MENU_HEIGHT,self.WIDTH,self.MENU_HEIGHT,border=None,predraw=self.pre)
        self.desc = wp.desc
        self.waypoint = wp

    def pre( self ):
        if my_state.view:
            my_state.view()
        default_border.render( self.FULL_RECT.get_rect() )
        draw_text( my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify = 0 )


class Waypoint( object ):
    TILE = None
    ATTACH_TO_WALL = False
    MENU_CLASS = PuzzleMenu # Custom classes should follow the same interface as the PuzzleMenu above
    name = None
    desc = ""
    desctags = tuple()
    def __init__( self, scene=None, pos=(0,0), plot_locked=False, desc=None, anchor=None, name='' ):
        """Place this waypoint in a scene."""
        if scene:
            self.place( scene, pos )
        self.contents = container.ContainerList(owner=self)
        self.plot_locked = plot_locked
        if desc:
            self.desc = desc
        if anchor:
            self.anchor = anchor
        if name != '':
            self.name = name

    def place( self, scene, pos=None ):
        if hasattr( self, "container" ) and self.container:
            self.container.remove( self )
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

    def remove(self, scene):
        if self in scene.contents:
            scene.contents.remove(self)
            if self.TILE:
                if self.TILE.floor:
                    scene._map[self.pos[0]][self.pos[1]].floor = None
                if self.TILE.wall:
                    scene._map[self.pos[0]][self.pos[1]].wall = None
                if self.TILE.decor:
                    scene._map[self.pos[0]][self.pos[1]].decor = None

    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        if self.desc:
            alert( self.desc )

    def bump( self, camp, pc ):
        # Send a BUMP trigger.
        camp.check_trigger("BUMP",self)
        # If plot_locked, check plots for possible actions.
        # Otherwise, use the normal unlocked_use.
        if self.plot_locked:
            rpm = self.MENU_CLASS( camp, self )
            camp.expand_puzzle_menu( self, rpm )
            fx = rpm.query()
            if fx:
                fx( camp )
        else:
            self.unlocked_use( camp )

    def get_scene(self):
        if hasattr( self, "container" ) and self.container and self.container.owner:
            return self.container.owner

    @property
    def scene(self):
        return self.get_scene()

    def __str__(self):
        return str(self.name)

