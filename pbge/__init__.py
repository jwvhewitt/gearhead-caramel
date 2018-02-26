# Polar Bear Game Engine

# This package contains some low-level graphics stuff needed to
# create an isometric RPG style game in Python. The idea is to
# isolate the graphics handling from the code as much as possible,
# so that if PyGame is replaced the interface shouldn't change
# too much. Also, so that creating a new game should be as simple
# as importing this package.

# Word wrapper taken from the PyGame wiki plus
# the list-printer from Anne Archibald's GearHead Prime demo.

import pygame
from itertools import chain
import util
import glob
import random
import exceptions

# Import the android module. If we can't import it, set it to None - this
# lets us test it, and check to see if we want android-specific behavior.
try:
    import android

except ImportError:
    android = None

class KeyObject( object ):
    """A catcher for multiple inheritence. Subclass this instead of object if
       you're going to use multiple inheritence, so that erroneous keywords
       will get caught and identified."""
    def __init__( self, **keywords ):
        for k,i in keywords.iteritems():
            print "WARNING: KeyObject got parameters {}={}".format(k,i)

class Singleton( object ):
    """For game constants that don't need to be instanced."""
    def __init__( self ):
        raise exceptions.NotImplementedError("Singleton can't be instantiated.")

class Border( object ):
    def __init__( self , border_width=16, tex_width=32, border_name="", tex_name="", padding=16, tl=0, tr=0, bl=0, br=0, t=1, b=1, l=2, r=2, transparent=True ):
        # tl,tr,bl,br are the top left, top right, bottom left, and bottom right frames
        # Bug: The border must be exactly half as wide as the texture.
        self.border_width = border_width
        self.tex_width = tex_width
        self.border_name = border_name
        self.tex_name = tex_name
        self.border = None
        self.tex = None
        self.padding = padding
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br
        self.t = t
        self.b = b
        self.l = l
        self.r = r
        self.transparent = transparent

    def render( self, dest ):
        """Draw this decorative border at dest on screen."""
        # We're gonna draw a decorative border to surround the provided area.
        if self.border == None:
            self.border = image.Image( self.border_name, self.border_width, self.border_width )
        if self.tex == None:
            self.tex = image.Image( self.tex_name, self.tex_width, self.tex_width )
            if self.transparent:
                self.tex.bitmap.set_alpha(224)


        # Draw the backdrop.
        self.tex.tile(dest.inflate(self.padding,self.padding))

        # Expand the dimensions to their complete size.
        # The method inflate_ip doesn't seem to be working... :(
        fdest = dest.inflate(self.padding,self.padding)

        self.border.render( ( fdest.x-self.border_width/2 , fdest.y-self.border_width/2 ) , self.tl )
        self.border.render( ( fdest.x-self.border_width/2 , fdest.y+fdest.height-self.border_width/2 ) , self.bl )
        self.border.render( ( fdest.x+fdest.width-self.border_width/2 , fdest.y-self.border_width/2 ) , self.tr )
        self.border.render( ( fdest.x+fdest.width-self.border_width/2 , fdest.y+fdest.height-self.border_width/2 ) , self.br )

        fdest = dest.inflate(self.padding-self.border_width,self.padding+self.border_width)
        my_state.screen.set_clip(fdest)
        for x in range(0,fdest.w/self.border_width+2):
            self.border.render( ( fdest.x+x*self.border_width , fdest.y ) , self.t )
            self.border.render( ( fdest.x+x*self.border_width , fdest.y+fdest.height-self.border_width ) , self.b )

        fdest = dest.inflate(self.padding+self.border_width,self.padding-self.border_width)
        my_state.screen.set_clip(fdest)
        for y in range(0,fdest.h/self.border_width+2):
            self.border.render( ( fdest.x , fdest.y+y*self.border_width ) , self.l )
            self.border.render( ( fdest.x+fdest.width-self.border_width , fdest.y+y*self.border_width ) , self.r )
        my_state.screen.set_clip(None)


default_border = Border( border_width=8, tex_width=16, border_name="sys_defborder.png", tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2 )
#map_border = Border( border_name="sys_mapborder.png", tex_name="sys_maptexture.png", tl=0, tr=1, bl=2, br=3, t=4, b=6, l=7, r=5 )
#gold_border = Border( border_width=8, tex_width=16, border_name="sys_rixsborder.png", tex_name="sys_rixstexture.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2 )

TEXT_COLOR = (240,240,50)
WHITE = (255,255,255)


