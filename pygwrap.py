# Wrapper for pygame which should seamlessly handle the android stuff whether
# this program is run on a phone or not. Started as a wrap border routine,
# added a word wrapping function, then decided to merge in the android wrapper.
# Later on I may expand this unit to make burritos.

# Word wrapper taken from the PyGame wiki plus
# the list-printer from Anne Archibald's GearHead Prime demo.

import pygame
from itertools import chain
import image

# Import the android module. If we can't import it, set it to None - this
# lets us test it, and check to see if we want android-specific behavior.
try:
    import android

except ImportError:
    android = None


WRAP_BACKGROUND = None
WRAP_BORDERS = None

TEX_WIDTH = 16
BORDER_WIDTH = 8

INIT_DONE = False

# The FPS the game runs at.
FPS = 30

# Use a timer to control FPS.
TIMEREVENT = pygame.USEREVENT
pygame.time.set_timer(TIMEREVENT, 1000 / FPS)

# Remember whether or not this unit has been initialized, since we don't need
# to initialize it more than once.
INIT_DONE = False


def wait_event():
    # Wait for input, then return it when it comes.
    ev = pygame.event.wait()

    # Android-specific:
    if android:
        if android.check_pause():
            android.wait_for_resume()

    return ev



def draw_border( screen,dest ):
    # We're gonna draw a decorative border to surround the provided area.
    # Step one: Determine the size of our box. Both dimensions should be 
    # a multiple of TEX_WIDTH. 
    # W32 and H32 will store the number of columns/rows. 
    W32 = ( dest.width + BORDER_WIDTH ) / TEX_WIDTH + 1
    H32 = ( dest.height + BORDER_WIDTH ) / TEX_WIDTH + 1

    # X0 and Y0 will store the upper left corner of the box.
    X0 = dest.left - ( ( ( W32 * TEX_WIDTH ) - dest.width ) / 2 )
    Y0 = dest.top - ( ( ( H32 * TEX_WIDTH ) - dest.height ) / 2 )

    # Draw the backdrop.
    for X in range( W32 ):
        Dest_X = X0 + X * TEX_WIDTH
        for Y in range( H32 ):
            Dest_Y = Y0 + Y * TEX_WIDTH
            WRAP_BACKGROUND.render( screen , ( Dest_X , Dest_Y ) )

    WRAP_BORDERS.render( screen , ( X0 - BORDER_WIDTH / 2 , Y0 - BORDER_WIDTH / 2 ) , 0 )
    WRAP_BORDERS.render( screen , ( X0 - BORDER_WIDTH / 2 , Y0 - BORDER_WIDTH / 2 + H32 * TEX_WIDTH ) , 4 )
    WRAP_BORDERS.render( screen , ( X0 - BORDER_WIDTH / 2 + W32 * TEX_WIDTH , Y0 - BORDER_WIDTH / 2 ) , 3 )
    WRAP_BORDERS.render( screen , ( X0 - BORDER_WIDTH / 2 + W32 * TEX_WIDTH , Y0 - BORDER_WIDTH / 2 + H32 * TEX_WIDTH ) , 5 )

    for X in range( 1 , W32 * 2 ):
        Dest_X = X0 + X * BORDER_WIDTH - BORDER_WIDTH / 2
        Dest_Y = Y0 - BORDER_WIDTH / 2
        WRAP_BORDERS.render( screen , ( Dest_X , Dest_Y ) , 1 )
        Dest_Y = Y0 + H32 * TEX_WIDTH - BORDER_WIDTH / 2
        WRAP_BORDERS.render( screen , ( Dest_X , Dest_Y ) , 1 )
    for Y in range( 1 ,H32 * 2 ):
        Dest_Y = Y0 + Y * BORDER_WIDTH - BORDER_WIDTH / 2
        Dest_X = X0 - BORDER_WIDTH / 2
        WRAP_BORDERS.render( screen , ( Dest_X , Dest_Y ) , 2 )
        Dest_X = X0 + W32 * TEX_WIDTH - BORDER_WIDTH / 2
        WRAP_BORDERS.render( screen , ( Dest_X , Dest_Y ) , 2 )

def truncline(text, font, maxwidth):
        real=len(text)       
        stext=text           
        l=font.size(text)[0]
        cut=0
        a=0                  
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n: 
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)               
            done=0                        
        return real, done, stext             
        
def wrapline(text, font, maxwidth): 
    done=0                      
    wrapped=[]                  
                               
    while not done:             
        nl, done, stext=truncline(text, font, maxwidth) 
        wrapped.append(stext.strip())                  
        text=text[nl:]                                 
    return wrapped
 
 
def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)


def render_text(font, text, width, color = (255,255,255) ):
    lines = wrap_multi_line( text , font , width )

    imgs = [ font.render(l, True, color ) for l in lines]
    h = sum(i.get_height() for i in imgs)
    s = pygame.surface.Surface((width,h))
    s.fill((0,0,0))
    o = 0
    for i in imgs:
        s.blit(i,(0,o))
        o += i.get_height()
    s.set_colorkey((0,0,0),pygame.RLEACCEL)
    return s


def init():
    global INIT_DONE
    if not INIT_DONE:
        global WRAP_BACKGROUND, WRAP_BORDERS
        WRAP_BACKGROUND = image.Image( "sys_defbackground.png" , TEX_WIDTH , TEX_WIDTH )
        WRAP_BORDERS = image.Image( "sys_defborder.png" , BORDER_WIDTH , BORDER_WIDTH )

        if android:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

        # Set key repeat.
        pygame.key.set_repeat( 200 , 75 )

        INIT_DONE = True

if __name__ == "__main__":
    pygame.init()

    myfont = pygame.font.Font( "VeraBd.ttf" , 24 )

    # Set the screen size.
    screen = pygame.display.set_mode((540, 960))
    text = render_text( myfont , "This is an example of an overly long line that will probably need to be split into multiple lines. I used to use song lyrics for this, but have decided against it as I didn't think of it at the time." , 500 , color = (125,250,180) )

    init()

    init()

    init()

    screen.fill((0,0,0))
    draw_border( screen , pygame.rect.Rect(20,10,500,500) )
    screen.blit( text , (20,10) )
    pygame.display.flip()

    while True:
        ev = pygame.event.wait()
        if ( ev.type == pygame.MOUSEBUTTONDOWN ) or ( ev.type == pygame.QUIT ) or (ev.type == pygame.KEYDOWN):
            break



