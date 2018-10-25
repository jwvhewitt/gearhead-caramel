from pbge import Singleton
import color
import jobs
import tags
import random

FR_ENEMY = "ENEMY"

class Faction(Singleton):
    name = "Faction"
    mecha_colors = (color.AceScarlet, color.CometRed, color.HotPink, color.Black, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    @classmethod
    def get_faction_tag(cls):
        return cls
    @classmethod
    def is_enemy(cls,other_fac):
        return False
    @classmethod
    def choose_job(cls,role):
        candidates = cls.CAREERS.get(role)
        if candidates:
            print "Selecting..."
            job = jobs.ALL_JOBS[random.choice(candidates)]
        else:
            job = jobs.ALL_JOBS["Mecha Pilot"]
        return job

class AegisOverlord(Faction):
    name = "Aegis Overlord Luna"
    mecha_colors = (color.LunarGrey, color.AegisCrimson, color.LemonYellow, color.CeramicColor, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    @classmethod
    def is_enemy(cls,other_fac):
        return other_fac in (BladesOfCrihna,TerranDefenseForce)


class BladesOfCrihna(Faction):
    name = "the Blades of Crihna"
    mecha_colors = (color.HeavyPurple, color.SeaGreen, color.PirateSunrise, color.Black, color.StarViolet)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }


class BoneDevils(Faction):
    name = "the Bone Devil Gang"
    mecha_colors = (color.Black, color.Cream, color.BrightRed, color.Avocado, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    @classmethod
    def is_enemy(cls,other_fac):
        return other_fac in (TerranDefenseForce,)


class TerranDefenseForce(Faction):
    name = "the Terran Defense Force"
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    @classmethod
    def is_enemy(cls,other_fac):
        return other_fac in (BoneDevils,)


class Circle(object):
    def __init__(self, parent_faction=None, mecha_colors=None, name="", faction_reactions=None, careers=None):
        self.name = name
        self.parent_faction = parent_faction
        if parent_faction and not mecha_colors:
            mecha_colors = parent_faction.mecha_colors
        self.mecha_colors = mecha_colors or color.random_mecha_colors()
        self.faction_reactions = dict()
        if faction_reactions:
            self.faction_reactions.update(faction_reactions)
        self.careers = dict()
        if careers:
            self.careers.update(careers)

    def get_faction_tag(self):
        if self.parent_faction:
            return self.parent_faction
        else:
            return self.name

    def is_enemy(self, other_fac):
        if self.faction_reactions.get(other_fac) == FR_ENEMY:
            return True
        elif self.parent_faction:
            return self.parent_faction.is_enemy(other_fac)

    def choose_job(self,role):
        candidates = self.careers.get(role)
        job = jobs.ALL_JOBS["Mecha Pilot"]
        if candidates:
            job = jobs.ALL_JOBS[random.choice(candidates)]
        elif self.parent_faction:
            job = self.parent_faction.choose_job(role)
        return job


    def __str__(self):
        return self.name
