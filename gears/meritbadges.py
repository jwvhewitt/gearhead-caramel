# A merit badge is a tag that the PC receives recording some achievement or life experience.
# Usually these badges give bonuses to reaction score; some might have other effects.
from gears import tags, personality, factions


class TagReactionBadge(object):
    def __init__(self,name,desc,remods = None, tags=(), contra=()):
        self.name = name
        self.desc = desc
        self.reaction_modifiers = dict()
        if remods:
            self.reaction_modifiers.update(remods)
        self.tags = set(tags)
        self.contra = list(contra)

    def get_reaction_modifier(self,pc,npc,camp):
        total = 0
        npc_tags = npc.get_tags()
        if self.reaction_modifiers:
            for k,v in self.reaction_modifiers.items():
                if k in npc_tags:
                    total += v
        return total

    def get_effect_desc(self):
        mylist = list()
        for k,v in self.reaction_modifiers.items():
            mylist.append("{:+} reaction from {} NPCs".format(v, k))
        for t in self.tags:
            mylist.append("+{} tag".format(t))
        return ", ".join(mylist)

    def __setstate__(self, state):
        # For saves from V0.820 or earlier, add tags
        self.__dict__.update(state)
        if "tags" not in state:
            self.tags = set()

    def __str__(self):
        return self.name


class UniversalReactionBadge(object):
    def __init__(self,name,desc,reaction_modifier = 5, tags=(), contra=()):
        self.name = name
        self.desc = desc
        self.reaction_modifier = reaction_modifier
        self.tags = set(tags)
        self.contra = list(contra)

    def get_reaction_modifier(self,pc,npc,camp):
        return self.reaction_modifier

    def __setstate__(self, state):
        # For saves from V0.820 or earlier, add tags
        self.__dict__.update(state)
        if "tags" not in state:
            self.tags = set()

    def get_effect_desc(self):
        mylist = list()
        mylist.append("{:+} reaction from all NPCs".format(self.reaction_modifier))
        for t in self.tags:
            mylist.append("+{} tag".format(t))
        return ", ".join(mylist)

    def __str__(self):
        return self.name


def add_badge(mylist,mybadge):
    if hasattr(mybadge, "contra"):
        for b in list(mylist):
            for opp in mybadge.contra:
                if str(b) == str(opp):
                    mylist.remove(b)
    for b in list(mylist):
        if b.name == mybadge.name:
            mylist.remove(b)
    mylist.append(mybadge)


def add_badges(mylist,badgelist):
    for b in badgelist:
        add_badge(mylist,b)


BADGE_ACADEMIC = TagReactionBadge("Academic","You are familiar with the language and culture of academia.",remods={tags.Academic:10}, tags=(tags.Academic,))
BADGE_GEARHEAD = TagReactionBadge("Gearhead","You are obsessed with mecha and anything having to do with mecha.",remods={tags.Craftsperson:10}, tags=(tags.Craftsperson,))
BADGE_POPSTAR = TagReactionBadge("Pop Star","You released a few songs and attained some notoriety as a pop star.",remods={tags.Media:10}, tags=(tags.Media,))
BADGE_SOLDIER = TagReactionBadge("Soldier","Your time in the army taught you camraderie with all who serve.",remods={tags.Military:10}, tags=(tags.Military,))
BADGE_CRIMINAL = TagReactionBadge("Criminal","You put some action in your life by breaking the law.",remods={tags.Police:-10,tags.Criminal:10}, tags=(tags.Criminal,), contra=("Police",))
BADGE_POLICE = TagReactionBadge("Police","You have worked in law enforcement.",remods={tags.Police:10,tags.Criminal:-10}, tags=(tags.Police,), contra=("Criminal",))

BADGE_AEGIS_DEFECTOR = TagReactionBadge("Aegis Defector","You have renounced all ties to Aegis Overlord Luna.",remods={factions.AegisOverlord: -10, personality.GreenZone: 5, personality.DeadZone: 5}, contra=("Aegis Collaborator",))
BADGE_AEGIS_COLLABORATOR = TagReactionBadge("Aegis Collaborator","You serve the totalitarian government of Aegis Overlord Luna.",remods={factions.AegisOverlord: 10, personality.GreenZone: -10, personality.DeadZone: -10}, contra=("Aegis Defector",))

BADGE_TURNCOAT = TagReactionBadge("Turncoat", "You have shown willingness to renege on a contract.", remods={personality.Duty: -10, tags.Adventurer: -10, tags.Military: -10}, tags={personality.Irresponsible})
