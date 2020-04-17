# Targeting Conditions
# Callable objects; take camp,pc,npc as paramaters, return True if condition met.
from pbge import scenes

class TargetIsEnemy(object):
    def __call__(self, camp, pc, npc):
        return camp.scene.are_hostile(pc, npc)


class TargetIsAlly(object):
    def __call__(self, camp, pc, npc):
        return camp.scene.are_allies(pc, npc)


class TargetIsOperational(object):
    def __call__(self, camp, pc, npc):
        return npc and npc.is_operational()


class TargetIsHidden(object):
    def __call__(self, camp, pc, npc):
        return npc and npc.hidden


class TargetIsNotHidden(object):
    def __call__(self, camp, pc, npc):
        return npc and not npc.hidden


class TargetIsDamaged(object):
    def __init__(self, damage_type):
        self.damage_type = damage_type
    def __call__(self, camp, pc, npc):
        damage = sum(part.hp_damage for part in npc.get_all_parts() if hasattr(part, "hp_damage") and part.hp_damage > 0 and part.material.repair_type == self.damage_type)
        return damage > 0


class TargetDoesNotHaveEnchantment(object):
    def __init__(self, enchantment_class):
        self.enchantment_class = enchantment_class
    def __call__(self, camp, pc, npc):
        return hasattr(npc,'ench_list') and not npc.ench_list.get_enchantment_of_class(self.enchantment_class)


class GenericTargeter(object):
    # This targeter will attempt to use its invocation against an enemy model.
    DEFAULT_CONDITIONS = ()

    def __init__(self, impulse_score=5, conditions=[], targetable_types=object):
        self.impulse_score = impulse_score
        self.conditions = list(conditions)
        for con in self.DEFAULT_CONDITIONS:
            self.conditions.append(con())
        self.targetable_types = targetable_types

    def is_potential_target(self, camp, pc, npc):
        # type: (GearHeadCampaign, object, object) -> bool
        # Return True if npc is a good target for this invocation.
        return isinstance(npc,self.targetable_types) and all(con(camp, pc, npc) for con in self.conditions)

    def get_potential_targets(self, invo, camp, pc):
        if hasattr(invo.area,"get_potential_targets"):
            return [npc for npc in invo.area.get_potential_targets(camp,pc) if self.is_potential_target(camp,pc,npc)]
        else:
            return [npc for npc in camp.scene.contents if self.is_potential_target(camp,pc,npc)]

    def get_impulse(self, invo, camp, pc):
        # Return an integer rating how desirable this action is.
        # An impulse of 10 is the default attack action.
        if self.get_potential_targets(invo, camp, pc):
            return self.impulse_score
        else:
            return 0

    def can_use_immediately(self):
        # Return True if this invocation can be used right away.
        pass


class AttackTargeter(GenericTargeter):
    # This targeter will attempt to use its invocation against an enemy model.
    DEFAULT_CONDITIONS = (TargetIsEnemy, TargetIsOperational)
