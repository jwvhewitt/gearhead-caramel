import copy
from . import grammar
from .. import my_state, default_border, frects, draw_text, rpgmenu, util
import random

# Basic context tags.

INFO = "INFO"  # INFO: The NPC gives the PC some information.
#       The data property should contain "subject"


# Configuration constants- fill out these lists with game-specific stuff.

STANDARD_OFFERS = list()
STANDARD_REPLIES = list()

# Generic offers are added to every conversation. Things like saying goodbye.
GENERIC_OFFERS = list()

# Grammar Builder is a function with parameters (mygram,camp,npc,pc)
# It fills mygram with the default grammar for this game + context.
GRAMMAR_BUILDER = None


class ContextTag(tuple):
    def matches(self, other):
        # A context tag matches self if each level defined in self matches
        # the equivalent level in other. Note that this is not reciprocal-
        # If of different lengths, the short can match the long but the long
        # won't match the short.
        return self[0:len(self)] == other[0:len(self)]


class Cue(object):
    # An empty node, waiting to be filled with a randomly selected Offer.
    def __init__(self, context):
        self.context = ContextTag(context)

    def get_context_set(self):
        # Get the set of all context tags used by this Cue. Since a cue doesn't
        # link to anything else, that would be its own context and nothing else.
        return set([self.context])

    def get_cue_list(self):
        # Get the set of all cues. Since this is a cue, return itself.
        return [self, ]


# The two parts of a conversation use improv theatre terminology-
# an Offer is a line spoken by the NPC, a Reply is the PC's response.

class Offer(object):
    # An Offer is a single line spoken by the NPC, along with its context tag,
    # effect, and a list of replies.
    # "effect" is a function that takes the campaign as its parameter. Called after dialogue selection is made.
    # "subject" is an identifier that limits conversation branches.
    # "subject_start" marks this offer as the entry point for a subject; it can be branched to from a different subject
    # "no_repeats" means this offer can't be replied by an offer with the same context + subject
    # "dead_end" means this offer will have no automatically generated replies
    # "custom_menu_fun" is a function that takes (reply,menu,pcgrammar) and alters the menu, returning the item added.
    # "is_generic" tells whether or not this is a generic offer
    # "allow_generics" allows generic offers to link from this one
    # "skill_info" is a string describing what skills or whatever were used to access this message (or which will be
    #   tested if this message is chosen). Printed as a suffix to the reply.
    # "prefx" is a callable with signature (camp) that is called as soon as this offer is displayed.
    # "data" is a dict holding strings that may be requested by format.
    def __init__(
            self, msg, context=(), effect=None, replies=None, subject=None, subject_start=False, no_repeats=False,
            dead_end=False, data=None, custom_menu_fun=None, is_generic=False, allow_generics=True, skill_info=None,
            prefx=None
    ):
        self.msg = msg
        self.context = ContextTag(context)
        self.effect = effect
        self.subject = subject
        self.data = data or dict()
        self.subject_start = subject_start
        self.no_repeats = no_repeats
        self.dead_end = dead_end
        self.custom_menu_fun = custom_menu_fun
        self.is_generic = is_generic
        self.allow_generics = allow_generics
        self.skill_info = skill_info
        self.prefx = prefx

        if not replies:
            self.replies = list()
        else:
            self.replies = list(replies)

    def get_context_set(self):
        # Get the set of all context tags used by this offer and any offers or
        # cues linked by the replies.
        context = set([self.context])
        for e in self.replies:
            context = context | e.destination.get_context_set()
        return context

    def get_cue_list(self):
        # Get the set of all offers which are not really offers, but are just
        # cues waiting to be filled.
        cues = list()
        for e in self.replies:
            cues += e.destination.get_cue_list()
        return cues

    def format_text(self, mygrammar):
        text = self.msg
        try:
            if self.data:
                text = text.format(**self.data)
        except KeyError as err:
            raise RuntimeError("Text Key Missing: {}".format(text)) from err
        text = grammar.convert_tokens(text, mygrammar)
        try:
            if self.data:
                text = text.format(**self.data)
        except KeyError as err:
            raise RuntimeError("Text Key Missing: {}".format(text)) from err
        return text

    def __str__(self):
        return self.msg

    def __repr__(self):
        return self.msg


