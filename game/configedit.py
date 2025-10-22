import pbge
from pbge import util
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
                _=util.config.remove_option(section, key)
                return

        my_scroll_column.add_interior(
            pbge.widgets.CheckboxWidget(CONFIG_EDITOR_WIDTH, name, current_val, cls(key, section, extra_fun=extra_fun))
        )


class ConfigEditor(pbge.widgetmenu.MenuWidget):
    TAGS_TO_HIDE = {pbge.widgets.WTAG_TITLEMENU,}
    TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_WIDGET,}
    ACTIVATE_IMMEDIATELY = True

    def __init__(self, dy=-125):
        super().__init__(
            -CONFIG_EDITOR_WIDTH//2, dy, CONFIG_EDITOR_WIDTH, 250, draw_border=True,
            on_escape=self.save_and_quit
        )

        self.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"General Options", font=pbge.BIGFONT))

        OptionToggler.add_menu_toggle(self.scroll_column, "Fullscreen", "fullscreen", extra_fun=self.toggle_fullscreen)
        OptionToggler.add_menu_toggle(self.scroll_column, "Stretch Screen", "stretchy_screen", extra_fun=self.toggle_stretchyscreen, section="ACCESSIBILITY")
        OptionToggler.add_menu_toggle(self.scroll_column, "Music On", "music_on", extra_fun=self.toggle_music)
        volume_menu = pbge.widgetmenu.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Music Volume", on_select=self.set_music_volume
        )
        for msg,val in self.VOLUME_LEVELS:
            volume_menu.add_item(msg, None, data=val)
        volume_menu.set_item_by_data(util.config.get("GENERAL", "music_volume"))
        self.add_interior(volume_menu)
        music_mode_menu = pbge.widgetmenu.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Music Mode", on_select=self.set_music_mode, add_desc=True
        )
        music_mode_menu.add_item(pbge.MUSIC_MODE_PRELOAD, None, data=pbge.MUSIC_MODE_PRELOAD, desc="Preload all music files. This option takes the most memory and increases load time, but provides flawless playback.")
        music_mode_menu.add_item(pbge.MUSIC_MODE_CACHED, None, data=pbge.MUSIC_MODE_CACHED, desc="Cache the most recently used music files. This option uses a medium amount of memory, but reduces interruptions when new music is loaded.")
        music_mode_menu.add_item(pbge.MUSIC_MODE_STREAM, None, data=pbge.MUSIC_MODE_STREAM, desc="Stream music directly from disk. This option uses the least amount of memory, but causes a slight delay when the music stream is changed.")
        music_mode_menu.set_item_by_data(util.config.get("GENERAL", "music_mode"))
        self.add_interior(music_mode_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Sound FX On", "sound_on")
        volume_menu = pbge.widgetmenu.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Sound FX Volume", on_select=self.set_sound_volume
        )
        for msg,val in self.VOLUME_LEVELS:
            volume_menu.add_item(msg, data=val)
        volume_menu.set_item_by_data(util.config.get("GENERAL", "sound_volume"))
        self.add_interior(volume_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Names Above Heads", "names_above_heads")
        OptionToggler.add_menu_toggle(self.scroll_column, "Auto Save on Scene Change", "auto_save")
        OptionToggler.add_menu_toggle(self.scroll_column, "Can Replay Adventures", "can_replay_adventures")
        OptionToggler.add_menu_toggle(self.scroll_column, "No Escape From Main Menu", "no_escape_from_title_screen")
        window_menu = pbge.widgetmenu.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Window Size", on_select=self.set_window_size
        )
        for res in self.WINDOW_SIZES:
            window_menu.add_item(res, data=res)
        window_menu.set_item_by_data(util.config.get("GENERAL", "window_size"))
        self.add_interior(window_menu)

        resolution_menu = pbge.widgetmenu.ColDropdownWidget(
            CONFIG_EDITOR_WIDTH, "Fullscreen Resolution", on_select=self.set_resolution
        )
        for res in self.RESOLUTIONS:
            resolution_menu.add_item(res, data=res)
        myres = util.config.get("GENERAL", "fullscreen_resolution")
        if myres not in self.RESOLUTIONS:
            resolution_menu.add_item(myres, data=myres)
        resolution_menu.set_item_by_data(myres)
        self.add_interior(resolution_menu)

        OptionToggler.add_menu_toggle(self.scroll_column, "Lancemates repaint their mecha", "lancemates_repaint_mecha")
        OptionToggler.add_menu_toggle(self.scroll_column, "Announce start of player turns", "announce_pc_turn_start")
        OptionToggler.add_menu_toggle(self.scroll_column, "Scroll to start of action library", "scroll_to_start_of_action_library")
        OptionToggler.add_menu_toggle(self.scroll_column, "Auto-center map cursor", "auto_center_map_cursor")
        OptionToggler.add_menu_toggle(self.scroll_column, "Mouse scroll at map edges", "mouse_scroll_at_map_edges")
        OptionToggler.add_menu_toggle(self.scroll_column, "Show numbers in pilot info", "show_numbers_in_pilot_info")
        OptionToggler.add_menu_toggle(self.scroll_column, "Dock tile info panel", "dock_tile_info_panel")
        OptionToggler.add_menu_toggle(self.scroll_column, "Show skills used in dialogue", "show_convo_skills")
        OptionToggler.add_menu_toggle(self.scroll_column, "Indicate lance members on map", "indicate_lance_tiles")

        self.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"\nDifficulty Options", font=pbge.BIGFONT))
        for op in util.config.options("DIFFICULTY"):
            OptionToggler.add_menu_toggle(self.scroll_column, op, op, section="DIFFICULTY")

        self.add_interior(pbge.widgets.LabelWidget(0,0,CONFIG_EDITOR_WIDTH,0,"Save and Exit", on_click=self.save_and_quit))

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

    def set_resolution(self, result):
        if result:
            util.config.set("GENERAL", "fullscreen_resolution", result)
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

    def save_and_quit(self, *_args):
        # Export the new config options.
        with open(util.user_dir("config.cfg"), "wt") as f:
            util.config.write(f)
        self.pop()

    WINDOW_SIZES = (
        "800x600", "1280x720", "1600x900", "1600x1200", "1920x1080", "2560x1440"
    )
    RESOLUTIONS = (
        "auto", "800x600", "1280x720", "1366x768", "1440x900", "1536x864", "1600x900", "1600x1200", "1920x1080", "2560x1440"
    )
    VOLUME_LEVELS = (
        ("100%", "1.0"), ("90%", "0.9"), ("80%", "0.8"), ("70%", "0.7"), ("60%", "0.6"),
        ("50%", "0.5"), ("40%", "0.4"), ("30%", "0.3"), ("20%", "0.2"), ("10%", "0.1")
    )


class PopupGameMenu(pbge.widgetmenu.MenuWidget):
    TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_WIDGET,}
    ACTIVATE_IMMEDIATELY = True

    def __init__(self):
        super().__init__(
            -150, -100, 300, 200, font=pbge.my_state.huge_font,
            on_escape=self.exit_menu
        )
        _=self.add_item("Quit Game", self.do_quit)
        _=self.add_item("Config Options", self.do_config)
        _=self.add_item("Continue", self.exit_menu)

    def do_quit(self, _wid, _ev):
        pbge.my_state.session_data[pbge.campaign.SDAT_GOT_QUIT] = True
        self.pop()

    def do_config(self, wid, _ev):
        self.pop()
        ConfigEditor.push_state_and_instantiate()

    def exit_menu(self, _wid, _ev):
        self.pop()


def init_configedit():
    global default_config
    with open(util.data_dir("config_defaults.cfg")) as f:
        default_config.read_file( f )
