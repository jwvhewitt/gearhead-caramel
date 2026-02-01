# Oh man... pcaction is the name of the kitchen sink "stuff the PC is capable of 
# doing" unit in GearHead Arena that over time morphed into the FieldHQ and phones unit.
# Also the save/load campaign stuff is in there. Wild.
#
# Anyhow, this unit should be more focused. I'm sticking the PlayerTurnWidget and its
# support stuff in here.

from game.combat import actions
import pygame
import pbge
from . import movementui, usableui
from . import targetingui
from . import programsui
from .. import configedit, invoker


class BonusActionWidget(pbge.widgets.ButtonWidget):
    def __init__(self, pc, camp, on_buy_action):
        self.pc = pc
        self.camp = camp
        self.comrec = camp.fight.cstat[pc]
        self.on_buy_action = on_buy_action
        super().__init__(
            -80, 13, 32, 32,
            sprite=pbge.image.Image("sys_bonusaction_widget.png", 32, 32),
            frame=0, on_frame=0, off_frame=1,
            anchor=pbge.frects.ANCHOR_TOP, tooltip="Actions Remaining",
            on_click=self.buy_action
        )
        self.last_update = None

    def buy_action(self, *_args):
        if self.comrec.can_buy_bonus_action():
            self.comrec.buy_bonus_action()
            self.on_buy_action()

    def _render(self, delta):
        if self.frame == self.on_frame and not self.comrec.can_buy_bonus_action():
            self.frame = self.off_frame
        if self.last_update != self.comrec.extra_actions_taken:
            self.last_update = self.comrec.extra_actions_taken
            self.tooltip = "Spend {} SP for +1 Action".format(self.comrec.bonus_action_cost())

        super()._render(delta)


