from pbge import Singleton
from . import geffects
import pbge
import random
from . import materials
from . import aitargeters
from . import listentomysong, enchantments, personality

DIFFICULTY_TRIVIAL = -50
DIFFICULTY_EASY = -25
DIFFICULTY_AVERAGE = 0
DIFFICULTY_HARD = 25
DIFFICULTY_LEGENDARY = 50


def get_skill_target(rank, difficulty=DIFFICULTY_AVERAGE):
    return rank + difficulty + 50


#  ***************
#  ***  STATS  ***
#  ***************

class Stat(Singleton):
    @classmethod
    def __str__(self):
        return self.name


class Reflexes(Stat):
    name = 'Reflexes'


class Body(Stat):
    name = 'Body'


class Speed(Stat):
    name = 'Speed'


class Perception(Stat):
    name = 'Perception'

    @classmethod
    def add_invocations(self, pc, invodict):
        pc_skill = pc.get_skill_score(self, Scouting)
        ba = pbge.effects.Invocation(
            name='Search',
            fx=geffects.CheckConditions([aitargeters.TargetIsEnemy(), aitargeters.TargetIsHidden()],
                                        anim=geffects.SearchAnim, on_success=[
                    geffects.OpposedSkillRoll(Perception, Scouting, Speed, Stealth,
                                              roll_mod=25, min_chance=25,
                                              on_success=[geffects.SetVisible(anim=geffects.SmokePoof, )],
                                              ), ]),
            area=pbge.scenes.targetarea.SelfCentered(radius=6, delay_from=-1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(), aitargeters.TargetIsHidden()]),
            shot_anim=geffects.OriginSpotShotFactory(geffects.SearchTextAnim),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 6),
            price=[],
            targets=1,
            help_text="Attempt to spot hidden units within a 6 tile radius."
        )
        invodict[Scouting].append(ba)


class Craft(Stat):
    name = 'Craft'


class Ego(Stat):
    name = 'Ego'


class Knowledge(Stat):
    name = 'Knowledge'


class Charm(Stat):
    name = 'Charm'


PRIMARY_STATS = (Reflexes, Body, Speed, Perception, Craft, Ego, Knowledge, Charm)


#  ****************
#  ***  SKILLS  ***
#  ****************

class Skill(Singleton):
    name = ''
    desc = ''

    SKILL_COST = (100, 100, 200, 300, 400,
                  500, 800, 1300, 2100, 3400,
                  5500, 8900, 14400, 23300, 37700)

    @classmethod
    def improvement_cost(cls, pc, current_value):
        return cls.SKILL_COST[min(max(current_value, 0), 14)]


class MechaGunnery(Skill):
    name = 'Mecha Gunnery'
    desc = "Used when attacking with mecha scale ranged weapons such as guns, missile launchers, and flamethrowers."


class MechaFighting(Skill):
    name = 'Mecha Fighting'
    desc = "Used when attacking with mecha scale close combat weapons and also when making unarmed attacks in a mecha."


class MechaPiloting(Skill):
    name = 'Mecha Piloting'
    desc = "Determines your ability to evade attacks when piloting a mecha."


class RangedCombat(Skill):
    name = 'Ranged Combat'
    desc = "Used when attacking with personal ranged weapons such as guns, missile launchers, and flamethrowers."


class CloseCombat(Skill):
    name = 'Close Combat'
    desc = "Used when attacking with personal close combat weapons and also when making unarmed attacks."


class Dodge(Skill):
    name = 'Dodge'
    desc = "Determines your ability to evade attacks in personal combat."


