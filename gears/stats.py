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
            fx= geffects.OpposedSkillRoll(Perception,Scouting,Speed,Stealth,
                anim=geffects.SearchAnim, roll_mod=25, min_chance=25,
                on_success=[geffects.SetVisible(anim=geffects.SmokePoof,)],
                ),
            area=pbge.scenes.targetarea.SelfCentered(delay_from=-1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsHidden()]),
            shot_anim=geffects.OriginSpotShotFactory(geffects.SearchTextAnim),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
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
    @classmethod
    def __str__(self):
        return self.name

class MechaGunnery( Skill ):
    name = 'Mecha Gunnery'

class MechaFighting( Skill ):
    name = 'Mecha Fighting'

class MechaPiloting( Skill ):
    name = 'Mecha Piloting'

class RangedCombat( Skill ):
    name = 'Ranged Combat'

class CloseCombat( Skill ):
    name = 'Close Combat'

class Dodge( Skill ):
    name = 'Dodge'

class Repair( Skill ):
    name = 'Repair'
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
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)

class Medicine( Skill ):
    name = 'Medicine'
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
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)

class Biotechnology( Skill ):
    name = 'Biotechnology'
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
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5)],
            targets=1)
        invodict[self].append(ba)

class Stealth( Skill ):
    name = 'Stealth'
    @classmethod
    def add_invocations(self,pc,invodict):
        pc_skill = pc.get_skill_score(Craft,self)
        n,extra = divmod(pc_skill,6)
        if random.randint(1,6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name = 'Hide', 
            fx=geffects.SetHidden(anim=geffects.SmokePoof,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[],
            targets=1)
        invodict[self].append(ba)

class Science( Skill ):
    name = 'Science'

class Computers( Skill ):
    name = 'Computers'

class Performance( Skill ):
    name = 'Performance'

class Negotiation( Skill ):
    name = 'Negotiation'

class Scouting( Skill ):
    name = 'Scouting'

class DominateAnimal( Skill ):
    name = 'Dominate Animal'

class Vitality( Skill ):
    name = 'Vitality'

class Athletics( Skill ):
    name = 'Athletics'

class Concentration( Skill ):
    name = 'Concentration'












