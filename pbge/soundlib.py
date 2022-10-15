import functools
import os
import pygame
import glob


search_path = list()
proprietary_search_path = list()    # Contains music files released under a non-free license; these are excluded from
                                    # the Scenario Creator sound selection menus.

SOUND_FX_LIBRARY = dict()


def glob_sounds(pattern, include_proprietary=False):
    mylist = list()
    mypaths = list(search_path)
    if include_proprietary:
        mypaths += proprietary_search_path
    for p in mypaths:
        myglob = glob.glob(os.path.join(p,pattern))
        for fname in myglob:
            mylist.append(os.path.basename(fname))
    mylist.sort()
    return mylist


@functools.lru_cache(maxsize=23)
def load_cached_sound(fname):
    if not os.path.exists(fname):
        for p in search_path + proprietary_search_path:
            if os.path.exists(os.path.join(p, fname)):
                fname = os.path.join(p, fname)
                break

    return pygame.mixer.Sound(fname)


def init_sound(game_dir, def_music_folder):
    search_path.append(def_music_folder)

    # pre-load all sound effects.
    myglob = glob.glob(os.path.join(game_dir, "soundfx", "*.ogg"))
    for fname in myglob:
        SOUND_FX_LIBRARY[os.path.basename(fname)] = pygame.mixer.Sound(fname)

    pygame.mixer.set_num_channels(16)