class Repair(Skill):
    name = 'Repair'
    desc = "This skill allows you to repair damage to mecha and equipment. Use of this skill costs MP."

    @classmethod
    def add_invocations(self, pc, invodict):
        pc_skill = pc.get_skill_score(Craft, self)
        n, extra = divmod(pc_skill, 6)
        if random.randint(1, 6) <= extra:
            n += 1
        n = max(n, 1)
        ba = pbge.effects.Invocation(
            name='Repair',
            fx=geffects.DoHealing(
                n, 6, repair_type=materials.RT_REPAIR,
                anim=geffects.RepairAnim,
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(impulse_score=10, conditions=[aitargeters.TargetIsAlly(),
                                                                             aitargeters.TargetIsOperational(),
                                                                             aitargeters.TargetIsDamaged(
                                                                                 materials.RT_REPAIR)],
                                               targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 0),
            price=[geffects.MentalPrice(5)],
            targets=1,
            help_text="Restore HP to inorganic mecha, equipment, and robots."
        )
        invodict[self].append(ba)


class Medicine(Skill):
    name = 'Medicine'
    desc = "This skill allows you to heal wounded lancemates. Use of this skill costs MP."

    @classmethod
    def add_invocations(self, pc, invodict):
        pc_skill = pc.get_skill_score(Craft, self)
        n, extra = divmod(pc_skill, 6)
        if random.randint(1, 6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name='Heal',
            fx=geffects.DoHealing(
                max(n, 1), 6, repair_type=materials.RT_MEDICINE,
                anim=geffects.MedicineAnim,
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(impulse_score=10, conditions=[aitargeters.TargetIsAlly(),
                                                                             aitargeters.TargetIsOperational(),
                                                                             aitargeters.TargetIsDamaged(
                                                                                 materials.RT_MEDICINE)],
                                               targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 0),
            price=[geffects.MentalPrice(5)],
            targets=1,
            help_text="Restore HP to people and animals."
        )
        invodict[self].append(ba)

        antidote = pbge.effects.Invocation(
            name='Cure Poison',
            fx=geffects.DispelEnchantments(
                dispel_this=enchantments.USE_ANTIDOTE,
                anim=geffects.MedicineAnim,
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(impulse_score=50, conditions=[aitargeters.TargetIsAlly(),
                                                                             aitargeters.TargetIsOperational(),
                                                                             aitargeters.TargetHasEnchantment(
                                                                                 geffects.Poisoned)],
                                               targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 15),
            price=[geffects.MentalPrice(5), geffects.StatValuePrice(self, 5)],
            targets=1,
            help_text="Remove the \"Poisoned\" status effect from one target."
        )
        invodict[self].append(antidote)


class Biotechnology(Skill):
    name = 'Biotechnology'
    desc = "This skill allows you to repair biotechnological constructs. Use of this skill requires MP."

    @classmethod
    def add_invocations(self, pc, invodict):
        pc_skill = pc.get_skill_score(Craft, self)
        n, extra = divmod(pc_skill, 6)
        if random.randint(1, 6) <= extra:
            n += 1
        ba = pbge.effects.Invocation(
            name='Repair',
            fx=geffects.DoHealing(
                max(n, 1), 6, repair_type=materials.RT_BIOTECHNOLOGY,
                anim=geffects.BiotechnologyAnim,
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=1),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(impulse_score=10, conditions=[aitargeters.TargetIsAlly(),
                                                                             aitargeters.TargetIsOperational(),
                                                                             aitargeters.TargetIsDamaged(
                                                                                 materials.RT_BIOTECHNOLOGY)],
                                               targetable_types=pbge.scenes.PlaceableThing),
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 0),
            price=[geffects.MentalPrice(5)],
            targets=1,
            help_text="Restore HP to biotechnological mecha, synths, and equipment."
        )
        invodict[self].append(ba)


class Stealth(Skill):
    name = 'Stealth'
    desc = "This skill allows you to hide during combat. Stealth attacks get bonuses."

    @classmethod
    def add_invocations(self, pc, invodict):
        ba = pbge.effects.Invocation(
            name='Hide',
            fx=geffects.StealthSkillRoll(
                on_success=[geffects.SetHidden(anim=geffects.SmokePoof), ],
                on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim), ],
            ),
            area=pbge.scenes.targetarea.SelfOnly(),
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsAlly(),
                                                           aitargeters.TargetIsNotHidden()]),
            used_in_combat=True, used_in_exploration=True,
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 3),
            price=[geffects.MentalPrice(5), ],
            targets=1,
            help_text="While hidden, enemies will be unable to directly target you with attacks. Your attacks will gain a bonus to hit and to damage."
        )
        invodict[self].append(ba)


