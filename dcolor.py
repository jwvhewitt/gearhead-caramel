import pbge
import os
from pbge import my_state
import pygame
import hotshot, hotshot.stats

gamedir = os.path.dirname(__file__)
pbge.init('GearHead Caramel','ghcaramel',gamedir)


class DynaColor( object ):
    def __init__( self, midtone ):
        self.mr,self.mg,self.mb = midtone
        self.hr = ( self.mr * 5 ) / 4
        self.hg = ( self.mg * 5 ) / 4
        self.hb = ( self.mb * 5 ) / 4
        self.lr = self.calc_low_color( self.mr, self.hr )
        self.lg = self.calc_low_color( self.mg, self.hg )
        self.lb = self.calc_low_color( self.mb, self.hb )

        self.base_image = pbge.image.Image('aaGradientTest.png',256,256)
        self.color_image = pbge.image.Image(None,256,256)
        self.recolor()

    def calc_low_color( self, midpoint, hipoint ):
        return ( 51 * midpoint - 40 * hipoint ) / 11

    def generate_color( self, color_level ):
        # The color_desc is a tuple of six values: r g b at lowest intensity,
        # and r g b at highest intensity.
        r = max(min((( self.hr - self.lr ) * color_level ) / 255 + self.lr, 255 ),0)
        g = max(min((( self.hg - self.lg ) * color_level ) / 255 + self.lg, 255 ),0)
        b = max(min((( self.hb - self.lb ) * color_level ) / 255 + self.lb, 255 ),0)
        return pygame.Color(r,g,b)

    def recolor( self ):
        for y in range( 256 ):
            for x in range( 256 ):
                c = self.base_image.bitmap.get_at( (x,y) )
                self.color_image.bitmap.set_at( (x,y), self.generate_color(c.r))

    def myview(self):
        screen_area = my_state.screen.get_rect()
        my_state.screen.fill( (0,0,0) )
        self.color_image.render()

        pbge.draw_text(pbge.SMALLFONT,'{} {} {}'.format(self.hr,self.hg,self.hb),pygame.Rect(300,10,300,30))

    def use( self ):
        keep_going = True
        while keep_going:
            # Get input and process it.
            gdi = pbge.wait_event()
            if gdi.type == pbge.TIMEREVENT:
                self.myview()
                pygame.display.flip()

            elif gdi.type == pygame.KEYDOWN:
                if gdi.unicode == u"Q":
                    keep_going = False
                elif gdi.unicode == u"y":
                    self.hr -= 10
                    self.lr = self.calc_low_color( self.mr, self.hr )
                    self.recolor()
                elif gdi.unicode == u"u":
                    self.hr += 10
                    self.lr = self.calc_low_color( self.mr, self.hr )
                    print self.hr, self.lr
                    self.recolor()
                elif gdi.unicode == u"h":
                    self.hg -= 10
                    self.lg = self.calc_low_color( self.mg, self.hg )
                    self.recolor()
                elif gdi.unicode == u"j":
                    self.hg += 10
                    self.lg = self.calc_low_color( self.mg, self.hg )
                    self.recolor()

            elif gdi.type == pygame.QUIT:
                keep_going = False

#mycolor = DynaColor((77,156,131))

#mycolor.use()

class ColorTest( object ):
    def __init__( self, fname='por_f_ladi_vikki(JAY).png' ):
        self.base_image = pbge.image.Image(fname,100,150,((17,78,200),(172,114,89),(175,26,10),(0,0,0),(0,0,0))) # Freedom Blue, Medium Skin, Pirate Sunrise
        self.color_image = pbge.image.Image(fname,100,150)
        self.bitmap = self.color_image.bitmap
        self.colors = ((21,177,255,3,7,36),(236,181,147,30,20,16),(235,57,13,31,1,6),(0,0,0,0,0,0),(0,0,0,0,0,0))

        self.recolor()

    def calc_low_color( self, midpoint, hipoint ):
        return ( 51 * midpoint - 40 * hipoint ) / 11

    def generate_color( self, color_range, color_level ):
        # The color_desc is a tuple of six values: r g b at lowest intensity,
        # and r g b at highest intensity.
        r = max(min((( color_range[0] - color_range[3] ) * color_level ) / 255 + color_range[3], 255 ),0)
        g = max(min((( color_range[1] - color_range[4] ) * color_level ) / 255 + color_range[4], 255 ),0)
        b = max(min((( color_range[2] - color_range[5] ) * color_level ) / 255 + color_range[5], 255 ),0)
        return pygame.Color(r,g,b)

    def recolor( self ):
        red_channel,yellow_channel,green_channel,cyan_channel,magenta_channel = self.colors
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


    def myview(self):
        screen_area = my_state.screen.get_rect()
        my_state.screen.fill( (0,0,0) )
        self.base_image.render(pygame.Rect(50, 50, 100, 150))
        self.color_image.render(pygame.Rect(200, 50, 100, 150))

    def use( self ):
        keep_going = True
        while keep_going:
            # Get input and process it.
            gdi = pbge.wait_event()
            if gdi.type == pbge.TIMEREVENT:
                self.myview()
                pygame.display.flip()

            elif gdi.type == pygame.KEYDOWN:
                if gdi.unicode == u"Q":
                    keep_going = False

            elif gdi.type == pygame.QUIT:
                keep_going = False

ColorTest('por_m_phil_wrongness(A-Y).png').use()

