import color
import random
import tags
import personality

ALL_STYLES = list()

class Style(object):
    def __init__(self, name, personality_tags, chara_tags=(None,None,None,None,None), mecha_tags=(None,None,None,None,None)):
        self.name = name
        self.personality_tags = personality_tags
        self.chara_tags = chara_tags
        self.mecha_tags = mecha_tags

    def generate_chara_colors(self, default_color_channels=color.CHARACTER_COLOR_CHANNELS):
        mylist = [random.choice(color.COLOR_LISTS[chan]) for chan in default_color_channels]

        for t in range(5):
            if self.chara_tags[t]:
                new_color = color.choose_color_by_tags(self.chara_tags[t])
                if new_color:
                    mylist[t] = new_color
        return mylist

    def generate_mecha_colors(self, default_color_channels=color.MECHA_COLOR_CHANNELS):
        mylist = [random.choice(color.COLOR_LISTS[chan]) for chan in default_color_channels]

        for t in range(5):
            if self.mecha_tags[t]:
                new_color = color.choose_color_by_tags(self.mecha_tags[t])
                if new_color:
                    mylist[t] = new_color
        return mylist

def choose_style(npc):
    npc_tags = set(npc.get_tags())
    candidates = [s for s in ALL_STYLES if s.personality_tags <= npc_tags]
    if candidates:
        return random.choice( candidates )



# Character Styles

PoliceStyle = Style("Police Style", {tags.Police,},
                    chara_tags = ((color.BLACK,color.CLOTHING),None,None,(color.YELLOW,),(color.BLUE,color.CLOTHING)),
                    mecha_tags=((color.BLUE,color.MECHA),(color.WHITE,color.MECHA),None,None,(color.BLACK,color.MECHA)))

DZPoliceStyle = Style("Deadzone Police Style", {tags.Police,},
                    chara_tags = ((color.GREY,color.CLOTHING),None,None,(color.YELLOW,),(color.BLUE,color.CLOTHING)),
                    mecha_tags=((color.GREY,color.MECHA),(color.WHITE,color.MECHA),None,None,(color.BLUE,color.MECHA)))

RiotSquadStyle = Style("Riot Squad Style", {tags.Police,},
                    chara_tags = ((color.BLACK,color.CLOTHING),None,None,(color.RED,),(color.BLUE,color.CLOTHING)),
                    mecha_tags=((color.BLUE,color.MECHA),(color.RED,color.MECHA),None,None,(color.BLACK,color.MECHA)))

GothStyle = Style("Goth Style", {personality.Grim,},
                    chara_tags = ((color.BLACK,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.BLACK,color.MECHA),None,None,None,(color.WHITE,color.MECHA)))

GothMetalStyle = Style("Goth Metal Style", {personality.Grim,personality.Passionate},
                    chara_tags = ((color.BLACK,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)),
                    mecha_tags=((color.BLACK,color.MECHA),(color.RED,color.MECHA),None,None,None))

GreyGothStyle = Style("Grey Goth Style", {personality.Grim,personality.Shy},
                    chara_tags = ((color.BLACK,color.CLOTHING),None,None,(color.WHITE,),(color.GREY,color.CLOTHING)),
                    mecha_tags=((color.BLACK,color.MECHA),(color.GREY,color.MECHA),None,None,(color.WHITE,color.MECHA)))

WallflowerStyle = Style("Wallflower Style", {personality.Shy,},
                    chara_tags = ((color.PURPLE,color.CLOTHING),None,None,None,(color.GREY,color.CLOTHING)),
                    mecha_tags=((color.GREY,color.MECHA),(color.PURPLE,color.MECHA),None,None,(color.BLACK,color.MECHA)))

SunnyStyle = Style("Sunny Style", {personality.Cheerful,},
                    chara_tags = ((color.YELLOW,color.CLOTHING),None,None,None,(color.ORANGE,color.CLOTHING)),
                    mecha_tags=((color.ORANGE,color.MECHA),(color.YELLOW,color.MECHA),None,None,None))

RosyStyle = Style("Rosy Style", {personality.Cheerful,personality.Sociable},
                    chara_tags = ((color.PINK,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)),
                    mecha_tags=((color.PINK,color.MECHA),None,None,None,(color.RED,color.MECHA)))

