from pbge import effects
from pbge.scenes import animobs,movement
import random
import materials
import damage

#  *************************
#  ***   Utility  Junk   ***
#  *************************

class AttackLibraryShelf( object ):
    def __init__(self,weapon,invo_list):
        self.weapon = weapon
        self.invo_list = invo_list
    def has_at_least_one_working_invo(self,chara,in_combat=True):
        has_one = False
        for invo in self.invo_list:
            if invo.can_be_invoked(chara,in_combat):
                has_one = True
                break
        return has_one
    def get_first_working_invo(self,chara,in_combat=True):
        for invo in self.invo_list:
            if invo.can_be_invoked(chara,in_combat):
                return invo

class AttackData( object ):
    # The data class passed to an attack invocation. Mostly just
    # contains the UI stuff.
    def __init__(self,attack_icon,active_frame,inactive_frame=None,disabled_frame=None):
        self.attack_icon = attack_icon
        self.active_frame = active_frame
        if inactive_frame is not None:
            self.inactive_frame = inactive_frame
        else:
            self.inactive_frame = active_frame + 1
        if disabled_frame is not None:
            self.disabled_frame = disabled_frame
        else:
            self.disabled_frame = active_frame + 2


#  ***************************
#  ***   Movement  Modes   ***
#  ***************************

class Skimming( movement.MoveMode ):
    NAME = 'skim'
    altitude = 1

class Rolling( movement.MoveMode ):
    NAME = 'roll'

class SpaceFlight( movement.MoveMode ):
    NAME = 'space flight'

MOVEMODE_LIST = (movement.Walking,movement.Flying,Skimming,Rolling,SpaceFlight)

#  *******************
#  ***   AnimObs   ***
#  *******************

class SmallBoom( animobs.AnimOb ):
    SPRITE_NAME = 'anim_smallboom.png'
    SPRITE_OFF = ((0,0),(-7,0),(-3,6),(3,6),(7,0),(3,-6),(-3,-6))
    def __init__(self, sprite=0, pos=(0,0), loop=0, delay=1, y_off=0 ):
        super(SmallBoom, self).__init__(sprite_name=self.SPRITE_NAME,pos=pos,start_frame=0,end_frame=7,loop=loop,ticks_per_frame=1, delay=delay)
        self.x_off,self.y_off = self.SPRITE_OFF[sprite]
        self.y_off += y_off

class NoDamageBoom( SmallBoom ):
    SPRITE_NAME = 'anim_nodamage.png'

class BigBoom( animobs.AnimOb ):
    DEFAULT_SPRITE_NAME = "anim_bigboom.png"
    DEFAULT_END_FRAME = 7

class SuperBoom( animobs.AnimOb ):
    DEFAULT_SPRITE_NAME = "anim_frogatto_nuke.png"
    DEFAULT_END_FRAME = 9


class MissAnim( animobs.Caption ):
    DEFAULT_TEXT = 'Miss!'

class BigBullet( animobs.ShotAnim ):
    DEFAULT_SPRITE_NAME = "anim_s_bigbullet.png"

class GunBeam( animobs.ShotAnim ):
    DEFAULT_SPRITE_NAME = "anim_s_gunbeam.png"

class SmallBeam( animobs.ShotAnim ):
    DEFAULT_SPRITE_NAME = "anim_s_smallbeam.png"

class Missile1( animobs.ShotAnim ):
    DEFAULT_SPRITE_NAME = "anim_s_missile1.png"


#  *******************
#  ***   Effects   ***
#  *******************

class AttackRoll( effects.NoEffect ):
    """ One actor is gonna attack another actor.
        This may be opposed by a succession of defensive rolls.
        If a defensive roll beats the attack roll, its children get returned.
        Otherwise, the penetration score is recorded in the fx_record and
        the children of this effect get returned.
    """
    def __init__(self, att_stat, att_skill, children=(), anim=None, accuracy=0, penetration=0, modifiers=(), defenses=() ):
        self.att_stat = att_stat
        self.att_skill = att_skill
        if not children:
            children = list()
        self.children = children
        self.anim = anim
        self.accuracy = accuracy
        self.penetration = penetration
        self.modifiers = modifiers
        self.defenses = defenses

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0 ):
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat,self.att_skill)
        else:
            att_bonus = random.randint(1,100)
        att_roll = random.randint(1,100)

        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp,originator,pos)

        targets = camp.scene.get_actors(pos)
        next_fx = []
        for target in targets:
            hi_def_roll = 50
            for defense in self.defenses:
                if defense.can_attempt(originator,target):
                    next_fx,def_roll = defense.make_roll(self,originator,target,att_bonus,att_roll)
                    hi_def_roll = max(def_roll,hi_def_roll)
                    if next_fx:
                        break
            fx_record['penetration'] = att_roll + att_bonus + self.penetration - hi_def_roll
        return next_fx or self.children

    def get_odds( self, camp, originator, target ):
        # Return the percent chance that this attack will hit.
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat,self.att_skill)
        else:
            att_bonus = 50
        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp,originator,target.pos)
        odds = 1.0
        for defense in self.defenses:
            if defense.can_attempt(originator,target):
                odds *= defense.get_odds(self,originator,target,att_bonus)
        return odds

