from pbge.image import Gradient
import random

class GHGradient( Gradient ):
    @classmethod
    def get_tags(cls):
        return set(cls.SETS + (cls.FAMILY,))
    SETS = ()
    FAMILY = -1

CLOTHING,SKIN,HAIR,MECHA,DETAILS,METAL = range(6)

# Color Families- the eleven basic color words in English.
PINK,RED,ORANGE,YELLOW,GREEN,BLUE,PURPLE,BROWN,GREY,BLACK,WHITE = range(100,111)

class ChannelRed( GHGradient ):
    NAME = 'Channel Red'
    COLOR_RANGE = (255,0,0,0,0,0)
    SETS = ()
    FAMILY = -1

class ChannelYellow( GHGradient ):
    NAME = 'Channel Yellow'
    COLOR_RANGE = (255,255,0,0,0,0)
    SETS = ()
    FAMILY = -1

class ChannelGreen( GHGradient ):
    NAME = 'Channel Green'
    COLOR_RANGE = (0,255,0,0,0,0)
    SETS = ()
    FAMILY = -1

class ChannelCyan( GHGradient ):
    NAME = 'Channel Cyan'
    COLOR_RANGE = (0,255,255,0,0,0)
    SETS = ()
    FAMILY = -1

class ChannelMagenta( GHGradient ):
    NAME = 'Channel Magenta'
    COLOR_RANGE = (255,0,255,0,0,0)
    SETS = ()
    FAMILY = -1


class RoyalPink( GHGradient ):
    NAME = 'Royal Pink'
    COLOR_RANGE = (255,135,241,80,43,54)
    SETS = (CLOTHING,MECHA,DETAILS)
    FAMILY = PINK

class Pink( GHGradient ):
    NAME = 'Pink'
    COLOR_RANGE = (255,230,208,149,16,100)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PINK

class HotPink( GHGradient ):
    NAME = 'Hot Pink'
    COLOR_RANGE = (255,92,133,120,14,98)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PINK

class Magenta( GHGradient ):
    NAME = 'Magenta'
    COLOR_RANGE = (255,0,215,45,0,95)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PINK

class AegisCrimson( GHGradient ):
    NAME = 'Aegis Crimson'
    COLOR_RANGE = (255,45,109,41,3,33)
    SETS = (CLOTHING,MECHA,DETAILS)
    FAMILY = PINK

class Maroon( GHGradient ):
    NAME = 'Maroon'
    COLOR_RANGE = (240,61,134,25,6,31)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = PINK

class CardinalRed( GHGradient ):
    NAME = 'Cardinal Red'
    COLOR_RANGE = (240,80,72,32,8,12)
    SETS = (CLOTHING,MECHA)
    FAMILY = RED

class BrightRed( GHGradient ):
    NAME = 'Bright Red'
    COLOR_RANGE = (255,57,56,112,4,12)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = RED

class GunRed( GHGradient ):
    NAME = 'Gun Red'
    COLOR_RANGE = (248,20,20,69,5,26)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = RED

class PirateSunrise( GHGradient ):
    NAME = 'Pirate Sunrise'
    COLOR_RANGE = (235,57,13,47,0,22)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = RED

class AceScarlet( GHGradient ):
    NAME = 'Ace Scarlet'
    COLOR_RANGE = (255,96,72,60,19,27)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = RED

class BlackRose( GHGradient ):
    NAME = 'Black Rose'
    COLOR_RANGE = (172,20,54,37,0,20)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = RED

class CometRed( GHGradient ):
    NAME = 'Comet Red'
    COLOR_RANGE = (209,76,82,58,27,33)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = RED

class OrangeRed( GHGradient ):
    NAME = 'Orange Red'
    COLOR_RANGE = (255,100,0,45,9,9)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = RED

class Persimmon( GHGradient ):
    NAME = 'Persimmon'
    COLOR_RANGE = (255,159,90,77,16,0)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = ORANGE

class HunterOrange( GHGradient ):
    NAME = 'Hunter Orange'
    COLOR_RANGE = (255,145,0,32,0,48)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = ORANGE

