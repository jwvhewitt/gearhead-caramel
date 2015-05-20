
class Damage( object ):
    def __init__( self, hp_damage, penetration ):
        self.hp_damage = hp_damage
        self.penetration = penetration

    def inflict( self, target ):
        """This damage is being inflicted against a gear."""