class MultiAttackRoll( effects.NoEffect ):
    """ One actor is gonna attack another actor.
        This may be opposed by a succession of defensive rolls.
        If a defensive roll beats the attack roll, its children get returned.
        Otherwise, the penetration score is recorded in the fx_record and
        the children of this effect get returned.
    """
    def __init__(self, att_stat, att_skill, num_attacks=2, children=(), anim=None, accuracy=0, penetration=0, modifiers=(), defenses=() ):
        self.att_stat = att_stat
        self.att_skill = att_skill
        self.num_attacks = num_attacks
        if not children:
            children = list()
        self.children = children
        self.anim = anim
        self.accuracy = accuracy
        self.penetration = penetration
        self.modifiers = modifiers
        self.defenses = defenses

    def get_multi_bonus( self ):
        # Launching multiple attacks results in a bonus to hit. Of course,
        # not all of these attacks are likely to hit.
        return min(self.num_attacks,10) * 2

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0 ):
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat,self.att_skill) + self.get_multi_bonus()
        else:
            att_bonus = random.randint(1,100)
        att_roll = random.randint(1,100)

        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp,originator,pos)

        targets = camp.scene.get_actors(pos)
        next_fx = []
        for target in targets:
            hi_def_roll = 50
            failed = False
            for defense in self.defenses:
                if defense.can_attempt(originator,target):
                    next_fx,def_roll = defense.make_roll(self,originator,target,att_bonus,att_roll)
                    hi_def_roll = max(def_roll,hi_def_roll)
                    if next_fx:
                        failed = True
                        break
            fx_record['penetration'] = att_roll + att_bonus + self.penetration - hi_def_roll - self.get_multi_bonus()
            if not failed:
                if self.num_attacks <= 10:
                    num_hits = int(min( min( att_roll + att_bonus - hi_def_roll, 45 ) // 5 + 1, self.num_attacks ))
                else:
                    num_hits = int(max((min( att_roll + att_bonus - hi_def_roll, 50 ) * self.num_attacks)//50,1))
                fx_record['number_of_hits'] = num_hits
                anims.append( animobs.Caption('x{}'.format(num_hits),pos=pos,delay=delay,y_off=camp.scene.model_altitude(target,pos[0],pos[1])-15) )


        return next_fx or self.children

    def get_odds( self, camp, originator, target ):
        # Return the percent chance that this attack will hit.
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat,self.att_skill)+ self.get_multi_bonus()
        else:
            att_bonus = 50+ self.get_multi_bonus()
        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp,originator,target.pos)
        odds = 1.0
        for defense in self.defenses:
            if defense.can_attempt(originator,target):
                odds *= defense.get_odds(self,originator,target,att_bonus)
        return odds


class DoDamage( effects.NoEffect ):
    """ Whatever is in this tile is going to take damage.
    """
    def __init__(self, damage_n, damage_d, children=(), anim=None, scale=None ):
        if not children:
            children = list()
        self.damage_n = damage_n
        self.damage_d = damage_d
        self.children = children
        self.anim = anim
        self.scale = scale
    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0 ):
        targets = camp.scene.get_actors(pos)
        penetration = fx_record.get("penetration",random.randint(1,100))
        number_of_hits = fx_record.get("number_of_hits",1)
        for target in targets:
            scale = self.scale or target.scale
            hits = [scale.scale_health(
              sum(random.randint(1,self.damage_d) for n in range(self.damage_n)),
              materials.Metal) for t in range(number_of_hits)]
            mydamage = damage.Damage( camp, hits,
                  penetration, target, anims )
        return self.children

#  ***************************
#  ***   Roll  Modifiers   ***
#  ***************************
#
# Modular roll modifiers.

class RangeModifier( object ):
    def __init__(self,range_step):
        self.range_step = range_step
    def calc_modifier( self, camp, attacker, pos ):
        my_range = camp.scene.distance(attacker.pos,pos)
        my_mod = ((my_range - 1)//self.range_step) * -5
        if my_range < (self.range_step-3):
            my_mod += (self.range_step-3-my_range) * -5
        return my_mod


#  **************************
#  ***   Defense  Rolls   ***
#  **************************
#
# Each defense roll takes the attack roll effect, the attacker, defender,
# attack bonus, and attack roll.
# It returns the roll result fx (None if the roll was unsuccessful)
# and the defense target (def roll + def bonus), which is used to calculate
# penetration if the attack hits.

class DodgeRoll( object ):
    def make_roll( self, atroller, attacker, defender, att_bonus, att_roll ):
        # If the attack roll + attack bonus + accuracy is higher than the
        # defender's defense bonus + maneuverability + 20, or if the attack roll
        # is greater than 95, the attack hits.
        def_target = defender.get_dodge_score() + 50

        if att_roll > 95:
            # A roll greater than 95 always hits.
            return (None,def_target)
        elif att_roll <= 5:
            # A roll of 5 or less always misses.
            return (self.CHILDREN, def_target)
        elif (att_roll + att_bonus + atroller.accuracy) > (def_target + defender.calc_mobility()):
            return (None,def_target)
        else:
            return (self.CHILDREN, def_target)

    def can_attempt( self, attacker, defender ):
        return True

    def get_odds( self, atroller, attacker, defender, att_bonus ):
        # Return the odds as a float.
        def_target = defender.get_dodge_score()
        # The chance to hit is clamped between 5% and 95%.
        percent = min(max(50 + (att_bonus + atroller.accuracy) - (def_target + defender.calc_mobility()),5),95)
        return float(percent)/100

    CHILDREN = (effects.NoEffect(anim=MissAnim),)

# BlockRoll, ParryRoll, ECMRoll, AntiMissileRoll

#  *****************
#  ***   PRICE   ***
#  *****************

class AmmoPrice(object):
    def __init__( self, ammo_source, ammo_amount ):
        self.ammo_source = ammo_source
        self.ammo_amount = ammo_amount

    def pay( self, chara ):
        self.ammo_source.spent += self.ammo_amount

    def can_pay( self, chara ):
        return self.ammo_source.quantity >= (self.ammo_source.spent + self.ammo_amount)








