import pbge
from pbge import plots
import random
import inspect
from . import GHNarrativeRequest, PLOT_LIST

ME_TAROTPOSITION = "TAROT_POSITION"
ME_AUTOREVEAL = "ME_AUTOREVEAL" # If this element is True, card is generated during adventure + doesn't need full init
ME_TAROTSCOPE = "TAROT_SCOPE"

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
        if self.visible:
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


class Interaction(object):
    def __init__(self, card_checker=None, action_triggers=(), effect_fun=None, results=(None, None, None),
                 passparams=(((), ()), ((), ()), ((), ()))):
        # The card_checker is an object that can determine if a given card or the current game state will trigger this interaction
        # The action_triggers are dialogue options and prop actions that are activated when the card_checker says this interaction is active
        # effect_fun is a function that gets called when this interaction is triggered. It takes alpha_card, beta_card, camp.
        #  If it doesn't exist or returns False, the card transformation is handled here. If it returns True, assume
        #  the card transformation will be handled elsewhere and do nothing.
        # The results indicate the projected outcomes for this card, the interacting card, and any new card added.
        # The passparams is a list of paramaters to pass to the new cards from the alpha and beta cards.
        self.card_checker = card_checker
        self.action_triggers = action_triggers
        self.effect_fun = effect_fun
        self.results = results
        self.passparams = passparams

    def maybe_activated_by(self, card_to_check):
        if self.card_checker:
            return self.card_checker.check(card_to_check)

    def get_interaction_dialogue_offers(self, npc, camp, alpha_card):
        ofrz = list()
        for beta_card in camp.active_tarot_cards():
            if beta_card.visible and self.maybe_activated_by(beta_card):
                for at in [a for a in self.action_triggers if hasattr(a,"get_at_dialogue_offers")]:
                    ofrz += at.get_at_dialogue_offers(npc, camp, alpha_card, beta_card, self.invoke)
        return ofrz

    def modify_interaction_puzzle_menu( self, camp, thing, thingmenu, alpha_card ):
        for beta_card in camp.active_tarot_cards():
            if beta_card.visible and self.maybe_activated_by(beta_card):
                for at in [a for a in self.action_triggers if hasattr(a,"can_modify_puzzle_menu") and a.can_modify_puzzle_menu(thing,alpha_card,beta_card)]:
                    at.modify_at_puzzle_menu(camp,thing,thingmenu,alpha_card,beta_card,self.invoke)

    def mutate_cards(self, alpha_card, beta_card, camp):
        nart = GHNarrativeRequest(camp, plot_list=PLOT_LIST)
        end_these_plots = list()
        for t in range(3):
            if self.results[t]:
                # Replace this card.
                pstate = pbge.plots.PlotState()
                pstate.elements[ME_AUTOREVEAL] = True
                if self.passparams[t]:
                    if self.passparams[t][0]:
                        for pp in self.passparams[t][0]:
                            pstate.elements[pp] = alpha_card.elements.get(pp)
                    if self.passparams[t][1]:
                        for pp in self.passparams[t][1]:
                            pstate.elements[pp] = beta_card.elements.get(pp)
                if t == 0:
                    pstate.elements[ME_TAROTPOSITION] = alpha_card.elements[ME_TAROTPOSITION]
                    pstate.elements[ME_TAROTSCOPE] = alpha_card.elements[ME_TAROTSCOPE]
                    end_these_plots.append(alpha_card)
                elif t == 1:
                    pstate.elements[ME_TAROTPOSITION] = beta_card.elements[ME_TAROTPOSITION]
                    pstate.elements[ME_TAROTSCOPE] = alpha_card.elements[ME_TAROTSCOPE]
                    end_these_plots.append(beta_card)

                newcard = nart.request_tarot_card_by_name(self.results[t], pstate)
                if not newcard:
                    pbge.alert("New tarot card failed for {}".format(self.results[t]))
                else:
                    nart.story.visible = True
                    nart.build()
        for p in end_these_plots:
            p.end_plot(camp)

    def invoke(self, alpha_card, beta_card, camp):
        if self.effect_fun:
            if not self.effect_fun(alpha_card, beta_card, camp):
                self.mutate_cards(alpha_card, beta_card, camp)
        else:
            self.mutate_cards(alpha_card, beta_card, camp)


class ActionTriggerInvoker(object):
    # extra_fx is an optional function that takes alpha, beta, camp as its parameters
    #  that is called after the primary atfun function.
    #  Now the terrible part: For whatever reason, if the function is a static method or object method,
    #  it won't if it's included in the card's Interactions dict. And, of course, a bound method can't be
    #  included in the Interactions dict because it doesn't even exist until the card is instantiated.
    #  So, instead, pretend that extra_fx takes just beta and camp as its parameters and call alpha self
    #  and everything will work but it's sleazy as hell.
    def __init__(self, alpha, beta, atfun, extra_fx):
        self.alpha = alpha
        self.beta = beta
        self.atfun = atfun
        self.extra_fx = extra_fx

    def __call__(self, camp):
        self.atfun(self.alpha, self.beta, camp)
        if self.extra_fx:
            self.extra_fx(self.alpha,self.beta,camp)

