from pbge import container,util
import cPickle

# An Egg is a container for a player character and all of that player character's associated data:
# - The PC object itself
# - Mecha and stuff
# - Lancemates, enemies, and other dramatis personae
# - Records regarding major GearHead NPCs

class Egg(object):
    def __init__(self,pc,mecha=None,stuff=(),dramatis_personae=(),major_npc_records = None):
        self.pc = pc
        self.mecha = mecha
        self.stuff = container.ContainerList(stuff)
        self.dramatis_personae = list(dramatis_personae)
        self.major_npc_records = dict()
        if major_npc_records:
            self.major_npc_records.update(major_npc_records)
        # past_adventures lists names of adventure modules this character has done, to prevent double dipping.
        self.past_adventures = list()

        # _con_rec records containers for dramatis personae while saving the egg.
        self._con_rec = dict()

    def _remove_container_for(self,thing):
        if hasattr(thing,"container") and thing.container:
            self._con_rec[thing] = thing.container
            thing.container.remove(thing)
    def _reset_container_for(self,thing):
        if thing in self._con_rec:
            self._con_rec[thing].append(thing)

    def save( self ):
        # Save a record of all the containers.
        self._con_rec.clear()
        self._remove_container_for(self.pc)
        self._remove_container_for(self.mecha)
        for npc in self.dramatis_personae:
            self._remove_container_for(npc)
        with open( util.user_dir( "egg_" + self.name + ".sav" ) , "wb" ) as f:
            cPickle.dump( self , f, -1 )
        self._reset_container_for(self.pc)
        self._reset_container_for(self.mecha)
        for npc in self.dramatis_personae:
            self._reset_container_for(npc)

