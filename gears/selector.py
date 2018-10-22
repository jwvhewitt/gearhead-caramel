import tags
import base
import random
import copy
import personality
import stats
import portraits
import genderobj
import color

DESIGN_LIST = list()
EARTH_NAMES = None


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


def random_personality():
    tset = set()
    traits = list(personality.TRAITS)
    random.shuffle(traits)
    for t in range(min(random.randint(1, 3), random.randint(1, 3))):
        tset.add(random.choice(traits[t]))
    if random.randint(1, 4) != 1:
        tset.add(random.choice(personality.VIRTUES))
    return tset


def random_pilot(rank=25, **kwargs):
    skill_rank = max((rank + 20) // 10, 1)
    # Build the creation matrix, aka the dict.
    creation_matrix = dict(name=EARTH_NAMES.gen_word(),
                        statline={stats.Reflexes: 10, stats.Body: 10, stats.Speed: 10,
                                  stats.Perception: 10, stats.Knowledge: 10, stats.Craft: 10, stats.Ego: 10,
                                  stats.Charm: 10, stats.MechaPiloting: skill_rank, stats.MechaGunnery: skill_rank,
                                  stats.MechaFighting: skill_rank}, portrait_gen=portraits.Portrait(),
                        personality=random_personality(), gender=genderobj.Gender.random_gender())
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
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
                self.commander = random_pilot(level)
                mek.load_pilot(self.commander)
                self.mecha_list.append(mek)

        else:
            print "No mecha to buy for {} {} {}".format(level, fac, env)

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
            pilot = random_pilot(pilot_level)
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
