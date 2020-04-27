import pbge
from pbge import Singleton
from . import geffects
from . import scale
from . import stats
from . import aitargeters


class Program(Singleton):
    # Actual programs MUST fill in the below
    name = 'Unknown Program'
    USE_AT = ()
    COST = 500

    @classmethod
    def get_invocations(cls, pc):
        raise NotImplementedError('Program must override get_invocations')
        return list()


class EMBlaster(Program):
    name = 'EM Blaster'
    desc = 'Blasts mecha with a strong electromagnetic pulse that makes them go haywire.'
    USE_AT = (scale.MechaScale,)
    COST = 500

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        myprog2 = pbge.effects.Invocation(
            name = 'Scrambler',
            fx= geffects.OpposedSkillRoll(stats.Knowledge,stats.Computers,stats.Ego,stats.Computers,
                    roll_mod=25, min_chance=10,
                    on_success=[geffects.AddEnchantment(geffects.HaywireStatus,anim=geffects.InflictHaywireAnim,)],
                    on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=5),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.HaywireStatus)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12,thrill_power=12),
            price=[geffects.MentalPrice(3),],
            targets=1)
        progs.append(myprog2)

        return progs


class TargetAnalysis(Program):
    name = 'Target Analysis'
    desc = 'Analyzes sensor inputs and scans hidden targets, or locks onto visible targets.'
    USE_AT = (scale.HumanScale, scale.MechaScale)
    COST = 100

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        myprog = pbge.effects.Invocation(
            name='Long Range Scan',
            fx=geffects.CheckConditions([aitargeters.TargetIsEnemy(), aitargeters.TargetIsHidden()],
                                        anim=geffects.SearchAnim, on_success=[
                    geffects.OpposedSkillRoll(stats.Perception, stats.Computers, stats.Ego, stats.Stealth,
                                              roll_mod=25, min_chance=50,
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
                    roll_mod=25, min_chance=50,
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


class Deflect(Program):
    name = 'Deflect'
    desc = 'Analyses the environment fully, predicting the paths of incoming fire to let the pilot more easily evade them.'
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


ALL_PROGRAMS = Program.__subclasses__()