class Science(Skill):
    name = 'Science'
    desc = "This skill allows you to craft advanced equipment, or carefully study your opponents in battle."

    @classmethod
    def add_invocations(cls, pc, invodict):
        ba = pbge.effects.Invocation(
            name='Spot Weakness',
            fx=geffects.OpposedSkillRoll(Perception, cls, Ego, Vitality,
                                         roll_mod=50, min_chance=25,
                                         on_success=[
                                             geffects.AddEnchantment(geffects.WeakPoint, anim=geffects.SearchAnim, )],
                                         on_failure=[pbge.effects.NoEffect(anim=geffects.FailAnim), ],
                                         ),
            area=pbge.scenes.targetarea.SingleTarget(reach=15),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(), aitargeters.TargetIsNotHidden(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(
                                                               geffects.WeakPoint)]),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 9),
            price=[geffects.MentalPrice(2), ],
            targets=1,
            help_text="One enemy you target within 15 tiles will suffer +20 penetration from all attacks until the end of combat."
        )
        invodict[cls].append(ba)


class Computers(Skill):
    name = 'Computers'
    desc = "This skill allows you to hack computers and use electronic warfare systems."


class Performance(Skill):
    name = 'Performance'
    desc = "This skill enables you to play music. Do it well enough and you might even inspire allies and demoralize enemies during combat."

    @classmethod
    def add_invocations(self, pc, invodict):
        invodict[self].append(listentomysong.Invocation(att_stat=Charm
                                                        , att_skill=Performance
                                                        , def_stat=Ego
                                                        , def_skill=Concentration,
                                                        help_text="Your music can inspire allies and confuse enemies... or if done poorly it may have the opposite result."
                                                        ))


class Negotiation(Skill):
    name = 'Negotiation'
    desc = "This skill is used to verbally influence other characters."

    @classmethod
    def add_invocations(self, pc, invodict):
        encourage = pbge.effects.Invocation(
            name="Encourage",
            fx=geffects.DoEncourage(Charm, self),
            area=pbge.scenes.targetarea.SingleTarget(reach=10),
            used_in_combat=True, used_in_exploration=True,
            ai_tar=aitargeters.GenericTargeter(
                targetable_types=(pbge.scenes.PlaceableThing,),
                conditions=[aitargeters.TargetIsAlly()
                    , aitargeters.TargetIsOperational()
                    , aitargeters.TargetIsLowMP()
                            ]),
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 0),
            price=[geffects.StaminaPrice(5)],
            targets=1,
            help_text="You can expend some of your stamina to recharge a single ally's mental points."
        )
        invodict[self].append(encourage)


class Scouting(Skill):
    name = 'Scouting'
    desc = "This skill is used to spot hidden things, and see enemies hiding behind cover."

    @classmethod
    def add_invocations(cls, pc, invodict):
        if pc and hasattr(pc, "get_sensor_range"):
            rng = pc.get_sensor_range(pc.scale)
        else:
            rng = 10
        ba2 = pbge.effects.Invocation(
            name='Spot Behind Cover',
            fx=geffects.CheckConditions([aitargeters.TargetIsEnemy()],
                                        on_success=[geffects.OpposedSkillRoll(Perception, cls, Speed, Stealth,
                                                                              roll_mod=50, min_chance=10,
                                                                              on_success=[geffects.AddEnchantment(
                                                                                  geffects.BreakingCover,
                                                                                  anim=geffects.SearchAnim)],
                                                                              on_failure=[pbge.effects.NoEffect(
                                                                                  anim=geffects.FailAnim)])]),
            area=pbge.scenes.targetarea.Blast(radius=2,
                                              reach=rng),
            ai_tar=aitargeters.GenericTargeter(targetable_types=(pbge.scenes.PlaceableThing,),
                                               conditions=[aitargeters.TargetIsOperational(),
                                                           aitargeters.TargetIsEnemy(),
                                                           aitargeters.TargetDoesNotHaveEnchantment(
                                                               geffects.BreakingCover)]),
            used_in_combat=True, used_in_exploration=False,
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 12),
            price=[geffects.MentalPrice(3),],
            targets=1,
            help_text="Affected enemies will lose 100% of their cover bonus against all allied attacks for two rounds."
        )
        invodict[Scouting].append(ba2)


