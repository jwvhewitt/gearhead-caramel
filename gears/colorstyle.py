import color
import random
import tags
import personality

ALL_STYLES = list()

class Style(object):
    def __init__(self, name, personality_tags, for_characters=True, channel_tags=(None,None,None,None,None)):
        self.name = name
        self.personality_tags = personality_tags
        self.for_characters = for_characters
        self.channel_tags = channel_tags

    def generate_colors(self, default_color_channels=color.MECHA_COLOR_CHANNELS):
        mylist = [random.choice(color.COLOR_LISTS[chan]) for chan in default_color_channels]

        for t in range(5):
            if self.channel_tags[t]:
                new_color = color.choose_color_by_tags(self.channel_tags[t])
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
                    channel_tags = ((color.BLACK,color.CLOTHING),None,None,(color.YELLOW,),(color.BLUE,color.CLOTHING)))

DZPoliceStyle = Style("Deadzone Police Style", {tags.Police,},
                    channel_tags = ((color.GREY,color.CLOTHING),None,None,(color.YELLOW,),(color.BLUE,color.CLOTHING)))

RiotSquadStyle = Style("Riot Squad Style", {tags.Police,},
                    channel_tags = ((color.BLACK,color.CLOTHING),None,None,(color.RED,),(color.BLUE,color.CLOTHING)))

GothStyle = Style("Goth Style", {personality.Grim,},
                    channel_tags = ((color.BLACK,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

GothMetalStyle = Style("Goth Metal Style", {personality.Grim,personality.Passionate},
                    channel_tags = ((color.BLACK,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)))

GreyGothStyle = Style("Grey Goth Style", {personality.Grim,personality.Shy},
                    channel_tags = ((color.BLACK,color.CLOTHING),None,None,(color.WHITE,),(color.GREY,color.CLOTHING)))

WallflowerStyle = Style("Wallflower Style", {personality.Shy,},
                    channel_tags = ((color.PURPLE,color.CLOTHING),None,None,None,(color.GREY,color.CLOTHING)))

SunnyStyle = Style("Sunny Style", {personality.Cheerful,},
                    channel_tags = ((color.YELLOW,color.CLOTHING),None,None,None,(color.ORANGE,color.CLOTHING)))

RosyStyle = Style("Rosy Style", {personality.Cheerful,personality.Sociable},
                    channel_tags = ((color.PINK,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)))

PeachyStyle = Style("Peachy Style", {personality.Easygoing,personality.Sociable},
                    channel_tags = ((color.WHITE,color.CLOTHING),None,None,None,(color.PINK,color.CLOTHING)))

DeadZoneStyle  = Style("Dead Zone Style", {personality.DeadZone,},
                    channel_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.GREY,color.CLOTHING)))

CamoStyle = Style("Camo Style", {tags.Military,},
                    channel_tags = ((color.GREEN,color.CLOTHING),None,None,(color.GREY,color.METAL),(color.BROWN,color.CLOTHING)))

CamoStyle2 = Style("Camo Style 2", {tags.Military,},
                    channel_tags = ((color.GREEN,color.CLOTHING),None,None,(color.METAL,),(color.GREY,color.CLOTHING)))

DesertCamoStyle = Style("Desert Camo Style", {tags.Military,personality.DeadZone},
                    channel_tags = ((color.BROWN,color.CLOTHING),None,None,(color.GREY,color.METAL),(color.YELLOW,color.CLOTHING)))


DoctorStyle = Style("Medical Style", {tags.Medic,},
                    channel_tags = ((color.WHITE,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)))

GloryAdventure = Style("Glory Adventure", {tags.Adventurer,personality.Glory},
                    channel_tags = ((color.RED,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

PeaceAdventure = Style("Peace Adventure", {tags.Adventurer,personality.Peace},
                    channel_tags = ((color.GREEN,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

JusticeAdventure = Style("Justice Adventure", {tags.Adventurer,personality.Justice},
                    channel_tags = ((color.BLUE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

DutyAdventure = Style("Duty Adventure", {tags.Adventurer,personality.Duty},
                    channel_tags = ((color.PURPLE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

FellowshipAdventure = Style("Fellowship Adventure", {tags.Adventurer,personality.Peace},
                    channel_tags = ((color.ORANGE,color.CLOTHING),None,None,None,(color.WHITE,color.CLOTHING)))

CriminalStyle = Style("Criminal Style", {tags.Criminal,},
                    channel_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.PURPLE,color.CLOTHING)))

SmoothCriminalStyle = Style("Smooth Criminal Style", {tags.Criminal,personality.Passionate},
                    channel_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.RED,color.CLOTHING)))

LaborStyle  = Style("Labor Style", {tags.Laborer,},
                    channel_tags = ((color.BROWN,color.CLOTHING),None,None,None,(color.BLUE,color.CLOTHING)))

HotBloodedStyle = Style("Hot Blooded Style", {personality.Passionate,personality.Cheerful},
                    channel_tags = ((color.RED,color.CLOTHING),None,None,None,(color.YELLOW,color.CLOTHING)))
