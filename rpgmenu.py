import pygame
import pygwrap
import glob


MENUFONT = None

INIT_DONE = False

class MenuItem( object ):
    def __init__(self,msg,value,desc=None):
        self.msg = msg
        self.value = value
        self.desc = desc

    def __lt__(self,other):
        """ Comparison of menu items done by msg string """
        return( self.msg < other.msg )

class DescBox( pygame.Rect ):
    # The DescBox inherits from Rect, since that's basically what it is.
    def __init__(self,menu,x,y,w=300,h=100):
        self.menu = menu
        super(DescBox, self).__init__(x,y,w,h)

    def render(self):
        pygwrap.draw_border( self.menu.screen , self )
        if self.menu.items[self.menu.selected_item].desc != None:
            img = pygwrap.render_text( MENUFONT , self.menu.items[self.menu.selected_item].desc , self.w )
            self.menu.screen.blit( img , self )



class Menu( pygame.Rect ):

    def __init__(self,screen,x,y,w=30,h=10,menuitem=(150,145,130),menuselect=(250,250,125)):
        super(Menu, self).__init__(x,y,w,h)
        self.screen = screen
        self.menuitem = menuitem
        self.menuselect = menuselect

        self.items = []
        self.top_item = 0
        self.selected_item = 0
        self.can_cancel = True
        self.descbox = None
        self.quick_keys = {}

        # predraw is a function that will take the screen as a parameter. It
        # redraws/clears the screen before the menu is rendered.
        self.predraw = None

    def add_item(self,msg,value,desc=None):
        item = MenuItem( msg , value , desc )
        self.items.append( item )

    def add_desc(self,x,y,w=30,h=10):
        self.descbox = DescBox( self, x , y , w , h )

    def render(self):
        if self.predraw != None:
            self.predraw( self.screen )

        pygwrap.draw_border( self.screen , self )
        self.screen.set_clip(self)

        item_num = self.top_item
        y = self.top
        while y < self.bottom:
            if item_num < len( self.items ):
                # The color of this item depends on whether or not it's the selected one.
                if item_num == self.selected_item:
                    color = self.menuselect
                else:
                    color = self.menuitem
                img = MENUFONT.render(self.items[item_num].msg, True, color )
                self.screen.blit( img , ( self.left , y ) )
                y += MENUFONT.get_linesize()
            else:
                break
            item_num += 1

        self.screen.set_clip(None)

        if self.descbox != None:
            self.descbox.render()

    def get_mouseover_item( self , pos ):
        # Return the menu item under this mouse position.
        x,y = pos
        if self.collidepoint( pos ):
            the_item = ( y - self.top ) / MENUFONT.get_linesize() + self.top_item
            if the_item > len( self.items ):
                the_item = None
            return the_item
        else:
            return None

    def query(self):
        # A return of False means selection was cancelled. 
        if self.selected_item >= len( self.items ):
            self.selected_item = 0
        no_choice_made = True
        choice = False

        menu_height = self.height / MENUFONT.get_linesize()

        mouse_button_down = False
        first_mouse_selection = None
        first_mouse_y = 0
        current_mouse_selection = None
 
        while no_choice_made:
            pc_input = pygwrap.wait_event()

            if pc_input.type == pygwrap.TIMEREVENT:
                # Redraw the menu on each timer event.
                self.render()
                pygame.display.flip()

                # Also deal with mouse stuff then...
                if mouse_button_down:
                    pos = pygame.mouse.get_pos()
                    dy = pos[1] - first_mouse_y

                    if dy > 10 and self.top_item > 0:
                        self.top_item += -1
                        first_mouse_selection = None
                    elif dy < -10 and self.top_item < len( self.items ) - menu_height:
                        self.top_item += 1
                        first_mouse_selection = None

                    current_mouse_selection = self.get_mouseover_item( pos )
                    if current_mouse_selection != None:
                        self.selected_item = current_mouse_selection

            elif pc_input.type == pygame.KEYDOWN:
                # A key was pressed, oh happy day! See what key it was and act
                # accordingly.
                if pc_input.key == pygame.K_UP:
                    self.selected_item -= 1
                    if self.selected_item < 0:
                        self.selected_item = len( self.items ) - 1
                    if ( self.selected_item < self.top_item ) or ( self.selected_item >= self.top_item + menu_height ):
                        self.top_item = self.selected_item
                elif pc_input.key == pygame.K_DOWN:
                    self.selected_item += 1
                    if self.selected_item >= len( self.items ):
                        self.selected_item = 0
                    if ( self.selected_item < self.top_item ) or ( self.selected_item >= self.top_item + menu_height ):
                        self.top_item = self.selected_item
                elif pc_input.key == pygame.K_SPACE or pc_input.key == pygame.K_RETURN:
                    choice = self.items[ self.selected_item ].value
                    no_choice_made = False
                elif ( pc_input.key == pygame.K_ESCAPE or pc_input.key == pygame.K_BACKSPACE ) and self.can_cancel:
                    no_choice_made = False
                elif pc_input.key >= 0 and pc_input.key < 256 and chr( pc_input.key ) in self.quick_keys:
                    choice = self.quick_keys[ chr(pc_input.key) ]
                    no_choice_made = False
            elif pc_input.type == pygame.MOUSEBUTTONDOWN and not mouse_button_down:
                # Mouse down does nothing but set the first mouse selection, and a
                # counter telling that the button is down.
                first_mouse_selection = self.get_mouseover_item( pc_input.pos )
                first_mouse_y = pc_input.pos[1]
                if first_mouse_selection != None:
                    self.selected_item = first_mouse_selection
                mouse_button_down = True
            elif pc_input.type == pygame.MOUSEBUTTONUP:
                # Mouse button up makes a selection, as long as your finger is still
                # on the first item selected.
                mouse_button_down = False

                current_mouse_selection = self.get_mouseover_item( pc_input.pos )
                if current_mouse_selection == first_mouse_selection and first_mouse_selection != None:
                    self.selected_item = current_mouse_selection
                    choice = self.items[ current_mouse_selection ].value
                    no_choice_made = False

            elif pc_input.type == pygame.QUIT:
                no_choice_made = False


        return( choice )

    def sort(self):
        self.items.sort()

    alpha_key_sequence = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    def add_alpha_keys(self):
        # Adds a quick key for every item currently in the menu.
        key_num = 0
        for item in self.items:
            item.msg = self.alpha_key_sequence[ key_num ] + ') ' + item.msg
            self.quick_keys[ self.alpha_key_sequence[ key_num ] ] = item.value
            key_num += 1
            if key_num >= len( self.alpha_key_sequence ):
                break

    def add_files( self , filepat ):
        file_list = glob.glob( filepat )
        for f in file_list:
            self.add_item( f , f )
        self.sort()

