from pbge import Singleton


# Environments

class GroundEnv(Singleton):
    name = "Ground"


class UrbanEnv(Singleton):
    name = "Urban"


class SpaceEnv(Singleton):
    name = "Space"


class AquaticEnv(Singleton):
    name = "Aquatic"

ALL_ENVIRONMENTS = (GroundEnv,UrbanEnv,SpaceEnv,AquaticEnv)

# Battlefield Roles

class Trooper(Singleton):
    name = "Trooper"


class Commander(Singleton):
    name = "Commander"


class Support(Singleton):
    name = "Support"

class EWarSupport(Singleton):
    name = "EWar Support"

ALL_ROLES = (Trooper,Commander,Support,EWarSupport)

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



# Scene Tags
class Village(Singleton):
    name = "Village"

class City(Singleton):
    name = "City"

SCENE_PUBLIC = "PUBLIC"
SCENE_SHOP = "SHOP"
SCENE_GARAGE = "GARAGE"
SCENE_HOSPITAL = "HOSPITAL"
SCENE_ARENA = "ARENA"
SCENE_BASE = "BASE"
SCENE_MEETING = "MEETING"   # A good place to meet other people.
SCENE_CULTURE = "CULTURE"   # A place to enjoy cultural activities. Music, art, whatever.
SCENE_TRANSPORT = "TRANSPORT"   # Someplace like a bus station or a spaceport
SCENE_GOVERNMENT = "GOVERNMENT"
SCENE_RUINS = "RUINS"
SCENE_SOLO = "SOLO"     # Only the PC will be deployed here.

# Shop Tags

ST_MECHA = "MECHA"
ST_WEAPON = "WEAPON"
ST_MELEEWEAPON = "MELEE WEAPON"
ST_ESSENTIAL = "ESSENTIAL"
ST_MISSILEWEAPON = "MISSILE WEAPON"
ST_CLOTHING = "CLOTHING"
ST_MECHA_EQUIPMENT = "MEXTRA"
ST_MECHA_WEAPON = "MECHA_WEAPON"

# Inventory Slots- note that these don't work exactly like slots in most RPGs.
# Multiple items can be equipped in the same place as long as none of them have the same slot.
SLOT_ITEM = "ITEM"
SLOT_SHIELD = "SHIELD"