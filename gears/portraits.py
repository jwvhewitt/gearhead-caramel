import collections
import glob
import json
import os.path
import random

import pbge
import pygame
import color

PORTRAIT_BITS = dict()
PORTRAIT_BITS_BY_TYPE = collections.defaultdict(list)

FRAMES = ((0, 0, 400, 600), (0, 600, 100, 100), (100, 600, 64, 64))

TAG_COMMON = "Common"

class Portrait(object):
    def __init__(self):
        self.bits = list()

    @staticmethod
    def get_bit_of_type(ptype, form_tags):
        candidates = list()
        for pb in PORTRAIT_BITS_BY_TYPE[ptype]:
            if pb.is_legal_bit(form_tags):
                # Generate a list. The length of the list depends on the appropriateness of this bit.
                pblist = [pb,]
                if TAG_COMMON in pb.prefers:
                    pblist *= 3
                tags_in_common = len(pb.prefers.intersection(form_tags))
                if tags_in_common > 0:
                    pblist *= (3 + 2 * tags_in_common)
                candidates += pblist
        if candidates:
            return random.choice(candidates)

    def random_portrait(self, pc):
        frontier = ["Base", ]
        form_tags = list()
        if hasattr(pc, "gender"):
            form_tags += pc.gender.tags
        for pt in pc.personality:
            form_tags.append(pt.name)
        if pc.job:
            form_tags += [tag.name for tag in pc.job.tags]
        if pc.combatant:
            form_tags.append("Combatant")
        else:
            form_tags.append("Noncombatant")
        if pc.faction:
            form_tags.append(pc.faction.get_faction_tag().name)
        while frontier:
            nu_part = self.get_bit_of_type(frontier.pop(), form_tags)
            if nu_part:
                self.bits.append(nu_part.name)
                frontier += nu_part.children
                form_tags += nu_part.form_tags

    def build_portrait(self,pc,add_color=True):
        porimage = pbge.image.Image(frame_width=400, frame_height=700)
        porimage.custom_frames = FRAMES

        # Check first to see if the portrait already exists.
        if add_color and (self,repr(pc.colors)) in pbge.image.pre_loaded_images:
            porimage.bitmap = pbge.image.pre_loaded_images[(self,repr(pc.colors))]
            return porimage

        # If the portrait has not been generated yet, generate it now.
        if not self.bits:
            self.random_portrait(pc)

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
                pc.colors = color.random_character_colors()
                #If this character has a faction, update the colors with faction colors.

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
        for k, v in kwargs.items():
            setattr(self, k, v)

    LAYER_OFFSETS = {"left_eye": "head", "right_eye": "head", "mouth": "head", "ear": "head"}

    def get_rect(self, limage, canvas, anchors):
        mydest = limage.get_rect(self.frame)
        if self.anchor == u"midbottom":
            mydest.midbottom = canvas.get_rect().midbottom
        elif self.anchor == u"center":
            mydest.center = canvas.get_rect().center
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
                 requires=(), prefers=(), **kwargs):
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
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_legal_bit(self, existing_form_tags):
        if self.requires:
            return self.requires.issubset(existing_form_tags)
        else:
            return True


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
