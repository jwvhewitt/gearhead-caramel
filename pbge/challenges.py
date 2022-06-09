from . import dialogue, widgets, okapipuzzle, BasicNotification

# Triggers used by Challenges and Resources:
ADVANCE_CHALLENGE = "ADVANCE_CHALLENGE"
SETBACK_CHALLENGE = "SETBACK_CHALLENGE"
SPEND_RESOURCE = "SPEND_RESOURCE"

MYSTERY_CHALLENGE = "MYSTERY_CHALLENGE"


class ChallengeMemo(object):
    def __init__(self, text, challenge=None):
        self._text = text
        self.challenge = challenge

    def __str__(self):
        if not self.challenge:
            return self._text
        else:
            return "{}\n\nCompletion: {}/{}".format(
                self._text, self.challenge.points_earned, self.challenge.points_target
            )


# Involvement Checker
#   A callable that takes (Campaign, Object) and returns True if the object can be involved in this Challenge.
class InvolvedSet(object):
    # This checker just has a list of things that are involved, returning True if the provided object is in the list.
    def __init__(self, things):
        self.things = set(things)

    def __call__(self, camp, ob):
        return ob in self.things


class AutoOfferInvoker(object):
    def __init__(self, aoffer, npc):
        self.aoffer = aoffer
        self.npc = npc

    def __call__(self, camp):
        self.aoffer.invoke_effect(camp, self.npc)


class AutoOffer(object):
    # AutoOffer
    #   A callable that takes (Challenge, Campaign, NPC) and may return an Offer.
    #  offer_dict = A dictionary holding the parameters for the Offer creation
    #  involvement = An involvement checker. If None, use the involvement checker of the challenge.
    #  access_fun = Basically another involvement checker; a callable that takes (camp,npc) and returns True if this offer
    #   can be added. May be used to add skill rolls or whatnot.
    #  npc_effect = A function that is called when this offer is selected that has signature (camp, npc)
    def __init__(self, offer_dict, active=True, uses=1, involvement=None, access_fun=None, once_per_npc=True,
                 npc_effect=None):
        self.offer_dict = offer_dict.copy()
        self.offer_effect = offer_dict.get("effect", None)
        self.active = active
        self.uses = uses
        self.used_on = set()
        self.used = False
        self.involvement = involvement
        self.access_fun = access_fun
        self.once_per_npc = once_per_npc
        self.npc_effect = npc_effect

    def invoke_effect(self, camp, npc):
        if self.offer_effect:
            self.offer_effect(camp)
        if self.npc_effect:
            self.npc_effect(camp, npc)
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
            if self.involvement:
                if self.involvement(camp, npc):
                    return self._get_offer(npc)
            elif my_challenge.involvement:
                if my_challenge.involvement(camp, npc):
                    return self._get_offer(npc)
            else:
                return self._get_offer(npc)


# AutoUsage
#   A callable that takes (Challenge, Campaign, Ob, Thingmenu) and may add a menu item.
#
#   effect = A callable that takes (Campaign)
#   access_fun = A callable that takes (camp,item) and returns True or False

class AutoUsage(object):
    def __init__(self, menu_text, effect, active=True, uses=1, involvement=None, access_fun=None, once_per_item=True):
        self.menu_text = menu_text
        self.effect = effect
        self.active = active
        self.uses = uses
        self.used_on = set()
        self.used = False
        self.involvement = involvement
        self.access_fun = access_fun
        self.once_per_item = once_per_item

    def invoke_effect(self, camp, item):
        self.effect(camp)
        self.used = True
        self.uses -= 1
        if self.uses < 1:
            self.active = False
        if self.once_per_item:
            self.used_on.add(item)

    def _modify_menu(self, my_challenge, thing, thingmenu):
        thingmenu.add_item(self.menu_text.format(challenge=my_challenge), AutoOfferInvoker(self, thing))

    def __call__(self, my_challenge, camp, thing, thingmenu):
        if self.active and (not self.access_fun or self.access_fun(camp, thing)) and thing not in self.used_on:
            if self.involvement:
                if self.involvement(camp, thing):
                    self._modify_menu(my_challenge, thing, thingmenu)
            elif my_challenge.involvement:
                if my_challenge.involvement(camp, thing):
                    self._modify_menu(my_challenge, thing, thingmenu)
            else:
                self._modify_menu(my_challenge, thing, thingmenu)


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
    # data = A dict of challenge-specific data that may be used by scenario generators. Just keeping my options open.
    def __init__(self, name, chaltype, key=(), involvement=None, active=True, grammar=None, oppoffers=(), oppuses=(),
                 data=None, points_target=10, memo=None, memo_active=False):
        self.name = name
        self.points_earned = 0
        self._active = active
        self.chaltype = chaltype
        self.key = tuple(key)
        self.involvement = involvement
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)
        self.oppoffers = oppoffers
        self.oppuses = oppuses
        self.data = dict()
        if data:
            self.data.update(data)
        self.points_target = points_target
        self.memo = memo
        if self.memo:
            self.memo.challenge = self
        self.memo_active = memo_active

    def advance(self, camp, delta):
        if self._active:
            self.points_earned += delta
            if delta > 0:
                camp.check_trigger(ADVANCE_CHALLENGE, self)
                if self.points_earned >= self.points_target:
                    camp.check_trigger("WIN", self)
            elif delta < 0:
                camp.check_trigger(SETBACK_CHALLENGE, self)
            self.memo_active = True
            camp.check_trigger("UPDATE")

    def activate(self, camp):
        self._active = True
        camp.check_trigger("UPDATE")

    def deactivate(self, camp):
        self._active = False
        camp.check_trigger("UPDATE")

    @property
    def active(self):
        return self._active

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
        for o in self.oppuses:
            o(self, camp, thing, thingmenu)

    def is_won(self):
        return self.points_earned >= self.points_target

    def __str__(self):
        return self.name

    def get_memo(self):
        if self.memo and self.memo_active and self.active:
            return self.memo


