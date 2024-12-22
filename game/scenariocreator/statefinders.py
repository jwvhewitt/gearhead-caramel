import gears
from gears import personality, tags
import game
from game.content import ghterrain, gharchitecture, ghwaypoints, ghrooms
from game.ghdialogue import context
import pbge

# For any variable which can only be one of a set of possible states, find those states and return them as a series
# of (name,code) tuples. This will be used both for the widgets and also for validating blueprints.

def find_factions(part):
    mylist = list()
    for fac in gears.ALL_FACTIONS:
        mylist.append((fac.name, "gears.factions." + fac.__name__))

    myroot = part.get_root()
    for c in myroot.children:
        if c.brick.name == "New Sub Faction":
            mylist.append((c.raw_vars["faction_name"], "self.elements[CUSTOM_FACTIONS]['FACTION_{}']".format(c._uid)))
    mylist.append(("==None==", None))
    return mylist


def _check_part_for_physicals(part, e_type=None):
    mylist = list()
    uvars = part.get_ultra_vars()
    myelements = part.get_elements(uvars=uvars)

    for p in part.brick.physicals:
        elem = myelements[p.element_key.format(**uvars)]
        if (not e_type) or (e_type == elem.e_type):
            mylist.append((elem.name, elem.uid))

    for c in part.children:
        mylist += _check_part_for_physicals(c, e_type)

    return mylist

def find_physicals(part, e_type=None, add_none=True):
    mylist = _check_part_for_physicals(part, e_type)
    if add_none:
        mylist.append(("==None==", None))
    return mylist

class DialogueContextDescription(object):
    def __init__(self, name, desc, needed_data=()):
        self.name = name
        self.desc = desc
        self.needed_data = set(needed_data)


CONTEXT_INFO = {
    context.HELLO: DialogueContextDescription("Hello", "The NPC greets the PC."),
    context.ASK_FOR_ITEM: DialogueContextDescription("Ask For Item", "The NPC responds to the PC asking for an item.", {"item",}),
    context.INFO: DialogueContextDescription("Info", "The NPC tells the PC about a certain subject.", {"subject",}),
    context.SELFINTRO: DialogueContextDescription("Self Introduction", "The NPC tells the PC about themself."),
    context.REVEAL: DialogueContextDescription("React to Reveal", "The NPC reacts to information given by the PC.", {"reveal",}),
    context.MISSION: DialogueContextDescription("Mission", "The NPC describes a mission."),
    context.PROPOSAL: DialogueContextDescription("Proposal", "The NPC will offer a deal to the PC.", {"subject",}),
    context.CUSTOM: DialogueContextDescription("Custom", "The PC has just spoken a custom reply to the NPC.", {"reply",}),
    context.CUSTOMREPLY: DialogueContextDescription("Custom Reply", "The PC has spoken a custom reply to the previous CUSTOM offer.", {"reply",}),
    context.CUSTOMGOODBYE: DialogueContextDescription("Custom Goodbye", "The PC has spoken a custom reply and the NPC will now end the conversation.", {"reply",}),
    context.QUERY: DialogueContextDescription("Query", "The NPC asks the PC a question."),
    context.ANSWER: DialogueContextDescription("Answer", "The NPC receives an answer from the PC.", {"reply",}),
    context.SOLUTION: DialogueContextDescription("Solution", "The NPC will present a possible solution for a problem."),
    context.PROBLEM: DialogueContextDescription("Problem", "The NPC will describe a problem to the PC."),
    context.ACCEPT: DialogueContextDescription("Accept", "The PC has accepted the NPC's mission or proposal."),
    context.DENY: DialogueContextDescription("Deny", "The PC has rejected the NPC's mission or proposal."),
    context.ARREST: DialogueContextDescription("Arrest", "The NPC reacts to the PC announcing that they are under arrest."),
    context.GOODBYE: DialogueContextDescription("Goodbye", "The NPC ends the conversation."),
    context.JOIN: DialogueContextDescription("Join", "The NPC reacts to the PC asking them to join the lance."),
    context.LEAVEPARTY: DialogueContextDescription("Leave Party", "The NPC has been asked to leave the lance."),
    context.PERSONAL: DialogueContextDescription("Personal", "The NPC relates some personal information."),
    context.OPEN_SHOP: DialogueContextDescription("Open Shop", "The NPC has something to sell."),
    context.OPEN_SCHOOL: DialogueContextDescription("Open School", "The NPC will train the PC's skills."),
    context.ATTACK: DialogueContextDescription("Attack", "[Combat Only] The opening for an enemy conversation during combat."),
    context.CHALLENGE: DialogueContextDescription("Challenge", "[Combat Only] The NPC responds to the PC's challenge."),
    context.COMBAT_INFO: DialogueContextDescription("Combat Info", "[Combat Only] The NPC gives the PC some information during combat.", {"subject",}),
    context.MERCY: DialogueContextDescription("Mercy", "[Combat Only] The hostile NPC is being allowed to flee the battle."),
    context.RETREAT: DialogueContextDescription("Retreat", "[Combat Only] The NPC is retreating after being intimidated by the PC."),
    context.WITHDRAW: DialogueContextDescription("Withdraw", "[Combat Only] The NPC reacts to the PC fleeing from battle.")

}

