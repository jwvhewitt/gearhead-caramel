import personality
import pbge
import json
import glob
import os.path
import collections
import random
import pygame

PORTRAIT_BITS = dict()
PORTRAIT_BITS_BY_TYPE = collections.defaultdict( list )


class Portrait(object):
    def __init__(self):
        self.bits = list()

    def get_bit_of_type(self,ptype,form_tags):
        candidates = list()
        for pb in PORTRAIT_BITS_BY_TYPE[ptype]:
            if pb.is_legal_bit(form_tags):
                candidates.append(pb)
        if candidates:
            return random.choice(candidates)

    def random_portrait(self):
        frontier = ["Base",]
        form_tags = list()
        while frontier:
            nu_part = self.get_bit_of_type(frontier.pop(),form_tags)
            if nu_part:
                self.bits.append(nu_part.name)
                frontier += nu_part.children
                form_tags += nu_part.form_tags

    def build_portrait(self):
        layers = list()
        anchors = dict()
        for bitname in self.bits:
            bit = PORTRAIT_BITS.get(bitname)
            layers += bit.layers
            anchors.update(bit.anchors)
        layers.sort(key=lambda a: a.depth)

        porimage = pbge.image.Image(frame_width=400,frame_height=600)

        for l in layers:
            mysprite = pbge.image.Image(l.fname,frame_width=l.frame_width,frame_height=l.frame_height,custom_frames=l.custom_frames)
            mydest = l.get_rect(mysprite,porimage.bitmap,anchors)
            mysprite.render(mydest,l.frame,porimage.bitmap)

        return porimage

class PortraitLayer(object):
    def __init__(self,fname=None,depth=0,frame=0,frame_width=0,frame_height=0,custom_frames=None,anchor="center",x_offset=0,y_offset=0,**kwargs):
        self.fname = fname
        self.depth = depth
        self.frame = frame
        self.anchor = anchor
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.custom_frames = custom_frames
        self.x_offset = x_offset
        self.y_offset = y_offset
        for k,v in kwargs.items():
            setattr(self,k,v)
    LAYER_OFFSETS = {"left_eye":"head","right_eye":"head","mouth":"head","ear":"head"}
    def get_rect(self,limage,canvas,anchors):
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
    def __init__(self,name="No_Name",btype="No_Type",layers=(),children=(),anchors=dict(),form_tags=(),fit_forms=(),**kwargs):
        self.name = name
        self.btype = btype
        self.layers = list()
        self.anchors = dict()
        self.anchors.update(anchors)
        for l in layers:
            self.layers.append(PortraitLayer(**l))
        self.children = list(children)
        self.form_tags = list(form_tags)
        self.fit_forms = set(fit_forms)
        for k,v in kwargs.items():
            setattr(self,k,v)
    def is_legal_bit(self,existing_form_tags):
        if self.fit_forms:
            return self.fit_forms.intersection(existing_form_tags)
        else:
            return True

def init_portraits():
    # Load all the json portrait descriptions.
    portrait_bits_list = list()
    for p in pbge.image.search_path:
        myfiles = glob.glob(os.path.join(p,"portrait_*.json"))
        for f in myfiles:
            with open(f,'rb') as fp:
                mylist = json.load(fp)
                if mylist:
                    portrait_bits_list += mylist
    global PORTRAIT_BITS
    global PORTRAIT_BITS_BY_TYPE
    for pbdict in portrait_bits_list:
        pb = PortraitBit(**pbdict)
        PORTRAIT_BITS[pb.name] = pb
        PORTRAIT_BITS_BY_TYPE[pb.btype].append(pb)

