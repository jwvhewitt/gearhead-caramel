from pbge import Singleton
from . import color
from . import jobs
from . import tags
import random
from . import personality

FR_ENEMY = "ENEMY"

class Faction(Singleton):
    name = "Faction"
    factags = ()
    mecha_colors = (color.AceScarlet, color.CometRed, color.HotPink, color.Black, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot","Field Medic"),
    }
    LOCATIONS = ()
    NAME_PATTERNS = ("the {number} {noun}","the {adjective} {noun}")
    NAME_PAT_WITH_CITY = ("the {number} {noun} of {city}",)
    ADJECTIVES = ("Whatever",)
    NOUNS = ("Circle",)
    uniform_colors = (None,None,None,None,None)

    @classmethod
    def get_faction_tag(cls):
        return cls

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
    ORDINALS = ("1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th","11th","12th","13th")

    @classmethod
    def get_circle_name(cls,city=None):
        sub_dic = {
            "number": random.choice(cls.ORDINALS),
            "adjective": random.choice(cls.ADJECTIVES),
            "noun": random.choice(cls.NOUNS)
        }
        candidates = list(cls.NAME_PATTERNS)
        if city:
            candidates += list(cls.NAME_PAT_WITH_CITY)
            sub_dic["city"] = str(city)
        return random.choice(candidates).format(**sub_dic)


class AegisOverlord(Faction):
    name = "Aegis Overlord Luna"
    factags = (tags.Politician, tags.Military)
    mecha_colors = (color.LunarGrey, color.AegisCrimson, color.LemonYellow, color.CeramicColor, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot","Field Medic"),
    }
    LOCATIONS = (personality.Luna,)
    ADJECTIVES = ("Expedition","Strike Force")
    NOUNS = ("Aegis","Lunar")
    uniform_colors = (color.LunarGrey,None,None,None,color.AegisCrimson)


class BladesOfCrihna(Faction):
    name = "the Blades of Crihna"
    factags = (tags.Criminal,)
    mecha_colors = (color.HeavyPurple, color.SeaGreen, color.PirateSunrise, color.Black, color.StarViolet)
    LOCATIONS = (personality.L5DustyRing,)
    CAREERS = {
        tags.Trooper: ("Pirate","Thief"),
        tags.Commander: ("Pirate Captain",),
        tags.Support: ("Mecha Pilot",),
    }
    ADJECTIVES = ("Pirate",)
    NOUNS = ("Blades","Fleet")
    uniform_colors = (color.HeavyPurple,None,None,None,color.SeaGreen)


class BoneDevils(Faction):
    name = "the Bone Devil Gang"
    factags = (tags.Criminal, tags.Military)
    mecha_colors = (color.Black, color.Cream, color.BrightRed, color.Avocado, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Bandit","Thief"),
        tags.Commander: ("Commander","Scavenger"),
        tags.Support: ("Mecha Pilot",),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Bone Devil",)
    NOUNS = ("Gang",)
    uniform_colors = (color.Black,None,None,color.BrightRed,color.Terracotta)

class TerranFederation(Faction):
    name = "the Terran Federation"
    factags = (tags.Politician,)
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Citizen"),
        tags.Commander: ("Bureaucrat", "Commander",),
        tags.Support: ("Explorer", "Firefighter", "Paramedic", "Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran",)
    NOUNS = ("Council",)
    uniform_colors = (color.Turquoise,None,None,None,None)


class TerranDefenseForce(Faction):
    name = "the Terran Defense Force"
    factags = (tags.Military,)
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot","Field Medic"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran",)
    NOUNS = ("Defense Team","Militia")
    uniform_colors = (color.GriffinGreen,None,None,None,color.Khaki)

class Guardians(Faction):
    name = "the Guardians"
    factags = (tags.Police,)
    mecha_colors = (color.ShiningWhite, color.PrussianBlue, color.BrightRed, color.WarmGrey, color.Black)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Police Officer"),
        tags.Commander: ("Detective",),
        tags.Support: ("Bounty Hunter",),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Investigation","Peacekeeping")
    NOUNS = ("Unit","Squad")
    uniform_colors = (color.Black,None,None,None,color.FreedomBlue)