class GameState( object ):
    def __init__( self , screen=None ):
        self.screen = screen
        self.view = None
        self.got_quit = False
        self.widgets = list()
        self.widgets_active = True
        self.widget_clicked = False
        self.music = None
        self.music_name = None
        self.music_library = dict()

    def render_widgets( self ):
        for w in self.widgets:
            w.super_render()

    def do_flip( self, show_widgets=True ):
        self.widget_tooltip = None
        if show_widgets:
            self.render_widgets()
        if self.widget_tooltip:
            x,y = pygame.mouse.get_pos()
            if x + 200 > self.screen.get_width():
                x -= 200
            myrect = pygame.rect.Rect(x,y,200,20)
            default_border.render(myrect)
            draw_text(self.small_font,self.widget_tooltip,myrect)
        pygame.display.flip()

    def locate_music( self, mfname ):
        if mfname in self.music_library:
            return self.music_library[mfname]
        else:
            sound = pygame.mixer.Sound(util.music_dir(mfname))
            self.music_library[mfname] = sound
            return sound

    def start_music( self, mfname ):
        if mfname != self.music_name and util.config.getboolean( "DEFAULT", "music_on" ):
            sound = self.locate_music(mfname)
            if self.music:
                self.music.fadeout(2000)
            self.music = sound
            sound.play(loops=-1,fade_ms=2000)
        self.music_name = mfname

    def stop_music( self ):
        if self.music:
            self.music.stop()
    def resume_music( self ):
        if self.music_name:
            mname,self.music_name = self.music_name,None
            self.start_music(mname)





INPUT_CURSOR = None
SMALLFONT = None
TINYFONT = None
ITALICFONT = None
BIGFONT = None
ANIMFONT = None
POSTERS = list()
my_state = GameState()



INIT_DONE = False

# The FPS the game runs at.
FPS = 30

# Use a timer to control FPS.
TIMEREVENT = pygame.USEREVENT

# Remember whether or not this unit has been initialized, since we don't need
# to initialize it more than once.
INIT_DONE = False






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


def render_text(font, text, width, color = TEXT_COLOR, justify = -1, antialias=True ):
    # Return an image with prettyprinted text.
    lines = wrap_multi_line( text , font , width )

    imgs = [ font.render(l, antialias, color ) for l in lines]
    h = sum(i.get_height() for i in imgs)
    s = pygame.surface.Surface((width,h))
    s.fill((0,0,0))
    o = 0
    for i in imgs:
        if justify == 0:
            x = width//2 - i.get_width()//2
        elif justify > 0:
            x = width - i.get_width()
        else:
            x = 0
        s.blit(i,(x,o))
        o += i.get_height()
    s.set_colorkey((0,0,0),pygame.RLEACCEL)
    return s

def draw_text( font , text , rect , color = TEXT_COLOR, justify=-1, antialias=True, dest_surface=None ):
    # Draw some text to the screen with the provided options.
    dest_surface = dest_surface or my_state.screen
    myimage = render_text( font , text , rect.width , color , justify, antialias )
    if justify == 0:
        myrect = myimage.get_rect( midtop = rect.midtop )
    elif justify > 0:
        myrect = myimage.get_rect( topleft = rect.topleft )
    else:
        myrect = rect
    dest_surface.set_clip( rect )
    dest_surface.blit( myimage , myrect )
    dest_surface.set_clip( None )

def wait_event():
    # Wait for input, then return it when it comes.
    ev = pygame.event.wait()

    # Android-specific:
    if android:
        if android.check_pause():
            android.wait_for_resume()

    # Record if a quit event took place
    if ev.type == pygame.QUIT:
        my_state.got_quit = True
    elif ev.type == TIMEREVENT:
        pygame.event.clear( TIMEREVENT )
    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_PRINT:
        pygame.image.save( my_state.screen, util.user_dir( "out.png" ) )
    elif ev.type == pygame.VIDEORESIZE:
        my_state.screen = pygame.display.set_mode( (max(ev.w,800),max(ev.h,600)), pygame.RESIZABLE )

    # Inform any interested widgets of the event.
    my_state.widget_clicked = False
    if my_state.widgets_active:
        for w in my_state.widgets:
            w.respond_event(ev)

    return ev

def anim_delay():
    while wait_event().type != TIMEREVENT:
        pass

