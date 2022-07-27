import gears.tags
import pbge
import gears
from gears import info
from game import traildrawer
import pygame


class MovementWidget(pbge.widgets.Widget):
    # This widget stores the movement icons and lets the player switch movemodes.
    IMAGE_NAME = 'sys_invokerinterface_movement.png'
    MENU_POS = (-380, 15, 200, 180)
    DESC_POS = (-160, 15, 140, 180)

    def __init__(
            self, camp, pc, update_callback, start_source=None,
            top_shelf_fun=None, bottom_shelf_fun=None, **kwargs
    ):
        # update_callback is a function that gets called when the move mode
        #   is changed. It passes the new move mode as a parameter.
        # top_shelf_fun and bottom_shelf_fun are functions called when the user
        #   tries to scroll up or down. Unlike the invocation widgets, this widget only has one shelf,
        #   so unless these functions are defined scrolling up and down does nothing. Nothing!
        super().__init__(-383, -5, 383, 57, anchor=pbge.frects.ANCHOR_UPPERRIGHT, **kwargs)
        self.camp = camp
        self.pc = pc

        self.update_callback = update_callback
        self.top_shelf_fun = top_shelf_fun
        self.bottom_shelf_fun = bottom_shelf_fun
        self.active_button = 0
        # The shelf_offset tells the index of the first movemode in the menu.
        self.shelf_offset = 0

        self.selection = 0
        self.mmodes = list()

        self.label = pbge.widgets.LabelWidget(12, 15, 208, 21, str(self.pc), font=pbge.BIGFONT, parent=self,
                                              anchor=pbge.frects.ANCHOR_UPPERLEFT)
        self.children.append(self.label)
        if isinstance(self.pc, gears.base.Mecha):
            self.children.append(pbge.widgets.LabelWidget(
                26, 37, 212, 14, str(self.pc.get_pilot()), font=pbge.MEDIUMFONT, parent=self,
                anchor=pbge.frects.ANCHOR_UPPERLEFT, color=pbge.WHITE
            ))

        self.buttons = list()
        self.movemode_sprite = pbge.image.Image("sys_movemode_default.png", 32, 32)
        ddx = 231
        for t in range(4):
            self.buttons.append(
                pbge.widgets.ButtonWidget(ddx, 16, 32, 32, None, on_click=self.click_button, data=t, parent=self,
                                          anchor=pbge.frects.ANCHOR_UPPERLEFT))
            ddx += 34
        self.children += self.buttons

        self.sprite = pbge.image.Image(self.IMAGE_NAME, 383, 57)
        self._update_move_modes()
        if start_source:
            self.select_requested_movemode(start_source)
        else:
            self.select_current_movemode()

    def _builtin_responder(self, ev):
        # Respond to keyboard and mouse scroll events.
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 4:
                self.prev_shelf()
            elif ev.button == 5:
                self.next_shelf()
        elif ev.type == pygame.KEYDOWN:
            if ev.key in pbge.my_state.get_keys_for("up"):
                self.prev_shelf()
            elif ev.key in pbge.my_state.get_keys_for("down"):
                self.next_shelf()
            elif ev.key in pbge.my_state.get_keys_for("left"):
                self.prev_invo()
            elif ev.key in pbge.my_state.get_keys_for("right"):
                self.next_invo()

    def _update_move_modes(self):
        self.mmodes = list()
        for mm in gears.tags.MOVEMODE_LIST:
            if self.camp.scene.can_use_movemode(mm) and self.pc.get_speed(mm) > 0:
                self.mmodes.append(mm)

        if self.camp.scene.can_use_movemode(gears.tags.Jumping) and self.pc.get_speed(gears.tags.Jumping) > 0:
            self.mmodes.append(gears.tags.Jumping)

    def prev_invo(self):
        if self.selection > 0:
            self.set_selection(self.selection - 1)

    def next_invo(self):
        if self.selection < (len(self.mmodes) - 1):
            self.set_selection(self.selection + 1)

    def prev_shelf(self):
        if self.top_shelf_fun:
            self.top_shelf_fun()

    def next_shelf(self):
        if self.bottom_shelf_fun:
            self.bottom_shelf_fun()

    def click_button(self, button, ev):
        target_mm = button.data + self.shelf_offset
        if target_mm < len(self.mmodes):
            self.set_selection(target_mm)

    def set_selection(self, new_selection):
        self.selection = new_selection
        if self.selection > 3:
            self.shelf_offset = self.selection - 3
        else:
            self.shelf_offset = 0
        self.update_buttons()

    def select_current_movemode(self):
        self.selection = self.mmodes.index(self.pc.mmode)
        self.update_buttons()

    def select_requested_movemode(self, mmode):
        self.update_buttons()

    def _generate_tooltip(self, mmode):
        return '{} ({})'.format(mmode, self.pc.get_speed(mmode))

    def render(self, flash=False):
        self.sprite.render(self.get_rect(), 0)

    MOVEMODE_FRAMES = {
        pbge.scenes.movement.Walking: 0,
        pbge.scenes.movement.Flying: 9,
        gears.tags.Skimming: 6,
        gears.tags.Rolling: 3,
        gears.tags.SpaceFlight: 12,
        gears.tags.Jumping: 15,
        gears.tags.Cruising: 18
    }

    def update_buttons(self):
        self._update_move_modes()

        for butt in range(4):
            if butt + self.shelf_offset < len(self.mmodes):
                mmode = self.mmodes[butt + self.shelf_offset]
                self.buttons[butt].sprite = self.movemode_sprite
                if not self.camp.scene.can_use_movemode_here(mmode, *self.pc.pos) and mmode is not gears.tags.Jumping:
                    self.buttons[butt].frame = self.MOVEMODE_FRAMES[mmode] + 2
                elif butt + self.shelf_offset == self.selection:
                    self.buttons[butt].frame = self.MOVEMODE_FRAMES[mmode]
                else:
                    self.buttons[butt].frame = self.MOVEMODE_FRAMES[mmode] + 1
                self.buttons[butt].tooltip = self._generate_tooltip(mmode)
            else:
                self.buttons[butt].sprite = None
                self.buttons[butt].tooltip = None
        self.update_callback(self.get_move_mode())

    def get_move_mode(self):
        if self.selection < len(self.mmodes):
            return self.mmodes[self.selection]