class Orange( GHGradient ):
    NAME = 'Orange'
    COLOR_RANGE = (255,187,0,109,0,32)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = ORANGE

class Saffron( GHGradient ):
    NAME = 'Saffron'
    COLOR_RANGE = (255,255,142,157,0,0)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = ORANGE

class DesertYellow( GHGradient ):
    NAME = 'Desert Yellow'
    COLOR_RANGE = (229,234,163,26,32,15)
    SETS = (CLOTHING,MECHA)
    FAMILY = YELLOW

class Khaki( GHGradient ):
    NAME = 'Khaki'
    COLOR_RANGE = (252,240,147,32,64,39)
    SETS = (CLOTHING,MECHA)
    FAMILY = YELLOW

class LemonYellow( GHGradient ):
    NAME = 'Lemon Yellow'
    COLOR_RANGE = (255,255,77,74,80,56)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = YELLOW

class Gold( GHGradient ):
    NAME = 'Gold'
    COLOR_RANGE = (0xDB,0xF8,0x96,0xDD,0x7C,0x00)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS,METAL)
    FAMILY = YELLOW

class ElectricYellow( GHGradient ):
    NAME = 'Electric Yellow'
    COLOR_RANGE = (255,224,0,120,69,80)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = YELLOW

class NobleGold( GHGradient ):
    NAME = 'NobleGold'
    COLOR_RANGE = (255,249,128,69,38,23)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS,METAL)
    FAMILY = YELLOW

class CharredBlonde( GHGradient ):
    NAME = 'Charred Blonde'
    COLOR_RANGE = (255,255,208,111,80,56)
    SETS = (HAIR,MECHA,DETAILS)
    FAMILY = YELLOW

class Mustard( GHGradient ):
    NAME = 'Mustard'
    COLOR_RANGE = (179,139,19,41,36,4)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = YELLOW

class GreenYellow( GHGradient ):
    NAME = 'Green Yellow'
    COLOR_RANGE = (239,255,60,16,89,55)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = GREEN

class Celadon( GHGradient ):
    NAME = 'Celadon'
    COLOR_RANGE = (232,255,190,19,60,46)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = GREEN

class MountainDew( GHGradient ):
    # This color's name is supposed to be rhyming slang for Zaku II
    NAME = 'Mountain Dew'
    COLOR_RANGE = (194,243,227,51,64,62)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = GREEN

class Avocado( GHGradient ):
    NAME = 'Avocado'
    COLOR_RANGE = (183,224,82,31,34,36)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = GREEN

class ArmyDrab( GHGradient ):
    NAME = 'Army Drab'
    COLOR_RANGE = (127,201,150,21,32,42)
    SETS = (CLOTHING,MECHA)
    FAMILY = GREEN

class GrassGreen( GHGradient ):
    NAME = 'Grass Green'
    COLOR_RANGE = (138,232,93,3,47,70)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class Cactus( GHGradient ):
    NAME = 'Cactus'
    COLOR_RANGE = (118,184,94,2,51,49)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class GriffinGreen( GHGradient ):
    NAME = 'Griffin Green'
    COLOR_RANGE = (60,135,70,2,24,10)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class Olive( GHGradient ):
    NAME = 'Olive'
    COLOR_RANGE = (126,153,72,13,18,8)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class DarkGreen( GHGradient ):
    NAME = 'Dark Green'
    COLOR_RANGE = (43,140,0,0,36,26)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class MassiveGreen( GHGradient ):
    NAME = 'Massive Green'
    COLOR_RANGE = (78,161,107,0,9,43)
    SETS = (CLOTHING,MECHA)
    FAMILY = GREEN

class ForestGreen( GHGradient ):
    NAME = 'ForestGreen'
    COLOR_RANGE = (78,204,52,12,50,19)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class Malachite( GHGradient ):
    NAME = 'Malachite'
    COLOR_RANGE = (0,255,94,12,78,35)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = GREEN

class SeaGreen( GHGradient ):
    NAME = 'SeaGreen'
    COLOR_RANGE = (89,169,153,0,32,29)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class Jade( GHGradient ):
    NAME = 'Jade'
    COLOR_RANGE = (115,255,223,17,49,87)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class Viridian( GHGradient ):
    NAME = 'Viridian'
    COLOR_RANGE = (104,213,169,7,40,90)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class DoctorGreen( GHGradient ):
    NAME = 'Doctor Green'
    COLOR_RANGE = (85,236,193,24,66,54)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = GREEN

