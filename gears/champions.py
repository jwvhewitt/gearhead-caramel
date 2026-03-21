import random
import math
import copy
import pbge
import gears
from . import attackattributes
from . import base
from . import materials, tags


class UpgradeTheme(pbge.Singleton):
    name = "Default Theme"
    ADJECTIVES = ("Great", "Ultimate", "Boosted", "Wonder", "Super", "Brave", "Custom", "Bespoke", "Special")
    NOUNS = ("Champion", "Mecha", "Contender", "Hero", "Machine", "Battler", "Striker", )
    WEAPON_DESIGNATIONS = ("Mk.2", "Mk.3", "Enhanced", "Mk.4", "Mk.5", "Strike")

    FAVORED_UPGRADES = (base.Engine, base.Armor, base.MovementSystem,)
    ATTACK_ATTRIBUTES = (
        attackattributes.Accurate, attackattributes.Agonize, attackattributes.Automatic, attackattributes.Blast1,
        attackattributes.Blast2, attackattributes.BonusStrike1, attackattributes.BonusStrike2, attackattributes.Brutal,
        attackattributes.BurnAttack, attackattributes.BurstFire2, attackattributes.BurstFire3, attackattributes.BurstFire4,
        attackattributes.BurstFire5, attackattributes.ChargeAttack, attackattributes.Defender, attackattributes.Designator,
        attackattributes.DisintegrateAttack, attackattributes.DrainsPower, attackattributes.FastAttack, 
        attackattributes.HaywireAttack, attackattributes.Intercept, attackattributes.OverloadAttack, attackattributes.Plasma,
        attackattributes.Smash, attackattributes.SwarmFire2, attackattributes.SwarmFire3, attackattributes.VariableFire2,
        attackattributes.VariableFire3, attackattributes.VariableFire4, attackattributes.VariableFire5
    )

    THEME_TAG = tags.ST_MECHA_WEAPON

    @staticmethod
    def change_is_okay(old_part, new_part):
        # old_part is a gear that is currently installed in the mecha
        # new_part is a gear that is going to replace it
        parent = old_part.parent
        if not parent:
            return True
        if old_part in parent.sub_com:
            if parent.can_install(new_part, False):
                delta_v = new_part.volume - old_part.volume
                return delta_v <= parent.free_volume
        else:
            return parent.can_equip(new_part, False)
    
    @staticmethod
    def upgrade_material(part):
        if part.material is materials.Metal:
            part.material = materials.Ceramic
            return True
        if part.material is materials.Ceramic:
            part.material = materials.Advanced
            return True
        return False

    @staticmethod
    def replace_part(old_part, new_part):
        slot = old_part.container
        if slot:
            slot.remove(old_part)
            slot.append(new_part)

    #   **************************************
    #   ***   WEAPON  UPGRADE  FUNCTIONS   ***
    #   **************************************

    @classmethod
    def random_weapon_designation(cls, weapon: base.Weapon):
        adjectives = list(cls.ADJECTIVES) * 2
        for aa in weapon.attributes:
            if hasattr(aa, "ADJECTIVES"):
                adjectives += list(aa.ADJECTIVES)
        if random.randint(1,3) == 2:
            return random.choice(adjectives)
        else:
            return "{} {}".format(random.choice(adjectives), random.choice(cls.WEAPON_DESIGNATIONS))

    @classmethod
    def random_missiles_name(cls, weapon: base.Weapon):
        adjectives = list(cls.ADJECTIVES) * 2
        for aa in weapon.attributes:
            if hasattr(aa, "ADJECTIVES"):
                adjectives += list(aa.ADJECTIVES)
        if weapon.penetration > weapon.accuracy:
            base_name = "Rockets"
        else:
            base_name = "Missiles"
        return "{} {}".format(random.choice(adjectives), base_name)

    @classmethod
    def get_legal_attack_attributes(cls, part):
        candidates = list()
        for aa in cls.ATTACK_ATTRIBUTES:
            if aa not in part.LEGAL_ATTRIBUTES:
                continue
            if aa in part.attributes:
                continue
            if hasattr(aa, "FAMILY") and aa.FAMILY and any([(getattr(wa, "FAMILY", None)==aa.FAMILY and wa.COST_MODIFIER >= aa.COST_MODIFIER) for wa in part.attributes]):
                continue
            candidates.append(aa)
        return candidates

    @staticmethod
    def gain_attack_attribute(weapon, nu_aa):
        if hasattr(nu_aa, "FAMILY") and nu_aa.FAMILY:
            for old_aa in list(weapon.attributes):
                if hasattr(old_aa, "FAMILY") and old_aa.FAMILY == nu_aa.FAMILY:
                    weapon.attributes.remove(old_aa)
        weapon.attributes.append(nu_aa)

    @classmethod
    def upgrade_ammo(cls, part):
        protoammo = copy.deepcopy(part)
        candidate_attributes = cls.get_legal_attack_attributes(protoammo)
        if candidate_attributes:
            cls.gain_attack_attribute(protoammo, random.choice(candidate_attributes))
            while not cls.change_is_okay(part, protoammo) and protoammo.quantity > 0:
                protoammo.quantity -= 1
            if protoammo.quantity > 0 and cls.change_is_okay(part, protoammo):
                if isinstance(protoammo, base.Missile):
                    protoammo.name = cls.random_missiles_name(protoammo)
                cls.replace_part(part, protoammo)
                return protoammo

    @classmethod
    def create_upgraded_weapon(cls, weapon):
        protoweapon = copy.deepcopy(weapon)
        candidate_attributes = cls.get_legal_attack_attributes(protoweapon)
        if candidate_attributes:
            cls.gain_attack_attribute(protoweapon, random.choice(candidate_attributes))
        if hasattr(protoweapon, "get_ammo") and (random.randint(1,3)==2 or not candidate_attributes):
            protoammo = protoweapon.get_ammo()
            if protoammo:
                cls.upgrade_ammo(protoammo)
        protoweapon.desig = cls.random_weapon_designation(protoweapon)
        return protoweapon

    MELEE_WEAPONS = (base.MeleeWeapon, base.EnergyWeapon)
    MISSILE_WEAPONS = (base.BallisticWeapon, base.BeamWeapon, base.ChemThrower, base.Launcher)

    @classmethod
    def get_new_weapon(cls, weapon):
        needed_class = (base.Weapon, base.Launcher)
        if weapon:
            old_cost = weapon.cost + min(random.randint(1,100000), random.randint(1,100000))
            if isinstance(weapon, cls.MELEE_WEAPONS):
                needed_class = cls.MELEE_WEAPONS
            elif isinstance(weapon, cls.MISSILE_WEAPONS):
                needed_class = cls.MISSILE_WEAPONS
        else:
            old_cost = random.randint(1,100000)
        candidate_weapon = None
        for w in gears.selector.DESIGN_LIST:
            if isinstance(w, needed_class) and cls.THEME_TAG in w.shop_tags:
                if w.cost > old_cost and (not candidate_weapon or w.cost < candidate_weapon.cost):
                    candidate_weapon = w
        return candidate_weapon

    @classmethod
    def upgrade_weapon(cls, weapon):
        # Attempt to upgrade the provided weapon. If an upgrade is possible, return new weapon.
        if random.randint(1,3) == 2:
            nu_weapon = cls.get_new_weapon(weapon)
            if nu_weapon and cls.change_is_okay(weapon, nu_weapon):
                cls.replace_part(weapon, nu_weapon)
                return nu_weapon
        nu_weapon = cls.create_upgraded_weapon(weapon)
        if nu_weapon and cls.change_is_okay(weapon, nu_weapon):
            cls.replace_part(weapon, nu_weapon)
            return nu_weapon

    #   ************************************
    #   ***   GEAR  UPGRADE  FUNCTIONS   ***
    #   ************************************

    @classmethod
    def upgrade_engine(cls, part):
        if random.randint(1,10) == 5 and cls.upgrade_material(part):
            return part
        elif part.__class__ is base.Engine and random.randint(1,5) == 3:
            if random.randint(1,3) != 2:
                nupart = base.HighPerformanceEngine(size=part.size, scale=part.scale, material=part.material)
            else:
                nupart = base.HighOutputEngine(size=part.size, scale=part.scale, material=part.material)
            cls.replace_part(part, nupart)
            return nupart
        new_size = min(part.size + random.randint(1,4) * 50, part.MAX_SIZE)
        nupart = part.__class__(size=new_size, scale=part.scale, material=part.material)
        if new_size > part.size and cls.change_is_okay(part, nupart):
            cls.replace_part(part, nupart)
            return nupart

    @classmethod
    def upgrade_armor(cls, part):
        if random.randint(1,3) != 2 and cls.upgrade_material(part):
            return part
        if part.size < part.MAX_SIZE:
            nupart = base.Armor(size=part.size + 1, scale=part.scale, material=part.material)
            if cls.change_is_okay(part, nupart):
                cls.replace_part(part, nupart)
                return nupart

    @classmethod
    def upgrade_movesys(cls, part):
        if random.randint(1,5) == 5 and cls.upgrade_material(part):
            return part
        elif isinstance(part, (base.HoverJets, base.FlightJets)) and random.randint(1,10) == 5:
            nupart = base.ArcJets(size=part.size, scale=part.scale, material=part.material)
            cls.replace_part(part, nupart)
            return nupart
        nupart = part.__class__(size=part.size + 1, scale=part.scale, material=part.material)
        if cls.change_is_okay(part, nupart):
            cls.replace_part(part, nupart)
            return nupart

    #   *********************************
    #   ***   TOP  LEVEL  FUNCTIONS   ***
    #   *********************************

    @classmethod
    def upgrade_mecha(cls, mecha: base.Mecha, points=5):
        mecha.desig = "{} {}".format(random.choice(cls.ADJECTIVES), random.choice(cls.NOUNS))

        candidates = list()
        empty_holders = list()
        for part in mecha.get_all_parts():
            if isinstance(part, (base.Weapon, base.Missile)) and not (hasattr(part, "integral") and part.integral):
                candidates.append(part)
            elif isinstance(part, cls.FAVORED_UPGRADES) and not part.integral:
                candidates.append(part)
            elif isinstance(part, (base.Hand, base.Mount)) and not part.inv_com:
                empty_holders.append(part)

        random.shuffle(candidates)
        while points > 0 and (candidates or empty_holders):
            if candidates:
                part = candidates.pop()

                if isinstance(part, base.Engine):
                    nupart = cls.upgrade_engine(part)
                    if nupart:
                        points -= 1
                        candidates.append(nupart)
                        random.shuffle(candidates)
                elif isinstance(part, base.Armor):
                    nupart = cls.upgrade_armor(part)
                    if nupart:
                        points -= 1
                        candidates.append(nupart)
                        random.shuffle(candidates)
                elif isinstance(part, base.MovementSystem):
                    nupart = cls.upgrade_movesys(part)
                    if nupart:
                        points -= 1
                        candidates.append(nupart)
                        random.shuffle(candidates)
                elif isinstance(part, base.Weapon):
                    nupart = cls.upgrade_weapon(part)
                    if nupart:
                        points -= 1
                        candidates.append(nupart)
                        random.shuffle(candidates)
                elif isinstance(part, base.Missile):
                    nupart = cls.upgrade_ammo(part)
                    if nupart:
                        points -= 1
                        candidates.append(nupart)
                        random.shuffle(candidates)

            if empty_holders and random.randint(1,23)==5 or not candidates:
                part = empty_holders.pop()
                nupart = cls.get_new_weapon(None)
                if nupart:
                    points -= 1
                    part.inv_com.append(nupart)
                    candidates.append(nupart)
                    random.shuffle(candidates)


