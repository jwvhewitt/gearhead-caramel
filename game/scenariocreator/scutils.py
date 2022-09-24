# Utilities that are useful for the scenario creator and not much else.

class DialogueOfferHandler:
    # Keeps track of single-use dialogue offers without the scenario designer needing to add new global variables
    # or whatnot.
    def __init__(self, uid, single_use=False):
        self.uid = uid
        self.single_use = single_use
        self.has_been_used = False
        self.effect = None

    def can_add_offer(self):
        return not (self.single_use and self.has_been_used)

    def get_effect(self, effect=None):
        self.effect = effect
        return self

    def __call__(self, camp):
        self.has_been_used = True
        if self.effect:
            self.effect(camp)

