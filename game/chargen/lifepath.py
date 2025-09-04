import pbge
import gears
from gears import personality, stats
import pygame

from .. import ghdialogue
import random
import json
import glob
import collections

ALL_LP_EVENTS = list()
LP_EVENTS_BY_STAGE = collections.defaultdict(list)


class BioBlock( object ):
    def __init__(self,model,width=220,bio_font=None,**kwargs):
        self.model = model
        self.width = width
        self.image:pygame.Surface=None
        self.font = bio_font or pbge.MEDIUMFONT
        self.update()

    def update(self):
        self.image = pbge.render_text(self.font, self.model.bio, self.width, justify=-1)
        self.height = self.image.get_height()

    def render(self,x,y):
        _=pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))

class CGNonComSkillBlock(object):
    def __init__(self,cgen,width=220,skill_font=None,**kwargs):
        self.cgen = cgen
        self.width = width
        self.image:pygame.Surface=None
        self.font = skill_font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        skillz = [sk.name for sk in list(self.cgen.bio_bonuses.keys()) if sk in stats.NONCOMBAT_SKILLS]
        self.image = pbge.render_text(self.font, 'Skills: {}'.format(', '.join(skillz or ["None"])), self.width, justify=-1)

    def render(self,x,y):
        _=pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))


class LifePathStatusPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (BioBlock,CGNonComSkillBlock)


STAGE_ORIGIN = "ORIGIN"
STAGE_CHILDHOOD = "CHILDHOOD"
STAGE_VOCATION = "VOCATION"
STAGE_CRISIS = "CRISIS"
STAGE_RESOLUTION = "RESOLUTION"

STAGES = (
    ("Where are you from?", STAGE_ORIGIN), 
    ("How was your early life?", STAGE_CHILDHOOD), 
    ("How did you learn to be a cavalier?", STAGE_VOCATION), 
    ("What crisis shaped your life?", STAGE_CRISIS), 
    ("What path have you chosen to walk?", STAGE_RESOLUTION)
)


class LifePathEvent:
    def __init__(
        self, name, desc, stage, biomessage="", 
        required_tags=(), forbidden_tags=(),
        new_tags=(), new_personality=(), push_stages=(), biogram=None,
        stat_mods=None, merit_badges=(), idealist_bonus=False, gain_mutation=False
    ):
        self.name = name
        self.desc = desc
        self.stage = stage
        self.biomessage = biomessage
        self.required_tags = set(self.convert_tags(required_tags))
        self.forbidden_tags = set(self.convert_tags(forbidden_tags))
        self.new_tags = set(self.convert_tags(new_tags))
        self.new_personality = set(self.convert_tags(new_personality))
        self.push_stages: list = push_stages
        self.biogram = dict()
        if biogram:
            self.biogram.update(biogram)
        self.stat_mods = dict()
        if stat_mods:
            for k,v in stat_mods.items():
                st = gears.SINGLETON_TYPES.get(k, gears.stats.Body)
                self.stat_mods[st] = v
        self.merit_badges = list(self.convert_tags(merit_badges))
        self.idealist_bonus = idealist_bonus
        self.gain_mutation = gain_mutation
        ALL_LP_EVENTS.append(self)
        LP_EVENTS_BY_STAGE[self.stage].append(self)

    @staticmethod
    def convert_tags(taglist):
        nulist = list()
        for tag in taglist:
            if tag in gears.SINGLETON_TYPES:
                nulist.append(gears.SINGLETON_TYPES[tag])
            else:
                nulist.append(tag)
        return nulist

    def apply(self,lpath: "Lifepath"):
        lpath.biogram.absorb(self.biogram)
        if self.gain_mutation:
            self.apply_mutation(lpath)
        if self.biomessage:
            nugramdict = lpath.biogram.copy()
            ghdialogue.trait_absorb(nugramdict,ghdialogue.ghgrammar.DEFAULT_GRAMMAR,lpath.tags)
            lpath.bio_text += ' {}: '.format(self.stage) + pbge.dialogue.grammar.convert_tokens(self.biomessage,nugramdict,allow_maybe=False)
        for k,v in list(self.stat_mods.items()):
            lpath.bio_bonuses[k] += v
        gears.meritbadges.add_badges(lpath.bio_badges,self.merit_badges)
        lpath.bio_personality += self.new_personality
        lpath.lifepath_tags |= self.new_tags
        if self.idealist_bonus:
            self.apply_idealist_bonus(lpath)
        for stage in reversed(self.push_stages):
            lpath.stages.insert(0, stage)

    def apply_idealist_bonus(self, lpath: "Lifepath"):
        stat_list = random.sample(gears.stats.PRIMARY_STATS,3)
        for s in stat_list:
            lpath.bio_bonuses[s] += 2

    MUTANT_BIOGRAM = {
        personality.FelineMutation: [
            "feline features", "cat ears", "feline ears"
        ],
        personality.DraconicMutation: [
            "scaly skin", "armored plates on your skin",
            "bonelike growths protruding from your flesh"
        ],
        personality.GeneralMutation: [
            "brightly colored skin", "visible mutations"
        ]
    }

    def apply_mutation(self, lpath):
        mutation = random.choice(gears.mutations.MUTATIONS)
        lpath.bio_personality.append(mutation)
        bonuses = mutation.get_stat_modifier()
        for k,v in bonuses.items():
            lpath.bio_bonuses[k] += v

        lpath.biogram["[mutation]"] = self.MUTANT_BIOGRAM[mutation]

    def matches(self, lpath):
        return self.required_tags.issubset(lpath.tags) and self.forbidden_tags.isdisjoint(lpath.tags)


class Lifepath:
    def __init__(self):
        self.biogram = pbge.dialogue.grammar.Grammar()
        self.bio_personality = list()
        self.bio_badges = list()
        self.bio_bonuses = collections.defaultdict(int)
        self.bio_text = ""
        self.lifepath_tags = set()
        self.stages = list(STAGES)
        self.mutation = None

    @property
    def tags(self):
        ptags = set(self.bio_personality)
        for badge in self.bio_badges:
            if hasattr(badge, "tags") and badge.tags:
                ptags |= badge.tags
        return set(self.bio_personality) | ptags

    def get_candidates_for_stage(self, stage):
        return [a for a in LP_EVENTS_BY_STAGE[stage] if a.matches(self)]

    @classmethod
    def random_lifepath(cls):
        mylp = cls()

        while mylp.stages:
            _, next_stage = mylp.stages.pop(0)
            print(next_stage)
            candidates = mylp.get_candidates_for_stage(next_stage)
            if candidates:
                my_event = random.choice(candidates)
                my_event.apply(mylp)

        return mylp

    def apply(self, pc: gears.base.Character):
        pc.personality.update( self.bio_personality)
        pc.badges += self.bio_badges
        for k,v in list(self.bio_bonuses.items()):
            if pc.statline.get(k,0) < 1 and k in gears.stats.NONCOMBAT_SKILLS:
                pc.statline[k] += 3
            pc.statline[k] += v
        if self.mutation:
            self.mutation.apply(pc, False)
        pc.bio = self.bio_text


def init_lifepath():
    protoevents = list()
    myfiles = glob.glob(pbge.util.data_dir( "lifepath_*.json"))
    for f in myfiles:
        with open(f, 'rt') as fp:
            mylist = json.load(fp)
            if mylist:
                protoevents += mylist
    for j in protoevents:
        _=LifePathEvent(**j)
