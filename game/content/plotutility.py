from pbge.dialogue import Offer, ContextTag
from . import ghwaypoints
import random
import pbge
import gears
from game.content import GHNarrativeRequest, PLOT_LIST
from ..ghdialogue import context, ghgrammar


class AdventureModuleData(object):
    def __init__(self, name, desc, date, title_card, character_check_fun=None, convoborder=None):
        # date is a tuple in (year, month, day) format. Day is optional. GH1 took place in 157, GH2 in 162.
        # character_check_fun is a function that takes the PC's Egg as a parameter and returns True if the PC can
        #    take part in this adventure.
        self.name = name
        self.desc = desc
        self.date = date
        self.title_card = title_card
        self.character_check_fun = character_check_fun
        self.convoborder = convoborder

    def can_play(self, egg: gears.eggs.Egg):
        base = pbge.util.config.getboolean("GENERAL", "can_replay_adventures") or self.name not in egg.past_adventures
        if self.character_check_fun:
            return base and self.character_check_fun(egg)
        else:
            return base

    def apply(self, camp: gears.GearHeadCampaign):
        camp.year = self.date[0]
        # Compatibility code for v0.600 and previous: past_adventures used to be a list, but we wanna make sure
        # it's a set.
        if not isinstance(camp.egg.past_adventures, set):
            camp.egg.past_adventures = set()
        camp.egg.past_adventures.add(self.name)
        if self.convoborder:
            camp.convoborder = self.convoborder


class SceneConnection(object):
    DEFAULT_ROOM_1 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_ROOM_1_W = 3
    DEFAULT_ROOM_1_H = 3
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_ROOM_2_W = 5
    DEFAULT_ROOM_2_H = 5
    DEFAULT_DOOR_1 = ghwaypoints.Exit
    DEFAULT_DOOR_2 = ghwaypoints.Exit

    def __init__(self, nart, plot, scene1, scene2, room1=None, room1_id=None, room2=None, room2_id=None, anchor1=None,
                 anchor2=None, door1=None, door1_id=None, door2=None, door2_id=None, move_door1=True, move_door2=True):
        self.nart = nart
        self.scene1 = scene1
        self.scene2 = scene2
        if not room1:
            room1 = plot.register_element(room1_id, self.DEFAULT_ROOM_1(self.DEFAULT_ROOM_1_W, self.DEFAULT_ROOM_1_H,
                                                                        parent=scene1,
                                                                        anchor=anchor1 or self.get_room1_anchor()))
            plot.place_element(room1, scene1)
        self.room1 = room1
        if not room2:
            room2 = plot.register_element(room2_id, self.DEFAULT_ROOM_2(self.DEFAULT_ROOM_2_W, self.DEFAULT_ROOM_2_H,
                                                                        parent=scene2,
                                                                        anchor=anchor2 or self.get_room2_anchor()))
            plot.place_element(room2, scene2)
        self.room2 = room2
        if not door1:
            door1 = plot.register_element(door1_id, self.get_door1())
        if move_door1:
            plot.place_element(door1, room1)
        self.door1 = door1
        if not door2:
            door2 = plot.register_element(door2_id, self.get_door2())
        if move_door2:
            plot.place_element(door2, room2)
        self.door2 = door2
        self.door1.dest_wp = self.door2
        self.door2.dest_wp = self.door1

    def get_room1_anchor(self):
        return None

    def get_room2_anchor(self):
        return None

    def get_door1(self):
        return self.DEFAULT_DOOR_1(anchor=pbge.randmaps.anchors.middle)

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.middle)


class NatureTrailConnection(SceneConnection):
    DEFAULT_DOOR_1 = ghwaypoints.TrailSign

    def get_room1_anchor(self):
        scenegen = self.nart.get_map_generator(self.scene1)
        if scenegen and scenegen.edge_positions:
            return scenegen.edge_positions.pop()

    def get_room2_anchor(self):
        scenegen = self.nart.get_map_generator(self.scene2)
        if scenegen and scenegen.edge_positions:
            return scenegen.edge_positions.pop()


class TownBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.ClosedRoom

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMCommTowerConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDWCommTower
    r2anchor = pbge.randmaps.anchors.middle

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class IntCommTowerConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDCommTower

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMConcreteBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDWConcreteBuilding
    r2anchor = None

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class IntConcreteBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDConcreteBuilding

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMDZTownConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDTown
    r2anchor = None

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class StairsDownToStairsUpConnector(SceneConnection):
    DEFAULT_DOOR_1 = ghwaypoints.StairsDown
    DEFAULT_DOOR_2 = ghwaypoints.StairsUp

    def get_room1_anchor(self):
        return pbge.randmaps.anchors.middle

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.middle


class TrapdoorToStairsUpConnector(SceneConnection):
    DEFAULT_DOOR_1 = ghwaypoints.Trapdoor
    DEFAULT_DOOR_2 = ghwaypoints.StairsUp

    def get_room1_anchor(self):
        return pbge.randmaps.anchors.middle

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.middle


class StairsUpToStairsDownConnector(StairsDownToStairsUpConnector):
    DEFAULT_DOOR_1 = ghwaypoints.StairsUp
    DEFAULT_DOOR_2 = ghwaypoints.StairsDown


class RandomBanditCircle(gears.factions.Circle):
    CHART_A = ("Brutal", "Cruel", "Desert", "Deadly", "Frenzied", "Angry", "Despicable", "Evil", "Freaky", "Greedy",
               "Glorious", "Hellbound", "Horrid", "Invincible", "Jolly", "Killer", "Lucky", "Larcenous", "Murderous",
               "Merciless", "Nasty", "Pierced", "Rancid", "Razor", "Speed", "Savage", "Terrible", "Thunder", "Jugular",
               "Unbeatable", "Vicious", "Violent", "Red", "Bloody", "Wanton", "Xtreem", "Heavy Metal", "Blood Pact")
    CHART_B = (
        "Warriors", "Bandits", "Pirates", "Demons", "Gang", "Hooligans", "Destroyers", "Raiders", "Droogs", "Modez",
        "Breakers", "Bruisers", "Crashers", "Executors", "Frenz", "Grabberz", "Hammers", "Jokerz", "Killerz",
        "Mob", "Ogres", "Queenz", "Kingz", "Raptors", "Slashers", "Titanz", "Vizigoths", "Freakz", "Junk Ratz",
        "Rippers", "Gougers", "Horde")

    def __init__(self, camp, **kwargs):
        parent_faction = random.choice(
            [gears.factions.BoneDevils, gears.factions.BoneDevils, gears.factions.BladesOfCrihna, None])
        if parent_faction and random.randint(1, 3) != 1:
            name = parent_faction.get_circle_name()
        else:
            name = "the {} {}".format(random.choice(self.CHART_A), random.choice(self.CHART_B))
        super().__init__(camp, name=name, parent_faction=parent_faction, **kwargs)
        if gears.tags.Criminal not in self.factags:
            self.factags.append(gears.tags.Criminal)