LIST_TYPES = {
    "objectives": (
        game.content.ghplots.missionbuilder.BAMO_AID_ALLIED_FORCES,
        game.content.ghplots.missionbuilder.BAMO_CAPTURE_THE_MINE,
        game.content.ghplots.missionbuilder.BAMO_CAPTURE_BUILDINGS,
        game.content.ghplots.missionbuilder.BAMO_DEFEAT_ARMY,
        game.content.ghplots.missionbuilder.BAMO_DEFEAT_COMMANDER,
        game.content.ghplots.missionbuilder.BAMO_DEFEAT_NPC,
        game.content.ghplots.missionbuilder.BAMO_DEFEAT_THE_BANDITS,
        game.content.ghplots.missionbuilder.BAMO_DESTROY_ARTILLERY,
        game.content.ghplots.missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
        game.content.ghplots.missionbuilder.BAMO_EXTRACT_ALLIED_FORCES_VS_DINOSAURS,
        game.content.ghplots.missionbuilder.BAMO_FIGHT_DINOSAURS,
        game.content.ghplots.missionbuilder.BAMO_LOCATE_ENEMY_FORCES,
        game.content.ghplots.missionbuilder.BAMO_NEUTRALIZE_ALL_DRONES,
        game.content.ghplots.missionbuilder.BAMO_PROTECT_BUILDINGS_FROM_DINOSAURS,
        game.content.ghplots.missionbuilder.BAMO_RECOVER_CARGO,
        game.content.ghplots.missionbuilder.BAMO_RESCUE_NPC,
        game.content.ghplots.missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,
        game.content.ghplots.missionbuilder.BAMO_STORM_THE_CASTLE,
        game.content.ghplots.missionbuilder.BAMO_SURVIVE_THE_AMBUSH
    )
}

