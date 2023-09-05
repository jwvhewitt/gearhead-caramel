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


class TargetHasEnchantment(object):
    def __init__(self, enchantment_class):
        self.enchantment_class = enchantment_class
    def __call__(self, camp, pc, npc):
        return hasattr(npc,'ench_list') and npc.ench_list.get_enchantment_of_class(self.enchantment_class)


class TargetDoesNotHaveEnchantment(object):
    def __init__(self, enchantment_class):
        self.enchantment_class = enchantment_class
    def __call__(self, camp, pc, npc):
        return hasattr(npc,'ench_list') and not npc.ench_list.get_enchantment_of_class(self.enchantment_class)


class TargetIsLowMP(object):
    def __init__(self, threshold = 6):
        self.threshold = threshold
    def __call__(self, camp, pc, npc):
        if not npc:
            return False
        if hasattr(npc, 'get_pilot'):
            npc = npc.get_pilot()
        if hasattr(npc, 'get_current_mental'):
            return npc.get_current_mental() <= self.threshold
        return False


class TargetIsLowSP(object):
    def __init__(self, threshold = 6):
        self.threshold = threshold
    def __call__(self, camp, pc, npc):
        if not npc:
            return False
        if hasattr(npc, 'get_pilot'):
            npc = npc.get_pilot()
        if hasattr(npc, 'get_current_stamina'):
            return npc.get_current_stamina() <= self.threshold
        return False


class TargetHasSP(object):
    def __init__(self, threshold = 0):
        self.threshold = threshold
    def __call__(self, camp, pc, npc):
        if not npc:
            return False
        if hasattr(npc, 'get_pilot'):
            npc = npc.get_pilot()
        if hasattr(npc, 'get_current_stamina'):
            return npc.get_current_stamina() > self.threshold
        return False


class TargetIsOriginator(object):
    def __call__(self, camp, pc, npc):
        return pc is npc


# AI will cast this only if there are 2 or more opponents/allies within reach.
class CasterIsSurrounded(object):
   # `by` can be 'are_hostile' or 'are_allies'.
   def __init__(self, reach=2, by='are_hostile'):
       self.reach = reach
       self.by = by
   def __call__(self, camp, pc, npc):
       if (not hasattr(pc, 'pos')) or (pc.pos is None):
           return False
       pos = pc.pos
       scene = camp.scene
       pred = getattr(scene, self.by)
       num = 0
       for a in scene.get_operational_actors():
           if (not hasattr(a, 'pos')) or (a.pos is None):
               continue
           if scene.distance(pos, a.pos) <= self.reach:
               num = num + 1
               if num > 1:
                   return True
       return False


# AI will cast this only if it has no allies within reach.
class CasterIsAlone(object):
    # `by` can be 'are_allies' or 'are_hostile'.
   def __init__(self, reach=2, by='are_allies'):
       self.reach = reach
       self.by = by
   def __call__(self, camp, pc, npc):
       if (not hasattr(pc, 'pos')) or (pc.pos is None):
           return False
       pos = pc.pos
       scene = camp.scene
       pred = getattr(scene, self.by)
       for a in scene.get_operational_actors():
           if (not hasattr(a, 'pos')) or (a.pos is None):
               continue
           if scene.distance(pos, a.pos) <= self.reach:
               return False
       return True


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
