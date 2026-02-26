# The invocation selection and targeting UI.
import gears
import pbge
from game import traildrawer
from gears import info
import pygame
from collections.abc import Callable


# Shelf needs name, desc properties & __str__ method.
# AttackData should be renamed InvoData

# Data Gatherers are explicitly left undefined in the pbge Invocation specs. In GearHead Caramel, a data gatherer
# should be a callable that takes the invocation's data dict as a parameter and returns True if data was successfully
# gathered or False if it was not.

class DataGatherer:
    def gather(self, _data: dict):
        raise(NotImplementedError("This data gatherer does nothing!"))

    def confirm(self, _data: dict):
        raise(NotImplementedError("This data gatherer cannot confirm the data it did not collect."))


# The On_Invoke callable accepts the invocation being invoked, the "firing position",
# the list of target points, and the invocation data.
type On_Invoke = Callable[[pbge.effects.Invocation, tuple[int, int], list, dict], None]


class InvoMenuDesc(pbge.widgetmenu.DescBoxWidget):
    def _desc_text_fun(self, _widg):
        my_invo = self.menu.current_data
        if my_invo and hasattr(my_invo, 'desc'):
            return my_invo.desc
        else:
            return "???"


class InvocationLibraryWidget(pbge.widgets.Widget):
    # This widget stores the invocation library and allows the player
    # to select which invocation to invoke.
    DESC_CLASS = InvoMenuDesc
    IMAGE_NAME = 'sys_invokerinterface_widget.png'
    MENU_POS = (-380, 15, 200, 180)
    DESC_POS = (-160, 15, 140, 180)
    HELP_FRECT = pbge.frects.Frect(-316, 65, 300, 120, anchor=pbge.frects.ANCHOR_UPPERRIGHT)

    def __init__(
            self, camp, pc, build_library_function, update_callback, start_source=None,
            top_shelf_fun=None, bottom_shelf_fun=None, auto_launch_fun=None, **kwargs
    ):
        # This widget holds the attack library and determines what invocation
        # from the library is going to be used.
        # build_library_function is a function that builds the library. Duh.
        # update_callback is a function that gets called when the invocation
        #   is changed. It passes the new invocation as a parameter.
        # top_shelf_fun and bottom_shelf_fun are functions called when the user
        #   tries to scroll above the top item or below the bottom item. If None,
        #   this widget will just loop around to the other end of the list.
        super(InvocationLibraryWidget, self).__init__(-383, -5, 383, 65, anchor=pbge.frects.ANCHOR_UPPERRIGHT, **kwargs)
        self.camp = camp
        self.pc = pc
        self.build_library = build_library_function
        self.library = build_library_function()
        self.update_callback = update_callback
        self.top_shelf_fun = top_shelf_fun
        self.bottom_shelf_fun = bottom_shelf_fun
        self.auto_launch_fun = auto_launch_fun
        self.shelf = None
        self.invo = 0
        # The shelf_offset tells the index of the first invocation in the menu.
        self.shelf_offset = 0

        self.label = pbge.widgets.LabelWidget(12, 15, 198, 30, "", font=pbge.BIGFONT, parent=self,
                                              anchor=pbge.frects.ANCHOR_UPPERLEFT, on_click=self.pop_invo_menu,
                                              alt_smaller_fonts=(pbge.MEDIUM_DISPLAY_FONT, pbge.MEDIUMFONT, pbge.SMALLFONT, pbge.TINYFONT,))
        self.children.append(self.label)

        self.buttons = list()
        ddx = 231
        for t in range(4):
            self.buttons.append(
                pbge.widgets.ButtonWidget(ddx, 16, 32, 32, None, on_click=self.click_button, data=t, parent=self,
                                          anchor=pbge.frects.ANCHOR_UPPERLEFT))
            ddx += 34
        self.children += self.buttons

        self.sprite = pbge.image.Image(self.IMAGE_NAME, 383, 65)
        if start_source:
            self.select_shelf_with_this_source(start_source)
        else:
            self.select_first_usable_invo()

        self.help_on = False

    def _builtin_responder(self, ev):
        # Respond to keyboard and mouse scroll events.
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 4:
                self.prev_shelf()
                self.register_response()
            elif ev.button == 5:
                self.next_shelf()
                self.register_response()
            elif ev.button == 2:
                self.pop_invo_menu()
        elif ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "up"):
                self.prev_shelf()
                self.register_response()
            elif pbge.my_state.is_key_for_action(ev, "down"):
                self.next_shelf()
                self.register_response()
            elif pbge.my_state.is_key_for_action(ev, "left"):
                self.prev_invo()
                self.register_response()
            elif pbge.my_state.is_key_for_action(ev, "right"):
                self.next_invo()
                self.register_response()
            elif pbge.my_state.is_key_for_action(ev, "help"):
                self.help_on = not self.help_on
            elif pbge.my_state.is_key_for_action(ev, "exit"):
                self.help_on = False

    def prev_invo(self):
        usable_invos = [i for i in self.shelf.invo_list if
                        i.can_be_invoked(self.pc, bool(self.camp.fight)) or i is self.shelf.invo_list[self.invo]]
        current_invo_uix = usable_invos.index(self.shelf.invo_list[self.invo])
        if len(usable_invos) > 1 and current_invo_uix > 0:
            new_i = current_invo_uix - 1
            self.set_shelf_invo(self.shelf, usable_invos[new_i])

    def next_invo(self):
        usable_invos = [i for i in self.shelf.invo_list if
                        i.can_be_invoked(self.pc, bool(self.camp.fight)) or i is self.shelf.invo_list[self.invo]]
        current_invo_uix = usable_invos.index(self.shelf.invo_list[self.invo])
        if len(usable_invos) > 1 and current_invo_uix < (len(usable_invos) - 1):
            new_i = current_invo_uix + 1
            self.set_shelf_invo(self.shelf, usable_invos[new_i])

    def prev_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc) or s is self.shelf]
        old_i = usable_shelves.index(self.shelf)
        if old_i == 0 and self.top_shelf_fun:
            self.top_shelf_fun()
        elif len(usable_shelves) > 1:
            nu_shelf = usable_shelves[old_i - 1]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def next_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc) or s is self.shelf]
        old_i = usable_shelves.index(self.shelf)
        if old_i == len(usable_shelves)-1 and self.bottom_shelf_fun:
            self.bottom_shelf_fun()
        elif len(usable_shelves) > 1:
            new_i = old_i + 1
            if new_i >= len(usable_shelves):
                new_i = 0
            nu_shelf = usable_shelves[new_i]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def set_top_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc)]
        if usable_shelves:
            nu_shelf = usable_shelves[0]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def set_bottom_shelf(self):
        usable_shelves = [s for s in self.library if s.has_at_least_one_working_invo(self.pc)]
        if usable_shelves:
            nu_shelf = usable_shelves[-1]
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def click_button(self, button, _ev):
        target_invo = button.data + self.shelf_offset
        if self.shelf and target_invo < len(self.shelf.invo_list) and self.shelf.invo_list[target_invo].can_be_invoked(
                self.pc, self.camp.fight):
            if target_invo == self.invo and self.auto_launch_fun:
                self.auto_launch_fun()
                # print("Selecting again")
            else:
                self.set_shelf_invo(self.shelf, self.shelf.invo_list[target_invo])

    def pop_invo_menu(self, _button=None, _ev=None):
        mymenu = pbge.widgetmenu.MenuWidget(
            *self.MENU_POS, anchor=pbge.frects.ANCHOR_UPPERRIGHT, font=pbge.BIGFONT,
            pop_when_clicked=True, auto_escape=True
        )
        mymenu.children.append(self.DESC_CLASS(*self.DESC_POS, anchor=pbge.frects.ANCHOR_UPPERRIGHT, menu=mymenu))
        for shelf in self.library:
            if shelf.has_at_least_one_working_invo(self.pc, self.camp.fight):
                _=mymenu.add_item(str(shelf), self._click_invo_menu, data=shelf)

    def _click_invo_menu(self, wid, _ev):
        nu_shelf = wid.data
        if nu_shelf in self.library and nu_shelf != self.shelf:
            self.set_shelf_invo(nu_shelf, nu_shelf.get_first_working_invo(self.pc))

    def maybe_select_shelf_with_this_source(self, this_source):
        if this_source:
            self.library = self.build_library()
            shelf_to_use = None
            for shelf in self.library:
                if this_source is shelf.source:
                    if shelf.has_at_least_one_working_invo(self.pc):
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
                if shelf.has_at_least_one_working_invo(self.pc):
                    self.set_shelf_invo(shelf, shelf.get_first_working_invo(self.pc, self.camp.fight) or shelf.invo_list[0])
                    break
                else:
                    self.select_first_usable_invo()
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
                self.buttons[butt].tooltip = self._generate_tooltip(b_invo)
            else:
                self.buttons[butt].sprite = None
                self.buttons[butt].tooltip = None
        self.update_callback(self.get_invo())

    def _generate_tooltip(self, invo: pbge.effects.Invocation):
        done_classes = set()
        descs = list()
        # Merge descriptions according to class.
        # Otherwise, Linked Fire will have a long list of prices,
        # one for each linked weapon.
        for p in invo.price:
            cls = p.__class__
            if cls in done_classes:
                continue
            done_classes.add(cls)
            if not hasattr(cls, 'describe'):
                continue

            prices = [price for price in invo.price if price.__class__ is cls]
            desc = cls.describe(prices)
            if not desc:
                continue

            descs.append(desc)

        invo_header = invo.name
        if invo.help_text:
            invo_header = "{}: {}".format(invo.name, invo.help_text)

        if not descs:
            return invo_header

        return '{} ({})'.format(invo_header, ', '.join(descs))

    def _render(self, delta):
        self.sprite.render(self.get_rect(), 0)
        if self.help_on:
            myrect = self.HELP_FRECT.get_rect()
            pbge.default_border.render(myrect)
            pbge.draw_text(pbge.MEDIUMFONT, self._generate_tooltip(self.shelf.invo_list[self.invo]), myrect)

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

    def on_activate(self):
        self.update_buttons()

