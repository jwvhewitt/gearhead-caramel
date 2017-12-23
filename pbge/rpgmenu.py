import pygame
import glob
import util
from frects import Frect,ANCHOR_CENTER,ANCHOR_UPPERLEFT

from . import default_border,render_text,wait_event,TIMEREVENT,my_state

class MenuItem( object ):
    def __init__(self,msg,value,desc=None):
        self.msg = msg
        self.value = value
        self.desc = desc

    def __lt__(self,other):
        """ Comparison of menu items done by msg string """
        return( self.msg < other.msg )

# The DescBox is the default MenuDesc. It takes a string stored in the menu
# item and displays it. However, it is not the only menu description possible!
# Any object with a render_desc(menu_item) method will work.
# Also note that the desc associated with each menu item doesn't need to be
# a string- it all depends on the needs of the descobj you're using.

class DescBox( Frect ):
    # The DescBox inherits from Frect, since that's basically what it is.
    def __init__(self,menu,dx,dy,w=300,h=100,anchor=ANCHOR_CENTER,border=default_border,justify=-1,font=None):
        self.menu = menu
        self.border = border
        self.justify = justify
        if not anchor:
            anchor = menu.anchor
        self.font = font or my_state.small_font
        super(DescBox, self).__init__(dx,dy,w,h,anchor)

    def render_desc(self,menu_item):
        mydest = self.get_rect()
        if self.border:
            self.border.render( my_state.screen , mydest )
        if menu_item and menu_item.desc:
            img = render_text( self.font, menu_item.desc, self.w, justify = self.justify )
            my_state.screen.blit( img , mydest )



class Menu( Frect ):

    def __init__(self,dx,dy,w=300,h=100,anchor=ANCHOR_CENTER,menuitem=(150,145,130),menuselect=(128,250,230),border=default_border,predraw=None,font=None):
        super(Menu, self).__init__(dx,dy,w,h,anchor)
        self.menuitem = menuitem
        self.menuselect = menuselect
        self.border = border
        self.font = font or my_state.small_font

        self.items = []
        self.top_item = 0
        self.selected_item = 0
        self.can_cancel = True
        self.descobj = None
        self.quick_keys = {}

        # predraw is a function that
        # redraws/clears the screen before the menu is rendered.
        self.predraw = predraw

    def add_item(self,msg,value,desc=None):
        item = MenuItem( msg , value , desc )
        self.items.append( item )

    def add_descbox(self,x,y,w=30,h=10,justify=-1):
        self.descobj = DescBox( self, x , y , w , h, self.border, justify )

    def render(self,do_extras=True):
        mydest = self.get_rect()
        if do_extras:
            if self.predraw:
                self.predraw()
            else:
                my_state.view()
            my_state.render_widgets()
            if self.border:
                self.border.render( mydest )

        my_state.screen.set_clip(mydest)

        item_num = self.top_item
        y = mydest.top
        while y < mydest.bottom:
            if item_num < len( self.items ):
                # The color of this item depends on whether or not it's the selected one.
                if ( item_num == self.selected_item ) and do_extras:
                    color = self.menuselect
                else:
                    color = self.menuitem
                img = self.font.render(self.items[item_num].msg, True, color )
                my_state.screen.blit( img , ( mydest.left , y ) )
                y += self.font.get_linesize()
            else:
                break
            item_num += 1

        my_state.screen.set_clip(None)

        if self.descobj != None:
            self.descobj.render_desc(self.get_current_item())

    def get_mouseover_item( self , pos ):
        # Return the menu item under this mouse position.
        mydest = self.get_rect()
        x,y = pos
        if mydest.collidepoint( pos ):
            the_item = ( y - mydest.top ) // self.font.get_linesize() + self.top_item
            if the_item >= len( self.items ):
                the_item = None
            return the_item
        else:
            return None

    def query(self):
        # A return of False means selection was cancelled. 
        if not self.items :
            return False
        elif self.selected_item >= len( self.items ):
            self.selected_item = 0
        no_choice_made = True
        choice = False

        # Disable widgets while menuing.
        push_widget_state = my_state.widgets_active
        my_state.widgets_active = False

        menu_height = self.menu_height()

        mouse_button_down = False
        first_mouse_selection = None
        first_mouse_y = 0
        current_mouse_selection = None
 
        while no_choice_made:
            pc_input = wait_event()

            if pc_input.type == TIMEREVENT:
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
                elif pc_input.key > 255 and pc_input.key in self.quick_keys:
                    choice = self.quick_keys[ pc_input.key ]
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

        # Restore the widgets.
        my_state.widgets_active = push_widget_state

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

    def menu_height( self ):
        return self.h // self.font.get_linesize()

    def reposition( self ):
        if self.selected_item < self.top_item:
            self.top_item = self.selected_item
        elif self.selected_item > ( self.top_item + self.menu_height() - 1 ):
            self.top_item = max( self.selected_item - self.menu_height() + 1 , 0 )

    def set_item_by_value( self , v ):
        for n,i in enumerate( self.items ):
            if i.value == v:
                self.selected_item = n
        self.reposition()

    def set_item_by_position( self , n ):
        if n < len( self.items ):
            self.selected_item = n
        self.reposition()

    def get_current_item( self ):
        if self.selected_item < len( self.items ):
            return self.items[self.selected_item]


class PopUpMenu( Menu ):
    """Creates a small menu at the current mouse position."""
    WIDTH = 200
    HEIGHT = 250
    def __init__( self, predraw=None, border=default_border ):
        x,y = pygame.mouse.get_pos()
        x += 8
        y += 8
        sw,sh = my_state.screen.get_size()
        if x + self.WIDTH + 32 > sw:
            x += -self.WIDTH - 32
        if y + self.HEIGHT + 32 > sh:
            y += -self.HEIGHT - 32

        super(PopUpMenu, self).__init__(x,y,self.WIDTH,self.HEIGHT,ANCHOR_UPPERLEFT, border=border, predraw=predraw)