class FlourescentGreen( GHGradient ):
    NAME = 'Flourescent Green'
    COLOR_RANGE = (222,255,0,0,121,106)
    SETS = (HAIR,DETAILS)
    FAMILY = GREEN

class AeroBlue( GHGradient ):
    NAME = 'Aero Blue'
    COLOR_RANGE = (240,252,255,42,66,93)
    SETS = (CLOTHING,MECHA,DETAILS,METAL)
    FAMILY = BLUE

class Aquamarine( GHGradient ):
    NAME = 'Aquamarine'
    COLOR_RANGE = (171,255,240,50,0,103)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BLUE

class SkyBlue( GHGradient ):
    NAME = 'Sky Blue'
    COLOR_RANGE = (96,255,255,30,88,118)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BLUE

class Cyan( GHGradient ):
    NAME = 'Cyan'
    COLOR_RANGE = (0,255,234,0,79,86)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BLUE

class Turquoise( GHGradient ):
    NAME = 'Turquoise'
    COLOR_RANGE = (50,250,222,60,0,90)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BLUE

class FadedDenim( GHGradient ):
    NAME = 'Faded Denim'
    COLOR_RANGE = (222,233,249,0,7,97)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class SteelBlue( GHGradient ):
    NAME = 'Steel Blue'
    COLOR_RANGE = (117,183,230,38,17,50)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = BLUE

class FreedomBlue( GHGradient ):
    NAME = 'Freedom Blue'
    COLOR_RANGE = (21,177,255,12,3,36)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class PlasmaBlue( GHGradient ):
    NAME = 'Plasma Blue'
    COLOR_RANGE = (247,255,232,0,128,171)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BLUE

class Azure( GHGradient ):
    NAME = 'Azure'
    COLOR_RANGE = (47,151,198,26,0,79)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class BugBlue( GHGradient ):
    NAME = 'Bug Blue'
    COLOR_RANGE = (49,85,153,46,3,43)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class Cobalt( GHGradient ):
    NAME = 'Cobalt'
    COLOR_RANGE = (8,79,179,17,3,64)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = BLUE

class PrussianBlue( GHGradient ):
    NAME = 'Prussian Blue'
    COLOR_RANGE = (0,136,217,10,10,18)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class MidnightBlue( GHGradient ):
    NAME = 'Midnight Blue'
    COLOR_RANGE = (37,60,163,10,0,16)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class DeepSeaBlue( GHGradient ):
    NAME = 'Deep Sea Blue'
    COLOR_RANGE = (99,136,172,25,5,41)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BLUE

class StarViolet( GHGradient ):
    NAME = 'Star Violet'
    COLOR_RANGE = (236,163,231,48,24,82)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PURPLE

class Fuschia( GHGradient ):
    NAME = 'Fuschia'
    COLOR_RANGE = (191,112,247,35,31,69)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PURPLE

class Twilight( GHGradient ):
    NAME = 'Twilight'
    COLOR_RANGE = (255,170,255,0,69,82)
    SETS = (HAIR,DETAILS)
    FAMILY = PURPLE

class HeavyPurple( GHGradient ):
    NAME = 'Heavy Purple'
    COLOR_RANGE = (142, 96, 176,16,7,71)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = PURPLE

class KettelPurple( GHGradient ):
    NAME = 'Kettel Purple'
    COLOR_RANGE = (170,68,204,27,16,64)
    SETS = (CLOTHING,MECHA)
    FAMILY = PURPLE

class Wine( GHGradient ):
    NAME = 'Wine'
    COLOR_RANGE = (210,62,105,44,16,92)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = PURPLE

class Eggplant( GHGradient ):
    NAME = 'Eggplant'
    COLOR_RANGE = (209,95,217,60,9,98)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = PURPLE

class Grape( GHGradient ):
    NAME = 'Grape'
    COLOR_RANGE = (120,20,204,30,14,43)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = PURPLE