def init():
    # Don't call init until after the display has been set.
    global INIT_DONE
    if not INIT_DONE:
        INIT_DONE = True
        pygwrap.init()
        global MENUFONT
        MENUFONT = pygame.font.Font( "gfx/VeraBd.ttf" , 24 )

if __name__=='__main__':
    pygame.init()

    # Set the screen size.
    screen = pygame.display.set_mode((540, 960))

    init()

    screen.fill((0,0,250))

    mymenu = Menu(screen,50,50,440,320)
    mymenu.add_item( "First Item" , 1 )
    mymenu.add_item( "Second Item" , 2 )
    mymenu.add_item( "Third Item" , 3 )
    mymenu.add_item( "First Item" , 1 )
    mymenu.add_item( "Second Item" , 2 )
    mymenu.add_item( "Third Item" , 3 )
    mymenu.add_item( "First Item" , 1 )
    mymenu.add_item( "Second Item" , 2 )
    mymenu.add_item( "Third Item" , 3 )
    mymenu.add_item( "First Item" , 1 )
    mymenu.add_item( "Second Item" , 2 )
    mymenu.add_item( "Third Item" , 3 )
    mymenu.add_item( "First Item" , 1 )
    mymenu.add_item( "Second Item" , 2 )
    mymenu.add_item( "Third Item" , 3 )

    mymenu.add_alpha_keys()

    n = mymenu.query()

    pygame.quit()

    print n


