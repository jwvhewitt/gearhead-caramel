from pbge import Singleton
import geffects
import pbge
import random
import materials
import aitargeters


#  ***************
#  ***  STATS  ***
#  ***************

class Stat( Singleton ):
    @classmethod
    def __str__(self):
        return self.name


class Reflexes( Stat ):
    name = 'Reflexes'


class Body( Stat ):
    name = 'Body'


class Speed( Stat ):
    name = 'Speed'


class Perception( Stat ):
    name = 'Perception'
    @classmethod
    def add_invocations(self,pc,invodict):
        pc_skill = pc.get_skill_score(self,Scouting)
        ba = pbge.effects.Invocation(
            name = 'Search',
            fx= geffects.CheckConditions([aitargeters.TargetIsEnemy(),aitargeters.TargetIsHidden()],
                anim=geffects.SearchAnim, on_success=[
                    geffects.OpposedSkillRoll(Perception,Scouting,Speed,Stealth,
                    roll_mod=25, min_chance=25,
                    on_success=[geffects.SetVisible(anim=geffects.SmokePoof,)],
                ),]),
            area=pbge.scenes.targetarea.SelfCentered(radius=10,delay_from=-1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsHidden()]),
            shot_anim=geffects.OriginSpotShotFactory(geffects.SearchTextAnim),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),6),
            price=[],
            targets=1)
        invodict[Scouting].append(ba)


class Craft( Stat ):
    name = 'Craft'


class Ego( Stat ):
    name = 'Ego'


class Knowledge( Stat ):
    name = 'Knowledge'


class Charm( Stat ):
    name = 'Charm'


PRIMARY_STATS = (Reflexes,Body,Speed,Perception,Craft,Ego,Knowledge,Charm)

#  ****************
#  ***  SKILLS  ***
#  ****************

class Skill( Singleton ):
    name = ''
    desc = ''

    SKILL_COST = (100,100,200,300,400,
		500,800,1300,2100,3400,
		5500,8900,14400,23300,37700)
    @classmethod
    def improvement_cost(cls,pc,current_value):
        return cls.SKILL_COST[min(max(current_value,0),14)]

class MechaGunnery( Skill ):
    name = 'Mecha Gunnery'
    desc = "Used when attacking with mecha scale ranged weapons such as guns, missile launchers, and flamethrowers."


class MechaFighting( Skill ):
    name = 'Mecha Fighting'
    desc = "Used when attacking with mecha scale close combat weapons and also when making unarmed attacks in a mecha."


class MechaPiloting( Skill ):
    name = 'Mecha Piloting'
    desc = "Determines your ability to evade attacks when piloting a mecha."


class RangedCombat( Skill ):
    name = 'Ranged Combat'
    desc = "Used when attacking with personal ranged weapons such as guns, missile launchers, and flamethrowers."


class CloseCombat( Skill ):
    name = 'Close Combat'
    desc = "Used when attacking with personal close combat weapons and also when making unarmed attacks."


class Dodge( Skill ):
    name = 'Dodge'
    desc = "Determines your ability to evade attacks in personal combat."


class Repair( Skill ):
    name = 'Repair'
    desc = "This skill allows you to repair damage to mecha and equipment. Use of this skill costs MP."
    @classmethod
    def get_invocations(self,pc,invodict):
        pc_skill = pc.get_skill_score(Craft,self)
        n,extra = divmod(pc_skill,6)
        if random.randint(1,6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name = 'Repair (5MP)', 
            fx=geffects.DoHealing(
                max(n,1),6,repair_type=materials.RT_REPAIR,
                anim = geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_REPAIR)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)


class Medicine( Skill ):
    name = 'Medicine'
    desc = "This skill allows you to heal wounded lancemates. Use of this skill costs MP."
    @classmethod
    def add_invocations(self,pc,invodict):
        pc_skill = pc.get_skill_score(Craft,self)
        n,extra = divmod(pc_skill,6)
        if random.randint(1,6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name = 'Heal (5MP)', 
            fx=geffects.DoHealing(
                max(n,1),6,repair_type=materials.RT_MEDICINE,
                anim = geffects.MedicineAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_MEDICINE)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)


class Biotechnology( Skill ):
    name = 'Biotechnology'
    desc = "This skill allows you to repair biotechnological constructs. Use of this skill requires MP."
    @classmethod
    def add_invocations(self,pc,invodict):
        pc_skill = pc.get_skill_score(Craft,self)
        n,extra = divmod(pc_skill,6)
        if random.randint(1,6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name = 'Repair (5MP)', 
            fx=geffects.DoHealing(
                max(n,1),6,repair_type=materials.RT_BIOTECHNOLOGY,
                anim = geffects.BiotechnologyAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_BIOTECHNOLOGY)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)


class Stealth( Skill ):
    name = 'Stealth'
    desc = "This skill allows you to hide during combat. Stealth attacks get bonuses."
    @classmethod
    def add_invocations(self,pc,invodict):
        ba = pbge.effects.Invocation(
            name = 'Hide', 
            fx=geffects.StealthSkillRoll(
                on_success=[geffects.SetHidden(anim=geffects.SmokePoof),],
                on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SelfOnly(),
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsAlly(),aitargeters.TargetIsNotHidden()]),
            used_in_combat = True, used_in_exploration=True,
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),3),
            price=[geffects.MentalPrice(5),],
            targets=1)
        invodict[self].append(ba)


class Science( Skill ):
    name = 'Science'
    desc = "This skill allows you to craft advanced equipment."


class Computers( Skill ):
    name = 'Computers'
    desc = "This skill allows you to hack computers and use electronic warfare systems."


class Performance( Skill ):
    name = 'Performance'
    desc = "This skill enables you to play music. Do it well enough and you might even get paid."


class Negotiation( Skill ):
    name = 'Negotiation'
    desc = "This skill is used to verbally influence other characters."


class Scouting( Skill ):
    name = 'Scouting'
    desc = "This skill is used to spot hidden things, and may be used to identify an enemy's weak points."
    @classmethod
    def add_invocations(self,pc,invodict):
        ba = pbge.effects.Invocation(
            name = 'Spot Weakness',
            fx= geffects.OpposedSkillRoll(Craft,self,Ego,Vitality,
                    roll_mod=50, min_chance=10,
                    on_success=[geffects.AddEnchantment(geffects.WeakPoint,anim=geffects.SearchAnim,)],
                    on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.WeakPoint)]),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),9),
            price=[geffects.MentalPrice(2),],
            targets=1)
        invodict[Scouting].append(ba)


class DominateAnimal( Skill ):
    name = 'Dominate Animal'
    desc = "This skill is used to train animals."


class Vitality( Skill ):
    name = 'Vitality'
    desc = "This skill determines your health point total."


class Athletics( Skill ):
    name = 'Athletics'
    desc = "This skill determines your stamina point total."


class Concentration( Skill ):
    name = 'Concentration'
    desc = "This skill determines your mental point total."


COMBATANT_SKILLS = (MechaFighting,MechaGunnery,MechaPiloting,RangedCombat,CloseCombat,Dodge,Vitality,Athletics,Concentration)
NONCOMBAT_SKILLS = (Repair,Medicine,Biotechnology,Stealth,Science,Computers,Performance,Negotiation,Scouting,DominateAnimal)









