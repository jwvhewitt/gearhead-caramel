import pbge
from pbge import plots
import random
import inspect

class TarotCard(plots.Plot):
    LABEL = "TAROT"
    UNIQUE = False
    TAGS = ()
    INTERACTIONS = ()
    NEGATIONS = ()
    def install( self, nart ):
        """Plot generation complete. Mesh plot with campaign."""
        for sp in self.subplots.itervalues():
            sp.install( nart )
        del self.move_records
        dest = self.elements.get( 'TAROT_POSITION' )
        if dest:
            nart.camp.tarot[dest] = self
        else:
            # No unique ID provided... sure wish we had a unique hashable identifier
            # that isn't already being used in the dictionary...
            nart.camp.tarot[self] = self
    def get_negations(self,num_neg=2):
        # Return a list of tarot cards that this card can turn into to negate itself.
        try:
            return random.sample(self.NEGATIONS,num_neg)
        except ValueError:
            return list(self.NEGATIONS)

class TagChecker(object):
    def __init__(self,needed_tags=set(),needed_elements=()):
        self.needed_tags = set(needed_tags)
        self.needed_elements = set(needed_elements)
    def check(self,card_to_check):
        # Return True if the given card might activate this checker.
        return self.needed_tags.issubset(card_to_check.TAGS)

class NameChecker(object):
    def __init__(self,name_set,needed_elements=()):
        self.name_set = set(name_set)
        self.needed_elements = set(needed_elements)
    def check(self,card_to_check):
        # Return True if the given card might activate this checker.
        if inspect.isclass(card_to_check):
            return card_to_check.__name__ in self.name_set
        else:
            return card_to_check.__class__.__name__ in self.name_set

class Interaction(object):
    def __init__(self,card_checker,action_triggers=(),effect_plot="",results=(None,None,None),passparams=(((),()),((),()),((),()))):
        # The card_checker is an object that can determine if a given card or the current game state will trigger this interaction
        # The action_triggers are dialogue options and prop actions that are activated when the card_checker says this interaction is active
        # The effect_plot is a subplot that gets activated when any of the action_triggers are selected
        # The results indicate the projected outcomes for this card, the interacting card, and any new card added.
        self.card_checker = card_checker
        self.action_triggers = action_triggers
        self.effect_plot = effect_plot
        self.results = results
        self.passparams = passparams
    def maybe_activated_by(self,card_to_check):
        return self.card_checker.check(card_to_check)


class ProtoCard(object):
    def __init__(self,card,elements=dict()):
        self.card = card
        self.elements = dict(elements)

