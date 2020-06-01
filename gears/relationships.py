import random
import collections

# Relationship tags- describe the history of this character in relation to the PC.
RT_FAMILY = "Family"
RT_SCHOOLMATE = "Schoolmate"
RT_LANCEMATE = "Lancemate"

# Attitude- the way the NPC looks at the PC.
# Note that this is a Proppian Ratchet- you can change attitude from one previous in the following order to one
#  later in the following order, but do not move backwards.
A_JUNIOR = "Junior"     # NPC is PC's junior/subordinate/student
A_SENIOR = "Senior"     # NPC is PC's senior/superior/mentor
A_RESENT = "Resent"     # NPC resents the PC for one reason or another. Maybe just because PCs are annoying.
A_FRIENDLY = "Friendly" # NPC is casually friendly with the PC
A_THANKFUL = "Thankful" # NPC is thankful to the PC for something
A_SECRETIVE = "Secretive"   # NPC is keeping some kind of secret from the PC
A_FLIRTY = "Flirty"     # NPC is casually flirty with the PC
A_EQUAL = "Equal"       # NPC regards PC as an equal
A_DISRESPECT = "Disrespect"     # NPC has lost respect for the PC
A_ENVY = "Envy"         # NPC envies the PC
A_ADMIRE = "Admire"     # NPC admires the PC
A_HATE = "Hate"         # NPC has reason to hate the PC
A_OBSESSED = "Obsessed" # NPC is obsessed with the PC

# Expectation- What the NPC is seeking, or what the NPC expects from the PC.
# Also a Proppian Ratchet.
E_MERCENARY = "Mercenary"       # NPC is in it for the money
E_IMPROVER = "Improver"         # NPC trying to lead a better life
E_PROFESSIONAL = "Professional" # NPC aims to be the best
E_RIVAL = "Rival"               # NPC just wants to beat the PC
E_GREATERGOOD = "Greater Good"  # NPC sees self as working for a greater good
E_DESPAIR = "Despair"           # NPC has been consumed by despair
E_SEEKER = "Seeker"             # NPC looking for a new way
E_AVENGER = "Avenger"           # NPC seeking retribution for some past wrong
E_REVENGE = "Revenge"           # NPC seeks revenge against the PC
E_ATONEMENT = "Atonement"       # NPC seeks atonement for some past failing
E_DOOMSEEKER = "Doomseeker"     # NPC seeks destruction
E_SATISFACTION = "Satisfaction" # NPC has become satisfied with their life
E_MEGALOMANIA = "Megalomania"   # NPC seeks to impose will on entire world
E_AMORFATI = "Amor Fati"        # NPC has accepted their own fate
E_ILLUMINATED = "Illuminated"   # NPC has attained transcendence

# Role- The NPC's relationship with the PC, explained briefly.
R_ACQUAINTANCE = "Acquaintance" # NPC knows the PC somewhat.
R_OPPONENT = "Opponent"         # NPC knows the PC somewhat, but from the enemy side.
R_COLLEAGUE = "Colleague"       # NPC knows the PC, but just in a bizness sense
R_ADVERSARY = "Adversary"       # Relationship defined by conflict
R_CRUSH = "Crush"               # NPC has possibly unrequited romantic feelings for PC
R_FRIEND = "Friend"             # NPC is on good social terms with the PC
R_ROMANCE = "Romance"           # NPC has possibly returned romantic feelings for PC
R_PARTNER = "Partner"           # NPC and PC have taken their romance to the next level, wotever that is
R_NEMESIS = "Nemesis"           # Like "Adversary" but now it's personal

# Memory Types
MEM_DefeatPC = "MEM_DefeatPC"   # The NPC defeated the PC in this memory.
MEM_LoseToPC = "MEM_LoseToPC"   # The NPC was defeated by the PC in this memory
MEM_CallItADraw = "MEM_CallItADraw" # Neither the NPC nor the PC came out clearly on top
MEM_Clash = "MEM_Clash"         # This memory is about the NPC and PC fighting
MEM_AidedByPC = "MEM_AidedByPC" # NPC got help from the PC

MEMORY_TYPES = (MEM_DefeatPC,MEM_LoseToPC,MEM_CallItADraw,MEM_Clash,MEM_AidedByPC)

class Memory(object):
    def __init__(self, npc_perspective, pc_perspective, reaction_mod=0, memtags=(), ):
        # npc_perspective is a clause in simple past describing the memory from the NPC's point of view
        # pc_perspective is a clause in simple past describing the memory from the PC's point of view
        self.npc_perspective = npc_perspective
        self.pc_perspective = pc_perspective
        self.reaction_mod = reaction_mod
        self.memtags = set(memtags)


class Relationship(object):
    # Contains info about the relationship between this NPC and the player character.
    def __init__(self,reaction_mod=0,attitude=None,expectation=None,role=None,tags=(),history=()):
        self._reaction_mod = reaction_mod
        self.attitude = attitude
        self.expectation = expectation
        self.role = role
        self.tags = set(tags)
        self.data = dict()
        self.met_before = False
        self.history = list(history)
        # The following properties are mostly for lancemates.
        self.missions_together = 0  # Increment each time NPC completes mission as part of lance
        self.development_plots = 1  # Increment each time NPC gets a character development plot
                                    # Start at 1 to prevent two plots loading simultaneously at 0/1

    def can_do_development(self):
        # Return True if this lancemate is currently eligible for a character development plot.
        return self.missions_together > self.development_plots ** 2 - self.development_plots + self.data.setdefault("DEVELOPMENT_PLOTS_APTITUDE",random.randint(1,10))

    def hilights(self):
        return ', '.join([str(self.attitude),str(self.expectation),str(self.role)])

    # Gonna set up the credits as a property.
    def _get_react(self):
        return self._reaction_mod + sum(mem.reaction_mod for mem in self.history)

    def _set_react(self,nuval):
        self._reaction_mod = nuval - sum(mem.reaction_mod for mem in self.history)

    def _del_react(self):
        self._reaction_mod = 0

    reaction_mod = property(_get_react, _set_react, _del_react)

    def get_grammar(self):
        mygram = collections.defaultdict(list)
        for mem in self.history:
            for mt in mem.memtags:
                mygram["[{}]".format(mt)].append(mem.npc_perspective)
        return mygram

    def get_pc_grammar(self):
        mygram = collections.defaultdict(list)
        for mem in self.history:
            for mt in mem.memtags:
                mygram["[{}]".format(mt)].append(mem.pc_perspective)
        return mygram

    def get_recent_memory(self, tagset=()):
        # Return the most recent memory that matches the provided tags.
        tagset = set(tagset)
        for mem in reversed(self.history):
            if mem.memtags >= tagset:
                return mem

