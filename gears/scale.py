# A gear's scale determines how big of a thing we're talking about.
# There are two scales: MechaScale and HumanScale. The first is really
# really big and the second is relatively tiny.
#
# The scales are singletons- instead of instancing, just point to the class.

from . import stats

class MechaScale( object ):
    SIZE_FACTOR = 10
    RANGE_FACTOR = 2
    COST_FACTOR = 1.60
    RANGED_SKILL = stats.MechaGunnery
    MELEE_SKILL = stats.MechaFighting
    XP_MULTIPLIER = 1
    DEFAULT_DAMAGE_DIE = 4
    BONUS_ACTION_BASE_COST = 10
    @classmethod
    def scale_mass( cls, mass, material ):
        # Scale mass based on scale and material.
        # The universal mass unit is 100 grams.
        return int(mass * pow( cls.SIZE_FACTOR, 3 ) * material.mass_scale )
    @classmethod
    def unscale_mass( cls, mass ):
        # Convert a real mass to a value in scale units.
        return int( mass / pow( cls.SIZE_FACTOR, 3 ) )
    @classmethod
    def scale_cost( cls, cost , material ):
        # Scale mass based on scale and material.
        return int( cost * cls.SIZE_FACTOR*cls.COST_FACTOR * material.cost_scale ) // 10
    @classmethod
    def scale_health( cls, hp , material ):
        # Scale mass based on scale and material.
        return int( hp * cls.SIZE_FACTOR ** 2 * 2.5 * material.damage_scale + 0.5 )
    @classmethod
    def scale_power( cls, power ):
        return power * cls.SIZE_FACTOR ** 2
    @staticmethod
    def get_mass_string( mass ):
        return '{:.1f} tons'.format(mass / 10000.0)

class HumanScale( MechaScale ):
    SIZE_FACTOR = 1
    RANGE_FACTOR = 1
    COST_FACTOR = 5.0
    RANGED_SKILL = stats.RangedCombat
    MELEE_SKILL = stats.CloseCombat
    XP_MULTIPLIER = 2
    DEFAULT_DAMAGE_DIE = 6
    BONUS_ACTION_BASE_COST = 5
    @staticmethod
    def get_mass_string( mass ):
        return '{:.1f}kg'.format(mass / 10.0)

class WorldScale( MechaScale ):
    SIZE_FACTOR = 100
    RANGE_FACTOR = 3

