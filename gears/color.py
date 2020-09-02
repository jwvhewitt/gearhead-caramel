from pbge.image import Gradient
import random

class GHGradient( Gradient ):
    def __init__(self,name,color_range,sets=(),family=-1):
        super().__init__(name,color_range)
        self.sets = sets
        self.family = family
    def get_tags(self):
        return set(self.sets + (self.family,))

CLOTHING,SKIN,HAIR,MECHA,DETAILS,METAL = list(range(6))

# Color Families- the eleven basic color words in English.
PINK,RED,ORANGE,YELLOW,GREEN,BLUE,PURPLE,BROWN,GREY,BLACK,WHITE = list(range(100,111))

ChannelRed = GHGradient('Channel Red',(255,0,0,0,0,0),(),-1)
ChannelYellow = GHGradient('Channel Yellow',(255,255,0,0,0,0),(),-1)
ChannelGreen = GHGradient('Channel Green',(0,255,0,0,0,0),(),-1)
ChannelCyan = GHGradient('Channel Cyan',(0,255,255,0,0,0),(),-1)
ChannelMagenta = GHGradient('Channel Magenta',(255,0,255,0,0,0),(),-1)


RoyalPink = GHGradient('Royal Pink',(255,135,241,80,43,54),(CLOTHING,MECHA,DETAILS),PINK)
Pink = GHGradient('Pink',(255,230,208,149,16,100),(CLOTHING,HAIR,MECHA,DETAILS),PINK)
HotPink = GHGradient('Hot Pink',(255,92,133,120,14,98),(CLOTHING,HAIR,MECHA,DETAILS),PINK)
Magenta = GHGradient('Magenta',(255,0,215,45,0,95),(CLOTHING,HAIR,MECHA,DETAILS),PINK)
AegisCrimson = GHGradient('Aegis Crimson',(255,45,109,41,3,33),(CLOTHING,MECHA,DETAILS),PINK)
Maroon = GHGradient('Maroon',(240,61,134,25,6,31),(CLOTHING,HAIR,MECHA),PINK)

CardinalRed = GHGradient('Cardinal Red',(240,80,72,32,8,12),(CLOTHING,MECHA),RED)
BrightRed = GHGradient('Bright Red',(255,57,56,112,4,12),(CLOTHING,HAIR,MECHA,DETAILS),RED)
GunRed = GHGradient('Gun Red',(248,20,20,69,5,26),(CLOTHING,HAIR,MECHA,DETAILS),RED)
PirateSunrise = GHGradient('Pirate Sunrise',(235,57,13,47,0,22),(CLOTHING,HAIR,MECHA),RED)
AceScarlet = GHGradient('Ace Scarlet',(255,96,72,60,19,27),(CLOTHING,HAIR,MECHA),RED)
BlackRose = GHGradient('Black Rose',(172,20,54,37,0,20),(CLOTHING,HAIR,MECHA),RED)
CometRed = GHGradient('Comet Red',(209,76,82,58,27,33),(CLOTHING,HAIR,MECHA),RED)
OrangeRed = GHGradient('Orange Red',(255,100,0,45,9,9),(CLOTHING,HAIR,MECHA,DETAILS),RED)

Persimmon = GHGradient('Persimmon',(255,159,90,77,16,0),(CLOTHING,HAIR,MECHA,DETAILS),ORANGE)
HunterOrange = GHGradient('Hunter Orange',(255,145,0,32,0,48),(CLOTHING,HAIR,MECHA,DETAILS),ORANGE)
Orange = GHGradient('Orange',(255,187,0,109,0,32),(CLOTHING,HAIR,MECHA,DETAILS),ORANGE)
Saffron = GHGradient('Saffron',(255,255,142,157,0,0),(CLOTHING,HAIR,MECHA,DETAILS),ORANGE)

