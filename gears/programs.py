import pbge
from pbge import Singleton
from . import geffects
from . import scale
from . import stats
from . import aitargeters
from . import materials
import random


class Program(Singleton):
    # Actual programs MUST fill in the below
    name = 'Unknown Program'
    USE_AT = ()
    COST = 500

    # Set this to True to prevent champions from getting it.
    UNIQUE = False

    @classmethod
    def get_invocations(cls, pc):
        raise NotImplementedError('Program must override get_invocations')


class EMBlaster(Program):
    name = 'EM Blaster'
    desc = 'Blasts mecha with a strong electromagnetic pulse that makes them go haywire.'
    USE_AT = (scale.MechaScale,)
    COST = 500

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        def is_vulnerable(camp, pc, npc):
            return geffects.HaywireStatus.can_affect(npc)

        myprog2 = pbge.effects.Invocation(
            name = 'Remote Scramble',
            fx= geffects.OpposedSkillRoll(stats.Knowledge,stats.Computers,stats.Ego,stats.Computers,
                    roll_mod=25, min_chance=50,
                    on_success=[geffects.AddEnchantment(geffects.HaywireStatus,anim=geffects.InflictHaywireAnim,)],
                    on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=5),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.HaywireStatus)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12,thrill_power=30),
            price=[geffects.MentalPrice(3),],
            targets=1,
            help_text=""
        )
        progs.append(myprog2)

        myprog = pbge.effects.Invocation(
            name = 'Localized EMP',
            fx = geffects.CheckConditions([is_vulnerable],
                     anim = geffects.DustCloud,
                     on_success = [
                         geffects.OpposedSkillRoll(stats.Knowledge, stats.Computers, stats.Ego, stats.Computers,
                             roll_mod = 50, min_chance=25,
                             on_success = [geffects.AddEnchantment(geffects.HaywireStatus, anim = geffects.InflictHaywireAnim)],
                             on_failure = [pbge.effects.NoEffect(anim=geffects.FailAnim)])]),
            area = pbge.scenes.targetarea.SelfCentered(3,exclude_middle=True, delay_from = -1),
            used_in_combat = True, used_in_exploration = False,
            ai_tar = aitargeters.GenericTargeter(targetable_types = (pbge.scenes.PlaceableThing,),
                                                 conditions = [aitargeters.CasterIsSurrounded(2),
                                                               aitargeters.CasterIsAlone(2),
                                                               aitargeters.TargetDoesNotHaveEnchantment(geffects.HaywireStatus)]),
            data = geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12,thrill_power=12),
            price = [geffects.MentalPrice(5), geffects.StatValuePrice(stats.Computers,5)],
            targets = 1)
        progs.append(myprog)

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
            fx= geffects.AddEnchantment(geffects.SensorLock,anim=geffects.SearchAnim,),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.SensorLock)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12),
            price=[geffects.MentalPrice(2), geffects.StatValuePrice(stats.Computers, 3)],
            targets=1)
        progs.append(myprog2)

        progs.append(pbge.effects.Invocation(
            name='Deep Probe',
            fx=geffects.OpposedSkillRoll(stats.Knowledge, stats.Computers, stats.Ego, stats.Computers,
                                         roll_mod=25, min_chance=50,
                                         on_success=[
                                             geffects.AddEnchantment(geffects.SensorLock, anim=geffects.SearchAnim, ),
                                             geffects.AddEnchantment(geffects.WeakPoint, anim=geffects.DeepProbeAnim, )
                                         ],
                                         on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim), ],
                                         ),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(), aitargeters.TargetIsNotHidden(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(
                                                               geffects.SensorLock)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 12),
            price=[geffects.MentalPrice(2), geffects.StatValuePrice(stats.Computers, 5)],
            targets=1
        ))

        progs.append(pbge.effects.Invocation(
            name='Sensor Beam',
            fx=geffects.CheckConditions(
                conditions=[aitargeters.TargetIsOperational(),
                            aitargeters.TargetIsEnemy(),
                            aitargeters.TargetDoesNotHaveEnchantment(geffects.SensorLock)],
                on_success=[
                    geffects.OpposedSkillRoll(stats.Knowledge, stats.Computers, stats.Ego, stats.Computers,
                                         roll_mod=25, min_chance=50,
                                         on_success=[
                                             geffects.AddEnchantment(geffects.SensorLock, anim=geffects.SensorLockAnim, ),
                                         ],
                                         on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim), ]
                                         )
                    ], anim=geffects.SearchAnim,
            ),
            area=pbge.scenes.targetarea.Cone(reach=12),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(), aitargeters.TargetIsNotHidden(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(
                                                               geffects.SensorLock)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 12),
            price=[geffects.MentalPrice(4), geffects.StatValuePrice(stats.Computers, 7)],
            targets=1
        ))

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
            price=[geffects.MentalPrice(1),],
            targets=1)
        progs.append(myprog)

        progs.append(pbge.effects.Invocation(
            name='Defense Net',
            fx=geffects.CheckConditions(
                conditions=[
                    aitargeters.TargetIsOperational(), aitargeters.TargetIsAlly(),
                    aitargeters.TargetDoesNotHaveEnchantment(geffects.Prescience),
                ], on_success=[
                    geffects.AddEnchantment(geffects.Prescience,anim=geffects.SearchAnim,),
                ],
            ),
            area=pbge.scenes.targetarea.SelfCentered(radius=10),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsAlly(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(geffects.Prescience)]),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 12),
            price=[geffects.MentalPrice(3),geffects.StatValuePrice(stats.Computers, 5)],
            targets=1
        ))

        return progs


