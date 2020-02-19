import collections
import glob
import json
import os.path
import random
from . import stats
from . import base

import pbge
import pygame
from . import color
from . import colorstyle

PORTRAIT_BITS = dict()
PORTRAIT_BITS_BY_TYPE = collections.defaultdict(list)

FRAMES = ((0, 0, 400, 600), (0, 600, 100, 100), (100, 600, 64, 64))

TAG_COMMON = "Common"

class Portrait(object):
    def __init__(self):
        self.bits = list()
        self.color_channels = list(color.CHARACTER_COLOR_CHANNELS)

    @staticmethod
    def get_list_of_type(ptype, form_tags,use_weight=True):
        candidates = list()
        for pb in PORTRAIT_BITS_BY_TYPE[ptype]:
            if pb.is_legal_bit(form_tags):
                # Generate a list. The length of the list depends on the appropriateness of this bit.
                pblist = [pb,]
                if use_weight:
                    if TAG_COMMON in pb.prefers:
                        pblist *= 3
                    tags_in_common = len(pb.prefers.intersection(form_tags))
                    if tags_in_common > 0:
                        pblist *= (3 + 2 * tags_in_common)
                candidates += pblist
        return candidates

    def get_bit_of_type(self, ptype, form_tags):
        candidates = self.get_list_of_type(ptype, form_tags)
        if candidates:
            return random.choice(candidates)

    @staticmethod
    def get_form_tags(pc,year=158):
        """

        :type pc: base.Character
        """
        form_tags = list()
        for pt in pc.get_tags():
            form_tags.append(pt.name)
        if pc.combatant:
            form_tags.append("Combatant")
        else:
            form_tags.append("Noncombatant")
        if pc.gender:
            form_tags += pc.gender.tags
        for s in stats.PRIMARY_STATS:
            sval = pc.statline.get(s,12)
            if sval < 10:
                form_tags.append("-{}".format(s.name))
            elif sval > 13:
                form_tags.append("+{}".format(s.name))
        if year - pc.birth_year <= 20:
            form_tags.append("Young")
        elif year - pc.birth_year >= 40:
            form_tags.append("Old")
        return form_tags

    def random_portrait(self, pc=None, form_tags=()):
        frontier = ["Base", ]
        self.bits = list()
        form_tags = list(form_tags)
        if pc and not form_tags:
            form_tags = self.get_form_tags(pc)
        while frontier:
            nu_part = self.get_bit_of_type(frontier.pop(), form_tags)
            if nu_part:
                self.bits.append(nu_part.name)
                frontier += nu_part.children
                form_tags += nu_part.form_tags

    def verify(self, pc, form_tags):
        # Check through the bits, make sure they're all legal, replace the ones that don't fit.
        frontier = ["Base",]
        form_tags = list(form_tags)
        bits_to_check = list(self.bits)
        self.bits = list()
        for bitname in bits_to_check:
            bit = PORTRAIT_BITS[bitname]
            if bit.btype in frontier:
                frontier.remove(bit.btype)
                if bit.is_legal_bit(form_tags):
                    self.bits.append(bitname)
                    frontier += bit.children
                    form_tags += bit.form_tags
                else:
                    # This part is not legal, but it is needed.
                    nu_part = self.get_bit_of_type(bit.btype, form_tags)
                    if nu_part:
                        self.bits.append(nu_part.name)
                        frontier += nu_part.children
                        form_tags += nu_part.form_tags
        while frontier:
            nu_part = self.get_bit_of_type(frontier.pop(), form_tags)
            if nu_part:
                self.bits.append(nu_part.name)
                frontier += nu_part.children
                form_tags += nu_part.form_tags

    def generate_random_colors(self,pc):
        mystyle = colorstyle.choose_style(pc)
        if mystyle:
            mycolors = mystyle.generate_chara_colors(self.color_channels)
            mekcolors = mystyle.generate_mecha_colors()
        else:
            mycolors = [random.choice(color.COLOR_LISTS[chan]) for chan in self.color_channels]
            mekcolors = [random.choice(color.COLOR_LISTS[chan]) for chan in color.MECHA_COLOR_CHANNELS]
        # If this character has a faction, update the colors with faction colors.
        if pc.faction and pc.faction.uniform_colors:
            for t in range(len(pc.faction.uniform_colors)):
                if pc.faction.uniform_colors[t]:
                    mycolors[t] = pc.faction.uniform_colors[t]
        if pc.faction and pc.faction.mecha_colors:
            for t in range(len(pc.faction.mecha_colors)):
                if pc.faction.mecha_colors[t] and random.randint(1,3) != 2:
                    mekcolors[t] = pc.faction.mecha_colors[t]
        pc.colors = mycolors
        pc.mecha_colors = mekcolors

    def build_portrait(self,pc,add_color=True,force_rebuild=False,form_tags=()):
        porimage = pbge.image.Image(frame_width=400, frame_height=700)
        porimage.custom_frames = FRAMES

        # Check first to see if the portrait already exists.
        if add_color and (self,repr(pc.colors)) in pbge.image.pre_loaded_images and not force_rebuild:
            porimage.bitmap = pbge.image.pre_loaded_images[(self,repr(pc.colors))]
            return porimage

        # If the portrait has not been generated yet, generate it now.
        if not self.bits:
            self.random_portrait(pc,form_tags=form_tags)

        portrait_bm = porimage.bitmap.subsurface(pygame.Rect(FRAMES[0]))
        avatar_bm = porimage.bitmap.subsurface(pygame.Rect(FRAMES[2]))

        layers = list()
        avatar_layers = list()
        anchors = dict()
        for bitname in self.bits:
            bit = PORTRAIT_BITS.get(bitname)
            layers += bit.layers
            avatar_layers += bit.avatar_layers
            anchors.update(bit.anchors)
        layers.sort(key=lambda a: a.depth)
        avatar_layers.sort(key=lambda a: a.depth)


        for l in layers:
            mysprite = pbge.image.Image(l.fname, frame_width=l.frame_width, frame_height=l.frame_height,
                                        custom_frames=l.custom_frames)
            mydest = l.get_rect(mysprite, portrait_bm, anchors)
            mysprite.render(mydest, l.frame, portrait_bm)

        for l in avatar_layers:
            mysprite = pbge.image.Image(l.fname, frame_width=l.frame_width, frame_height=l.frame_height,
                                        custom_frames=l.custom_frames)
            mydest = l.get_rect(mysprite, avatar_bm, anchors)
            mysprite.render(mydest, l.frame, avatar_bm)

        if add_color:
            if not pc.colors:
                # Generate random colors for this character.
                self.generate_random_colors(pc)

            porimage.recolor(pc.colors)
            pbge.image.Image.record_pre_loaded(self,pc.colors,porimage.bitmap)

            # Create the mini-portrait.
            myrect = pygame.Rect(100,200,200,200)
            myoffset = anchors.get("head",(10,-137))
            myrect.left += myoffset[0]
            myrect.top += myoffset[1]
            myrect.clamp_ip(pygame.Rect(FRAMES[0]))
            mini_por_source = porimage.bitmap.subsurface(myrect)
            mini_por_bm = pygame.transform.scale(mini_por_source,(100,100))
            porimage.bitmap.blit(mini_por_bm,pygame.Rect(0,600,100,100))
            # Interesting bug- saving the image messes up the alpha.
            #pygame.image.save(porimage.bitmap,pbge.util.user_dir('testportrait.png'))

        #print anchors
        return porimage

