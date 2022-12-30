#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2021 Joseph Hewitt <pyrrho12@yahoo.ca>
#
# 

from . import my_state
from . import container
from . import util, dialogue
import pickle
import os
from . import scenes, challenges

ALL_CONTENTS_SEARCH_PATH = ["contents", "sub_scenes"]


class Campaign(object):
    """Barebones campaign featuring functionality used by other pbge units."""

    def __init__(self, name="BobDwarf19", explo_class=None, home_base=None):
        # home_base is a (scene,entrance) tuple to be used in case no scene is found.
        self.name = name
        self.party = list()
        self.scene = None
        self._destination = None
        self.contents = container.ContainerList()
        self.scripts = container.ContainerList()
        self.uniques = set()
        self.explo_class = explo_class
        self.time = 1
        self.campdata = dict()
        # home_base is a scene where the party gets sent if they get utterly defeated in combat.
        # It must have scripts in place to restore the party or end the game.
        self.home_base = home_base
        self.entered_via = None

    def __setstate__(self, state):
        # For saves from v0.946 or earlier, rename day to time.
        if "day" in state:
            state["time"] = state["day"]
            del state["day"]
        # For saves from V0.941 or earlier, make sure there's an entered_via waypoint. Or not.
        self.__dict__.update(state)
        if "entered_via" not in state:
            self.entered_via = None

    def go(self, dest_wp: scenes.waypoints.Waypoint):
        dest_scene = dest_wp.scene
        if dest_scene:
            self._destination = dest_wp

    def _really_go(self):
        dest_wp = self._destination
        dest_scene = self._destination.scene

        if self.scene:
            self.remove_party_from_scene()
        self.scene, self._destination = dest_scene, None
        self.place_party(dest_wp)
        self.entered_via = dest_wp

    def save(self):
        with open(util.user_dir(util.sanitize_filename("rpg_" + self.name + ".sav")), "wb") as f:
            pickle.dump(self, f, 4)

    def delete_save_file(self, del_name=None):
        name = del_name or self.name
        if os.path.exists(util.user_dir("rpg_{}.sav".format(name))):
            os.remove(util.user_dir("rpg_{}.sav".format(name)))

    def keep_playing_campaign(self):
        # The default version of this method will keep playing forever.
        # You're probably gonna want to redefine this in your subclass.
        return True

    def keep_playing_scene(self):
        return not self._destination

    def has_a_destination(self):
        return self._destination

    def active_plots(self):
        for p in self.scene.scripts:
            if p.active:
                yield p
        for p in self.scripts:
            if p.active:
                yield p

    def get_active_challenges(self):
        my_challenges = set()
        if self.scene:
            for p in self.active_plots():
                for k, v in p.elements.items():
                    if isinstance(v, challenges.Challenge) and v.active:
                        my_challenges.add(v)
        return my_challenges

    def get_active_resources(self):
        my_resources = set()
        for p in self.active_plots():
            for k, v in p.elements.items():
                if isinstance(v, challenges.Resource) and v.active:
                    my_resources.add(v)
        return my_resources

    def get_dialogue_offers_and_grammar(self, npc):
        npc_offers = list()
        pgram = dialogue.grammar.Grammar()
        for p in self.active_plots():
            npc_offers += p.get_dialogue_offers(npc, self)
            nugram = p.get_dialogue_grammar(npc, self)
            if nugram:
                pgram.absorb(nugram)

        my_challenges = self.get_active_challenges()
        for c in my_challenges:
            npc_offers += c.get_dialogue_offers(npc, self)
            pgram.absorb(c.grammar)

        for r in self.get_active_resources():
            npc_offers += r.get_dialogue_offers(npc, self, my_challenges)

        return npc_offers, pgram

    def all_plots(self):
        for ob in self.all_contents(self):
            if hasattr(ob, "scripts"):
                for p in ob.scripts:
                    yield p

    def check_trigger(self, trigger, thing=None):
        # Something is happened that plots may need to react to.
        # Only check a trigger if the campaign has been constructed.
        if self.scene:
            if trigger == "UPDATE":
                self._update_plots()
            for p in self.active_plots():
                p.handle_trigger(self, trigger, thing)

    def expand_puzzle_menu(self, thing, thingmenu):
        # Something is happened that plots may need to react to.
        for p in self.active_plots():
            p.modify_puzzle_menu(self, thing, thingmenu)

        my_challenges = self.get_active_challenges()
        for c in my_challenges:
            c.modify_puzzle_menu(self, thing, thingmenu)

        for r in self.get_active_resources():
            r.modify_puzzle_menu(self, thing, thingmenu, my_challenges)

        if not thingmenu.items:
            thingmenu.add_item("[Continue]", None)
        else:
            thingmenu.sort()
            thingmenu.add_alpha_keys()

    def place_party(self, entrance):
        """Stick the party close to the waypoint."""
        raise NotImplementedError("Method place_party needs custom implementation.")

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        pass

    def remove_party_from_scene(self):
        for pc in self.party:
            pc.pos = None
            if pc in self.scene.contents:
                self.scene.contents.remove(pc)

    def play(self):
        while self.keep_playing_campaign() and not my_state.got_quit:
            self._update_plots()
            exp = self.explo_class(self)
            exp.go()
            if self._destination:
                self._really_go()
            elif not exp.no_quit:
                # If the player quit in exploration mode, exit to main menu.
                break
            elif not self.first_active_pc() and self.home_base:
                # IMPORTANT: If home_base is defined, it MUST have some kind of code to deal with a defeated party!
                # Otherwise this is gonna get stuck in an endless loop of going to home base over and over.
                self.remove_party_from_scene()
                self.go(self.home_base)
                self._really_go()

    def _update_plots(self):
        # Perform maintenance on all plots. This happens in between scenes, so don't do anything screwy during
        # the update. Mostly this is for removing expired plots from the campaign.
        for p in self.all_plots():
            p.update(self)

    def dump_info(self):
        # Print info on all scenes in this world.
        for c in self.contents:
            c.dump_info()

    def all_contents(self, thing, check_subscenes=True, search_path=None):
        """Iterate over this thing and all of its descendants."""
        search_path = search_path or ALL_CONTENTS_SEARCH_PATH
        yield thing
        for cs in search_path:
            if hasattr(thing, cs):
                for t in getattr(thing, cs):
                    if check_subscenes or not isinstance(t, scenes.Scene):
                        for tt in self.all_contents(t, check_subscenes):
                            yield tt

    def get_memos(self):
        mymemos = [p.memo for p in self.active_plots() if p.memo]
        for c in self.get_active_challenges():
            cmemo = c.get_memo()
            if cmemo:
                mymemos.append(cmemo)
        mymemos.sort(key=lambda m: str(m))
        return mymemos
