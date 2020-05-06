from . import tags
from . import base
import random
import copy
from . import personality
from . import stats
from . import portraits
from . import genderobj
from . import color
from . import jobs
from . import cyberinstaller
import math

DESIGN_LIST = list()
STC_LIST = list()

DESIGN_BY_NAME = dict()
EARTH_NAMES = None
LUNA_NAMES = None
ORBITAL_NAMES = None
MARS_NAMES = None
GENERIC_NAMES = None
DEADZONE_TOWN_NAMES = None


def calc_threat_points(level, percent=30):
    # Copied from GH2.
    level = min(max(level, 0), 300)
    if level < 31:
        it = level * 10000 // 30
    else:
        it = 20 * level * level - 900 * level + 19040
    return it * percent


def check_design_list(echo_on=False):
    for mek in list(DESIGN_LIST):
        if isinstance(mek, base.Mecha):
            if not mek.check_design():
                if echo_on:
                    print("Warning: {} {} design is broken".format(mek.desig, mek))
                DESIGN_LIST.remove(mek)
            elif echo_on:
                print("{} {}: ${:,}".format(mek.desig, mek, mek.cost))

def random_name(npc):
    candidates = list()
    if personality.GreenZone in npc.personality or personality.DeadZone in npc.personality:
        candidates.append(EARTH_NAMES)
    if personality.L5Spinners in npc.personality or personality.L5DustyRing in npc.personality:
        candidates.append(ORBITAL_NAMES)
    if personality.Mars in npc.personality:
        candidates.append(MARS_NAMES)
    if personality.Luna in npc.personality:
        candidates.append(LUNA_NAMES)
    if random.randint(1,10) == 7 or not candidates:
        candidates.append(GENERIC_NAMES)
    ngen = random.choice(candidates)
    return ngen.gen_word()


def random_personality(preselected=()):
    tset = set(preselected)
    traits = list(personality.TRAITS)
    random.shuffle(traits)
    for t in range(min(random.randint(1, 3), random.randint(1, 3))):
        tset.add(random.choice(traits[t]))
    if random.randint(1, 4) != 1:
        tset.add(random.choice(personality.VIRTUES))
    return tset

def random_age():
    age = random.randint(21,30)
    if random.randint(1,4) == 1:
        age += random.randint(1,20)
    elif random.randint(1,4) == 2:
        age -= random.randint(1,6)
    if random.randint(1,20) == 17:
        age += random.randint(1,30)
    return age

def random_install_cyberware(pc, rank):
    # 0 or negative rank gets no cyberware.
    if rank <= 0:
        return
    # Get all cyberware.
    cybersource = cyberinstaller.AllCyberwareSource()

    cyberwares = cybersource.get_cyberware_list()
    # Remove cw that cannot be installed anyway.
    remaining_trauma = pc.max_trauma - pc.current_trauma
    cyberwares = [cw for cw in cyberwares if cw.trauma <= remaining_trauma]
    # If no more candidates, just quit.
    if len(cyberwares) == 0:
        return
    # Sort according to cost.
    cyberwares.sort(key = lambda cw: cw.cost)
    # If rank < 100, treat as percentage.
    # Only the cheapest will get in.
    if rank < 100:
        truncate_to = math.ceil(len(cyberwares) * rank / 100.0)
        cyberwares = cyberwares[:truncate_to]

    # Set up the installer.
    class FakeCamp(object):
        def __init__(self):
            self.credits = 99999999999
    def fake_alert(text):
        pass
    def fake_choose(items):
        # The last choice is always cancel, don't select that.
        return random.randint(0, len(items) - 2)
    installer = cyberinstaller.CyberwareInstaller(pc, cybersource, FakeCamp(), fake_alert, fake_choose)

    # And install.
    installer.install(random.choice(cyberwares))

def _try_cyberize(pc, rank):
    if random.randint(1,6) != 1:
        return
    for i in range(1 + pc.get_stat(stats.Cybertech)):
        random_install_cyberware(pc, rank)

def random_pilot(rank=25, current_year=158, can_cyberize = None, **kwargs):
    # Build the creation matrix, aka the dict.
    creation_matrix = dict(statline=base.Being.random_stats(points=max(rank+50,80)),portrait_gen=portraits.Portrait(),
                           combatant=True, renown=rank,
                        personality=random_personality(), gender=genderobj.Gender.random_gender(),
                        birth_year=current_year - random_age(),
                           job=jobs.ALL_JOBS["Mecha Pilot"])
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
    if "name" not in creation_matrix:
        pc.name = random_name(pc)
    if can_cyberize is None:
        can_cyberize = "name" not in creation_matrix
    if can_cyberize:
        _try_cyberize(pc, rank)
    #creation_matrix["job"].scale_skills(pc,rank)
    return pc

def random_character(rank=25, needed_tags=(), local_tags=(), current_year=158, can_cyberize = None, **kwargs):
    # Build the creation matrix, aka the dict.
    possible_origins = [o for o in local_tags if o in personality.ORIGINS]
    job = jobs.choose_random_job(needed_tags,local_tags)
    meanstatpts = max(rank+50,80)
    combatant = random.choice([True,False,False,False,False,False]) or job.always_combatant
    creation_matrix = dict(statline=base.Being.random_stats(points=random.randint(meanstatpts-15,meanstatpts+15)),
                           portrait_gen=portraits.Portrait(), job=job, combatant=combatant,
                           personality=random_personality(possible_origins), gender=genderobj.Gender.random_gender(),
                           birth_year=current_year - random_age(),renown=rank)
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
    if "name" not in creation_matrix:
        pc.name = random_name(pc)
    if can_cyberize is None:
        can_cyberize = "name" not in creation_matrix
    if can_cyberize:
        _try_cyberize(pc, rank)
    return pc