class ActionClockWidget(pbge.widgets.Widget):
    ACTION_QUARTER_ANCHORS = (
        (27, 2), (27, 27), (2, 27), (2, 2)
    )
    def __init__(self, pc, camp):
        self.pc = pc
        self.camp = camp
        self.bg_image = pbge.image.Image("sys_actionclock_bg.png")
        self.quarters = pbge.image.Image("sys_actionclock_quarters.png", 23, 23)
        self.ap_to_spend = 0
        self.mp_to_spend = 0

        super().__init__(-42, 2, 54, 54, anchor=pbge.frects.ANCHOR_TOP, tooltip="Actions Remaining")

    def set_ap_mp_costs(self, ap_to_spend=0, mp_to_spend=0):
        self.ap_to_spend = ap_to_spend
        self.mp_to_spend = mp_to_spend

    def _draw_clock(self, actions, leftover, frame_offset=0):
        if actions > 4:
            actions = 4
            leftover = 0
        if actions > 0:
            for t in range(actions):
                adest = self.get_rect()
                adest.x += self.ACTION_QUARTER_ANCHORS[t][0]
                adest.y += self.ACTION_QUARTER_ANCHORS[t][1]
                self.quarters.render(adest, t*32 + frame_offset)
        if leftover > 0:
            adest = self.get_rect()
            adest.x += self.ACTION_QUARTER_ANCHORS[actions][0]
            adest.y += self.ACTION_QUARTER_ANCHORS[actions][1]
            frame = actions * 32 + min(max((16 * (100-leftover))//100, 0), 15) + frame_offset
            if leftover < 50:
                frame = max(frame, actions * 32 + 9 + frame_offset)
            else:
                frame = min(frame, actions * 32 + 8 + frame_offset)
            self.quarters.render(adest, frame)

    def _render(self, delta):
        mydest = self.get_rect()
        self.bg_image.render(mydest)
        actions, leftover = self.camp.fight.cstat[self.pc].get_actions_and_move_percent()
        self._draw_clock(actions, leftover, frame_offset=16)
        actions, leftover = self.camp.fight.cstat[self.pc].get_modified_actions_and_move_percent(self.ap_to_spend, self.mp_to_spend)
        self._draw_clock(actions, leftover)


class WaypointBumper:
    # A special action so the player can go bump a waypoint.
    def __init__(self, pc, camp, turn, nav, wp, dest):
        self.pc = pc
        self.camp = camp
        self.turn = turn
        self.nav = nav
        self.wp = wp
        self.dest = dest

    def __call__(self):
        dest = self.camp.fight.move_model_to(self.pc, self.nav, self.dest)
        self.turn.movement_ui.needs_tile_update = True
        if dest == self.dest:
            self.wp.combat_bump(self.camp, self.pc)


class PlayerTurn(pbge.widgets.Widget):
    # It's the player's turn. Allow the player to control this PC.
    def __init__(self, pc, camp):
        super().__init__(0,0,0,0,tags={pbge.scenes.viewer.WTAG_DEACTIVATE_DURING_ANIMATION,})
        self.pc = pc
        self.camp = camp
        self.active_ui = None

        myclock = ActionClockWidget(self.pc, self.camp)
        self.children.append(myclock)
        my_bonus_action_button = BonusActionWidget(self.pc, self.camp, self._update_current_nav)
        myclock.children.append(my_bonus_action_button)

        # How this is gonna work: There are several modes that can be switched
        #  between: movement, attack, use skill, etc. Each mode is gonna get
        #  a handler. The radio buttons widget determines what mode is current.
        #  Then, this routine routes the input to the correct UI handler.
        # Create all the UIs first. Then create the top_shelf and bottom_shelf switch lists based
        # on which UIs this character needs.
        self.all_funs = dict()
        self.all_uis = list()

        buttons_to_add = [
            dict(on_frame=6, off_frame=7, on_click=self.switch_movement, tooltip='Movement'),
            dict(on_frame=2, off_frame=3, on_click=self.switch_attack, tooltip='Attack',
                 on_right_click=self._use_attack_menu),
        ]

        self.movement_ui = movementui.MovementUI(
            self.camp, self.pc, on_move=self._on_move, on_switch_to_attack=self.switch_attack,
            top_shelf_fun=self.switch_top_shelf, bottom_shelf_fun=self.switch_bottom_shelf, clock=myclock,
            visible=True
        )
        self.all_uis.append(self.movement_ui)
        self.all_funs[self.movement_ui] = self.switch_movement

        self.attack_ui = targetingui.TargetingUI(
            self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
            on_invoke=self._on_invoke, visible=False,
            bottom_shelf_fun=self.switch_bottom_shelf, name="attacks", clock=myclock
        )
        self.all_uis.append(self.attack_ui)
        self.all_funs[self.attack_ui] = self.switch_attack

        has_skills = self.pc.get_skill_library(True)
        self.skill_ui = invoker.InvocationUI(self.camp, self.pc, self._get_skill_library,
                                             top_shelf_fun=self.switch_top_shelf, name="skills",
                                             on_invoke=self._on_invoke, visible=False,
                                             bottom_shelf_fun=self.switch_bottom_shelf, clock=myclock)
        if has_skills:
            buttons_to_add.append(
                dict(on_frame=8, off_frame=9, on_click=self.switch_skill, tooltip='Skills',
                     on_right_click=self._use_skills_menu)
            )
            self.all_uis.append(self.skill_ui)
            self.all_funs[self.skill_ui] = self.switch_skill

        has_programs = self.pc.get_program_library()
        self.program_ui = programsui.ProgramsUI(
            self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
            on_invoke=self._on_invoke, visible=False,
            bottom_shelf_fun=self.switch_bottom_shelf, name="programs", clock=myclock
        )
        if has_programs:
            buttons_to_add.append(
                dict(on_frame=10, off_frame=11, on_click=self.switch_programs, tooltip='Programs',
                     on_right_click=self._use_programs_menu)
            )
            self.all_uis.append(self.program_ui)
            self.all_funs[self.program_ui] = self.switch_programs

        has_usables = self.pc.get_usable_library()
        self.usable_ui = usableui.UsablesUI(
            self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
            on_invoke=self._on_invoke, visible=False,
            bottom_shelf_fun=self.switch_bottom_shelf, name="usables", clock=myclock
        )
        if has_usables:
            buttons_to_add.append(
                dict(on_frame=12, off_frame=13, on_click=self.switch_usables, tooltip='Usables',
                     on_right_click=self._use_usables_menu)
            )
            self.all_uis.append(self.usable_ui)
            self.all_funs[self.usable_ui] = self.switch_usables

        buttons_to_add.append(
            dict(on_frame=4, off_frame=5, on_click=self.end_turn, tooltip='End Turn')
        )
        self.my_radio_buttons = pbge.widgets.RadioButtonWidget(8, 8, 220, 40,
                                                               sprite=pbge.image.Image('sys_combat_mode_buttons.png',
                                                                                       40, 40),
                                                               buttons=buttons_to_add,
                                                               anchor=pbge.frects.ANCHOR_UPPERLEFT)
        self.children.append(self.my_radio_buttons)
        for ui in self.all_uis:
            self.children.append(ui)

        # Add the top_shelf and bottom_shelf functions
        self.top_shelf_funs = dict()
        self.bottom_shelf_funs = dict()
        for t in range(len(self.all_uis)):
            if t > 0:
                self.top_shelf_funs[self.all_uis[t]] = self.all_funs[self.all_uis[t - 1]]
            if t < (len(self.all_uis) - 1):
                self.bottom_shelf_funs[self.all_uis[t]] = self.all_funs[self.all_uis[t + 1]]

        self.active_ui: invoker.InvocationUI|movementui.MovementUI = self.movement_ui

        # Right before starting the player's turn, if announce_pc_turn_start is turned on, announce it.
        if pbge.util.config.getboolean("GENERAL", "announce_pc_turn_start"):
            _=pbge.alerts.TextAlert("{}'s Turn".format(self.pc.get_pilot()), font=pbge.BIGFONT, justify=0)

        self.actions = list()

    def _on_move(self, *my_actions):
        self.actions += my_actions

    def _on_invoke(self, invo, firing_pos, targets, data):
        if firing_pos != self.pc.pos:
            self.actions.append(actions.MoveModelToPos(self.camp, self.pc, self.camp.fight.get_action_nav(self.pc), firing_pos))
        self.actions.append(actions.InvokeInvocation(self.camp, invo, firing_pos, self.pc, targets, data))

    def end_turn(self, _button, _ev):
        self.camp.fight.cstat[self.pc].end_turn()

    def switch_movement(self, _button=None, _ev=None):
        if self.active_ui != self.movement_ui:
            self.active_ui.deactivate()
            self.movement_ui.activate()
            self.active_ui = self.movement_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_attack(self, _button=None, _ev=None):
        if self.active_ui != self.attack_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_attack_library():
                self.active_ui.deactivate()
                self.attack_ui.activate()
                self.active_ui = self.attack_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[1])
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_skill(self, _button=None, _ev=None):
        if self.active_ui != self.skill_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_skill_library(True):
                self.active_ui.deactivate()
                self.skill_ui.activate()
                self.active_ui = self.skill_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.get_button(self.switch_skill))
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_programs(self, _button=None, _ev=None):
        if self.active_ui != self.program_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_program_library():
                self.active_ui.deactivate()
                self.program_ui.activate()
                self.active_ui = self.program_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.get_button(self.switch_programs))
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_usables(self, _button=None, _ev=None):
        if self.active_ui != self.usable_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_usable_library():
                self.active_ui.deactivate()
                self.usable_ui.activate()
                self.active_ui = self.usable_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.get_button(self.switch_usables))
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_top_shelf(self):
        if self.active_ui in self.top_shelf_funs:
            self.top_shelf_funs[self.active_ui]()
            if pbge.util.config.getboolean("GENERAL", "scroll_to_start_of_action_library") and hasattr(self.active_ui, "set_top_shelf"):
                _=self.active_ui.set_top_shelf()
            elif hasattr(self.active_ui, "set_bottom_shelf"):
                _=self.active_ui.set_bottom_shelf()

    def switch_bottom_shelf(self):
        if self.active_ui in self.bottom_shelf_funs:
            self.bottom_shelf_funs[self.active_ui]()
            if hasattr(self.active_ui, "set_top_shelf"):
                _=self.active_ui.set_top_shelf()

    def _focus_on_pc_from_menu(self, _wid, _ev):
        # Focus on the PC from the popup menu.
        pbge.my_state.view.focus(self.pc.pos[0], self.pc.pos[1])

    def _quit_the_game_from_menu(self, _wid, _ev):
        # Quit the game from the popup menu.
        self.camp.fight.no_quit = False

    ACCEPTABLE_HOTKEYS = "abcdefghijklmnopqrstuvwxyz1234567890"

    def pop_menu(self):
        # Pop Pop PopMenu Pop Pop PopMenu
        mymenu = pbge.widgetmenu.PopupMenuWidget(auto_escape=True)
        mynav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene, self.pc.pos, self.camp.fight.cstat[
                self.pc].total_mp_remaining, self.pc.mmode, self.camp.scene.get_blocked_tiles())
        path = pbge.scenes.pathfinding.AStarPath(self.camp.scene, self.pc.pos, pbge.my_state.view.mouse_tile,
                                                 self.pc.mmode)
        if len(path.results) > 1 and path.results[-2] in mynav.cost_to_tile:
            for wp in self.camp.scene.get_waypoints(pbge.my_state.view.mouse_tile):
                if hasattr(wp, "combat_bump"):
                    _=mymenu.add_item("Use {}".format(wp.name), self._bump_waypoint_from_popup_menu, data=(wp, mynav, path.results[-2]))

        _=mymenu.add_item("Center on {}".format(self.pc.get_pilot()), self._focus_on_pc_from_menu)
        _=mymenu.add_item("Record hotkey for current action", self._record_hotkey_from_menu)
        _=mymenu.add_item("View hotkeys", self._view_hotkeys_from_menu)
        _=mymenu.add_item("Quit Game", self._quit_the_game_from_menu)

        mymenu.push_and_deploy()

    def _bump_waypoint_from_popup_menu(self, wid, _ev):
        wp, mynav, dest = wid.data
        if dest != self.pc.pos:
            self.actions.append(actions.MoveModelToPos(self.camp, self.pc, mynav, dest))
        self.actions.append(actions.BumpWaypoint(self.camp, self.pc, wp))

    def find_this_option(self, op_string):
        op_list = op_string.split('/')
        ui_name = op_list.pop(0)
        myui = None
        for ui in self.all_uis:
            if ui.name == ui_name and ui in self.all_funs:
                self.all_funs[ui]()
                myui = ui
                break
        if op_list and myui and hasattr(myui, "find_shelf_invo"):
            myui.find_shelf_invo(op_list)

    def name_current_option(self):
        op_list = list()
        op_list.append(self.active_ui.name)
        if hasattr(self.active_ui, "name_current_option"):
            op_list += self.active_ui.name_current_option()
        return '/'.join(op_list)

    def record_hotkey(self, mykey):
        if not mykey:
            return

        option_string = self.name_current_option()

        pbge.util.config.set("HOTKEYS", mykey, option_string)
        _=pbge.BasicNotification("New hotkey set: {} = {}".format(mykey, option_string), count=200)
        # Export the new config options.
        current_use = pbge.my_state.key_is_in_use(mykey)
        if current_use:
            _=pbge.alerts.TextAlert("Warning: Key {} is currently in use by \"{}\". It can't be used as a hotkey unless you change your key configuration.".format(mykey, current_use))

        with open(pbge.util.user_dir("config.cfg"), "wt") as f:
            pbge.util.config.write(f)

    def _record_hotkey_from_menu(self, _wid, _ev):
        # TODO: replace this alert with a custom widget
        _=pbge.alerts.TextAlert(
            "Press a letter or number key to record a new macro for {}. You could also do this by holding Alt + key.".format(
                self.name_current_option()),
            on_close=self._receive_hotkey
        )

    def _receive_hotkey(self, _wid, ev):
        if ev.type == pygame.KEYDOWN and ev.unicode in self.ACCEPTABLE_HOTKEYS:
            self.record_hotkey(ev.unicode)

    def _view_hotkeys_from_menu(self, _wid, _ev):
        mymenu = pbge.widgetmenu.MenuWidget(
            -250, -100, 500, 200, font=pbge.my_state.big_font,
            auto_escape=True,
        )
        for op in pbge.util.config.options("HOTKEYS"):
            _=mymenu.add_item("{}: {}".format(op, pbge.util.config.get("HOTKEYS", op)), mymenu.auto_escape_fun)
        _=mymenu.add_item("[Exit]", mymenu.auto_escape_fun)
        mymenu.push_and_deploy(self)

    def _use_attack_menu(self, _button, _ev):
        mymenu = pbge.widgetmenu.PopupMenuWidget(auto_escape=True)
        for shelf in self.attack_ui.my_widget.library:
            _=mymenu.add_item(shelf.name, self._find_option_from_menu, data='/'.join([self.attack_ui.name, shelf.name, '0']))
        mymenu.push_and_deploy()

    def _find_option_from_menu(self, wid, _ev):
        op = wid.data
        if op:
            self.find_this_option(op)

    def _use_skills_menu(self, _button, _ev):
        mymenu = pbge.widgetmenu.PopupMenuWidget(auto_escape=True)
        for shelf in self.skill_ui.my_widget.library:
            _=mymenu.add_item(shelf.name, self._find_option_from_menu, data='/'.join([self.skill_ui.name, shelf.name, '0']))
        mymenu.push_and_deploy()

    def _use_programs_menu(self, _button, _ev):
        mymenu = pbge.widgetmenu.PopupMenuWidget(auto_escape=True)
        for shelf in self.program_ui.my_widget.library:
            _=mymenu.add_item(shelf.name, self._find_option_from_menu, data='/'.join([self.program_ui.name, shelf.name, '0']))
        mymenu.push_and_deploy()

    def _use_usables_menu(self, _button, _ev):
        mymenu = pbge.widgetmenu.PopupMenuWidget(auto_escape=True)
        for shelf in self.usable_ui.my_widget.library:
            _=mymenu.add_item(shelf.name, self._find_option_from_menu, data='/'.join([self.usable_ui.name, shelf.name, '0']))
        mymenu.push_and_deploy()

    def _update_current_nav(self):
        if isinstance(self.active_ui, movementui.MovementUI):
            self.active_ui.needs_tile_update = True
        else:
            self.active_ui.update_nav()

    def _get_skill_library(self):
        return self.pc.get_skill_library(True)

    def _builtin_responder(self, ev):
        if not self.actions:
            if self.camp.fight.still_fighting() and (self.pc in self.camp.scene.contents) and self.camp.fight.cstat[self.pc].can_act():
                if ev.type == pygame.KEYDOWN:
                    if ev.unicode and ev.unicode in self.ACCEPTABLE_HOTKEYS and ev.mod & pygame.KMOD_ALT:
                        # Record a hotkey.
                        self.record_hotkey(ev.unicode)
                        self.register_response()
                    elif ev.unicode in self.ACCEPTABLE_HOTKEYS and pbge.util.config.has_option("HOTKEYS", ev.unicode) and not pbge.my_state.key_is_in_use(ev.unicode):
                        self.find_this_option(pbge.util.config.get("HOTKEYS", ev.unicode))
                        self.register_response()
                    elif pbge.my_state.is_key_for_action(ev, "quit_game"):
                        pbge.my_state.session_data[pbge.campaign.SDAT_GOT_QUIT] = True
                        self.register_response()
                    elif ev.key == pygame.K_ESCAPE:
                        configedit.PopupGameMenu().push_state_and_instantiate()
                        self.register_response()
                elif ev.type == pygame.MOUSEBUTTONUP:
                    if ev.button == 3 and not pbge.my_state.widget_responded:
                        self.pop_menu()
                        self.register_response()

    def update(self, delta):
        super().update(delta)
        if self.active:
            if self.actions:
                self.visible = False
                if not pbge.my_state.view.has_animations():
                    # It shouldn't be necessary to check this, since this
                    # widget deactivates during animations. But, this is me
                    # future-proofing stuff in case that changes.
                    act = self.actions[0]
                    if not act():
                        self.actions.pop(0)
            else:
                self.visible = True
                if not (self.camp.fight.cstat[self.pc].can_act() and self.camp.fight.still_fighting()):
                    self.pop()

            