class Reply(object):
    # A Reply is a single line spoken by the PC, leading to a new offer
    def __init__(self, msg, destination: Offer = None, context=()):
        self.msg = msg
        self.destination = destination
        self.context = ContextTag(context)

    def get_context_set(self):
        # Get the set of contexts this link. This is going to depend on the links
        # in the replies.
        return self.destination.get_context_set()

    def __str__(self):
        return self.msg

    def format_text(self, mygrammar):
        text = self.msg
        if self.destination:
            text = text.format(**self.destination.data)
        text = grammar.convert_tokens(text, mygrammar)
        if self.destination:
            text = text.format(**self.destination.data)
        return text

    def apply_to_menu(self, mymenu, pcgrammar, pc):
        if self.destination and self.destination.custom_menu_fun:
            myitem = self.destination.custom_menu_fun(self, mymenu, pcgrammar)
        else:
            text = self.format_text(pcgrammar)
            myitem = mymenu.add_item(text, self.destination, "{}: {}".format(pc, text))
        if myitem and self.destination.skill_info and util.config.getboolean("GENERAL",
                                                                             "show_convo_skills") and hasattr(myitem,
                                                                                                              "msg"):
            myitem.msg = myitem.msg + self.destination.skill_info


class SimpleVisualizer(object):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = frects.Frect(-150, -100, 300, 100)
    MENU_AREA = frects.Frect(-150, 20, 300, 80)

    def __init__(self):
        self.text = ''

    def render(self):
        if my_state.view:
            my_state.view()
        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(my_state.small_font, self.text, text_rect)
        default_border.render(self.MENU_AREA.get_rect())

    def get_menu(self):
        return rpgmenu.Menu(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h, border=None,
                            predraw=self.render)


