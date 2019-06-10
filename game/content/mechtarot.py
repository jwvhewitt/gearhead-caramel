import pbge
from pbge import plots
import random
import inspect
from . import GHNarrativeRequest, PLOT_LIST

ME_TAROTPOSITION = "TAROT_POSITION"
ME_AUTOREVEAL = "ME_AUTOREVEAL" # If this element is True, card is generated during adventure + doesn't need full init
ME_TAROTSCOPE = "TAROT_SCOPE"

# Action Trigger Keys
# These store functions that get called to generate dialogue, alter puzzle menus, or whatever
# when an interaction is activated.
AT_GET_DIALOGUE_OFFERS = "AT_GET_DIALOGUE_OFFERS"
# Params: alpha_card, beta_card, npc, camp, interaction
# Returns: list of offers for npc
AT_ALTER_ALPHA_PUZZLE_MENU = "AT_ALTER_ALPHA_PUZZLE_MENU"
AT_ALTER_BETA_PUZZLE_MENU = "AT_ALTER_BETA_PUZZLE_MENU"
# The key is (AT_ALTER_[x]_PUZZLEMENU,puzzle_item_element_id)
# Params: alpha_card,beta_card,camp,thing,thingmenu,interaction

class TarotCard(plots.Plot):
    LABEL = "TAROT"
    UNIQUE = False
    TAGS = ()
    INTERACTIONS = ()
    NEGATIONS = ()

    def __init__(self, nart, pstate):
        self.visible = False
        super(TarotCard, self).__init__(nart, pstate)

    def install(self, nart):
        """Plot generation complete. Mesh plot with campaign."""
        for sp in self.subplots.itervalues():
            sp.install(nart)
        del self.move_records
        scope = self.elements.get(ME_TAROTSCOPE)
        if not (scope and hasattr(scope,"tarot")):
            scope = nart.camp
        dest = self.elements.get(ME_TAROTPOSITION)
        if dest:
            scope.tarot[dest] = self
        else:
            # No unique ID provided... sure wish we had a unique hashable identifier
            # that isn't already being used in the dictionary...
            scope.tarot[hash(self)] = self
            self.elements[ME_TAROTPOSITION] = hash(self)

    def get_negations(self, num_neg=2):
        # Return a list of tarot cards that this card can turn into to negate itself.
        try:
            return random.sample(self.NEGATIONS, num_neg)
        except ValueError:
            return list(self.NEGATIONS)

    def get_dialogue_offers(self, npc, camp):
        """Get any dialogue offers this plot has for npc."""
        # Start with the basic offers.
        ofrz = super(TarotCard, self).get_dialogue_offers(npc, camp)
        # Check the interactions for any further offers.
        if self.visible and npc:
            for interac in self.INTERACTIONS:
                ofrz += interac.get_interaction_dialogue_offers(npc, camp, self)
        return ofrz

    def modify_puzzle_menu( self, camp, thing, thingmenu ):
        """Modify the thingmenu based on this plot."""
        # Method [ELEMENTID]_menu will be called with the menu as parameter.
        # This method should modify the menu as needed- typically by altering
        # the "desc" property (menu caption) and adding menu items.
        super(TarotCard,self).modify_puzzle_menu(camp,thing,thingmenu)
        if self.visible:
            for interac in self.INTERACTIONS:
                interac.modify_interaction_puzzle_menu(camp, thing, thingmenu, self)

    def reveal(self,camp):
        self.visible = True
        camp.check_trigger("UPDATE")

class TagChecker(object):
    def __init__(self, needed_tags=(), needed_elements=()):
        self.needed_tags = set(needed_tags)
        self.needed_elements = set(needed_elements)

    def check(self, card_to_check):
        # Return True if the given card might activate this checker.
        return self.needed_tags.issubset(card_to_check.TAGS)


class NameChecker(object):
    def __init__(self, name_set, needed_elements=()):
        self.name_set = set(name_set)
        self.needed_elements = set(needed_elements)

    def check(self, card_to_check):
        # Return True if the given card might activate this checker.
        if inspect.isclass(card_to_check):
            return card_to_check.__name__ in self.name_set
        else:
            return card_to_check.__class__.__name__ in self.name_set