PeachyStyle = Style("Peachy Style", {personality.Easygoing,personality.Sociable},
                    chara_tags = ((color.WHITE,color.CLOTHING),None,None,None,(color.PINK,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.PINK,color.MECHA),None,None,None))

DeadZoneStyle  = Style("Dead Zone Style", {personality.DeadZone,},
                    chara_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.GREY,color.CLOTHING)),
                    mecha_tags=((color.GREY,color.MECHA),None,None,None,(color.BROWN,color.MECHA)))

CamoStyle = Style("Camo Style", {tags.Military,},
                    chara_tags = ((color.GREEN,color.CLOTHING),None,None,(color.GREY,color.METAL),(color.BROWN,color.CLOTHING)),
                    mecha_tags=((color.GREEN,color.MECHA),(color.BROWN,color.MECHA),None,None,(color.GREEN,color.MECHA)))

CamoStyle2 = Style("Camo Style 2", {tags.Military,},
                    chara_tags = ((color.GREEN,color.CLOTHING),None,None,(color.METAL,),(color.GREY,color.CLOTHING)),
                    mecha_tags=((color.GREEN,color.MECHA),(color.BROWN,color.MECHA),None,None,(color.GREEN,color.MECHA)))

DesertCamoStyle = Style("Desert Camo Style", {tags.Military,personality.DeadZone},
                    chara_tags = ((color.BROWN,color.CLOTHING),None,None,(color.GREY,color.METAL),(color.YELLOW,color.CLOTHING)),
                    mecha_tags=((color.BROWN,color.MECHA),(color.YELLOW,color.MECHA),None,None,(color.GREY,color.MECHA)))


DoctorStyle = Style("Medical Style", {tags.Medic,},
                    chara_tags = ((color.WHITE,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.RED,color.MECHA),None,None,None))

GloryAdventure = Style("Glory Adventure", {tags.Adventurer,personality.Glory},
                    chara_tags = ((color.RED,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.RED,color.MECHA),None,None,(color.GREY,color.MECHA)))

PeaceAdventure = Style("Peace Adventure", {tags.Adventurer,personality.Peace},
                    chara_tags = ((color.GREEN,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.GREEN,color.MECHA),None,None,(color.GREY,color.MECHA)))

JusticeAdventure = Style("Justice Adventure", {tags.Adventurer,personality.Justice},
                    chara_tags = ((color.BLUE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.BLUE,color.MECHA),None,None,(color.BLACK,color.MECHA)))

DutyAdventure = Style("Duty Adventure", {tags.Adventurer,personality.Duty},
                    chara_tags = ((color.PURPLE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.GREY,color.MECHA),(color.PURPLE,color.MECHA),None,None,(color.WHITE,color.MECHA)))

FellowshipAdventure = Style("Fellowship Adventure", {tags.Adventurer,personality.Peace},
                    chara_tags = ((color.ORANGE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)),
                    mecha_tags=((color.WHITE,color.MECHA),(color.ORANGE,color.MECHA),None,None,(color.BROWN,color.MECHA)))

CriminalStyle = Style("Criminal Style", {tags.Criminal,},
                    chara_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.PURPLE,color.CLOTHING)),
                    mecha_tags=((color.BLACK,color.MECHA),None,None,None,(color.BROWN,color.MECHA)))

SmoothCriminalStyle = Style("Smooth Criminal Style", {tags.Criminal,personality.Passionate},
                    chara_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)),
                    mecha_tags=((color.BLACK,color.MECHA),None,None,None,(color.RED,color.MECHA)))

LaborStyle  = Style("Labor Style", {tags.Laborer,},
                    chara_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.BLUE,color.CLOTHING)),
                    mecha_tags=((color.BROWN,color.MECHA),(color.GREY,color.MECHA),None,None,(color.BLUE,color.MECHA)))

HotBloodedStyle = Style("Hot Blooded Style", {personality.Passionate,personality.Cheerful},
                    chara_tags = ((color.RED,color.CLOTHING),None,None,None,(color.YELLOW,color.CLOTHING)),
                    mecha_tags=((color.RED,color.MECHA),(color.DETAILS,),None,None,(color.ORANGE,color.MECHA)))