class MechaShoppingList(object):
    """Examine the DESIGN_LIST, locate mecha that fit the criteria given."""

    def __init__(self, hi_price, fac=None, env=tags.GroundEnv):
        self.hi_price = hi_price
        if hasattr(fac,"parent_faction"):
            fac = fac.parent_faction
        self.fac = fac
        self.env = env
        self.best_choices = list()
        self.backup_choices = list()
        self._go_shopping()

    def matches_criteria(self, mek):
        return ((self.fac in mek.faction_list) or (None in mek.faction_list)) and self.env in mek.environment_list

    def _go_shopping(self):
        # Why is this a separate method instaed of just part of init?
        # I dunno. Might be useful later. Might be useful never.
        # But writing this comment about it? Pure procrastination.
        for mek in DESIGN_LIST:
            if isinstance(mek, base.Mecha) and mek.check_design() and self.matches_criteria(mek):
                if mek.cost < self.hi_price:
                    if mek.cost > self.hi_price // 2:
                        self.best_choices.append(mek)
                    else:
                        self.backup_choices.append(mek)

    def get_best_mecha(self):
        if self.best_choices:
            protomek = max([random.choice(self.best_choices) for t in range(5)], key=lambda m: m.cost)
        else:
            protomek = random.choice(self.backup_choices)
        return copy.deepcopy(protomek)

    @classmethod
    def generate_single_mecha(cls,level,fac,env):
        shopping_list = cls(
            max(calc_threat_points(level + 20), 350000),
            fac, env)
        mek = shopping_list.get_best_mecha()
        if fac:
            mek.colors = fac.mecha_colors
        else:
            mek.colors = color.random_mecha_colors()
        return mek


class RandomMechaUnit(object):
    MIN_HI_PRICE = 250000

    def __init__(self, level, strength, fac, env, add_commander=False):
        # level refers to the renown rating of this encounter. It
        #   determines the skill level of pilots and the types of
        #   mecha you will face.
        # strength refers to the size of this encounter. It determines
        #   the number of mecha you will face.
        self.level = max(level,1)
        self.strength = strength
        self.fac = fac
        if fac:
            self.team_colors = fac.mecha_colors
        else:
            self.team_colors = color.random_mecha_colors()
        self.shopping_list = MechaShoppingList(
            max(calc_threat_points(level), self.MIN_HI_PRICE),
            fac, env)
        self.points = max(calc_threat_points(level, strength),10)
        self.mecha_list = list()
        if self.shopping_list.best_choices or self.shopping_list.backup_choices:
            self.buy_mecha()
            if add_commander:
                mek = self.choose_mecha()
                self.commander = self.generate_pilot(level,tag=tags.Commander)
                mek.load_pilot(self.commander)
                self.mecha_list.append(mek)

        else:
            print("No mecha to buy for {} {} {}".format(level, fac, env))

    def generate_pilot(self,pilot_level,tag=tags.Trooper):
        if self.fac:
            job = self.fac.choose_job(tag)
            origin = self.fac.choose_location()
            if origin:
                personality = random_personality([origin,])
            else:
                personality = random_personality()
        else:
            job = jobs.ALL_JOBS["Mecha Pilot"]
            personality = random_personality()
        return random_pilot( pilot_level,faction=self.fac,job=job,personality=personality)

    def prep_mecha(self, protomek):
        mek = copy.deepcopy(protomek)
        mek.colors = self.team_colors
        return mek

    def choose_mecha(self):
        if self.shopping_list.best_choices:
            mek = self.prep_mecha(random.choice(self.shopping_list.best_choices))
            if mek.cost > self.points and self.shopping_list.backup_choices:
                mek = self.prep_mecha(random.choice(self.shopping_list.backup_choices))
        else:
            mek = self.prep_mecha(random.choice(self.shopping_list.backup_choices))
        return mek

    def buy_mecha(self):
        ideal_cost = calc_threat_points(self.level, 20)
        quit_at = min(m.cost for m in (self.shopping_list.best_choices + self.shopping_list.backup_choices))
        if quit_at >= self.points:
            quit_at = 0
        while self.points > quit_at:
            mek = self.choose_mecha()
            pilot_level = self.level - 20
            if mek.cost > self.points:
                pilot_level -= 10
            elif mek.cost < ideal_cost // 2:
                pilot_level += 10
                self.points -= mek.cost // 2
            self.points -= mek.cost
            pilot = self.generate_pilot(pilot_level)
            mek.load_pilot(pilot)
            self.mecha_list.append(mek)

def generate_ace(level,fac,env):
    mek = MechaShoppingList.generate_single_mecha(level,fac,env)
    ace = random_pilot(level + 10)
    mek.load_pilot(ace)
    return mek

def generate_fortification(level,fac,env):
    # TODO: Add different buildings for different levels + environments
    return get_design_by_full_name("Bunker")

def get_design_by_full_name(name):
    if name in DESIGN_BY_NAME:
        return copy.deepcopy(DESIGN_BY_NAME[name])
    else:
        print("Error: design {} not found".format(name))

# print calc_threat_points(10)
# print calc_threat_points(20)
# print calc_threat_points(30)
# print calc_threat_points(40)
# print calc_threat_points(50)
# print calc_threat_points(60)
# print calc_threat_points(70)
# print calc_threat_points(80)
# print calc_threat_points(90)
# print calc_threat_points(100)