class AIAssistant(Program):
    name = 'AI Assistant'
    desc = 'Grants a bonus to your ranged, melee, and evasion skills throughout combat, but is cancelled if your mecha goes haywire.'
    USE_AT = (scale.MechaScale,)
    COST = 200

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        myprog = pbge.effects.Invocation(
            name = 'AI Assistant',
            fx = geffects.AddEnchantment(geffects.AIAssisted,
                                         enchant_params = {'percent_prob': pc.get_skill_score(stats.Knowledge, stats.Computers) * 2},
                                         anim = geffects.AIAssistAnim),
            area = pbge.scenes.targetarea.SelfOnly(),
            used_in_combat = True, used_in_exploration = False,
            ai_tar = aitargeters.GenericTargeter(targetable_types = (pbge.scenes.PlaceableThing,),
                                                 conditions = [aitargeters.TargetIsOperational(),
                                                               aitargeters.TargetIsAlly(),
                                                               aitargeters.TargetDoesNotHaveEnchantment(geffects.HaywireStatus)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12),
            price=[],
            targets=1,
            help_text=""
        )
        progs.append(myprog)

        return progs

class Necromatix(Program):
    # This program can only be found in one place- the Mecha Graveyard.
    name = 'Necromatix'
    desc = 'An experimental PreZero self-repair system.'
    USE_AT = (scale.MechaScale,)
    COST = 500

    UNIQUE = True

    @classmethod
    def get_invocations(cls, pc):
        progs = list()

        pc_skill = pc.get_skill_score(stats.Craft, stats.Biotechnology)
        n, extra = divmod(pc_skill, 6)
        if random.randint(1, 6) <= extra:
            n += 1
        myprog = pbge.effects.Invocation(
            name = 'Self Repair',
            fx=geffects.DoHealing(
                max(n,2)+1,6, repair_type=materials.RT_REPAIR,
                anim = geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SelfOnly(),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_REPAIR)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(3)],
            targets=1,
            help_text="The bionites inside your mecha will repair the damage you have suffered."
        )
        progs.append(myprog)

        myprog = pbge.effects.Invocation(
            name = 'Repair Net',
            fx=geffects.CheckConditions(
                conditions=[
                    aitargeters.TargetIsOperational(), aitargeters.TargetIsAlly(),
                ], on_success=[
                    geffects.DoHealing(
                        max(n, 2), 6, repair_type=materials.RT_REPAIR,
                        anim=geffects.RepairAnim,
                    )
                ],
            ),
            area=pbge.scenes.targetarea.SelfCentered(radius=3),
            used_in_combat = True, used_in_exploration=True,
            ai_tar = aitargeters.GenericTargeter(impulse_score=10,conditions=[aitargeters.TargetIsAlly(),aitargeters.TargetIsOperational(),aitargeters.TargetIsDamaged(materials.RT_REPAIR)],targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png',32,32),0),
            price=[geffects.MentalPrice(5),geffects.StatValuePrice(stats.Biotechnology, 5)],
            targets=1,
            help_text="The bionites which repair your mecha will spread out and repair all allied mecha within a three tile radius."
        )
        progs.append(myprog)

        myprog2 = pbge.effects.Invocation(
            name = 'Contagion',
            fx= geffects.OpposedSkillRoll(stats.Knowledge,stats.Biotechnology,stats.Ego,stats.Computers,
                    roll_mod=25, min_chance=50,
                    on_success=[geffects.AddEnchantment(geffects.Disintegration,anim=geffects.InflictDisintegrationAnim,)],
                    on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim),],
                ),
            area=pbge.scenes.targetarea.SingleTarget(reach=5),
            used_in_combat = True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),conditions=[aitargeters.TargetIsOperational(),aitargeters.TargetIsEnemy(),aitargeters.TargetIsNotHidden(),aitargeters.TargetDoesNotHaveEnchantment(geffects.Disintegration)]),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),12,thrill_power=25),
            price=[geffects.MentalPrice(5),geffects.StatValuePrice(stats.Biotechnology,9)],
            targets=1,
            help_text="You unleash the bionites infesting your mecha on a single enemy within 5 tiles; instead of repairing the enemy mecha, the bionites will disassemble it to its component atoms."
        )
        progs.append(myprog2)


        return progs



ALL_PROGRAMS = Program.__subclasses__()
