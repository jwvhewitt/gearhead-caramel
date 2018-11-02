from pbge import Singleton
import color
import jobs
import tags
import random
import personality

FR_ENEMY = "ENEMY"

class Faction(Singleton):
    name = "Faction"
    mecha_colors = (color.AceScarlet, color.CometRed, color.HotPink, color.Black, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    LOCATIONS = ()
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
            job = jobs.ALL_JOBS[random.choice(candidates)]
        else:
            job = jobs.ALL_JOBS["Mecha Pilot"]
        return job
    @classmethod
    def choose_location(cls):
        if cls.LOCATIONS:
            return random.choice(cls.LOCATIONS)


class AegisOverlord(Faction):
    name = "Aegis Overlord Luna"
    mecha_colors = (color.LunarGrey, color.AegisCrimson, color.LemonYellow, color.CeramicColor, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Mecha Pilot",),
    }
    LOCATIONS = (personality.Luna,)
    @classmethod
    def is_enemy(cls,other_fac):
        return other_fac in (BladesOfCrihna,TerranDefenseForce)


class BladesOfCrihna(Faction):
    name = "the Blades of Crihna"
    mecha_colors = (color.HeavyPurple, color.SeaGreen, color.PirateSunrise, color.Black, color.StarViolet)
    LOCATIONS = (personality.L5DustyRing,)
    CAREERS = {
        tags.Trooper: ("Pirate","Thief"),
        tags.Commander: ("Pirate Captain",),
        tags.Support: ("Mecha Pilot",),
    }


class BoneDevils(Faction):
    name = "the Bone Devil Gang"
    mecha_colors = (color.Black, color.Cream, color.BrightRed, color.Avocado, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Bandit","Thief"),
        tags.Commander: ("Commander","Scavenger"),
        tags.Support: ("Mecha Pilot",),
    }
    LOCATIONS = (personality.DeadZone,)
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
    LOCATIONS = (personality.GreenZone,)
    @classmethod
    def is_enemy(cls,other_fac):
        return other_fac in (BoneDevils,)


class Circle(object):
    def __init__(self, parent_faction=None, mecha_colors=None, name="Circle", faction_reactions=None, careers=None, locations=()):
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
        self.locations = list(locations)
        if self.parent_faction:
            self.locations += self.parent_faction.LOCATIONS

    def get_faction_tag(self):
        if self.parent_faction:
            return self.parent_faction
        else:
            return self

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

    def choose_location(self):
        if self.locations:
            return random.choice(self.locations)

    def __str__(self):
        return self.name
