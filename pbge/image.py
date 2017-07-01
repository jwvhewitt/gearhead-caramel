# Load one image file, use it for multiple images.

import pygame
import weakref
import util
from . import my_state

# Keep a list of already-loaded images, to save memory when multiple objects
# need to use the same image file.
pre_loaded_images = weakref.WeakValueDictionary()

class Image( object ):
    def __init__(self,fname=None,frame_width=0,frame_height=0,color=None):
        """Load image file, or create blank image, at frame size"""
        if fname:
            if (fname,color) in pre_loaded_images:
                self.bitmap = pre_loaded_images[(fname,color)]
            else:
                self.bitmap = pygame.image.load( util.image_dir( fname ) ).convert()
                self.bitmap.set_colorkey((0,0,255),pygame.RLEACCEL)
                if color:
                    self.recolor(color)
                pre_loaded_images[(fname,color)] = self.bitmap
        else:
            self.bitmap = pygame.Surface( (frame_width , frame_height) )
            self.bitmap.fill((0,0,255))
            self.bitmap.set_colorkey((0,0,255),pygame.RLEACCEL)

        if frame_width == 0:
            frame_width = self.bitmap.get_width()
        if frame_height == 0:
            frame_height = self.bitmap.get_height()

        if frame_width > self.bitmap.get_width():
            frame_width = self.bitmap.get_width()
        self.fname = fname
        self.frame_width = frame_width
        self.frame_height = frame_height

    def render( self , dest = (0,0) , frame=0, dest_surface=None ):
        # Render this Image onto the provided surface.
        # Start by determining the correct sub-area of the image.
        frames_per_row = self.bitmap.get_width() / self.frame_width
        area_x = ( frame % frames_per_row ) * self.frame_width
        area_y = ( frame / frames_per_row ) * self.frame_height
        area = pygame.Rect( area_x , area_y , self.frame_width , self.frame_height )
        dest_surface = dest_surface or my_state.screen
        dest_surface.blit(self.bitmap , dest , area )

    def num_frames( self ):
        frames_per_row = self.bitmap.get_width() / self.frame_width
        frames_per_column = self.bitmap.get_height() / self.frame_height
        return frames_per_row * frames_per_column

    def generate_color( self, color_desc, color_level ):
        # The color_desc is a tuple of six values: r g b at lowest intensity,
        # and r g b at highest intensity.
        dr,dg,db = color_desc
        r = min( ( dr * color_level ) / 200, 255 )
        g = min( ( dg * color_level ) / 200, 255 )
        b = min( ( db * color_level ) / 200, 255 )
        return pygame.Color(r,g,b)

    def recolor( self, color_channels ): 
        # Just gonna brute force this. It could probably be speeded up by using
        # a pixel array, but that would add dependencies. Besides- this should get
        # called just once, when the image is created, so speed isn't that
        # important.
        red_channel,yellow_channel,green_channel,cyan_channel,magenta_channel = color_channels
        for y in range( self.bitmap.get_height() ):
            for x in range( self.bitmap.get_width() ):
                c = self.bitmap.get_at( (x,y) )
                if ( c.r > 0 ) and ( c.g == 0 ) and ( c.b == 0 ):
                    self.bitmap.set_at( (x,y), self.generate_color(red_channel,c.r))
                elif ( c.r > 0 ) and ( c.g == c.r ) and ( c.b == 0 ):
                    self.bitmap.set_at( (x,y), self.generate_color(yellow_channel,c.r))
                elif ( c.r > 0 ) and ( c.g == 0 ) and ( c.b == c.r ):
                    self.bitmap.set_at( (x,y), self.generate_color(magenta_channel,c.r))
                elif ( c.r == 0 ) and ( c.g > 0 ) and ( c.b == 0 ):
                    self.bitmap.set_at( (x,y), self.generate_color(green_channel,c.g))
                elif ( c.r == 0 ) and ( c.g > 0 ) and ( c.b == c.g ):
                    self.bitmap.set_at( (x,y), self.generate_color(cyan_channel,c.g))


    def __reduce__( self ):
        # Rather than trying to save the bitmap image, just save the filename.
        return Image, ( self.fname , self.frame_width , self.frame_height )

    def tile( self , dest , frame = 0, dest_surface=None ):
        dest_surface = dest_surface or my_state.screen
        grid_w = dest.w / self.frame_width + 2
        grid_h = dest.h / self.frame_height + 2
        dest_surface.set_clip( dest )
        my_rect = pygame.Rect(0,0,0,0)

        for x in range(0,grid_w):
            my_rect.x = dest.x + x * self.frame_width
            for y in range(0,grid_h):
                my_rect.y = dest.y + y*self.frame_height
                self.render(my_rect,frame,dest_surface)

        dest_surface.set_clip( None )




