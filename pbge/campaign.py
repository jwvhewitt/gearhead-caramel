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
from . import container
from . import util, dialogue
import pickle
import os
from . import scenes

ALL_CONTENTS_SEARCH_PATH = ["contents","sub_scenes"]

class Campaign( object ):
    """Barebones campaign featuring functionality used by other pbge units."""
    def __init__( self, name = "BobDwarf19", explo_class=None, home_base=None ):
        # home_base is a (scene,entrance) tuple to be used in case no scene is found.
        self.name = name
        self.party = list()
        self.scene = None 
        self.entrance = None
        self.destination = None
        self.contents = container.ContainerList()
        self.scripts = container.ContainerList()
        self.uniques = set()
        self.explo_class = explo_class
        self.day = 1
        self.campdata = dict()
        # home_base is a scene where the party gets sent if they get utterly defeated in combat.
        # It must have scripts in place to restore the party or end the game.
        self.home_base = home_base


    def save( self ):
        with open( util.user_dir( "rpg_" + self.name + ".sav" ) , "wb" ) as f:
            pickle.dump( self , f, -1 )

    def delete_save_file( self ):
        os.remove(util.user_dir("rpg_{}.sav".format(self.name)))

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

    def get_dialogue_offers_and_grammar(self, npc):
        npc_offers = list()
        pgram = dialogue.grammar.Grammar()
        for p in self.active_plots():
            npc_offers += p.get_dialogue_offers(npc, self)
            nugram = p.get_dialogue_grammar(npc, self)
            if nugram:
                pgram.absorb(nugram)
        return npc_offers, pgram

    def all_plots(self):
        for ob in self.all_contents(self):
            if hasattr(ob,"scripts"):
                for p in ob.scripts:
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
        raise NotImplementedError("Method place_party needs custom implementation.")

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
            elif not self.first_active_pc() and self.home_base:
                # IMPORTANT: If home_base is defined, it MUST have some kind of code to deal with a defeated party!
                # Otherwise this is gonna get stuck in an endless loop of going to home base over and over.
                self.remove_party_from_scene()
                self.scene, self.entrance = self.home_base
                self.place_party()

    def dump_info( self ):
        # Print info on all scenes in this world.
        for c in self.contents:
            c.dump_info()

    def all_contents( self, thing, check_subscenes=True, search_path=ALL_CONTENTS_SEARCH_PATH ):
        """Iterate over this thing and all of its descendants."""
        yield thing
        for cs in search_path:
            if hasattr( thing, cs ):
                for t in getattr(thing,cs):
                    if check_subscenes or not isinstance( t, scenes.Scene ):
                        for tt in self.all_contents( t, check_subscenes ):
                            yield tt