class CargoContainer(gears.base.Prop):
    DEFAULT_COLORS = (
    gears.color.White, gears.color.Aquamarine, gears.color.DeepGrey, gears.color.Black, gears.color.GullGrey)

    def __init__(self, name="Shipping Container", size=1, colors=None, imagename="prop_shippingcontainer.png",
                 **kwargs):
        super(CargoContainer, self).__init__(name=name, size=size, imagename=imagename, **kwargs)
        self.colors = colors or self.DEFAULT_COLORS

    @staticmethod
    def random_fleet_colors():
        return [random.choice(gears.color.MECHA_COLORS),
                random.choice(gears.color.DETAIL_COLORS),
                random.choice(gears.color.METAL_COLORS),
                gears.color.Black,
                random.choice(gears.color.MECHA_COLORS)]

    @classmethod
    def generate_cargo_fleet(cls, rank, colors=None):
        if not colors:
            colors = cls.random_fleet_colors()
        myfleet = [cls(colors=colors) for t in range(random.randint(2, 3) + max(0, rank // 25))]
        return myfleet


class AutoJoiner(object):
    # A callable to handle lancemate join requests. The NPC will join the party,
    # bringing along any mecha and pets they may have.
    def __init__(self, npc: gears.base.Character):
        """
        Prepare to add the NPC to the party.
        :type npc: gears.base.Character
        """
        self.npc = npc

    def _get_pet_from_campdata(self, camp: gears.GearHeadCampaign):
        return camp.campdata.get(("PET", self.npc))

    def __call__(self, camp):
        """
        Add the NPC to the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc not in camp.party:
            camp.party.append(self.npc)
            mek = self.get_mecha_for_character(self.npc)
            self.add_lancemate_mecha_to_party(camp, self.npc, mek)
            if camp.scene:
                camp.scene.local_teams[self.npc] = camp.scene.player_team
            pet = self._get_pet_from_campdata(camp)
            if pet:
                camp.party.append(pet)
                if camp.scene:
                    camp.scene.local_teams[pet] = camp.scene.player_team
                    if pet not in camp.scene.contents and pet.scale is camp.scene.scale and self.npc in camp.scene and self.npc.pos:
                        camp.scene.place_gears_near_spot(*self.npc.pos, camp.scene.player_team, pet)

    @staticmethod
    def add_lancemate_mecha_to_party(camp, npc, mek):
        camp.party.append(mek)
        camp.assign_pilot_to_mecha(npc, mek)
        for part in mek.get_all_parts():
            part.owner = npc

    @staticmethod
    def get_mecha_for_character(npc, choose_new_one=False):
        if not npc.mecha_colors:
            npc.mecha_colors = gears.color.random_mecha_colors()
            if random.randint(1,3) == 2:
                npc.mecha_colors = (npc.colors[0], *npc.mecha_colors[1:])
                if random.randint(1,2) == 2:
                    npc.mecha_colors = (*npc.mecha_colors[:4], npc.colors[4])
        if npc.mecha_pref and npc.mecha_pref in gears.selector.DESIGN_BY_NAME and not choose_new_one:
            mek = gears.selector.get_design_by_full_name(npc.mecha_pref)
        else:
            level = max(npc.renown, 15)
            if hasattr(npc, "relationship") and npc.relationship:
                level = max(level + npc.relationship.data.get("mecha_level_bonus", 0), 10)
            mek = gears.selector.MechaShoppingList.generate_single_mecha(level, npc.faction, gears.tags.GroundEnv)
            npc.mecha_pref = mek.get_full_name()
        if npc.mecha_colors:
            mek.colors = npc.mecha_colors
        return mek


class AutoLeaver(object):
    # A partner for the above- this NPC will leave the party, along with any mecha + pets.
    def __init__(self, npc):
        """
        Prepare to remove the NPC from the party. This object can be used as a dialogue effect.
        :type npc: gears.base.Character
        """
        self.npc = npc

    def _save_pet_to_campdata(self, camp: gears.GearHeadCampaign, pet):
        camp.campdata[("PET", self.npc)] = pet

    def __call__(self, camp):
        """
        Remove the NPC from the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc in camp.party:
            camp.assign_pilot_to_mecha(self.npc, None)
            camp.party.remove(self.npc)
            if camp.scene:
                camp.scene.local_teams[self.npc] = camp.scene.civilian_team
            for mek in list(camp.party):
                if hasattr(mek, "owner") and mek.owner is self.npc:
                    camp.party.remove(mek)
                elif isinstance(mek, gears.base.Monster) and mek.pet_data and mek.pet_data.trainer is self.npc:
                    camp.party.remove(mek)
                    self._save_pet_to_campdata(camp, mek)
                    if camp.scene and mek in camp.scene.contents:
                        camp.scene.contents.remove(mek)

            # for mek in list(camp.incapacitated_party):
            #    if hasattr(mek,"owner") and mek.owner is self.npc:
            #        camp.incapacitated_party.remove(mek)


class CharacterMover(object):
    def __init__(self, camp, plot: pbge.plots.Plot, character: gears.base.Character, dest_scene, dest_team,
                 allow_death=False, upgrade_mek=True, suppress_warnings=False):
        # Record the character's original location, move them to the new location.
        # Only set suppress_warnings to True if you know what you're doing, i.e. you are me. It only suppresses the
        #   warning about characters not being locked; this is only a problem if you are in an adventure with random
        #   plots or dynamic content. That would mean most adventures.
        self.original_scene = character.scene
        if not suppress_warnings:
            if character not in plot.get_locked_elements():
                print("Warning: Character {} should be locked by {} before moving!".format(character, plot))
        if not (hasattr(character, "container") and character.container):
            print("Warning: Character {} moved by {} has no original container!".format(character, plot))
            character.container = None
        elif not self.original_scene:
            print("Warning: Character {} moved by {} has no original scene!".format(character, plot))
        if not plot.active:
            print("Warning: Plot {} not active")
        if not plot.scope:
            print("Warning: Plot {} has no scope set")

        character.restore_all()
        self.character = character
        self.original_container = character.container

        self.is_lancemate = character in camp.party
        if self.is_lancemate:
            AutoLeaver(character)(camp)
        elif plot.rank + random.randint(-10,20) > character.renown:
            # Level up this pilot a bit.
            character.renown = min(character.renown + random.randint(1,6), plot.rank)
            character.job.scale_skills(character, character.renown)
            if random.randint(1,4) == 2:
                character.mecha_pref = None

        # Check to see if the character can use a mecha in the destination scene.
        if character.combatant and dest_scene.scale is gears.scale.MechaScale:
            mek = AutoJoiner.get_mecha_for_character(character)
            if mek:
                if upgrade_mek:
                    gears.champions.upgrade_to_champion(mek)
                mek.load_pilot(character)
                character = mek

        self.dest = dest_scene
        character.place(dest_scene, team=dest_team)

        self.allow_death = allow_death
        plot.call_on_end.append(self)
        if hasattr(plot, "move_records"):
            plot.move_records.append((character, dest_scene.contents))
        self.done = False

        # print('Moving {} {}'.format(self.character,self.original_container))

    def __call__(self, camp: gears.GearHeadCampaign):
        # print('Homing {} {}'.format(self.character,self.original_container))
        if not self.done:
            if self.character.is_not_destroyed() or not self.allow_death:
                # print("Checking...")
                self.character.restore_all()
                if self.character.scene is self.dest or not self.character.scene:
                    if hasattr(self.character, "container") and self.character.container:
                        self.character.container.remove(self.character)
                        # print("Removing")
                    if self.original_scene is not None:
                        self.original_scene.deploy_actor(self.character)
                    elif self.original_container is not None:
                        self.original_container.append(self.character)
                        # print("Appending")
                    else:
                        camp.freeze(self.character)
                if self.is_lancemate and camp.can_add_lancemate() and self.character.scene is camp.scene:
                    AutoJoiner(self.character)(camp)
                self.done = True


class EnterTownLanceRecovery(object):
    # When you enter a town, call this to restore the party and deal with dead/incapacitated members
    def __init__(self, camp, metroscene, metro):
        creds = camp.totally_restore_party()
        self.did_recovery = False
        if creds > 0:
            pbge.alert("Repair/Reload: ${}".format(creds))
            camp.credits -= creds
            camp.time += 1
        if camp.incapacitated_party or camp.dead_party or any(
                [pc for pc in camp.get_lancemates() if not camp.get_pc_mecha(pc)]):
            # Go through the injured/dead lists and see who needs help.
            if camp.pc not in camp.party:
                # This is serious.
                init = pbge.plots.PlotState(elements={"METRO": metro, "METROSCENE": metroscene})
                nart = GHNarrativeRequest(camp, init, adv_type="RECOVER_PC", plot_list=PLOT_LIST)
                if nart.story:
                    nart.build()
                    nart.story.start_recovery(camp)
                    self.did_recovery = True
                else:
                    print(nart.errors)
            else:
                init = pbge.plots.PlotState(elements={"METRO": metro, "METROSCENE": metroscene})
                nart = GHNarrativeRequest(camp, init, adv_type="RECOVER_LANCE", plot_list=PLOT_LIST)
                if nart.story:
                    nart.build()
                    nart.story.start_recovery(camp)
                    self.did_recovery = True


DZSPOT_PART_ONE = (
    "Deadly", "Bone", "Dead Man's", "Toxic", "Haunted", "Forsaken", "Whispering", "Shivering", "Thousand Rad", "Janky"
)

DZSPOT_PART_TWO = (
    "Ruins", "Quarry", "Gulch", "Valley", "Mountain", "Radzone", "Necropolis", "Brook", "Lake", "Dustbowl", "Point",
    "Miles",
    "Hill", "Crater"
)


def random_deadzone_spot_name():
    if random.randint(1, 4) != 1:
        A = random.choice(DZSPOT_PART_ONE)
    else:
        A = gears.selector.DEADZONE_TOWN_NAMES.gen_word()
    B = random.choice(DZSPOT_PART_TWO)
    return "{} {}".format(A, B)


DISEASE_PART_ONE = (
    "Crimson", "Radiated", "Bloody", "Violet", "Deadly", "Lumpy", "Infectious", "Oozing", "Shivering", "Creeping",
    "Necrotic", "Torturous", "Quaking", "Venomous", "Screaming", "Martian", "Flaying", "Bacterial", "Fungal",
    "Gangrenous", "Cancerous", "Pathologic", "Hazardous", "Fatal", "Wasting", "Ocular", "Parasitic", "Mutagenic"
)
DISEASE_PART_TWO = (
    "Fever", "Flopsy", "Palsy", "Plague", "Disease", "Gurgle", "Syndrome", "Bonerot", "Brainbleed", "Heartworm",
    "Skinrash", "Cough", "Tumors", "Boils", "Doom", "Bloodsludge", "Gutwrench", "Flux", "Virus", "Thrush",
    "Spinewrack", "Blight", "Decay", "Skintaker", "Earache", "Fleshmelt", "Infestation", "Ague", "Pox", "Ennui"
)


def random_disease_name():
    return "{} {}".format(random.choice(DISEASE_PART_ONE), random.choice(DISEASE_PART_TWO))


DRUG_START = (
    "Ata", "Peace", "Neo", "Well", "Cura", "Hexa", "Sol", "Med", "Asp", "Bey", "Con", "De", "Ele", "Eu",
    "Flum", "Go", "Jo", "Mod", "Nu", "Opt", "Pax", "Ques", "Rad", "Stim", "Val", "Wex", "Xan", "Ys", "Zoa"
)
DRUG_END = (
    "zine", "ite", "ide", "ium", "let", "phen", "fine", "phene", "ax", "tune", "sid", "trose", "tine", "cid",
    "pto", "int", "ium", "ga"
)
DRUG_LETTER = (
    "Alpha", "Beta", "Gamma", "Delta", "Omega", "Zeta", "Kappa"
)


def random_medicine_name():
    return "{}{} {}".format(random.choice(DRUG_START), random.choice(DRUG_END), random.choice(DRUG_LETTER))

PLANT_TYPE = (
    "Thistle", "Wort", "Flower", "Orchid", "Spinedew", "Wasabi", "Herb", "Weed", "Verbure", "Berry",
    "Marigold", "Fern", "Fiddlehead", "Greens", "Reed", "Wood", "Leaf", "Bracken", "Plant", "Lichen",
    "Grass", "Grain"
)

def random_plant_name():
    adjective = random.choice(ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None])
    return "{} {}".format(adjective, random.choice(PLANT_TYPE))


class LMSkillsSelfIntro(Offer):
    RANK_GRAM = ("[SELFINTRO_RANK_GREEN]", "[SELFINTRO_RANK_REGULAR]", "[SELFINTRO_RANK_VETERAN]",
                 "[SELFINTRO_RANK_ELITE]", "[SELFINTRO_RANK_ACE]")

    def __init__(self, npc: gears.base.Character):
        items = list()
        data = dict()
        items.append(self.get_rank_gram(npc))

        if not npc.mecha_pref:
            AutoJoiner.get_mecha_for_character(npc)

        if npc.mecha_pref:
            items.append("[SELFINTRO_MECHA]")
            data["mecha"] = npc.mecha_pref

        specialties = [sk for sk in gears.stats.NONCOMBAT_SKILLS if sk in npc.statline]
        if len(specialties) > 1:
            items.append("[SELFINTRO_SKILLS]")
            if len(specialties) > 2:
                prefix = ", ".join([s.name for s in specialties[:-1]])
            else:
                prefix = specialties[0].name
            data["skills"] = ' and '.join([prefix, specialties[-1].name])
        elif len(specialties) == 1:
            items.append("[SELFINTRO_SKILL]")
            data["skill"] = specialties[0].name

        super().__init__(
            " ".join(items),
            context=ContextTag((context.SELFINTRO,)), data=data, is_generic=True
        )

    @classmethod
    def get_rank_gram(cls, npc):
        rank = min(max((npc.renown - 1) // 20, 0), 4)
        return cls.RANK_GRAM[rank]


class SkillExperienceEffect:
    # An effect for conversations which will boost skill XP. Only works once. May include a secondary function to
    # call.
    def __init__(self, skill, xp_amount, other_fun=None):
        self.ready = True
        self.skill = skill
        self.xp_amount = xp_amount
        self.other_fun = other_fun

    def __call__(self, camp: gears.GearHeadCampaign):
        if self.ready:
            self.ready = False
            camp.dole_xp(self.xp_amount, self.skill)
            if self.other_fun:
                self.other_fun(camp)


class EffectCallPlusNPC:
    # Normally an effect call from dialogue or using a waypoint calls a function with signature (camp).
    # This turns that into a function with signature (camp, npc).
    def __init__(self, fun, npc):
        self.fun = fun
        self.npc = npc

    def __call__(self, camp):
        self.fun(camp, self.npc)


#  *****************************************
#  ***   RUMOR  PROHIBITION  CALLABLES   ***
#  *****************************************

class ProhibitFactionMembers:
    def __init__(self, faction_element_id):
        self.faction_element_id = faction_element_id

    def __call__(self, plot, camp, npc):
        fac = plot.elements.get(self.faction_element_id)
        return fac and npc.faction is fac


class ProhibitFactionAndPCIfAllied:
    # Faction members won't give this rumor. The PC won't be told this rumor if the PC is allied with the faction.
    def __init__(self, faction_element_id):
        self.faction_element_id = faction_element_id

    def __call__(self, plot, camp: gears.GearHeadCampaign, npc):
        fac = plot.elements.get(self.faction_element_id)
        return fac and ((npc.faction is fac) or camp.is_favorable_to_pc(fac))


#  ***********************************
#  ***   PLOT  EXPIRATION  TYPES   ***
#  ***********************************

class RulingFactionExpiration:
    # This plot will expire if the ruling faction of a location changes.
    def __init__(self, location, ruling_faction):
        self.location = location
        self.ruling_faction = ruling_faction

    def __call__(self, camp, plot):
        return self.location.faction is not self.ruling_faction

