# A merit badge is a tag that the PC receives recording some achievement or life experience.
# Usually these badges give bonuses to reaction score; some might have other effects.
from gears import tags


class TagReactionBadge(object):
    def __init__(self,name,desc,remods = None):
        self.name = name
        self.desc = desc
        self.reaction_modifiers = dict()
        if remods:
            self.reaction_modifiers.update(remods)
    def get_reaction_modifier(self,pc,npc,camp):
        total = 0
        npc_tags = npc.get_tags()
        if self.reaction_modifiers:
            for k,v in self.reaction_modifiers.iteritems():
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



BADGE_ACADEMIC = TagReactionBadge("Academic","You are familiar with the language and culture of academia.",remods={tags.Academic:10})
BADGE_GEARHEAD = TagReactionBadge("Gearhead","You are obsessed with mecha and anything having to do with mecha.",remods={tags.Craftsperson:10})
BADGE_POPSTAR = TagReactionBadge("Pop Star","You released a few songs and attained some notoriety as a pop star.",remods={tags.Media:10})
BADGE_SOLDIER = TagReactionBadge("Soldier","Your time in the army taught you camraderie with all who serve.",remods={tags.Military:10})
BADGE_CRIMINAL = TagReactionBadge("Criminal","",remods={tags.Police:-10,tags.Criminal:10})