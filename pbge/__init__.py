# Polar Bear Game Engine

# This package contains some low-level graphics stuff needed to
# create an isometric RPG style rules in Python. The idea is to
# isolate the graphics handling from the code as much as possible,
# so that if PyGame is replaced the interface shouldn't change
# too much. Also, so that creating a new rules should be as simple
# as importing this package.

# Word wrapper taken from the PyGame wiki plus
# the list-printer from Anne Archibald's GearHead Prime demo.

import sdl2
from sdl2 import ext, sdlmixer, sdlimage
from itertools import chain
from . import util, clock
import glob
import random
import weakref
#import sys
#import os

#from steam.client import SteamClient
#myclient = SteamClient()

from . import soundlib

MUSIC_MODE_STREAM = "Stream"
MUSIC_MODE_CACHED = "Cached"
MUSIC_MODE_PRELOAD = "Preload"


class KeyObject(object):
    """A catcher for multiple inheritence. Subclass this instead of object if
       you're going to use multiple inheritence, so that erroneous keywords
       will get caught and identified."""

    def __init__(self, **keywords):
        for k, i in keywords.items():
            print("WARNING: KeyObject got parameters {}={}".format(k, i))


class SingletonMeta(type):
    def __str__(cls):
        return cls.name


class Singleton(object, metaclass=SingletonMeta):
    """For rules constants that don't need to be instanced."""
    name = "Singleton"

    def __init__(self):
        raise NotImplementedError("Singleton can't be instantiated.")