class CardTransformer(object):
    def __init__(self,new_card_name,alpha_params=(),beta_params=()):
        # new_card_name is the name of the tarot card to transform this card to
        # alpha_params is a list of parameters to copy from the alpha_card (the card this interaction belongs to)
        # beta_params is a list of parameters to copy from the beta_card (the card triggering this interaction)
        self.new_card_name = new_card_name
        self.alpha_params = alpha_params
        self.beta_params = beta_params
    def __call__(self,camp,alpha_card,beta_card=None,transform_card=None):
        """

        :type alpha_card: TarotCard
        """
        nart = GHNarrativeRequest(camp, plot_list=PLOT_LIST)
        pstate = pbge.plots.PlotState()
        pstate.elements[ME_AUTOREVEAL] = True
        pstate.rank = alpha_card.rank
        if self.alpha_params:
            for pp in self.alpha_params:
                pstate.elements[pp] = alpha_card.elements.get(pp)
        if self.beta_params and beta_card:
            for pp in self.beta_params:
                pstate.elements[pp] = beta_card.elements.get(pp)
        if transform_card:
            pstate.elements[ME_TAROTPOSITION] = transform_card.elements[ME_TAROTPOSITION]
            pstate.elements[ME_TAROTSCOPE] = transform_card.elements[ME_TAROTSCOPE]
        else:
            pstate.elements[ME_TAROTSCOPE] = alpha_card.elements[ME_TAROTSCOPE]
        newcard = nart.request_tarot_card_by_name(self.new_card_name, pstate)
        if not newcard:
            pbge.alert("New tarot card failed for {}".format(self.new_card_name))
        else:
            nart.story.visible = True
            nart.build()


class Consequence(object):
    # An object that handles the transformation of tarot cards.
    def __init__(self,alpha_card_tf=None,beta_card_tf=None,new_card_tf=None):
        self.alpha_card_tf = alpha_card_tf
        self.beta_card_tf = beta_card_tf
        self.new_card_tf = new_card_tf
    def get_transform_for(self,target_card_name):
        if self.alpha_card_tf and self.alpha_card_tf.new_card_name == target_card_name:
            return self.alpha_card_tf
        elif self.beta_card_tf and self.beta_card_tf.new_card_name == target_card_name:
            return self.beta_card_tf
        elif self.new_card_tf and self.new_card_tf.new_card_name == target_card_name:
            return self.new_card_tf

    def __call__(self,camp,alpha_card,beta_card=None):
        end_these_plots = list()

        if self.alpha_card_tf:
            self.alpha_card_tf(camp, alpha_card, beta_card, alpha_card)
            end_these_plots.append(alpha_card)
        if self.beta_card_tf:
            self.alpha_card_tf(camp, alpha_card, beta_card, beta_card)
            if beta_card:
                end_these_plots.append(beta_card)
        if self.new_card_tf:
            self.new_card_tf(camp, alpha_card, beta_card, None)

        for p in end_these_plots:
            p.end_plot(camp)


class Interaction(object):
    def __init__(self, card_checker=None, action_triggers=None, consequences=None):
        # The card_checker is an object that can determine if a given card or the current game state will trigger this interaction
        # The action_triggers are functions called in various situations to activate this interaction
        self.card_checker = card_checker
        self.action_triggers = dict()
        if action_triggers:
            self.action_triggers.update(action_triggers)
        self.consequences = dict()
        if consequences:
            self.consequences.update(consequences)

    def maybe_activated_by(self, card_to_check):
        if self.card_checker:
            return self.card_checker.check(card_to_check)

    def can_change_card_to_target(self, card_to_change, target_card):
        # Return a list of consequences that will turn card_to_change into target_card, ignoring fail states
        mycon = list()
        if self.maybe_activated_by(card_to_change):
            for k,v in self.consequences.items():
                if not k.startswith("_"):
                    if v.beta_card_tf and v.beta_card_tf.new_card_name == target_card:
                        mycon.append(v)
        return mycon

    def can_change_self_to_target(self, reaction_card, target_card):
        # Return a list of consequences that will turn self into target_card, ignoring fail states
        mycon = list()
        if self.maybe_activated_by(reaction_card):
            for k,v in self.consequences.items():
                if not k.startswith("_"):
                    if v.alpha_card_tf and v.alpha_card_tf.new_card_name == target_card:
                        mycon.append(v)
        return mycon

    def can_produce_target(self, target_card):
        mycon = list()
        for k,v in self.consequences.items():
            if not k.startswith("_"):
                if (v.alpha_card_tf and v.alpha_card_tf.new_card_name == target_card) or (v.beta_card_tf and v.beta_card_tf.new_card_name == target_card) or (v.new_card_tf and v.new_card_tf.new_card_name == target_card):
                    mycon.append(v)
        return mycon


    def get_interaction_dialogue_offers(self, npc, camp, alpha_card):
        ofrz = list()
        if AT_GET_DIALOGUE_OFFERS in self.action_triggers:
            for beta_card in camp.active_tarot_cards():
                if beta_card.visible and self.maybe_activated_by(beta_card):
                    ofrz += self.action_triggers[AT_GET_DIALOGUE_OFFERS](alpha_card, beta_card=beta_card, npc=npc, camp=camp, interaction=self)
        return ofrz

    def modify_interaction_puzzle_menu( self, camp, thing, thingmenu, alpha_card ):
        for beta_card in camp.active_tarot_cards():
            if beta_card.visible and self.maybe_activated_by(beta_card):
                for el_name in alpha_card.get_element_idents(thing):
                    if (AT_ALTER_ALPHA_PUZZLE_MENU,el_name) in self.action_triggers:
                        self.action_triggers[(AT_ALTER_ALPHA_PUZZLE_MENU,el_name)](alpha_card,beta_card=beta_card,camp=camp,thing=thing,thingmenu=thingmenu,interaction=self)
                for el_name in beta_card.get_element_idents(thing):
                    if (AT_ALTER_BETA_PUZZLE_MENU,el_name) in self.action_triggers:
                        self.action_triggers[(AT_ALTER_BETA_PUZZLE_MENU,el_name)](alpha_card,beta_card=beta_card,camp=camp,thing=thing,thingmenu=thingmenu,interaction=self)

    def invoke(self, alpha_card, beta_card, camp, consequence):
        if consequence in self.consequences:
            self.consequences[consequence](camp,alpha_card,beta_card)
        else:
            print "Error: No consequence {}".format(consequence)