SINGULAR_TYPES = {
    "scene_generator": (
        "pbge.randmaps.SceneGenerator", "pbge.randmaps.CityGridGenerator",
        "gharchitecture.DeadZoneHighwaySceneGen"
    ),
    "architecture": (
        "gharchitecture.MechaScaleSemiDeadzone", "gharchitecture.MechaScaleDeadzone",
        "gharchitecture.MechaScaleGreenzone", "gharchitecture.MechaScaleRuins",
        "gharchitecture.MechaScaleSemiDeadzoneRuins"
    ),
    "personal_tags": (
        "personality.Cheerful", "personality.Grim", "personality.Easygoing", "personality.Passionate",
        "personality.Sociable", "personality.Shy", "personality.Justice", "personality.Peace", "personality.Glory",
        "personality.Duty", "personality.Fellowship", "personality.GreenZone", "personality.DeadZone",
        "personality.L5Spinners", "personality.L5DustyRing", "personality.Luna", "personality.Mars", "tags.Academic",
        "tags.Adventurer", "tags.CorporateWorker", "tags.Craftsperson", "tags.Criminal", "tags.Faithworker",
        "tags.Laborer", "tags.Media", "tags.Medic", "tags.Merchant", "tags.Military", "tags.Police", "tags.Politician"
    ),
    "personality_types": (
        "personality.Cheerful", "personality.Grim", "personality.Easygoing", "personality.Passionate",
        "personality.Sociable", "personality.Shy", "personality.Justice", "personality.Peace", "personality.Glory",
        "personality.Duty", "personality.Fellowship"
    ),
    "job_tags": (
        "tags.Academic",
        "tags.Adventurer", "tags.CorporateWorker", "tags.Craftsperson", "tags.Criminal", "tags.Faithworker",
        "tags.Laborer", "tags.Media", "tags.Medic", "tags.Merchant", "tags.Military", "tags.Police", "tags.Politician"
    ),
    "map_anchor": (
        "pbge.randmaps.anchors.north", "pbge.randmaps.anchors.northeast", "pbge.randmaps.anchors.east",
        "pbge.randmaps.anchors.southeast", "pbge.randmaps.anchors.south", "pbge.randmaps.anchors.southwest",
        "pbge.randmaps.anchors.west", "pbge.randmaps.anchors.northwest", "pbge.randmaps.anchors.middle",
        "None"
    ),
    "scene_tags": (
        "gears.tags.SCENE_BUILDING", "gears.tags.SCENE_PUBLIC", "gears.tags.SCENE_SHOP", "gears.tags.SCENE_GARAGE",
        "gears.tags.SCENE_HOSPITAL", "gears.tags.SCENE_ARENA", "gears.tags.SCENE_BASE", "gears.tags.SCENE_MEETING",
        "gears.tags.SCENE_CULTURE", "gears.tags.SCENE_TRANSPORT", "gears.tags.SCENE_GOVERNMENT",
        "gears.tags.SCENE_RUINS", "personality.GreenZone", "personality.DeadZone",
        "personality.L5Spinners", "personality.L5DustyRing", "personality.Luna", "personality.Mars",
        "gears.tags.SCENE_SOLO", "gears.tags.SCENE_DUNGEON", "gears.tags.SCENE_SEMIPUBLIC", "gears.tags.SCENE_FACTORY",
        "gears.tags.SCENE_OUTDOORS", "gears.tags.SCENE_ARENARULES", "gears.tags.City", "gears.tags.Village",
        "gears.tags.SCENE_VEHICLE", "gears.tags.CITY_NAUTICAL", "gears.tags.SCENE_WAREHOUSE", 
        "gears.tags.CITY_UNDERCLASS", "gears.tags.CITY_DANGEROUS", "gears.tags.CITY_UNINHABITED",
        "gears.tags.CITY_MARTIAL", "gears.tags.CITY_TRANSPORT_HUB", "gears.tags.CITY_TRADE",
        "gears.tags.CITY_CORRUPT", "gears.tags.CITY_INDUSTRIAL"
    ),
    "city_scene_generator": (
        "pbge.randmaps.CityGridGenerator", "pbge.randmaps.PartlyUrbanGenerator", "pbge.randmaps.SceneGenerator"
    ),
    "personal_scale_architecture": (
        "gharchitecture.HumanScaleGreenzone", "gharchitecture.HumanScaleDeadzone",
        "gharchitecture.HumanScaleSemiDeadzone", "gharchitecture.HumanScaleDeadzoneWilderness",
        "gharchitecture.HumanScaleForest", "gharchitecture.HumanScaleUrbanDeadzone",
        "gharchitecture.HumanScaleJunkyard",
        "gharchitecture.IndustrialBuilding", "gharchitecture.CommercialBuilding", "gharchitecture.ResidentialBuilding",
        "gharchitecture.HospitalBuilding", "gharchitecture.TentArchitecture", "gharchitecture.DefaultBuilding",
        "gharchitecture.EarthCave", "gharchitecture.FactoryBuilding", "gharchitecture.FortressBuilding",
        "gharchitecture.OrganicBuilding", "gharchitecture.ScrapIronWorkshop", "gharchitecture.StoneBuilding",
        "gharchitecture.StoneCave", "gharchitecture.VehicleArchitecture", "gharchitecture.WarmColorsWallArchitecture",
        "gharchitecture.CoolColorsWallArchitecture", "gharchitecture.DingyResidentialArchitecture",
        "gharchitecture.SewerArchitecture", "gharchitecture.DerelictArchitecture", "gharchitecture.AegisArchitecture"
    ),
    'terrain_set': (
        "ghterrain.CorsairTerrset",
    ),
    'waypoint': (
        "ghwaypoints.Bunk", "ghwaypoints.MechEngTerminal", "ghwaypoints.AmmoBox",
        "ghwaypoints.Biotank", "ghwaypoints.BoardingChute", "ghwaypoints.Bookshelf", "ghwaypoints.BrokenBiotank",
        "ghwaypoints.ClosedBoardingChute", "ghwaypoints.Crate", "ghwaypoints.EarthMap", "ghwaypoints.EmptyBiotank",
        "ghwaypoints.GoldPlaque", "ghwaypoints.HamsterCage", "ghwaypoints.Herbs", "ghwaypoints.KenneyCratesWP",
        "ghwaypoints.KenneyWoodenTableWP", "ghwaypoints.Lockers", "ghwaypoints.OccupiedBed", "ghwaypoints.OldCrate",
        "ghwaypoints.OldTerminal", "ghwaypoints.OldMainframe", "ghwaypoints.OrganicTube",
        "ghwaypoints.PZHolo", "ghwaypoints.RecoveryBed", "ghwaypoints.RetroComputer", "ghwaypoints.ShippingShelves",
        "ghwaypoints.Shrine", "ghwaypoints.Skeleton", "ghwaypoints.SkullTownSign", "ghwaypoints.StorageBox",
        "ghwaypoints.TrailSign", "ghwaypoints.Trapdoor", "ghwaypoints.UlsaniteFilingCabinet",
        "ghwaypoints.VendingMachine", "ghwaypoints.Victim", "ghwaypoints.WallMap", "ghwaypoints.TattooChair",
        "ghwaypoints.HarpyModel", "ghwaypoints.VadelModel", "ghwaypoints.KojedoModel",
        "ghwaypoints.GladiusModel", "ghwaypoints.BuruBuruModel", "ghwaypoints.ClaymoreModel",
        "ghwaypoints.ParkStatueSynth", "ghwaypoints.ParkStatueSerpent", "ghwaypoints.ParkStatueMecha",
        "ghwaypoints.ParkStatueWoman", "ghwaypoints.ParkStatueMan", "ghwaypoints.StatueF", "ghwaypoints.StatueM",
        "ghwaypoints.KnifeNote"
    ),
    "door_type": (
        "ghwaypoints.ScrapIronDoor", "ghwaypoints.GlassDoor", "ghwaypoints.ScreenDoor", "ghwaypoints.WoodenDoor",
        "ghwaypoints.ReinforcedDoor", "ghwaypoints.LockedReinforcedDoor"
    ),
    "building_terrset": (
        "ghterrain.BrickBuilding", "ghterrain.IndustrialBuilding", "ghterrain.CommercialBuilding",
        "ghterrain.ConcreteBuilding", "ghterrain.ResidentialBuilding", "ghterrain.ScrapIronBuilding"
    ),
    "exterior_architecture": (
        "gharchitecture.HumanScaleGreenzone", "gharchitecture.HumanScaleDeadzone",
        "gharchitecture.HumanScaleSemiDeadzone", "gharchitecture.HumanScaleDeadzoneWilderness",
        "gharchitecture.HumanScaleForest", "gharchitecture.HumanScaleUrbanDeadzone",
        "gharchitecture.HumanScaleJunkyard",
    ),
    "interior_architecture": (
        "gharchitecture.IndustrialBuilding", "gharchitecture.CommercialBuilding", "gharchitecture.ResidentialBuilding",
        "gharchitecture.HospitalBuilding", "gharchitecture.TentArchitecture", "gharchitecture.DefaultBuilding",
        "gharchitecture.EarthCave", "gharchitecture.FactoryBuilding", "gharchitecture.FortressBuilding",
        "gharchitecture.OrganicBuilding", "gharchitecture.ScrapIronWorkshop", "gharchitecture.StoneBuilding",
        "gharchitecture.StoneCave", "gharchitecture.VehicleArchitecture", "gharchitecture.WarmColorsWallArchitecture",
        "gharchitecture.CoolColorsWallArchitecture", "gharchitecture.DingyResidentialArchitecture",
        "gharchitecture.SewerArchitecture", "gharchitecture.DerelictArchitecture", "gharchitecture.AegisArchitecture"
    ),
    "interior_decor": (
        "gharchitecture.DungeonDecor", "gharchitecture.FactoryDecor", "gharchitecture.DefiledFactoryDecor",
        "gharchitecture.CheeseShopDecor", "gharchitecture.BunkerDecor", "gharchitecture.CaveDecor",
        "gharchitecture.ColumnsDecor", "gharchitecture.MysteryDungeonDecor", "gharchitecture.OfficeDecor",
        "gharchitecture.ResidentialDecor", "gharchitecture.OrganicStructureDecor", "gharchitecture.SewerDecor",
        "gharchitecture.RundownChemPlantDecor", "gharchitecture.RundownFactoryDecor",
        "gharchitecture.StorageRoomDecor", "gharchitecture.TechDungeonDecor", "gharchitecture.ToxicCaveDecor",
        "gharchitecture.StoneUndercityDecor", "gharchitecture.UlsaniteOfficeDecor", "None"
    ),
    "door_sign": (
        "AlliedArmorSign", "FixitShopSign", "RustyFixitShopSign", "CrossedSwordsTerrain", "KettelLogoTerrain",
        "RegExLogoTerrain", "HospitalSign", "TownBanner", "GoldTownHallSign", "MilitarySign", "GeneralStoreSign1",
        "TavernSign1", "CafeSign1", "MechaModelSign", "SkullWallSign", "JollyRogerSign", "AegisLogoSign",
        "SolarNavyLogoSign", "DragonSign", "None", "KirasTattoosSign", "GunShopSign", "YeOldeShopSign", "ShieldSign",
        "BladesOfCrihnaSign"
    ),
    "shop_type": (
        "game.services.GENERAL_STORE", "game.services.GENERAL_STORE_PLUS_MECHA", "game.services.MECHA_STORE",
        "game.services.MECHA_PARTS_STORE", "game.services.MECHA_WEAPON_STORE", "game.services.TIRE_STORE",
        "game.services.ARMOR_STORE", "game.services.BARE_ESSENTIALS_STORE", "services.BLACK_MARKET",
        "game.services.PHARMACY"
    ),
    "room": (
        "pbge.randmaps.rooms.FuzzyRoom", "pbge.randmaps.rooms.OpenRoom", "pbge.randmaps.rooms.ClosedRoom",
        "ghrooms.LakeRoom", "ghrooms.MSRuinsRoom", "ghrooms.WreckageRoom", "ghrooms.BarArea", "ghrooms.BushesRoom",
        "ghrooms.DragonToothRoom", "ghrooms.ForestRoom", "ghrooms.GrassRoom", "ghrooms.ToxicSludgeRoom"
    ),
    "monster_tags": (
        "AIR", "ANIMAL", "BRIGHT", "BUG", "CAVE", "CITY", "CREEPY", "DARK", "DESERT", "DEVO", "DINOSAUR", "EARTH",
        "EXOTIC", "FACTORY", "FIRE", "FOREST", "GREEN", "GUARD", "HUNTER-X", "JUNGLE", "MINE", "MOUNTAIN", "MUTANT",
        "REPTILE", "ROBOT", "RUINS", "SWAMP", "SYNTH", "TOXIC", "VERMIN", "WASTELAND", "WATER", "ZOMBOT"
    ),
    "container_waypoint": (
        "ghwaypoints.OldCrate", "ghwaypoints.Skeleton", "ghwaypoints.StorageBox", "ghwaypoints.AmmoBox",
        "ghwaypoints.SteelBox", "ghwaypoints.LockedSteelBox"
    ),
    "exit_types": (
        "ghwaypoints.Exit", "ghwaypoints.ScrapIronDoor", "ghwaypoints.GlassDoor", "ghwaypoints.ScreenDoor",
        "ghwaypoints.WoodenDoor", "ghwaypoints.Trapdoor", "ghwaypoints.StairsUp", "ghwaypoints.StairsDown",
        "ghwaypoints.StoneStairsUp", "ghwaypoints.UndergroundEntrance", "ghwaypoints.ReinforcedDoor",
        "ghwaypoints.LockedReinforcedDoor"
    )

}