def alert(text,font=None):
    if not font:
        font = my_state.medium_font
    #mydest = pygame.Rect( my_state.screen.get_width() // 2 - 200, my_state.screen.get_height()//2 - 100, 400, 200 )
    mytext = render_text( font, text, 400 )
    mydest = mytext.get_rect( center = (my_state.screen.get_width() // 2, my_state.screen.get_height()//2) )

    pygame.event.clear([TIMEREVENT,pygame.KEYDOWN])
    while True:
        ev = pygame.event.wait()
        if ( ev.type == pygame.MOUSEBUTTONUP) or ( ev.type == pygame.QUIT ) or (ev.type == pygame.KEYDOWN):
            break
        elif ev.type == TIMEREVENT:
            if my_state.view:
                my_state.view()
            default_border.render( mydest )
            my_state.screen.blit( mytext, mydest )
            my_state.do_flip()

def alert_display(disp):
    pygame.event.clear([TIMEREVENT,pygame.KEYDOWN])
    while True:
        ev = pygame.event.wait()
        if ( ev.type == pygame.MOUSEBUTTONUP) or ( ev.type == pygame.QUIT ) or (ev.type == pygame.KEYDOWN):
            break
        elif ev.type == TIMEREVENT:
            if my_state.view:
                my_state.view()
            disp.render()
            my_state.do_flip()
    

ALLOWABLE_CHARACTERS = u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890()-=_+,.?"'

def input_string( font = None, redrawer = None, prompt = "Enter text below", prompt_color = (255,255,255), input_color = TEXT_COLOR, border=default_border ):
    # Input a string from the user.
    it = []
    keep_going = True
    cursor_frame = 1

    if not font:
        font = BIGFONT

    myrect = pygame.Rect( my_state.screen.get_width() / 2 - 200 , my_state.screen.get_height() / 2 - 32 , 400 , 64 )
    prompt_image = font.render( prompt, True, prompt_color )

    while keep_going:
        ev = wait_event()

        if ev.type == TIMEREVENT:
            if redrawer != None:
                redrawer()
            border.render( myrect )
            mystring = "".join( it )
            myimage = font.render( mystring, True, input_color )
            my_state.screen.blit( prompt_image , ( my_state.screen.get_width() / 2 - prompt_image.get_width() / 2 , my_state.screen.get_height() / 2 - prompt_image.get_height() - 2 ) )
            my_state.screen.set_clip( myrect )
            my_state.screen.blit( myimage , ( my_state.screen.get_width() / 2 - myimage.get_width() / 2 , my_state.screen.get_height() / 2 ) )
            INPUT_CURSOR.render( ( my_state.screen.get_width() / 2 + myimage.get_width() / 2 + 2 , my_state.screen.get_height() / 2 ) , cursor_frame / 3 )
            my_state.screen.set_clip( None )
            cursor_frame = ( cursor_frame + 1 ) % ( INPUT_CURSOR.num_frames() * 3 )
            pygame.display.flip()


        elif ev.type == pygame.KEYDOWN:
            if ( ev.key == pygame.K_BACKSPACE ) and ( len( it ) > 0 ):
                del it[-1]
            elif ( ev.key == pygame.K_RETURN ) or ( ev.key == pygame.K_ESCAPE ):
                keep_going = False
            elif ( ev.unicode in ALLOWABLE_CHARACTERS ) and ( len( ev.unicode ) > 0 ):
                it.append( ev.unicode )
        elif ev.type == pygame.QUIT:
            keep_going = False
    return "".join( it )


def please_stand_by( caption=None ):
    img = pygame.image.load( random.choice( POSTERS ) ).convert()
    dest = img.get_rect( center=(my_state.screen.get_width()//2,my_state.screen.get_height()//2) )
    my_state.screen.fill( (0,0,0) )
    my_state.screen.blit(img,dest)
    if caption:
        mytext = BIGFONT.render(caption, True, TEXT_COLOR )
        dest2 = mytext.get_rect( topleft = (dest.x+32,dest.y+32) )
        gold_border.render( my_state.screen, dest2 )
        my_state.screen.blit( mytext, dest2 )
    pygame.display.flip()


import frects
import rpgmenu
import container
import namegen
import randmaps
import scenes
import plots
import image
import effects
import campaign
import widgets
import dialogue
import cutscene


def init(winname,appname,gamedir,icon="sys_icon.png",poster_pattern="poster_*.png"):
    global INIT_DONE
    if not INIT_DONE:
        util.init(appname,gamedir)

        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(winname,appname)
        pygame.display.set_icon(pygame.image.load(util.image_dir(icon)))
        # Set the screen size.
        if util.config.getboolean( "DEFAULT", "fullscreen" ):
            my_state.screen = pygame.display.set_mode( (0,0), pygame.FULLSCREEN )
        else:
            my_state.screen = pygame.display.set_mode( (800,600), pygame.RESIZABLE )

        global INPUT_CURSOR
        INPUT_CURSOR = image.Image( "sys_textcursor.png" , 8 , 16 )

        global SMALLFONT
        SMALLFONT = pygame.font.Font( util.image_dir( "DejaVuSansCondensed-Bold.ttf" ) , 12 )
        my_state.small_font = SMALLFONT

        global TINYFONT
        TINYFONT = pygame.font.Font( util.image_dir( "DejaVuSansCondensed-Bold.ttf" ) , 9 )
        my_state.tiny_font = TINYFONT

        global ANIMFONT
        ANIMFONT = pygame.font.Font( util.image_dir( "DejaVuSansCondensed-Bold.ttf" ) , 16 )
        my_state.anim_font = ANIMFONT

        MEDIUMFONT = pygame.font.Font( util.image_dir( "DejaVuSansCondensed-Bold.ttf" ) , 14 )
        my_state.medium_font = MEDIUMFONT


        global ITALICFONT
        ITALICFONT = pygame.font.Font( util.image_dir( "DejaVuSansCondensed-Oblique.ttf" ) , 12 )

        global BIGFONT
        BIGFONT = pygame.font.Font( util.image_dir( "Anita semi square.ttf" ) , 16 )
        my_state.big_font = BIGFONT

        my_state.huge_font = pygame.font.Font( util.image_dir( "Anita semi square.ttf" ) , 24 )

        global POSTERS
        POSTERS += glob.glob( util.image_dir(poster_pattern) )

        global FPS
        FPS = util.config.getint( "DEFAULT", "frames_per_second" )
        pygame.time.set_timer(TIMEREVENT, 1000 / FPS)

        if android:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

        # Set key repeat.
        pygame.key.set_repeat( 200 , 75 )

        INIT_DONE = True