WTAG_INVOKER = "WTAG_INVOKER"

class DataGatheringWidget(pbge.widgets.Widget):
    TAGS_TO_DEACTIVATE = {WTAG_INVOKER,}

    def __init__(self, data_gatherers: list, data_dict: dict, on_completion, on_cancel):
        # on_completion and on_cancel are callables that don't take any params.
        super().__init__(0,0,0,0)
        self.data_gatherers = list(data_gatherers)
        self.current_data_gatherer = None
        self.data_dict = data_dict
        self.on_completion = on_completion
        self.on_cancel = on_cancel

    def update(self, delta):
        super().update(delta)
        if self.active:
            if self.current_data_gatherer:
                # The only way this widget can be active with a current_data_gatherer set is if
                # the data gatherer has finished its work.
                if not self.current_data_gatherer.confirm(self.data_dict):
                    self.pop()
                    self.on_cancel()
                    return
                self.current_data_gatherer = None
            
            if self.data_gatherers:
                self.current_data_gatherer = self.data_gatherers.pop(0)
                self.current_data_gatherer.gather(self.data_dict)
            else: 
                # We have run out of data to gather.
                self.pop()
                self.on_completion()


class InvocationUI(pbge.widgets.Widget):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    SC_ENDCURSOR = 5
    SC_TRAILMARKER = 6
    SC_ZEROCURSOR = 7
    SC_ENEMYCURSOR = 12
    SC_GOODTARGET = 13
    SC_VOIDENEMYCURSOR = 14
    SC_VOIDGOODTARGET = 15
    LIBRARY_WIDGET = InvocationLibraryWidget

    TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_EXPLORATIONMODE,}

    def __init__(
        self, camp: gears.GearHeadCampaign, pc, build_library_function, on_invoke: On_Invoke,
        source=None, top_shelf_fun=None, auto_escape=False,
        bottom_shelf_fun=None, name="invocations", clock=None , **kwargs
    ):
        super().__init__(0,0,0,0, tags={WTAG_INVOKER, }, **kwargs)
        self.camp = camp
        self.pc = pc
        # self.change_invo(invo)
        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png', 64, 64)
        self.invo: pbge.effects.Invocation = None
        self.data = dict()

        self.legal_tiles = set()
        self.num_targets = 0
        self.targets = list()


        self.my_widget = self.LIBRARY_WIDGET(
            camp, pc, build_library_function, self.change_invo, start_source=source,
            top_shelf_fun=top_shelf_fun, bottom_shelf_fun=bottom_shelf_fun,
            auto_launch_fun=self.auto_launch
        )
        self.name = name

        self.targets_widget = pbge.widgets.LabelWidget(-300,68,200,0,font=pbge.MEDIUMFONT, justify=0, draw_border=True,
                                                       border=pbge.default_border, text_fun=self._get_target_count,
                                                       visible=False, anchor=pbge.frects.ANCHOR_UPPERRIGHT)
        self.my_widget.children.append(self.targets_widget)

        self.children.append(self.my_widget)
        self.record = False
        self.keep_exploring = True
        self.clock = clock
        self.ready_to_invoke = False

        self.firing_points = set()
        self.mypath = list()
        self.on_invoke = on_invoke
        self.auto_escape = auto_escape
        self.nav = None

    def _get_target_count(self, *_args):
        return "{}/{} Targets".format(len(self.targets), self.num_targets)

    def change_invo(self, new_invo):
        self.invo = new_invo
        if new_invo:
            self.legal_tiles = new_invo.area.get_targets(self.camp, self.pc.pos)
            self.num_targets = new_invo.targets
        else:
            self.legal_tiles = set()
            self.num_targets = 0
        self.targets = list()

    def set_top_shelf(self):
        self.my_widget.set_top_shelf()

    def set_bottom_shelf(self):
        self.my_widget.set_bottom_shelf()

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

    def _render(self, delta):
        if self.num_targets > 1:
            self.targets_widget.visible = True
        else:
            self.targets_widget.visible = False
        pbge.my_state.view.overlays.clear()

        # Find out what mecha are in the targeted tile.
        mmecha = [m for m in pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile, ()) if self.camp.scene.is_an_actor(m) and m.is_operational()]
        if mmecha and self.camp.scene.is_hostile_to_player(mmecha[0]):
            pbge.my_state.view.cursor.frame = self.SC_ENEMYCURSOR
        elif mmecha and self.invo and self.invo.ai_tar and self.invo.ai_tar.is_potential_target(self.camp, self.pc, mmecha[0]):
            pbge.my_state.view.cursor.frame = self.SC_GOODTARGET
        else:
            pbge.my_state.view.cursor.frame = self.SC_CURSOR

        pbge.my_state.view.overlays[self.pc.pos] = (self.cursor_sprite, self.SC_ORIGIN)

        if self.invo and self.invo.area.AUTOMATIC:
            aoe = self.invo.area.get_area(self.camp, self.pc.pos, pbge.my_state.view.mouse_tile)
            for p in aoe:
                pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_AOE)
        else:
            if self.invo and pbge.my_state.view.mouse_tile in self.legal_tiles:
                aoe = self.invo.area.get_area(self.camp, self.pc.pos, pbge.my_state.view.mouse_tile)
                for p in aoe:
                    pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_AOE)
                pbge.my_state.view.overlays[pbge.my_state.view.mouse_tile] = None
            if self.invo and self.targets:
                for t in self.targets:
                    aoe = self.invo.area.get_area(self.camp, self.pc.pos, t)
                    for p in aoe:
                        pbge.my_state.view.overlays[p] = (self.cursor_sprite, self.SC_AOE)
        if pbge.my_state.view.mouse_tile in self.legal_tiles:
            if self.clock:
                self.clock.indicate_mp_cost()
        elif mmecha and self.can_move_and_attack(mmecha[0].pos):
            if self.camp.fight:
                mp_remaining = self.camp.fight.cstat[self.pc].mp_remaining
                if self.clock:
                    self.clock.indicate_mp_cost(mp_to_spend=self.nav.cost_to_tile[self.mypath[-1]])
            else:
                mp_remaining = float('inf')
            traildrawer.draw_trail( self.cursor_sprite
                                  , self.SC_TRAILMARKER, None
                                  , self.mypath + [pbge.my_state.view.mouse_tile]
                                  )
        else:
            if mmecha and self.camp.scene.is_hostile_to_player(mmecha[0]):
                pbge.my_state.view.cursor.frame = self.SC_VOIDENEMYCURSOR
            elif mmecha and self.invo and self.invo.ai_tar and self.invo.ai_tar.is_potential_target(self.camp, self.pc,
                                                                                                    mmecha[0]):
                pbge.my_state.view.cursor.frame = self.SC_VOIDGOODTARGET
            else:
                pbge.my_state.view.cursor.frame = self.SC_VOIDCURSOR
            if self.clock:
                self.clock.indicate_mp_cost()

        # Display info for this tile.
        my_info = self.camp.scene.get_tile_info(pbge.my_state.view)
        if my_info:
            if self.invo and mmecha and hasattr(self.invo.fx, "get_odds"):
                odds, modifiers = self.invo.fx.get_odds(self.camp, self.pc, mmecha[0])
                my_info.info_blocks.append(info.OddsInfoBlock(odds, modifiers))
            my_info.view_display(self.camp)

    def launch(self):
        # This function is for use in combat. The explo_invoke class
        # method will handle invocations outside of combat.
        # Ideally, there should be a way to describe actions that works
        # both inside and outside of combat. I'm gonna think about that.
        self.ready_to_invoke = True
        self.data.clear()

        if self.invo.data_gatherers:
            DataGatheringWidget.push_state_and_instantiate(
                data_gatherers=self.invo.data_gatherers, data_dict=self.data, 
                on_completion=self._final_launch, on_cancel=self._cancel_launch
            )
        else:
            self._final_launch()

    def _cancel_launch(self):
        if self.auto_escape:
            self.pop()
        self.tidy()
        if not self.auto_escape:
            self.targets = list()
            self.my_widget.update_buttons()
            self.record = False
            self.activate()

    def _final_launch(self):
        if self.auto_escape:
            self.pop()
        self.tidy()
        self.on_invoke(self.invo, self.get_firing_pos(), self.targets, self.data)
        if not self.auto_escape:
            self.targets = list()
            self.my_widget.update_buttons()
            self.record = False
            #self.activate()

    def click_left(self):
        if self.invo.can_be_invoked(self.pc, bool(self.camp.fight)):
            if pbge.my_state.view.mouse_tile in self.legal_tiles:
                self.targets.append(pbge.my_state.view.mouse_tile)
            elif self.can_move_and_attack(pbge.my_state.view.mouse_tile) and pbge.my_state.view.modelmap.get(
                    pbge.my_state.view.mouse_tile):
                    self.targets.append(pbge.my_state.view.mouse_tile)

            if len(self.targets) >= self.num_targets and self.invo.can_be_invoked(self.pc, bool(self.camp.fight)):
                self.launch()

    def auto_launch(self):
        # Auto-launch will automatically launch an automatically targeted invocation.
        # Otherwise, it does nothing.
        if self.invo and self.invo.area.AUTOMATIC and self.invo.can_be_invoked(self.pc, bool(self.camp.fight)):
            while len(self.targets) < self.num_targets:
                self.targets.append(self.pc.pos)
            self.launch()
        else:
            self.click_left()

    def _builtin_responder(self, ev):
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not pbge.my_state.widget_responded:
            self.click_left()

        elif ev.type == pygame.KEYDOWN:
            if ev.unicode == "r":
                # self.camp.save(self.screen)
                self.record = True
                print("Recording")
                self.register_response()

            elif pbge.my_state.is_key_for_action(ev, "select"):
                self.auto_launch()
                self.register_response()

            elif pbge.my_state.is_key_for_action(ev, "cursor_click"):
                self.click_left()
                self.register_response()

            elif pbge.my_state.is_key_for_action(ev, "exit") and self.auto_escape:
                self.pop()
                self.tidy()
                self.register_response()

    def activate(self):
        self.visible = True
        self.legal_tiles = self.invo.area.get_targets(self.camp, self.pc.pos)
        if self.camp.fight:
            self.nav = self.camp.fight.get_action_nav(self.pc)

    def deactivate(self):
        # Used during combat only!
        self.visible = False
        self.my_widget.help_on = False
        self.tidy()
        pbge.my_state.view.cursor.frame = self.SC_VOIDCURSOR

    def update_nav(self):
        if self.camp.fight:
            self.nav = self.camp.fight.get_action_nav(self.pc)

    def get_firing_pos(self) -> tuple[int, int]:
        if self.targets[0] in self.legal_tiles:
            return self.pc.pos
        elif self.nav and self.camp.fight:
            self.firing_points = self.camp.fight.can_move_and_invoke(self.pc, self.nav, self.invo, self.targets[0])
            return min(self.firing_points, key=lambda r: self.nav.cost_to_tile.get(r, 10000))
        else:
            self.firing_points = self.invo.area.get_targets(self.camp, self.targets[0])
            mynav = pbge.scenes.pathfinding.AStarPath(self.camp.scene, self.pc.pos, self.targets[0], self.pc.mmode)
            if self.firing_points.intersection(list(mynav.cost_to_tile.keys())):
                return min(self.firing_points, key=lambda r: mynav.cost_to_tile.get(r, 10000))
            else:
                return self.pc.pos

    def name_current_invo(self):
        my_invo = self.my_widget.get_invo()
        if my_invo and my_invo.name:
            return my_invo.name
        else:
            return str(self.my_widget.invo)

    def name_current_option(self):
        op_list = list()
        op_list.append(self.my_widget.shelf.name)
        my_invo = self.my_widget.get_invo()
        if my_invo:
            op_list.append(self.name_current_invo())
        return op_list

    def tidy(self):
        pbge.my_state.view.cursor.frame = self.SC_VOIDCURSOR
        pbge.my_state.view.overlays.clear()

    def find_shelf_invo(self, op_list):
        # Attempt to find the requested shelf and invocation.
        shelf_name = op_list.pop(0)
        shelf = None
        for candidate in self.my_widget.library:
            if candidate.name == shelf_name:
                shelf = candidate
                break
        if shelf:
            invo = None
            if op_list:
                invo_name = op_list.pop(0)
                if invo_name.isdigit():
                    invo_num = int(invo_name)
                    if invo_num < len(shelf.invo_list):
                        invo = shelf.invo_list[invo_num]
                else:
                    for candidate in shelf.invo_list:
                        if candidate.name == invo_name:
                            invo = candidate
                            break

            if not invo:
                invo = shelf.get_first_working_invo(self.pc, bool(self.camp.fight))

            self.my_widget.set_shelf_invo(shelf, invo)

