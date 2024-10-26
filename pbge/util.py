#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2012 Anne Archibald <peridot.faceted@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
# 
import os
import configparser
import platform
import shutil

GAMEDIR = '.'
USERDIR = '.'


def sanitize_filename(fname):
    # Note: Only for use on filenames! Don't use this on a file path or it'll mess up.
    mychars = list()
    for c in fname:
        if c not in " %:/,\\[]<>*?\n\t\"'|":
            mychars.append(c)
        else:
            mychars.append("_")
    return ''.join(mychars)


def game_dir(*args):
    return os.path.join(GAMEDIR, *args)


def image_dir(fname=""):
    return os.path.join(game_dir('image'), fname)


def data_dir(fname=""):
    return os.path.join(game_dir('data'), fname)


def user_dir(*args):
    return os.path.join(USERDIR, *args)


def music_dir(fname=""):
    return os.path.join(game_dir('music'), fname)


def soundfx_dir(fname=""):
    return os.path.join(game_dir('soundfx'), fname)


# Load the configuration file.
config = None


def init(appname, gamedir):
    global GAMEDIR
    GAMEDIR = gamedir
    global USERDIR
    # for v0.940: Steam cloud save doesn't let you just stick your user dir in home on Windows. So,
    if platform.system() == "Windows":
        USERDIR = os.path.join(gamedir, appname + "_user")
        if not os.path.exists(USERDIR):
            OLDUSERDIR = os.path.expanduser(os.path.join('~', appname))
            if os.path.exists(OLDUSERDIR):
                shutil.move(OLDUSERDIR, USERDIR)
            else:
                os.mkdir(USERDIR)
    else:
        USERDIR = os.path.expanduser(os.path.join('~', appname))
        if not os.path.exists(USERDIR):
            os.mkdir(USERDIR)

    global config
    config = configparser.ConfigParser()
    with open(data_dir("config_defaults.cfg")) as f:
        config.read_file(f)
    if not config.read([user_dir("config.cfg")]):
        with open(user_dir("config.cfg"), "wt") as f:
            config.write(f)


# Code removed from the GearHead Caramel shopping UI unit. The original undo/redo system makes some assumptions about
# shopping that later turned out to not be true- that there would be one buy list and one sell list is the big one.
# Also, the redo functionality never gets used. So, I'm moving this code here because it might come in handy someday.
# It's good code.

# An Undo/Redo item.
class UndoRedoBase(object):
    # Return True if doing succeeded, False if not.
    def on_do(self):
        raise NotImplementedError('UndoRedoBase.on_do must be overridden')

    # Return True if undoing succeeded, False if not.
    def on_undo(self):
        raise NotImplementedError('UndoRedoBase.on_undo must be overridden')

# The undo/redo list.
class UndoRedoSystem(object):
    def __init__(self):
        self.undos = list()
        self.redos = list()

    def do_action(self, undo_redo_base):
        if undo_redo_base.on_do():
            self.undos.append(undo_redo_base)
            self.redos.clear()

    def is_empty(self):
        return not (self.undos or self.redos)

    def undo(self):
        if not self.undos:
            return
        undo_redo_base = self.undos[-1]
        if undo_redo_base.on_undo():
            self.undos.pop()
            self.redos.append(undo_redo_base)

    def redo(self):
        if not self.redos:
            return
        undo_redo_base = self.redos[-1]
        if undo_redo_base.on_do():
            self.redos.pop()
            self.undos.append(undo_redo_base)

    # Undo a specific item.
    def undo_specific(self, undo_redo_base):
        if not (undo_redo_base in self.undos):
            return
        if undo_redo_base.on_undo():
            self.undos.remove(undo_redo_base)
            self.redos.append(undo_redo_base)

    # Undo everything.
    def undo_all(self):
        while self.undos:
            undo_redo_base = self.undos.pop()
            undo_redo_base.on_undo()
        self.redos.clear()
