# The invocation selection and targeting UI.
import pbge
from gears import info
import pygame

# Shelf needs name, desc properties & __str__ method.
# AttackData should be renamed InvoData

class InvoMenuDesc( pbge.frects.Frect ):
    def render_desc( self, menu_item ):
        # Just print this weapon's stats in the provided window.
        myrect = self.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text( pbge.SMALLFONT, menu_item.value.desc, self.get_rect(), justify = -1, color=pbge.WHITE )


class InvocationsWidget(pbge.widgets.Widget):
    # This widget stores the invocation library and allows the player
    # to select which invocation to invoke.
    DESC_CLASS = InvoMenuDesc
    IMAGE_NAME = 'sys_invokerinterface_widget.png'
    def __init__( self, camp, pc, build_library_function, **kwargs ):
        # This widget holds the attack library and determines what invocation
        # from the library is going to be used.
        super(InvocationsWidget, self).__init__(-383,-5,383,57,anchor=pbge.frects.ANCHOR_UPPERRIGHT,**kwargs)
        self.camp = camp
        self.pc = pc
        self.build_library = build_library_function
        self.library = build_library_function()
        self.shelf = None
        self.invo = 0
        # The shelf_offset tells the index of the first invocation in the menu.
        self.shelf_offset = 0

        self.label = pbge.widgets.LabelWidget(12,15,208,21,"",font=pbge.BIGFONT,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT,on_click=self.pop_invo_menu)
        self.children.append(self.label)

        self.buttons = list()
        ddx = 231
        for t in range(4):
            self.buttons.append(pbge.widgets.ButtonWidget(ddx,16,32,32,None,on_click=self.click_button,data=t,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT))
            ddx += 34
        self.children += self.buttons

        self.sprite = pbge.image.Image(self.IMAGE_NAME,383,57)

    def click_button(self,button,ev):
        target_invo = button.data + self.shelf_offset
        if self.shelf and target_invo < len(self.shelf.invo_list) and self.shelf.invo_list[target_invo].can_be_invoked(self.attacker,self.camp.fight):
            self.set_shelf_invo(self.shelf,self.shelf.invo_list[target_invo])

    def pop_invo_menu(self,button,ev):
        mymenu = pbge.rpgmenu.Menu(-380,15,200,180,anchor=pbge.frects.ANCHOR_UPPERRIGHT,font=pbge.BIGFONT)
        mymenu.descobj = self.DESC_CLASS( -160, 15, 140, 180, anchor=pbge.frects.ANCHOR_UPPERRIGHT )
        for shelf in self.library:
            if shelf.has_at_least_one_working_invo(self.pc,self.camp.fight):
                mymenu.add_item(str(shelf),shelf)
        nu_shelf = mymenu.query()
        if nu_shelf in self.library and nu_shelf != self.shelf:
            self.set_shelf_invo( nu_shelf, nu_shelf.get_first_working_invo(self.pc) )

    def select_first_usable_attack(self):
        self.library = self.build_library()
        self.shelf = None
        for shelf in self.library:
            invo = shelf.get_first_working_invo(self.attacker)
            if invo:
                self.set_shelf_invo(shelf,invo)
                break

    def set_shelf_invo( self, nu_shelf, nu_invo ):
        self.shelf = nu_shelf
        invo_n = self.shelf.invo_list.index(nu_invo)
        self.invo = invo_n
        if invo_n > 3:
            self.shelf_offset = n - 3
        else:
            self.shelf_offset = 0
        self.label.text = str(nu_shelf)
        for butt in range(4):
            if butt + self.shelf_offset < len(self.shelf.invo_list):
                b_invo = self.shelf.invo_list[butt + self.shelf_offset]
                self.buttons[butt].sprite = b_invo.data.attack_icon
                if not b_invo.can_be_invoked(self.attacker,self.camp.fight):
                    self.buttons[butt].frame = b_invo.data.disabled_frame
                elif butt + self.shelf_offset == self.invo:
                    self.buttons[butt].frame = b_invo.data.active_frame
                else:
                    self.buttons[butt].frame = b_invo.data.inactive_frame                
                self.buttons[butt].tooltip = b_invo.name
            else:
                self.buttons[butt].sprite = None
                self.buttons[butt].tooltip = None
    def render( self ):
        self.sprite.render(self.get_rect(),0)
    def get_invo(self):
        if self.shelf and self.invo < len(self.shelf.invo_list):
            return self.shelf.invo_list[self.invo]

