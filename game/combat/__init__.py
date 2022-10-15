# Combat Actions:
# - Move
# - Attack
# - Skill (including talents, talking, etc)
# - EW Attack
# - Cover (overwatch)
# - Use usable gear
# - Access inventory

import pbge
from pbge import scenes
import collections
import pygame
from . import movementui, usableui
from . import targetingui
from . import programsui
from . import aibrain
from . import aihaywire
from game import fieldhq
import random
import gears
from .. import configedit, invoker
from game.content import ghcutscene

ALT_AIS = {
    "HaywireAI": aihaywire.HaywireTurn
}


class CombatStat(object):
    """Keep track of some stats that only matter during combat."""

    def __init__(self, combatant):
        self.combatant = combatant
        self.aoo_readied = False
        self.attacks_this_round = 0
        self.moves_this_round = 0
        self._mp_spent = 0
        self._ap_remaining = 0
        self.has_started_turn = False
        self.last_weapon_used = None
        self.last_program_used = None

    @property
    def mp_remaining(self):
        return self.combatant.get_current_speed() - self._mp_spent

    @property
    def total_mp_remaining(self):
        return self._ap_remaining * self.combatant.get_current_speed() - self._mp_spent

    @property
    def action_points(self):
        base_ap = self._ap_remaining
        if hasattr(self.combatant, "get_current_speed") and self._mp_spent > (self.combatant.get_current_speed()//2):
            base_ap -= 1
        return base_ap

    def can_act(self):
        return self.action_points > 0

    def spend_ap(self, ap):
        self._ap_remaining -= ap
        if hasattr(self.combatant, "get_current_speed") and self._mp_spent > (self.combatant.get_current_speed()//2):
            self._ap_remaining -= 1
        self._mp_spent = 0

    def spend_mp(self, mp):
        self._mp_spent += mp
        if hasattr(self.combatant, "get_current_speed"):
            speed = self.combatant.get_current_speed()
            if speed > 0:
                while self._mp_spent >= speed and self._ap_remaining > 0:
                    self._mp_spent -= speed
                    self._ap_remaining -= 1
            else:
                self.end_turn()
        else:
            self.end_turn()

    def reset_movement(self):
        if self._mp_spent > 0:
            self.spend_ap(1)

    def start_turn(self, chara):
        self._ap_remaining += chara.get_action_points()
        self.has_started_turn = True
        self.moves_this_round = 0
        self.attacks_this_round = 0
        self._mp_spent = 0

    def end_turn(self):
        if self._ap_remaining > 0:
            self._ap_remaining = 0
        self._mp_spent = 0

    def get_actions_and_move_percent(self):
        if hasattr(self.combatant, "get_current_speed") and self.combatant.get_current_speed() > 0 and self._mp_spent > 0:
            return self._ap_remaining - 1, (self.combatant.get_current_speed() - self._mp_spent)*100 // self.combatant.get_current_speed()
        else:
            return self.action_points, 0

    def get_modified_actions_and_move_percent(self, ap_to_spend=0, mp_to_spend=0):
        mp_spent = mp_to_spend + self._mp_spent
        ap_spent_on_movement = 0
        if hasattr(self.combatant, "get_current_speed"):
            speed = self.combatant.get_current_speed()
            if speed > 0:
                while mp_spent >= speed:
                    mp_spent -= speed
                    ap_spent_on_movement += 1

            #else:
                #ap_spent_on_movement = 999999999

            if ap_to_spend > 0 and mp_spent > (self.combatant.get_current_speed()//2):
                ap_to_spend += 1

        if ap_to_spend > 0 and mp_spent > 0:
            mp_spent = 0
        ap_to_spend += ap_spent_on_movement

        if hasattr(self.combatant, "get_current_speed") and self.combatant.get_current_speed() > 0 and mp_spent > 0:
            return max(self._ap_remaining - 1 - ap_to_spend, 0), (self.combatant.get_current_speed() - mp_spent)*100 // self.combatant.get_current_speed()
        else:
            return max(self.action_points - ap_to_spend, 0), 0


class CombatDict(object):
    def __init__(self):
        self._entries = dict()

    def __getitem__(self, key):
        if key in self._entries:
            return self._entries[key]
        else:
            val = CombatStat(key)
            self._entries[key] = val
            return val

    @classmethod
    def from_dict(cls, my_dict):
        nu_dict = cls()
        for k, v in my_dict.items():
            v = CombatStat(k)
            nu_dict._entries[k] = v
        return nu_dict


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

        super().__init__(-26, 2, 54, 54, anchor=pbge.frects.ANCHOR_TOP, tooltip="Actions Remaining")

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
            self.quarters.render(adest, frame)

    def render(self, flash=False):
        mydest = self.get_rect()
        self.bg_image.render(mydest)
        actions, leftover = self.camp.fight.cstat[self.pc].get_actions_and_move_percent()
        self._draw_clock(actions, leftover, frame_offset=16)
        actions, leftover = self.camp.fight.cstat[self.pc].get_modified_actions_and_move_percent(self.ap_to_spend, self.mp_to_spend)
        self._draw_clock(actions, leftover)


class PlayerTurn(object):
    # It's the player's turn. Allow the player to control this PC.
    def __init__(self, pc, camp):
        self.pc = pc
        self.camp = camp

    def end_turn(self, button, ev):
        self.camp.fight.cstat[self.pc].end_turn()

    def switch_movement(self, button=None, ev=None):
        if self.active_ui != self.movement_ui:
            self.active_ui.deactivate()
            self.movement_ui.activate()
            self.active_ui = self.movement_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_attack(self, button=None, ev=None):
        if self.active_ui != self.attack_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_attack_library():
                self.active_ui.deactivate()
                self.attack_ui.activate()
                self.active_ui = self.attack_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[1])
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_skill(self, button=None, ev=None):
        if self.active_ui != self.skill_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_skill_library(True):
                self.active_ui.deactivate()
                self.skill_ui.activate()
                self.active_ui = self.skill_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.get_button(self.switch_skill))
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_programs(self, button=None, ev=None):
        if self.active_ui != self.program_ui:
            if self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_program_library():
                self.active_ui.deactivate()
                self.program_ui.activate()
                self.active_ui = self.program_ui
                self.my_radio_buttons.activate_button(self.my_radio_buttons.get_button(self.switch_programs))
            else:
                # If the attack UI can't be activated, switch back to movement UI.
                self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_usables(self, button=None, ev=None):
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
                self.active_ui.set_top_shelf()
            elif hasattr(self.active_ui, "set_bottom_shelf"):
                self.active_ui.set_bottom_shelf()

    def switch_bottom_shelf(self):
        if self.active_ui in self.bottom_shelf_funs:
            self.bottom_shelf_funs[self.active_ui]()
            if hasattr(self.active_ui, "set_top_shelf"):
                self.active_ui.set_top_shelf()

    def focus_on_pc(self):
        pbge.my_state.view.focus(self.pc.pos[0], self.pc.pos[1])

    def quit_the_game(self):
        self.camp.fight.no_quit = False

    ACCEPTABLE_HOTKEYS = "abcdefghijklmnopqrstuvwxyz1234567890"

    def pop_menu(self):
        # Pop Pop PopMenu Pop Pop PopMenu
        mymenu = pbge.rpgmenu.PopUpMenu()
        mymenu.add_item("Center on {}".format(self.pc.get_pilot()), self.focus_on_pc)
        mymenu.add_item("Record hotkey for current action", self.gui_record_hotkey)
        mymenu.add_item("View hotkeys", self.gui_view_hotkeys)
        mymenu.add_item("Quit Game", self.quit_the_game)

        choice = mymenu.query()
        if choice:
            choice()

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
        option_string = self.name_current_option()

        pbge.util.config.set("HOTKEYS", mykey, option_string)
        pbge.BasicNotification("New hotkey set: {} = {}".format(mykey, option_string), count=200)
        # Export the new config options.
        current_use = pbge.my_state.key_is_in_use(mykey)
        if current_use:
            pbge.alert("Warning: Key {} is currently in use by \"{}\". It can't be used as a hotkey unless you change your key configuration.".format(mykey, current_use))

        with open(pbge.util.user_dir("config.cfg"), "wt") as f:
            pbge.util.config.write(f)

    def gui_record_hotkey(self):
        myevent = pbge.alert(
            "Press a letter or number key to record a new macro for {}. You could also do this by holding Alt + key.".format(
                self.name_current_option()))

        if myevent.type == pygame.KEYDOWN and myevent.unicode in self.ACCEPTABLE_HOTKEYS:
            self.record_hotkey(myevent.unicode)

    def gui_view_hotkeys(self):
        mymenu = pbge.rpgmenu.Menu(-250, -100, 500, 200, font=pbge.my_state.big_font)
        for op in pbge.util.config.options("HOTKEYS"):
            mymenu.add_item("{}: {}".format(op, pbge.util.config.get("HOTKEYS", op)), None)
        mymenu.add_item("[Exit]", None)
        mymenu.query()

    def _use_attack_menu(self, button, ev):
        mymenu = pbge.rpgmenu.PopUpMenu()
        for shelf in self.attack_ui.my_widget.library:
            mymenu.add_item(shelf.name, '/'.join([self.attack_ui.name, shelf.name, '0']))
        op = mymenu.query()
        if op:
            self.find_this_option(op)

    def _use_skills_menu(self, button, ev):
        mymenu = pbge.rpgmenu.PopUpMenu()
        for shelf in self.skill_ui.my_widget.library:
            mymenu.add_item(shelf.name, '/'.join([self.skill_ui.name, shelf.name, '0']))
        op = mymenu.query()
        if op:
            self.find_this_option(op)

    def _use_programs_menu(self, button, ev):
        mymenu = pbge.rpgmenu.PopUpMenu()
        for shelf in self.program_ui.my_widget.library:
            mymenu.add_item(shelf.name, '/'.join([self.program_ui.name, shelf.name, '0']))
        op = mymenu.query()
        if op:
            self.find_this_option(op)

    def _use_usables_menu(self, button, ev):
        mymenu = pbge.rpgmenu.PopUpMenu()
        for shelf in self.usable_ui.my_widget.library:
            mymenu.add_item(shelf.name, '/'.join([self.usable_ui.name, shelf.name, '0']))
        op = mymenu.query()
        if op:
            self.find_this_option(op)

    def go(self):
        # Perform this character's turn.
        # Start by creating the movement clock, since we're gonna be passing this widget to a bunch of our UIs.

        myclock = ActionClockWidget(self.pc, self.camp)
        pbge.my_state.widgets.append(myclock)

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

        self.movement_ui = movementui.MovementUI(self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
                                                 bottom_shelf_fun=self.switch_bottom_shelf, clock=myclock)
        self.all_uis.append(self.movement_ui)
        self.all_funs[self.movement_ui] = self.switch_movement

        self.attack_ui = targetingui.TargetingUI(self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
                                                 bottom_shelf_fun=self.switch_bottom_shelf, name="attacks", clock=myclock)
        self.all_uis.append(self.attack_ui)
        self.all_funs[self.attack_ui] = self.switch_attack

        has_skills = self.pc.get_skill_library(True)
        self.skill_ui = invoker.InvocationUI(self.camp, self.pc, self._get_skill_library,
                                             top_shelf_fun=self.switch_top_shelf, name="skills",
                                             bottom_shelf_fun=self.switch_bottom_shelf, clock=myclock)
        if has_skills:
            buttons_to_add.append(
                dict(on_frame=8, off_frame=9, on_click=self.switch_skill, tooltip='Skills',
                     on_right_click=self._use_skills_menu)
            )
            self.all_uis.append(self.skill_ui)
            self.all_funs[self.skill_ui] = self.switch_skill

        has_programs = self.pc.get_program_library()
        self.program_ui = programsui.ProgramsUI(self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
                                                bottom_shelf_fun=self.switch_bottom_shelf, name="programs", clock=myclock)
        if has_programs:
            buttons_to_add.append(
                dict(on_frame=10, off_frame=11, on_click=self.switch_programs, tooltip='Programs',
                     on_right_click=self._use_programs_menu)
            )
            self.all_uis.append(self.program_ui)
            self.all_funs[self.program_ui] = self.switch_programs

        has_usables = self.pc.get_usable_library()
        self.usable_ui = usableui.UsablesUI(self.camp, self.pc, top_shelf_fun=self.switch_top_shelf,
                                            bottom_shelf_fun=self.switch_bottom_shelf, name="usables", clock=myclock)
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
        pbge.my_state.widgets.append(self.my_radio_buttons)

        # Add the top_shelf and bottom_shelf functions
        self.top_shelf_funs = dict()
        self.bottom_shelf_funs = dict()
        for t in range(len(self.all_uis)):
            if t > 0:
                self.top_shelf_funs[self.all_uis[t]] = self.all_funs[self.all_uis[t - 1]]
            if t < (len(self.all_uis) - 1):
                self.bottom_shelf_funs[self.all_uis[t]] = self.all_funs[self.all_uis[t + 1]]

        self.active_ui = self.movement_ui

        # Right before starting the player's turn, if announce_pc_turn_start is turned on, announce it.
        if pbge.util.config.getboolean("GENERAL", "announce_pc_turn_start"):
            pbge.alert("{}'s Turn".format(self.pc.get_pilot()), font=pbge.BIGFONT, justify=0)

        keep_going = True
        while self.camp.fight.still_fighting() and (self.pc in self.camp.scene.contents) and self.camp.fight.cstat[
            self.pc].can_act():
            # Get input and process it.
            gdi = pbge.wait_event()

            self.active_ui.update(gdi, self)

            if gdi.type == pygame.KEYDOWN:
                if gdi.unicode in self.ACCEPTABLE_HOTKEYS and gdi.mod & pygame.KMOD_ALT:
                    # Record a hotkey.
                    self.record_hotkey(gdi.unicode)
                elif gdi.unicode in self.ACCEPTABLE_HOTKEYS and pbge.util.config.has_option("HOTKEYS", gdi.unicode) and not pbge.my_state.key_is_in_use(gdi.unicode):
                    self.find_this_option(pbge.util.config.get("HOTKEYS", gdi.unicode))
                elif pbge.my_state.is_key_for_action(gdi, "quit_game"):
                    keep_going = False
                    self.camp.fight.no_quit = False
                elif pbge.my_state.is_key_for_action(gdi, "center_on_pc"):
                    self.focus_on_pc()
                elif gdi.key == pygame.K_ESCAPE:
                    mymenu = configedit.PopupGameMenu()
                    mymenu(self.camp.fight)
                elif gdi.unicode == "," and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                    print("Checking...")
                    print(self.camp.fight.cstat[self.pc]._ap_remaining,self.camp.fight.cstat[self.pc].action_points, -self.camp.fight.cstat[self.pc]._mp_spent, self.camp.fight.cstat[self.pc].mp_remaining, self.camp.fight.cstat[self.pc].total_mp_remaining)
                elif gdi.unicode == "!" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                    myparty = self.camp.get_active_party()
                    myparty.remove(self.pc)
                    if myparty:
                        victim = random.choice(myparty)
                        pbge.alert("{} is immobilized!".format(victim))
                        for part in victim.get_all_parts():
                            if isinstance(part, gears.base.MovementSystem):
                                part.hp_damage += part.max_health
                            elif isinstance(part, gears.base.Module) and part.form is gears.base.MF_Leg:
                                part.hp_damage += part.max_health

            elif gdi.type == pygame.MOUSEBUTTONUP:
                if gdi.button == 3 and not pbge.my_state.widget_clicked:
                    self.pop_menu()

        pbge.my_state.widgets.remove(self.my_radio_buttons)
        pbge.my_state.view.overlays.clear()
        pbge.my_state.widgets.remove(myclock)

        for ui in self.all_uis:
            ui.dispose()

    def _get_skill_library(self):
        return self.pc.get_skill_library(True)


class Combat(object):
    def __init__(self, camp: gears.GearHeadCampaign):
        self.active = []
        self.scene: gears.GearHeadScene = camp.scene
        self.camp = camp
        self.ap_spent = collections.defaultdict(int)
        self.cstat = CombatDict()
        self.ai_brains = dict()
        self.no_quit = True
        self.n = 0

    def roll_initiative(self):
        # Sort based on initiative roll.
        self.active.sort(key=self._get_npc_initiative, reverse=True)

    def _get_npc_initiative(self, chara):
        return chara.get_stat(gears.stats.Speed) + random.randint(1, 20)

    def activate_foe(self, foe):
        # If the foe is already active, our work here is done.
        if foe in self.active:
            return

        foeteam = self.scene.local_teams.get(foe)
        team_frontier = [foeteam, self.scene.player_team]
        while team_frontier:
            myteam = team_frontier.pop()
            self.camp.check_trigger('ACTIVATETEAM', myteam)
            activation_area = set()
            # Add team members
            for m in self.scene.contents:
                if m not in self.active and self.scene.local_teams.get(m) is myteam and isinstance(m,
                                                                                                   gears.base.Combatant):
                    self.camp.check_trigger('ACTIVATE', m)
                    myview = scenes.pfov.PointOfView(self.scene, m.pos[0], m.pos[1], 5)
                    activation_area.update(myview.tiles)
                    if not hasattr(m, "combatant") or m.combatant:
                        self.active.append(m)
                    else:
                        pbge.my_state.view.anim_list.append(gears.geffects.SmokePoof(pos=m.pos))
                        m.pos = None

            # Check for further activations
            for m in self.scene.contents:
                if m not in self.active and m.pos in activation_area:
                    ateam = self.scene.local_teams.get(m)
                    if ateam and ateam not in team_frontier:
                        team_frontier.append(ateam)

        pbge.my_state.view.handle_anim_sequence()
        self.roll_initiative()

    def num_enemies(self):
        """Return the number of active, hostile characters."""
        n = 0
        for m in self.active:
            if m in self.scene.contents and self.scene.is_an_actor(
                    m) and m.is_operational() and self.scene.player_team.is_enemy(self.scene.local_teams.get(m)):
                n += 1
        return n

    def still_fighting(self):
        """Keep playing as long as there are enemies, players, and no quit."""
        return self.num_enemies() and self.camp.first_active_pc() and self.no_quit and self.camp.scene is self.scene and not pbge.my_state.got_quit and self.camp.keep_playing_scene() and self.camp.egg

    def step(self, chara, dest):
        """Move chara according to hmap, return True if movement ended."""
        # See if the movement starts in a threatened area- may be attacked if it ends
        # in a threatened area as well.
        # threat_area = self.get_threatened_area( chara )
        # started_in_threat = chara.pos in threat_area
        chara.move(dest, pbge.my_state.view, 0.25)
        pbge.my_state.view.handle_anim_sequence()
        self.cstat[chara].moves_this_round += 1

    def move_model_to(self, chara, nav, dest):
        # Move the model along the path. Handle attacks of opportunity and wotnot.
        # Return the tile where movement ends.
        is_player_model = chara in self.camp.party
        path = nav.get_path(dest)[1:]
        for p in path:
            self.step(chara, p)
            if is_player_model:
                self.scene.update_party_position(self.camp)

        # Spend the movement points.
        self.cstat[chara].spend_mp(nav.cost_to_tile[chara.pos])

        # Return the actual end point, which may be different from that requested.
        return chara.pos

    def get_action_nav(self, pc):
        # Return the navigation guide for this character taking into account that you can make
        # half a move while invoking an action.
        if hasattr(pc, 'get_current_speed'):
            return pbge.scenes.pathfinding.NavigationGuide(
                self.camp.scene, pc.pos, self.cstat[pc].total_mp_remaining - pc.get_current_speed() // 2, pc.mmode,
                self.camp.scene.get_blocked_tiles()
            )

    def can_move_and_invoke(self, chara, nav, invo, target_pos):
        if hasattr(invo.area, 'MOVE_AND_FIRE') and not invo.area.MOVE_AND_FIRE:
            return False
        else:
            firing_points = invo.area.get_firing_points(self.camp, target_pos)
            if nav:
                return firing_points.intersection(list(nav.cost_to_tile.keys()))
            else:
                return {chara.pos}.intersection(firing_points)

    def move_and_invoke(self, pc, nav, invo, target_list, firing_points, record=False):
        fp = min(firing_points, key=lambda r: nav.cost_to_tile.get(r, 10000))
        self.move_model_to(pc, nav, fp)
        if pc.pos == fp:
            pbge.my_state.view.overlays.clear()
            # Launch the effect.
            invo.invoke(self.camp, pc, target_list, pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence(record)
            self.cstat[pc].spend_ap(1)

        else:
            self.cstat[pc].spend_ap(1)

    def do_combat_turn(self, chara):
        if not self.cstat[chara].has_started_turn:
            self.cstat[chara].start_turn(chara)
            if hasattr(chara, 'ench_list'):
                chara.ench_list.update(self.camp, chara)
                alt_ais = chara.ench_list.get_tags('ALT_AI')
                if alt_ais:
                    current_ai = random.choice(alt_ais)
                    if current_ai in ALT_AIS:
                        ALT_AIS[current_ai](chara, self.camp)
        if chara in self.camp.party and chara.is_operational() and not (isinstance(chara, gears.base.Monster) and not pbge.util.config.getboolean("DIFFICULTY", "directly_control_pets")):
            # Outsource the turn-taking.
            my_turn = PlayerTurn(chara, self.camp)
            my_turn.go()
        elif chara.is_operational():
            if chara not in self.ai_brains:
                chara_ai = aibrain.BasicAI(chara)
                self.ai_brains[chara] = chara_ai
            else:
                chara_ai = self.ai_brains[chara]
            chara_ai.act(self.camp)

    def end_round(self):
        for chara in self.active:
            self.cstat[chara].end_turn()
            self.cstat[chara].has_started_turn = False

    def _try_to_fix_mkill(self, party, mkpc: gears.base.Mecha):
        total = 0
        if mkpc.material is gears.materials.Biotech:
            used_skill = gears.stats.Biotechnology
        else:
            used_skill = gears.stats.Repair
        for pc in party:
            if pc.get_current_mental() > 0:
                pc.spend_mental(random.randint(1,4)+random.randint(1,4))
                total += max(pc.get_skill_score(gears.stats.Craft, used_skill), random.randint(1, 5))
        my_invo = pbge.effects.Invocation(
            name = 'Repair',
            fx=gears.geffects.DoHealing(
                1, max(total,5), repair_type=mkpc.material.repair_type,
                anim = gears.geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(),
            targets=1)
        my_invo.invoke(self.camp, None, [mkpc.pos], pbge.my_state.view.anim_list)
        pbge.my_state.view.handle_anim_sequence()

        mkpc.gear_up(self.scene)
        if mkpc.get_current_speed() > 0:
            pbge.alert("The repairs are successful; {} is able to move again.".format(mkpc.get_pilot()))
        else:
            pbge.alert("The repairs failed. You are forced to leave {} behind.".format(mkpc.get_pilot()))
            self.scene.contents.remove(mkpc)

    def _abandon_mkill(self, party, mkpc: gears.base.Mecha):
        pbge.alert("You leave {} behind.".format(mkpc.get_pilot()))
        self.scene.contents.remove(mkpc)

    def go(self, explo):
        """Perform this combat."""
        pbge.my_state.view.overlays.clear()
        if self.scene.combat_music:
            pbge.my_state.start_music(self.scene.combat_music)

        while self.still_fighting():
            if self.n >= len(self.active):
                # It's the end of the round.
                self.n = 0
                explo.update_npcs()
                self.end_round()
                self.camp.check_trigger("COMBATROUND")
            if self.active[self.n] in self.camp.scene.contents and self.active[self.n].is_operational():
                chara = self.active[self.n]
                self.do_combat_turn(chara)
                # After action, renew attacks of opportunity
                self.cstat[chara].aoo_readied = True
                self.cstat[chara].attacks_this_round = 0
                chara.renew_power()
            if self.no_quit and not pbge.my_state.got_quit:
                # Only advance to the next character if we are not quitting. If we are quitting,
                # the game will be saved and the player will probably want any APs they have left.
                self.n += 1
            self.camp.check_trigger("COMBATLOOP")

        if self.no_quit and not pbge.my_state.got_quit:
            # Combat is over. Deal with things.
            # explo.check_trigger( "COMBATOVER" )
            # if self.camp.num_pcs() > 0:
            #    # Combat has ended because we ran out of enemies. Dole experience.
            #    self.give_xp_and_treasure( explo )
            #    # Provide some end-of-combat first aid.
            #    #self.do_first_aid(explo)
            #    self.recover_fainted(explo)
            treasure = pbge.container.ContainerList()
            for m in self.active:
                if m in self.scene.contents and self.scene.is_an_actor(m):
                    if not m.is_operational():
                        self.camp.check_trigger("FAINT", m)
                        n = m.get_pilot()
                        if n and m is not n and not n.is_operational():
                            self.camp.check_trigger("FAINT", n)
                        mteam = self.scene.local_teams.get(m)
                        if mteam and self.scene.player_team.is_enemy(mteam) and hasattr(m, "treasure_type") and m.treasure_type:
                            maybe_treasure = m.treasure_type.generate_treasure(self.camp, m, gears.selector.get_design_by_full_name)
                            if maybe_treasure:
                                treasure.append(maybe_treasure)

            # Deal with m-kills now; if someone is immobilized and can't be repaired, they get left behind.
            # I am well aware this might mean the entire party gets taken out of combat.
            myparty = self.camp.get_active_party()
            for pc in myparty:
                pc.hidden = False
                if isinstance(pc, gears.base.Mecha) and (pc.get_current_speed() < 10 or not self.scene.can_use_movemode_here(pc.mmode, *pc.pos)):
                    pc.gear_up(self.scene)
                    if pc.get_current_speed() < 10:
                        # Looks like we have a genuine Mobility Kill.
                        if pc.get_pilot() is self.camp.pc:
                            mymenu = pbge.rpgmenu.AlertMenu("Your {} has been immobilized. You can either try to repair the damage, or let the mission continue without you.".format(pc.get_full_name()))
                        else:
                            mymenu = ghcutscene.SimpleMonologueMenu("[I_HAVE_BEEN_IMMOBILIZED] [HELP_WITH_MOBILITY_KILL]", pc, self.camp)
                        if any([m.get_current_mental() > 0 for m in myparty]):
                            mymenu.add_item("Attempt to repair the damage.", self._try_to_fix_mkill)
                        mymenu.add_item("Leave {} behind.".format(pc), self._abandon_mkill)
                        choice = mymenu.query()
                        if choice:
                            choice(myparty, pc)
                        else:
                            self._abandon_mkill(myparty, pc)

            if myparty and treasure:
                pbge.alert("You acquired some valuables from the battle.")
                fieldhq.backpack.ItemExchangeWidget.create_and_invoke(self.camp, self.camp.first_active_pc(), treasure)

            self.scene.tidy_enchantments(gears.enchantments.END_COMBAT)

    def __setstate__(self, state):
        # For saves from V0.905 or earlier, make sure the CombatDict is used.
        mydict = state.get("cstat")
        if not isinstance(mydict, CombatDict):
            state["cstat"] = CombatDict.from_dict(mydict)
        self.__dict__.update(state)
