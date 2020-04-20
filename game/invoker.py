# The invocation selection and targeting UI.
import pbge
from gears import info
import pygame
from . import exploration


# Shelf needs name, desc properties & __str__ method.
# AttackData should be renamed InvoData

class InvoMenuDesc(pbge.frects.Frect):
    def __call__(self, menu_item):
        # Just print this weapon's stats in the provided window.
        myrect = self.get_rect()
        pbge.default_border.render(myrect)
        if hasattr(menu_item.value, 'desc'):
            pbge.draw_text(pbge.SMALLFONT, menu_item.value.desc, self.get_rect(), justify=-1, color=pbge.WHITE)
        else:
            pbge.draw_text(pbge.SMALLFONT, '???', self.get_rect(), justify=-1, color=pbge.WHITE)


class InvocationsWidget(pbge.widgets.Widget):
    # This widget stores the invocation library and allows the player
    # to select which invocation to invoke.
    DESC_CLASS = InvoMenuDesc
    IMAGE_NAME = 'sys_invokerinterface_widget.png'
    MENU_POS = (-380, 15, 200, 180)
    DESC_POS = (-160, 15, 140, 180)

    def __init__(self, camp, pc, build_library_function, update_callback, start_source=None, **kwargs):
        # This widget holds the attack library and determines what invocation
        # from the library is going to be used.
        # build_library_function is a function that builds the library. Duh.
        # update_callback is a function that gets called when the invocation
        #   is changed. It passes the new invocation as a parameter.
        super(InvocationsWidget, self).__init__(-383, -5, 383, 57, anchor=pbge.frects.ANCHOR_UPPERRIGHT, **kwargs)
        self.camp = camp
        self.pc = pc
        self.build_library = build_library_function
        self.library = build_library_function()
        self.update_callback = update_callback
        self.shelf = None
        self.invo = 0
        # The shelf_offset tells the index of the first invocation in the menu.
        self.shelf_offset = 0

        self.label = pbge.widgets.LabelWidget(12, 15, 208, 21, "", font=pbge.BIGFONT, parent=self,
                                              anchor=pbge.frects.ANCHOR_UPPERLEFT, on_click=self.pop_invo_menu)
        self.children.append(self.label)

        self.buttons = list()
        ddx = 231
        for t in range(4):
            self.buttons.append(
                pbge.widgets.ButtonWidget(ddx, 16, 32, 32, None, on_click=self.click_button, data=t, parent=self,
                                          anchor=pbge.frects.ANCHOR_UPPERLEFT))
            ddx += 34
        self.children += self.buttons

        self.sprite = pbge.image.Image(self.IMAGE_NAME, 383, 57)
        if start_source:
            self.select_shelf_with_this_source(start_source)
        else:
            self.select_first_usable_invo()

    def _builtin_responder(self, ev):
        # Respond to keyboard and mouse scroll events.
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 4:
                self.prev_shelf()
            elif ev.button == 5:
                self.next_shelf()
            elif ev.button == 3:
                self.pop_invo_menu()
        elif ev.type == pygame.KEYDOWN:
            if ev.key in pbge.my_state.get_keys_for("up"):
                self.prev_shelf()
            elif ev.key in pbge.my_state.get_keys_for("down"):
                self.next_shelf()
            elif ev.key in pbge.my_state.get_keys_for("left"):
                self.prev_invo()
            elif ev.key in pbge.my_state.get_keys_for("right"):
                self.next_invo()

    def prev_invo(self):
        usable_invos = [i for i in self.shelf.invo_list if
                        i.can_be_invoked(self.pc, bool(self.camp.fight)) or i is self.shelf.invo_list[self.invo]]
        if len(usable_invos) > 1:
            new_i = max(self.shelf.invo_list.index(self.shelf.invo_list[self.invo]) - 1, 0)
            self.set_shelf_invo(self.shelf, usable_invos[new_i])

    def next_invo(self):
        usable_invos = [i for i in self.shelf.invo_list if
                        i.can_be_invoked(self.pc, bool(self.camp.fight)) or i is self.shelf.invo_list[self.invo]]
        if len(usable_invos) > 1:
            new_i = min(self.shelf.invo_list.index(self.shelf.invo_list[self.invo]) + 1, len(usable_invos) - 1)
            self.set_shelf_invo(self.shelf, usable_invos[new_i])

    def prev_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc) or s is self.shelf]
        if len(usable_shelves) > 1:
            old_i = usable_shelves.index(self.shelf)
            nu_shelf = usable_shelves[old_i - 1]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def next_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc) or s is self.shelf]
        if len(usable_shelves) > 1:
            new_i = usable_shelves.index(self.shelf) + 1
            if new_i >= len(usable_shelves):
                new_i = 0
            nu_shelf = usable_shelves[new_i]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def click_button(self, button, ev):
        target_invo = button.data + self.shelf_offset
        if self.shelf and target_invo < len(self.shelf.invo_list) and self.shelf.invo_list[target_invo].can_be_invoked(
                self.pc, self.camp.fight):
            self.set_shelf_invo(self.shelf, self.shelf.invo_list[target_invo])

    def pop_invo_menu(self, button=None, ev=None):
        mymenu = pbge.rpgmenu.Menu(*self.MENU_POS, anchor=pbge.frects.ANCHOR_UPPERRIGHT, font=pbge.BIGFONT)
        mymenu.descobj = self.DESC_CLASS(*self.DESC_POS, anchor=pbge.frects.ANCHOR_UPPERRIGHT)
        for shelf in self.library:
            if shelf.has_at_least_one_working_invo(self.pc, self.camp.fight):
                mymenu.add_item(str(shelf), shelf)
        nu_shelf = mymenu.query()
        if nu_shelf in self.library and nu_shelf != self.shelf:
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def maybe_select_shelf_with_this_source(self, this_source):
        if this_source:
            self.library = self.build_library()
            shelf_to_use = None
            for shelf in self.library:
                if this_source is shelf.source:
                    shelf_to_use = shelf
                    break
            if shelf_to_use:
                self.set_shelf_invo(shelf_to_use,
                                    shelf_to_use.get_first_working_invo(self.pc, self.camp.fight) or
                                    shelf_to_use.invo_list[0])
            else:
                self.select_first_usable_invo()

    def select_shelf_with_this_source(self, this_source):
        self.library = self.build_library()
        self.shelf = None
        for shelf in self.library:
            if this_source is shelf.source:
                self.set_shelf_invo(shelf, shelf.get_first_working_invo(self.pc, self.camp.fight) or shelf.invo_list[0])
                break

    def select_first_usable_invo(self):
        self.library = self.build_library()
        self.shelf = None
        for shelf in self.library:
            invo = shelf.get_first_working_invo(self.pc, self.camp.fight)
            if invo:
                self.set_shelf_invo(shelf, invo)
                break

    def set_shelf_invo(self, nu_shelf, nu_invo):
        self.shelf = nu_shelf
        invo_n = self.shelf.invo_list.index(nu_invo)
        self.invo = invo_n
        if invo_n > 3:
            self.shelf_offset = invo_n - 3
        else:
            self.shelf_offset = 0
        self.label.text = str(nu_shelf)
        for butt in range(4):
            if butt + self.shelf_offset < len(self.shelf.invo_list):
                b_invo = self.shelf.invo_list[butt + self.shelf_offset]
                self.buttons[butt].sprite = b_invo.data.attack_icon
                if not b_invo.can_be_invoked(self.pc, self.camp.fight):
                    self.buttons[butt].frame = b_invo.data.disabled_frame
                elif butt + self.shelf_offset == self.invo:
                    self.buttons[butt].frame = b_invo.data.active_frame
                else:
                    self.buttons[butt].frame = b_invo.data.inactive_frame
                self.buttons[butt].tooltip = b_invo.name
            else:
                self.buttons[butt].sprite = None
                self.buttons[butt].tooltip = None
        self.update_callback(self.get_invo())

    def render(self):
        self.sprite.render(self.get_rect(), 0)

    def get_invo(self):
        if self.shelf and self.invo < len(self.shelf.invo_list):
            return self.shelf.invo_list[self.invo]

    def update_buttons(self):
        if not self.shelf.invo_list[self.invo].can_be_invoked(self.pc, True):
            if self.shelf.has_at_least_one_working_invo(self.pc):
                self.set_shelf_invo(self.shelf, self.shelf.get_first_working_invo(self.pc))
            else:
                self.select_first_usable_invo()
        else:
            self.set_shelf_invo(self.shelf, self.shelf.invo_list[self.invo])


