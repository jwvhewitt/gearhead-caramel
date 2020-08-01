import pbge
from pbge import plots
import random
import inspect
from . import GHNarrativeRequest, PLOT_LIST, CARDS_BY_NAME

ME_TAROTPOSITION = "TAROT_POSITION"
ME_AUTOREVEAL = "ME_AUTOREVEAL" # If this element is True, card is generated during adventure + doesn't need full init
ME_SOCKET = "ME_SOCKET"
ME_CARD = "ME_CARD"

CONSEQUENCE_WIN = "Consequence_Win"
CONSEQUENCE_LOSE = "Consequence_Lose"

# Action Trigger Keys
# These store functions that get called to generate dialogue, alter puzzle menus, or whatever
# when an interaction is activated.
AT_GET_DIALOGUE_OFFERS = "AT_GET_DIALOGUE_OFFERS"
# Params: this_card, other_card, npc, camp, interaction
# Returns: list of offers for npc
AT_ALTER_ALPHA_PUZZLE_MENU = "AT_ALTER_ALPHA_PUZZLE_MENU"
AT_ALTER_BETA_PUZZLE_MENU = "AT_ALTER_BETA_PUZZLE_MENU"
# The key is (AT_ALTER_[x]_PUZZLEMENU,puzzle_item_element_id)
# Params: this_card,other_card,camp,thing,thingmenu,interaction

# For every signal that a tarot card can catch, it should spawn a listener plot to listen for
# the signal and to call the consequence/fail state depending on what happens.


class ElementPasser(dict):
    def __init__(self,*args):
        # Initialize this dict with a list of element names to be passed with the signal.
        # The keys are the element names given to the socket, the values are the names from
        # the sending tarot card. If you pass a tuple, index 0 is the name passed to the
        # socket and index 1 is the element name from the sending plot. Otherwise these are
        # assumed to be the same.
        super().__init__()
        for arg in args:
            if isinstance(arg,tuple):
                self[arg[0]] = arg[1]
            else:
                self[arg] = arg
    def get_elements(self,card):
        passdict = dict()
        for k,v in self.items():
            passdict[k] = card.elements.get(v,None)
        return passdict


class TarotSignal(object):
    def __init__(self,signal_type,signal_elements=()):
        self.signal_type = signal_type
        self.signal_elements = ElementPasser(*signal_elements)
    def loosely_matches(self,other_sig):
        # Returns True if other_sig provides all the element names sought by this signal.
        return self.signal_type == other_sig.signal_type and all(k in other_sig.signal_elements for k in self.signal_elements.keys())
    def get_real_elements(self,card):
        my_ele = dict()
        for k,v in self.signal_elements.items():
            my_ele[k] = card.elements.get(v)
        return my_ele
    def matches(self,sig_card,socket_sig,socket_elements):
        my_ele = self.get_real_elements(sig_card)
        return self.signal_type == socket_sig.signal_type and all(my_ele.get(k) == socket_elements.get(k) for k in socket_elements.keys())


class TarotSocket(object):
    # Each interaction held by a tarot card needs a listener plot.
    def __init__(self,listener_type,signal_sought,consequences=None):
        self.listener_type = listener_type
        self.signal_sought = signal_sought
        self.consequences = dict()
        if consequences:
            self.consequences.update(consequences)

    def list_possible_outcomes(self):
        return [con.new_card_name for con in self.consequences.values() if hasattr(con,"new_card_name")]

    def get_potential_signals(self, original_card, target_type):
        # Return True if one of original_card's signals can activate this socket, and if the target_type
        # is found as one of this socket's consequences.
        if target_type in self.list_possible_outcomes():
            return [sig for sig in original_card.SIGNALS if self.signal_sought.loosely_matches(sig)]

    def get_activating_signals(self,card,camp):
        # Return a list of (card,signal) tuples that activate this socket.
        actsig = list()
        if card.visible:
            socket_ele = self.signal_sought.get_real_elements(card)
            for other_card in camp.active_tarot_cards():
                if other_card.visible:
                    for sig in other_card.SIGNALS:
                        if sig.matches(other_card,self.signal_sought,socket_ele):
                            # A connection is made!
                            actsig.append((other_card,sig))
        return actsig

    def get_transforming_consequence(self,target_card_name):
        candy = [con for con in self.consequences.values() if hasattr(con,"new_card_name"
                                                                      ) and con.new_card_name == target_card_name]
        if candy:
            return random.choice(candy)


