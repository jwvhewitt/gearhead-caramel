from pbge import Singleton
import geffects
import pbge

class Accurate(Singleton):
    # This weapon has an Aim action that gives +20 accuracy for 4MP.
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        aa = weapon.get_basic_attack(name='Aim (+20 acc, 4MP)',attack_icon=12)
        aa.fx.modifiers.append(geffects.GenericBonus('Aim',20))
        aa.price.append(geffects.MentalPrice(4))
        return [aa]

class Automatic(Singleton):
    # This weapon has two extra modes: x5 ammo for 2 shots, or x10 ammo for 3 shots

    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return [weapon.get_basic_attack(name='2 shots, x5 ammo',targets=2,ammo_cost=5,attack_icon=3),
                weapon.get_basic_attack(name='3 shots, x10 ammo',targets=3,ammo_cost=10,attack_icon=6)]

class Blast1(Singleton):
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 2.0
    BLAST_RADIUS = 1

    @classmethod
    def modify_basic_attack( self, weapon, attack ):
        # Change the area to blast.
        if hasattr(attack.area,"reach"):
            reach = attack.area.reach
        else:
            reach = weapon.reach
        attack.area = pbge.scenes.targetarea.Blast(radius=self.BLAST_RADIUS,reach=reach,delay_from=1)
        attack.fx.anim = geffects.BigBoom
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()

class Blast2(Blast1):
    MASS_MODIFIER = 3.0
    VOLUME_MODIFIER = 3.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 3.0
    BLAST_RADIUS = 2

class BurstFire2(Singleton):
    # Default fire action fires multiple bullets.
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0
    BURST_VALUE = 2

    @classmethod
    def replace_primary_attack( self, weapon ):
        base = weapon.get_basic_attack(name='Burst x{}'.format(self.BURST_VALUE),ammo_cost=self.BURST_VALUE,attack_icon=9)
        old_fx = base.fx
        base.shot_anim = geffects.BulletFactory(self.BURST_VALUE,base.shot_anim)
        base.fx = geffects.MultiAttackRoll(
            att_stat = old_fx.att_stat,
            att_skill = old_fx.att_skill,
            num_attacks = self.BURST_VALUE,
            children = old_fx.children,
            anim = old_fx.anim,
            accuracy = old_fx.accuracy,
            penetration = old_fx.penetration,
            modifiers = old_fx.modifiers,
            defenses = old_fx.defenses,
        )
        return [base,]

class BurstFire3(BurstFire2):
    # Default fire action fires multiple bullets.
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 3

class BurstFire4(BurstFire2):
    # Default fire action fires multiple bullets.
    MASS_MODIFIER = 1.4
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    BURST_VALUE = 4

class BurstFire5(BurstFire2):
    # Default fire action fires multiple bullets.
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 5

class VariableFire3(Singleton):
    # This weapon can do Burst x3 fire in addition to single fire
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire3.replace_primary_attack(weapon)

