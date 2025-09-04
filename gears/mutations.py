from . import stats, base, personality
from pbge import Singleton
from . import color
import random
from typing import Any


class FelineMutation(Singleton):
    name = "Feline Mutation"
    COLOR_CHANNELS = {1: color.HAIR}
    @staticmethod
    def get_stat_modifier() -> dict[Any, int]:
        return {stats.Speed: 2, stats.Body: -2}

    @staticmethod
    def apply_stat_modifier(pc, statmod: dict):
        for k,v in statmod.items():
            pc.statline[k] += v

    @classmethod
    def apply(cls, pc: base.Character, apply_stat_bonus=True):
        if apply_stat_bonus:
            cls.apply_stat_modifier(pc, cls.get_stat_modifier())
        if pc.portrait_gen:
            for k,v in cls.COLOR_CHANNELS.items():
                pc.portrait_gen.color_channels[k] = v


class DraconicMutation(FelineMutation):
    name = "Draconic Mutation"
    COLOR_CHANNELS = {1: color.MECHA, 2: color.METAL}
    @staticmethod
    def get_stat_modifier():
        return {stats.Body: 2, stats.Charm: -2}


class GeneralMutation(FelineMutation):
    name = "Mutation"
    COLOR_CHANNELS = {1: color.DETAILS, 2: color.DETAILS}
    @staticmethod
    def get_stat_modifier():
        s1,s2 = random.sample(stats.PRIMARY_STATS,2)
        return {s1:2, s2:-2}
            

# Mutations were originally located in the Personality module, so we're going
# to monkey patch references back there so as to not break savefile compatability.
personality.FelineMutation = FelineMutation
personality.DraconicMutation = DraconicMutation
personality.GeneralMutation = GeneralMutation

MUTATIONS = (FelineMutation,DraconicMutation,GeneralMutation)