class TarotTransformer(object):
    # One possible consequence of a tarot interaction.
    auto_params = ("METROSCENE", "METRO", "MISSION_GATE")
    def __init__(self, new_card_name, this_card_params=(), other_card_params=(),
                 auto_params=("METROSCENE","METRO","MISSION_GATE")):
        # new_card_name is the name of the tarot card to transform this card to
        # this_card_params is a list of parameters to copy from the this_card (the card this interaction belongs to)
        # other_card_params is a list of parameters to copy from the other_card (the card triggering this interaction)
        self.new_card_name = new_card_name
        self.this_card_params = ElementPasser(*this_card_params)
        self.other_card_params = ElementPasser(*other_card_params)
        self.auto_params = auto_params

    def __call__(self, camp, this_card, other_card=None):
        """

        :type this_card: TarotCard
        """
        # Activating a transformation gives XP.
        camp.dole_xp(100)

        nart = GHNarrativeRequest(camp, plot_list=PLOT_LIST)
        pstate = pbge.plots.PlotState()
        pstate.elements[ME_AUTOREVEAL] = True
        pstate.rank = this_card.rank
        for p in self.auto_params:
            pstate.elements[p] = this_card.elements.get(p)
        pstate.elements.update(self.this_card_params.get_elements(this_card))
        pstate.elements.update(self.other_card_params.get_elements(other_card))

        newcard = nart.request_tarot_card_by_name(self.new_card_name, pstate)
        if not newcard:
            pbge.alert("New tarot card failed for {}".format(self.new_card_name))
        else:
            newcard.tarot_position = this_card.tarot_position
            nart.story.visible = True
            nart.build()
            if other_card:
                other_card.invoke(camp,this_card)
            this_card.end_plot(camp,True)


class TarotCard(plots.Plot):
    LABEL = "TAROT"
    UNIQUE = False
    scope = "METRO"
    TAGS = ()
    SIGNALS = ()
    SOCKETS = ()
    NEGATIONS = ()
    ONE_USE = True
    AUTO_MEMO = None

    def __init__(self, nart, pstate):
        self.tarot_position = pstate.elements.get(ME_TAROTPOSITION,None)
        self.visible = False
        super().__init__(nart, pstate)

        # Add the socket-listeners
        for sock in self.SOCKETS:
            if sock.listener_type:
                self.add_sub_plot(nart,sock.listener_type,spstate=plots.PlotState(elements={ME_SOCKET:sock,ME_CARD:self}).based_on(self))

        # IF auto-revealed, activate the memo.
        if self.elements.get(ME_AUTOREVEAL) and self.AUTO_MEMO:
            self.memo = self.AUTO_MEMO.format(**self.elements)

    def get_negations(self, num_neg=2):
        # Return a list of tarot cards that this card can turn into to negate itself.
        try:
            return random.sample(self.NEGATIONS, num_neg)
        except ValueError:
            return list(self.NEGATIONS)

    def reveal(self,camp):
        self.visible = True
        camp.dole_xp(50)
        camp.check_trigger("UPDATE")

    def invoke(self,camp,other_card):
        # This tarot card has been invoked. Deal with it.
        if self.ONE_USE:
            self.end_plot(camp,True)

    def REVEAL_WIN(self,camp):
        # Always add reveal plots with the ID "REVEAL" so this will work.
        self.reveal(camp)
        if self.AUTO_MEMO:
            self.memo = self.AUTO_MEMO.format(**self.elements)


class CardDeactivator(object):
    # Uses the same signature as the above, but only deactivates the card.
    def __call__(self,camp,alpha_card,beta_card=None,transform_card=None):
        """

        :type alpha_card: TarotCard
        """
        if transform_card:
            transform_card.active = False


class CardCaller(object):
    # A utility class for calling consequences along with their cards.
    # Note that alpha and beta are meant to be the alpha and beta cards for a consequence, but feel free to abuse
    # this class by sticking any old data in there.
    def __init__(self, alpha, beta, camp_card_fun, kwargs=None):
        self.alpha = alpha
        self.beta = beta
        self.camp_card_fun = camp_card_fun
        self.kwargs = dict()
        if kwargs:
            self.kwargs.update(kwargs)
    def __call__(self,camp):
        self.camp_card_fun(camp, self.alpha, self.beta, **self.kwargs)



class ProtoCard(object):
    def __init__(self, card, elements=None):
        self.card = card
        self.elements = dict()
        if elements:
            self.elements.update(elements)


