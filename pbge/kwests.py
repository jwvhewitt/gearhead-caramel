
VERB_DEFEAT = "DEFEAT"


class KwestLore:
    def __init__(self, elements=None):
        self.elements = dict()
        if elements:
            self.elements.update(elements)


class KwestOutcome:
    def __init__(self, verb=VERB_DEFEAT, target=None, involvement=None, effect=None, loss_effect=None, lore=()):
        # verb is what's gonna happen in this outcome.
        # target is the Quest Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # involvement is a challenge involvement checker which checks to see what factions/NPCs might offer missions
        #   leading to this outcome.
        # effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        # loss_effect is a callable of form "loss_effect(camp)" which is called if/when this outcome fails
        # hooks is a list of hooks that can be claimed by the conclusion leading to this outcome.
        self.verb = verb
        self.target = target
        self.involvement = involvement
        self.effect = effect
        self.loss_effect = loss_effect
        self.hooks = list(lore)

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)

    def __str__(self):
        return "{}: {}".format(self.verb, self.target)