DesertYellow = GHGradient('Desert Yellow',(229,234,163,26,32,15),(CLOTHING,MECHA),YELLOW)
Khaki = GHGradient('Khaki',(252,240,147,32,64,39),(CLOTHING,MECHA),YELLOW)
LemonYellow = GHGradient('Lemon Yellow',(255,255,77,74,80,56),(CLOTHING,HAIR,MECHA,DETAILS),YELLOW)
Gold = GHGradient('Gold',(0xDB,0xF8,0x96,0xDD,0x7C,0x00),(CLOTHING,HAIR,MECHA,DETAILS,METAL),YELLOW)
ElectricYellow = GHGradient('Electric Yellow',(255,224,0,120,69,80),(CLOTHING,HAIR,MECHA,DETAILS),YELLOW)
NobleGold = GHGradient('NobleGold',(255,249,128,69,38,23),(CLOTHING,HAIR,MECHA,DETAILS,METAL),YELLOW)
CharredBlonde = GHGradient('Charred Blonde',(255,255,208,111,80,56),(HAIR,MECHA,DETAILS),YELLOW)
Mustard = GHGradient('Mustard',(179,139,19,41,36,4),(CLOTHING,HAIR,MECHA,DETAILS),YELLOW)

GreenYellow = GHGradient('Green Yellow',(239,255,60,16,89,55),(CLOTHING,HAIR,MECHA,DETAILS),GREEN)
Celadon = GHGradient('Celadon',(232,255,190,19,60,46),(CLOTHING,HAIR,MECHA,DETAILS),GREEN)
MountainDew = GHGradient('Mountain Dew',(194,243,227,51,64,62),(CLOTHING,HAIR,MECHA,DETAILS),GREEN)
Avocado = GHGradient('Avocado',(183,224,82,31,34,36),(CLOTHING,HAIR,MECHA,DETAILS),GREEN)
ArmyDrab = GHGradient('Army Drab',(127,201,150,21,32,42),(CLOTHING,MECHA),GREEN)
GrassGreen = GHGradient('Grass Green',(138,232,93,3,47,70),(CLOTHING,HAIR,MECHA),GREEN)
Cactus = GHGradient('Cactus',(118,184,94,2,51,49),(CLOTHING,HAIR,MECHA),GREEN)
GriffinGreen = GHGradient('Griffin Green',(60,135,70,2,24,10),(CLOTHING,HAIR,MECHA),GREEN)
Olive = GHGradient('Olive',(126,153,72,13,18,8),(CLOTHING,HAIR,MECHA),GREEN)

DarkGreen = GHGradient('Dark Green',(43,140,0,0,36,26),(CLOTHING,HAIR,MECHA),GREEN)
MassiveGreen = GHGradient('Massive Green',(78,161,107,0,9,43),(CLOTHING,MECHA),GREEN)
ForestGreen = GHGradient('ForestGreen',(78,204,52,12,50,19),(CLOTHING,HAIR,MECHA),GREEN)
Malachite = GHGradient('Malachite',(0,255,94,12,78,35),(CLOTHING,HAIR,MECHA,DETAILS),GREEN)
SeaGreen = GHGradient('SeaGreen',(89,169,153,0,32,29),(CLOTHING,HAIR,MECHA),GREEN)
Jade = GHGradient('Jade',(115,255,223,17,49,87),(CLOTHING,HAIR,MECHA),GREEN)
Viridian = GHGradient('Viridian',(104,213,169,7,40,90),(CLOTHING,HAIR,MECHA),GREEN)
DoctorGreen = GHGradient('Doctor Green',(85,236,193,24,66,54),(CLOTHING,HAIR,MECHA),GREEN)
FlourescentGreen = GHGradient('Flourescent Green',(222,255,0,0,121,106),(HAIR,DETAILS),GREEN)

