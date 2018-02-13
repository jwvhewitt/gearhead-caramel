from pbge import Singleton

#  ***************
#  ***  STATS  ***
#  ***************

class Stat( Singleton ):
    @classmethod
    def __str__(self):
        return self.name

class Reflexes( Stat ):
    name = 'Reflexes'

class Body( Stat ):
    name = 'Body'

class Speed( Stat ):
    name = 'Speed'

class Perception( Stat ):
    name = 'Perception'

class Craft( Stat ):
    name = 'Craft'

class Ego( Stat ):
    name = 'Ego'

class Knowledge( Stat ):
    name = 'Knowledge'

class Charm( Stat ):
    name = 'Charm'

PRIMARY_STATS = (Reflexes,Body,Speed,Perception,Craft,Ego,Knowledge,Charm)

#  ****************
#  ***  SKILLS  ***
#  ****************

class Skill( Singleton ):
    @classmethod
    def __str__(self):
        return self.name

class MechaGunnery( Skill ):
    name = 'Mecha Gunnery'

class MechaFighting( Skill ):
    name = 'Mecha Fighting'

class MechaPiloting( Skill ):
    name = 'Mecha Piloting'

class RangedCombat( Skill ):
    name = 'Ranged Combat'

class CloseCombat( Skill ):
    name = 'Close Combat'

class Dodge( Skill ):
    name = 'Dodge'

class Repair( Skill ):
    name = 'Repair'

class Medicine( Skill ):
    name = 'Medicine'

class Biotechnology( Skill ):
    name = 'Biotechnology'

class Stealth( Skill ):
    name = 'Stealth'

class Science( Skill ):
    name = 'Science'

class Computers( Skill ):
    name = 'Computers'

class Performance( Skill ):
    name = 'Performance'

class Negotiation( Skill ):
    name = 'Negotiation'

class Scouting( Skill ):
    name = 'Scouting'

class DominateAnimal( Skill ):
    name = 'Dominate Animal'

class Vitality( Skill ):
    name = 'Vitality'

class Athletics( Skill ):
    name = 'Athletics'

class Concentration( Skill ):
    name = 'Concentration'












