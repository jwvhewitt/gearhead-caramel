#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Offer: A line spoken by the NPC, with possible effects.
#   An Offer has a Context, which describes what kind of thing is being said.
# Reply: A line spoken by the PC, which leads to an Exchange.
# Cue: An empty space in a conversation waiting to be filled by an Offer.
#   Both Offers and Cues are described by a context value.
# Context: A value roughly describing the type of an offer/reply.


import random
import copy



class Context(object):
    # Basically, an enumerated type for conversation contexts.
    hello,misc,shop,mission,hint = range(5)

class Cue(object):
    # An empty node, waiting to be filled with randomly selected dialog.
    def __init__( self , context ):
        self.context = context

    def get_context_set(self):
        # Get the set of all context tags used by this Cue. Since a cue doesn't
        # link to anything else, that would be its own context and nothing else.
        return set( [ self.context ] )

    def get_cue_set(self):
        # Get the set of all cues. Since this is a cue, return itself.
        return set( [ self.context ] )


class Offer(object):
    # An Offer is a single line spoken by the NPC, along with its context tag,
    # effect, and a list of replies.
    def __init__(self, msg, context=Context.misc, effect = None, replies = None ):
        self.msg = msg
        self.context = context
        self.effect = effect

        if replies == None:
            self.replies = []
        else:
            self.replies = replies

    def get_context_set(self):
        # Get the set of all context tags used by this offer and any offers or
        # cues linked by the replies.
        context = set( [ self.context ] )
        for e in self.replies:
            context = context | e.destination.get_context_set()
        return context

    def get_cue_set(self):
        # Get the set of all offers which are not really offers, but are just
        # cues waiting to be filled.
        cues = set()
        for e in self.replies:
            cues = cues | e.destination.get_cue_set()
        return cues


class Reply(object):
    # A persona.Reply is a single line spoken by the PC, leading to a new exchange
    def __init__(self, msg, destination=None, context=Context.misc ):
        self.msg = msg
        self.destination = destination
        self.context = context

    def get_context_set( self ):
        # Get the set of contexts this link. This is going to depend on the links
        # in the replies.
        return self.destination.get_context_set()


standard_replies = []

Basic_To_Shop = Reply( "Do you have anything for sale?" , destination = Cue( Context.shop ) , context = Context.hello )

standard_replies.append( Basic_To_Shop )

standard_offers = []

Basic_Hello = Offer( msg = "Hi there!" , context = Context.hello )
Basic_Shop_Hello = Offer( msg = "Welcome to my store." , context = Context.hello , replies = [ Reply( "I'd like to see what you have." , destination = Cue( Context.shop ) ) ] )



standard_offers.append( Basic_Hello )
standard_offers.append( Basic_Shop_Hello )




def find_anchor_list( conversation , context_type ):
    # Find all offers in this conversation whose context matches the context_type.
    # One of these offers can be used as an anchor for attaching a new reply link
    # to the conversation.
    anchor_list = []
    if conversation.context == context_type:
        anchor_list.append( conversation )

    for r in conversation.replies:
        anchor_list += find_anchor_list( r.destination , context_type )

    return anchor_list

def find_anchor( conversation , context_type ):
    anchor_list = find_anchor_list( conversation , context_type )
    if len( anchor_list ) < 1:
        return None
    else:
        return random.choice( anchor_list )

def find_cue_list( conversation , context_type ):
    # Find a list of all cues in this conversation which match the context type.
    cue_list = []
    if isinstance( conversation , Cue ) and ( conversation.context == context_type ):
        cue_list.append( conversation )

    if isinstance( conversation , Offer ):
        for r in conversation.replies:
            cue_list += find_cue_list( r.destination , context_type )

    return cue_list

def find_cue( conversation , context_type ):
    cue_list = find_cue_list( conversation , context_type )
    if len( cue_list ) < 1:
        return None
    else:
        return random.choice( cue_list )


def find_offer_by_cues( cues , offers ):
    # Find an offer in this list which matches one of the provided cues.
    goffs = []
    for o in offers:
        if o.context in cues:
            goffs.append( o )
    if len( goffs ) > 0:
        return random.choice( goffs )
    else:
        return None

def list_context_set( offer_list ):
    # Given a list of offers, return the context of each of them.
    context_set = set()
    for o in offer_list:
        context_set.add( o.context )
    return context_set


def find_good_exchange( cues , offers ):
    # Find an exchange in the standard exchanges list which matches one of the provided cues
    # and may possibly branch to one of the provided offers.
    # Return a new instance of the good exchange found.
    candidates = []
    ofconset = list_context_set( offers )


    for e in standard_offers:
        # We want to check the links from this exchange against the offers on tap.
        # But we don't need to find a waiting offer for the root exchange.
        e_context = e.get_context_set()
        e_context.remove( e.context )

        if ( e.context in cues ) and ( e_context <= ofconset ):
            candidates.append( e )
    if len( candidates ) > 0:
        return copy.deepcopy( random.choice( candidates ) )
    else:
        return None

def replace_all_refs( conversation , cue , exchange ):
    # Searching through the conversation tree, replace all references to cue
    # with exchange.
    for r in conversation.replies:
        if r.destination is cue:
            r.destination = exchange
        elif isinstance( r.destination , Offer ):
            replace_all_refs( r.destination , cue , exchange )


def build_conversation( start,offers ):
    # Given a list of offers, construct a conversation which uses as many of
    # them as possible.
    # Each exchange added to the conversation must link from an exchange already
    # in the conversation. The start parameter provides a starting state from
    # which the first exchange will be generated.
    # "start" can be either a cue or an offer.
    keepgoing = True
    root = start

    while keepgoing:
        # If there are any unconverted context cues, convert those to new
        # offers.
        keep_seeking_cues = True
        while keep_seeking_cues:
            cues = root.get_cue_set()

            if len(cues) > 0:
                # We have cues to convert. Find a matching offer for one cue,
                # then add a new exhange.
                o = find_offer_by_cues( cues , offers )
                if o != None:
                    exc = copy.deepcopy( o )
                    offers.remove( o )
                else:
                    exc = find_good_exchange( cues , offers )

                # We now have an exchange. Find the cue it will replace.
                cue = find_cue( root , exc.context )
                if cue is root:
                    root = exc
                else:
                    replace_all_refs( root , cue , exc )
            else:
                keep_seeking_cues = False


        # If there are any unlinked offers, attempt to add some new links.

        # Start by determining the set of anchor contexts (those already part of
        # the conversation structure) and unlinked contexts (those not yet added
        # to the conversation).
        anchors = root.get_context_set()
        unlinked = list_context_set( offers )

        # Check through the list of standard links to see which ones match our
        # available anchors and unlinked offers.
        possible_links = []
        for l in standard_replies:
            if ( l.context in anchors ) and ( l.get_context_set() <= unlinked ):
                possible_links.append( l )

        if len( possible_links ) > 0:
            l = random.choice( possible_links )

            # We have a link. Add it to our structure.
            # Find a place where it can link
            a = find_anchor( root , l.context )
            a.replies.append( copy.deepcopy( l ) )
        else:
            keepgoing = False

    return root

def print_exchange( exc , header = "" ):
    print header + 'NPC: ' + exc.msg
    for r in exc.replies:
        print header + '  PC: ' + r.msg
        print_exchange( r.destination , header + '    ' )

if __name__=='__main__':
    O1 = Offer( "This is my shop. There's not much here yet." , context = Context.shop )
    O2 = Offer( "Hello. This is manual helloism." , context = Context.hello )

    offers = [O1]

    Convo = build_conversation( Cue( Context.hello ) , offers )
    print_exchange( Convo )


