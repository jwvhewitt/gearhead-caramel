import pbge
from pbge import Singleton
from . import geffects
from . import scale
from . import stats
from . import aitargeters


class TargetAnalysis(Singleton):
    name = 'Target Analysis'
    USE_AT = (scale.HumanScale, scale.MechaScale)
    COST = 100

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        myprog = pbge.effects.Invocation(
            name='Long Range Scan',
            fx=geffects.CheckConditions([aitargeters.TargetIsEnemy(), aitargeters.TargetIsHidden()],
                                        anim=geffects.SearchAnim, on_success=[
                    geffects.OpposedSkillRoll(stats.Perception, stats.Computers, stats.Speed, stats.Stealth,
                                              roll_mod=25, min_chance=25,
                                              on_success=[geffects.SetVisible(anim=geffects.SmokePoof, )],
                                              ), ]),
            area=pbge.scenes.targetarea.SelfCentered(radius=15, delay_from=-1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(),
                                                           aitargeters.TargetIsHidden()]),
            shot_anim=geffects.OriginSpotShotFactory(geffects.SearchTextAnim),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 6),
            price=[geffects.MentalPrice(1),],
            targets=1)
        progs.append(myprog)

        myprog2 = pbge.effects.Invocation(
            name = 'Sensor Lock',
            fx= geffects.OpposedSkillRoll(stats.Knowledge,stats.Computers,stats.Ego,stats.Computers,
                    roll_mod=25, min_chance=10,
                    on_success=[geffects.AddEnchantment(geffects.SensorLock,anim=geffects.SearchAnim,)],
                    on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.SensorLock)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12),
            price=[geffects.MentalPrice(3),],
            targets=1)
        progs.append(myprog2)

        return progs


class Deflect(Singleton):
    name = 'Deflect'
    USE_AT = (scale.MechaScale,)
    COST = 200

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        myprog = pbge.effects.Invocation(
            name='Prescience',
            fx=geffects.AddEnchantment(geffects.Prescience,anim=geffects.SearchAnim,),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsAlly(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(geffects.Prescience)]),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 12),
            price=[geffects.MentalPrice(2),],
            targets=1)
        progs.append(myprog)

        return progs

class EMPPulse(Singleton):
    name = 'EM Pulse'
    USE_AT = (scale.HumanScale, scale.MechaScale,)
    COST = 200

    @classmethod
    def get_invocations(cls, pc):
        return ()

ALL_PROGRAMS = (TargetAnalysis,Deflect,EMPPulse)
