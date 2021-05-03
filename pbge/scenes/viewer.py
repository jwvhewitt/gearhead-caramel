import collections
import weakref
from . import Tile
from .. import my_state,anim_delay,WHITE, wrap_multi_line
from .. import util, image
import pygame
from . import waypoints,terrain
import random

OVERLAY_ITEM = 0
OVERLAY_CURSOR = 1
OVERLAY_ATTACK = 2
OVERLAY_MOVETILE = 3
OVERLAY_AOE = 4
OVERLAY_CURRENTCHARA = 5
OVERLAY_HIDDEN = 6

SCROLL_STEP = 12


class TextTicker( object ):
    def __init__(self):
        self.text_images = list()
        self.counter = 0
        self.height = 20
        self.dy_off = 0

    def add(self, text, dy_off=0):
        pad = (self.counter // my_state.anim_font.get_linesize() - len(self.text_images))
        if pad > 0:
            for t in range(pad):
                self.text_images.append(None)
        newlines = wrap_multi_line(text, my_state.anim_font, 128)
        self.text_images += [ my_state.anim_font.render(l, False, WHITE) for l in newlines]
        self.dy_off = dy_off

    def tick(self, view, x, y):
        self.counter += 1
        x += 32
        y -= self.counter - self.dy_off - 32
        for img in self.text_images[:4]:
            if img:
                mydest = img.get_rect(center=(x,y))
                my_state.screen.blit(img, mydest)
            y += my_state.anim_font.get_linesize()
        if self.counter >= self.height:
            self.counter = self.height - my_state.anim_font.get_linesize()
            self.text_images.pop(0)

    def needs_deletion(self):
        return not self.text_images


class SceneView( object ):
    def __init__(self, scene, postfx=None):
        self.overlays = dict()
        self.anim_list = list()
        self.anims = collections.defaultdict(list)
        self.tickers = collections.defaultdict(TextTicker)

        self.modelmap = collections.defaultdict(list)
        self.uppermap = collections.defaultdict(list)
        self.undermap = collections.defaultdict(list)
        self.waypointmap = collections.defaultdict(list)
        self.fieldmap = dict()
        self.modelsprite = weakref.WeakKeyDictionary()
        self.namedsprite = dict()
        self.darksprite = dict()

        self.randoms = list()
        seed = ord(scene.name[0])
        for t in range(1237):
            #seed = (( seed * 401 ) + 73 ) % 1024
            #self.randoms.append( seed )
            self.randoms.append(random.randint(1,10000))

        self.scene = scene
        self.x_off = 600
        self.y_off = -200
        self.phase = 0

        self.mouse_tile = (-1,-1)

        self.postfx = postfx

        my_state.view = self


    def get_sprite( self, obj ):
        """Return the sprite for the requested object. If no sprite exists, try to load one."""
        spr = self.modelsprite.get( obj )
        if not spr:
            spr = obj.get_sprite()
            self.modelsprite[obj] = spr
        return spr

    def get_named_sprite( self, fname, transparent=False, colors=None ):
        """Return the requested sprite. If no sprite exists, try to load one."""
        spr = self.namedsprite.get( (fname,transparent,colors) )
        if not spr:
            spr = image.Image(fname,self.TILE_WIDTH,self.TILE_WIDTH, color=colors, transparent=transparent)
            self.namedsprite[(fname,transparent,colors)] = spr
        return spr

    def get_terrain_sprite(self,fname,pos,transparent=False, colors=None):
        if self.scene.in_sight:
            if pos in self.scene.in_sight:
                return self.get_named_sprite(fname,transparent=transparent,colors=colors)
            else:
                spr = self.darksprite.get((fname,colors))
                if not spr:
                    spr = self.get_named_sprite(fname, transparent=transparent, colors=colors).copy()
                    spr.bitmap.fill((190, 180, 200), special_flags=pygame.BLEND_MULT)
                    spr.bitmap.set_colorkey((0, 0, 199))
                    self.darksprite[(fname,colors)] = spr
                return spr
        else:
            return self.get_named_sprite(fname, transparent=transparent, colors=colors)

    def get_pseudo_random( self, x, y ):
        #self.seed = ( 73 * x + 101 * y + x * y ) % 1024
        #return self.seed
        return self.randoms[ ( x + y * self.scene.width ) % len(self.randoms) ]

    def calc_floor_score( self, x, y, terr ):
        """Return bitmask of how many floors of type terrain border tile x,y."""
        it = 0
        if ( self.scene.get_floor( x - 1 , y - 1 ) == terr ) or \
          ( self.scene.get_floor( x , y - 1 ) == terr ) or \
          ( self.scene.get_floor( x - 1 , y ) == terr ):
            it += 1
        if ( self.scene.get_floor( x + 1 , y - 1 ) == terr ) or \
          ( self.scene.get_floor( x , y - 1 ) == terr ) or \
          ( self.scene.get_floor( x + 1 , y ) == terr ):
            it += 2
        if ( self.scene.get_floor( x + 1 , y + 1 ) == terr ) or \
          ( self.scene.get_floor( x , y + 1 ) == terr ) or \
          ( self.scene.get_floor( x + 1 , y ) == terr ):
            it += 4
        if ( self.scene.get_floor( x - 1 , y + 1 ) == terr ) or \
          ( self.scene.get_floor( x , y + 1 ) == terr ) or \
          ( self.scene.get_floor( x - 1 , y ) == terr ):
            it += 8
        return it
    def is_same_terrain( self, terr_to_check, terr_prototype ):
        if terr_to_check:
            return issubclass( terr_to_check, terr_prototype )

    def calc_wall_score( self, x, y, terr ):
        """Return bitmask of visible connected walls at x,y."""
        it = 0
        if self.is_same_terrain(self.scene.get_wall( x , y - 1 ),terr) and \
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x - 1 , y )
         and self.scene.tile_blocks_vision( x + 1 , y - 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 2
        if self.is_same_terrain(self.scene.get_wall( x+1 , y ),terr) and \
         not ( self.scene.tile_blocks_vision( x+1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 )
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
            it += 4
        if self.is_same_terrain(self.scene.get_wall( x , y + 1 ),terr) and \
         not ( self.scene.tile_blocks_vision( x-1 , y +1 ) and self.scene.tile_blocks_vision( x - 1 , y )
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 8
        if self.is_same_terrain(self.scene.get_wall( x-1 , y ),terr) and \
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 )
         and self.scene.tile_blocks_vision( x - 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
            it += 1

        return it

    def calc_decor_score( self, x, y, terr ):
        """Return bitmask of how many decors of type terrain border tile x,y."""
        it = 0
        if self.is_same_terrain(self.scene.get_decor( x , y - 1 ),terr) or not self.scene.on_the_map(x, y-1):
            it += 2
        if self.is_same_terrain(self.scene.get_decor( x+1 , y ),terr) or not self.scene.on_the_map(x+1 , y):
            it += 4
        if self.is_same_terrain(self.scene.get_decor( x , y + 1 ),terr) or not self.scene.on_the_map(x, y+1):
            it += 8
        if self.is_same_terrain(self.scene.get_decor( x-1 , y ),terr) or not self.scene.on_the_map(x-1 , y):
            it += 1

        return it

    def is_border_wall( self, x, y ):
        """Return True if this loc is a wall or off the map."""
        return self.scene.get_wall( x , y ) or not self.scene.on_the_map( x,y )

    def calc_border_score( self, x, y ):
        """Return the wall border frame for this tile."""
        it = 0
        if self.is_border_wall( x-1 , y-1 ) and self.is_border_wall( x-1 , y ) and self.is_border_wall( x , y-1 ):
            it += 1
        if self.is_border_wall( x+1 , y-1 ) and self.is_border_wall( x+1 , y ) and self.is_border_wall( x , y-1 ):
            it += 2
        if self.is_border_wall( x+1 , y+1 ) and self.is_border_wall( x+1 , y ) and self.is_border_wall( x , y+1 ):
            it += 4
        if self.is_border_wall( x-1 , y+1 ) and self.is_border_wall( x-1 , y ) and self.is_border_wall( x , y+1 ):
            it += 8
        return it

    def space_to_south( self, x, y ):
        """Return True if no wall in tile to south."""
        return not self.scene.get_wall( x , y + 1 )

    def space_or_door_to_south( self, x, y ):
        """Return True if no wall in tile to south."""
        wall = self.scene.get_wall(x, y+1)
        return not wall or issubclass(wall,terrain.DoorTerrain)

    def space_nearby( self, x, y ):
        """Return True if a tile without a wall is adjacent."""
        found_space = False
        for d in self.scene.DELTA8:
            if not self.scene.get_wall( x + d[0], y + d[1] ):
                found_space = True
                break
        return found_space

    TILE_WIDTH = 64
    # Half tile width and half tile height
    HTW = 32
    HTH = 16

    def relative_x( self, x, y ):
        """Return the relative x position of this tile, ignoring offset."""
        return ( x * self.HTW ) - ( y * self.HTW )

    def relative_y( self, x, y ):
        """Return the relative y position of this tile, ignoring offset."""
        return ( y * self.HTH ) + ( x * self.HTH )

    def screen_coords(self, x, y):
        return (self.relative_x(x - 1, y - 1) + self.x_off, self.relative_y(x - 1, y - 1) + self.y_off)

    def map_x( self, sx, sy ):
        """Return the map x column for the given screen coordinates."""
        return int( float( sx - self.x_off ) / self.HTW + float( sy - self.y_off ) / self.HTH - 1) // 2 - 1

    def fmap_x( self, sx, sy ):
        """Return the map x column for the given screen coordinates."""
        return ( float( sx - self.x_off ) / self.HTW + float( sy - self.y_off ) / self.HTH - 1) / 2 - 1

    def map_y( self, sx, sy ):
        """Return the map y row for the given screen coordinates."""
        return int( float( sy - self.y_off ) / self.HTH - float( sx - self.x_off ) / self.HTW - 1) // 2

    def fmap_y( self, sx, sy ):
        """Return the map y row for the given screen coordinates."""
        return ( float( sy - self.y_off ) / self.HTH - float( sx - self.x_off ) / self.HTW - 1) / 2


    def check_origin( self ):
        """Make sure the offset point is within map boundaries."""
        if -self.x_off < self.relative_x( 0 , self.scene.height-1 ):
            self.x_off = -self.relative_x( 0 , self.scene.height-1 )
        elif -self.x_off > self.relative_x( self.scene.width-1 , 0 ):
            self.x_off = -self.relative_x( self.scene.width-1 , 0 )
        if -self.y_off < self.relative_y( 0 , 0 ):
            self.y_off = -self.relative_y( 0 , 0 )
        elif -self.y_off > self.relative_y( self.scene.width-1 , self.scene.height-1 ):
            self.y_off = -self.relative_y(  self.scene.width-1 , self.scene.height-1  )

    def focus( self, x, y ):
        self.x_off = my_state.screen.get_width()//2 - self.relative_x( x,y )
        self.y_off = my_state.screen.get_height()//2 - self.relative_y( x,y )
        self.check_origin()

    def regenerate_avatars( self, models ):
        """Regenerate the avatars for the listed models."""
        for m in models:
            self.modelsprite[ m ] = m.get_sprite()

    def draw_caption( self, center, txt ):
        myimage = my_state.tiny_font.render( txt, True, (240,240,240) )
        mydest = myimage.get_rect(center=center)
        myfill = pygame.Rect( mydest.x - 2, mydest.y - 1, mydest.width + 4, mydest.height + 2 )
        my_state.screen.fill( (36,37,36), myfill )
        my_state.screen.blit( myimage, mydest )

    def next_tile( self, x0,y0,x, y, line, sx, sy, screen_area ):
        """Locate the next map tile, moving left to right across the screen. """
        keep_going = True
        if (sx + self.TILE_WIDTH) > ( screen_area.x + screen_area.w ):
            if ( sy+self.HTH ) > ( screen_area.y + screen_area.h ):
                keep_going = False
            x = x0 + line // 2
            y = y0 + ( line + 1 ) // 2
            line += 1
        else:
            x += 1
            y -= 1
        return x,y,line,keep_going

    def handle_anim_sequence( self, record_anim=False ):
        # Disable widgets while animation playing.
        push_widget_state = my_state.widgets_active
        my_state.widgets_active = False

        tick = 0
        if record_anim:
            self.anims.clear()
            self()
            my_state.do_flip()
            pygame.image.save( my_state.screen, util.user_dir( "anim_{:0>3}.png".format(tick) ) )
            tick += 1

        while self.anim_list or self.tickers:
            should_delay = False
            self.anims.clear()
            for a in list(self.anim_list):
                if a.needs_deletion:
                    self.anim_list.remove( a )
                    self.anim_list += a.children
                else:
                    should_delay = True
                    a.update(self)
            if should_delay or self.tickers:
                self()
                my_state.do_flip()
            if record_anim:
                pygame.image.save( my_state.screen, util.user_dir( "anim_{:0>3}.png".format(tick) ) )

            anim_delay()
            tick += 1
        self.anims.clear()

        # Restore the widgets.
        my_state.widgets_active = push_widget_state

        # Update any placable things that need updates.
        for thing in self.scene.contents:
            if hasattr(thing,'update_graphics'):
                thing.update_graphics()

    def play_anims(self,*args):
        self.anim_list += args
        self.handle_anim_sequence()

    def PosToKey( self, pos ):
        # Convert the x,y coordinates to a model_map key...
        if pos:
            x,y = pos
            return ( int(round(x)), int(round(y)) )
        else:
            return "IT'S NOT ON THE MAP ALRIGHT?!"

    def model_depth( self, model ):
        return self.relative_y( model.pos[0], model.pos[1] )
    
    def show_model_name(self,model,sx,sy):
        myname = my_state.small_font.render(str(model),True,WHITE)
        namedest = myname.get_rect(midbottom=(sx,sy-60))
        my_state.screen.fill((0,0,0),namedest.inflate(2,2))
        my_state.screen.blit(myname,namedest)

    def __call__( self ):
        """Draws this mapview to the provided screen."""
        screen_area = my_state.screen.get_rect()
        mouse_x,mouse_y = my_state.mouse_pos
        my_state.screen.fill( (0,0,0) )

        # Check for map scrolling, depending on mouse position.
        if mouse_x < 20:
            self.x_off += SCROLL_STEP
            self.check_origin()
        elif mouse_x > ( screen_area.right - 20 ):
            self.x_off -= SCROLL_STEP
            self.check_origin()
        if mouse_y < 20:
            self.y_off += SCROLL_STEP
            self.check_origin()
        elif mouse_y > ( screen_area.bottom - 20 ):
            self.y_off -= SCROLL_STEP
            self.check_origin()

        x,y = self.map_x(0,0)-2, self.map_y(0,0)-1
        x0,y0 = x,y
        keep_going = True
        dest = pygame.Rect( 0, 0, self.TILE_WIDTH, self.TILE_WIDTH )
        line = 1

        # Record all of the scene contents for display when their tile comes up.
        self.modelmap.clear()
        self.uppermap.clear()
        self.undermap.clear()
        self.waypointmap.clear()
        for m in self.scene.contents:
            if hasattr( m , 'render' ) and self.PosToKey(m.pos) in self.scene.in_sight:
                d_pos = self.PosToKey(m.pos)
                if not m.hidden:
                    self.modelmap[d_pos].append(m)
                if self.scene.model_altitude(m,*d_pos) >= 0:
                    self.uppermap[ d_pos ].append( m )
                else:
                    self.undermap[ d_pos ].append( m )
            elif isinstance( m, waypoints.Waypoint ) and m.name:
                # Nameless waypoints are hidden. They probably serve some
                # utility purpose, but the player doesn't have to know they're
                # there.
                self.waypointmap[m.pos].append(m)

        show_names = util.config.getboolean( "GENERAL", "names_above_heads" )

        while keep_going:
            # In order to allow smooth sub-tile movement of stuff, we have
            # to draw everything in a particular order. First, do the predrawing
            # of a tile. Next, draw the models and other stuff in the tile
            # behind this one. When we reach the bottom of the screen, check
            # the next two rows of tiles anyway to finish drawing the models
            # and walls. It's completely nuts! But this is the kind of thing
            # you need to do if you don't have a Z-Buffer. Kinda makes me want
            # to reconsider that resolution to never again use OpenGL.
            sx = self.relative_x( x, y ) + self.x_off
            sy = self.relative_y( x, y ) + self.y_off
            dest.topleft = (sx,sy)

            if self.scene.on_the_map( x , y ) and self.scene._map[x][y].visible:
                self.scene._map[x][y].render_bottom( dest, self, x,y )

                mlist = self.undermap.get( (x,y) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        y_alt = self.scene.model_altitude(m,x,y)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)
                        if show_names:
                            self.show_model_name(m,self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt)

                self.scene._map[x][y].render_biddle( dest, self, x,y )

                if self.scene._map[x][y].floor and self.scene._map[x][y].floor.border:
                    self.scene._map[x][y].floor.border.render( dest, self, x, y )




            # We don't print the model in this tile yet- we print the one in
            # the tile above it.
            if self.scene.on_the_map( x-1, y-1) and self.scene._map[x-1][y-1].visible:
                dest.topleft = (self.relative_x( x-1, y-1 ) + self.x_off,self.relative_y( x-1, y-1 ) + self.y_off)
                self.scene._map[x-1][y-1].render_middle( dest, self, x-1,y-1 )

                if self.overlays.get( (x-1,y-1) , None ):
                    o_dest = dest.copy()
                    if self.scene._map[x-1][y-1].altitude() > 0:
                        o_dest.y -= self.scene._map[x-1][y-1].altitude()
                    o_sprite,o_frame = self.overlays[(x-1,y-1)]
                    o_sprite.render(o_dest,o_frame)

                mlist = self.uppermap.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        y_alt = self.scene.model_altitude(m,x-1,y-1)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)
                        if show_names:
                            self.show_model_name(m,self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt)

                dest.topleft = (self.relative_x( x-1, y-1 ) + self.x_off,self.relative_y( x-1, y-1 ) + self.y_off)
                self.scene._map[x-1][y-1].render_top( dest, self, x-1,y-1 )

                mlist = self.anims.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH), self)


            x,y,line,keep_going = self.next_tile(x0,y0,x,y,line,sx,sy,screen_area )

        the_limit = line + 1
        while line < the_limit:
            sx = self.relative_x( x, y ) + self.x_off
            sy = self.relative_y( x, y ) + self.y_off

            if self.scene.on_the_map( x-1, y-1) and self.scene._map[x-1][y-1].visible:
                dest.topleft = (self.relative_x( x-1, y-1 ) + self.x_off,self.relative_y( x-1, y-1 ) + self.y_off)
                self.scene._map[x-1][y-1].render_middle( dest, self, x-1,y-1 )

                if self.overlays.get( (x-1,y-1) , None ):
                    o_dest = dest.copy()
                    if self.scene._map[x-1][y-1].altitude() > 0:
                        o_dest.y -= self.scene._map[x-1][y-1].altitude()
                    o_sprite,o_frame = self.overlays[(x-1,y-1)]
                    
                    o_sprite.render(o_dest,o_frame)

                mlist = self.uppermap.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        y_alt = self.scene.model_altitude(m,x-1,y-1)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)
                        if show_names:
                            self.show_model_name(m,self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt)

                dest.topleft = (self.relative_x( x-1, y-1 ) + self.x_off,self.relative_y( x-1, y-1 ) + self.y_off)
                self.scene._map[x-1][y-1].render_top( dest, self, x-1,y-1 )

                mlist = self.anims.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH), self)

            x,y,line,keep_going = self.next_tile(x0,y0,x,y,line,sx,sy,screen_area )

        for k,v in list(self.tickers.items()):
            x,y = self.screen_coords(*k)
            if v.needs_deletion():
                del self.tickers[k]
            elif x >= 0 and x <= my_state.screen.get_width() and y >= 0 and y <= my_state.screen.get_height():
                v.tick(self, x, y)
            else:
                del self.tickers[k]

        self.phase = ( self.phase + 1 ) % 600
        self.mouse_tile = (self.map_x(mouse_x,mouse_y),self.map_y(mouse_x,mouse_y))

        if self.postfx:
            self.postfx()