class Constellation(object):
    def __init__(self, nart, root_plot, root_card, dest_card_name=None, steps=2):
        print(root_card)
        self.element_lookup = dict()
        dest_card_class = CARDS_BY_NAME[dest_card_name]
        if dest_card_class:
            possible_cards = self.get_protocards_that_change_this_one(root_card, dest_card_class.__name__, nart)
        else:
            possible_cards = [ProtoCard(root_card), ]
        if possible_cards:
            initial_cards = self.generate_puzzle_sequence(nart, [random.choice(possible_cards)], steps=steps)
            if initial_cards:
                # Add these cards to the adventure.
                for pcard in initial_cards:
                    pstate = pbge.plots.PlotState().based_on(root_plot)
                    for k, v in list(pcard.elements.items()):
                        # Copy any known elements to this tarot plot.
                        elem = self.element_lookup.get(v)
                        if elem:
                            pstate.elements[k] = elem
                    tcplot = nart.init_tarot_card(root_plot, pcard.card, pstate)
                    for k, v in list(pcard.elements.items()):
                        # Copy any newly defined elements to the lookup table.
                        if v not in self.element_lookup:
                            elem = tcplot.elements.get(k)
                            if elem:
                                self.element_lookup[v] = elem

    def copy_elements(self, source_proto, dest_proto, epass, reverse=False):
        if epass:
            for ekey,eval in epass.items():
                # ekey is the element's ID in dest, eval is the element's ID in source
                # Most of the time these will be the same, but not necessarily.
                if reverse:
                    ekey,eval = eval,ekey
                if ekey in dest_proto.elements:
                    pass
                elif eval in source_proto.elements:
                    # This is an already-defined key. Copy the code over.
                    dest_proto.elements[ekey] = source_proto.elements[eval]
                else:
                    # This is a new key. Give the element a name, and store it in element_lookup if possible.
                    dest_proto.elements[ekey] = (source_proto, eval)
                    source_proto.elements[eval] = (source_proto, eval)

                    if hasattr(source_proto.card, "elements") and eval in source_proto.card.elements:
                        self.element_lookup[(source_proto, eval)] = source_proto.card.elements[eval]

    def get_protocards_that_change_this_one(self, original_card, target_type, nart):
        # Return a list of cards that will change this one into another type.
        mylist = list()
        original_proto = ProtoCard(original_card)
        for tc in nart.plot_list[original_card.LABEL]:
            for sock in original_card.SOCKETS:
                signals = sock.get_potential_signals(tc,target_type)
                if signals:
                    # Create a protocard for the target card created by this interaction.
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    for sig in signals:
                        self.copy_elements(original_proto, tarproto, sig.signal_elements)
                        self.copy_elements(tarproto, myproto, sig.signal_elements, True)
                    self.copy_elements(original_proto, myproto, sock.signal_sought.signal_elements)
                    mylist.append(myproto)
        return mylist

    def get_protocards_that_produce_this_one(self, original_proto, nart):
        # Find a set of two cards that together can produce this card.
        candidates = list()
        for card_a in nart.plot_list[original_proto.card.LABEL]:
            # Check card_a for interactions that produce this card.
            for sock in card_a.SOCKETS:
                if original_proto.card.__name__ in sock.list_possible_outcomes():
                    # This is a potential card.
                    pair_cards = [card for card in nart.plot_list[original_proto.card.LABEL] if
                                  sock.get_potential_signals(card,original_proto.card.__name__)]
                    if pair_cards:
                        card_b = random.choice(pair_cards)
                        mysignal = random.choice(sock.get_potential_signals(card_b,original_proto.card.__name__))
                        mytransform = sock.get_transforming_consequence(original_proto.card.__name__)
                        proto_a = ProtoCard(card_a)
                        proto_b = ProtoCard(card_b)
                        # We are only worrying about the original_proto product here; any other products of this
                        # interaction don't matter.
                        self.copy_elements(original_proto, proto_a,
                                           mytransform.this_card_params,True)
                        self.copy_elements(original_proto, proto_b,
                                           mytransform.other_card_params,True)
                        self.copy_elements(proto_a, proto_b, sock.signal_sought.signal_elements,True)
                        self.copy_elements(proto_b, proto_a, sock.signal_sought.signal_elements)
                        candidates.append((proto_a, proto_b))
        if candidates:
            return random.choice(candidates)

    def generate_puzzle_sequence(self, nart, final_proto_list, steps=2):
        # Given a set of cards we want, return a set of ProtoCards that can generate those cards
        # within the requested number of steps.
        my_cards = list(final_proto_list)
        dead_ends = list()
        while steps > 0 and my_cards:
            random.shuffle(my_cards)
            card_to_replace = my_cards.pop()
            nu_cards = self.get_protocards_that_produce_this_one(card_to_replace, nart)
            if nu_cards:
                my_cards += nu_cards
                steps -= 1
            else:
                dead_ends.append(card_to_replace)
        return my_cards + dead_ends


