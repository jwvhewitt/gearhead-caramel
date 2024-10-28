from . import geffects, base
from pbge import effects
import pbge
import random
from . import aitargeters
from . import enchantments

SONG_REACH = 12
MENTAL_COST = 8
ROLL_MOD = 15

class _Info(object):
    def __init__(self, att_stat, att_skill, def_stat, def_skill):
        self.att_stat = att_stat
        self.att_skill = att_skill
        self.def_stat = def_stat
        self.def_skill = def_skill
        

# This is the entry point to this module.
class Invocation( effects.Invocation ):
    def __init__(self, att_stat, att_skill, def_stat, def_skill, help_text=""):
        info = _Info(att_stat, att_skill, def_stat, def_skill)
        super().__init__( name = 'Captivate Audience'
                        , fx = _top_fx(info)
                        , area = pbge.scenes.targetarea.SelfCentered(radius = SONG_REACH)
                        , used_in_combat = True
                        , used_in_exploration = False
                        , ai_tar = aitargeters.GenericTargeter( targetable_types = (base.Combatant,)
                                                              , conditions = [ aitargeters.CasterIsSurrounded(reach = SONG_REACH) ]
                                                              )
                        , shot_anim = geffects.OriginSpotShotFactory(geffects.ListenToMySongAnim)
                        , data = geffects.AttackData(pbge.image.Image('sys_skillicons.png', 32, 32), 27)
                        , price = [geffects.MentalPrice(MENTAL_COST)]
                        , targets = 1,
                          help_text=help_text
                        )


def _top_fx(info):
    '''Primary effect when cast.'''
    # The invocation has the entire area, so the effect will apply to
    # the entire area.
    # However, we want the song effect to be triggered once only,
    # at the originator.
    return geffects.CheckConditions( [aitargeters.TargetIsOriginator()]
                                   , on_success = [_sing_fx(info)]
                                   )
def _sing_fx(info):
    return geffects.SkillRoll( info.att_stat, info.att_skill
                             , roll_mod = ROLL_MOD
                             , on_success = [_positive_fx(info)]
                             , on_failure = [_fail_fx(info)]
                             )

def _fail_fx(info):
    # On failing, do another skill roll.
    # If they fail again, trigger a negative effect.
    return geffects.SkillRoll( info.att_stat, info.att_skill
                             , roll_mod = ROLL_MOD
                             , on_success = [_null_fx(info)]
                             , on_failure = [_negative_fx(info)]
                             )

###############################################################################

# Base classes for positive and negative invocations.
# These are invoked at the originator only, so has to redo the area.

class _SongInvocation(effects.Invocation):
    '''Common class for all invocations'''
    def __init__(self, fx):
        # The name is not actually seen.
        super().__init__( name = "Song Effect"
                        , fx = fx
                        , area = pbge.scenes.targetarea.SelfCentered( radius = SONG_REACH
                                                                    , exclude_middle = True
                                                                    , delay_from = -1
                                                                    )
                        )

# Actual base classes for positive and negative song results.
# Derived classes must accept a single argument, info, in
# their constructors.
class _PositiveSongInvocation(_SongInvocation):
    def __init__(self, fx):
        wrapfx = effects.NoEffect( anim = geffects.MusicAnim
                                 , children = [fx]
                                 )
        super().__init__(wrapfx)
class _NegativeSongInvocation(_SongInvocation):
    def __init__(self, fx):
        wrapfx = effects.NoEffect( anim = geffects.BadMusicAnim
                                 , children = [fx]
                                 )
        super().__init__(wrapfx)

# Actual class for a "normal failure" i.e. does nothing except
# waste mental points.
class _NeutralSongInvocation(_SongInvocation):
    def __init__(self):
        fx = geffects.CheckConditions( [aitargeters.TargetIsOperational()]
                                     , on_success = [effects.NoEffect(anim = geffects.HeckleAnim)]
                                     )
        wrapfx = effects.NoEffect( anim = geffects.BadMusicAnim
                                 , children = [fx]
                                 )
        super().__init__(wrapfx)

###############################################################################

# Utility functions for creating song effects.

def _affect_enemies(fx, ally_anim = None):
    """Give an effect that only affects enemies"""
    if ally_anim:
        on_failure = [geffects.CheckConditions( [ aitargeters.TargetIsOperational()
                                                , aitargeters.TargetIsAlly()
                                                ]
                                              , on_success = [effects.NoEffect(anim = ally_anim)]
                                              )]
    else:
        on_failure = []
    return geffects.CheckConditions( [ aitargeters.TargetIsOperational()
                                     , aitargeters.TargetIsEnemy()
                                     ]
                                   , on_success = [fx]
                                   , on_failure = on_failure
                                   )
