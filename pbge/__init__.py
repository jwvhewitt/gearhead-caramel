# Polar Bear Game Engine

# This package contains some low-level graphics stuff needed to
# create an isometric RPG style rules in Python. The idea is to
# isolate the graphics handling from the code as much as possible,
# so that if PyGame is replaced the interface shouldn't change
# too much. Also, so that creating a new rules should be as simple
# as importing this package.

# Word wrapper taken from the PyGame wiki plus
# the list-printer from Anne Archibald's GearHead Prime demo.

import pygame
from itertools import chain
from . import util
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

    def render(self, dest, dest_surface=None):
        """Draw this decorative border at dest on screen."""
        # We're gonna draw a decorative border to surround the provided area.
        if self.border == None:
            self.border = image.Image(self.border_name, self.border_width, self.border_width)
        if self.tex_name and not self.tex:
            self.tex = image.Image(self.tex_name, self.tex_width, self.tex_width)
            if self.transparent:
                _=self.tex.bitmap.set_alpha(224)

        if not dest_surface:
            dest_surface = my_state.screen

        # Draw the backdrop.
        if self.tex:
            self.tex.tile(dest.inflate(self.padding, self.padding), dest_surface=dest_surface)

        # Expand the dimensions to their complete size.
        # The method inflate_ip doesn't seem to be working... :(
        fdest = dest.inflate(self.padding, self.padding)

        self.border.render((fdest.x - self.border_width // 2, fdest.y - self.border_width // 2), self.tl, dest_surface=dest_surface)
        self.border.render((fdest.x - self.border_width // 2, fdest.y + fdest.height - self.border_width // 2), self.bl, dest_surface=dest_surface)
        self.border.render((fdest.x + fdest.width - self.border_width // 2, fdest.y - self.border_width // 2), self.tr, dest_surface=dest_surface)
        self.border.render(
            (fdest.x + fdest.width - self.border_width // 2, fdest.y + fdest.height - self.border_width // 2), self.br, dest_surface=dest_surface)

        fdest = dest.inflate(self.padding - self.border_width, self.padding + self.border_width)
        _=dest_surface.set_clip(fdest)
        for x in range(0, fdest.w // self.border_width + 2):
            self.border.render((fdest.x + x * self.border_width, fdest.y), self.t, dest_surface=dest_surface)
            self.border.render((fdest.x + x * self.border_width, fdest.y + fdest.height - self.border_width), self.b, dest_surface=dest_surface)

        fdest = dest.inflate(self.padding + self.border_width, self.padding - self.border_width)
        _=dest_surface.set_clip(fdest)
        for y in range(0, fdest.h // self.border_width + 2):
            self.border.render((fdest.x, fdest.y + y * self.border_width), self.l, dest_surface=dest_surface)
            self.border.render((fdest.x + fdest.width - self.border_width, fdest.y + y * self.border_width), self.r, dest_surface=dest_surface)
        _=dest_surface.set_clip(None)


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
    def __init__(self, screen=None):
        self.screen: pygame.Surface = screen
        self.physical_screen: pygame.Surface = None
        self.view = None
        self.got_quit = False
        self.widgets = list()
        self.widgets_active = True
        self.active_widget_hilight = False
        self._active_widget = None
        self.widget_clicked = False
        self.widget_responded = False
        self.widget_all_text = False
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

        # self.client = SteamClient()

    def render_notifications(self):
        for n in list(self.notifications):
            n.render()
            if n.is_done():
                self.notifications.remove(n)

    def render_and_flip(self, show_widgets=True, reset_standing_by=True):
        if self.view:
            self.view()
        self.do_flip(show_widgets=show_widgets, reset_standing_by=reset_standing_by)

    def do_flip(self, show_widgets=True, reset_standing_by=True):
        self.widget_tooltip = None
        if show_widgets:
            self.render_widgets()
        if self.notifications:
            self.render_notifications()
        if self.widget_tooltip:
            x, y = self.mouse_pos
            x += 16
            y += 16
            if x + 200 > self.screen.get_width():
                x -= 200
            myimage = render_text(self.small_font, self.widget_tooltip, 200)
            myrect = myimage.get_rect(topleft=(x, y))
            default_border.render(myrect)
            _=self.screen.blit(myimage, myrect)
        self.anim_phase = (self.anim_phase + 1) % 6000
        if reset_standing_by:
            self.standing_by = False
        if util.config.getboolean("ACCESSIBILITY", "stretchy_screen"):
            w, h = self.physical_screen.get_size()
            _=pygame.transform.smoothscale(self.screen, (w, h), self.physical_screen)
            # pygame.transform.scale(self.screen, (w, h), self.physical_screen)
        pygame.display.flip()

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
                return my_sound.play(loops=loops)

    def resume_music(self):
        if self.music_name:
            mname, self.music_name = self.music_name, None
            self.start_music(mname)

    def _set_active_widget(self, widj):
        if widj:
            self._active_widget = weakref.ref(widj)
        else:
            self._active_widget = None

    def _get_active_widget(self):
        if self._active_widget:
            return self._active_widget()

    def _del_active_widget(self):
        self._active_widget = None

    active_widget = property(_get_active_widget, _set_active_widget, _del_active_widget)

    def all_widgets(self):
        for w in self.widgets:
            for wc in w.get_all_widgets():
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

    def _get_all_kb_selectable_widgets(self, wlist):
        mylist = list()
        for w in wlist:
            if w.active:
                if w.is_kb_selectable():
                    mylist.append(w)
                if w.children:
                    mylist += self._get_all_kb_selectable_widgets(w.children)
        return mylist

    def activate_next_widget(self, backwards=False):
        wlist = self._get_all_kb_selectable_widgets(self.widgets)
        awid = self.active_widget
        if awid and awid in wlist:
            if backwards:
                n = wlist.index(awid) - 1
            else:
                n = wlist.index(awid) + 1
                if n >= len(wlist):
                    n = 0
            self.active_widget = wlist[n]
        elif wlist:
            self.active_widget = wlist[0]

    def resize_stretchy_layers(self, w, h):
        for sl in self.stretchy_layers:
            sl.resize_layer(w, h)

    def resize_stretchy(self):
        w, h = self.physical_screen.get_size()
        self.screen = pygame.Surface((max(800, 600 * w // h), 600))
        self.resize_stretchy_layers(w, h)

    def set_size(self, w, h):
        if util.config.getboolean("ACCESSIBILITY", "stretchy_screen"):
            self.physical_screen = pygame.display.set_mode((max(w, 800), max(h, 600)), pygame.RESIZABLE)
            self.resize_stretchy()
        else:
            self.screen = pygame.display.set_mode((max(w, 800), max(h, 600)), pygame.RESIZABLE)
            self.resize_stretchy_layers(*self.screen.get_size())

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

    def default_to_stretchy_windowed(self):
        my_state.physical_screen = pygame.display.set_mode(self.get_window_config(), WINDOWED_FLAGS)
        util.config.set("GENERAL", "fullscreen", "False")
        with open(util.user_dir("config.cfg"), "wt") as f:
            util.config.write(f)

    def default_to_windowed(self):
        my_state.screen = pygame.display.set_mode(self.get_window_config(), WINDOWED_FLAGS)
        util.config.set("GENERAL", "fullscreen", "False")
        with open(util.user_dir("config.cfg"), "wt") as f:
            util.config.write(f)

    def reset_screen(self):
        if util.config.getboolean("ACCESSIBILITY", "stretchy_screen"):
            if util.config.getboolean("GENERAL", "fullscreen"):
                try:
                    self.physical_screen = pygame.display.set_mode(self.get_resolution_config(), FULLSCREEN_FLAGS)
                except:
                    self.default_to_stretchy_windowed()
            else:
                # my_state.physical_screen = pygame.display.set_mode((800, 600), WINDOWED_FLAGS)
                self.physical_screen = pygame.display.set_mode(self.get_window_config(), WINDOWED_FLAGS)
            self.resize_stretchy()
        else:
            if util.config.getboolean("GENERAL", "fullscreen"):
                try:
                    self.screen = pygame.display.set_mode(self.get_resolution_config(), FULLSCREEN_FLAGS)
                except:
                    self.default_to_windowed()
            else:
                self.screen = pygame.display.set_mode(self.get_window_config(), WINDOWED_FLAGS)
            self.resize_stretchy_layers(*self.screen.get_size())

    def update_mouse_pos(self):
        if util.config.getboolean("ACCESSIBILITY", "stretchy_screen"):
            x, y = pygame.mouse.get_pos()
            w1, h1 = self.physical_screen.get_size()
            w2, h2 = self.screen.get_size()
            self.mouse_pos = (x * w2 // w1, y * h2 // h1)
        else:
            self.mouse_pos = pygame.mouse.get_pos()

    MESSAGE_LOG_LENGTH = 100
    def record_message(self, msg):
        self.message_log.append(msg)
        if len(self.message_log) > self.MESSAGE_LOG_LENGTH:
            self.message_log.pop(0)

    def clear_messages(self):
        self.message_log.clear()

    def play(self):
        # A nonblocking game loop.
        myclock = pygame.time.Clock()
        running = True
        delta = 1000.0 / float(FPS)

        while self.widgets and not self.got_quit:

            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.got_quit = True
                elif ev.type == pygame.MOUSEMOTION:
                    self.update_mouse_pos()
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_PRINT:
                        pygame.image.save(my_state.screen, util.user_dir("out.png"))
                    elif self.is_key_for_action(ev, "next_widget"):
                        self.active_widget_hilight = True
                        self.activate_next_widget(ev.mod & pygame.KMOD_SHIFT)
                elif ev.type == pygame.VIDEORESIZE:
                    # PG2 Change
                    # pygame.display._resize_event(ev)
                    self.set_size(max(ev.w, 800), max(ev.h, 600))

                # Inform any interested widgets of the event.
                self.widget_clicked = False
                self.widget_responded = False
                self.widget_all_text = False
                if self.widgets_active:
                    for w in self.widgets:
                        w.respond_event(ev)

            # RENDER YOUR GAME HERE
            for w in self.widgets:
                w.update(delta)

            # flip() the display to put your work on screen
            pygame.display.flip()

            pass
            delta = myclock.tick(FPS)


class StretchyLayer():
    # A layer that is guaranteed to fill the screen, even though its height is hard coded
    # to 600. Basically a way to make sure graphics created for the original 800x600 window
    # still fill the screen appropriately at higher modern resolutions.
    def __init__(self):
        w, h = my_state.screen.get_size()
        self.surf: pygame.Surface = None
        self.resize_layer(w,h)
        my_state.stretchy_layers.add(self)

    def resize_layer(self, w, h):
        # w and h are the width and height of the physical screen.
        if util.config.getboolean("TROUBLESHOOTING", "disable_scaling"):
            self.surf = pygame.Surface((w, 600), flags=pygame.SRCALPHA).convert_alpha()
        else:
            self.surf = pygame.Surface((max(800, 600 * w // h), 600), flags=pygame.SRCALPHA).convert_alpha()
        self.clear()

    def get_height(self):
        return self.surf.get_height()

    def get_width(self):
        return self.surf.get_width()

    def get_size(self):
        return self.surf.get_size()

    def render(self):
        w, h = my_state.screen.get_size()
        if util.config.getboolean("TROUBLESHOOTING", "disable_scaling"):
            _=my_state.screen.blit(self.surf, pygame.Rect(0,h//2 - 300,w,600))
        else:
            bigsurf = pygame.transform.smoothscale(self.surf, (w, h))
            #bigsurf.set_colorkey((0,0,255))
            _=my_state.screen.blit(bigsurf, pygame.Rect(0,0,800,600))

    def clear(self):
        _=self.surf.fill((0,0,0,0))



INPUT_CURSOR = None
SMALLFONT = None
TINYFONT = None
ITALICFONT = None
MEDIUM_DISPLAY_FONT = None
BIGFONT = None
HUGEFONT = None
ANIMFONT = None
MEDIUMFONT = None
ALTTEXTFONT = None  # Use this instead of MEDIUMFONT when you want to shake things up a bit.
POSTERS = list()
my_state = GameState()

# The FPS the rules runs at.
FPS = 30

# Use a timer to control FPS.
TIMEREVENT = pygame.event.custom_type()

# Remember whether or not this unit has been initialized, since we don't need
# to initialize it more than once.
INIT_DONE = False


def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    old = None
    while l > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def wrap_with_records(fulltext, font, maxwidth):
    # Do a word wrap, but also return the length of each line including whitespace and newlines.
    done = 0
    wrapped = list()
    line_lengths = list()

    for text in fulltext.splitlines(True):
        done = 0
        while not done:
            nl, done, stext = truncline(text, font, maxwidth)
            wrapped.append(stext.lstrip())
            # wrapped.append(stext)
            line_lengths.append(nl + 1)
            text = text[nl:]
    return wrapped, line_lengths


def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)


def render_text(font, text, width, color=TEXT_COLOR, justify=-1, antialias=True):
    # Return an image with prettyprinted text.
    lines = wrap_multi_line(text, font, width)

    imgs = [font.render(l, antialias, color) for l in lines]
    h = sum(i.get_height() for i in imgs)
    s = pygame.surface.Surface((width, h))
    s.fill((0, 0, 0))
    o = 0
    for i in imgs:
        if justify == 0:
            x = width // 2 - i.get_width() // 2
        elif justify > 0:
            x = width - i.get_width()
        else:
            x = 0
        s.blit(i, (x, o))
        o += i.get_height()
    s.set_colorkey((0, 0, 0), pygame.RLEACCEL)
    return s


def draw_text(font, text, rect, color=TEXT_COLOR, justify=-1, antialias=True, dest_surface=None, vjustify=-1):
    # Draw some text to the screen with the provided options.
    dest_surface = dest_surface or my_state.screen
    myimage = render_text(font, text, rect.width, color, justify, antialias)
    if justify == 0:
        myrect = myimage.get_rect(midtop=rect.midtop)
    elif justify > 0:
        myrect = myimage.get_rect(topleft=rect.topleft)
    else:
        myrect = rect
    if vjustify == 0:
        myrect.centery = rect.centery
    elif vjustify > 0:
        myrect.bottom = rect.bottom
    dest_surface.set_clip(rect)
    dest_surface.blit(myimage, myrect)
    dest_surface.set_clip(None)


def wait_event():
    # Wait for input, then return it when it comes.
    ev = pygame.event.wait()

    # Record if a quit event took placewaitwait
    if ev.type == pygame.QUIT:
        my_state.got_quit = True
    elif ev.type == TIMEREVENT:
        pygame.event.clear(TIMEREVENT)
    elif ev.type == pygame.MOUSEMOTION:
        my_state.update_mouse_pos()
    elif ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_PRINT:
            pygame.image.save(my_state.screen, util.user_dir("out.png"))
        elif my_state.is_key_for_action(ev, "next_widget"):
            my_state.active_widget_hilight = True
            my_state.activate_next_widget(ev.mod & pygame.KMOD_SHIFT)
    elif ev.type == pygame.VIDEORESIZE:
        # PG2 Change
        # pygame.display._resize_event(ev)
        my_state.set_size(max(ev.w, 800), max(ev.h, 600))

    # Inform any interested widgets of the event.
    my_state.widget_clicked = False
    my_state.widget_responded = False
    my_state.widget_all_text = False
    if my_state.widgets_active:
        for w in my_state.widgets:
            w.respond_event(ev)

    # If the view has a check_event method, call that.
    if my_state.view and hasattr(my_state.view, "check_event") and not (my_state.widget_responded or my_state.widget_all_text):
        my_state.view.check_event(ev)

    return ev


def anim_delay():
    while wait_event().type != TIMEREVENT:
        pass


def alert(text, font=None, justify=-1):
    if not font:
        font = my_state.medium_font
    # mydest = pygame.Rect( my_state.screen.get_width() // 2 - 200, my_state.screen.get_height()//2 - 100, 400, 200 )
    mytext = render_text(font, text, 400, justify=justify)
    mydest = mytext.get_rect(center=(my_state.screen.get_width() // 2, my_state.screen.get_height() // 2))
    initial_widget_state = my_state.widgets_active
    my_state.widgets_active = False

    my_state.record_message(text)

    pygame.event.clear([TIMEREVENT, pygame.KEYDOWN])
    while True:
        ev = wait_event()
        if (ev.type == pygame.MOUSEBUTTONUP) or (ev.type == pygame.QUIT) or (ev.type == pygame.KEYDOWN):
            my_state.widgets_active = initial_widget_state
            return ev
        elif ev.type == TIMEREVENT:
            if my_state.view:
                my_state.view()
            default_border.render(mydest)
            my_state.screen.blit(mytext, mydest)
            my_state.do_flip()


def alert_display(display_fun):
    pygame.event.clear()
    wid_state = my_state.widgets_active
    my_state.widgets_active = False
    while True:
        ev = wait_event()
        if (ev.type == pygame.MOUSEBUTTONUP) or (ev.type == pygame.QUIT):
            break
        elif ev.type == pygame.KEYDOWN and my_state.is_key_for_action(ev, "continue"):
            break
        elif ev.type == TIMEREVENT:
            if my_state.view:
                my_state.view()
            display_fun()
            my_state.do_flip()
    my_state.widgets_active = wid_state


def please_stand_by(caption=None):
    if not my_state.standing_by:
        img = pygame.image.load(random.choice(POSTERS)).convert()
        w, h = my_state.screen.get_size()
        bigsurf = pygame.transform.smoothscale(img, (img.get_width()*h//img.get_height(), h))

        dest = bigsurf.get_rect(center=(my_state.screen.get_width() // 2, my_state.screen.get_height() // 2))
        _=my_state.screen.fill((0, 0, 0))
        _=my_state.screen.blit(bigsurf, dest)
        if caption:
            mytext = BIGFONT.render(caption, True, TEXT_COLOR)
            dest2 = mytext.get_rect(topleft=(dest.x + 32, dest.y + 32))
            default_border.render(dest2)
            _=my_state.screen.blit(mytext, dest2)
        my_state.standing_by = True
        my_state.do_flip(False, reset_standing_by=False)


from . import frects


class BasicNotification(frects.Frect):
    IP_INFLATE = 0
    IP_DISPLAY = 1
    IP_DEFLATE = 2
    IP_DONE = 3

    def __init__(self, text, font=None, dx=16, dy=16, w=256, h=10, anchor=frects.ANCHOR_UPPERLEFT,
                 border=default_border, count=60, **kwargs):
        font = font or my_state.big_font
        w = min(w, font.size(text)[0])
        self.text_bitmap = render_text(font, text, w)
        h = max(h, self.text_bitmap.get_height())
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
            self.border.render(self.get_rect())
            my_state.screen.blit(self.text_bitmap, self.get_rect())
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


from . import rpgmenu
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

# PG2 Change
# FULLSCREEN_FLAGS = pygame.FULLSCREEN | pygame.SCALED
# WINDOWED_FLAGS = pygame.RESIZABLE | pygame.SCALED
FULLSCREEN_FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF
WINDOWED_FLAGS = pygame.RESIZABLE


class LeadingFont(pygame.font.Font):
    # Lead as in the metal, not as in leadership. Look it up on Wikipedia.
    def __init__(self, filename, size, leading=0):
        super().__init__(filename, size)
        self._leading = leading

    def render(self, text, antialias=True, color=TEXT_COLOR, background=None):
        my_image = super().render(text, antialias, color, background).convert_alpha()
        my_rect = my_image.get_rect()
        my_rect.y -= self._leading
        my_rect.h += self._leading
        return my_image.subsurface(my_rect)

    def size(self, text):
        w, h = super().size(text)
        return (w, h + self._leading)

    def get_linesize(self):
        return super().get_linesize() + self._leading

    def get_height(self):
        return super().get_height() + self._leading


def init(winname, appname, gamedir, icon="sys_icon.png", poster_pattern="poster_*.png",
         display_font="Atan.ttf"):
    global INIT_DONE
    if not INIT_DONE:
        util.init(appname, gamedir)
        # Init image.py
        image.init_image(util.image_dir(""))

        global POSTERS
        POSTERS += glob.glob(util.image_dir(poster_pattern))

        pygame.init()
        my_state.audio_enabled = not util.config.getboolean("TROUBLESHOOTING", "disable_audio_entirely")
        if my_state.audio_enabled:
            try:
                pygame.mixer.init()
            except pygame.error:
                my_state.audio_enabled = False
                print("Error: pygame.mixer failed to load.")
        pygame.display.set_caption(winname, appname)
        pygame.display.set_icon(pygame.image.load(util.image_dir(icon)))
        # Set the screen size.
        my_state.reset_screen()

        if my_state.audio_enabled:
            pygame.mixer.set_reserved(2)
            my_state.music_channels.append(pygame.mixer.Channel(0))
            my_state.music_channels.append(pygame.mixer.Channel(1))
            soundlib.init_sound(gamedir, util.music_dir(""))

        global INPUT_CURSOR
        INPUT_CURSOR = image.Image("sys_textcursor.png", 8, 16)

        global SMALLFONT
        SMALLFONT = LeadingFont(util.image_dir("SourceHanSans-Heavy.ttc"), 12, -1)
        my_state.small_font = SMALLFONT

        global TINYFONT
        TINYFONT = pygame.font.Font(util.image_dir("SourceHanSans-Heavy.ttc"), 10)
        my_state.tiny_font = TINYFONT

        global ANIMFONT
        ANIMFONT = LeadingFont(util.image_dir("SourceHanSans-Bold.ttc"), 16, -2)
        my_state.anim_font = ANIMFONT

        global MEDIUMFONT
        MEDIUMFONT = LeadingFont(util.image_dir("SourceHanSans-Heavy.ttc"), 14, -2)
        my_state.medium_font = MEDIUMFONT

        global ALTTEXTFONT

        ALTTEXTFONT = LeadingFont(util.image_dir("SourceHanSans-Heavy.ttc"), 14, -2)
        ALTTEXTFONT.set_italic(True)
        my_state.alt_text_font = ALTTEXTFONT

        global ITALICFONT
        ITALICFONT = LeadingFont(util.image_dir("SourceHanSans-Heavy.ttc"), 12, -1)
        ITALICFONT.set_italic(True)

        global MEDIUM_DISPLAY_FONT
        MEDIUM_DISPLAY_FONT = pygame.font.Font(util.image_dir(display_font), 14)

        global BIGFONT
        BIGFONT = pygame.font.Font(util.image_dir(display_font), 17)
        my_state.big_font = BIGFONT

        global HUGEFONT
        my_state.huge_font = pygame.font.Font(util.image_dir(display_font), 24)
        HUGEFONT = my_state.huge_font

        global FPS
        FPS = util.config.getint("GENERAL", "frames_per_second")
        #pygame.time.set_timer(TIMEREVENT, int(1000 / FPS))

        # Set key repeat.
        pygame.key.set_repeat(200, 100)

        INIT_DONE = True
