from pbge import plots
import random

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
    @classmethod
    def get_cards_that_change_this_one(cls, target_type, nart):
        # Return a list of cards that will change this one into another type.
        mylist = list()
        for tc in nart.plot_list[cls.LABEL]:
            if any(target_type == ip_list[1] for ip_list in tc.get_interaction_possibilities(cls))\
                    or any(target_type == ip_list[0] for ip_list in cls.get_interaction_possibilities(tc)):
                mylist.append(tc)
        return mylist
    @classmethod
    def get_interaction_possibilities(cls,other_card):
        for inter in cls.INTERACTIONS:
            if inter.maybe_activated_by(other_card):
                yield inter.results
    @classmethod
    def get_cards_that_produce_this_one(cls,nart):
        # Find a set of two cards that together can produce this card.
        candidates = list()
        for tc in nart.plot_list[cls.LABEL]:
            # Check tc for interactions that produce this card.
            for tc_int in tc.INTERACTIONS:
                if cls.__name__ in tc_int.results:
                    # This is a potential card.
                    pair_cards = [card for card in nart.plot_list[cls.LABEL] if tc_int.maybe_activated_by(card)]
                    if pair_cards:
                        candidates.append([tc,random.choice(pair_cards)])
        if candidates:
            return random.choice(candidates)
    @classmethod
    def generate_puzzle_sequence(cls,nart,final_card_list,steps=2):
        # Given a set of cards we want, return a set of cards that can generate those cards
        # within the requested number of steps.
        my_cards = list(final_card_list)
        dead_ends = list()
        while steps > 0 and my_cards:
            random.shuffle(my_cards)
            card_to_replace = my_cards.pop()
            nu_cards = card_to_replace.get_cards_that_produce_this_one(nart)
            if nu_cards:
                my_cards += nu_cards
                steps -= 1
            else:
                dead_ends.append(card_to_replace)
        return my_cards + dead_ends

class TagChecker(object):
    def __init__(self,needed_tags=set()):
        self.needed_tags = set(needed_tags)
    def check(self,card_to_check):
        # Return True if the given card might activate this checker.
        return self.needed_tags.issubset(card_to_check.TAGS)

class NameChecker(object):
    def __init__(self,name_set):
        self.name_set = set(name_set)
    def check(self,card_to_check):
        # Return True if the given card might activate this checker.
        return card_to_check.__name__ in self.name_set

class Interaction(object):
    def __init__(self,card_checker,action_triggers=(),effect_plot="",results=(None,None,None)):
        # The card_checker is an object that can determine if a given card or the current game state will trigger this interaction
        # The action_triggers are dialogue options and prop actions that are activated when the card_checker says this interaction is active
        # The effect_plot is a subplot that gets activated when any of the action_triggers are selected
        # The results indicate the projected outcomes for this card, the interacting card, and any new card added.
        self.card_checker = card_checker
        self.action_triggers = action_triggers
        self.effect_plot = effect_plot
        self.results = results
    def maybe_activated_by(self,card_to_check):
        return self.card_checker.check(card_to_check)