class Border(object):
    def __init__(self, border_width=16, tex_width=32, border_name="", tex_name="", padding=16, tl=0, tr=0, bl=0, br=0,
                 t=1, b=1, l=2, r=2, transparent=True):
        # tl,tr,bl,br are the top left, top right, bottom left, and bottom right frames
        # Bug: The border must be exactly half as wide as the texture.
        self.border_width = border_width
        self.tex_width = tex_width
        self.border_name = border_name
        self.tex_name = tex_name
        self.border = None
        self.tex = None
        self.padding = padding
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br
        self.t = t
        self.b = b
        self.l = l
        self.r = r
        self.transparent = transparent

    def render(self, dest):
        """Draw this decorative border at dest on screen."""
        # We're gonna draw a decorative border to surround the provided area.
        if self.border == None:
            self.border = image.Image(self.border_name, self.border_width, self.border_width)
        if self.tex_name and not self.tex:
            self.tex = image.Image(self.tex_name, self.tex_width, self.tex_width)
            if self.transparent:
                self.tex.set_alpha(224)

        # Draw the backdrop.
        if self.tex:
            self.tex.tile(dest.inflate(self.padding, self.padding))

        # Expand the dimensions to their complete size.
        # The method inflate_ip doesn't seem to be working... :(
        fdest = dest.inflate(self.padding, self.padding)

        self.border.render((fdest.x - self.border_width // 2, fdest.y - self.border_width // 2), self.tl)
        self.border.render((fdest.x - self.border_width // 2, fdest.y + fdest.height - self.border_width // 2), self.bl)
        self.border.render((fdest.x + fdest.width - self.border_width // 2, fdest.y - self.border_width // 2), self.tr)
        self.border.render(
            (fdest.x + fdest.width - self.border_width // 2, fdest.y + fdest.height - self.border_width // 2), self.br)

        fdest = dest.inflate(self.padding - self.border_width, self.padding + self.border_width)
        sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, fdest)
        for x in range(0, fdest.w // self.border_width + 2):
            self.border.render((fdest.x + x * self.border_width, fdest.y), self.t)
            self.border.render((fdest.x + x * self.border_width, fdest.y + fdest.height - self.border_width), self.b)

        fdest = dest.inflate(self.padding + self.border_width, self.padding - self.border_width)
        sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, fdest)
        for y in range(0, fdest.h // self.border_width + 2):
            self.border.render((fdest.x, fdest.y + y * self.border_width), self.l)
            self.border.render((fdest.x + fdest.width - self.border_width, fdest.y + y * self.border_width), self.r)
        sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, None)


# Monkey Type these definitions to fit your game/assets.
default_border = Border(border_width=8, tex_width=16, border_name="sys_defborder.png", tex_name="sys_defbackground.png",
                        tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2)
notex_border = Border(border_width=8, border_name="sys_defborder.png", padding=4, tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2,
                      r=2)
# map_border = Border( border_name="sys_mapborder.png", tex_name="sys_maptexture.png", tl=0, tr=1, bl=2, br=3, t=4, b=6, l=7, r=5 )
# gold_border = Border( border_width=8, tex_width=16, border_name="sys_rixsborder.png", tex_name="sys_rixstexture.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2 )

TEXT_COLOR = (240, 240, 50)
WHITE = (255, 255, 255)
GREY = (160, 160, 160)
BLACK = (0, 0, 0)

INFO_GREEN = (50, 200, 0)
INFO_HILIGHT = (100, 250, 0)
ENEMY_RED = (250, 50, 0)



class GameState(object):
    def __init__(self):
        self.title = "PBGE Game"
        self.screen: ext.renderer.Renderer = None   # pyright: ignore[reportAttributeAccessIssue]
        self.window: ext.Window = None              # pyright: ignore[reportAttributeAccessIssue]
        self.target_texture: sdl2.SDL_Texture = None
        self.view = None
        self.got_quit = False
        self.widgets = list()
        self._widgets_active = True
        self._focused_widget = None
        self.widget_responded = False
        self.audio_enabled = True
        #self.music = None
        self.music_name = ""
        self.anim_phase = 0
        self.standing_by = False
        self.notifications = list()

        self.music_channels = list()
        self.current_music_channel = 0

        self.stretchy_layers = weakref.WeakSet()

        self.mouse_pos = (0, 0)

        self.message_log = list()

        self.ui_stack = list()
        self.widget_tooltip = None

        self.session_data = dict()
        # See alerts.py for a more thorough description of alerts. Basically,
        # a queue of display widgets that get cycled through automatically.
        self.alert_queue = list()

        # Instead of getting deployed immediately, widgets get stored here.
        self.deployment_queue = list()

        # The following stack is used by the check_trigger function in campaign
        self.trigger_tripped_stack = list()
        self.trigger_queue = list()

        # self.client = SteamClient()

    def render_notifications(self):
        if self.notifications:
            self.notifications[0].render()
            if self.notifications[0].is_done():
                del self.notifications[0]

    def locate_music(self, mfname):
        if mfname and util.config.get("GENERAL", "music_mode").casefold() != MUSIC_MODE_STREAM.casefold():
            sound = soundlib.load_cached_sound(mfname)
            return sound

    def _start_cached_music(self, mfname, yafi=False):
        if ((yafi or (mfname and mfname != self.music_name and
                      util.config.getboolean("GENERAL", "music_on"))) and self.audio_enabled and
                not util.config.getboolean("TROUBLESHOOTING", "disable_audio_entirely")):
            sound = self.locate_music(mfname)
            if sound:
                if self.music_channels[self.current_music_channel].get_busy():
                    self.music_channels[self.current_music_channel].fadeout(2000)
                    self.current_music_channel = 1 - self.current_music_channel
                self.music_channels[self.current_music_channel].play(sound, loops=-1, fade_ms=2000)
                self.set_music_volume(util.config.getfloat("GENERAL", "music_volume"))
                #sound.set_volume(util.config.getfloat("GENERAL", "music_volume"))
                #self.music_channels[self.current_music_channel].set_volume(util.config.getfloat("GENERAL", "music_volume"))

    def _start_streaming_music(self, mfname, yafi):
        if ((yafi or (mfname and mfname != self.music_name and
                      util.config.getboolean("GENERAL", "music_on"))) and self.audio_enabled and
                not util.config.getboolean("TROUBLESHOOTING", "disable_audio_entirely")):
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.unload()
            pygame.mixer.music.load(soundlib.find_music_file(mfname))
            pygame.mixer.music.play(-1, fade_ms=2000)
            pygame.mixer.music.set_volume(util.config.getfloat("GENERAL", "music_volume"))

    def start_music(self, mfname, yafi=False):
        # yafi = You Asked For It
        if util.config.get("GENERAL", "music_mode").casefold() != MUSIC_MODE_STREAM.casefold():
            self._start_cached_music(mfname, yafi)
        else:
            self._start_streaming_music(mfname, yafi)
        if mfname:
            self.music_name = mfname

    def stop_music(self):
        if self.music_channels[self.current_music_channel].get_busy():
            self.music_channels[self.current_music_channel].stop()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
        #self.music_name = ""

    def set_music_volume(self, nu_volume):
        if util.config.get("GENERAL", "music_mode").casefold() != MUSIC_MODE_STREAM.casefold():
            if self.music_channels[self.current_music_channel].get_busy():
                self.music_channels[self.current_music_channel].get_sound().set_volume(nu_volume)
        else:
            pygame.mixer.music.set_volume(nu_volume)

    def start_sound_effect(self, sound_fx_name, loops=0, allow_multiple_copies=False):
        if (util.config.getboolean("GENERAL", "sound_on") and self.audio_enabled and not util.config.getboolean("TROUBLESHOOTING", "disable_audio_entirely")):
            my_sound = soundlib.SOUND_FX_LIBRARY.get(sound_fx_name, None)
            if my_sound and allow_multiple_copies or my_sound.get_num_channels() < 1:
                my_sound.set_volume(util.config.getfloat("GENERAL", "sound_volume"))
                sdlmixer.Mix_PlayChannel(-1, my_sound, loops)

    def resume_music(self):
        if self.music_name:
            mname, self.music_name = self.music_name, None
            self.start_music(mname)

    def _set_focused_widget(self, widj):
        if widj and widj.can_take_focus:
            self._focused_widget = weakref.ref(widj)
        else:
            self._focused_widget = None

    def _get_focused_widget(self):
        if self._focused_widget:
            return self._focused_widget()

    def _del_active_widget(self):
        self._focused_widget = None

    focused_widget = property(_get_focused_widget, _set_focused_widget, _del_active_widget)

    def all_widgets(self):
        for w in self.widgets:
            for wc in w.get_all_widgets():
                yield wc

    def all_active_widgets(self):
        for w in self.widgets:
            if w.active and w.visible:
                for wc in w.get_all_active_widgets():
                    yield wc

    def get_keys_for(self, action):
        keys = util.config.get("KEYS", action)
        key_set = set()
        for k in keys.split():
            if k.startswith("K_"):
                k = getattr(pygame, k, None)
                if k:
                    key_set.add(k)
        return key_set

    def is_key_for_action(self, ev, action):
        keys = util.config.get("KEYS", action)
        for k in keys.split():
            if k.startswith("K_"):
                k = getattr(pygame, k, None)
                if k and k == ev.key:
                    return True
            elif k == ev.unicode:
                return True

    def key_is_in_use(self, ukey):
        for op in util.config.options("KEYS"):
            keys = util.config.get("KEYS", op)
            for k in keys.split():
                if k.startswith("K_"):
                    k = getattr(pygame, k, None)
                    if k and pygame.key.name(k) == ukey:
                        return op
                elif k == ukey:
                    return op

    def get_window_config(self):
        myconfig = util.config.get("GENERAL", "window_size")
        ws, hs = myconfig.split("x")
        try:
            return int(ws), int(hs)
        except ValueError:
            return 800, 600

    def get_resolution_config(self):
        myconfig = util.config.get("GENERAL", "fullscreen_resolution")
        if "x" in myconfig:
            ws, hs = myconfig.split("x")
            try:
                return int(ws), int(hs)
            except ValueError:
                return 0,0
        else:
            return 0,0

    def default_to_windowed(self):
        self.window = ext.window.Window(self.title, self.get_window_config(), flags=WINDOWED_FLAGS)
        util.config.set("GENERAL", "fullscreen", "False")
        with open(util.user_dir("config.cfg"), "wt") as f:
            util.config.write(f)

    def reset_screen(self):
        # TODO: SDL_SetWindowFullscreen is probably a better way to switch screen.
        # This function sets up the window, renderer, and target texture.
        if util.config.getboolean("GENERAL", "fullscreen"):
            try:
                self.window = ext.window.Window(self.title, self.get_resolution_config(), flags=FULLSCREEN_FLAGS)
            except:
                self.default_to_windowed()
        else:
            self.window = ext.window.Window(self.title, self.get_window_config(), flags=WINDOWED_FLAGS)
        winwidth, winheight = self.window.size
        if self.screen:
            self.screen.destroy()
        self.screen = ext.renderer.Renderer(
            self.window, logical_size=((max(800, 600 * winwidth // winheight), 600)), 
            flags=sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_TARGETTEXTURE | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        if self.target_texture:
            sdl2.SDL_DestroyTexture(self.target_texture)
        self.target_texture = sdl2.SDL_CreateTexture(self.screen.renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_TARGET, *self.screen.logical_size)


    def _update_mouse_pos(self):
        self.mouse_pos = ext.mouse.mouse_coords()

    MESSAGE_LOG_LENGTH = 100
    def record_message(self, msg):
        self.message_log.append(msg)
        if len(self.message_log) > self.MESSAGE_LOG_LENGTH:
            self.message_log.pop(0)

    def clear_messages(self):
        self.message_log.clear()

    def activate_next_widget(self, backwards=False, key=None):
        wlist = [widg for widg in self.all_active_widgets() if widg.can_take_focus]
        if key:
            wlist.sort(key=key)
        awid = self.focused_widget
        if awid and awid in wlist:
            if backwards:
                n = wlist.index(awid) - 1
            else:
                n = wlist.index(awid) + 1
                if n >= len(wlist):
                    n = 0
            self.focused_widget = wlist[n]
        elif wlist:
            self.focused_widget = wlist[0]

    @staticmethod
    def _sort_widgets_vertically(widg):
        my_rect = widg.get_rect()
        return (my_rect.centerx, my_rect.centery)

    @staticmethod
    def _sort_widgets_horizontally(widg):
        my_rect = widg.get_rect()
        return (my_rect.centery, my_rect.centerx)

    def activate_down_widget(self):
        fwid = self.focused_widget
        if fwid and fwid.down_widget:
            self.focused_widget = fwid.down_widget
        else:
            self.activate_next_widget(key=self._sort_widgets_vertically)

    def activate_up_widget(self):
        fwid = self.focused_widget
        if fwid and fwid.up_widget:
            self.focused_widget = fwid.up_widget
        else:
            self.activate_next_widget(backwards=True, key=self._sort_widgets_vertically)

    def activate_right_widget(self):
        fwid = self.focused_widget
        if fwid and fwid.right_widget:
            self.focused_widget = fwid.right_widget
        else:
            self.activate_next_widget(key=self._sort_widgets_horizontally)

    def activate_left_widget(self):
        fwid = self.focused_widget
        if fwid and fwid.left_widget:
            self.focused_widget = fwid.left_widget
        else:
            self.activate_next_widget(backwards=True, key=self._sort_widgets_horizontally)

    def _draw_tooltip(self):
        x, y = self.mouse_pos
        x += 16
        y += 16
        if x + 200 > self.screen.logical_size[0]:
            x -= 200
        myimage = image.TextImage(self.widget_tooltip, 200, fontstyles.SMALLFONT)
        myrect = myimage.get_rect(0)
        myrect.x = x
        myrect.y = y
        default_border.render(myrect)
        myimage.render(myrect)

    def ui_is_active(self):
        # Return True if there are any active UI elements.
        return any([w.active for w in self.widgets]) or self.alert_queue or self.deployment_queue or self.trigger_queue

    def flip(self):
        self.screen.present()

    def update_alerts(self):
        if self.alert_queue:
            if not any(alerts.WTAG_ALERT in w.tags for w in self.widgets):
                aw = self.alert_queue.pop(0)
                aw.deploy_to_main()
                sdl2.SDL_FlushEvents(0, 65535)

    @property
    def widgets_active(self):
        return self._widgets_active
    
    @widgets_active.setter
    def widgets_active(self, new_val):
        self._widgets_active = bool(new_val)
        for w in self.all_active_widgets():
            if self._widgets_active and hasattr(w, "on_activate"):
                w.on_activate()
            elif not self._widgets_active and hasattr(w, "on_freeze"):
                w.on_freeze()

    def update_trigger_queue(self):
        camp = self.session_data.get(campaign.SDAT_CAMPAIGN, None)
        if not camp:
            self.trigger_queue.clear()
            return
        while self.trigger_queue:
            current_round = list(self.trigger_queue)
            self.trigger_queue.clear()
            done = set()

            for item in current_round:
                if item not in done:
                    done.add(item)
                camp.process_trigger(*item)

    def play(self):
        # A nonblocking game loop.
        myclock = clock.Clock()
        delta = 1000.0 / float(FPS)

        while self.widgets and not self.got_quit:
            # BEFORE polling for events, check for alerts!
            self.update_alerts()

            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for ev in ext.common.get_events():
                if ev.type == sdl2.SDL_QUIT:
                    self.got_quit = True
                elif ev.type == sdl2.SDL_MOUSEMOTION:
                    self._update_mouse_pos()
                elif ev.type == sdl2.SDL_KEYDOWN:
                    if self.is_key_for_action(ev, "next_widget"):
                        self.activate_next_widget(ev.mod & sdl2.keycode.KMOD_SHIFT)
                    elif ev.key == sdl2.keycode.SDLK_F10:
                        self.print_widgets()

                # Inform any interested widgets of the event.
                self.widget_responded = False
                if self.widgets_active:
                    for w in list(reversed(self.widgets)):
                        if not self.widget_responded:
                            w.respond_event(ev)
                        else:
                            break

                if not self.widget_responded:
                    if ev.type == sdl2.SDL_KEYDOWN:
                        if self.is_key_for_action(ev, "up"):
                            self.activate_up_widget()
                        elif self.is_key_for_action(ev, "down"):
                            self.activate_down_widget()
                        elif self.is_key_for_action(ev, "left"):
                            self.activate_left_widget()
                        elif self.is_key_for_action(ev, "right"):
                            self.activate_right_widget()

            # Deploy queued widgets here, if appropriate.
            if self.deployment_queue and not (self.alert_queue or any(alerts.WTAG_ALERT in w.tags for w in self.widgets)):
                while self.deployment_queue:
                    w = self.deployment_queue.pop(0)
                    w.launch()

            # Rendering happens here.
            sdl2.SDL_SetRenderTarget(self.screen.renderer, self.target_texture)
            sdl2.SDL_RenderClear(self.screen.renderer)
            
            #self.screen.fill((0,0,self.screen.logical_size[0], self.screen.logical_size[1]))
            self.anim_phase = (self.anim_phase + 1) % 6000
            self.widget_tooltip = None
            for w in self.widgets:
                w.update(delta)
            self.render_notifications()
            if self.widget_tooltip:
                self._draw_tooltip()

            self.update_trigger_queue()

            # flip() the display to put your work on screen
            sdl2.SDL_SetRenderTarget(self.screen.renderer, None)
            sdl2.SDL_RenderClear(self.screen.renderer)
            sdl2.SDL_RenderCopy(self.screen.renderer, self.target_texture, None, None)
            self.screen.present()
            #self.flip()

            delta = myclock.tick(FPS)
            self.standing_by = False

    def print_widgets(self):
        print("Top Level Widgets")
        print("\n".join(["{}: {}".format(w, w.active) for w in self.widgets]))




INPUT_CURSOR = None

POSTERS = list()
my_state = GameState()

# The FPS the rules runs at.
FPS = 30

# Remember whether or not this unit has been initialized, since we don't need
# to initialize it more than once.
INIT_DONE = False


def please_stand_by(caption=None):
    if not my_state.standing_by:
        img: sdl2.SDL_Surface = ext.image.load_img(random.choice(POSTERS))
        w, h = my_state.screen.logical_size

        dest = frects.PyRect(0,0,int(img.w * h//img.h),h)
        dest.centerx = w//2
        tex = ext.renderer.Texture(my_state.screen, img)
        sdl2.SDL_FreeSurface(img)

        my_state.screen.clear()
        my_state.screen.copy(tex, dstrect=dest)
        tex.destroy()

        my_state.standing_by = True
        my_state.screen.present()


from . import frects, ttfhelper
from . import fontstyles

VALIGN_TOP = -1
VALIGN_CENTER = 0
VALIGN_BOTTOM = 1

def draw_text(style: fontstyles.FontStyle, text, dest: frects.PyRect, color=None, align=fontstyles.ALIGN_LEFT, vjustify=VALIGN_TOP):
    # Draw some text to the screen with the provided options.
    myimage = style.render_text(text, dest.width, align=align, color=color)
    if myimage.h < dest.h:
        if vjustify == 0:
            dest.y += (dest.h - myimage.h)//2
        elif vjustify > 0:
            dest.y += dest.h - myimage.h
    sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, dest)
    texture = ext.renderer.Texture(my_state.screen, myimage)
    sdl2.SDL_FreeSurface(myimage)
    dest.size = texture.size
    _=my_state.screen.copy(texture, dstrect=dest)
    texture.destroy()
    sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, None)


class BasicNotification(frects.Frect):
    IP_INFLATE = 0
    IP_DISPLAY = 1
    IP_DEFLATE = 2
    IP_DONE = 3

    def __init__(self, text, style=None, dx=16, dy=16, w=256, h=10, anchor=frects.ANCHOR_UPPERLEFT,
                 border=default_border, count=60, **kwargs):
        style = style or fontstyles.BIGFONT
        w = min(w, style.linesize(text)[0])
        self.text_image = image.TextImage(text, w, style)
        h = max(h, self.text_image.size[1])
        super().__init__(dx, dy, w, h, anchor, **kwargs)
        self.border = border
        self.count = count
        self._inflation_phase = self.IP_INFLATE
        self._inflation_count = 0
        my_state.notifications.append(self)

    def render(self):
        if self._inflation_phase == self.IP_INFLATE:
            # Inflating
            mydest = self.get_rect()
            mydest.inflate_ip(-(self.w * (5 - self._inflation_count)) // 6,
                              -(self.h * (5 - self._inflation_count)) // 6)
            self.border.render(mydest)
            self._inflation_count += 1
            if self._inflation_count >= 5:
                self._inflation_phase = self.IP_DISPLAY
        elif self._inflation_phase == self.IP_DISPLAY and self.count > 0:
            mydest = self.get_rect()
            self.border.render(mydest)
            self.text_image.render(mydest)
            self.count -= 1
        else:
            mydest = self.get_rect()
            mydest.inflate_ip(-(self.w * (5 - self._inflation_count)) // 6,
                              -(self.h * (5 - self._inflation_count)) // 6)
            self.border.render(mydest)
            self._inflation_count -= 1
            if self._inflation_count <= 0:
                self._inflation_phase = self.IP_DONE

    def is_done(self):
        return self._inflation_phase == self.IP_DONE


from . import container
from . import namegen
from . import randmaps
from . import scenes
from . import plots, stories
from . import image
from . import effects
from . import campaign
from . import widgets
from . import dialogue
from . import cutscene
from . import okapipuzzle
from . import challenges
from . import memos
from . import internationalization
from . import widgetmenu
from . import alerts






FULLSCREEN_FLAGS = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN
WINDOWED_FLAGS = sdl2.SDL_WINDOW_SHOWN



def init(winname, appname, gamedir, icon="sys_icon.png", poster_pattern="poster_*.png",
         display_font="Atan.ttf", text_font="SourceHanSans-Heavy.ttc", 
         bold_font="SourceHanSans-Bold.ttc", italic_font="SourceHanSans-Heavy.ttc", 
         start_gfx=True):
    global INIT_DONE
    if not INIT_DONE:
        util.init(appname, gamedir)
        # Init image.py
        image.init_image(util.image_dir(""))

        global POSTERS
        POSTERS += glob.glob(util.image_dir(poster_pattern))

        my_state.title = winname

        if start_gfx:
            ext.common.init()
            sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG)
            my_state.audio_enabled = not util.config.getboolean("TROUBLESHOOTING", "disable_audio_entirely")
            if my_state.audio_enabled:
                sdlmixer.Mix_Init(sdlmixer.MIX_INIT_OGG)
            # pygame.display.set_caption(winname, appname)
            # pygame.display.set_icon(pygame.image.load(util.image_dir(icon)))
            # Set the screen size.
            my_state.reset_screen()
            ext.renderer.set_texture_scale_quality("best")
            #sdl2.SDL_RenderSetIntegerScale(my_state.screen.renderer, sdl2.SDL_TRUE)

            if my_state.audio_enabled:
                # Initialize a 44.1 kHz 16-bit stereo mixer with a 1024-byte buffer size
                ret = sdlmixer.Mix_OpenAudio(44100, sdl2.AUDIO_S16SYS, 2, 1024)
                if ret < 0:
                    err = sdlmixer.Mix_GetError().decode("utf8")
                    raise RuntimeError("Error initializing the mixer: {0}".format(err))
                soundlib.init_sound(gamedir, util.music_dir(""))

            global INPUT_CURSOR
            INPUT_CURSOR = image.Image("sys_textcursor.png", 8, 16)

            fontstyles.init_fonts(display_font, text_font, bold_font, italic_font)

            global FPS
            FPS = util.config.getint("GENERAL", "frames_per_second")

        INIT_DONE = True

def quit():
    fontstyles.quit()
    my_state.screen.destroy()
    my_state.window.close()
    sdlimage.IMG_Quit()
    soundlib.quit()
    sdlmixer.Mix_Quit()
    ext.common.quit()
    
