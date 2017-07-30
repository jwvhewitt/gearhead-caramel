import collections
import weakref
from . import Tile
from .. import my_state,anim_delay
from .. import util, image
import pygame

OVERLAY_ITEM = 0
OVERLAY_CURSOR = 1
OVERLAY_ATTACK = 2
OVERLAY_MOVETILE = 3
OVERLAY_AOE = 4
OVERLAY_CURRENTCHARA = 5
OVERLAY_HIDDEN = 6

SCROLL_STEP = 12

class SceneView( object ):
    def __init__( self, scene ):
        self.overlays = dict()
        self.anim_list = list()
        self.anims = collections.defaultdict(list)

        self.modelmap = collections.defaultdict(list)
        self.undermap = collections.defaultdict(list)
        self.fieldmap = dict()
        self.modelsprite = weakref.WeakKeyDictionary()
        self.namedsprite = dict()

        self.randoms = list()
        seed = ord(scene.name[0])
        for t in range(1237):
            seed = (( seed * 401 ) + 73 ) % 1024
            self.randoms.append( seed )

        self.scene = scene
        self.x_off = 600
        self.y_off = -200
        self.phase = 0

        self.mouse_tile = (-1,-1)


    def get_sprite( self, obj ):
        """Return the sprite for the requested object. If no sprite exists, try to load one."""
        spr = self.modelsprite.get( obj )
        if not spr:
            spr = obj.get_sprite()
            self.modelsprite[obj] = spr
        return spr

    def get_named_sprite( self, fname, transparent=False ):
        """Return the requested sprite. If no sprite exists, try to load one."""
        spr = self.namedsprite.get( fname )
        if not spr:
            spr = image.Image(fname,self.TILE_WIDTH,self.TILE_WIDTH)
            if transparent:
                spr.bitmap.set_alpha(155)
            self.namedsprite[fname] = spr
        return spr

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
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x - 1 , y ) \
         and self.scene.tile_blocks_vision( x + 1 , y - 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 2
        if self.is_same_terrain(self.scene.get_wall( x+1 , y ),terr) and \
         not ( self.scene.tile_blocks_vision( x+1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 ) \
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
            it += 4
        if self.is_same_terrain(self.scene.get_wall( x , y + 1 ),terr) and \
         not ( self.scene.tile_blocks_vision( x-1 , y +1 ) and self.scene.tile_blocks_vision( x - 1 , y ) \
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 8
        if self.is_same_terrain(self.scene.get_wall( x-1 , y ),terr) and \
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 ) \
         and self.scene.tile_blocks_vision( x - 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
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

    def map_x( self, sx, sy ):
        """Return the map x column for the given screen coordinates."""
        return ( ( sx - self.x_off ) / self.HTW + ( sy - self.y_off ) / self.HTH ) // 2

    def map_y( self, sx, sy ):
        """Return the map y row for the given screen coordinates."""
        return ( ( sy - self.y_off ) / self.HTH - ( sx - self.x_off ) / self.HTW ) // 2


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
        myimage = pygwrap.TINYFONT.render( txt, True, (240,240,240) )
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
            x = x0 + line / 2
            y = y0 + ( line + 1 ) / 2
            line += 1
        else:
            x += 1
            y -= 1
        return x,y,line,keep_going

    def handle_anim_sequence( self, record_anim=False ):
        tick = 0
        if record_anim:
            self.anims.clear()
            self()
            pygame.display.flip()
            pygame.image.save( my_state.screen, util.user_dir( "anim_{:0>3}.png".format(tick) ) )
            tick += 1

        while self.anim_list:
            should_delay = False
            self.anims.clear()
            for a in list(self.anim_list):
                if a.needs_deletion:
                    self.anim_list.remove( a )
                    self.anim_list += a.children
                else:
                    should_delay = True
                    a.update(self)
            if should_delay:
                self()
                pygame.display.flip()
            if record_anim:
                pygame.image.save( my_state.screen, util.user_dir( "anim_{:0>3}.png".format(tick) ) )

            anim_delay()
            tick += 1
        self.anims.clear()

    def PosToKey( self, pos ):
        # Convert the x,y coordinates to a model_map key...
        x,y = pos
        return ( int(round(x)), int(round(y)) )

    def model_altitude( self, m,x,y ):
        if m.altitude is None:
            return self.scene._map[x][y].altitude()
        else:
            return m.altitude


    def model_depth( self, model ):
        return self.relative_y( model.pos[0], model.pos[1] )

    def __call__( self ):
        """Draws this mapview to the provided screen."""
        screen_area = my_state.screen.get_rect()
        mouse_x,mouse_y = pygame.mouse.get_pos()
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
        self.undermap.clear()
        for m in self.scene._contents:
            if hasattr( m , 'render' ):
                d_pos = self.PosToKey(m.pos)
                if self.model_altitude(m,*d_pos) >= 0:
                    self.modelmap[ d_pos ].append( m )
                else:
                    self.undermap[ d_pos ].append( m )


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
                        y_alt = self.model_altitude(m,x,y)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)

                self.scene._map[x][y].render_biddle( dest, self, x,y )

                if self.scene._map[x][y].floor and self.scene._map[x][y].floor.border:
                    self.scene._map[x][y].floor.border.render( dest, self, x, y )


            # We don't print the model in this tile yet- we print the one in
            # the tile above it.
            if self.scene.on_the_map( x-1, y-1) and self.scene._map[x-1][y-1].visible:
                dest.topleft = (self.relative_x( x-1, y-1 ) + self.x_off,self.relative_y( x-1, y-1 ) + self.y_off)
                self.scene._map[x-1][y-1].render_middle( dest, self, x-1,y-1 )

                mlist = self.modelmap.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        y_alt = self.model_altitude(m,x-1,y-1)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)


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

                mlist = self.modelmap.get( (x-1,y-1) )
                if mlist:
                    if len( mlist ) > 1:
                        mlist.sort( key = self.model_depth )
                    for m in mlist:
                        mx,my = m.pos
                        y_alt = self.model_altitude(m,x-1,y-1)
                        m.render( (self.relative_x(mx,my)+self.x_off+self.HTW,self.relative_y(mx,my)+self.y_off+self.TILE_WIDTH-self.HTH-y_alt), self)

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


        self.phase = ( self.phase + 1 ) % 600
        self.mouse_tile = (self.map_x(mouse_x,mouse_y),self.map_y(mouse_x,mouse_y))


"""        # Fill the modelmap, fieldmap, and itemmap.
        self.modelmap.clear()
        self.fieldmap.clear()
        itemmap = dict()
        for m in self.scene._contents:
            if isinstance( m , characters.Character ):
                self.modelmap[ tuple( m.pos ) ] = m
            elif isinstance( m , enchantments.Field ):
                self.fieldmap[ tuple( m.pos ) ] = m
            elif isinstance( m, items.Item ):
                itemmap[ tuple( m.pos ) ] = True

        x_min = self.map_x( *screen_area.topleft ) - 1
        x_max = self.map_x( *screen_area.bottomright )
        y_min = self.map_y( *screen_area.topright ) - 1
        y_max = self.map_y( *screen_area.bottomleft )

        tile_x,tile_y = self.mouse_tile

        dest = pygame.Rect( 0, 0, 54, 54 )

        for x in range( x_min, x_max + 1 ):
            for y in range( y_min, y_max + 1 ):
                sx = self.relative_x( x, y ) + self.x_off
                sy = self.relative_y( x, y ) + self.y_off
                dest.topleft = (sx,sy)

                # Check the mouse position.
                if ( mouse_x >= sx ) and ( mouse_x < ( sx + 54 ) ) and ( mouse_y >= ( sy + 41 ) ) and ( mouse_y < ( sy + 54 ) ):
                    # If it's in the lower left triangle, it's one tile south.
                    # If it's in the lower right triangle, it's one tile east.
                    # Otherwise it's right here.
                    if mouse_y > ( sy + 41 + ( mouse_x - sx ) // 2 ):
                        tile_x = x
                        tile_y = y+1
                    elif mouse_y > ( sy + 67 - ( mouse_x - sx ) // 2 ):
                        tile_x = x + 1
                        tile_y = y
                    else:
                        tile_x = x
                        tile_y = y

                if self.scene.on_the_map( x , y ) and self.scene._map[x][y].visible and screen_area.colliderect( dest ):
                    if self.scene._map[x][y].floor:
                        self.scene._map[x][y].floor.render( screen, dest, self, self.map[x][y].floor )

                    if self.scene._map[x][y].wall:
                        self.scene._map[x][y].wall.prerender( screen, dest, self, self.map[x][y].wall )

                    # Print overlay in between the wall border and the wall proper.
                    if self.overlays.get( (x,y) , None ):
                        self.extrasprite.render( screen, dest, self.overlays[(x,y)] )

                    if self.scene._map[x][y].wall:
                        self.scene._map[x][y].wall.render( screen, dest, self, self.map[x][y].wall )

                    if self.scene._map[x][y].decor:
                        self.scene._map[x][y].decor.render( screen, dest, self, self.map[x][y].decor )

                    if itemmap.get( (x,y), False ):
                        self.extrasprite.render( screen, dest, OVERLAY_ITEM )


                    modl = self.modelmap.get( (x,y) , None )
                    if modl:
                        if modl.hidden:
                            # This is easy! All hidden models get the same sprite.
                            self.extrasprite.render( screen, dest, OVERLAY_HIDDEN )
                        else:
                            msprite = self.modelsprite.get( modl , None )
                            if not msprite:
                                msprite = modl.generate_avatar()
                                self.modelsprite[ modl ] = msprite
                            msprite.render( screen, dest, modl.FRAME )

                    fild = self.fieldmap.get( (x,y) , None )
                    if fild:
                        msprite = self.modelsprite.get( fild , None )
                        if not msprite:
                            msprite = fild.generate_avatar()
                            self.modelsprite[ fild ] = msprite
                        msprite.render( screen, dest, fild.frame( self.phase ) )


                    if ( x==tile_x ) and ( y==tile_y) and modl and show_quick_stats and not modl.hidden:
                        if first_pc_pos == (x,y):
                            add_item_note = itemmap.get( (x,y), False )
                        else:
                            add_item_note = False
                        self.quick_model_status( screen, dest, modl, add_item_note )

                    mlist = self.anims.get( (x,y) , None )
                    if mlist:
                        for m in mlist:
                            m.render( self, screen, dest )





        self.phase = ( self.phase + 1 ) % 600
        self.mouse_tile = ( tile_x, tile_y )
"""