class RegExCorporation(Faction):
    name = "RegEx Corporation"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.Turquoise,color.AeroBlue,color.OrangeRed,color.FieldGrey,color.ElectricYellow)
    CAREERS = {
        tags.Trooper: ("Test Pilot","Trucker","Factory Worker"),
        tags.Commander: ("Corporate Executive","Dispatcher"),
        tags.Support: ("Construction Worker","Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("RegEx","Corporate")
    NOUNS = ("Team","Division")
    uniform_colors = (color.Turquoise,None,None,None,color.ElectricYellow)


class BioCorp(Faction):
    name = "BioCorp"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.RoyalPink,color.Cream,color.BrightRed,color.GothSkin,color.DeepSeaBlue)
    CAREERS = {
        tags.Trooper: ("Arena Pilot","Test Pilot"),
        tags.Commander: ("Corporate Executive","Scientist"),
        tags.Support: ("Field Medic","Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("BioCorp","Research")
    NOUNS = ("Team","Division")
    uniform_colors = (color.Cream,None,None,None,color.RoyalPink)


class KettelIndustries(Faction):
    name = "Kettel Industries"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.KettelPurple,color.StarViolet,color.FlourescentGreen,color.Charcoal,color.SteelBlue)
    CAREERS = {
        tags.Trooper: ("Arena Pilot","Test Pilot","Trucker"),
        tags.Commander: ("Corporate Executive",),
        tags.Support: ("Recon Pilot","Construction Worker","Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("BioCorp","Research")
    NOUNS = ("Team","Division")
    uniform_colors = (color.KettelPurple,None,None,None,color.StarViolet)

class DeadzoneFederation(Faction):
    name = "the Deadzone Federation"
    factags = (tags.Politician,)
    mecha_colors = (color.DarkBrown, color.AeroBlue, color.GunRed, color.DeepSeaBlue, color.DesertYellow)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Mercenary"),
        tags.Commander: ("Commander","Aristo","Warlord"),
        tags.Support: ("Recon Pilot","Scavenger"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Deadzone","Wasteland","Frontier")
    NOUNS = ("Council",)
    uniform_colors = (color.DesertYellow,None,None,None,color.DarkBrown)

class ClanIronwind(Faction):
    name = "Clan Ironwind"
    factags = (tags.Politician,tags.Military)
    mecha_colors = (color.CometRed,color.DimGrey,color.GreenYellow,color.Black,color.BlackRose)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Mercenary","Bandit"),
        tags.Commander: ("Aristo","Warlord"),
        tags.Support: ("Recon Pilot","Scavenger"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Deadzone","Wasteland","Iron")
    NOUNS = ("Legion","Warriors","Warband")
    uniform_colors = (color.BlackRose,None,None,None,None)

class TheSilverKnights(Faction):
    name = "the Silver Knights"
    factags = (tags.Military,)
    mecha_colors = (color.SkyBlue, color.ShiningWhite, color.BrightRed, color.SlateGrey, color.AeroBlue)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Knight"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot","Field Medic"),
    }
    LOCATIONS = (personality.L5Spinners,)
    ADJECTIVES = ("Silver",)
    NOUNS = ("Knights","Order")
    uniform_colors = (color.AeroBlue,None,None,None,color.SkyBlue)


class TheSolarNavy(Faction):
    name = "the Solar Navy"
    factags = (tags.Military,)
    mecha_colors = (color.DeepSeaBlue, color.Jade, color.OrangeRed, color.GullGrey, color.GhostGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot","Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot","Field Medic"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran","Solar")
    NOUNS = ("Defense Fleet","Wing")
    uniform_colors = (color.SkyBlue,None,None,None,color.DeepSeaBlue)


class Circle(object):
    def __init__(self, camp, parent_faction=None, mecha_colors=None, name="", careers=None, factags=(), locations=(), uniform_colors=None, active=True, allies=(), enemies=()):
        if parent_faction and not name:
            name = parent_faction.get_circle_name()
        elif not name:
            name = Faction.get_circle_name()
        self.name = name
        self.parent_faction = parent_faction
        random_colors = color.random_mecha_colors()
        if parent_faction and not mecha_colors:
            mecha_colors = list(parent_faction.mecha_colors)
            for col_i in range(len(mecha_colors)):
                if random.randint(1,5) == 3:
                    mecha_colors[col_i] = color.choose_color_by_tags((mecha_colors[col_i].family,))
                elif random.randint(1,10) == 7:
                    mecha_colors[col_i] = random_colors[col_i]
        self.mecha_colors = mecha_colors or random_colors
        if parent_faction and not uniform_colors:
            uniform_colors = parent_faction.uniform_colors
        self.uniform_colors = uniform_colors or (None,None,None,None,None)
        self.careers = dict()
        if careers:
            self.careers.update(careers)
        self.factags = list(factags)
        if parent_faction and not factags:
            self.factags = list(parent_faction.factags)
        self.locations = list(locations)
        if self.parent_faction:
            self.locations += self.parent_faction.LOCATIONS
        self.active = active
        if camp and (allies or enemies):
            camp.faction_relations[self] = FactionRelations(allies=allies,enemies=enemies)

    def get_faction_tag(self):
        if self.parent_faction:
            return self.parent_faction
        else:
            return self

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

class FactionRelations(object):
    def __init__(self,allies=(),enemies=()):
        self.allies = list(allies)
        self.enemies = list(enemies)


DEFAULT_FACTION_DICT_NT158 = {
    AegisOverlord: FactionRelations(
        allies = (),
        enemies = (TerranFederation,BladesOfCrihna)
    ),
    BladesOfCrihna: FactionRelations(
        allies = (),
        enemies = (AegisOverlord,Guardians)
    ),
    BoneDevils: FactionRelations(
        allies = (),
        enemies = (TerranDefenseForce,Guardians)
    ),
    TerranFederation: FactionRelations(
        allies = (TerranDefenseForce,Guardians),
        enemies= (AegisOverlord,)
    ),
    TerranDefenseForce: FactionRelations(
        allies= (TerranFederation,TheSolarNavy),
        enemies= (AegisOverlord,BoneDevils,ClanIronwind)
    ),
    Guardians: FactionRelations(
        allies=(TerranFederation,DeadzoneFederation),
        enemies=(BoneDevils,BladesOfCrihna)
    ),
    DeadzoneFederation: FactionRelations(
        allies=(Guardians,),
        enemies=(BoneDevils,ClanIronwind),
    ),
    ClanIronwind: FactionRelations(
        allies=(),
        enemies=(TerranFederation,TerranDefenseForce,DeadzoneFederation)
    ),
    TheSilverKnights: FactionRelations(
        allies=(TheSolarNavy,),
        enemies=(AegisOverlord,BladesOfCrihna)
    ),
    TheSolarNavy: FactionRelations(
        allies=(TerranFederation,TerranDefenseForce,TheSilverKnights),
        enemies=(AegisOverlord,BladesOfCrihna)
    )

}