class ResourceSpender(object):
    def __init__(self, my_resource, my_challenge, call_dialogue_effect=True):
        self.my_resource = my_resource
        self.my_challenge = my_challenge
        self.call_dialogue_effect = call_dialogue_effect

    def __call__(self, camp):
        self.my_resource.spend_resource(camp, self.my_challenge, self.call_dialogue_effect)


class Resource(object):
    # A Resource is a thing that can be spent to advance a Challenge.
    #
    # Like Challenges, a Resource must be an element of an active plot in order to be found.
    #
    # Things a Resource can do:
    #   - Be identified by a challenge it can be spent on
    #   - Identify a character or waypoint that can be used to spend the resource
    #   - Add a dialogue offer or a menu item to spend the resource
    def __init__(self, name, chaltype, key=(), points=1, single_use=True, active=True, involvement=None,
                 spend_offer_dict=None, menu_item_text=None):
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

    def spend_resource(self, camp, my_challenge: Challenge, call_dialogue_effect=True):
        my_challenge.advance(camp, self.points)
        self.used = True
        if self.single_use:
            self.active = False
        if self.spend_offer_effect and call_dialogue_effect:
            self.spend_offer_effect(camp)
        camp.check_trigger(SPEND_RESOURCE, self)

    def _get_offer(self, my_challenge):
        mydict = self.spend_offer_dict.copy()
        mydict["msg"] = self.spend_offer_dict["msg"].format(resource=self, challenge=my_challenge)
        mydict["effect"] = ResourceSpender(self, my_challenge, True)
        return dialogue.Offer(**mydict)

    def is_involved(self, camp, thing):
        if self.involvement:
            return self.involvement(camp, thing)
        else:
            return True

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
                mylist.append(self._get_offer(c))

        return mylist

    def modify_puzzle_menu(self, camp, thing, thingmenu, clist):
        if self.menu_item_text and self.is_involved(camp, thing):
            for c in clist:
                if c.can_spend_resource(self) and c.is_involved(camp, thing):
                    thingmenu.add_item(self.menu_item_text.format(resource=self, challenge=c),
                                       ResourceSpender(self, c, False))

    def __str__(self):
        return self.name


class MysteryMemo(object):
    def __init__(self, text, challenge=None):
        self._text = text
        self.challenge = challenge

    def __str__(self):
        if not self.challenge:
            return self._text
        else:
            return "{}\n\nCompletion: {}/{}".format(
                self._text, self.challenge.points_earned, self.challenge.points_target
            )

    def get_widget(self, memobrowser, camp):
        mylabel = widgets.LabelWidget(
            memobrowser.dx, memobrowser.dy, memobrowser.w, memobrowser.h, text=str(self),
            data=memobrowser, justify=0)
        mybutton = widgets.LabelWidget(
            0, 116, 0, 0, text="Examine Clues", draw_border=True, justify=0, border=widgets.widget_border_on,
            on_click=self.open_mystery, data=(memobrowser,camp), parent=mylabel
        )
        mylabel.children.append(mybutton)
        return mylabel

    def open_mystery(self, wid, ev):
        # Open the Hypothesis Widget.
        memob, camp = wid.data
        memob.active = False
        okapipuzzle.OkapiPuzzleWidget(self.challenge.mystery, self.solve_mystery)
        memob.active = True

    def solve_mystery(self):
        pass

class MysteryChallenge(Challenge):
    # A mystery challenge takes an Okapi Puzzle and makes a challenge of it.
    # Instead of victory points you accumulate clues, and instead of winning when you've found all the clues you win
    # when you solve the puzzle via a hypothesis widget. If no memo is provided, this challenge will add a memo that
    # can open the hypothesis widget from the memo viewer.
    def __init__(self, name, mystery, **kwargs):
        super().__init__(name, MYSTERY_CHALLENGE, **kwargs)
        self.mystery = mystery

    def advance(self, camp, clue=None):
        if self._active:
            if self.mystery.unknown_clues:
                if self.mystery.unknown_clues and not (clue and clue in self.mystery.unknown_clues):
                    clue = self.mystery.unknown_clues.pop()
                if clue:
                    self.mystery.known_clues.append(clue)
                    BasicNotification("You learned {}!".format(clue), count=120)
                camp.check_trigger(ADVANCE_CHALLENGE, self)
            self.memo_active = True
            camp.check_trigger("UPDATE")

    def is_won(self):
        return self.mystery.solved