class ShiningViolet( GHGradient ):
    NAME = 'Shining Violet'
    COLOR_RANGE = (255,0,240,64,40,156)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = PURPLE

class Straw( GHGradient ):
    NAME = 'Straw'
    COLOR_RANGE = (236,230,140,96,35,84)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class Beige( GHGradient ):
    NAME = 'Beige'
    COLOR_RANGE = (235,185,171,45,31,60)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class RosyBrown( GHGradient ):
    NAME = 'Rosy Brown'
    COLOR_RANGE = (245,192,192,101,12,51)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class Sandstone( GHGradient ):
    NAME = 'Sandstone'
    COLOR_RANGE = (192,141,88,77,16,21)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class DarkBrown( GHGradient ):
    NAME = 'Dark Brown'
    COLOR_RANGE = (166,115,49,51,0,23)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class Cinnamon( GHGradient ):
    NAME = 'Cinnamon'
    COLOR_RANGE = (207,123,0,51,10,44)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BROWN

class Terracotta( GHGradient ):
    NAME = 'Terracotta'
    COLOR_RANGE = (237,67,45,89,31,91)
    SETS = (CLOTHING,HAIR,MECHA)
    FAMILY = BROWN

class GothSkin( GHGradient ):
    NAME = 'Goth Skin'
    COLOR_RANGE = (255,232,248,47,100,70)
    SETS = (SKIN,METAL)
    FAMILY = BROWN

class Alabaster( GHGradient ):
    NAME = 'Alabaster'
    COLOR_RANGE = (255,251,242,169,115,96)
    SETS = (CLOTHING,SKIN,MECHA)
    FAMILY = WHITE

class Maize( GHGradient ):
    NAME = 'Maize'
    COLOR_RANGE = (251,236,93,88,76,57)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS)
    FAMILY = BROWN

class Burlywood( GHGradient ):
    NAME = 'Burlywood'
    COLOR_RANGE = (255,233,170,124,48,32)
    SETS = (SKIN,MECHA,DETAILS)
    FAMILY = BROWN

class LightSkin( GHGradient ):
    NAME = 'Light Skin'
    COLOR_RANGE = (255,237,189,135,94,75)
    SETS = (SKIN,)
    FAMILY = BROWN

class SandyBrown( GHGradient ):
    NAME = 'Sandy Brown'
    COLOR_RANGE = (255,214,135,131,82,51)
    SETS = (CLOTHING,SKIN,HAIR,MECHA,DETAILS)
    FAMILY = BROWN

class TannedSkin( GHGradient ):
    NAME = 'Tanned Skin'
    COLOR_RANGE = (242,180,119,99,58,38)
    SETS = (SKIN,)
    FAMILY = BROWN

class MediumSkin( GHGradient ):
    NAME = 'Medium Skin'
    COLOR_RANGE = (236,181,147,30,20,16)
    SETS = (SKIN,)
    FAMILY = BROWN

class Leather( GHGradient ):
    NAME = 'Leather'
    COLOR_RANGE = (204,159,120,54,38,32)
    SETS = (CLOTHING,SKIN,HAIR,MECHA)
    FAMILY = BROWN

class Chocolate( GHGradient ):
    NAME = 'Chocolate'
    COLOR_RANGE = (181,91,49,51,19,14)
    SETS = (CLOTHING,SKIN,HAIR,MECHA)
    FAMILY = BROWN

class DarkSkin( GHGradient ):
    NAME = 'Dark Skin'
    COLOR_RANGE = (122,78,42,17,8,5)
    SETS = (SKIN,)
    FAMILY = BROWN

class Black( GHGradient ):
    NAME = 'Black'
    COLOR_RANGE = (64,64,64,10,10,10)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS,METAL)
    FAMILY = BLACK

class Charcoal( GHGradient ):
    NAME = 'Charcoal'
    COLOR_RANGE = (54,69,79,15,5,10)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS,METAL)
    FAMILY = BLACK

class Ebony( GHGradient ):
    NAME = 'Ebony'
    COLOR_RANGE = (85,93,80,0,0,10)
    SETS = (CLOTHING,HAIR,MECHA,DETAILS,METAL)
    FAMILY = BLACK