class Constellation(object):
    def __init__(self,nart,root_plot,root_card,dest_card_class=None,steps=3):
        self.element_lookup = dict()
        if dest_card_class:
            possible_cards = self.get_protocards_that_change_this_one(root_card,dest_card_class.__name__,nart)
        else:
            possible_cards = [ProtoCard(root_card),]
        if possible_cards:
            initial_cards = self.generate_puzzle_sequence(nart,[random.choice(possible_cards)],steps=steps)
            if initial_cards:
                # Add these cards to the adventure.
                for pcard in initial_cards:
                    print pcard.card.__name__
                    print pcard.elements
                    pstate = pbge.plots.PlotState().based_on(root_plot)
                    for k,v in pcard.elements.items():
                        # Copy any known elements to this tarot plot.
                        elem = self.element_lookup.get(v)
                        if elem:
                            pstate.elements[k] = elem
                    tcplot = nart.init_tarot_card(root_plot,pcard.card,pstate)
                    for k, v in pcard.elements.items():
                        # Copy any newly defined elements to the lookup table.
                        if v not in self.element_lookup:
                            elem = tcplot.elements.get(k)
                            if elem:
                                self.element_lookup[v] = elem

    def inherit_elements(self,source_proto,dest_proto,element_list):
        if element_list:
            for ekey in element_list:
                if ekey in dest_proto.elements:
                    pass
                elif ekey in source_proto.elements:
                    # This is an already-defined key. Copy the code over.
                    dest_proto.elements[ekey] = source_proto.elements[ekey]
                else:
                    # This is a new key. Give the element a name, and store it in element_lookup if possible.
                    dest_proto.elements[ekey] = (source_proto,ekey)
                    source_proto.elements[ekey] = (source_proto,ekey)

                    if hasattr(source_proto.card,"elements") and ekey in source_proto.card.elements:
                        self.element_lookup[(source_proto,ekey)] = source_proto.card.elements[ekey]
    def get_protocards_that_change_this_one(self, original_card, target_type, nart):
        # Return a list of cards that will change this one into another type.
        mylist = list()
        original_proto = ProtoCard(original_card)
        for tc in nart.plot_list[original_card.LABEL]:
            for inter in tc.INTERACTIONS:
                if inter.maybe_activated_by(original_card) and target_type == inter.results[1]:
                    # Create a protocard for the target card created by this interaction.
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    self.inherit_elements(original_proto,tarproto,inter.passparams[1][1])
                    self.inherit_elements(original_proto,myproto,inter.card_checker.needed_elements)
                    self.inherit_elements(tarproto,myproto,inter.passparams[1][0])
                    mylist.append(myproto)
            for inter in original_card.INTERACTIONS:
                if inter.maybe_activated_by(tc) and target_type == inter.results[0]:
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    self.inherit_elements(original_proto,tarproto,inter.passparams[0][0])
                    self.inherit_elements(original_proto,myproto,inter.card_checker.needed_elements)
                    self.inherit_elements(tarproto,myproto,inter.passparams[0][1])
                    mylist.append(myproto)
        return mylist
    def get_protocards_that_produce_this_one(self,original_proto,nart):
        # Find a set of two cards that together can produce this card.
        candidates = list()
        for card_a in nart.plot_list[original_proto.card.LABEL]:
            # Check card_a for interactions that produce this card.
            for inter in card_a.INTERACTIONS:
                if original_proto.card.__name__ in inter.results:
                    # This is a potential card.
                    pair_cards = [card for card in nart.plot_list[original_proto.card.LABEL] if inter.maybe_activated_by(card)]
                    if pair_cards:
                        card_b = random.choice(pair_cards)
                        proto_a = ProtoCard(card_a)
                        proto_b = ProtoCard(card_b)
                        # We are only worrying about the original_proto product here; any other products of this
                        # interaction don't matter.
                        print "initial {}: {}".format(proto_a.card.__name__,proto_a.elements)
                        print "initial {}: {}".format(proto_b.card.__name__,proto_b.elements)
                        self.inherit_elements(original_proto, proto_a, inter.passparams[inter.results.index(original_proto.card.__name__)][0])
                        self.inherit_elements(original_proto, proto_b, inter.passparams[inter.results.index(original_proto.card.__name__)][1])
                        self.inherit_elements(proto_a, proto_b, inter.card_checker.needed_elements)
                        self.inherit_elements(proto_b, proto_a, inter.card_checker.needed_elements)
                        print "final {}: {}".format(proto_a.card.__name__,proto_a.elements)
                        print "final {}: {}".format(proto_b.card.__name__,proto_b.elements)
                        candidates.append((proto_a,proto_b))
        if candidates:
            return random.choice(candidates)
    def generate_puzzle_sequence(self,nart,final_proto_list,steps=2):
        # Given a set of cards we want, return a set of ProtoCards that can generate those cards
        # within the requested number of steps.
        my_cards = list(final_proto_list)
        dead_ends = list()
        while steps > 0 and my_cards:
            random.shuffle(my_cards)
            card_to_replace = my_cards.pop()
            nu_cards = self.get_protocards_that_produce_this_one(card_to_replace,nart)
            if nu_cards:
                my_cards += nu_cards
                steps -= 1
            else:
                dead_ends.append(card_to_replace)
        return my_cards + dead_ends