class ProtoCard(object):
    def __init__(self, card, elements=None):
        self.card = card
        self.elements = dict()
        if elements:
            self.elements.update(elements)


class Constellation(object):
    def __init__(self, nart, root_plot, root_card, dest_card_class=None, steps=3):
        self.element_lookup = dict()
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
                    for k, v in pcard.elements.items():
                        # Copy any known elements to this tarot plot.
                        elem = self.element_lookup.get(v)
                        if elem:
                            pstate.elements[k] = elem
                    tcplot = nart.init_tarot_card(root_plot, pcard.card, pstate)
                    for k, v in pcard.elements.items():
                        # Copy any newly defined elements to the lookup table.
                        if v not in self.element_lookup:
                            elem = tcplot.elements.get(k)
                            if elem:
                                self.element_lookup[v] = elem

    def inherit_elements(self, source_proto, dest_proto, element_list):
        if element_list:
            for ekey in element_list:
                if ekey in dest_proto.elements:
                    pass
                elif ekey in source_proto.elements:
                    # This is an already-defined key. Copy the code over.
                    dest_proto.elements[ekey] = source_proto.elements[ekey]
                else:
                    # This is a new key. Give the element a name, and store it in element_lookup if possible.
                    dest_proto.elements[ekey] = (source_proto, ekey)
                    source_proto.elements[ekey] = (source_proto, ekey)

                    if hasattr(source_proto.card, "elements") and ekey in source_proto.card.elements:
                        self.element_lookup[(source_proto, ekey)] = source_proto.card.elements[ekey]

    def get_protocards_that_change_this_one(self, original_card, target_type, nart):
        # Return a list of cards that will change this one into another type.
        mylist = list()
        original_proto = ProtoCard(original_card)
        for tc in nart.plot_list[original_card.LABEL]:
            for inter in tc.INTERACTIONS:
                mycon = inter.can_change_card_to_target(original_card,target_type)
                if mycon:
                    # Create a protocard for the target card created by this interaction.
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    for conseq in mycon:
                        self.inherit_elements(original_proto, tarproto, conseq.beta_card_tf.beta_params)
                        self.inherit_elements(tarproto, myproto, conseq.beta_card_tf.alpha_params)
                    self.inherit_elements(original_proto, myproto, inter.card_checker.needed_elements)
                    mylist.append(myproto)
            for inter in original_card.INTERACTIONS:
                mycon = inter.can_change_self_to_target(tc, target_type)
                if mycon:
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    for conseq in mycon:
                        self.inherit_elements(original_proto, tarproto, conseq.alpha_card_tf.alpha_params)
                        self.inherit_elements(tarproto, myproto, conseq.alpha_card_tf.beta_params)
                    self.inherit_elements(original_proto, myproto, inter.card_checker.needed_elements)
                    mylist.append(myproto)
        return mylist

    def get_protocards_that_produce_this_one(self, original_proto, nart):
        # Find a set of two cards that together can produce this card.
        candidates = list()
        for card_a in nart.plot_list[original_proto.card.LABEL]:
            # Check card_a for interactions that produce this card.
            for inter in card_a.INTERACTIONS:
                allcons = inter.can_produce_target(original_proto.card.__name__)
                if allcons:
                    # This is a potential card.
                    pair_cards = [card for card in nart.plot_list[original_proto.card.LABEL] if
                                  inter.maybe_activated_by(card)]
                    if pair_cards:
                        card_b = random.choice(pair_cards)
                        mycon = random.choice(allcons)
                        mytransform = mycon.get_transform_for(original_proto.card.__name__)
                        proto_a = ProtoCard(card_a)
                        proto_b = ProtoCard(card_b)
                        # We are only worrying about the original_proto product here; any other products of this
                        # interaction don't matter.
                        self.inherit_elements(original_proto, proto_a,
                                              mytransform.alpha_params)
                        self.inherit_elements(original_proto, proto_b,
                                              mytransform.beta_params)
                        self.inherit_elements(proto_a, proto_b, inter.card_checker.needed_elements)
                        self.inherit_elements(proto_b, proto_a, inter.card_checker.needed_elements)
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