AeroBlue = GHGradient('Aero Blue',(240,252,255,42,66,93),(CLOTHING,MECHA,DETAILS,METAL),BLUE)
Aquamarine = GHGradient('Aquamarine',(171,255,240,50,0,103),(CLOTHING,HAIR,MECHA,DETAILS),BLUE)
SkyBlue = GHGradient('Sky Blue',(96,255,255,30,88,118),(CLOTHING,HAIR,MECHA,DETAILS),BLUE)
Cyan = GHGradient('Cyan',(0,255,234,0,79,86),(CLOTHING,HAIR,MECHA,DETAILS),BLUE)
Turquoise = GHGradient('Turquoise',(50,250,222,60,0,90),(CLOTHING,HAIR,MECHA,DETAILS),BLUE)
FadedDenim = GHGradient('Faded Denim',(222,233,249,0,7,97),(CLOTHING,HAIR,MECHA),BLUE)
SteelBlue = GHGradient('Steel Blue',(117,183,230,38,17,50),(CLOTHING,HAIR,MECHA,METAL),BLUE)
FreedomBlue = GHGradient('Freedom Blue',(21,177,255,12,3,36),(CLOTHING,HAIR,MECHA),BLUE)
PlasmaBlue = GHGradient('Plasma Blue',(247,255,232,0,128,171),(CLOTHING,HAIR,MECHA,DETAILS),BLUE)
Azure = GHGradient('Azure',(47,151,198,26,0,79),(CLOTHING,HAIR,MECHA),BLUE)
BugBlue = GHGradient('Bug Blue',(49,85,153,46,3,43),(CLOTHING,HAIR,MECHA),BLUE)
Cobalt = GHGradient('Cobalt',(8,79,179,17,3,64),(CLOTHING,HAIR,MECHA,METAL),BLUE)
PrussianBlue = GHGradient('Prussian Blue',(0,136,217,10,10,18),(CLOTHING,HAIR,MECHA),BLUE)
MidnightBlue = GHGradient('Midnight Blue',(37,60,163,10,0,16),(CLOTHING,HAIR,MECHA),BLUE)
DeepSeaBlue = GHGradient('Deep Sea Blue',(99,136,172,25,5,41),(CLOTHING,HAIR,MECHA),BLUE)

StarViolet = GHGradient('Star Violet',(236,163,231,48,24,82),(CLOTHING,HAIR,MECHA,DETAILS),PURPLE)
Fuschia = GHGradient('Fuschia',(191,112,247,35,31,69),(CLOTHING,HAIR,MECHA,DETAILS),PURPLE)
Twilight = GHGradient('Twilight',(255,170,255,0,69,82),(HAIR,DETAILS),PURPLE)
HeavyPurple = GHGradient('Heavy Purple',(142, 96, 176,16,7,71),(CLOTHING,HAIR,MECHA),PURPLE)
KettelPurple = GHGradient('Kettel Purple',(170,68,204,27,16,64),(CLOTHING,MECHA),PURPLE)
Wine = GHGradient('Wine',(210,62,105,44,16,92),(CLOTHING,HAIR,MECHA),PURPLE)
Eggplant = GHGradient('Eggplant',(209,95,217,60,9,98),(CLOTHING,HAIR,MECHA),PURPLE)
Grape = GHGradient('Grape',(120,20,204,30,14,43),(CLOTHING,HAIR,MECHA),PURPLE)
ShiningViolet = GHGradient('Shining Violet',(255,0,240,64,40,156),(CLOTHING,HAIR,MECHA,DETAILS),PURPLE)

Straw = GHGradient('Straw',(236,230,140,96,35,84),(CLOTHING,HAIR,MECHA),BROWN)
Beige = GHGradient('Beige',(235,185,171,45,31,60),(CLOTHING,HAIR,MECHA),BROWN)
RosyBrown = GHGradient('Rosy Brown',(245,192,192,101,12,51),(CLOTHING,HAIR,MECHA),BROWN)
Sandstone = GHGradient('Sandstone',(192,141,88,77,16,21),(CLOTHING,HAIR,MECHA),BROWN)
DarkBrown = GHGradient('Dark Brown',(166,115,49,51,0,23),(CLOTHING,HAIR,MECHA),BROWN)
Cinnamon = GHGradient('Cinnamon',(207,123,0,51,10,44),(CLOTHING,HAIR,MECHA,DETAILS),BROWN)
Terracotta = GHGradient('Terracotta',(237,67,45,89,31,91),(CLOTHING,HAIR,MECHA),BROWN)
GothSkin = GHGradient('Goth Skin',(255,232,248,47,100,70),(SKIN,METAL),BROWN)
Maize = GHGradient('Maize',(251,236,93,88,76,57),(CLOTHING,HAIR,MECHA,DETAILS),BROWN)
Burlywood = GHGradient('Burlywood',(255,233,170,124,48,32),(SKIN,MECHA,DETAILS),BROWN)