class GhostGrey( GHGradient ):
    NAME = 'Ghost Grey'
    COLOR_RANGE = (181,243,203,9,12,116)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = GREY

class DeepGrey( GHGradient ):
    NAME = 'Deep Grey'
    COLOR_RANGE = (102,102,120,42,42,42)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = GREY

class FieldGrey( GHGradient ):
    NAME = 'Field Grey'
    COLOR_RANGE = (98,118,103,41,50,46)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = GREY

class DimGrey( GHGradient ):
    NAME = 'Dim Grey'
    COLOR_RANGE = (140,140,140,56,56,64)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = GREY

class WarmGrey( GHGradient ):
    NAME = 'Warm Grey'
    COLOR_RANGE = (184,169,136,64,57,48)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = GREY

class BattleshipGrey( GHGradient ):
    NAME = 'Battleship Grey'
    COLOR_RANGE = (169,183,145,69,77,61)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = GREY

class LunarGrey( GHGradient ):
    NAME = 'Lunar Grey'
    COLOR_RANGE = (146,166,164,65,70,70)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = GREY

class SlateGrey( GHGradient ):
    NAME = 'Slate Grey'
    COLOR_RANGE = (143,173,196,63,69,77)
    SETS = (CLOTHING,HAIR,MECHA,METAL)
    FAMILY = GREY

class GullGrey( GHGradient ):
    NAME = 'Gull Grey'
    COLOR_RANGE = (200,220,234,80,86,98)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = GREY

class CeramicColor( GHGradient ):
    NAME = 'Ceramic'
    COLOR_RANGE = (255,255,255,90,115,124)
    SETS = (CLOTHING,MECHA,DETAILS,METAL)
    FAMILY = WHITE

class Cream( GHGradient ):
    NAME = 'Cream'
    COLOR_RANGE = (255,253,219,135,123,97)
    SETS = (CLOTHING,MECHA,DETAILS)
    FAMILY = WHITE

class White( GHGradient ):
    NAME = 'White'
    COLOR_RANGE = (255,255,255,106,95,108)
    SETS = (CLOTHING,MECHA)
    FAMILY = WHITE

class ShiningWhite( GHGradient ):
    NAME = 'Shining White'
    COLOR_RANGE = (255,255,255,0,110,120)
    SETS = (CLOTHING,MECHA,METAL)
    FAMILY = WHITE


ALL_COLORS = list()
CLOTHING_COLORS = list()
SKIN_COLORS = list()
HAIR_COLORS = list()
MECHA_COLORS = list()
DETAIL_COLORS = list()
METAL_COLORS = list()

COLOR_LISTS = {
    CLOTHING: CLOTHING_COLORS,
    SKIN: SKIN_COLORS,
    HAIR: HAIR_COLORS,
    MECHA: MECHA_COLORS,
    DETAILS: DETAIL_COLORS,
    METAL: METAL_COLORS
}

CHARACTER_COLOR_LISTS = (CLOTHING_COLORS,SKIN_COLORS,HAIR_COLORS,DETAIL_COLORS,CLOTHING_COLORS)
CHARACTER_COLOR_CHANNELS = (CLOTHING,SKIN,HAIR,DETAILS,CLOTHING)

MECHA_COLOR_CHANNELS = (MECHA,MECHA,DETAILS,METAL,MECHA)

def random_character_colors():
    return [random.choice(CLOTHING_COLORS),random.choice(SKIN_COLORS),random.choice(HAIR_COLORS),random.choice(DETAIL_COLORS),random.choice(CLOTHING_COLORS)]

def random_mecha_colors():
    return [random.choice(MECHA_COLORS),random.choice(MECHA_COLORS),random.choice(DETAIL_COLORS),random.choice(METAL_COLORS),random.choice(MECHA_COLORS)]

def choose_color_by_tags(all_these_tags):
    # Choose a color which has all of the requested tags. Return None if no appropriate colors found.
    candidates = [c for c in ALL_COLORS if c.get_tags().issuperset(all_these_tags)]
    if candidates:
        return random.choice(candidates)