class JumpNav(object):
    def __init__(self, camp, pc):
        self.camp = camp
        self.pc = pc
        self.cost_to_tile = dict()

    def get_path(self, dest_pos):
        pass


class MovementUI(object):
    SC_ORIGIN = 4
    SC_AOE = 2
    SC_CURSOR = 3
    SC_VOIDCURSOR = 0
    SC_ENDCURSOR = 5
    SC_TRAILMARKER = 6
    SC_ZEROCURSOR = 7

    def __init__(self, camp, mover, top_shelf_fun=None, bottom_shelf_fun=None, name="movement", clock=None):
        self.camp = camp
        self.mover = mover
        self.origin = mover.pos
        self.needs_tile_update = True
        self.name = name

        self.cursor_sprite = pbge.image.Image('sys_mapcursor.png', 64, 64)
        self.my_widget = MovementWidget(camp, mover, self.change_movemode, top_shelf_fun=top_shelf_fun,
                                        bottom_shelf_fun=bottom_shelf_fun)
        self.selected_mmode = mover.mmode

        self.reachable_waypoints = dict()
        self.clock = clock
        pbge.my_state.widgets.append(self.my_widget)

    def render(self):
        pbge.my_state.view.overlays.clear()
        pbge.my_state.view.overlays[self.origin] = (self.cursor_sprite, self.SC_ORIGIN)

        if pbge.my_state.view.mouse_tile in self.nav.cost_to_tile:
            mypath = self.nav.get_path(pbge.my_state.view.mouse_tile)

            # Draw the trail, highlighting where one action point ends and the next begins.
            traildrawer.draw_trail(self.cursor_sprite
                                   , self.SC_TRAILMARKER, self.SC_ZEROCURSOR, self.SC_ENDCURSOR
                                   , self.camp.scene, self.mover
                                   , self.camp.fight.cstat[self.mover].mp_remaining
                                   , mypath
                                   )
            self.clock.set_ap_mp_costs(mp_to_spend=self.nav.cost_to_tile[pbge.my_state.view.mouse_tile])
        elif pbge.my_state.view.mouse_tile in self.reachable_waypoints:
            wp, pos = self.reachable_waypoints[pbge.my_state.view.mouse_tile]
            mypath = self.nav.get_path(pos)

            # Draw the trail, highlighting where one action point ends and the next begins.
            traildrawer.draw_trail(self.cursor_sprite
                                   , self.SC_TRAILMARKER, self.SC_ZEROCURSOR, self.SC_ENDCURSOR
                                   , self.camp.scene, self.mover
                                   , self.camp.fight.cstat[self.mover].mp_remaining
                                   , mypath
                                   )
            self.clock.set_ap_mp_costs(ap_to_spend=1, mp_to_spend=self.nav.cost_to_tile[mypath[-1]])

        else:
            pbge.my_state.view.overlays[pbge.my_state.view.mouse_tile] = (self.cursor_sprite, self.SC_VOIDCURSOR)
            self.clock.set_ap_mp_costs()

        pbge.my_state.view()

        # Display info for this tile.
        my_info = self.camp.scene.get_tile_info(pbge.my_state.view.mouse_tile)
        if my_info:
            my_info.popup()

        pbge.my_state.do_flip()

    def change_movemode(self, new_mm):
        self.selected_mmode = new_mm
        if new_mm is not self.mover.mmode:
            self.camp.fight.cstat[self.mover].reset_movement()
        if new_mm is not gears.tags.Jumping:
            self.mover.mmode = new_mm
        self.needs_tile_update = True

    def update_tiles(self):
        # Step one: figure out which tiles can be reached from here.
        self.origin = self.mover.pos
        self.nav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene, self.origin, self.camp.fight.cstat[
            self.mover].total_mp_remaining, self.mover.mmode, self.camp.scene.get_blocked_tiles())

        # Calculate the paths for the waypoints.
        self.reachable_waypoints.clear()
        for wp in self.camp.scene.contents:
            if hasattr(wp, "combat_bump") and hasattr(wp, "pos") and self.camp.scene.on_the_map(*wp.pos):
                path = pbge.scenes.pathfinding.AStarPath(self.camp.scene, self.mover.pos, wp.pos, self.mover.mmode)
                if len(path.results) > 1 and path.results[-2] in self.nav.cost_to_tile:
                    self.reachable_waypoints[wp.pos] = (wp, path.results[-2])

    def click_left(self, player_turn):
        if pbge.my_state.view.mouse_tile in self.nav.cost_to_tile:
            # Move!
            dest = self.camp.fight.move_model_to(self.mover, self.nav, pbge.my_state.view.mouse_tile)
            self.needs_tile_update = True
        elif pbge.my_state.view.mouse_tile in self.reachable_waypoints:
            # Bump!
            wp, target_tile = self.reachable_waypoints[pbge.my_state.view.mouse_tile]
            dest = self.camp.fight.move_model_to(self.mover, self.nav, target_tile)
            self.needs_tile_update = True
            if dest == target_tile:
                wp.combat_bump(self.camp, self.mover)
        else:
            mmecha = pbge.my_state.view.modelmap.get(pbge.my_state.view.mouse_tile)
            if mmecha and self.camp.scene.player_team.is_enemy(self.camp.scene.local_teams.get(mmecha[0])):
                player_turn.switch_attack()

    def update(self, ev, player_turn):
        # We just got an event. Deal with it.
        if self.needs_tile_update:
            self.update_tiles()
            self.needs_tile_update = False

        if self.camp.fight.cstat[self.mover].action_points < 1 and self.camp.fight.cstat[
            self.mover].mp_remaining < self.nav.cheapest_move:
            self.camp.fight.cstat[self.mover].end_turn()
        elif ev.type == pbge.TIMEREVENT:
            self.render()
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not pbge.my_state.widget_clicked:
            self.click_left(player_turn)
        elif ev.type == pygame.KEYDOWN:
            if ev.key in pbge.my_state.get_keys_for("cursor_click") and not pbge.my_state.widget_clicked:
                self.click_left(player_turn)

            elif ev.unicode == "t":
                mypos = pbge.my_state.view.mouse_tile
                myscene = self.camp.scene
                print("Ground: {}\n Wall: {}\n Decor: {}".format(myscene.get_floor(*mypos), myscene.get_wall(*mypos),
                                                                 myscene.get_decor(*mypos)))

    def dispose(self):
        # Get rid of the widgets and shut down.
        pbge.my_state.widgets.remove(self.my_widget)

    def activate(self):
        self.my_widget.active = True
        self.needs_tile_update = True

    def deactivate(self):
        self.my_widget.active = False
