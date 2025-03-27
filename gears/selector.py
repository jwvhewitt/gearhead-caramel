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
import math
import collections
import pbge

DESIGN_LIST = list()
STC_LIST = list()
MONSTER_LIST = list()

DESIGN_BY_NAME = dict()
MAJOR_NPCS = dict()

EARTH_NAMES: pbge.namegen.NameGen = None
DEADZONE_NAMES: pbge.namegen.NameGen = None
LUNA_NAMES: pbge.namegen.NameGen = None
ORBITAL_NAMES: pbge.namegen.NameGen = None
MARS_NAMES: pbge.namegen.NameGen = None
VENUS_NAMES: pbge.namegen.NameGen = None
GENERIC_NAMES: pbge.namegen.NameGen = None
DEADZONE_TOWN_NAMES: pbge.namegen.NameGen = None
GREENZONE_TOWN_NAMES: pbge.namegen.NameGen = None


def calc_threat_points(level, percent=50):
    # Copied from GH2.
    level = min(max(level, 0), 300)
    if level < 31:
        it = level * 10000 // 30
    else:
        it = 20 * level * level - 900 * level + 19040
    return it * percent


def calc_mission_reward(level, percent=100, round_it_off=False):
    reward = max(calc_threat_points(level, percent) // 5, 10000)
    if round_it_off:
        if reward > 100000:
            reward = (reward//10000) * 10000
        else:
            reward = (reward//1000) * 1000
    return reward


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
    if personality.GreenZone in npc.personality:
        candidates.append(EARTH_NAMES)
    if personality.DeadZone in npc.personality:
        candidates.append(DEADZONE_NAMES)
    if personality.L5Spinners in npc.personality or personality.L5DustyRing in npc.personality:
        candidates.append(ORBITAL_NAMES)
    if personality.Mars in npc.personality:
        candidates.append(MARS_NAMES)
    if personality.Luna in npc.personality:
        candidates.append(LUNA_NAMES)
    if personality.Venus in npc.personality:
        candidates.append(VENUS_NAMES)
    if random.randint(1, 10) == 7 or not candidates:
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
    age = random.randint(21, 30)
    if random.randint(1, 4) == 1:
        age += random.randint(1, 20)
    elif random.randint(1, 4) == 2:
        age -= random.randint(1, 6)
    if random.randint(1, 20) == 17:
        age += random.randint(1, 30)
    return age


def random_install_cyberware(pc, rank):
    # 0 or negative rank gets no cyberware.
    if rank <= 0:
        return
    # Get all cyberware.
    cyberwares = [cw for cw in DESIGN_LIST if isinstance(cw, base.BaseCyberware)]
    # Remove cw that cannot be installed anyway.
    remaining_trauma = pc.max_trauma - pc.current_trauma
    cyberwares = [cw for cw in cyberwares if cw.trauma <= remaining_trauma]
    # If no more candidates, just quit.
    if len(cyberwares) == 0:
        return
    # Sort according to cost.
    cyberwares.sort(key=lambda cw: cw.cost)
    # If rank < 100, treat as percentage.
    # Only the cheapest will get in.
    if rank < 80:
        truncate_to = max((len(cyberwares) * rank) // 80, 5)
        cyberwares = cyberwares[:truncate_to]

    cw = random.choice(cyberwares)

    candidates = list()
    for bodpart in pc.sub_com:
        if bodpart.can_install(cw):
            candidates.append(bodpart)

    if candidates:
        bodpart = random.choice(candidates)
        bodpart.sub_com.append(cw)


def _try_cyberize(pc, rank):
    if random.randint(1, 8) != 1 and stats.Cybertech not in pc.statline:
        return
    for i in range(random.randint(1,2) + pc.get_stat(stats.Cybertech)):
        random_install_cyberware(pc, rank)


def random_pilot(rank=25, current_year=158, can_cyberize=None, **kwargs):
    # Build the creation matrix, aka the dict.
    creation_matrix = dict(statline=base.Being.random_stats(points=max(rank + 50, 80)),
                           portrait_gen=portraits.Portrait(),
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
    # creation_matrix["job"].scale_skills(pc,rank)
    return pc


def get_equipment_that_fits(holder: base.BaseGear, type_tag, price_limit):
    candidates = list()
    for part in DESIGN_LIST:
        if type_tag in part.shop_tags and holder.can_equip(part, check_slots=False) and part.cost <= price_limit:
            candidates.append(part)
    if candidates:
        candidates.sort(key=lambda p: abs(p.cost - price_limit))
        n = min(len(candidates)-1, 5)
        myitem = copy.deepcopy(candidates[random.randint(0, n)])
        if not holder.can_equip(myitem):
            existing_items = [i for i in holder.inv_com if i.slot == myitem.slot]
            best_item = max(existing_items, key=lambda i: i.cost)
            if best_item.cost < myitem.cost:
                for ei in existing_items:
                    holder.inv_com.remove(ei)
            else:
                return
        holder.inv_com.append(myitem)


def equip_combatant(npc: base.Character):
    spending_limit = calc_threat_points(npc.renown, 15)
    if npc.get_stat(stats.CloseCombat) > npc.get_stat(stats.RangedCombat):
        weapon_types = [tags.ST_MELEEWEAPON, tags.ST_WEAPON]
    elif npc.get_stat(stats.CloseCombat) < npc.get_stat(stats.RangedCombat):
        weapon_types = [tags.ST_MISSILEWEAPON, tags.ST_WEAPON]
    else:
        weapon_types = [tags.ST_MELEEWEAPON, tags.ST_MISSILEWEAPON]
    for part in npc.sub_sub_coms():
        if isinstance(part, base.Module):
            # Try and add some armor.
            get_equipment_that_fits(part, tags.ST_CLOTHING, spending_limit // 2)
        elif isinstance(part, (base.Hand, base.Mount)) and weapon_types:
            get_equipment_that_fits(part, weapon_types.pop(random.randint(0, len(weapon_types) - 1)), spending_limit)


def get_random_loot(rank, amount, allowed_tags):
    myloot = list()
    allowed_tags = set(allowed_tags)
    mybudget = calc_threat_points(rank,amount)//2
    while mybudget > 0:
        hicost = int(mybudget * 1.2)
        candidates = [i for i in DESIGN_LIST if allowed_tags.intersection(i.shop_tags) and i.cost <= hicost]
        if candidates:
            candidates.sort(key=lambda i: i.cost)
            ind = max(random.randint(0,len(candidates)-1),random.randint(0,len(candidates)-1),random.randint(0,len(candidates)-1))
            myloot.append(copy.deepcopy(candidates[ind]))
            mybudget -= candidates[ind].cost
        else:
            break
    return myloot


def random_character(rank=25, needed_tags=(), local_tags=(), current_year=158, can_cyberize=None, camp=None, age=None, **kwargs):
    # Build the creation matrix, aka the dict.
    possible_origins = [o for o in local_tags if o in personality.ORIGINS]
    if "faction" in kwargs and kwargs["faction"] and "job" not in kwargs:
        job = kwargs["faction"].choose_job(random.choice((tags.Commander,tags.Support,tags.Support,tags.Trooper,tags.Trooper,tags.Trooper)))
    else:
        job = kwargs.pop("job",None) or jobs.choose_random_job(needed_tags, local_tags)
    if camp:
        current_year = camp.year
    if not age:
        age = random_age()
    meanstatpts = max(rank // 5 + 90, 90)
    combatant = random.choice([True, False, False, False, False, False]) or job.always_combatant
    creation_matrix = dict(statline=base.Being.random_stats(points=random.randint(meanstatpts - 5, meanstatpts + 5)),
                           portrait_gen=portraits.Portrait(), job=job, combatant=combatant,
                           personality=random_personality(possible_origins), gender=genderobj.Gender.random_gender(),
                           birth_year=current_year - age, renown=rank)
    # The always_combatant job property takes precedence over requesting "False" for combatant in kwargs.
    # If you want a soldier who isn't a combatant, you're going to have to set that manually after the character
    # is generated.
    if "combatant" in kwargs and job.always_combatant:
        kwargs["combatant"] = True
    if kwargs:
        creation_matrix.update(kwargs)
    pc = base.Character(**creation_matrix
                        )
    if "name" not in creation_matrix or not pc.name:
        pc.name = random_name(pc)
    if can_cyberize is None:
        can_cyberize = "name" not in creation_matrix
    if can_cyberize:
        _try_cyberize(pc, rank)
    if pc.combatant:
        equip_combatant(pc)
        if not pc.mecha_colors:
            if pc.faction:
                pc.mecha_colors = color.mutate_colors(pc.faction.mecha_colors)
            else:
                pc.mecha_colors = color.random_mecha_colors()
    return pc


class MechaShoppingList(object):
    """Examine the DESIGN_LIST, locate mecha that fit the criteria given."""

    def __init__(self, hi_price, fac=None, env=tags.GroundEnv):
        self.hi_price = hi_price
        if hasattr(fac, "parent_faction"):
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
                    if mek.cost > self.hi_price // 3:
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
    def generate_single_mecha(cls, level, fac, env=tags.GroundEnv):
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
    MIN_HI_PRICE = 300000

    def __init__(self, level, strength, fac, env, add_commander=False):
        # level refers to the renown rating of this encounter. It
        #   determines the skill level of pilots and the types of
        #   mecha you will face.
        # strength refers to the size of this encounter. It determines
        #   the number of mecha you will face.
        self.level = max(level, 1)
        self.strength = strength
        self.fac = fac
        if fac:
            self.team_colors = fac.mecha_colors
        else:
            self.team_colors = color.random_mecha_colors()
        self.shopping_list = MechaShoppingList(
            max(calc_threat_points(level), self.MIN_HI_PRICE),
            fac, env)
        self.ideal_cost = calc_threat_points(self.level, 20)
        self.points = strength
        self.mecha_list = list()
        if self.shopping_list.best_choices or self.shopping_list.backup_choices:
            self.buy_mecha()
            if add_commander:
                mek = self.choose_mecha()
                self.commander = self.generate_pilot(level, tag=tags.Commander)
                mek.load_pilot(self.commander)
                self.mecha_list.append(mek)

        else:
            print("No mecha to buy for {} {} {}".format(level, self.shopping_list.fac, env))

    def generate_pilot(self, pilot_level, tag=tags.Trooper):
        if self.fac:
            job = self.fac.choose_job(tag)
            origin = self.fac.choose_location()
            if origin:
                personality = random_personality([origin, ])
            else:
                personality = random_personality()
        else:
            job = jobs.ALL_JOBS["Mecha Pilot"]
            personality = random_personality()
        return random_pilot(pilot_level, faction=self.fac, job=job, personality=personality)

    def prep_mecha(self, protomek):
        mek = copy.deepcopy(protomek)
        mek.colors = self.team_colors
        return mek

    def mecha_strength_cost(self, mek):
        mycost = mek.cost
        return int(mycost * 15 / self.ideal_cost) + 10

    def choose_mecha(self):
        if self.shopping_list.best_choices:
            mek = self.prep_mecha(random.choice(self.shopping_list.best_choices))
            if self.mecha_strength_cost(mek) > self.points and self.shopping_list.backup_choices:
                mek = self.prep_mecha(random.choice(self.shopping_list.backup_choices))
        else:
            mek = self.prep_mecha(random.choice(self.shopping_list.backup_choices))
        return mek

    def buy_mecha(self):
        quit_at = 9
        if quit_at >= self.points:
            quit_at = 0
        while self.points > quit_at:
            mek = self.choose_mecha()
            pilot_level = self.level - 20
            mycost = self.mecha_strength_cost(mek)
            if mycost > self.points:
                pilot_level -= 10
            elif mycost < 20:
                pilot_level += 25 - mycost
            self.points -= mycost
            pilot = self.generate_pilot(pilot_level)
            mek.load_pilot(pilot)
            self.mecha_list.append(mek)


class RandomMonsterUnit(object):
    def __init__(self, level, strength, env, type_tags, scale):
        # level refers to the renown rating of this encounter.
        # strength refers to the size of this encounter. It determines
        #   the number of enemies you will face.
        self.level = min(max(level, 1), 100)
        self.strength = strength

        self.shopping_lists = collections.defaultdict(list)

        for mon in MONSTER_LIST:
            if mon.matches(level, env, type_tags, scale):
                self.shopping_lists["UNSORTED"].append(mon)
                for fam in mon.families:
                    self.shopping_lists[fam].append(mon)

        self.contents = list()
        if self.shopping_lists:
            mylist = random.choice(list(self.shopping_lists.values()))
        else:
            print("ERROR: No monsters found for {} {} {} {}".format(level, env, type_tags, scale))
            mylist = [mon for mon in MONSTER_LIST if mon.scale is scale and mon.type_tags]

        if random.randint(1,30) == 23:
            monster_limit = random.randint(3, 15)
        else:
            monster_limit = random.randint(9, 15)
        if mylist:
            while strength > 0 and len(self.contents) < monster_limit:
                numon = copy.deepcopy(self.select_monster_from_list(mylist))
                cost = self.monster_cost(numon)
                if random.randint(1, cost) <= strength or not self.contents:
                    self.contents.append(numon)
                strength -= cost

            if strength > 10:
                boss = random.choice(self.contents)
                boss.threat += strength//2
                if strength > 30:
                    boss.name = "{} the {}".format(GENERIC_NAMES.gen_word(), boss)
                boss.statline[stats.Vitality] += strength//10
                while strength > 0:
                    boss.statline[random.choice(stats.PRIMARY_STATS)] += 1
                    strength -= 5

    def select_monster_from_list(self, list):
        list.sort(key=lambda a: self.monster_cost(a))
        i = max(random.randint(0, len(list)-1), random.randint(0, len(list)-1))
        return list[i]

    def monster_cost(self, mon):
        delta = mon.threat - self.level
        if delta > 0:
            return 25 + delta * 3
        else:
            return max(delta + 25, 10)


def generate_boss_monster(level, env, type_tags, scale):
    shopping_list = list()
    for mon in MONSTER_LIST:
        if mon.matches(level, env, type_tags, scale):
            shopping_list.append(mon)
    if shopping_list:
        bossmon = copy.deepcopy(random.choice(shopping_list))
        upgrade = max(level - bossmon.threat + 10, 5)
        bossmon.statline[stats.Vitality] += upgrade
        bossmon.statline[stats.Athletics] += upgrade//4
        bossmon.statline[stats.Concentration] += upgrade//5
        for t in range(upgrade//4):
            bossmon.statline[random.choice((stats.CloseCombat, stats.RangedCombat, stats.Dodge))] += 1
        return bossmon


def generate_ace(level, fac, env):
    mek = MechaShoppingList.generate_single_mecha(level, fac, env)
    ace = random_pilot(level + 10)
    mek.load_pilot(ace)
    return mek


def generate_fortification(level, fac, env):
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