class DynaConversation(object):
    # As above, but instead of building the whole conversation at
    # the start we're gonna build the set of replies when a node
    # is entered.
    def __init__(self, camp, npc, pc, start, visualizer=None):
        self.camp = camp
        self.npc = npc
        self.pc = pc
        if not visualizer:
            visualizer = SimpleVisualizer()
        self.visualizer = visualizer
        self.root = None
        self.npc_offers = list()
        self.npc_grammar = grammar.Grammar()
        self.pc_grammar = grammar.Grammar()
        # Locate the initial offer, but don't build it.
        self._get_dialogue_data()
        # If the start is a cue, change it to an offer.
        if isinstance(start, Cue):
            self.root = self._get_offer_for_cue(start, self.npc_offers)
        else:
            self.root = start

    def _get_dialogue_data(self):
        self.npc_offers = list()
        self.pc_grammar.clear()
        self.npc_grammar.clear()
        if GRAMMAR_BUILDER:
            GRAMMAR_BUILDER(self.npc_grammar, self.camp, self.npc, self.pc)
            GRAMMAR_BUILDER(self.pc_grammar, self.camp, self.pc, self.npc)
        self.pc_grammar.absorb({"[pc]": [str(self.pc), ], "[npc]": [str(self.npc)]})
        self.npc_grammar.absorb({"[pc]": [str(self.pc)], "[npc]": [str(self.npc)]})

        self.npc_offers, pgram = self.camp.get_dialogue_offers_and_grammar(self.npc)
        if pgram:
            self.npc_grammar.absorb(pgram)
            self.pc_grammar.absorb(pgram)

        for goff in GENERIC_OFFERS:
            # Add a copy of this to the npc_offers if there isn't
            # currently an offer with a compatible tag.
            if not self._get_offer_for_cue(goff, self.npc_offers, False):
                self.npc_offers.append(copy.deepcopy(goff))

    def _find_std_offer_to_match_cue(self, cue_in_question):
        # Find an exchange in the standard exchanges list which matches the provided
        # cue and may possibly branch to one of the provided offers.
        # Return a new instance of the good exchange found.
        candidates = []

        for e in STANDARD_OFFERS:
            # We want to check the links from this exchange against the offers on tap.
            # But we don't need to find a waiting offer for the root exchange.
            e_cues = e.get_cue_list()

            if cue_in_question.context.matches(e.context):
                candidates.append(e)
        if candidates:
            return copy.deepcopy(random.choice(candidates))
        else:
            return None

    def _get_offer_for_cue(self, cue, candidates, allow_standards=True):
        short_list = [c for c in candidates if cue.context.matches(c.context)]
        if short_list:
            # Great! just return one of these.
            return random.choice(short_list)
        elif allow_standards:
            # No good. Try one of the standard offers instead.
            return self._find_std_offer_to_match_cue(cue)

    def _get_reply_for_offers(self, off1: Offer, off2: Offer):
        # First, make sure this offer even can be connected to the other offer.
        if off1.no_repeats and off1.subject == off2.subject and off1.context == off2.context:
            # Off2 repeats the subject and context of Off1 when we've been told to avoid repeats.
            return None

        elif off2.is_generic and not off1.allow_generics:
            # Off2 is a generic reply and we've been asked to avoid generics.
            return None

        elif not (off1.subject == off2.subject or off2.subject is None or str(off2.subject) in off1.msg or off2.subject_start):
            # There is a subject mismatch between the two offers. Don't connect them.
            return None

        else:
            # First, check for replies that match off1's context perfectly.
            candidates = [
                r for r in STANDARD_REPLIES if off1.context.matches(r.context) and r.destination.context.matches(off2.context)
            ]
            if not candidates:
                candidates = [r for r in STANDARD_REPLIES if
                          r.context.matches(off1.context) and r.destination.context.matches(off2.context)]
            if candidates:
                return copy.deepcopy(random.choice(candidates))

    def build(self, current):
        # Renew the data
        self._get_dialogue_data()
        # If the current is a cue, change it to an offer.
        if isinstance(current, Cue):
            self.root = self._get_offer_for_cue(current, self.npc_offers)
        else:
            self.root = current
        if self.root in self.npc_offers:
            self.npc_offers.remove(self.root)
        # Process the root offer message.
        self.root.msg = self.root.format_text(self.npc_grammar)

        # If the current offer has replies, fill them first.
        for r in self.root.replies:
            if isinstance(r.destination, Cue):
                r.destination = self._get_offer_for_cue(r.destination, self.npc_offers)
                if r.destination in self.npc_offers:
                    self.npc_offers.remove(r.destination)

        if not self.root.dead_end:
            # Shuffle self.npc_offers.
            random.shuffle(self.npc_offers)

            # Go through self.npc_offers, adding any offers that connect to current
            for o in self.npc_offers:
                r = self._get_reply_for_offers(self.root, o)
                if r:
                    self.root.replies.append(r)
                    r.destination = o

        # Add any needed standards: Goodbye, Can I ask something else
        # That's it.

    def converse(self):
        # coff is the "current offer"
        coff = self.root
        while coff:
            if coff.prefx:
                coff.prefx(self.camp)
            self.build(coff)
            self.visualizer.text = coff.msg
            my_state.record_message("{}: {}".format(self.npc, coff.msg))
            mymenu = self.visualizer.get_menu()
            for i in coff.replies:
                i.apply_to_menu(mymenu, self.pc_grammar, self.pc)
            if self.visualizer.text and not mymenu.items:
                mymenu.add_item("[Continue]", None)
            else:
                mymenu.sort()
            nextfx = coff.effect

            coff = mymenu.query()
            if coff:
                my_state.record_message(mymenu.get_current_desc())

            if nextfx:
                nextfx(self.camp)


def list_nouns(mylist, conjunction="and"):
    # A utility function to turn a list of whatever into a grammatically correct phrase.
    mywords = [str(thing) for thing in mylist]
    if len(mywords) > 2:
        return ", ".join(mywords[:-1]) + ", {} {}".format(conjunction, mywords[-1])
    elif len(mywords) > 1:
        return "{} {} {}".format(mywords[0], conjunction, mywords[1])
    elif mywords:
        return mywords[0]
    else:
        return "nothing"