class PortraitLayer(object):
    def __init__(self, fname=None, depth=0, frame=0, frame_width=0, frame_height=0, custom_frames=None, anchor="center",
                 x_offset=0, y_offset=0, **kwargs):
        self.fname = fname
        self.depth = depth
        self.frame = frame
        self.anchor = anchor
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.custom_frames = custom_frames
        self.x_offset = x_offset
        self.y_offset = y_offset
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    LAYER_OFFSETS = {"left_eye": "head", "right_eye": "head", "mouth": "head", "ear": "head", "nose": "head"}

    def get_rect(self, limage, canvas, anchors):
        mydest = limage.get_rect(self.frame)
        if self.anchor == "midbottom":
            mydest.midbottom = canvas.get_rect().midbottom
        elif self.anchor == "center":
            mydest.center = canvas.get_rect().center
        elif self.anchor == "topleft":
            mydest.center = canvas.get_rect().topleft
        elif self.anchor in anchors:
            mydest.center = canvas.get_rect().center
            mydest.right += anchors[self.anchor][0]
            mydest.top += anchors[self.anchor][1]
            if self.anchor in self.LAYER_OFFSETS and self.LAYER_OFFSETS[self.anchor] in anchors:
                mydest.right += anchors[self.LAYER_OFFSETS[self.anchor]][0]
                mydest.top += anchors[self.LAYER_OFFSETS[self.anchor]][1]
        mydest.right += self.x_offset
        mydest.top += self.y_offset
        return mydest

class PortraitBit(object):
    def __init__(self, name="No_Name", btype="No_Type", layers=(), avatar_layers=(), children=(), anchors=(), form_tags=(),
                 requires=(), prefers=(), rejects=(), **kwargs):
        self.name = name
        self.btype = btype
        self.layers = list()
        self.anchors = dict()
        self.anchors.update(anchors)
        for l in layers:
            self.layers.append(PortraitLayer(**l))
        self.avatar_layers = list()
        for l in avatar_layers:
            self.avatar_layers.append(PortraitLayer(**l))
        self.children = list(children)
        self.form_tags = list(form_tags)
        self.requires = set(requires)
        self.prefers = set(prefers)
        self.rejects = set(rejects)
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def is_legal_bit(self, existing_form_tags):
        if self.requires:
            return self.requires.issubset(existing_form_tags) and not self.rejects.intersection(existing_form_tags)
        else:
            return not self.rejects.intersection(existing_form_tags)


def init_portraits():
    # Load all the json portrait descriptions.
    portrait_bits_list = list()
    for p in pbge.image.search_path:
        myfiles = glob.glob(os.path.join(p, "portrait_*.json"))
        for f in myfiles:
            with open(f, 'rb') as fp:
                mylist = json.load(fp)
                if mylist:
                    portrait_bits_list += mylist
    global PORTRAIT_BITS
    global PORTRAIT_BITS_BY_TYPE
    for pbdict in portrait_bits_list:
        pb = PortraitBit(**pbdict)
        PORTRAIT_BITS[pb.name] = pb
        PORTRAIT_BITS_BY_TYPE[pb.btype].append(pb)

