# Load one image file, use it for multiple images.

import pygame
import weakref
import util

# Keep a list of already-loaded images, to save memory when multiple objects
# need to use the same image file.
pre_loaded_images = weakref.WeakValueDictionary()

class Image( object ):
    def __init__(self,fname=None,frame_width=0,frame_height=0):
        """Load image file, or create blank image, at frame size"""
        if fname:
            if fname in pre_loaded_images:
                self.bitmap = pre_loaded_images[fname]
            else:
                self.bitmap = pygame.image.load( util.image_dir( fname ) ).convert()
                self.bitmap.set_colorkey((0,0,255),pygame.RLEACCEL)
                pre_loaded_images[fname] = self.bitmap
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

    def render( self , screen , dest = (0,0) , frame = 0 ):
        # Render this Image onto the provided surface.
        # Start by determining the correct sub-area of the image.
        frames_per_row = self.bitmap.get_width() / self.frame_width
        area_x = ( frame % frames_per_row ) * self.frame_width
        area_y = ( frame / frames_per_row ) * self.frame_height
        area = pygame.Rect( area_x , area_y , self.frame_width , self.frame_height )
        screen.blit(self.bitmap , dest , area )

    def num_frames( self ):
        frames_per_row = self.bitmap.get_width() / self.frame_width
        frames_per_column = self.bitmap.get_height() / self.frame_height
        return frames_per_row * frames_per_column


    def __reduce__( self ):
        # Rather than trying to save the bitmap image, just save the filename.
        return Image, ( self.fname , self.frame_width , self.frame_height )

    def tile( self , screen , dest , frame = 0 ):
        x0,y0 = dest
        start_x = ( -x0/ 10 ) % self.frame_width - self.frame_width
        start_y = ( -y0/ 10 ) % self.frame_height - self.frame_height

        for x in range( 0 , screen.get_width() / self.frame_width + 2 ):
            for y in range( 0 , screen.get_height() / self.frame_height + 2 ):
                self.render( screen , (x * self.frame_width + start_x , y * self.frame_height + start_y ) , frame )



if __name__ == '__main__':
    pygame.init()

    # Set the screen size.
    screen = pygame.display.set_mode((640, 480))

    myimg = Image( "sys_defborder.png" , 16 , 16 )

    screen.fill((0,0,0))
    myimg.render( screen , ( 10 , 10 ) , 0 )
    myimg.render( screen , ( 26 , 10 ) , 1 )
    myimg.render( screen , ( 10 , 26 ) , 2 )
    myimg.render( screen , ( 42 , 10 ) , 0 )
    myimg.render( screen , ( 42 , 26 ) , 2 )
    myimg.render( screen , ( 10 , 42 ) , 0 )
    myimg.render( screen , ( 26 , 42 ) , 1 )
    myimg.render( screen , ( 42 , 42 ) , 0 )

    myimg2 = Image( frame_width = 32 , frame_height = 32 )
    myimg2.render( screen , ( 100, 100 ) )

    pygame.display.flip()

    while True:
        ev = pygame.event.wait()
        if ( ev.type == pygame.MOUSEBUTTONDOWN ) or ( ev.type == pygame.QUIT ) or (ev.type == pygame.KEYDOWN):
            break



