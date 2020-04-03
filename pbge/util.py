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

GAMEDIR = '.'
USERDIR = '.'

def game_dir(*args):
    return os.path.join(GAMEDIR,*args)
def image_dir(fname=""):
    return os.path.join(game_dir('image'),fname)
def data_dir(fname=""):
    return os.path.join(game_dir('data'),fname)
def user_dir( *args):
    return os.path.join(USERDIR,*args)
def music_dir(fname=""):
    return os.path.join(game_dir('music'),fname)

# Load the configuration file.
config = None

def init( appname,gamedir ):
    global GAMEDIR
    GAMEDIR = gamedir
    global USERDIR
    USERDIR = os.path.expanduser( os.path.join( '~' , appname ) )
    if not os.path.exists( USERDIR ):
        os.mkdir( USERDIR )

    global config
    config = configparser.ConfigParser()
    with open(data_dir("config_defaults.cfg")) as f:
        config.read_file( f )
    if not config.read( [user_dir( "config.cfg" )] ):
        with open( user_dir( "config.cfg" ) , "wt" ) as f:
            config.write( f )

