
import copy
import grammar
from .. import my_state,default_border,frects,draw_text,rpgmenu
import random


# Configuration constants- fill out these lists with game-specific stuff.

STANDARD_OFFERS = list()
STANDARD_REPLIES = list()

# Generic offers are added to every conversation. Things like saying goodbye.
GENERIC_OFFERS = list()

# Grammar Builder is a function with parameters (mygram,camp,npc,pc)
# It fills mygram with the default grammar for this game + context.
GRAMMAR_BUILDER = None


class ContextTag( tuple ):
    def matches( self, other ):
        # A context tag matches self if each level defined in self matches
        # the equivalent level in other. Note that this is not reciprocal-
        # If of different lengths, the short can match the long but the long
        # won't match the short.
        return self[0:len(self)] == other[0:len(self)]

class Cue(object):
    # An empty node, waiting to be filled with a randomly selected Offer.
    def __init__( self , context ):
        self.context = ContextTag(context)

    def get_context_set(self):
        # Get the set of all context tags used by this Cue. Since a cue doesn't
        # link to anything else, that would be its own context and nothing else.
        return set( [ self.context ] )

    def get_cue_list(self):
        # Get the set of all cues. Since this is a cue, return itself.
        return [ self, ]

# The two parts of a conversation use improv theatre terminology-
# an Offer is a line spoken by the NPC, a Reply is the PC's response.

class Offer(object):
    # An Offer is a single line spoken by the NPC, along with its context tag,
    # effect, and a list of replies.
    # "effect" is a function that takes the campaign as its parameter.
    # "subject" is an identifier that limits conversation branches.
    # "subject_start" marks this offer as the entry point for a subject
    # "dead_end" means this offer will have no automatically generated replies

    # "data" is a dict holding strings that may be requested by format.
    def __init__(self, msg, context=(), effect = None, replies = None, subject=None, subject_start=False, dead_end=False, data=None ):
        self.msg = msg
        self.context = ContextTag(context)
        self.effect = effect
        self.subject = subject
        self.data = data or dict()
        self.subject_start = subject_start
        self.dead_end = dead_end

        if not replies:
            self.replies = list()
        else:
            self.replies = list(replies)

    def get_context_set(self):
        # Get the set of all context tags used by this offer and any offers or
        # cues linked by the replies.
        context = set( [ self.context ] )
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

    def __str__(self):
        return self.msg
    def __repr__(self):
        return self.msg


class Reply(object):
    # A Reply is a single line spoken by the PC, leading to a new offer
    def __init__(self, msg, destination=None, context=() ):
        self.msg = msg
        self.destination = destination
        self.context = ContextTag(context)

    def get_context_set( self ):
        # Get the set of contexts this link. This is going to depend on the links
        # in the replies.
        return self.destination.get_context_set()

    def __str__(self):
        return self.msg

class SimpleVisualizer(object):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = frects.Frect(-150,-100,300,100)
    MENU_AREA = frects.Frect(-150,20,300,80)
    def __init__(self):
        self.text = ''
    def render(self):
        if my_state.view:
            my_state.view()
        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(my_state.small_font,self.text,text_rect)
        default_border.render(self.MENU_AREA.get_rect())
    def get_menu(self):
        return rpgmenu.Menu(self.MENU_AREA.dx,self.MENU_AREA.dy,self.MENU_AREA.w,self.MENU_AREA.h,border=None,predraw=self.render)

