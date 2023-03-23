import pbge
from pbge import util
import pygame
import configparser

default_config = configparser.ConfigParser()

CONFIG_EDITOR_WIDTH = 500

class OptionToggler(object):
    def __init__(self, key, section="GENERAL", extra_fun=None):
        self.key = key
        self.section = section
        self.extra_fun = extra_fun

    def __call__(self, new_value):
        util.config.set(self.section, self.key, str(new_value))
        if self.extra_fun:
            self.extra_fun()

    @classmethod
    def add_menu_toggle(cls, my_scroll_column: pbge.widgets.ScrollColumnWidget, name, key, section="GENERAL", extra_fun=None):
        try:
            current_val = util.config.getboolean(section, key)
        except ValueError:
            try:
                current_val = default_config.getboolean(section, key)
                util.config.set(section, key, str(current_val))
            except configparser.NoOptionError:
                util.config.remove_option(section, key)
                return

        my_scroll_column.add_interior(
            pbge.widgets.CheckboxWidget(CONFIG_EDITOR_WIDTH, name, current_val, cls(key, section, extra_fun=extra_fun))
        )


class ConfigEditor(object):
    def __init__(self, predraw, dy=-125):
        self.dy = dy
        self.predraw = predraw
        self.finished = False

    def toggle_fullscreen(self):
        # Actually toggle the fullscreen.
        pbge.my_state.reset_screen()

    def toggle_stretchyscreen(self):
        # Actually toggle the fullscreen.
        pbge.my_state.reset_screen()

    def set_window_size(self, result):
        if result:
            util.config.set("GENERAL", "window_size", result)
            pbge.my_state.reset_screen()

    def set_music_volume(self, result):
        if result:
            util.config.set("GENERAL", "music_volume", result)
            pbge.my_state.set_music_volume(float(result))

    def set_sound_volume(self, result):
        if result:
            util.config.set("GENERAL", "sound_volume", result)

    def toggle_music(self):
        # Actually turn off or on the music.
        if util.config.getboolean("GENERAL", "music_on"):
            pbge.my_state.resume_music()
        else:
            pbge.my_state.stop_music()

    def _preload_music(self):
        if util.config.getboolean("GENERAL", "preload_all_music") and not pbge.soundlib.CACHED_MUSIC:
            #current_music = pbge.my_state.music_name
            pbge.my_state.stop_music()
            pbge.please_stand_by()
            pbge.soundlib.preload_all_music()
            if util.config.getboolean("GENERAL", "music_on"):
                #pbge.my_state.start_music(current_music)
                pbge.my_state.resume_music()

    def set_music_mode(self, result):
        if result:
            util.config.set("GENERAL", "music_mode", result)
            if result == pbge.MUSIC_MODE_PRELOAD:
                self._preload_music()
            elif util.config.getboolean("GENERAL", "music_on"):
                #current_music = pbge.my_state.music_name
                pbge.my_state.stop_music()
                #pbge.my_state.start_music(current_music)
                pbge.my_state.resume_music()

    def save_and_quit(self, *args):
        self.finished = True

    WINDOW_SIZES = (
        "800x600", "1280x720", "1600x900", "1600x1200", "1920x1080", "2560x1440"
    )
    VOLUME_LEVELS = (
        ("100%", "1.0"), ("90%", "0.9"), ("80%", "0.8"), ("70%", "0.7"), ("60%", "0.6"),
        ("50%", "0.5"), ("40%", "0.4"), ("30%", "0.3"), ("20%", "0.2"), ("10%", "0.1")
    )

    def __call__(self):
        action = True
        pos = 0

        self.column = pbge.widgets.ColumnWidget(
            -CONFIG_EDITOR_WIDTH//2, self.dy, CONFIG_EDITOR_WIDTH, 250, draw_border=True
        )
        up_arrow = pbge.widgets.ButtonWidget(0, 0, 128, 16,
                                             sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                             on_frame=0, off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0, 0, 128, 16,
                                               sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                               on_frame=2, off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(
            0, 0, CONFIG_EDITOR_WIDTH, 200 - 40, up_arrow, down_arrow, padding=5, focus_locked=True
        )
        self.column.add_interior(up_arrow)
        self.column.add_interior(self.scroll_column)
        self.column.add_interior(down_arrow)

        self.scroll_column.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"General Options", font=pbge.BIGFONT))

        OptionToggler.add_menu_toggle(self.scroll_column, "Fullscreen", "fullscreen", extra_fun=self.toggle_fullscreen)
        OptionToggler.add_menu_toggle(self.scroll_column, "Stretch Screen", "stretchy_screen", extra_fun=self.toggle_stretchyscreen)
        OptionToggler.add_menu_toggle(self.scroll_column, "Music On", "music_on", extra_fun=self.toggle_music)
        volume_menu = pbge.widgets.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Music Volume", on_select=self.set_music_volume
        )
        for msg,val in self.VOLUME_LEVELS:
            volume_menu.add_item(msg, val)
        volume_menu.my_menu_widget.menu.set_item_by_value(util.config.get("GENERAL", "music_volume"))
        self.scroll_column.add_interior(volume_menu)
        music_mode_menu = pbge.widgets.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Music Mode", on_select=self.set_music_mode, add_desc=True
        )
        music_mode_menu.add_item(pbge.MUSIC_MODE_PRELOAD, pbge.MUSIC_MODE_PRELOAD, "Preload all music files. This option takes the most memory and increases load time, but provides flawless playback.")
        music_mode_menu.add_item(pbge.MUSIC_MODE_CACHED, pbge.MUSIC_MODE_CACHED, "Cache the most recently used music files. This option uses a medium amount of memory, but reduces interruptions when new music is loaded.")
        music_mode_menu.add_item(pbge.MUSIC_MODE_STREAM, pbge.MUSIC_MODE_STREAM, "Stream music directly from disk. This option uses the least amount of memory, but causes a slight delay when the music stream is changed.")
        music_mode_menu.my_menu_widget.menu.set_item_by_value(util.config.get("GENERAL", "music_mode"))
        self.scroll_column.add_interior(music_mode_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Sound FX On", "sound_on")
        volume_menu = pbge.widgets.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Sound FX Volume", on_select=self.set_sound_volume
        )
        for msg,val in self.VOLUME_LEVELS:
            volume_menu.add_item(msg, val)
        volume_menu.my_menu_widget.menu.set_item_by_value(util.config.get("GENERAL", "sound_volume"))
        self.scroll_column.add_interior(volume_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Names Above Heads", "names_above_heads")
        OptionToggler.add_menu_toggle(self.scroll_column, "Auto Save on Scene Change", "auto_save")
        OptionToggler.add_menu_toggle(self.scroll_column, "Can Replay Adventures", "can_replay_adventures")
        OptionToggler.add_menu_toggle(self.scroll_column, "No Escape From Main Menu", "no_escape_from_title_screen")
        window_menu = pbge.widgets.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Window Size", on_select=self.set_window_size
        )
        for res in self.WINDOW_SIZES:
            window_menu.add_item(res, res)
        window_menu.my_menu_widget.menu.set_item_by_value(util.config.get("GENERAL", "window_size"))
        self.scroll_column.add_interior(window_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Lancemates repaint their mecha", "lancemates_repaint_mecha")
        OptionToggler.add_menu_toggle(self.scroll_column, "Announce start of player turns", "announce_pc_turn_start")
        OptionToggler.add_menu_toggle(self.scroll_column, "Scroll to start of action library", "scroll_to_start_of_action_library")
        OptionToggler.add_menu_toggle(self.scroll_column, "Auto-center map cursor", "auto_center_map_cursor")
        OptionToggler.add_menu_toggle(self.scroll_column, "Mouse scroll at map edges", "mouse_scroll_at_map_edges")
        OptionToggler.add_menu_toggle(self.scroll_column, "Show numbers in pilot info", "show_numbers_in_pilot_info")
        OptionToggler.add_menu_toggle(self.scroll_column, "Dock tile info panel", "dock_tile_info_panel")

        self.scroll_column.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"\nDifficulty Options", font=pbge.BIGFONT))
        for op in util.config.options("DIFFICULTY"):
            OptionToggler.add_menu_toggle(self.scroll_column, op, op, section="DIFFICULTY")

        self.scroll_column.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"Save and Exit", on_click=self.save_and_quit))

        pbge.my_state.widgets.append(self.column)
        keepgoing = True
        while keepgoing and not self.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                if self.predraw:
                    self.predraw()
                else:
                    pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if pbge.my_state.is_key_for_action(ev, "exit"):
                    keepgoing = False

        pbge.my_state.widgets.remove(self.column)

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
        my_menu = pbge.rpgmenu.Menu(-150, -100, 300, 200,
                                   font=pbge.my_state.huge_font)
        my_menu.add_item("Quit Game", self.do_quit)
        my_menu.add_item("Config Options", self.do_config)
        my_menu.add_item("Continue", False)
        action = True
        while action and enc_or_com.no_quit:
            action = my_menu.query()
            if action:
                action(enc_or_com)


def init_configedit():
    global default_config
    with open(util.data_dir("config_defaults.cfg")) as f:
        default_config.read_file( f )
