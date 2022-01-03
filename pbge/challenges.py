from . import dialogue

# Triggers used by Challenges and Resources:
ADVANCE_CHALLENGE = "ADVANCE_CHALLENGE"
SETBACK_CHALLENGE = "SETBACK_CHALLENGE"

# Challenge Types


# Involvement Checker
#   A callable that takes (Campaign, Object) and returns True if the object can be involved in this Challenge.
class InvolvedSet(object):
    # This checker just has a list of things that are involved, returning True if the provided object is in the list.
    def __init__(self, things):
        self.things = set(things)

    def __call__(self, camp, ob):
        return ob in self.things


# AutoOffer
#   A callable that takes (Challenge, Campaign, NPC) and may return an Offer.
#  offer_dict = A dictionary holding the parameters for the Offer creation
#  involvement = An involvement checker. If None, use the involvement checker of the challenge.
#  access_fun = Basically another involvement checker; a callable that takes (camp,npc) and returns True if this offer
#   can be added. May be used to add skill rolls or whatnot.

class AutoOfferInvoker(object):
    def __init__(self, aoffer, npc):
        self.aoffer = aoffer
        self.npc = npc

    def __call__(self, camp):
        self.aoffer.invoke_effect(camp, self.npc)


class AutoOffer(object):
    def __init__(self, offer_dict, active=True, uses=1, involvement=None, access_fun=None, once_per_npc=True):
        self.offer_dict = offer_dict.copy()
        self.offer_effect = offer_dict.get("effect", None)
        self.active = active
        self.uses = uses
        self.used_on = set()
        self.used = False
        self.involvement = involvement
        self.access_fun = access_fun
        self.once_per_npc = once_per_npc

    def invoke_effect(self, camp, npc):
        if self.offer_effect:
            self.offer_effect(camp)
        self.used = True
        self.uses -= 1
        if self.uses < 1:
            self.active = False
        if self.once_per_npc:
            self.used_on.add(npc)

    def _get_offer(self, npc):
        mydict = self.offer_dict.copy()
        mydict["effect"] = AutoOfferInvoker(self, npc)
        return dialogue.Offer(**mydict)

    def __call__(self, my_challenge, camp, npc):
        if self.active and (not self.access_fun or self.access_fun(camp, npc)) and npc not in self.used_on:
            if self.involvement and self.involvement(camp, npc):
                return self._get_offer(npc)
            elif my_challenge.involvement and my_challenge.involvement(camp, npc):
                return self._get_offer(npc)
            else:
                return self._get_offer(npc)


# AutoUsage
#   A callable that takes (Campaign, Ob, Thingmenu) and may add a menu item.



class Challenge(object):
    # What is a challenge? It's an object that can get passed around to the scenario builder or to the random plot
    # loader describing a plot hook, and featuring methods + properties for incorporating that plot hook into bits
    # of the adventure. The advantage of using Challenges is that you can set up a conflict/quest in terms of the
    # challenges for the PC, then just leave them to run.
    #
    # Note that in order for a Challenge to be found, it must be an element of an active plot.
    #
    # Things a Challenge can do:
    #   - Tell other plots and resources what sort of challenge this is
    #   - Tell which NPCs may give quests related to this challenge
    #   - Keep a running total of challenge points earned
    #   - Be activated and deactivated
    #   - Add dialogue grammar
    #   - Add conversation options
    #   - Add waypoint menu items
    #
    # chaltype = What kind of challenge is this?
    # key = A tuple containing identifying characteristics specific to this challenge; used to tell whether a resource
    #       can be spent on this challenge or not. May also be used by the plot/scenario generator. The characteristics
    #       should be listed from less specific to more specific.
    # involvement = An Involvement Checker to see if an NPC, Waypoint, or some other object can be involved in this
    #       challenge. If None, every item passed will return True.
    # grammar = Dialogue grammar to be used while this challenge is active
    # oppoffers = A list of AutoOffers used by this challenge
    # oppuses = A list of AutoUsages used by this challenge
    def __init__(self, name, chaltype, key=(), involvement=None, active=True, grammar=None, oppoffers=(), oppuses=()):
        self.points_earned = 0
        self.active = active
        self.chaltype = chaltype
        self.key = tuple(key)
        self.involvement = involvement
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)
        self.oppoffers = oppoffers
        self.oppuses = oppuses

    def advance(self, camp, delta):
        self.points_earned += delta
        if delta > 0:
            camp.check_trigger(ADVANCE_CHALLENGE, self)
        elif delta < 0:
            camp.check_trigger(SETBACK_CHALLENGE, self)

    def can_spend_resource(self, resource):
        return self.chaltype == resource.chaltype and self.key == resource.key[:len(self.key)]

    def is_involved(self, camp, ob):
        if self.involvement:
            return self.involvement(camp, ob)
        else:
            return True

    def get_dialogue_offers(self, npc, camp):
        mylist = list()

        for o in self.oppoffers:
            myoff = o(self, camp, npc)
            if myoff:
                mylist.append(myoff)

        return mylist

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        pass


class ResourceSpender(object):
    def __init__(self, my_resource, my_challenge):
        self.my_resource = my_resource
        self.my_challenge = my_challenge

    def __call__(self, camp):
        self.my_resource.spend_resource(camp, self.my_challenge)


class Resource(object):
    # A Resource is a thing that can be spent to advance a Challenge.
    #
    # Like Challenges, a Resource must be an element of an active plot in order to be found.
    #
    # Things a Resource can do:
    #   - Be identified by a challenge it can be spent on
    #   - Identify a character or waypoint that can be used to spend the resource
    #   - Add a dialogue offer or a menu item to spend the resource
    def __init__(self, name, chaltype, key=(), points=1, single_use=True, active=True, involvement=None, spend_offer_dict=None, menu_item_text=None):
        self.name = name
        self.chaltype = chaltype
        self.key = tuple(key)
        self.points = points
        self.single_use = single_use
        self.used = False
        self.active = active
        self.involvement = involvement
        if spend_offer_dict:
            self.spend_offer_dict = spend_offer_dict.copy()
            self.spend_offer_effect = spend_offer_dict.get("effect", None)
        else:
            self.spend_offer_dict = None
            self.spend_offer_effect = None

        self.menu_item_text = menu_item_text

    def spend_resource(self, camp, my_challenge: Challenge):
        my_challenge.advance(self.points)
        self.used = True
        if self.single_use:
            self.active = False
        if self.spend_offer_effect:
            self.spend_offer_effect(camp)

    def _get_offer(self, my_challenge):
        mydict = self.spend_offer_dict.copy()
        mydict["msg"] = self.spend_offer_dict["msg"].format(resource=self.name, challenge=my_challenge.name)
        mydict["effect"] = ResourceSpender(self, my_challenge)
        return dialogue.Offer(**mydict)

    def get_dialogue_offers(self, npc, camp, clist):
        # clist is a list of challenges.
        mylist = list()

        # If this NPC cannot access this resource, exit with nothing.
        if self.involvement and not self.involvement(camp, npc):
            return mylist
        elif not self.spend_offer_dict:
            return mylist

        for c in clist:
            if c.can_spend_resource(self) and c.is_involved(camp, npc):
                mylist.append(self._get_offer(self, c))

        return mylist

    def modify_puzzle_menu(self, camp, thing, thingmenu, clist):
        pass