class InvocationUI( object ):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    SC_TRAILMARKER = 6
    SC_ZEROCURSOR = 7
    LIBRARY_WIDGET = InvocationsWidget
    def __init__(self, camp, pc, build_library_function, invo=None ):
        self.camp = camp
        self.attacker = pc
        self.invo = invo
        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png',64,64)

        self.my_widget = self.LIBRARY_WIDGET(camp,pc,build_library_function)
        pbge.my_state.widgets.append(self.my_widget)
        self.my_widget.active = False

        self.record = False

    def can_move_and_attack( self, target ):
        if self.num_targets == 1:
            self.firing_points = self.invo.area.get_targets(self.camp,target.pos)
            return self.firing_points.intersection(self.nav.cost_to_tile.keys())


    def render( self ):
        pbge.my_state.view.overlays.clear()
        pbge.my_state.view.overlays[ self.attacker.pos ] = (self.cursor_sprite,self.SC_ORIGIN)
        mmecha = pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            aoe = self.invo.area.get_area( self.camp, self.attacker.pos, pbge.my_state.view.mouse_tile )
            for p in aoe:
                pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_AOE)
        if self.targets:
            for t in self.targets:
                aoe = self.invo.area.get_area( self.camp, self.attacker.pos, t )
                for p in aoe:
                    pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_AOE)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_CURSOR)
        elif mmecha and self.can_move_and_attack( mmecha[0] ):
            fp = min(self.firing_points, key=lambda r: self.nav.cost_to_tile.get(r,10000))
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_CURSOR)
            mypath = self.nav.get_path(fp)
            for p in mypath[1:]:
                pbge.my_state.view.overlays[ p ] = (self.cursor_sprite,self.SC_TRAILMARKER)

        else:
            pbge.my_state.view.overlays[ pbge.my_state.view.mouse_tile ] = (self.cursor_sprite,self.SC_VOIDCURSOR)

        pbge.my_state.view()

        # Display info for this tile.
        my_info = self.camp.scene.get_tile_info(pbge.my_state.view.mouse_tile)
        if my_info:
            if mmecha and hasattr(self.invo.fx,"get_odds"):
                odds,modifiers = self.invo.fx.get_odds(self.camp,self.attacker,mmecha[0])
                my_info.info_blocks.append(info.OddsInfoBlock(odds,modifiers))
            my_info.popup()


    def launch( self ):
        pbge.my_state.view.overlays.clear()
        # Launch the effect.
        self.invo.invoke(self.camp, self.attacker, self.targets, pbge.my_state.view.anim_list )
        pbge.my_state.view.handle_anim_sequence(self.record)
        self.camp.fight.cstat[self.attacker].spend_ap(1)
        self.targets = list()
        self.my_widget.update_buttons()
        self.record = False

        # Recalculate the combat info.
        self.activate()


    def update( self, ev, player_turn ):
        # We just got an event. Deal with it.

        if not self.my_widget.library:
            if ev.type == pbge.TIMEREVENT:
                self.render()
                pbge.my_state.do_flip()
            player_turn.switch_movement()
        elif ev.type == pbge.TIMEREVENT:
            self.render()
            pbge.my_state.do_flip()

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not pbge.my_state.widget_clicked:
            if pbge.my_state.view.mouse_tile in self.legal_tiles:
                self.targets.append( pbge.my_state.view.mouse_tile )
            elif self.num_targets == 1 and pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile):
                # Maybe we can move into range? We can determine firing points by
                # checking from the target's position.
                tarp = pbge.my_state.view.mouse_tile
                firing_points = self.invo.area.get_targets(self.camp,pbge.my_state.view.mouse_tile)
                if firing_points.intersection(self.nav.cost_to_tile.keys()):
                    fp = min(firing_points, key=lambda r: self.nav.cost_to_tile.get(r,10000))
                    self.camp.fight.cstat[self.attacker].mp_remaining += self.attacker.get_current_speed()//2
                    self.camp.fight.move_model_to(self.attacker,self.nav,fp)
                    if self.attacker.pos == fp:
                        self.targets.append( tarp )
                    else:
                        self.camp.fight.cstat[self.attacker].spend_ap(1)
                    # Recalculate the combat info.
                    self.activate()

            if len(self.targets) >= self.num_targets and self.invo.can_be_invoked(self.attacker,True):
                self.launch()

        elif ev.type == pygame.KEYDOWN:
            if ev.unicode == u"r":
                #self.camp.save(self.screen)
                self.record = True
                print "Recording"

    def dispose( self ):
        # Get rid of the widgets and shut down.
        pbge.my_state.widgets.remove(self.my_widget)

    def activate( self ):
        self.my_widget.active = True
        self.legal_tiles = self.invo.area.get_targets(self.camp,self.attacker.pos)
        self.nav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene,self.attacker.pos,(self.camp.fight.cstat[self.attacker].action_points-1)*self.attacker.get_current_speed()+self.attacker.get_current_speed()//2+self.camp.fight.cstat[self.attacker].mp_remaining,self.attacker.mmode,self.camp.scene.get_blocked_tiles())

    def deactivate( self ):
        self.my_widget.active = False



