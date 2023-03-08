# After years of building 'em manually, I have decided to create a standard interface for stories built using Propp's
# Ratchet. This is a random story technique that has been used since GearHead 1.
import collections
import random
from . import util

# Not a grapg0- use algebra. Find ending states (as current) and then select a beginning state. Add components which
# purposefully move story state closer to desired outcome- or which branch to other outcone. Loss is an issue but I think
# it will work. Make propp states tell their own stories. Or at least provide grammar to describe their contribution to
# overall story. Algebra- remember each state is a number that only goes up. Make numbers go up. Maybe add standard
# roles to propp state- I rejected that idea before, but may be useful. Not as simple as enemy/ally. Or maybe just
# enemy/ally.
# MAYBE_NOT = "MAYBE_NOT"     # Faction/character can be convinced to oppose this outcome
from . import plots


STORY_ELEMENT = "STORY"

DEFAULT_STORY_PLOT = "STORY_PLOT"
DEFAULT_STORY_CONCLUSION = "STORY_CONCLUSION"


class ProppNarrateme:
    def __init__(self, name, tags=(), grammar=None):
        self.name = name
        self.tags = set(tags)
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, ProppNarrateme):
            return self.name == other.name and self.tags == other.tags

    def __hash__(self):
        return hash((self.name, self.tags))


class ProppKey:
    def __init__(self, name, narratemes=(), max_starting_state=0):
        self.name = name
        self.narratemes = tuple(narratemes)
        # Store CONSTs for all the narrateme values.
#        for numb, narr in enumerate(self.narratemes):
#            setattr(self, self._name_to_identifier(narr.name), numb)
        self.max_starting_state = max_starting_state

    def _name_to_identifier(self, name: str):
        mychars = list()
        name = name or "A"
        for c in name:
            if c.isalpha():
                mychars.append(c.upper())
            elif c.isdigit() and mychars:
                mychars.append(c)
            elif c.isspace() and mychars:
                mychars.append("_")
        myident = "".join(mychars)
        n = 1
        while hasattr(self, myident):
            # This is less efficient than caching the base name and then adding the number to the end. WGAFBF? If
            # the key is set up correctly, you shouldn't have two narratemes with the same name anyhow. Even if all
            # the narratemes have the same name the amount of time taken up by this loop will be tiny. So I'm not
            # going to worry about it. Also: Covid brain fog seems to be lifting.
            myident = "".join(mychars) + str(n)
            n += 1
        return myident

    def __eq__(self, other):
        if isinstance(other, ProppKey):
            return self.name == other.name and self.narratemes == other.narratemes

    def __hash__(self):
        return hash((self.name, self.narratemes))


class ProppValue:
    def __init__(self, narrateme, params=()):
        self.narrateme = narrateme
        self.elements = tuple(params)


class ProppState:
    def __init__(self, channels=None):
        # Channels is a dict in which the keys are ProppKey objects and the values are ProppValue objects
        self.channels = collections.defaultdict(ProppValue)
        if channels:
            self.channels.update(channels)


class ProppControl:
    def __init__(self, entry_state: ProppState, exit_states=None):
        self.entry_state = entry_state
        self.exit_states = dict()
        if exit_states:
            self.exit_states.update(exit_states)


class Story:
    # The base class for stories; probably should not be used by itself. See "InstantStory" and "OngoingStory" below.
    def __init__(self, state=None, plot_type=DEFAULT_STORY_PLOT, elements=None):
        self.state = state
        self.plot_type = plot_type
        self.elements = dict()
        if elements:
            self.elements.update(elements)


class OngoingStory(Story):
    # An ongoing story is a story that happens one episode at a time. The story may be called to generate a new
    # chapter whenever appropriate.
    def start_next_chapter(self):
        pass


class StoryPlot(plots.Plot):
    LABEL = DEFAULT_STORY_PLOT
    PROPP_CONTROL = ProppControl(ProppState())


