from pbge import Singleton
from . import geffects
import pbge

class Accurate(Singleton):
    # This weapon has an Aim action that gives +20 accuracy for 4MP.
    name = "Accurate"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        aa = weapon.get_basic_attack(name='Aim (+20 acc, 4MP)',attack_icon=12)
        aa.fx.modifiers.append(geffects.GenericBonus('Aim',20))
        aa.price.append(geffects.MentalPrice(4))
        aa.data.thrill_power += 1
        return [aa]

class Automatic(Singleton):
    # This weapon has two extra modes: x5 ammo for 2 shots, or x10 ammo for 3 shots
    name = "Automatic"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return [weapon.get_basic_attack(name='2 shots, x5 ammo',targets=2,ammo_cost=5,attack_icon=3),
                weapon.get_basic_attack(name='3 shots, x10 ammo',targets=3,ammo_cost=10,attack_icon=6)]

class Blast1(Singleton):
    name = "Blast 1"
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
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.children[0].scatter = True

class Blast2(Blast1):
    name = "Blast 2"
    MASS_MODIFIER = 3.0
    VOLUME_MODIFIER = 3.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 3.0
    BLAST_RADIUS = 2


class BurnAttack(Singleton):
    name = "Burn"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.5

    @classmethod
    def modify_basic_attack(self, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children.append(geffects.AddEnchantment(geffects.Burning,))


class BurstFire2(Singleton):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 2"
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
    name = "Burst Fire 3"
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 3


class BurstFire4(BurstFire2):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 4"
    MASS_MODIFIER = 1.4
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    BURST_VALUE = 4


class BurstFire5(BurstFire2):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 5"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 5


class ChargeAttack(Singleton):
    # This weapon has a charge attack
    name = "Charge Attack"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.5
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        aa = weapon.get_basic_attack(name='Charge',attack_icon=15)
        aa.fx.modifiers.append(geffects.GenericBonus('Charge',10))
        aa.fx.children[0].damage_d = 10
        aa.area = geffects.DashTarget(weapon.get_root())
        aa.data.thrill_power = int(aa.data.thrill_power * 1.5)
        aa.shot_anim = geffects.DashFactory(weapon.get_root())
        return [aa]

class ConeAttack(Singleton):
    name = "Cone Area"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 3.0

    @classmethod
    def modify_basic_attack( self, weapon, attack ):
        # Change the area to cone.
        attack.area = pbge.scenes.targetarea.Cone(reach=weapon.reach*2,delay_from=-1)
        attack.shot_anim = None
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.children[0].scatter = True
    @classmethod
    def get_reach_str(self,weapon):
        return '{}-{} cone'.format(weapon.reach,weapon.reach*2)


class Defender(Singleton):
    name = "Defender"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0
    PARRY_BONUS = 20

class Flail(Singleton):
    name = "Flail"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    NO_PARRY = True

    @classmethod
    def modify_basic_attack( self, weapon, attack ):
        # Flails cannot be blocked or parried.
        attack.fx.defenses[geffects.PARRY] = None
        attack.fx.defenses[geffects.BLOCK] = None

class Intercept(Singleton):
    name = "Intercept"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    CAN_INTERCEPT = True
    
class LineAttack(Singleton):
    name = "Line Area"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 2.0

    @classmethod
    def modify_basic_attack( self, weapon, attack ):
        # Change the area to cone.
        attack.area = pbge.scenes.targetarea.Line(reach=weapon.reach*3,delay_from=-1)
        attack.shot_anim = None
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.children[0].scatter = True


class Scatter(Singleton):
    name = "Scatter Shot"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    @classmethod
    def modify_basic_attack( self, weapon, attack ):
        # Change the damage type to scatter. That was easy.
        attack.fx.children[0].scatter = True
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()

class SwarmFire2(Singleton):
    # Default fire action fires at multiple targets.
    name = "Swarm Fire 2"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 2.5
    SWARM_VALUE = 2

    @classmethod
    def replace_primary_attack( self, weapon ):
        base = weapon.get_basic_attack(name='Swarm x{}'.format(self.SWARM_VALUE),ammo_cost=self.SWARM_VALUE,targets=self.SWARM_VALUE,attack_icon=9)
        return [base,]

class SwarmFire3(SwarmFire2):
    # Default fire action fires at multiple targets.
    name = "Swarm Fire 3"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 1.5
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 3.5
    SWARM_VALUE = 3


class VariableFire2(Singleton):
    # This weapon can do Burst x2 fire in addition to single fire
    name = "Variable Fire 2"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire2.replace_primary_attack(weapon)

class VariableFire3(Singleton):
    # This weapon can do Burst x3 fire in addition to single fire
    name = "Variable Fire 3"
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire3.replace_primary_attack(weapon)

class VariableFire4(Singleton):
    # This weapon can do Burst x4 fire in addition to single fire
    name = "Variable Fire 4"
    MASS_MODIFIER = 1.4
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire4.replace_primary_attack(weapon)

class VariableFire5(Singleton):
    # This weapon can do Burst x4 fire in addition to single fire
    name = "Variable Fire 5"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire5.replace_primary_attack(weapon)