TERRAIN_TYPES = {
    "floor": (
        ghterrain.GreenZoneGrass, ghterrain.Sand, ghterrain.Flagstone, ghterrain.DeadZoneGround,
        ghterrain.SemiDeadZoneGround, ghterrain.Pavement, ghterrain.SmallDeadZoneGround, ghterrain.TechnoRubble,
        ghterrain.OldTilesFloor, ghterrain.WhiteTileFloor, ghterrain.HardwoodFloor, ghterrain.GrateFloor,
        ghterrain.CrackedEarth, ghterrain.Snow, ghterrain.SmallSnow, ghterrain.OrganicFloor, ghterrain.Water,
        ghterrain.GreenTileFloor, ghterrain.GravelFloor
    ),
    "wall": (
        ghterrain.FortressWall, ghterrain.ScrapIronWall, ghterrain.DefaultWall, ghterrain.CommercialWall,
        ghterrain.ResidentialWall, ghterrain.WoodenWall, ghterrain.HospitalWall, ghterrain.IndustrialWall,
        ghterrain.MSRuinedWall, ghterrain.StoneWall, ghterrain.EarthWall, ghterrain.OrganicWall,
        ghterrain.VehicleWall
    )
}


def find_elements(part, e_type):
    mylist = list()
    for k, fac in part.get_elements().items():
        if fac.e_type == e_type:
            mylist.append((fac.name, "self.elements[\"{}\"]".format(k)))
    mylist.append(("==None==", None))
    return mylist


