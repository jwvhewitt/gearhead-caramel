from pbge import Singleton
from . import geffects, stats, materials, aitargeters, enchantments
import pbge

class AntidotePill(Singleton):
    VALUE = 800
    @classmethod
    def get_invocations(cls, pc):
        mylist = list()
        mylist.append(pbge.effects.Invocation(
            name = 'Antidote',
            fx=geffects.DispelEnchantments(
                dispel_this=enchantments.USE_ANTIDOTE,
                anim = geffects.MedicineAnim,
                ),
            area=pbge.scenes.targetarea.SelfOnly(),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=50,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetHasEnchantment(geffects.Poisoned)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),15),
            price=[],
            targets=1
        ))
        return mylist


class QuickFixPill(Singleton):
    VALUE = 1000
    @classmethod
    def get_invocations(cls, pc):
        mylist = list()
        mylist.append(pbge.effects.Invocation(
            name = 'Quick Fix',
            fx=geffects.DoHealing(
                3,6,repair_type=materials.RT_MEDICINE,
                anim = geffects.MedicineAnim,
                ),
            area=pbge.scenes.targetarea.SelfOnly(),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_MEDICINE)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[],
            targets=1
        ))
        return mylist


class DuctTape(Singleton):
    VALUE = 75
    @classmethod
    def get_invocations(cls, pc):
        mylist = list()
        mylist.append(pbge.effects.Invocation(
            name = 'Duct Tape',
            fx=geffects.DoHealing(
                3,6,repair_type=materials.RT_REPAIR,
                anim = geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_REPAIR)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[],
            targets=1
        ))
        return mylist


class SpareParts(Singleton):
    VALUE = 150
    @classmethod
    def get_invocations(cls, pc):
        mylist = list()
        mylist.append(pbge.effects.Invocation(
            name = 'Spare Parts',
            fx=geffects.DoHealing(
                3,8,repair_type=materials.RT_REPAIR,
                anim = geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_REPAIR)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[],
            targets=1
        ))
        return mylist

class MeatFX(Singleton):
    VALUE = 200
    @classmethod
    def get_invocations(cls, pc):
        mylist = list()
        mylist.append(pbge.effects.Invocation(
            name = 'Eat Meat',
            fx=geffects.RestoreSP(
                2,6,
                anim = geffects.SparkleRedAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat = False, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsLowSP()],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_usableicons.png',32,32),0),
            price=[],
            targets=1
        ))
        return mylist

