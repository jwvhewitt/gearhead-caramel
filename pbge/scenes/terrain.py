
""" How Terrain Works: Each terraintype is supposed to be a singleton, so
    every reference to a particular terrain type points at the same thing,
    and there will be no problems with serialization. So, to create a new
    terrain type, create a subclass of the closest match and change its
    constants.
"""
import exceptions
from .. import image, Singleton

# Each terrain type can have up to four rendering actions:
# - render_bottom draws a layer beneath all models
# - render_biddle draws a layer above a submerged model, but below a non-submerged one
#   biddle = between bottom and middle
# - render_middle draws a layer beneath a model in the same tile
# - render_top draws a layer on top of a model in the same tile

class FloorBorder( object ):
    def __init__( self, terrain_to_seek, border_image ):
        self.terrain_to_seek = terrain_to_seek
        self.border_image = border_image

    def calc_edges_and_corners( self, view, x, y ):
        """Return the wall border frame for this tile."""
        edges = 0
        check_nw,check_ne,check_sw,check_se=True,True,True,True
        if view.scene.get_floor(x-1,y) is self.terrain_to_seek:
            edges += 1
            check_nw,check_sw=False,False
        if view.scene.get_floor(x,y-1) is self.terrain_to_seek:
            edges += 2
            check_nw,check_ne=False,False
        if view.scene.get_floor(x+1,y) is self.terrain_to_seek:
            edges += 4
            check_ne,check_se=False,False
        if view.scene.get_floor(x,y+1) is self.terrain_to_seek:
            edges += 8
            check_sw,check_se=False,False
        corners = 16
        if check_nw and view.scene.get_floor(x-1,y-1) is self.terrain_to_seek:
            corners += 1
        if check_ne and view.scene.get_floor(x+1,y-1) is self.terrain_to_seek:
            corners += 2
        if check_se and view.scene.get_floor(x+1,y+1) is self.terrain_to_seek:
            corners += 4
        if check_sw and view.scene.get_floor(x-1,y+1) is self.terrain_to_seek:
            corners += 8

        return edges,corners


    def render( self, dest, view, x, y ):
        # Step One: See if there are any of the terrain in question to
        # deal with.
        edges,corners = self.calc_edges_and_corners( view, x, y )
        if edges > 0 or corners > 16:
            spr = view.get_named_sprite( self.border_image )
            if edges > 0:
                spr.render( dest, edges )
            if corners > 16:
                spr.render( dest, corners )



class Terrain( Singleton ):
    name = 'Undefined Terrain'
    image_bottom = ''
    image_biddle = ''
    image_middle = ''
    image_top = ''
    block_vision = False
    block_walk = False
    block_fly = False
    frame = 0
    altitude = 0
    transparent = False
    border = None

    @classmethod
    def render_top( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_top:
            spr = view.get_named_sprite( self.image_top, transparent=self.transparent )
            spr.render( dest, self.frame )
    @classmethod
    def render_biddle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_biddle:
            spr = view.get_named_sprite( self.image_biddle, transparent=self.transparent )
            spr.render( dest, self.frame )
    @classmethod
    def render_middle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_middle:
            spr = view.get_named_sprite( self.image_middle, transparent=self.transparent )
            spr.render( dest, self.frame )
    @classmethod
    def render_bottom( self, dest, view, x, y ):
        """Draw terrain that should appear behind a model in the same tile"""
        if self.image_bottom:
            spr = view.get_named_sprite( self.image_bottom, transparent=self.transparent )
            spr.render( dest, self.frame )
    @classmethod
    def place( self, scene, pos ):
        if scene.on_the_map( *pos ):
            scene.map[pos[0]][pos[1]].decor = self
    @classmethod
    def __str__( self ):
        return self.name
    @classmethod
    def get_sprite( self ):
        """Generate the sprite for this terrain."""
        return image.Image(self.image_top,64,64)

class VariableTerrain( Terrain ):
    frames = (0,1,2,3,4,5,6,7)
    @classmethod
    def render_top( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_top:
            spr = view.get_named_sprite( self.image_top, transparent=self.transparent )
            spr.render( dest, self.frames[view.get_pseudo_random(x,y) % len(self.frames)] )
    @classmethod
    def render_middle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_middle:
            spr = view.get_named_sprite( self.image_middle, transparent=self.transparent )
            spr.render( dest, self.frames[view.get_pseudo_random(x,y) % len(self.frames)] )
    @classmethod
    def render_biddle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_biddle:
            spr = view.get_named_sprite( self.image_biddle, transparent=self.transparent )
            spr.render( dest, self.frames[view.get_pseudo_random(x,y) % len(self.frames)] )
    @classmethod
    def render_bottom( self, dest, view, x, y ):
        """Draw terrain that should appear behind a model in the same tile"""
        if self.image_bottom:
            spr = view.get_named_sprite( self.image_bottom, transparent=self.transparent )
            spr.render( dest, self.frames[view.get_pseudo_random(x,y) % len(self.frames)] )

class AnimTerrain( Terrain ):
    frames = (0,1,2,3,4,5,6,7)
    anim_delay = 4
    @classmethod
    def render_top( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_top:
            spr = view.get_named_sprite( self.image_top, transparent=self.transparent )
            spr.render( dest, self.frames[(view.phase / self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )
    @classmethod
    def render_middle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_middle:
            spr = view.get_named_sprite( self.image_middle, transparent=self.transparent )
            spr.render( dest, self.frames[(view.phase / self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )
    @classmethod
    def render_biddle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model under the same tile"""
        if self.image_biddle:
            spr = view.get_named_sprite( self.image_biddle, transparent=self.transparent )
            spr.render( dest, self.frames[(view.phase / self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )
    @classmethod
    def render_bottom( self, dest, view, x, y ):
        """Draw terrain that should appear behind a model in the same tile"""
        if self.image_bottom:
            spr = view.get_named_sprite( self.image_bottom, transparent=self.transparent )
            spr.render( dest, self.frames[(view.phase / self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )


class WallTerrain( Terrain ):
    block_vision = True
    block_walk = True
    block_fly = True
    bordername = 'terrain_wbor_tall.png'

    @classmethod
    def render_top( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.bordername:
            bor = view.calc_border_score( x, y )
            if bor == 15:
                wal = None
            else:
                wal = view.calc_wall_score( x, y, WallTerrain )
        else:
            bor = -1
            wal = view.calc_wall_score( x, y, WallTerrain )

        if wal:
            spr = view.get_named_sprite( self.image_top, transparent=self.transparent )
            spr.render( dest, wal )
        if bor > 0:
            spr = view.get_named_sprite( self.bordername )
            spr.render( dest, bor )

class HillTerrain( Terrain ):
    block_vision = False
    block_walk = False
    block_fly = False
    bordername = None

    @classmethod
    def render_middle( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.bordername:
            bor = view.calc_border_score( x, y )
            if bor == 15:
                wal = None
            else:
                wal = view.calc_wall_score( x, y, HillTerrain )
        else:
            bor = -1
            wal = view.calc_wall_score( x, y, HillTerrain )

        if wal:
            spr = view.get_named_sprite( self.image_middle, transparent=self.transparent )
            spr.render( dest, wal )
        if bor > 0:
            spr = view.get_named_sprite( self.bordername )
            spr.render( dest, bor )

