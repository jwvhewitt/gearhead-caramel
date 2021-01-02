from pbge import container,util
import pickle
import collections

# An Egg is a container for a player character and all of that player character's associated data:
# - The PC object itself
# - Mecha and stuff
# - Lancemates, enemies, and other dramatis personae
# - Records regarding major GearHead NPCs

class Egg(object):
    def __init__(self,pc,mecha=None,stuff=(),dramatis_personae=(),major_npc_records = None,credits=0):
        # The dramatis personae are in a regular list because I need to remember who they are, not necessarily
        #    where they are.
        # The stuff is in a containerlist because these are the possessions of the PC and we need to make sure
        #    there's only one copy of each.
        # The mecha is separated from stuff because... alright, that one I don't know.
        # Probably the eject and campaign insertion code from GearHeadCampaign should be methods here, but
        #    for now I'm willing to ignore that.
        # Before ejecting an egg from a campaign, everything in the egg needs to be scrubbed of references to
        #    the game world. Also references that may lead to the game world. This means that anything in a
        #    ContainerList needs to be removed from its container, etc.
        self.pc = pc
        self.mecha = mecha
        self.stuff = container.ContainerList(stuff)
        self.dramatis_personae = list(dramatis_personae)
        self.major_npc_records = dict()
        if major_npc_records:
            self.major_npc_records.update(major_npc_records)
        self.credits = credits
        self.data = dict()
        # past_adventures lists names of adventure modules this character has done, to prevent double dipping.
        self.past_adventures = set()
        self.faction_scores = collections.defaultdict(int)

    def __setstate__(self, state):
        # For saves from V0.600 or earlier, make sure there's a faction_scores dict.
        self.__dict__.update(state)
        if "faction_scores" not in state:
            self.faction_scores = collections.defaultdict(int)

    def _remove_container_for(self,thing,con_rec):
        if hasattr(thing,"container") and thing.container:
            con_rec[thing] = thing.container
            thing.container.remove(thing)

    def _reset_container_for(self,thing, con_rec):
        if thing in con_rec:
            con_rec[thing].append(thing)

    def save( self, sfpat = 'egg_{}.sav' ):
        # Save a record of all the containers.
        con_rec = dict()
        self._remove_container_for(self.pc, con_rec)
        self._remove_container_for(self.mecha, con_rec)
        for npc in list(self.dramatis_personae):
            self._remove_container_for(npc, con_rec)
            if npc.is_destroyed():
                self.dramatis_personae.remove(npc)
        with open( util.user_dir( sfpat.format( self.pc.name ) ) , "wb" ) as f:
            pickle.dump( self , f, -1 )
        self._reset_container_for(self.pc, con_rec)
        self._reset_container_for(self.mecha, con_rec)
        for npc in self.dramatis_personae:
            self._reset_container_for(npc, con_rec)

    def backup( self ):
        # Save a record of all the containers.
        self.save(sfpat='backup_{}.sav')