class PyromaniacTheme(UpgradeTheme):
    name = "Pyromaniac"
    NOUNS = ("Pyromaniac", "Firestarter", "Volcano", "Salamander","Burninator")
    ADJECTIVES = ("Flash", "Fire", "Blazing", "Hot", "Burning")

    FAVORED_UPGRADES = (base.Engine, base.MovementSystem,)
    ATTACK_ATTRIBUTES = (
        attackattributes.Agonize, attackattributes.Blast1, attackattributes.Blast2, attackattributes.Brutal,
        attackattributes.BurnAttack, attackattributes.BurstFire2, attackattributes.BurstFire3, attackattributes.ChargeAttack, 
        attackattributes.Defender, attackattributes.DrainsPower, attackattributes.FastAttack, 
        attackattributes.Plasma, attackattributes.Smash, attackattributes.ConeAttack, attackattributes.LineAttack,
        attackattributes.Scatter
    )


THEMES = [ t for t in UpgradeTheme.__subclasses__() ]

###############################################################################


def upgrade_to_champion(mek, theme: None|type[UpgradeTheme] = None):
    if not theme:
        if random.randint(1,5) == 5:
            theme = random.choice(THEMES)
        else:
            theme = UpgradeTheme
    # First upgrade the engines.
    theme.upgrade_mecha(mek, 5)
