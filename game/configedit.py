import pbge
from pbge import util
import pygame
import configparser

default_config = configparser.ConfigParser()

class OptionToggler(object):
    def __init__(self, key, section="GENERAL", extra_fun=None):
        self.key = key
        self.section = section
        self.extra_fun = extra_fun

    def __call__(self):
        mystate = not util.config.getboolean(self.section, self.key)
        util.config.set(self.section, self.key, str(mystate))
        if self.extra_fun:
            self.extra_fun()

    @classmethod
    def add_menu_toggle(cls, mymenu, name, key, section="GENERAL", extra_fun=None):
        try:
            current_val = util.config.getboolean(section, key)
        except ValueError:
            try:
                current_val = default_config.getboolean(section, key)
                util.config.set(section, key, str(current_val))
            except configparser.NoOptionError:
                util.config.remove_option(section, key)
                return

        mymenu.add_item(
            "{}: {}".format(name, current_val),
            cls(key, section, extra_fun=extra_fun))


class ConfigEditor(object):
    def __init__(self, predraw, dy=-100):
        self.dy = dy
        self.predraw = predraw

    def toggle_fullscreen(self):
        # Actually toggle the fullscreen.
        pbge.my_state.reset_screen()

    def toggle_stretchyscreen(self):
        # Actually toggle the fullscreen.
        pbge.my_state.reset_screen()

    def toggle_music(self):
        # Actually turn off or on the music.
        if util.config.getboolean("GENERAL", "music_on"):
            pbge.my_state.resume_music()
        else:
            pbge.my_state.stop_music()

    def __call__(self):
        action = True
        pos = 0
        while action:
            # rebuild the menu.
            mymenu = pbge.rpgmenu.Menu(-250, self.dy, 500, 200,
                                       predraw=self.predraw, font=pbge.my_state.big_font)
            OptionToggler.add_menu_toggle(mymenu, "Fullscreen", "fullscreen", extra_fun=self.toggle_fullscreen)
            OptionToggler.add_menu_toggle(mymenu, "Stretch Screen", "stretchy_screen", extra_fun=self.toggle_stretchyscreen)
            OptionToggler.add_menu_toggle(mymenu, "Music On", "music_on", extra_fun=self.toggle_music)
            OptionToggler.add_menu_toggle(mymenu, "Names Above Heads", "names_above_heads")
            OptionToggler.add_menu_toggle(mymenu, "Auto Save on Scene Change", "auto_save")
            OptionToggler.add_menu_toggle(mymenu, "Can Replay Adventures", "can_replay_adventures")
            OptionToggler.add_menu_toggle(mymenu, "No Escape From Main Menu", "no_escape_from_title_screen")

            OptionToggler.add_menu_toggle(mymenu, "Lancemates repaint their mecha", "lancemates_repaint_mecha")
            OptionToggler.add_menu_toggle(mymenu, "Announce start of player turns", "announce_pc_turn_start")
            OptionToggler.add_menu_toggle(mymenu, "Scroll to start of action library", "scroll_to_start_of_action_library")
            OptionToggler.add_menu_toggle(mymenu, "Auto-center map cursor", "auto_center_map_cursor")
            OptionToggler.add_menu_toggle(mymenu, "Mouse scroll at map edges", "mouse_scroll_at_map_edges")

            for op in util.config.options("DIFFICULTY"):
                OptionToggler.add_menu_toggle(mymenu, op, op, section="DIFFICULTY")

            mymenu.add_item("Save and Exit", False)
            mymenu.set_item_by_position(pos)
            action = mymenu.query()
            if action and action is not True:
                pos = mymenu.selected_item
                action()

        # Export the new config options.
        with open(util.user_dir("config.cfg"), "wt") as f:
            util.config.write(f)


class PopupGameMenu(object):
    def do_quit(self, enc_or_com):
        enc_or_com.no_quit = False

    def do_config(self, enc_or_com):
        myconfigmenu = ConfigEditor(None)
        myconfigmenu()

    def __call__(self, enc_or_com):
        mymenu = pbge.rpgmenu.Menu(-150, -100, 300, 200,
                                   font=pbge.my_state.huge_font)
        mymenu.add_item("Quit Game", self.do_quit)
        mymenu.add_item("Config Options", self.do_config)
        mymenu.add_item("Continue", False)
        action = True
        while action and enc_or_com.no_quit:
            action = mymenu.query()
            if action:
                action(enc_or_com)


def init_configedit():
    global default_config
    with open(util.data_dir("config_defaults.cfg")) as f:
        default_config.read_file( f )