class InvocationUI(object):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    SC_TRAILMARKER = 6
    SC_ZEROCURSOR = 7
    LIBRARY_WIDGET = InvocationsWidget

    def __init__(self, camp, pc, build_library_function, source=None):
        self.camp = camp
        self.pc = pc
        # self.change_invo(invo)
        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png', 64, 64)

        self.my_widget = self.LIBRARY_WIDGET(camp, pc, build_library_function, self.change_invo, source)
        self.my_widget.active = False
        pbge.my_state.widgets.append(self.my_widget)
        self.record = False
        self.keep_exploring = True

    def change_invo(self, new_invo):
        self.invo = new_invo
        if new_invo:
            self.legal_tiles = new_invo.area.get_targets(self.camp, self.pc.pos)
            self.num_targets = new_invo.targets
        else:
            self.legal_tiles = set()
            self.num_targets = 0
        self.targets = list()

    def can_move_and_attack(self, target_pos):
        # Return True if model can move and invoke.
        # Record the path in self.mypath.
        if self.num_targets != 1:
            return False
        elif not self.camp.fight:
            self.firing_points = self.invo.area.get_targets(self.camp, target_pos)
            mynav = pbge.scenes.pathfinding.AStarPath(self.camp.scene, self.pc.pos, target_pos, self.pc.mmode)
            if self.firing_points.intersection(list(mynav.cost_to_tile.keys())):
                fp = min(self.firing_points, key=lambda r: mynav.cost_to_tile.get(r, 10000))
                self.mypath = mynav.get_path(fp)
                return True
        else:
            self.firing_points = self.camp.fight.can_move_and_invoke(self.pc, self.nav, self.invo, target_pos)
            if self.firing_points:
                fp = min(self.firing_points, key=lambda r: self.nav.cost_to_tile.get(r, 10000))
                self.mypath = self.nav.get_path(fp)
                return True

    def render(self):
        pbge.my_state.view.overlays.clear()
        pbge.my_state.view.overlays[self.pc.pos] = (self.cursor_sprite, self.SC_ORIGIN)
        mmecha = pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile)
        if self.invo and pbge.my_state.view.mouse_tile in self.legal_tiles:
            aoe = self.invo.area.get_area(self.camp, self.pc.pos, pbge.my_state.view.mouse_tile)
            for p in aoe:
                pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_AOE)
        if self.invo and self.targets:
            for t in self.targets:
                aoe = self.invo.area.get_area(self.camp, self.pc.pos, t)
                for p in aoe:
                    pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_AOE)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            pbge.my_state.view.overlays[pbge.my_state.view.mouse_tile] = (self.cursor_sprite, self.SC_CURSOR)
        elif mmecha and self.can_move_and_attack(mmecha[0].pos):
            pbge.my_state.view.overlays[pbge.my_state.view.mouse_tile] = (self.cursor_sprite, self.SC_CURSOR)
            for p in self.mypath[1:]:
                pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_TRAILMARKER)
        else:
            pbge.my_state.view.overlays[pbge.my_state.view.mouse_tile] = (self.cursor_sprite, self.SC_VOIDCURSOR)

        pbge.my_state.view()

        # Display info for this tile.
        my_info = self.camp.scene.get_tile_info(pbge.my_state.view.mouse_tile)
        if my_info:
            if self.invo and mmecha and hasattr(self.invo.fx, "get_odds"):
                odds, modifiers = self.invo.fx.get_odds(self.camp, self.pc, mmecha[0])
                my_info.info_blocks.append(info.OddsInfoBlock(odds, modifiers))
            my_info.popup()

    def launch(self):
        # This function is for use in combat. The explo_invoke class
        # method will handle invocations outside of combat.
        # Ideally, there should be a way to describe actions that works
        # both inside and outside of combat. I'm gonna think about that.
        if self.camp.fight:
            pbge.my_state.view.overlays.clear()
            # Launch the effect.
            self.invo.invoke(self.camp, self.pc, self.targets, pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence(self.record)
            self.camp.fight.cstat[self.pc].spend_ap(1)
            self.targets = list()
            self.my_widget.update_buttons()
            self.record = False

            # Recalculate the combat info.
            self.activate()
            self.camp.scene.update_party_position(self.camp)

    def update(self, ev, player_turn):
        # We just got an event. Deal with it.

        if player_turn and not self.my_widget.library:
            if ev.type == pbge.TIMEREVENT:
                self.render()
                pbge.my_state.do_flip()
            player_turn.switch_movement()
        elif ev.type == pbge.TIMEREVENT:
            self.render()
            pbge.my_state.do_flip()

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not pbge.my_state.widget_clicked:
            if pbge.my_state.view.mouse_tile in self.legal_tiles:
                self.targets.append(pbge.my_state.view.mouse_tile)
            elif self.can_move_and_attack(pbge.my_state.view.mouse_tile) and pbge.my_state.view.modelmap.get(
                    pbge.my_state.view.mouse_tile):
                if self.camp.fight:
                    # Maybe we can move into range? We can determine firing points by
                    # checking from the target's position.
                    tarp = pbge.my_state.view.mouse_tile
                    firing_points = self.camp.fight.can_move_and_invoke(self.pc, self.nav, self.invo, tarp)
                    if firing_points:
                        self.camp.fight.move_and_invoke(self.pc, self.nav, self.invo, [tarp, ], firing_points,
                                                        self.record)
                        # Recalculate the combat info.
                        self.targets = list()
                        self.my_widget.update_buttons()
                        self.record = False
                        self.activate()
                else:
                    self.targets.append(pbge.my_state.view.mouse_tile)

            if len(self.targets) >= self.num_targets and self.invo.can_be_invoked(self.pc, True):
                self.launch()

        elif ev.type == pygame.KEYDOWN:
            if ev.unicode == "r":
                # self.camp.save(self.screen)
                self.record = True
                print("Recording")
            elif ev.key == pygame.K_ESCAPE:
                self.keep_exploring = False

    def dispose(self):
        # Get rid of the widgets and shut down.
        pbge.my_state.widgets.remove(self.my_widget)

    def activate(self):
        self.my_widget.active = True
        self.legal_tiles = self.invo.area.get_targets(self.camp, self.pc.pos)
        if self.camp.fight:
            self.nav = self.camp.fight.get_action_nav(self.pc)

    def deactivate(self):
        # Used during combat only!
        self.my_widget.active = False

    def get_firing_pos(self):
        if self.targets[0] in self.legal_tiles:
            return self.pc.pos
        else:
            self.firing_points = self.invo.area.get_targets(self.camp, self.targets[0])
            mynav = pbge.scenes.pathfinding.AStarPath(self.camp.scene, self.pc.pos, self.targets[0], self.pc.mmode)
            if self.firing_points.intersection(list(mynav.cost_to_tile.keys())):
                return min(self.firing_points, key=lambda r: mynav.cost_to_tile.get(r, 10000))
            else:
                return self.pc.pos

    @classmethod
    def explo_invoke(cls, explo, pc, build_library_function, source=None):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(explo.camp, pc, build_library_function, source)
        myui.activate()
        while myui.keep_exploring and len(myui.targets) < myui.num_targets:
            gdi = pbge.wait_event()
            myui.update(gdi, None)

        myui.dispose()

        if myui.invo and len(myui.targets) >= myui.num_targets and myui.invo.can_be_invoked(myui.pc, False):
            return exploration.DoInvocation(explo, pc, myui.get_firing_pos(), myui.invo, myui.targets, myui.record)