class Wildcraft(Skill):
    name = 'Wildcraft'
    desc = "This skill is used for wilderness survival and to train animals."

    @classmethod
    def add_invocations(cls, pc, invodict):
        take_cover_skill = cls
        take_cover_stat = Speed
        take_cover_bonus = min(max(pc.get_skill_score(take_cover_stat, take_cover_skill) * 2 - 50, 25), 100)
        take_cover = pbge.effects.Invocation(
            name='Stalk Prey',
            fx=geffects.AddEnchantment(geffects.TakingCover,
                                       anim=geffects.TakeCoverAnim),
            area=pbge.scenes.targetarea.SelfOnly(),
            ai_tar=aitargeters.GenericTargeter(
                targetable_types=(pbge.scenes.PlaceableThing,),
                conditions=[
                    aitargeters.TargetIsOperational(),
                    aitargeters.TargetIsAlly(),
                    aitargeters.TargetDoesNotHaveEnchantment(geffects.TakingCover)]),
            used_in_combat=True, used_in_exploration=True,
            shot_anim=None,
            data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 24),
            price=[geffects.MentalPrice(3),],
            targets=1,
            help_text="For three rounds you will receive a 50% bonus to cover against enemy attacks, while your own attacks will negate 50% of the cover bonus of all enemies."
        )
        invodict[cls].append(take_cover)

        call_animal_companion = pbge.effects.Invocation(
            name="Call Animal Companion",
            fx=geffects.CallAnimalCompanion(
                Charm, cls, cls.get_pet_tags(pc)
            ),
            area=pbge.scenes.targetarea.SelfOnly(),
            ai_tar=None,
            used_in_combat=True, used_in_exploration=True,
            shot_anim=None, data=geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 21),
            price=[geffects.MentalPrice(5), geffects.StatValuePrice(cls, 5)]
        )
        invodict[cls].append(call_animal_companion)

    @staticmethod
    def get_pet_tags(pc):
        mytags = ["ANIMAL"]
        if personality.Cheerful in pc.personality:
            mytags.append("BRIGHT")
        if personality.Grim in pc.personality:
            mytags.append("DARK")
        if personality.Easygoing in pc.personality:
            mytags.append("GREEN")
        if personality.Passionate in pc.personality:
            mytags.append("FIRE")
        if personality.Sociable in pc.personality:
            mytags.append("CITY")
        if personality.Shy in pc.personality:
            mytags.append("EXOTIC")
        if personality.GreenZone in pc.personality:
            mytags.append("FOREST")
        if personality.DeadZone in pc.personality:
            mytags.append("MUTANT")
        if Science in pc.statline:
            mytags.append("DINOSAUR")
        if Biotechnology in pc.statline:
            mytags.append("SYNTH")
        if Stealth in pc.statline:
            mytags.append("TOXIC")
        return mytags


class Cybertech(Skill):
    name = 'Cybertech'
    desc = "This skill determines how much cyberware a person can safely have."


class Vitality(Skill):
    name = 'Vitality'
    desc = "This skill determines your health point total."


class Athletics(Skill):
    name = 'Athletics'
    desc = "This skill determines your stamina point total."


class Concentration(Skill):
    name = 'Concentration'
    desc = "This skill determines your mental point total."


COMBATANT_SKILLS = (
MechaFighting, MechaGunnery, MechaPiloting, RangedCombat, CloseCombat, Dodge, Vitality, Athletics, Concentration)
FUNDAMENTAL_COMBATANT_SKILLS = (MechaFighting, MechaGunnery, MechaPiloting, RangedCombat, CloseCombat, Dodge)
EXTRA_COMBAT_SKILLS = (Vitality, Athletics, Concentration)

NONCOMBAT_SKILLS = (
Repair, Medicine, Biotechnology, Stealth, Science, Computers, Performance, Negotiation, Scouting, Wildcraft, Cybertech)
ALL_SKILLS = COMBATANT_SKILLS + NONCOMBAT_SKILLS

REPAIR_SKILLS = {
    materials.RT_BIOTECHNOLOGY: Biotechnology,
    materials.RT_MEDICINE: Medicine,
    materials.RT_REPAIR: Repair
}
