import tags
import base
import random
import copy
import personality
import stats
import portraits
import genderobj
import color
import jobs

DESIGN_LIST = list()
EARTH_NAMES = None
LUNA_NAMES = None
ORBITAL_NAMES = None
MARS_NAMES = None
GENERIC_NAMES = None


def calc_threat_points(level, percent=30):
    # Copied from GH2.
    level = min(max(level, 0), 300)
    if level < 31:
        it = level * 10000 // 30
    else:
        it = 20 * level * level - 900 * level + 19040
    return it * percent


def check_design_list():
    for mek in DESIGN_LIST:
        if isinstance(mek, base.Mecha):
            if not mek.check_design():
                print "Warning: {} {} design is broken".format(mek.desig, mek)
            else:
                print "{} {}: ${}".format(mek.desig, mek, mek.cost)

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


def random_pilot(rank=25, current_year=158, **kwargs):
    # Build the creation matrix, aka the dict.
    age = random.randint(21,30)
    if random.randint(1,4) == 1:
        age += random.randint(1,20)
    elif random.randint(1,4) == 2:
        age -= random.randint(1,6)
    if random.randint(1,20) == 17:
        age += random.randint(1,30)
    creation_matrix = dict(statline={stats.Reflexes: 10, stats.Body: 10, stats.Speed: 10,
                                  stats.Perception: 10, stats.Knowledge: 10, stats.Craft: 10, stats.Ego: 10,
                                  stats.Charm: 10 }, portrait_gen=portraits.Portrait(),
                           combatant=True,
                        personality=random_personality(), gender=genderobj.Gender.random_gender(),
                        birth_year=current_year - age,
                           job=jobs.ALL_JOBS["Mecha Pilot"])
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
    if "name" not in creation_matrix:
        pc.name = random_name(pc)
    creation_matrix["job"].scale_skills(pc,rank)
    return pc

def random_character(rank=25, needed_tags=(), local_tags=(), **kwargs):
    # Build the creation matrix, aka the dict.
    possible_origins = [o for o in local_tags if o in personality.ORIGINS]
    job = jobs.choose_random_job(needed_tags,local_tags)
    creation_matrix = dict(statline={stats.Reflexes: 10, stats.Body: 10, stats.Speed: 10,
                                     stats.Perception: 10, stats.Knowledge: 10, stats.Craft: 10, stats.Ego: 10,
                                     stats.Charm: 10}, portrait_gen=portraits.Portrait(), job=job,
                           personality=random_personality(possible_origins), gender=genderobj.Gender.random_gender(),
                           birth_year=138 - random.randint(1, 10) + random.randint(1, 5))
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
    if "name" not in creation_matrix:
        pc.name = random_name(pc)
    job.scale_skills(pc, rank)
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


class RandomMechaUnit(object):
    MIN_HI_PRICE = 250000

    def __init__(self, level, strength, fac, env, add_commander=False):
        # level refers to the renown rating of this encounter. It
        #   determines the skill level of pilots and the types of
        #   mecha you will face.
        # strength refers to the size of this encounter. It determines
        #   the number of mecha you will face.
        self.level = level
        self.strength = strength
        self.fac = fac
        if fac:
            self.team_colors = fac.mecha_colors
        else:
            self.team_colors = color.random_mecha_colors()
        self.shopping_list = MechaShoppingList(
            max(calc_threat_points(level), self.MIN_HI_PRICE),
            fac, env)
        self.points = calc_threat_points(level, strength)
        self.mecha_list = list()
        if self.shopping_list.best_choices or self.shopping_list.backup_choices:
            self.buy_mecha()
            if add_commander:
                mek = self.choose_mecha()
                self.commander = self.generate_pilot(level,tag=tags.Commander)
                mek.load_pilot(self.commander)
                self.mecha_list.append(mek)

        else:
            print "No mecha to buy for {} {} {}".format(level, fac, env)

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
