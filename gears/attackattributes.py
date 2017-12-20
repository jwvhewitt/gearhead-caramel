from pbge import Singleton

class Automatic(Singleton):
    # This weapon has two extra modes: x5 ammo for 2 shots, or x10 ammo for 3 shots

    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.0

    @classmethod
    def get_attacks( self, weapon, user ):
        return [weapon.get_basic_attack(name='2 shots, x5 ammo',targets=2,ammo_cost=5,attack_icon=3),
                weapon.get_basic_attack(name='3 shots, x10 ammo',targets=3,ammo_cost=10,attack_icon=6)]