class DynaConversation(object):
    # As above, but instead of building the whole conversation at
    # the start we're gonna build the set of replies when a node
    # is entered.
    def __init__(self,camp,npc,pc,start,visualizer=None):
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
        #self._get_dialogue_data()
        self.build(start)

    def _get_dialogue_data( self ):
        self.npc_offers = list()
        self.pc_grammar.clear()
        self.npc_grammar.clear()
        if GRAMMAR_BUILDER:
            GRAMMAR_BUILDER(self.npc_grammar,self.camp,self.npc,self.pc)
            GRAMMAR_BUILDER(self.pc_grammar,self.camp,self.pc,self.npc)
        self.pc_grammar.absorb({"[pc]":[str(self.pc),], "[npc]":[str(self.npc)]})
        self.npc_grammar.absorb({"[pc]":[str(self.pc)], "[npc]":[str(self.npc)]})

        for p in self.camp.active_plots():
            self.npc_offers += p.get_dialogue_offers( self.npc, self.camp )
            pgram = p.get_dialogue_grammar( self.npc, self.camp )
            if pgram:
                self.npc_grammar.absorb( pgram )
                self.pc_grammar.absorb( pgram )
        for goff in GENERIC_OFFERS:
            # Add a copy of this to the npc_offers if there isn't
            # currently an offer with a compatible tag.
            if not self._get_offer_for_cue(goff,self.npc_offers,False):
                self.npc_offers.append(copy.deepcopy(goff))
                
    def _find_std_offer_to_match_cue( self, cue_in_question ):
        # Find an exchange in the standard exchanges list which matches the provided
        # cue and may possibly branch to one of the provided offers.
        # Return a new instance of the good exchange found.
        candidates = []

        for e in STANDARD_OFFERS:
            # We want to check the links from this exchange against the offers on tap.
            # But we don't need to find a waiting offer for the root exchange.
            e_cues = e.get_cue_list()

            if cue_in_question.context.matches( e.context ):
                candidates.append( e )
        if candidates:
            return copy.deepcopy( random.choice( candidates ) )
        else:
            return None

    def _get_offer_for_cue( self,cue,candidates,allow_standards=True):
        short_list = [c for c in candidates if cue.context.matches(c.context)]
        if short_list:
            # Great! just return one of these.
            return random.choice(short_list)
        elif allow_standards:
            # No good. Try one of the standard offers instead.
            return self._find_std_offer_to_match_cue(cue)

    def _get_reply_for_offers(self,off1,off2):
        candidates = [r for r in STANDARD_REPLIES if off1.context.matches(r.context) and r.destination.context.matches(off2.context)
                      and (off1.subject == off2.subject or off2.subject is None or off2.subject in off1.msg or off2.subject_start)]
        if candidates:
            return copy.deepcopy(random.choice(candidates))

    def build( self,current ):
        # Renew the data
        self._get_dialogue_data()
        # If the current is a cue, change it to an offer.
        if isinstance(current,Cue):
            self.root = self._get_offer_for_cue(current,self.npc_offers)
        else:
            self.root = current
        if self.root in self.npc_offers:
            self.npc_offers.remove(self.root)
        # Process the root offer message.
        self.root.msg = self.format_text( self.root.msg , self.npc_grammar, self.root )
        
        # If the current offer has replies, fill them first.
        for r in self.root.replies:
            if isinstance(r.destination,Cue):
                r.destination = self._get_offer_for_cue(r.destination,self.npc_offers)
                if r.destination in self.npc_offers:
                    self.npc_offers.remove(r.destination)

        if not self.root.dead_end:
            # Shuffle self.npc_offers.
            random.shuffle(self.npc_offers)

            # Go through self.npc_offers, adding any offers that connect to current
            for o in self.npc_offers:
                r = self._get_reply_for_offers(self.root,o)
                if r:
                    self.root.replies.append(r)
                    r.destination = o
            
        # Add any needed standards: Goodbye, Can I ask something else
        # That's it.

    def format_text( self, text, mygrammar, offer ):
        text = grammar.convert_tokens( text, mygrammar )
        if offer:
            text = text.format(**offer.data)
        return text

    def converse( self ):
        # coff is the "current offer"
        coff = self.root
        while coff:
            self.visualizer.text = self.format_text( coff.msg , self.npc_grammar, coff )
            mymenu = self.visualizer.get_menu()
            for i in coff.replies:
                mymenu.add_item( self.format_text( i.msg, self.pc_grammar, i.destination ), i.destination )
            if self.visualizer.text and not mymenu.items:
                mymenu.add_item( "[Continue]", None )
            else:
                mymenu.sort()
            nextfx = coff.effect

            coff = mymenu.query()

            if nextfx:
                nextfx( self.camp )
            if coff:
                self.build(coff)




