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
        self.sprites = dict()

        self.overlays = dict()
        self.anims = collections.defaultdict(list)

        self.modelmap = dict()
        self.fieldmap = dict()
        self.modelsprite = weakref.WeakKeyDictionary()

        self.scene = scene
        self.seed = 1
        self.x_off = 600
        self.y_off = -200
        self.phase = 0

        self.mouse_tile = (-1,-1)

        self.map = []
        for x in range( scene.width ):
            self.map.append( [] )
            for y in range( scene.height ):
                self.map[x].append( Tile() )

                if scene.map[x][y].floor:
                    self.map[x][y].floor = scene.map[x][y].floor.get_data( self, x, y )
                if scene.map[x][y].wall:
                    self.map[x][y].wall = scene.map[x][y].wall.get_data( self, x, y )
                if scene.map[x][y].decor:
                    self.map[x][y].decor = scene.map[x][y].decor.get_data( self, x, y )


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

    def calc_wall_score( self, x, y ):
        """Return bitmask of visible connected walls at x,y."""
        it = -1
        if isinstance(self.scene.get_wall( x , y - 1 ),WallTerrain) and \
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x - 1 , y ) \
         and self.scene.tile_blocks_vision( x + 1 , y - 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 1
        if isinstance(self.scene.get_wall( x+1 , y ),WallTerrain) and \
         not ( self.scene.tile_blocks_vision( x+1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 ) \
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
            it += 2
        if isinstance(self.scene.get_wall( x , y + 1 ),WallTerrain) and \
         not ( self.scene.tile_blocks_vision( x-1 , y +1 ) and self.scene.tile_blocks_vision( x - 1 , y ) \
         and self.scene.tile_blocks_vision( x + 1 , y + 1 ) and self.scene.tile_blocks_vision( x + 1 , y ) ):
            it += 4
        if isinstance(self.scene.get_wall( x-1 , y ),WallTerrain) and \
         not ( self.scene.tile_blocks_vision( x-1 , y -1 ) and self.scene.tile_blocks_vision( x , y-1 ) \
         and self.scene.tile_blocks_vision( x - 1 , y + 1 ) and self.scene.tile_blocks_vision( x , y+1 ) ):
            it += 8

        if it == -1:
            it = 14
        return it

    def is_border_wall( self, x, y ):
        """Return True if this loc is a wall or off the map."""
        return isinstance(self.scene.get_wall( x , y ),WallTerrain ) or not self.scene.on_the_map( x,y )

    def calc_border_score( self, x, y ):
        """Return the wall border frame for this tile."""
        it = -1
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

    def get_pseudo_random( self ):
        self.seed = ( 73 * self.seed + 101 ) % 1024
        return self.seed

    # Half tile width and half tile height
    HTW = 27
    HTH = 13

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

    def focus( self, screen, x, y ):
        self.x_off = screen.get_width()//2 - self.relative_x( x,y )
        self.y_off = screen.get_height()//2 - self.relative_y( x,y )
        self.check_origin()

    def regenerate_avatars( self, models ):
        """Regenerate the avatars for the listed models."""
        for m in models:
            self.modelsprite[ m ] = m.generate_avatar()

    def draw_caption( self, screen, center, txt ):
        myimage = pygwrap.TINYFONT.render( txt, True, (240,240,240) )
        mydest = myimage.get_rect(center=center)
        myfill = pygame.Rect( mydest.x - 2, mydest.y - 1, mydest.width + 4, mydest.height + 2 )
        screen.fill( (36,37,36), myfill )
        screen.blit( myimage, mydest )

    def quick_model_status( self, screen, dest, model, add_item_note ):
        # Do a quick model status for this model.
        self.draw_caption( screen, (dest.centerx,dest.y-8), str( model ) )

        box = pygame.Rect( dest.x + 7, dest.y , 40, 3 )
        screen.fill( ( 250, 0, 0, 200 ), box )
        hp = model.max_hp()
        hpd = min( model.hp_damage, hp )
        if hp > 0:
            box.x += box.w - ( hpd * box.w ) // hp
            box.w = dest.x + 7 + box.w - box.x
            screen.fill( (120, 0, 0, 100), box )

        box = pygame.Rect( dest.x + 7, dest.y + 4 , 40, 3 )
        screen.fill( ( 0, 150, 250, 200 ), box )
        hp = model.max_mp()
        hpd = min( model.mp_damage, hp )
        if hp > 0:
            box.x += box.w - ( hpd * box.w ) // hp
            box.w = dest.x + 7 + box.w - box.x
            screen.fill( (0, 0, 120, 100), box )

        if add_item_note:
            self.draw_caption( screen, (dest.centerx,dest.y+8), "ITEM" )



    def __call__( self , screen, show_quick_stats=True, first_pc_pos=None ):
        """Draws this mapview to the provided screen."""
        screen_area = screen.get_rect()
        mouse_x,mouse_y = pygame.mouse.get_pos()
        screen.fill( (0,0,0) )

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


        # Fill the modelmap, fieldmap, and itemmap.
        self.modelmap.clear()
        self.fieldmap.clear()
        itemmap = dict()
        for m in self.scene.contents:
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

                if self.scene.on_the_map( x , y ) and self.scene.map[x][y].visible and screen_area.colliderect( dest ):
                    if self.scene.map[x][y].floor:
                        self.scene.map[x][y].floor.render( screen, dest, self, self.map[x][y].floor )

                    if self.scene.map[x][y].wall:
                        self.scene.map[x][y].wall.prerender( screen, dest, self, self.map[x][y].wall )

                    # Print overlay in between the wall border and the wall proper.
                    if self.overlays.get( (x,y) , None ):
                        self.extrasprite.render( screen, dest, self.overlays[(x,y)] )

                    if self.scene.map[x][y].wall:
                        self.scene.map[x][y].wall.render( screen, dest, self, self.map[x][y].wall )

                    if self.scene.map[x][y].decor:
                        self.scene.map[x][y].decor.render( screen, dest, self, self.map[x][y].decor )

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


