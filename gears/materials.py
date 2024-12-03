# A gear's material determines how durable it is, how heavy it is, and how
# expensive it is. This is usually relative to volume.
#
# The materials are singletons- instead of instancing, just point to the class.

from pbge import Singleton

RT_REPAIR,RT_MEDICINE,RT_BIOTECHNOLOGY = list(range(3))


class Material( Singleton ):
    # This base class is just used so all other materials count as subclasses
    # of "Material". I don't think this is an elegant way to handle things,
    # but do you have a better idea? Check out Dungeon Monkey Eternal for some
    # worse ways to handle game rule constants.
    desig = "?"
    name = "Base Material"
    mass_scale = 1.0
    damage_scale = 1.0
    cost_scale = 0
    repair_type = RT_REPAIR
    repair_cost = 1
    BONUS_ACTION_COST_MOD = 0
    DESTROYED_SOUND_FX = "hq-explosion-6288.ogg"


class Metal( Material ):
    desig = "M"
    name = "Metal"
    mass_scale = 1.0
    damage_scale = 1.0
    cost_scale = 10
    repair_type = RT_REPAIR


class Advanced( Material ):
    desig = "A"
    name = "Advanced"
    mass_scale = 0.8
    damage_scale = 1.0
    cost_scale = 20
    repair_type = RT_REPAIR


class Ceramic( Material ):
    desig = "C"
    name = "Ceramic"
    mass_scale = 0.7
    damage_scale = 0.8
    cost_scale = 15
    repair_type = RT_REPAIR


class Meat( Material ):
    desig = "meat"
    name = "Meat"
    mass_scale = 1.6
    damage_scale = 0.7
    cost_scale = 7
    repair_type = RT_MEDICINE
    repair_cost = 2
    DESTROYED_SOUND_FX = "cqccreaturedie7.ogg"


class Biotech( Material ):
    desig = "B"
    name = "Biotech"
    mass_scale = 0.9
    damage_scale = 1.5
    cost_scale = 120
    repair_type = RT_BIOTECHNOLOGY
    repair_cost = 2
    BONUS_ACTION_COST_MOD = 2
    DESTROYED_SOUND_FX = "cqccreaturedie7.ogg"


class DamageMat(Material):
    # Only used for rolling damage. Do not use this for a gear. I'll only warn you once.
    #  I never give a warning twice
    # Anything could happen like the rollin' of the dice - now!
    damage_scale = 0.4


MECHA_MATERIALS = (Metal,Advanced,Ceramic,Biotech)
