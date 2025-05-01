from . import base, scale, stats, attackattributes, geffects, materials
import random

class MeleeWeaponClass:
    def __init__(self, name, min_damage=1, min_accuracy=1, min_penetration=1, reach=1, attack_stat=stats.Reflexes, attributes=(), shot_anim=None):
        self.name = name
        self.min_damage = min_damage
        self.min_accuracy = min_accuracy
        self.min_penetration = min_penetration
        self.reach = reach
        self.attack_stat=attack_stat
        self.attributes = list(attributes)
        self.shot_anim = shot_anim

    def generate_weapon(self, weapon_scale=scale.MechaScale):
        return base.MeleeWeapon(
            name=self.name, reach=self.reach, damage=self.min_damage, accuracy=self.min_accuracy,
            penetration=self.min_penetration, attack_stat=self.attack_stat, scale=weapon_scale,
            attributes=self.attributes, shot_anim=self.shot_anim or geffects.SlashShot
        )

    ENERGY_TYPES = (
        "Beam", "Energy", "Plasma", "Laser", "Heat", "Power"
    )

    def generate_energy_weapon(self, weapon_scale=scale.MechaScale):
        return base.EnergyWeapon(
            name="{} {}".format(random.choice(self.ENERGY_TYPES), self.name), reach=self.reach, damage=self.min_damage, accuracy=self.min_accuracy,
            penetration=self.min_penetration, attack_stat=self.attack_stat, scale=weapon_scale,
            attributes=self.attributes, shot_anim=self.shot_anim or geffects.BeamSlashShot
        )

MELEE_WEAPON_CLASSES = (
    MeleeWeaponClass("Sword", min_damage=2, min_accuracy=2, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Scimitar", min_damage=2, min_accuracy=2, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Katana", min_damage=2, min_accuracy=2, min_penetration=2),
    MeleeWeaponClass("Machete", min_accuracy=2, min_penetration=2),
    MeleeWeaponClass("Flamberge", min_damage=2, min_penetration=2, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Dagger", min_accuracy=2, attributes=(attackattributes.FastAttack,)),
    MeleeWeaponClass("Knife", min_accuracy=2, attack_stat=stats.Speed, attributes=(attackattributes.FastAttack,)),
    MeleeWeaponClass("Axe", min_damage=2, min_penetration=2,),
    MeleeWeaponClass("Hammer", attack_stat=stats.Body, attributes=(attackattributes.Smash,)),
    MeleeWeaponClass("Staff", attack_stat=stats.Body, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Rapier", min_accuracy=2, attack_stat=stats.Speed, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Mace", min_penetration=2, attributes=(attackattributes.Smash,)),
    MeleeWeaponClass("Morningstar", min_damage=2, attributes=(attackattributes.Brutal,)),
    MeleeWeaponClass("Flail", attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Lash", attack_stat=stats.Speed, attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Whip", reach=2, attack_stat=stats.Speed, attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Chain", min_damage=2, reach=2, attack_stat=stats.Speed, attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Spear", reach=2),
    MeleeWeaponClass("Lance", reach=2, attributes=(attackattributes.ChargeAttack,)),
    MeleeWeaponClass("Trident", min_penetration=2, reach=2, attributes=(attackattributes.ChargeAttack,)),
    MeleeWeaponClass("Scythe", min_damage=2, min_penetration=2, reach=2),
    MeleeWeaponClass("Halberd", reach=2, min_damage=2, min_accuracy=2),
    MeleeWeaponClass("Glaive", min_damage=2, reach=2,),
    MeleeWeaponClass("Ranseur", reach=2, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Naginata", min_damage=2, reach=2, attributes=(attackattributes.FastAttack,)),
    MeleeWeaponClass("Greathammer", min_damage=2, reach=2, attack_stat=stats.Body, attributes=(attackattributes.Smash,)),
    MeleeWeaponClass("Meteor Hammer", min_penetration=2, reach=3, attack_stat=stats.Speed, attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Boomerang", reach=3,),
    MeleeWeaponClass("Shuriken", min_accuracy=2, reach=3,),

)

MELEE_WEAPON_ATTRIBUTES = (
    attackattributes.Accurate, attackattributes.Agonize, attackattributes.BonusStrike1, attackattributes.BonusStrike2, 
    attackattributes.Brutal, attackattributes.BurnAttack, attackattributes.ChargeAttack,
    attackattributes.Defender, attackattributes.FastAttack, attackattributes.HaywireAttack,
    attackattributes.OverloadAttack, attackattributes.DrainsPower
)

class ArtifactBuilder:
    def __init__(self, rank, target_scale=scale.MechaScale):
        self.rank = rank + random.randint(1,10)
        if random.randint(1,5) == 3:
            self.rank += random.randint(-5, 10)

        self.item = None

        self.generate_melee_weapon(target_scale)

    def _improve_damage(self):
        self.item.damage += 1

    def _improve_accuracy(self):
        self.item.accuracy += 1

    def _improve_penetration(self):
        self.item.penetration += 1

    def _gain_melee_attribute(self):
        nu_aa = random.choice(self.get_possible_attack_attributes(MELEE_WEAPON_ATTRIBUTES))
        self.item.attributes.append(nu_aa)

    def get_possible_attack_attributes(self, full_list):
        return [aa for aa in full_list if aa in self.item.LEGAL_ATTRIBUTES and aa not in self.item.attributes]

    def generate_melee_weapon(self, weapon_scale=scale.MechaScale):
        myclass = random.choice(MELEE_WEAPON_CLASSES)
        if random.randint(1,3) == 2 or self.rank > random.randint(25,120):
            self.item = myclass.generate_energy_weapon(weapon_scale)
        else:
            self.item = myclass.generate_weapon(weapon_scale)
        if max(random.randint(20,200), random.randint(20,200)) <= self.rank:
            self.item.material = materials.Biotech
        elif random.randint(0,120) <= self.rank:
            self.item.material = materials.Advanced
        elif random.randint(0,75) <= min(self.rank, 74):
            self.item.material = materials.Ceramic

        while self.item.shop_rank() < max(self.rank, 25):
            candidates = list()
            if self.item.damage < self.item.MAX_DAMAGE:
                candidates += [self._improve_damage] * 4
            if self.item.accuracy < self.item.MAX_ACCURACY:
                candidates += [self._improve_accuracy] * 3
            if self.item.penetration < self.item.MAX_PENETRATION:
                candidates += [self._improve_penetration] * 3
            if self.get_possible_attack_attributes(MELEE_WEAPON_ATTRIBUTES) and len(self.item.attributes) < 3:
                candidates += [self._gain_melee_attribute] * (3 - len(self.item.attributes))

            if not candidates:
                break

            upgrade = random.choice(candidates)
            upgrade()

for t in range(100):
    test = ArtifactBuilder(100)
    print("{}: {}".format(test.item.get_full_name(), str(test.item.material)))
    print(test.item.get_text_desc())
    print()