LightSkin = GHGradient('Light Skin',(255,237,189,135,94,75),(SKIN,),BROWN)
SandyBrown = GHGradient('Sandy Brown',(255,214,135,131,82,51),(CLOTHING,SKIN,HAIR,MECHA,DETAILS),BROWN)
TannedSkin = GHGradient('Tanned Skin',(242,180,119,99,58,38),(SKIN,),BROWN)
MediumSkin = GHGradient('Medium Skin',(236,181,147,30,20,16),(SKIN,),BROWN)
ForRami = GHGradient('For Rami', (249,182,137,86,57,25), (SKIN,), BROWN)
Leather = GHGradient('Leather',(204,159,120,54,38,32),(CLOTHING,SKIN,HAIR,MECHA),BROWN)
Chocolate = GHGradient('Chocolate',(181,91,49,51,19,14),(CLOTHING,SKIN,HAIR,MECHA),BROWN)
DarkSkin = GHGradient('Dark Skin',(122,78,42,17,8,5),(SKIN,),BROWN)

Black = GHGradient('Black',(64,64,64,10,10,10),(CLOTHING,HAIR,MECHA,DETAILS,METAL),BLACK)
Charcoal = GHGradient('Charcoal',(54,69,79,15,5,10),(CLOTHING,HAIR,MECHA,DETAILS,METAL),BLACK)
Ebony = GHGradient('Ebony',(85,93,80,0,0,10),(CLOTHING,HAIR,MECHA,DETAILS,METAL),BLACK)

GhostGrey = GHGradient('Ghost Grey',(181,243,203,9,12,116),(CLOTHING,MECHA,METAL),GREY)
DeepGrey = GHGradient('Deep Grey',(102,102,120,42,42,42),(CLOTHING,HAIR,MECHA,METAL),GREY)
FieldGrey = GHGradient('Field Grey',(98,118,103,41,50,46),(CLOTHING,MECHA,METAL),GREY)
DimGrey = GHGradient('Dim Grey',(140,140,140,56,56,64),(CLOTHING,HAIR,MECHA,METAL),GREY)
WarmGrey = GHGradient('Warm Grey',(184,169,136,64,57,48),(CLOTHING,MECHA,METAL),GREY)
BattleshipGrey = GHGradient('Battleship Grey',(169,183,145,69,77,61),(CLOTHING,HAIR,MECHA,METAL),GREY)
LunarGrey = GHGradient('Lunar Grey',(146,166,164,65,70,70),(CLOTHING,MECHA,METAL),GREY)
SlateGrey = GHGradient('Slate Grey',(143,173,196,63,69,77),(CLOTHING,HAIR,MECHA,METAL),GREY)
GullGrey = GHGradient('Gull Grey',(200,220,234,80,86,98),(CLOTHING,MECHA,METAL),GREY)

CeramicColor = GHGradient('Ceramic',(255,255,255,90,115,124),(CLOTHING,MECHA,DETAILS,METAL),WHITE)
Cream = GHGradient('Cream',(255,253,219,135,123,97),(CLOTHING,MECHA,DETAILS),WHITE)
White = GHGradient('White',(255,255,255,106,95,108),(CLOTHING,MECHA),WHITE)
ShiningWhite = GHGradient('Shining White',(255,255,255,0,110,120),(CLOTHING,MECHA,METAL),WHITE)
Alabaster = GHGradient('Alabaster',(255,251,242,169,115,96),(CLOTHING,SKIN,MECHA),WHITE)


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

def mutate_colors(original_color_tuple):
    mylist = list()
    for c in original_color_tuple:
        if random.randint(1,3) != 2:
            mylist.append(c)
        else:
            mylist.append(choose_color_by_tags([c.family]))
    return tuple(mylist)