class AlphaCardDialogueTrigger(object):
    def __init__(self, npc_ident, dialogue_text, dialogue_context, data=None, data_fun=None, extra_fx=None):
        self.npc_ident = npc_ident
        self.dialogue_text = dialogue_text
        self.dialogue_context = dialogue_context
        self.data = data
        self.data_fun = data_fun
        self.extra_fx = extra_fx

    def get_at_dialogue_offers(self, npc, camp, alpha_card, beta_card, effect_fun):
        ofrz = list()
        if alpha_card.elements.get(self.npc_ident) is npc:
            if self.data:
                mydata = self.data
            elif self.data_fun:
                mydata = self.data_fun(camp)
            else:
                mydata = False
            ofrz.append(pbge.dialogue.Offer(self.dialogue_text, self.dialogue_context,
                                            effect=ActionTriggerInvoker(alpha_card, beta_card, effect_fun, self.extra_fx),
                                            data=mydata))
        return ofrz


class BetaCardDialogueTrigger(object):
    def __init__(self, npc_ident, dialogue_text, dialogue_context, data=None, data_fun=None, extra_fx=None):
        self.npc_ident = npc_ident
        self.dialogue_text = dialogue_text
        self.dialogue_context = dialogue_context
        self.data = data
        self.data_fun = data_fun
        self.extra_fx = extra_fx

    def get_at_dialogue_offers(self, npc, camp, alpha_card, beta_card, effect_fun):
        ofrz = list()
        if beta_card.elements.get(self.npc_ident) is npc:
            if self.data:
                mydata = self.data
            elif self.data_fun:
                mydata = self.data_fun(camp)
            else:
                mydata = False
            ofrz.append(pbge.dialogue.Offer(self.dialogue_text, self.dialogue_context,
                                            effect=ActionTriggerInvoker(alpha_card, beta_card, effect_fun, self.extra_fx),
                                            data=mydata))
        return ofrz

class AlphaCardPuzzleItemTrigger(object):
    # This trigger adds an option to a puzzlemenu.
    def __init__(self, item_ident, caption_pattern='{}', menu_option='[]', data=None, data_fun=None, extra_fx=None):
        self.item_ident = item_ident
        self.caption_pattern = caption_pattern
        self.menu_option = menu_option
        self.data = data
        self.data_fun = data_fun
        self.extra_fx = extra_fx

    def can_modify_puzzle_menu(self, thing, alpha_card, beta_card):
        return alpha_card.elements.get(self.item_ident) == thing

    def modify_at_puzzle_menu(self,camp,thing,thingmenu,alpha_card,beta_card,effect_fun):
        if self.data:
            mydata = self.data
        elif self.data_fun:
            mydata = self.data_fun(camp)
        else:
            mydata = dict()
        thingmenu.desc = self.caption_pattern.format(thingmenu.desc).format(**mydata)
        thingmenu.add_item(self.menu_option.format(**mydata),ActionTriggerInvoker(alpha_card, beta_card, effect_fun, self.extra_fx))



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
                if inter.maybe_activated_by(original_card) and target_type == inter.results[1]:
                    # Create a protocard for the target card created by this interaction.
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    self.inherit_elements(original_proto, tarproto, inter.passparams[1][1])
                    self.inherit_elements(original_proto, myproto, inter.card_checker.needed_elements)
                    self.inherit_elements(tarproto, myproto, inter.passparams[1][0])
                    mylist.append(myproto)
            for inter in original_card.INTERACTIONS:
                if inter.maybe_activated_by(tc) and target_type == inter.results[0]:
                    tarproto = ProtoCard(target_type)
                    myproto = ProtoCard(tc)
                    self.inherit_elements(original_proto, tarproto, inter.passparams[0][0])
                    self.inherit_elements(original_proto, myproto, inter.card_checker.needed_elements)
                    self.inherit_elements(tarproto, myproto, inter.passparams[0][1])
                    mylist.append(myproto)
        return mylist

    def get_protocards_that_produce_this_one(self, original_proto, nart):
        # Find a set of two cards that together can produce this card.
        candidates = list()
        for card_a in nart.plot_list[original_proto.card.LABEL]:
            # Check card_a for interactions that produce this card.
            for inter in card_a.INTERACTIONS:
                if original_proto.card.__name__ in inter.results:
                    # This is a potential card.
                    pair_cards = [card for card in nart.plot_list[original_proto.card.LABEL] if
                                  inter.maybe_activated_by(card)]
                    if pair_cards:
                        card_b = random.choice(pair_cards)
                        proto_a = ProtoCard(card_a)
                        proto_b = ProtoCard(card_b)
                        # We are only worrying about the original_proto product here; any other products of this
                        # interaction don't matter.
                        self.inherit_elements(original_proto, proto_a,
                                              inter.passparams[inter.results.index(original_proto.card.__name__)][0])
                        self.inherit_elements(original_proto, proto_b,
                                              inter.passparams[inter.results.index(original_proto.card.__name__)][1])
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