def find_world_maps(part):
    mylist = list()
    myroot = part.get_root()
    for c in myroot.children:
        if c.brick.name == "New World Map":
            mylist.append((c.raw_vars["world_map_name"], "'WORLDMAP_{}'".format(c.uid)))
    mylist.append(("==None==", None))
    return mylist


def get_possible_states(part, category: str):
    if category == "faction":
        return find_factions(part)
    elif category.startswith("physical:"):
        return find_physicals(part.get_root(), category[9:])
    elif category == "starting_point":
        return find_physicals(part.get_root(), "gate", add_none=False) + [("Entry Scenario", None)]
    elif category == "dialogue_context":
        mylist = list()
        for k,v in CONTEXT_INFO.items():
            mylist.append((v.name, k))
        return mylist
    elif category.endswith(".png"):
        return [(a,'"{}"'.format(a)) for a in pbge.image.glob_images(category)] + [("None", None),]
    elif category in LIST_TYPES:
        return [(a,a) for a in LIST_TYPES[category]]
    elif category in SINGULAR_TYPES:
        return [(a.rpartition(".")[2], a) for a in SINGULAR_TYPES[category]]
    elif category.startswith("terrain:") and category[8:] in TERRAIN_TYPES:
        return [(a.__name__, "ghterrain.{}".format(a.__name__)) for a in TERRAIN_TYPES[category[8:]]]
    elif category == "world_map":
        return find_world_maps(part)
    elif category == "job":
        return list((k, "gears.jobs.ALL_JOBS['{}']".format(k)) for k in gears.jobs.ALL_JOBS.keys()) + [("None", None),]
    elif category == "major_npc_id":
        return list([(npc.name, "'{}'".format(npc.mnpcid)) for npc in gears.selector.STC_LIST if isinstance(npc, gears.base.Character) and npc.mnpcid])
    else:
        return find_elements(part, category)


def is_legal_state(part, state_type, state_value):
    my_names_and_states = get_possible_states(part, state_type)
    mystates = [a[1] for a in my_names_and_states]
    mystates.append(None)
    return state_value in mystates


