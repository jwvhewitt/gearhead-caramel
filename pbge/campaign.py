#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2013 Joeph Hewitt <pyrrho12@yahoo.ca>
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

from . import my_state
import container
import exceptions
import util
import cPickle

class Campaign( object ):
    """Barebones campaign featuring functionality used by other pbge units."""
    def __init__( self, name = "BobDwarf19", explo_class=None ):
        self.name = name
        self.party = list()
        self.scene = None 
        self.entrance = None
        self.destination = None
        self.contents = container.ContainerList()
        self.scripts = container.ContainerList()
        self.uniques = set()
        self.explo_class = explo_class


    def save( self ):
        with open( util.user_dir( "rpg_" + self.name + ".sav" ) , "wb" ) as f:
            cPickle.dump( self , f, -1 )

    def keep_playing_campaign( self ):
        # The default version of this method will keep playing forever.
        # You're probably gonna want to redefine this in your subclass.
        return True

    def active_plots( self ):
        for p in self.scene.scripts:
            if p.active:
                yield p
        for p in self.scripts:
            if p.active:
                yield p

    def check_trigger( self, trigger, thing=None ):
        # Something is happened that plots may need to react to.
        for p in self.active_plots():
            p.handle_trigger( self, trigger, thing )

    def expand_puzzle_menu( self, thing, thingmenu ):
        # Something is happened that plots may need to react to.
        for p in self.active_plots():
            p.modify_puzzle_menu( self, thing, thingmenu )
        if not thingmenu.items:
            thingmenu.add_item( "[Continue]", None )
        else:
            thingmenu.sort()
            thingmenu.add_alpha_keys()


    def place_party( self ):
        """Stick the party close to the waypoint."""
        raise exceptions.NotImplementedError("Method place_party needs custom implementation.")

    def remove_party_from_scene( self ):
        for pc in self.party:
            pc.pos = None
            if pc in self.scene.contents:
                self.scene.contents.remove( pc )

    def play( self ):
        while self.keep_playing_campaign() and not my_state.got_quit:
            exp = self.explo_class( self )
            exp.go()
            if self.destination:
                self.remove_party_from_scene()
                self.scene, self.destination = self.destination, None
                self.place_party()
            elif not exp.no_quit:
                # If the player quit in exploration mode, exit to main menu.
                break

    def dump_info( self ):
        # Print info on all scenes in this world.
        for c in self.contents:
            c.dump_info()


