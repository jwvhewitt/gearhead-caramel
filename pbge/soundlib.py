import os
from sdl2 import sdlmixer
import glob
import collections


search_path = list()
proprietary_search_path = list()    # Contains music files released under a non-free license; these are excluded from
                                    # the Scenario Creator sound selection menus.

SOUND_FX_LIBRARY = dict()
CACHED_MUSIC = collections.OrderedDict()
MUSIC_CACHE_SIZE = 10


def glob_sounds(pattern, include_proprietary=False):
    mylist = list()
    mypaths = list(search_path)
    if include_proprietary:
        mypaths += proprietary_search_path
    for p in mypaths:
        myglob = glob.glob(os.path.join(p, pattern))
        for fname in myglob:
            mylist.append(os.path.basename(fname))
    mylist.sort()
    return mylist


def find_music_file(fname):
    if not os.path.exists(fname):
        for p in search_path + proprietary_search_path:
            if os.path.exists(os.path.join(p, fname)):
                fname = os.path.join(p, fname)
                break
    return fname


def load_cached_sound(fname):
    if fname in CACHED_MUSIC:
        CACHED_MUSIC.move_to_end(fname)
        return CACHED_MUSIC[fname]

    full_fname = find_music_file(fname)
    if full_fname:
        while len(CACHED_MUSIC) >= MUSIC_CACHE_SIZE:
            _k, v = CACHED_MUSIC.popitem()
            sdlmixer.Mix_FreeMusic(v)
        CACHED_MUSIC[fname] = sdlmixer.Mix_LoadMUS(bytes(full_fname, "UTF8"))

    return CACHED_MUSIC[fname]


def init_sound(game_dir, def_music_folder):
    search_path.append(def_music_folder)

    # pre-load all sound effects.
    myglob = glob.glob(os.path.join(game_dir, "soundfx", "*.ogg"))
    for fname in myglob:
        SOUND_FX_LIBRARY[os.path.basename(fname)] = sdlmixer.Mix_LoadWAV(bytes(fname, "UTF8"))


def quit():
    for v in SOUND_FX_LIBRARY.values():
        sdlmixer.Mix_FreeChunk(v)
    for v in CACHED_MUSIC.values():
        sdlmixer.Mix_FreeMusic(v)



