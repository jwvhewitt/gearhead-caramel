# A merit badge is a tag that the PC receives recording some achievement or life experience.
# Usually these badges give bonuses to reaction score; some might have other effects.


class TagReactionBadge(object):
    def __init__(self,name,desc,remods = None):
        self.name = name
        self.desc = desc
        self.reaction_modifiers = dict
        if remods:
            self.reaction_modifiers.update(remods)
    def get_reaction_modifier(self,pc,npc,camp):
        total = 0
        npc_tags = npc.get_tags()
        for k,v in self.reaction_modifiers:
            if k in npc_tags:
                total += v
        return total

class UniversalReactionBadge(object):
    def __init__(self,name,desc,reaction_modifier = 5):
        self.name = name
        self.desc = desc
        self.reaction_modifier = reaction_modifier
    def get_reaction_modifier(self,pc,npc,camp):
        return self.reaction_modifier
