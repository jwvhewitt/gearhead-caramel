import gears
from gears import personality, tags
import game
from game.content import ghterrain, gharchitecture
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

def find_physicals(part, e_type=None):
    mylist = _check_part_for_physicals(part, e_type)
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
    "door_sign": (
        "AlliedArmorSign", "FixitShopSign", "RustyFixitShopSign", "CrossedSwordsTerrain", "KettelLogoTerrain",
        "RegExLogoTerrain", "HospitalSign", "TownBanner", "GoldTownHallSign", "MilitarySign", "GeneralStoreSign1",
        "TavernSign1", "CafeSign1", "MechaModelSign", "SkullWallSign", "JollyRogerSign", "AegisLogoSign",
        "SolarNavyLogoSign"
    ),
    "door_type": (
        "ScrapIronDoor", "GlassDoor", "ScreenDoor", "WoodenDoor"
    ),
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

SCENE_TAGS = (
    gears.tags.SCENE_BUILDING, gears.tags.SCENE_PUBLIC, gears.tags.SCENE_SHOP, gears.tags.SCENE_GARAGE,
    gears.tags.SCENE_HOSPITAL, gears.tags.SCENE_ARENA, gears.tags.SCENE_BASE, gears.tags.SCENE_MEETING,
    gears.tags.SCENE_CULTURE, gears.tags.SCENE_TRANSPORT, gears.tags.SCENE_GOVERNMENT, gears.tags.SCENE_RUINS,
    gears.tags.SCENE_SOLO, gears.tags.SCENE_DUNGEON, gears.tags.SCENE_SEMIPUBLIC, gears.tags.SCENE_FACTORY,
    gears.tags.SCENE_OUTDOORS, gears.tags.SCENE_ARENARULES, gears.tags.City, gears.tags.Village,
) + gears.personality.ORIGINS

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
    )
}

TERRAIN_TYPES = {
    "floor": (
        ghterrain.GreenZoneGrass, ghterrain.Sand, ghterrain.Flagstone, ghterrain.DeadZoneGround,
        ghterrain.SemiDeadZoneGround, ghterrain.Pavement, ghterrain.SmallDeadZoneGround, ghterrain.TechnoRubble,
        ghterrain.OldTilesFloor, ghterrain.WhiteTileFloor, ghterrain.HardwoodFloor, ghterrain.GrateFloor,
        ghterrain.CrackedEarth, ghterrain.Snow, ghterrain.SmallSnow, ghterrain.OrganicFloor, ghterrain.Water
    ),
    "wall": (
        ghterrain.FortressWall, ghterrain.ScrapIronWall, ghterrain.DefaultWall, ghterrain.CommercialWall,
        ghterrain.ResidentialWall, ghterrain.WoodenWall, ghterrain.HospitalWall, ghterrain.IndustrialWall,
        ghterrain.MSRuinedWall, ghterrain.StoneWall, ghterrain.EarthWall, ghterrain.OrganicWall,
    )
}


def get_scene_tags():
    mylist = list()
    for st in SCENE_TAGS:
        if isinstance(st, str):
            mylist.append((st,"gears.tags.{}".format(st)))
        else:
            mylist.append((st.__name__, "gears.SINGLETON_TYPES[\"{}\"]".format(st.__name__)))
    return mylist


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
        return find_physicals(part.get_root(), "gate") + [("Entry Scenario", None)]
    elif category == "dialogue_context":
        mylist = list()
        for k,v in CONTEXT_INFO.items():
            mylist.append((v.name, k))
        return mylist
    elif category == "scene_tags":
        return get_scene_tags()
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
    else:
        return find_elements(part, category)

