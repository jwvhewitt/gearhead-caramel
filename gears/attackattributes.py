from pbge import Singleton
from . import geffects,stats
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
        aa = weapon.get_basic_attack(name='Aim +20',attack_icon=12)
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
    COST_MODIFIER = 2.2
    POWER_MODIFIER = 1.0

    # Treat weapons with this modifier as having at least reach 5.
    COST_EFFECTIVE_REACH_MIN = 5

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


class FastAttack(Singleton):
    # Extra fire action can hit twice.
    name = "Fast Attack"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 2.0
    BURST_VALUE = 2

    @classmethod
    def get_attacks( self, weapon ):
        aa = weapon.get_basic_attack(name='2 attacks', attack_icon=9)
        aa.price.append(geffects.MentalPrice(3))
        aa.data.thrill_power += 2
        old_fx = aa.fx
        aa.fx = geffects.MultiAttackRoll(
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
        return [aa]


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

class HaywireAttack(Singleton):
    name = "Haywire"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def modify_basic_attack(self, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.HaywireStatus,
                on_success=(
                    geffects.ResistanceRoll(stats.Knowledge,stats.Ego,roll_mod=25,min_chance=25,
                        on_success=(geffects.AddEnchantment(geffects.HaywireStatus,dur_n=2,dur_d=4,anim=geffects.InflictHaywireAnim),)
                    ),
                ),
            )
        )

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

class LinkedFire(Singleton):
    name = "Linked Fire"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        myroot = weapon.get_root()
        weapons = cls.get_all_weapons(myroot,weapon)
        invos = [wep.get_primary_attacks()[0] for wep in weapons]
        mylist = list()
        if invos and len(invos) > 1:
            myattack = weapon.get_primary_attacks()[0]
            myattack.targets = 0
            for i in invos:
                if i.can_be_invoked(myroot,True):
                    myattack.targets += 1
                    myattack.price += i.price
            if myattack.targets > 1:
                myattack.price.append(geffects.MentalPrice(myattack.targets+1))
                myattack.name = "Link {} shots".format(myattack.targets)
                myattack.data.active_frame = 18
                myattack.data.inactive_frame = 19
                myattack.data.disabled_frame = 20
                mylist.append(myattack)
        return mylist

    @classmethod
    def get_all_weapons(cls,myroot,weapon):
        mylist = list()
        for wep in myroot.ok_descendants(False):
            if cls.matches(weapon,wep):
                mylist.append(wep)
        return mylist
    @staticmethod
    def matches(wep1,wep2):
        return (
            wep1.__class__ is wep2.__class__ and wep1.scale is wep2.scale and wep1.damage == wep2.damage and
            wep1.reach == wep2.reach and wep1.accuracy == wep2.accuracy and wep1.penetration == wep2.penetration and
            set(wep1.attributes) == set(wep2.attributes)
        )

class OverloadAttack(Singleton):
    name = "Overload"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.5

    @classmethod
    def modify_basic_attack(self, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.OverloadStatus,
                on_success=(geffects.AddEnchantment(geffects.OverloadStatus,dur_n=2,dur_d=4,anim=geffects.OverloadAnim),),
            )
        )


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

class Smash(Scatter):
    # Exactly the same as Scatter, but better name for melee.
    name = "Smash"

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
    # This weapon can do Burst x5 fire in addition to single fire
    name = "Variable Fire 5"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks( self, weapon ):
        return BurstFire5.replace_primary_attack(weapon)



