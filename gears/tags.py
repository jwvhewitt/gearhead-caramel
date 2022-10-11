from pbge import Singleton
from pbge.scenes import movement


#  ***************************
#  ***   Movement  Modes   ***
#  ***************************

class Skimming(movement.MoveMode):
    name = 'skim'
    altitude = 1


class Rolling(movement.MoveMode):
    name = 'roll'


class SpaceFlight(movement.MoveMode):
    name = 'space flight'

    @classmethod
    def get_short_name(cls):
        return 'space'


class Jumping(movement.MoveMode):
    name = 'jump'


class Cruising(movement.MoveMode):
    name = 'cruise'


class Crashed(movement.MoveMode):
    # Crash the the movemode you get set to when you crash.
    name = 'crash'


MOVEMODE_LIST = (movement.Walking, movement.Flying, Skimming, Rolling, SpaceFlight, Cruising)


def model_matches_environment(model, enviro):
    if not enviro:
        return True
    for mm in enviro.LEGAL_MOVEMODES:
        if model.get_speed(mm) > 0:
            return True


# Environments


class GroundEnv(Singleton):
    name = "Ground"
    LEGAL_MOVEMODES = (Rolling, Skimming, movement.Walking, movement.Flying)
    HAS_CEILING = False
    DEEP_SPACE = False


class UrbanEnv(Singleton):
    name = "Urban"
    LEGAL_MOVEMODES = (Rolling, Skimming, movement.Walking)
    HAS_CEILING = False
    DEEP_SPACE = False


class SpaceEnv(Singleton):
    name = "Space"
    LEGAL_MOVEMODES = (SpaceFlight,)
    HAS_CEILING = False
    DEEP_SPACE = True


class AquaticEnv(Singleton):
    name = "Aquatic"
    LEGAL_MOVEMODES = (Skimming, movement.Flying)
    HAS_CEILING = False
    DEEP_SPACE = False


ALL_ENVIRONMENTS = (GroundEnv, UrbanEnv, SpaceEnv, AquaticEnv)


# Battlefield Roles

class Trooper(Singleton):
    name = "Trooper"


class Commander(Singleton):
    name = "Commander"


class Support(Singleton):
    name = "Support"


class EWarSupport(Singleton):
    name = "EWar Support"


ALL_ROLES = (Trooper, Commander, Support, EWarSupport)


# Job tags
class Academic(Singleton):
    name = "Academic"


class Adventurer(Singleton):
    name = "Adventurer"


class CorporateWorker(Singleton):
    name = "Corporate Worker"


class Craftsperson(Singleton):
    name = "Craftsperson"


class Criminal(Singleton):
    name = "Criminal"


class Faithworker(Singleton):
    name = "Faithworker"


class Laborer(Singleton):
    name = "Laborer"


class Media(Singleton):
    name = "Media"


class Medic(Singleton):
    name = "Medic"


class Merchant(Singleton):
    name = "Merchant"


class Military(Singleton):
    name = "Military"


class Police(Singleton):
    name = "Police"


class Politician(Singleton):
    name = "Politician"

PROFESSIONS = (Academic, Adventurer, CorporateWorker, Craftsperson, Criminal, Faithworker, Laborer, Media, Medic,
               Merchant, Military, Police, Politician)

# Miscellaneous character types

COMBATANT = "Combatant"


# Scene Tags
class Village(Singleton):
    name = "Village"


class City(Singleton):
    name = "City"


SCENE_BUILDING = "BUILDING"
SCENE_PUBLIC = "PUBLIC"
SCENE_SHOP = "SHOP"
SCENE_GARAGE = "GARAGE"
SCENE_HOSPITAL = "HOSPITAL"
SCENE_ARENA = "ARENA"
SCENE_BASE = "BASE"
SCENE_MEETING = "MEETING"  # A good place to meet other people.
SCENE_CULTURE = "CULTURE"  # A place to enjoy cultural activities. Music, art, whatever.
SCENE_TRANSPORT = "TRANSPORT"  # Someplace like a bus station or a spaceport
SCENE_GOVERNMENT = "GOVERNMENT"
SCENE_RUINS = "RUINS"
SCENE_SOLO = "SOLO"  # Only the PC will be deployed here.
SCENE_DUNGEON = "DUNGEON"
SCENE_SEMIPUBLIC = "SEMIPUBLIC"  # No-one is stopping you from going there. Usually used for dungeons.
SCENE_FACTORY = "FACTORY"
SCENE_OUTDOORS = "OUTDOORS"
SCENE_ARENARULES = "ARENARULES"  # No death, no permanent loss of mecha possible.
SCENE_NOLEADERNEEDED = "NO_LEADER_NEEDED"  # This Metroscene doesn't need a leader, so don't replace the leader if None
SCENE_MINE = "MINE"  # This scene is mine. Actually it's _a_ mine. But it's still mine.
SCENE_CAVE = "CAVE"  # This scene is a semi-natural underground area
SCENE_LABORATORY = "LABORATORY"     # A science lab of some type.
SCENE_FOREST = "FOREST"
SCENE_VEHICLE = "VEHICLE"
SCENE_WAREHOUSE = "WAREHOUSE"

CITY_NAUTICAL = "NAUTICAL" # A city by the sea

# Shop Tags

ST_MECHA = "MECHA"
ST_WEAPON = "WEAPON"
ST_MELEEWEAPON = "MELEE WEAPON"
ST_ESSENTIAL = "ESSENTIAL"
ST_MISSILEWEAPON = "MISSILE WEAPON"
ST_CLOTHING = "CLOTHING"
ST_MECHA_MOBILITY = "MMOBILITY"
ST_MECHA_EQUIPMENT = "MEXTRA"
ST_MECHA_WEAPON = "MECHA_WEAPON"
ST_MEDICINE = "MEDICINE"
ST_CYBERWARE = "CYBERWARE"
ST_TREASURE = "TREASURE"
ST_LOSTECH = "LOSTECH"
ST_MINERAL = "MINERAL"
ST_GEMSTONE = "GEMSTONE"
ST_ODDITY = "ODDITY"
ST_JEWELRY = "JEWELRY"
ST_ANTIQUE = "ANTIQUE"
ST_CONTRABAND = "CONTRABAND"
ST_TOOL = "TOOL"
ST_SURVIVAL = "SURVIVAL"

# Inventory Slots- note that these don't work exactly like slots in most RPGs.
# Multiple items can be equipped in the same place as long as none of them have the same slot.
SLOT_ITEM = "ITEM"
SLOT_SHIELD = "SHIELD"