def _affect_allies(fx, enemy_anim = None):
    """Give an effect that only affects allies"""
    if enemy_anim:
        on_failure = [geffects.CheckConditions( [ aitargeters.TargetIsOperational()
                                                , aitargeters.TargetIsEnemy()
                                                ]
                                              , on_success = [effects.NoEffect(anim = enemy_anim)]
                                              )]
    else:
        on_failure = []
    return geffects.CheckConditions( [ aitargeters.TargetIsOperational()
                                     , aitargeters.TargetIsAlly()
                                     ]
                                   , on_success = [fx]
                                   , on_failure = on_failure
                                   )

def _double_skill_roll(info, fx, roll_mod = 35, min_chance = 25):
    """Do an opposed skill roll, if it fails do another skill roll."""
    return geffects.OpposedSkillRoll( info.att_stat, info.att_skill
                                    , info.def_stat, info.def_skill
                                    , roll_mod = roll_mod
                                    , min_chance = min_chance
                                    , on_success = [fx]
                                    , on_failure = [ geffects.OpposedSkillRoll( info.att_stat, info.att_skill
                                                                              , info.def_stat, info.def_skill
                                                                              , roll_mod = 25
                                                                              , min_chance = 25
                                                                              , on_success = [fx]
                                                                              , on_failure = [effects.NoEffect(anim = geffects.ResistAnim)]
                                                                              )
                                                   ]
                                    )

########################
### Positive Effects ###
########################

class _HaywireEnemies(_PositiveSongInvocation):
    # THis is mostly a placeholder for now.
    def __init__(self, info):
        super().__init__(_affect_enemies( self._get_fx(info)
                                        , geffects.CheerAnim
                                        ))
    def _get_fx(self, info):
        return _double_skill_roll(info, geffects.AddEnchantment( geffects.HaywireStatus
                                                               , anim = geffects.InflictHaywireAnim
                                                               ))


class _InspireAllies(_PositiveSongInvocation):
    def __init__(self, info):
        super().__init__(_affect_allies(self._get_fx(info)))
    def _get_fx(self, info):
        return geffects.AddEnchantment( geffects.Inspired
                                      , anim = geffects.BurnAnim
                                      )


class _DemoralizeEnemies(_PositiveSongInvocation):
    def __init__(self, info):
        super().__init__(_affect_enemies( self._get_fx(info)
                                        , geffects.CheerAnim
                                        ))
    def _get_fx(self, info):
        return  _double_skill_roll(info, geffects.AddEnchantment( geffects.Demoralized
                                                                , anim = geffects.SuperBoom
                                                                ))


class _EnergizeAllies(_PositiveSongInvocation):
    def __init__(self, info):
        super().__init__(_affect_allies(self._get_fx(info)))
    def _get_fx(self, info):
        children = [ geffects.DoEncourage(info.att_stat, info.att_skill)
                   , geffects.DispelEnchantments(enchantments.ON_DISPEL_NEGATIVE)
                   ]
        return effects.NoEffect( children = children
                               , anim = geffects.OverloadAnim
                               )


########################
### Negative Effects ###
########################

class _DemoralizeAllies(_NegativeSongInvocation):
    # THis is mostly a placeholder for now.
    def __init__(self, info):
        super().__init__(_affect_allies( self._get_fx(info)
                                       , geffects.HeckleAnim
                                       ))
    def _get_fx(self, info):
        return geffects.AddEnchantment( geffects.Demoralized
                                      , anim = geffects.SuperBoom
                                      )

###############################################################################

def _random_fx(BaseSongInvocation, info):
    '''Returns a RandomEffect that randomly chooses the subclasses of the given
    BaseSongInvocation.
    '''
    possible_fx = list()
    for cls in BaseSongInvocation.__subclasses__():
        possible_fx.append(effects.InvokeEffect(invocation = cls(info)))
    return geffects.RandomEffect(possible_fx = possible_fx)

def _positive_fx(info):
    return _random_fx(_PositiveSongInvocation, info)
def _null_fx(info):
    return effects.InvokeEffect(invocation = _NeutralSongInvocation())
def _negative_fx(info):
    return _random_fx(_NegativeSongInvocation, info)
