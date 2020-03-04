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
    name = "Base Material"
    mass_scale = 0
    damage_scale = 0
    cost_scale = 0
    repair_type = RT_REPAIR
    repair_cost = 1

class Metal( Material ):
    name = "Metal"
    mass_scale = 10
    damage_scale = 5
    cost_scale = 10
    repair_type = RT_REPAIR

class Advanced( Material ):
    name = "Advanced"
    mass_scale = 8
    damage_scale = 5
    cost_scale = 50
    repair_type = RT_REPAIR

class Ceramic( Material ):
    name = "Ceramic"
    mass_scale = 9
    damage_scale = 4
    cost_scale = 15
    repair_type = RT_REPAIR

class Meat( Material ):
    name = "Meat"
    mass_scale = 16
    damage_scale = 4
    cost_scale = 7
    repair_type = RT_MEDICINE
    repair_cost = 2

class Biotech( Material ):
    name = "Biotech"
    mass_scale = 9
    damage_scale = 6
    cost_scale = 120
    repair_type = RT_BIOTECHNOLOGY
    repair_cost = 2


MECHA_MATERIALS = (Metal,Advanced,Ceramic,Biotech)
