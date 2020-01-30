import glob
import pbge
import os
from . import stats
from . import personality
import random

from gears.meritbadges import BADGE_CRIMINAL
from . import random_character_colors, DETAIL_COLORS, CLOTHING_COLORS, SKIN_COLORS, HAIR_COLORS
from . import color
from . import base
from . import eggs
from . import meritbadges
from . import portraits
from . import genderobj
from . import tags

TYPHON_SLAYER = meritbadges.UniversalReactionBadge("Typhon Slayer", "You led the team that defeated Typhon.", 10)
ELEMENTAL_ADEPT = meritbadges.TagReactionBadge("Elemental Adept", "You meditated at the elemental shrines, attaining illumination.",{tags.Faithworker: 20})
ROBOT_WARRIOR = meritbadges.TagReactionBadge("Robot Warrior", "You ranked in the Robot Warriors mecha tournament.",{tags.Adventurer: 10,tags.Military: 5})

class RetroGear(object):
    # A container for gear info.
    def __init__(self, g, s, v, scale):
        self.g = g
        self.s = s
        self.v = v
        self.scale = scale
        self.natt = dict()
        self.satt = dict()
        self.sub_com = list()
        self.inv_com = list()


class GH1Loader(object):
    # Class to load and parse a GearHead1 (aka GearHead Arena) save file.
    def __init__(self, fname):
        self.fname = fname

    def _read_map(self, myfile):
        # Since we aren't keeping the map, just advance myfile to the end of
        # the map block.
        # {First, get rid of the descriptive message & the dimensions.}
        myfile.readline()
        x_max = int(myfile.readline())
        y_max = int(myfile.readline())
        tile = 0
        # Read the terrain
        while tile < x_max * y_max:
            count = int(myfile.readline())
            terrain = myfile.readline()
            tile += count
            if len(terrain) < 1:
                break
        # Read the second descriptive label
        myfile.readline()
        # Read the visibility
        tile = 0
        while tile < x_max * y_max:
            count = myfile.readline()
            if len(count) < 1:
                break
            else:
                tile += int(count)

    #  **************************************
    #  ***   GEARHEAD  ARENA  CONSTANTS   ***
    #  **************************************

    GG_CHARACTER = 2
    NAG_LOCATION = -1
    NAS_TEAM = 4
    NAV_DEFPLAYERTEAM = 1

    GG_ADVENTURE = -7

    NAG_SCRIPTVAR = 0

    NAG_SKILL = 1
    NAS_MECHAGUNNERY = 1
    NAS_MECHAARTILLERY = 2
    NAS_MECHAWEAPONS = 3
    NAS_MECHAFIGHTING = 4
    NAS_MECHAPILOTING = 5
    NAS_SMALLARMS = 6
    NAS_HEAVYWEAPONS = 7
    NAS_ARMEDCOMBAT = 8
    NAS_MARTIALARTS = 9
    NAS_DODGE = 10
    NAS_AWARENESS = 11
    NAS_INITIATIVE = 12
    NAS_VITALITY = 13
    NAS_SURVIVAL = 14
    NAS_MECHAREPAIR = 15
    NAS_MEDICINE = 16
    NAS_ELECTRONICWARFARE = 17
    NAS_SPOTWEAKNESS = 18
    NAS_CONVERSATION = 19
    NAS_FIRSTAID = 20
    NAS_SHOPPING = 21
    NAS_BIOTECHNOLOGY = 22
    NAS_GENERALREPAIR = 23
    NAS_CYBERTECH = 24
    NAS_STEALTH = 25
    NAS_ATHLETICS = 26
    NAS_FLIRTATION = 27
    NAS_INTIMIDATION = 28
    NAS_SCIENCE = 29
    NAS_CONCENTRATION = 30
    NAS_MECHAENGINEERING = 31
    NAS_CODEBREAKING = 32
    NAS_WEIGHTLIFTING = 33
    NAS_MYSTICISM = 34
    NAS_PERFORMANCE = 35
    NAS_RESISTANCE = 36
    NAS_INVESTIGATION = 37
    NAS_ROBOTICS = 38
    NAS_LEADERSHIP = 39
    NAS_DOMINATEANIMAL = 40
    NAS_PICKPOCKETS = 41

    NAG_CHARDESCRIPTION = 3
    NAS_HEROIC = -1
    NAS_LAWFUL = -2
    NAS_SOCIABLE = -3
    NAS_EASYGOING = -4
    NAS_CHEERFUL = -5
    NAS_RENOWNED = -6
    NAS_PRAGMATIC = -7
    NAS_GENDER = 0

    NAG_EXPERIENCE = 4
    NAS_TOTAL_XP = 0
    NAS_SPENT_XP = 1
    NAS_CREDITS = 2

    NAG_TALENT = 16
    NAS_IDEALIST = 17

    SAVE_FILE_CONTINUE = 0
    SAVE_FILE_SENTINEL = -1

    COLOR_CONVERT = {
        (212, 155, 196): color.RoyalPink,
        (255, 192, 203): color.Pink,
        (255, 105, 180): color.HotPink,
        (255, 0, 255): color.Magenta,
        (230, 20, 130): color.AegisCrimson,
        (176, 48, 96): color.Maroon,
        (180, 46, 60): color.CardinalRed,
        (220, 44, 51): color.BrightRed,
        (194, 16, 38): color.GunRed,
        (175, 26, 10): color.PirateSunrise,
        (135, 30, 17): color.AceScarlet,
        (103, 3, 45): color.BlackRose,
        (197, 80, 69): color.CometRed,
        (255, 69, 0): color.OrangeRed,
        (255, 107, 83): color.Persimmon,
        (224, 112, 20): color.HunterOrange,
        (255, 165, 0): color.Orange,
        (250, 200, 49): color.Saffron,
        (234, 180, 88): color.DesertYellow,
        (205, 198, 115): color.Khaki,
        (225, 201, 48): color.LemonYellow,
        (255, 215, 0): color.Gold,
        (255, 233, 2): color.ElectricYellow,
        (211, 195, 82): color.NobleGold,
        (222, 222, 156): color.CharredBlonde,
        (116, 100, 13): color.Mustard,
        (173, 255, 47): color.GreenYellow,
        (172, 225, 175): color.Celadon,
        (152, 190, 181): color.MountainDew,
        (136, 141, 101): color.Avocado,
        (104, 130, 117): color.ArmyDrab,
        (113, 175, 98): color.GrassGreen,
        (88, 143, 86): color.Cactus,
        (28, 52, 38): color.GriffinGreen,
        (79, 101, 48): color.Olive,
        (0, 100, 0): color.DarkGreen,
        (40, 105, 73): color.MassiveGreen,
        (36, 140, 46): color.ForestGreen,
        (11, 218, 81): color.Malachite,
        (41, 112, 94): color.SeaGreen,
        (66, 121, 119): color.Jade,
        (77, 156, 131): color.Viridian,
        (67, 185, 151): color.DoctorGreen,
        (70, 230, 30): color.FlourescentGreen,
        (201, 205, 229): color.AeroBlue,
        (127, 255, 212): color.Aquamarine,
        (75, 200, 220): color.SkyBlue,
        (0, 240, 240): color.Cyan,
        (144, 166, 195): color.FadedDenim,
        (70, 130, 180): color.SteelBlue,
        (17, 78, 200): color.FreedomBlue,
        (174, 238, 251): color.PlasmaBlue,
        (49, 91, 141): color.Azure,
        (39, 54, 120): color.BugBlue,
        (6, 42, 120): color.Cobalt,
        (0, 49, 83): color.PrussianBlue,
        (25, 25, 112): color.MidnightBlue,
        (67, 73, 100): color.DeepSeaBlue,
        (172, 128, 185): color.StarViolet,
        (122, 88, 193): color.Fuschia,
        (121, 109, 150): color.HeavyPurple,
        (80, 40, 120): color.KettelPurple,
        (152, 61, 97): color.Wine,
        (153, 17, 153): color.Eggplant,
        (56, 26, 81): color.Grape,
        (200, 0, 200): color.ShiningViolet,
        (185, 159, 92): color.Straw,
        (170, 132, 80): color.Beige,
        (188, 143, 143): color.RosyBrown,
        (150, 94, 69): color.Sandstone,
        (100, 49, 30): color.DarkBrown,
        (123, 63, 0): color.Cinnamon,
        (166, 47, 32): color.Terracotta,
        (241, 254, 223): color.GothSkin,
        (255, 244, 208): color.Alabaster,
        (245, 213, 160): color.Maize,
        (222, 184, 135): color.Burlywood,
        (250, 183, 139): color.LightSkin,
        (244, 164, 96): color.SandyBrown,
        (184, 124, 81): color.TannedSkin,
        (172, 114, 89): color.MediumSkin,
        (150, 112, 89): color.Leather,
        (142, 62, 39): color.Chocolate,
        (96, 49, 33): color.DarkSkin,
        (45, 45, 45): color.Black,
        (80, 80, 85): color.DeepGrey,
        (77, 93, 83): color.FieldGrey,
        (105, 105, 105): color.DimGrey,
        (119, 110, 89): color.WarmGrey,
        (130, 143, 114): color.BattleshipGrey,
        (122, 130, 130): color.LunarGrey,
        (112, 128, 144): color.SlateGrey,
        (157, 172, 183): color.GullGrey,
        (169, 169, 169): color.DeepGrey,
        (211, 224, 230): color.CeramicColor,
        (206, 195, 162): color.Cream,
        (240, 240, 240): color.White,
        (236, 254, 255): color.ShiningWhite,
    }

    GENDER_OPS = {
        0: genderobj.Gender.get_default_male(),
        1: genderobj.Gender.get_default_female(),
        2: genderobj.Gender.get_default_nonbinary()
    }

    NPC_VIKKI = "Vikki Shingo"

    # This dictionary lists Character IDs for major NPCs.
    # The G,S for the Character ID is 5,0
    MAJOR_NPCS = {
        NPC_VIKKI: 6
    }

    def _extract_value(self, myline):
        bits = myline.split(None, 1)
        if bits:
            v = int(bits[0])
            if len(bits) > 1:
                return v, bits[1]
            else:
                return v, ''
        else:
            return -1, ''

    def _read_numeric_attributes(self, myfile):
        # Return the dict of numeric attributes.
        mydict = dict()
        keep_going = True
        while keep_going:
            rawline = myfile.readline()

            if len(rawline) < 1:
                # Conveniently, a blank line is both the Python end of file
                # indicator and a halting error in GearHead1.
                keep_going = False
            else:
                # This line should contain an "action code".
                n, myline = self._extract_value(rawline)
                if n == self.SAVE_FILE_CONTINUE:
                    # This is a gear.
                    g, myline = self._extract_value(myline)
                    s, myline = self._extract_value(myline)
                    v, myline = self._extract_value(myline)
                    mydict[(g, s)] = v

                elif n == self.SAVE_FILE_SENTINEL:
                    keep_going = False
                else:
                    print("GH1Loader Error... no idea what action code {} is.".format(n))
        return mydict

    def _read_string_attributes(self, myfile):
        # Return the dict of string attributes.
        mydict = dict()
        keep_going = True
        while keep_going:
            rawline = myfile.readline()

            if len(rawline) < 1 or '<' not in rawline:
                # Conveniently, a blank line is both the Python end of file
                # indicator and a halting error in GearHead1.
                keep_going = False
            else:
                k, raw_v = rawline.split(None, 1)
                v = raw_v.strip().strip('<>')
                mydict[k.upper()] = v

        return mydict

    def _process_stat_line(self, rawline):
        mydict = dict()
        stat_stuff = rawline.split()
        del stat_stuff[0]
        mystat = -1
        for s in stat_stuff:
            if mystat is -1:
                mystat = int(s)
            else:
                mydict[mystat] = int(s)
                mystat = -1
        return mydict

    def _load_gears(self, myfile):
        # Start reading, and keep going until we reach the save file sentinel
        # or end of file.
        keep_going = True
        mylist = list()
        while keep_going:
            rawline = myfile.readline()

            if len(rawline) < 1:
                # Conveniently, a blank line is both the Python end of file
                # indicator and a halting error in GearHead1.
                keep_going = False
            else:
                # This line should contain an "action code".
                n, myline = self._extract_value(rawline)
                if n == self.SAVE_FILE_CONTINUE:
                    # This is a gear.
                    g, myline = self._extract_value(myline)
                    s, myline = self._extract_value(myline)
                    v, myline = self._extract_value(myline)
                    scale, myline = self._extract_value(myline)

                    mygear = RetroGear(g, s, v, scale)
                    mylist.append(mygear)

                    # Read the stats line.
                    rawline = myfile.readline()
                    mygear.stats = self._process_stat_line(rawline)

                    mygear.natt = self._read_numeric_attributes(myfile)
                    mygear.satt = self._read_string_attributes(myfile)
                    mygear.inv_com = self._load_gears(myfile)
                    mygear.sub_com = self._load_gears(myfile)

                elif n == self.SAVE_FILE_SENTINEL:
                    keep_going = False
                else:
                    print("GH1Loader Error... no idea what action code {} is.".format(n))

        return mylist

    def _chuck_the_maps(self, myfile):
        n = int(myfile.readline())
        while n != -1:
            # Read and dispose of the mapname and the map.
            myfile.readline()
            self._read_map(myfile)
            n = int(myfile.readline())

    def _load_list(self, myfile):
        # Load a GH1 RPG_*.txt save file, and extract the useful bits.
        # Map definitions and anything we don't want just gets tossed.

        # Read the comtime and map scale. Promptly throw them out.
        myfile.readline()
        myfile.readline()

        # Read the current map. Throw it out as well.
        self._read_map(myfile)

        # Load the scene index. Throw it out.
        myfile.readline()

        # Load the contents of the current gameboard.
        self.gb_contents = self._load_gears(myfile)

        # Load and throw away all the frozen maps.
        self._chuck_the_maps(myfile)

        # Load the rest of the adventure.
        self.gb_contents += self._load_gears(myfile)

    @classmethod
    def all_gears(self, mylist):
        # Cycle through all the gears in this tree.
        for gear in mylist:
            yield gear
            if gear.sub_com:
                for p in self.all_gears(gear.sub_com):
                    yield p
            if gear.inv_com:
                for p in self.all_gears(gear.inv_com):
                    yield p

    def find_pc(self):
        pc = None
        for mpc in self.all_gears(self.gb_contents):
            if mpc.g == self.GG_CHARACTER and mpc.natt.get(
                    (self.NAG_LOCATION, self.NAS_TEAM)) == self.NAV_DEFPLAYERTEAM:
                pc = mpc
        return pc

    def find_npc(self,characterid):
        npc = None
        for candidate in self.all_gears(self.gb_contents):
            if candidate.g == self.GG_CHARACTER and candidate.natt.get((5,0)) == characterid:
                npc = candidate
        return npc

    def find_adventure(self):
        adv = None
        for g in self.all_gears(self.gb_contents):
            if g.g == self.GG_ADVENTURE:
                adv = g
                break
        return adv

    def _set_personality(self, pc, traits, nas, hi_trait, lo_trait):
        oldval = pc.natt.get((self.NAG_CHARDESCRIPTION, nas), 0)
        if oldval > 25:
            traits.append(hi_trait)
        elif oldval < -25:
            traits.append(lo_trait)

    def _convert_color(self, color_string, color_type):
        # Return the GHC color and the truncated string.
        r, color_string = self._extract_value(color_string)
        g, color_string = self._extract_value(color_string)
        b, color_string = self._extract_value(color_string)

        my_color = self.COLOR_CONVERT.get((r, g, b), None)
        if my_color:
            return my_color, color_string
        else:
            return random.choice(color_type), color_string

    def convert_character(self, pc):
        # Convert a character from GH1 rules to GearHead Caramel rules.
        statline = dict()
        t = 1
        for stat in stats.PRIMARY_STATS:
            statline[stat] = pc.stats.get(t, 10)
            t += 1

        # Convert the skills. MechaGunnery is max of MechaGunnery, MechaArtillery... and so on.
        statline[stats.MechaGunnery] = max(pc.natt.get((self.NAG_SKILL, self.NAS_MECHAGUNNERY), 0),
                                           pc.natt.get((self.NAG_SKILL, self.NAS_MECHAARTILLERY), 0))
        statline[stats.MechaFighting] = max(pc.natt.get((self.NAG_SKILL, self.NAS_MECHAWEAPONS), 0),
                                            pc.natt.get((self.NAG_SKILL, self.NAS_MECHAFIGHTING), 0))
        statline[stats.MechaPiloting] = pc.natt.get((self.NAG_SKILL, self.NAS_MECHAPILOTING), 0)
        statline[stats.RangedCombat] = max(pc.natt.get((self.NAG_SKILL, self.NAS_SMALLARMS), 0),
                                           pc.natt.get((self.NAG_SKILL, self.NAS_HEAVYWEAPONS), 0))
        statline[stats.CloseCombat] = max(pc.natt.get((self.NAG_SKILL, self.NAS_ARMEDCOMBAT), 0),
                                          pc.natt.get((self.NAG_SKILL, self.NAS_MARTIALARTS), 0))
        statline[stats.Dodge] = pc.natt.get((self.NAG_SKILL, self.NAS_DODGE), 0)
        statline[stats.Repair] = max(pc.natt.get((self.NAG_SKILL, self.NAS_MECHAREPAIR), 0),
                                     pc.natt.get((self.NAG_SKILL, self.NAS_GENERALREPAIR), 0))
        statline[stats.Medicine] = max(pc.natt.get((self.NAG_SKILL, self.NAS_MEDICINE), 0),
                                       pc.natt.get((self.NAG_SKILL, self.NAS_FIRSTAID), 0),
                                       pc.natt.get((self.NAG_SKILL, self.NAS_CYBERTECH), 0))
        statline[stats.Biotechnology] = pc.natt.get((self.NAG_SKILL, self.NAS_BIOTECHNOLOGY), 0)
        statline[stats.Stealth] = max(pc.natt.get((self.NAG_SKILL, self.NAS_STEALTH), 0),
                                      pc.natt.get((self.NAG_SKILL, self.NAS_PICKPOCKETS), 0))
        statline[stats.Science] = max(pc.natt.get((self.NAG_SKILL, self.NAS_SCIENCE), 0),
                                      pc.natt.get((self.NAG_SKILL, self.NAS_MECHAENGINEERING), 0),
                                      pc.natt.get((self.NAG_SKILL, self.NAS_ROBOTICS), 0))
        statline[stats.Computers] = max(pc.natt.get((self.NAG_SKILL, self.NAS_ELECTRONICWARFARE), 0),
                                        pc.natt.get((self.NAG_SKILL, self.NAS_CODEBREAKING), 0))
        statline[stats.Performance] = pc.natt.get((self.NAG_SKILL, self.NAS_PERFORMANCE), 0)
        statline[stats.Negotiation] = max(pc.natt.get((self.NAG_SKILL, self.NAS_CONVERSATION), 0),
                                          pc.natt.get((self.NAG_SKILL, self.NAS_SHOPPING), 0),
                                          pc.natt.get((self.NAG_SKILL, self.NAS_FLIRTATION), 0),
                                          pc.natt.get((self.NAG_SKILL, self.NAS_INTIMIDATION), 0),
                                          pc.natt.get((self.NAG_SKILL, self.NAS_LEADERSHIP), 0))
        statline[stats.Scouting] = max(pc.natt.get((self.NAG_SKILL, self.NAS_AWARENESS), 0),
                                       pc.natt.get((self.NAG_SKILL, self.NAS_SURVIVAL), 0),
                                       pc.natt.get((self.NAG_SKILL, self.NAS_INVESTIGATION), 0))
        statline[stats.DominateAnimal] = pc.natt.get((self.NAG_SKILL, self.NAS_DOMINATEANIMAL), 0)
        statline[stats.Vitality] = max(pc.natt.get((self.NAG_SKILL, self.NAS_VITALITY), 0),
                                       pc.natt.get((self.NAG_SKILL, self.NAS_RESISTANCE), 0))
        statline[stats.Athletics] = max(pc.natt.get((self.NAG_SKILL, self.NAS_ATHLETICS), 0),
                                        pc.natt.get((self.NAG_SKILL, self.NAS_WEIGHTLIFTING), 0))
        # Concentration builds Mental Points, which in Caramel will be used to
        # power special attacks and skills. So, it's Concentrtation that absorbs
        # Initiative and SpotWeakness. Also Mysticism, because all that meditation
        # has to help.
        statline[stats.Concentration] = max(pc.natt.get((self.NAG_SKILL, self.NAS_CONCENTRATION), 0),
                                            pc.natt.get((self.NAG_SKILL, self.NAS_INITIATIVE), 0),
                                            pc.natt.get((self.NAG_SKILL, self.NAS_SPOTWEAKNESS), 0),
                                            pc.natt.get((self.NAG_SKILL, self.NAS_MYSTICISM), 0))

        # Delete any "skills" that don't actually exist.
        for k in stats.COMBATANT_SKILLS + stats.NONCOMBAT_SKILLS:
            if k in statline and statline[k] < 1:
                del statline[k]

        # Generate the personality.
        traits = list()
        self._set_personality(pc, traits, self.NAS_SOCIABLE, personality.Sociable, personality.Shy)
        self._set_personality(pc, traits, self.NAS_EASYGOING, personality.Easygoing, personality.Passionate)
        self._set_personality(pc, traits, self.NAS_CHEERFUL, personality.Cheerful, personality.Grim)

        numvirt = max(pc.natt.get((self.NAG_CHARDESCRIPTION, self.NAS_HEROIC), 0) // 25, 1)
        virtues = list(personality.VIRTUES)
        random.shuffle(virtues)
        if numvirt > 0:
            traits += virtues[:numvirt - 1]

        if pc.natt.get((self.NAG_TALENT,self.NAS_IDEALIST),0) != 0:
            traits.append(personality.Idealist)

        # Generate the badges.
        badges = list()
        if pc.natt.get((self.NAG_CHARDESCRIPTION, self.NAS_LAWFUL), 0) < -10:
            badges.append(BADGE_CRIMINAL)

        # Convert the colors.
        sdlcolor = pc.satt.get('SDL_COLORS', None)
        if sdlcolor:
            rchan, sdlcolor = self._convert_color(sdlcolor, CLOTHING_COLORS)
            ychan, sdlcolor = self._convert_color(sdlcolor, SKIN_COLORS)
            gchan, sdlcolor = self._convert_color(sdlcolor, HAIR_COLORS)
            pc_colors = [rchan, ychan, gchan, random.choice(DETAIL_COLORS), random.choice(CLOTHING_COLORS)]
        else:
            pc_colors = random_character_colors()

        # Determine gender.
        gender = self.GENDER_OPS.get(pc.natt.get((self.NAG_CHARDESCRIPTION, self.NAS_GENDER), 0),genderobj.Gender.get_default_nonbinary())

        ghcpc = base.Character(name=pc.satt.get('NAME', "Bob's Dwarf"), statline=statline, personality=traits,
                              colors=pc_colors, portrait_gen=portraits.Portrait(), gender=gender)

        # Set experience totals and renown.
        ghcpc.experience[ghcpc.TOTAL_XP] = pc.natt.get((self.NAG_EXPERIENCE,self.NAS_TOTAL_XP),0)
        ghcpc.experience[ghcpc.SPENT_XP] = pc.natt.get((self.NAG_EXPERIENCE, self.NAS_SPENT_XP), 0)
        ghcpc.renown = pc.natt.get((self.NAG_CHARDESCRIPTION,self.NAS_RENOWNED),1)

        return ghcpc

    def record_pc_stuff(self, rawpc, ghcpc):
        # Try to figure out as much as you can about the PC, and store that information.
        adv = self.find_adventure()
        if adv:
            # We're gonna try to determine the PC's origin based on the first line of their life history.
            if adv.satt.get("HISTORY1", "Fire in the Taco Bell") in (
                "You arrived in Hogye as a refugee from Luna.",
                "You fled Luna after deserting from Aegis Overlord Luna."
            ):
                ghcpc.personality.add(personality.Luna)
            else:
                ghcpc.personality.add(personality.GreenZone)

            bio_bits = list()
            bio_bits.append(rawpc.satt.get("BIO1", ""))
            bio_bits.append(adv.satt.get("HISTORY1", ""))
            bio_bits.append(adv.satt.get("HISTORY2", ""))

            history_list = list()
            for k,v in adv.satt.items():
                if k.startswith("HISTORY"):
                    history_list.append(v)

            if any(h.startswith("You killed the biomonster Cetus in") for h in history_list):
                print("Killed Cetus!")

            if adv.s != 0:
                ghcpc.badges.append(TYPHON_SLAYER)
                bio_bits.append("You defeated the biomonster Typhon.")

            if adv.natt.get((self.NAG_SCRIPTVAR,16),0) != 0:
                ghcpc.badges.append(ELEMENTAL_ADEPT)

            if adv.natt.get((self.NAG_SCRIPTVAR,24),0) != 0:
                ghcpc.badges.append(ROBOT_WARRIOR)

            ghcpc.bio = ' '.join(bio_bits)


    def load(self):
        with open(self.fname, 'rb') as f:
            self._load_list(f)

    def get_relationships(self,egg):
        pass

    def get_egg(self):
        rpc = self.find_pc()
        pc = self.convert_character(rpc)
        my_egg = eggs.Egg(pc)
        my_egg.past_adventures.append("The Typhon Incident")
        my_egg.credits = max(rpc.natt.get((self.NAG_EXPERIENCE, self.NAS_CREDITS), 500000),500000)
        self.record_pc_stuff(rpc,pc)
        return my_egg

    @classmethod
    def seek_gh1_files(self):
        myfiles = list()
        myfiles += glob.glob(pbge.util.user_dir('RPG*.txt'))
        myfiles += glob.glob(pbge.util.user_dir(os.path.join('gharena', 'RPG*.txt')))
        myfiles += glob.glob(os.path.expanduser(os.path.join('~', '.config', 'gharena', 'SaveGame', 'RPG*.txt')))
        myfiles += glob.glob(os.path.expanduser(os.path.join('~', 'gharena', 'SaveGame', 'RPG*.txt')))
        return myfiles


