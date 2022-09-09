import functools
import os
import pygame
import glob


search_path = list()
proprietary_search_path = list()    # Contains music files released under a non-free license; these are excluded from
                                    # the Scenario Creator sound selection menus.


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


def init_sound(def_music_folder):
    search_path.append(def_music_folder)
