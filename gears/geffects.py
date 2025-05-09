from typing import override
import gears
import pbge
from pbge import effects
from pbge.scenes import animobs, movement, pfov
import random
from . import materials, scale
from . import damage, stats, pets
from .enchantments import Enchantment, END_COMBAT, ON_MOVE, DISPEL_NEGATIVE_ELECTRONIC, ON_DISPEL_POSITIVE, ON_DISPEL_NEGATIVE, USE_ANTIDOTE
import math
from . import base, tags
import copy

# For backwards compatibility reasons, import Skimming and Rolling to here. You can delete this import at
# version v1.000 when savefile compatibility breaks again.
from .tags import Skimming, Rolling

MONSTER_LIST = ()

FX_CRITICAL_HIT = "FX_CRITICAL_HIT"
FX_DAMAGE_BONUS = "FX_DAMAGE_BONUS"
FX_PENETRATION = "FX_PENETRATION"

#  *************************
#  ***   Utility  Junk   ***
#  *************************


class AttackInvocation(effects.Invocation):
    def __init__(self, weapon, *args, **kwargs):
        self.weapon = weapon
        super().__init__(*args, **kwargs)

    def invoke(self, camp, originator, target_points, anim_list, fx_record=None, data=None):
        if originator:
            anim_list.append(animobs.WatchMeWiggle(originator))
        super().invoke(camp, originator, target_points, anim_list, fx_record=fx_record, data=data)


class ItemInvocation(effects.Invocation):
    def __init__(self, weapon, *args, **kwargs):
        self.weapon = weapon
        super().__init__(*args, **kwargs)

    def invoke(self, camp, originator, target_points, anim_list, fx_record=None, data=None):
        if originator:
            anim_list.append(animobs.WatchMeWiggle(originator))
        super().invoke(camp, originator, target_points, anim_list, fx_record=fx_record, data=data)


class InvoLibraryShelf(object):
    def __init__(self, source, invo_list):
        self.source = source
        if hasattr(source, "get_shelf_name"):
            self.name = source.get_shelf_name()
        elif hasattr(source, "name"):
            self.name = source.name
        else:
            self.name = str(source)
        if hasattr(source, 'get_shelf_desc'):
            self.desc = source.get_shelf_desc()
        elif hasattr(source, 'desc'):
            self.desc = source.desc
        else:
            self.desc = '???'
        self.invo_list = invo_list

    def has_at_least_one_working_invo(self, chara, in_combat=True):
        has_one = False
        for invo in self.invo_list:
            if invo.can_be_invoked(chara, in_combat):
                has_one = True
                break
        return has_one

    def get_first_working_invo(self, chara, in_combat=True):
        for invo in self.invo_list:
            if invo.can_be_invoked(chara, in_combat):
                return invo

    def get_average_thrill_power(self, chara, in_combat=True):
        thrills = list()
        for invo in self.invo_list:
            if invo.can_be_invoked(chara, in_combat):
                thrills.append(invo.data.thrill_power)
        if thrills:
            return sum(thrills) / len(thrills)
        else:
            return 0

    def __str__(self):
        return self.name


class AttackData(object):
    # The data class passed to an attack invocation. Mostly just
    # contains the UI stuff.
    # thrill_power is a rough measurement of how exciting this attack is;
    #  used to determine what attacks to prioritize.
    def __init__(self, attack_icon, active_frame, inactive_frame=None, disabled_frame=None, thrill_power=1):
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
        self.thrill_power = thrill_power


class DashTarget(object):
    """You can charge and attack someone."""
    AUTOMATIC = False
    MOVE_AND_FIRE = False

    def __init__(self, model, delay_from=0):
        self.model = model
        self.delay_from = delay_from

    def get_area(self, camp, origin, target):
        tiles = set()
        tiles.add(target)
        return tiles

    def get_targets(self, camp, origin):
        return DashReach(camp, origin[0], origin[1], self.model).tiles

    def get_delay_point(self, origin, target):
        if self.delay_from < 0:
            return origin
        elif self.delay_from > 0:
            return target

    def get_reach(self):
        return self.model.get_current_speed() // 10 + 1

    def get_firing_points(self, camp, desired_target):
        return {self.model.pos}

    def get_potential_targets(self, camp, pc):
        mytiles = DashReach(camp, pc.pos[0], pc.pos[1], self.model).tiles
        return [pc for pc in camp.scene.get_operational_actors() if pc.pos in mytiles]


class DashReach(pfov.PointOfView):
    # Return the attackable tiles for a dash attack.
    def __init__(self, camp, x0, y0, model):
        self.x = x0
        self.y = y0
        self.model = model
        self.scene = camp.scene
        self.blocked_tiles = camp.scene.get_blocked_tiles()
        self.radius = model.get_current_speed() // 10 + 1
        self.tiles = set()
        self.vision_type = model.mmode
        self.nav = pbge.scenes.pathfinding.NavigationGuide(camp.scene, model.pos, model.get_current_speed(),
                                                           model.mmode, self.blocked_tiles)
        pfov.fieldOfView(x0, y0, camp.scene.width, camp.scene.height, self.radius, self)

    def TileBlocked(self, x, y):
        if (x, y) in self.blocked_tiles:
            return True
        elif self.scene.on_the_map(x, y):
            return self.scene.tile_blocks_movement(x, y, self.vision_type)
        else:
            return True

    def VisitTile(self, x, y):
        dist = round(math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2))
        intline = animobs.get_line(self.model.pos[0], self.model.pos[1], x, y)

        if dist <= self.radius and dist > 1 and intline[-2] in self.nav.cost_to_tile:
            self.tiles.add((x, y))


class TerrainBreaker:
    # Attach this to a terrain object as the "breaker" property.
    def __init__(self, damage_threshold, breaks_into, terrain_value=1):
        self.damage_threshold = damage_threshold
        self.breaks_into = breaks_into
        self.terrain_value = terrain_value

    def deal_with_damage(self, anims, myscene, pos, damage_class, anim_class):
        damage_die = damage_class
        if myscene.scale is scale.HumanScale:
            damage_die = damage_die // 2
        damage_roll = random.randint(0, damage_die)
        if damage_roll >= self.damage_threshold:
            anims.append(anim_class(pos, myscene, self.breaks_into))
            myscene.terrain_damage_done += self.terrain_value
            return True
        #_=FireAreaEnchantment(pos, scene=myscene)


class FireAreaEnchantment(pbge.scenes.areaenchant.AreaEnchantment):
    AREA_ENCHANTMENT_TYPE = "Fire!"
    IMAGENAME = "aren_fire.png"
    FRAMES = (0,1,2,3,4,5,6,7,8)
    DISPEL = {END_COMBAT, }

    def get_cover(self, vmode):
        return 5

    def get_invocation(self, myscene):
        return pbge.effects.Invocation(
            fx=DoDamage(
                1, 6, anim=BurnAnim, scale=myscene.scale, is_brutal=True,
                children=[SceneryChewing(random.randint(1,20), scale=myscene.scale)]
            ), area=pbge.scenes.targetarea.SingleTarget(),
        )


class SmokeAreaEnchantment(pbge.scenes.areaenchant.AreaEnchantment):
    AREA_ENCHANTMENT_TYPE = "Smoke"
    IMAGENAME = "aren_smoke.png"
    FRAMES = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
    DISPEL = {END_COMBAT, }

    def get_cover(self, vmode):
        return 5


# Defense constants
DODGE = 'DODGE'
PARRY = 'PARRY'
BLOCK = 'BLOCK'
INTERCEPT = 'INTERCEPT'


#  *******************
#  ***   AnimObs   ***
#  *******************


class SmallBoom(animobs.AnimOb):
    SPRITE_NAME = 'anim_smallboom.png'
    SPRITE_OFF = ((0, 0), (-7, 0), (-3, 6), (3, 6), (7, 0), (3, -6), (-3, -6))
    DEFAULT_SOUND_FX = "bum-94209.ogg"
    ALLOW_MULTIPLE_SOUND_FX = True

    def __init__(self, sprite=0, pos=(0, 0), loop=0, delay=1, y_off=0):
        super(SmallBoom, self).__init__(sprite_name=self.SPRITE_NAME, pos=pos, start_frame=0, end_frame=7, loop=loop,
                                        ticks_per_frame=1, delay=delay)
        self.x_off, self.y_off = self.SPRITE_OFF[sprite]
        self.y_off += y_off


class NoDamageBoom(SmallBoom):
    SPRITE_NAME = 'anim_nodamage.png'
    DEFAULT_SOUND_FX = "g_whiff_alt_2-81862.ogg"
    ALLOW_MULTIPLE_SOUND_FX = False


class PoisonDamageBoom(SmallBoom):
    SPRITE_NAME = 'anim_poisondamage.png'
    DEFAULT_TRANSPARENCY = True
    DEFAULT_END_FRAME = 15
    DEFAULT_SOUND_FX = "magical_7.ogg"
    ALLOW_MULTIPLE_SOUND_FX = False


class BigBoom(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_bigboom.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_SOUND_FX = "hq-explosion-6288.ogg"


class MiasmaAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_gervais_miasma.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_SOUND_FX = "weird_05.ogg"


class SparkleBlueAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_gervais_sparkle_blue.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_LOOP = 1
    DEFAULT_SOUND_FX = "magical_1.ogg"


class SparkleRedAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_gervais_sparkle_red.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_LOOP = 1
    DEFAULT_SOUND_FX = "magical_1.ogg"


class BonusActionAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_bonusaction.png"
    DEFAULT_END_FRAME = 24
    DEFAULT_SOUND_FX = "upgrade1.ogg"


class SuperBoom(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_frogatto_nuke.png"
    DEFAULT_END_FRAME = 9
    DEFAULT_SOUND_FX = "rock_breaking.ogg"


class SmokePoof(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_smokepoof.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_SOUND_FX = "poof_1.ogg"


class DustCloud(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_dustcloud.png"
    DEFAULT_END_FRAME = 7


class BurnAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_burning.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_SOUND_FX = "foom_0.ogg"


class Fireball(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_fireball.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_SOUND_FX = "foom_0.ogg"


class DisintegrationAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_disintegration.png"
    DEFAULT_END_FRAME = 15


class DeathWaveAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_deathwave.png"
    DEFAULT_END_FRAME = 15


class InvokeDeathWaveAnim(animobs.Caption):
    DEFAULT_TEXT = 'Death Wave!'


class HaywireAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_haywire.png"
    DEFAULT_END_FRAME = 19
    DEFAULT_SOUND_FX = "qubodupElectricityDamage02.ogg"


class OverloadAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_overload.png"
    DEFAULT_END_FRAME = 15
    DEFAULT_SOUND_FX = "UI_Electric_00.ogg"


class RepairAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_repair.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_LOOP = 4
    DEFAULT_SOUND_FX = "magical_1.ogg"


class MedicineAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_medicine.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_LOOP = 4
    DEFAULT_SOUND_FX = "magical_1.ogg"


class BiotechnologyAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_biotechnology.png"
    DEFAULT_END_FRAME = 7
    DEFAULT_LOOP = 4
    DEFAULT_SOUND_FX = "magical_1.ogg"


class SearchAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = 'anim_scouting_search.png'
    DEFAULT_END_FRAME = 7


class DeepProbeAnim(animobs.Caption):
    DEFAULT_TEXT = 'Deep Probe!'


class SensorLockAnim(animobs.Caption):
    DEFAULT_TEXT = 'Sensor Lock!'


class MissAnim(animobs.Caption):
    DEFAULT_TEXT = 'Miss!'


class BlockAnim(animobs.Caption):
    DEFAULT_TEXT = 'Block!'


class ParryAnim(animobs.Caption):
    DEFAULT_TEXT = 'Parry!'


class InterceptAnim(animobs.Caption):
    DEFAULT_TEXT = 'Intercept!'


class FailAnim(animobs.Caption):
    DEFAULT_TEXT = 'Fail!'


class ReloadAnim(animobs.Caption):
    DEFAULT_TEXT = 'Reload'
    DEFAULT_SOUND_FX = "reload.ogg"


class ResistAnim(animobs.Caption):
    DEFAULT_TEXT = "Resist!"


class SearchTextAnim(animobs.Caption):
    DEFAULT_TEXT = 'Search!'


class InflictDisintegrationAnim(animobs.Caption):
    DEFAULT_TEXT = 'Disintegrating!'


class InflictHaywireAnim(animobs.Caption):
    DEFAULT_TEXT = 'Haywire!'
    DEFAULT_SOUND_FX = "qubodupElectricityDamage02.ogg"


class InflictPoisonAnim(animobs.Caption):
    DEFAULT_TEXT = 'Poisoned!'


class AmmoExplosionAnim(animobs.ShotCaption):
    DEFAULT_TEXT = 'Ammo Explosion!'


class AIAssistAnim(animobs.Caption):
    DEFAULT_TEXT = 'AI Assisted!'


class AnnounceCrashAnim(animobs.Caption):
    DEFAULT_TEXT = 'Crashed!'


class AnnounceEjectAnim(animobs.Caption):
    DEFAULT_TEXT = 'Ejected!'


class MusicAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_music.png"
    DEFAULT_END_FRAME = 15


class BadMusicAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_music_bad.png"
    DEFAULT_END_FRAME = 7


class PerformanceAnim(animobs.AnimOb):
    DEFAULT_SPRITE_NAME = "anim_music.png"
    DEFAULT_END_FRAME = 15
    DEFAULT_LOOP = 2

    def render(self, foot_pos, view):
        self.y_off -= 2
        super().render(foot_pos, view)


class HeckleAnim(animobs.Caption):
    HECKLES = ("BOO!"
               , "You suck!"
               , "Eww!"
               , "Epic Fail!"
               , "Worst Attack Ever!"
               )

    def __init__(self, **keywords):
        super().__init__(txt=random.choice(self.HECKLES), **keywords)


class CheerAnim(animobs.Caption):
    CHEERS = ("YEAH!"
              , "Encore!"
              , "Again!"
              , "Whoo!"
              )

    def __init__(self, **keywords):
        super().__init__(txt=random.choice(self.CHEERS), **keywords)


class ListenToMySongAnim(animobs.Caption):
    DEFAULT_TEXT = 'LISTEN TO MY SONG!'
    DEFAULT_COLOR = (224, 192, 255)
    SONG_LYRICS = ('HELLO DARKNESS MY OLD FRIEND!'
                   , 'NEVER GONNA GIVE YOU UP!'
                   , 'ZANKOKU NO TENSHI NO TEZE!'
                   , "WE WILL WE WILL ROCK YOU!"
                   , "LET IT GO!"
                   , "OPPA GANGNAM STYLE!"
                   , 'PEN PINEAPPLE APPLE PEN!'
                   )

    def __init__(self, txt=None, width=256, **keywords):
        if txt is None:
            txt = self.DEFAULT_TEXT
            # Occassionally mess with the player because WHY NOT?
            if random.randint(1, 20) == 1:
                txt = random.choice(self.SONG_LYRICS)
        super().__init__(txt=txt, width=width, **keywords)


class TakeCoverAnim(SmokePoof):
    # TODO: derive from animobs and then fill with its own animation.
    pass


class SmallBullet(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_bullet.png"
    DEFAULT_SOUND_FX = "22-caliber-with-ricochet-39679.ogg"


class BigBullet(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_bigbullet.png"
    DEFAULT_SOUND_FX = "desert-eagle-gunshot-14622.ogg"


class HugeBullet(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_hugebullet.png"
    DEFAULT_SOUND_FX = "cannon-shot-14799.ogg"


class GunBeam(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_gunbeam.png"
    DEFAULT_SOUND_FX = "blaster-2-81267.ogg"


class SmallBeam(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_smallbeam.png"
    DEFAULT_SOUND_FX = "alienshoot1.ogg"


class PlasmaBall(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_shot_plasma.png"
    DEFAULT_SOUND_FX = "Spell1.ogg"


class PlasmaBeam(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_plasmabeam.png"
    DEFAULT_SOUND_FX = "SpellShort.ogg"


class FireBolt(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_shot_fire.png"
    DEFAULT_SOUND_FX = "foom_0.ogg"

class SlashShot(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_slash.png"
    DEFAULT_SOUND_FX = "cqcmelee.ogg"

class BeamSlashShot(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_beamslash.png"
    DEFAULT_SOUND_FX = "cqclaserswordhit.ogg"



# For the v0.900 series; can probably cut after 1.000.
FireBall = FireBolt


class AcidSpray(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_gervais_s_acidspray.png"
    DEFAULT_SOUND_FX = "lava.ogg"


class LightningBolt(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_gervais_s_lightning.png"
    DEFAULT_SOUND_FX = "hjm-tesla_sound_shot.ogg"


class Missile1(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_missile1.png"
    DEFAULT_SPEED = 0.3
    DEFAULT_SOUND_FX = "missile-blast-2-95177.ogg"


class Missile2(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_missile2.png"
    DEFAULT_SPEED = 0.3
    DEFAULT_SOUND_FX = "missile-blast-2-95177.ogg"


class Missile3(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_missile3.png"
    DEFAULT_SPEED = 0.3
    DEFAULT_SOUND_FX = "missile-blast-2-95177.ogg"


class Missile4(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_missile4.png"
    DEFAULT_SPEED = 0.3
    DEFAULT_SOUND_FX = "missile-blast-2-95177.ogg"


class Missile5(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_missile5.png"
    DEFAULT_SPEED = 0.3
    DEFAULT_SOUND_FX = "missile-blast-2-95177.ogg"


class ClusterShot(animobs.ShotAnim):
    # This shotanim is a container which holds a bunch of other shot anims.
    # It's used when a shot consists of more than one anim, for example
    # a large volley of missiles or a particularly long beam blast.
    def __init__(self, start_pos=(0, 0), end_pos=(0, 0), x_off=0, y_off=0, delay=0, child_classes=()):
        self.x_off = x_off
        self.y_off = y_off
        self.needs_deletion = False
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.child_classes = child_classes or self.DEFAULT_CHILD_CLASSES
        self.children = list()
        self.delay = delay

    DEFAULT_CHILD_CLASSES = []

    def update(self, view):
        if self.delay > 0:
            self.delay += -1
        else:
            self.needs_deletion = True
            delay = 0
            original_children = self.children
            self.children = list()
            for cc in self.child_classes:
                self.children.append(cc(start_pos=self.start_pos, end_pos=self.end_pos,
                                        x_off=self.x_off, y_off=self.y_off, delay=delay))
                delay += 3
            #self.children[0].sound_fx_loops = len(self.children)-1
            #for cc in self.children[1:]:
            #    cc.sound_fx = None
            self.children[0].children += original_children


class MissileFactory(object):
    # Used to create custom missile salvos.
    def __init__(self, num_missiles):
        self.num_missiles = min(num_missiles, 40)

    MISSILE_ANIMS = (Missile1, Missile2, Missile3, Missile4, Missile5)

    def __call__(self, start_pos, end_pos, delay=0):
        # Return as many missiles as requested.
        fives, leftover = divmod(self.num_missiles, 5)
        my_anim = list()
        if fives > 0:
            my_anim += [Missile5, ] * fives
        if leftover > 0:
            my_anim.append(self.MISSILE_ANIMS[leftover - 1])
        return ClusterShot(start_pos=start_pos, end_pos=end_pos, delay=delay, child_classes=my_anim)


class BulletFactory(object):
    # Used to create custom missile salvos.
    def __init__(self, num_bullets, proto_bullet):
        self.num_bullets = num_bullets
        self.proto_bullet = proto_bullet

    def __call__(self, start_pos, end_pos, delay=0):
        # Return as many missiles as requested.
        my_anim = [self.proto_bullet, ] * self.num_bullets
        return ClusterShot(start_pos=start_pos, end_pos=end_pos, delay=delay, child_classes=my_anim)


class OriginSpotShotFactory(object):
    # Instead of a shot anim, this factory generates a spot anim.
    def __init__(self, proto_spot):
        self.proto_spot = proto_spot

    def __call__(self, start_pos, end_pos, delay=0):
        # Return the spot anim.
        return self.proto_spot(pos=start_pos, delay=delay)


# A shot animation that also animates a return.
class ReturnAnim(animobs.AnimOb):
    BASE_ANIM = SmallBullet
    REVERSE_ON_RETURN = False

    def __init__(self, start_pos, end_pos, delay=0):
        self.going = self.BASE_ANIM(start_pos=start_pos, end_pos=end_pos, delay=0)
        self.returning = self.BASE_ANIM(start_pos=end_pos, end_pos=start_pos, delay=0,
                                        reverse_direction=self.REVERSE_ON_RETURN)
        self.children = list()
        self.delay = delay
        self.needs_deletion = False

    def update(self, view):
        if self.delay > 0:
            self.delay -= 1
        elif self.going:
            self.going.update(view)
            if self.going.needs_deletion:
                self.going = None
                self.children.append(self.returning)
                self.needs_deletion = True

    def render(self, foot_pos, view):
        if self.delay > 0:
            return
        elif self.going:
            self.going.render(foot_pos, view)


class AnimBox(animobs.AnimOb):
    # This anim does nothing but release other anims into the wild.
    def __init__(self, child_anims, delay=0):
        """
        :type child_anims: list
        :type delay: int
        """
        self.child_anims = child_anims
        self.children = list()
        self.delay = delay
        self.needs_deletion = False

    def update(self, view):
        if self.delay > 0:
            self.delay += -1
        else:
            self.needs_deletion = True
            original_children = self.children
            self.children = list(self.child_anims)
            self.children[0].children += original_children


class DashFactory(object):
    # Instead of a shot anim, this factory generates a dash anim.
    def __init__(self, dasher):
        self.dasher = dasher

    def __call__(self, start_pos, end_pos, delay=0):
        # Return the spot anim.
        mydash = animobs.Dash(self.dasher, end_pos=end_pos, delay=delay)
        mydust = DustCloud(pos=self.dasher.pos, delay=2, sound_fx="swoosh.ogg")
        return AnimBox([mydash, mydust])


class FlyingHammer(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_hammer.png"
    DEFAULT_SOUND_FX = "swoosh.ogg"


class ReturningHammer(ReturnAnim):
    BASE_ANIM = FlyingHammer


class FlyingDeathwing(animobs.AnimatedShotAnim):
    DEFAULT_SPRITE_NAME = "anim_shot_deathwing.png"
    DEFAULT_END_FRAME = 2
    DEFAULT_LOOP = 99999
    DEFAULT_SOUND_FX = "whipy-woosh.ogg"


class ReturningDeathwing(ReturnAnim):
    BASE_ANIM = FlyingDeathwing


class ChainClawShot(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_s_chainclaw.png"


class ReturningChainClaw(ReturnAnim):
    BASE_ANIM = ChainClawShot
    REVERSE_ON_RETURN = True


class JawShot(animobs.ShotAnim):
    DEFAULT_SPRITE_NAME = "anim_jaws.png"
    DEFAULT_SPEED = 0.3

    def __init__(self, start_pos, end_pos, delay=1):
        super().__init__(start_pos=start_pos, end_pos=end_pos, set_frame_offset=False, delay=delay)
        self.children.append(
            animobs.ShotAnim(sprite_name=self.DEFAULT_SPRITE_NAME, frame=1, delay=0, speed=self.DEFAULT_SPEED,
                             start_pos=end_pos, end_pos=start_pos, set_frame_offset=False)
        )


class CrashAnim(object):
    # The model will fall down. At the end of the anim, set the model's movemeode to Crashed
    def __init__(self, model, delay=0, final_altitude=0):
        self.model = model
        self.delay = delay
        self.step = 0
        self.speed = 1
        self.drop = 0
        self.final_altitude = final_altitude
        self.needs_deletion = False
        self.children = list()

    def model_altitude(self, view):
        return view.scene.model_altitude(self.model, *self.model.pos) - self.drop

    def update(self, view):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.model_altitude(view) > self.final_altitude:
            self.step += 1
            self.drop += self.speed
            # if self.step % 2 == 0:
            self.speed += 1
            if self.model_altitude(view) < self.final_altitude:
                self.drop = abs(self.final_altitude - view.scene.model_altitude(self.model, *self.model.pos))
            self.model.offset_pos = (0, self.drop)
        else:
            self.model.mmode = tags.Crashed
            self.model.offset_pos = (0, 0)
            self.needs_deletion = True


class JumpModel(object):
    def __init__(self, scene, model, start=None, dest=(0, 0), speed=0.4, delay=0, zenith=50):
        self.model = model
        self.speed = speed
        self.dest = dest
        self.delay = delay
        self.step = 0.0
        self.needs_deletion = False
        self.children = list()
        if not start:
            start = model.pos
        self.itinerary = pbge.scenes.animobs.get_fline(start, dest, speed)
        self.num_steps = float(len(self.itinerary))
        self.zenith = zenith

        self.start_alt = scene.model_altitude(model, *model.pos)
        self.final_alt = scene.model_altitude(model, *dest)

    def update(self, view):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.itinerary:
            self.step += 1.0
            px = self.step / self.num_steps
            py = -4 * px * px + 4 * px
            if self.step < self.num_steps / 2:
                y_off = int((self.zenith - self.start_alt) * py)
            else:
                y_off = int((self.zenith - self.final_alt) * py) - self.start_alt
            self.model.pos = self.itinerary.pop(0)
            self.model.offset_pos = (0, -y_off)
            if not self.itinerary:
                self.needs_deletion = True
                self.model.pos = self.dest
                self.model.offset_pos = (0, 0)
        else:
            self.needs_deletion = True
            self.model.pos = self.dest
            self.model.offset_pos = (0, 0)


# A curated list for the gear editor.
SHOT_ANIMS = (SmallBullet, BigBullet, HugeBullet, SmallBeam, GunBeam, Missile1, Missile2, Missile3, Missile4, Missile5,
              ReturningHammer, JawShot, FlyingDeathwing, AcidSpray, LightningBolt, FireBolt, SlashShot, BeamSlashShot)
AREA_ANIMS = (
    BigBoom, SuperBoom, SmallBoom, NoDamageBoom, SmokePoof, DustCloud, Fireball, BurnAnim, HaywireAnim, OverloadAnim)


#  *******************
#  ***   Effects   ***
#  *******************

class AttackRoll(effects.NoEffect):
    """ One actor is gonna attack another actor.
        This may be opposed by a succession of defensive rolls.
        If a defensive roll beats the attack roll, its children get returned.
        Otherwise, the penetration score is recorded in the fx_record and
        the children of this effect get returned.
    """

    def __init__(self, att_stat, att_skill, children=(), anim=None, accuracy=0, penetration=0, modifiers=(),
                 defenses=(), can_crit=True, terrain_effects=()):
        self.att_stat = att_stat
        self.att_skill = att_skill
        self.children = list(children)
        self.anim = anim
        self.accuracy = accuracy
        self.penetration = penetration
        self.modifiers = modifiers
        self.defenses = defenses
        self.can_crit = can_crit
        self.terrain_effects = list(terrain_effects)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat, self.att_skill)
        else:
            att_bonus = random.randint(1, 100)
        att_roll = random.randint(1, 100)

        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp, originator, pos)

        targets = camp.scene.get_operational_actors(pos)
        next_fx = []
        for target in targets:
            hi_def_roll = 50
            for defense in list(self.defenses.values()):
                if defense and defense.can_attempt(originator, target):
                    next_fx, def_roll = defense.make_roll(self, originator, target, att_bonus, att_roll, fx_record)
                    hi_def_roll = max(def_roll, hi_def_roll)
                    if next_fx:
                        break
            penetration = att_roll + att_bonus + self.penetration - hi_def_roll
            if hasattr(target, 'ench_list'):
                penetration += target.ench_list.get_funval(target, 'get_penetration_bonus')
            fx_record[FX_PENETRATION] = penetration

            if camp.fight:
                camp.fight.cstat[target].attacks_this_round += 1

            if originator and not next_fx and self.can_crit:
                critval = min(att_roll + att_bonus - hi_def_roll - 25, 50)
                if critval > 0:
                    max_crit = min(max((originator.get_stat(self.att_skill)-4) * 3, 5), 30)
                    dmg = max((max_crit * critval)//50, 1)
                    fx_record[FX_DAMAGE_BONUS] = dmg
                    if dmg > 3:
                        fx_record[FX_CRITICAL_HIT] = True


        if not next_fx and originator and hasattr(originator, "dole_experience"):
            originator.dole_experience(3, self.att_skill)

        return list(next_fx or self.children) + self.terrain_effects

    def get_odds(self, camp, originator, target):
        # Return the percent chance that this attack will hit and the list of
        # modifiers in (value,name) form.
        modifiers = list()
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat, self.att_skill)
        else:
            att_bonus = 50
        for m in self.modifiers:
            mval = m.calc_modifier(camp, originator, target.pos)
            att_bonus += mval
            if mval != 0:
                modifiers.append((mval, m.name))
        odds = 1.0
        for defense in list(self.defenses.values()):
            if defense and defense.can_attempt(originator, target):
                odds *= defense.get_odds(self, originator, target, att_bonus)
        return odds, modifiers


class MeleeAttackRoll(AttackRoll):
    def __init__(self, att_stat, att_skill, bonus_strikes=0, **kwargs):
        super().__init__(att_stat, att_skill, **kwargs)
        self.bonus_strikes = bonus_strikes

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat, self.att_skill)
            max_attacks = 1 + max(
                (originator.get_stat(stats.Speed) + originator.get_stat(self.att_skill) * 3) // 12 - 2, 0)
        else:
            att_bonus = random.randint(1, 100)
            max_attacks = 3
        att_roll = random.randint(1, 100)

        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp, originator, pos)

        targets = camp.scene.get_operational_actors(pos)
        next_fx = []
        for target in targets:
            hi_def_roll = 50
            failed = False
            for defense in list(self.defenses.values()):
                if defense and defense.can_attempt(originator, target):
                    next_fx, def_roll = defense.make_roll(self, originator, target, att_bonus, att_roll, fx_record)
                    hi_def_roll = max(def_roll, hi_def_roll)
                    if next_fx:
                        failed = True
                        break
            penetration = att_roll + att_bonus + self.penetration - hi_def_roll
            if hasattr(target, 'ench_list'):
                penetration += target.ench_list.get_funval(target, 'get_penetration_bonus')
            fx_record[FX_PENETRATION] = penetration

            if not failed:
                if originator and hasattr(originator, "dole_experience"):
                    originator.dole_experience(3, self.att_skill)

                num_hits = min(max((att_roll + att_bonus - hi_def_roll - 10) // 25, 0) + 1, max_attacks)

                # Add bonus strikes.
                if self.bonus_strikes > 0:
                    num_hits += random.randint(0, self.bonus_strikes)

                fx_record['number_of_hits'] = num_hits
                if num_hits > 1:
                    anims.append(animobs.Caption('x{}'.format(num_hits), pos=pos, delay=delay,
                                                 y_off=camp.scene.model_altitude(target, pos[0], pos[1]) - 15))

            if camp.fight:
                camp.fight.cstat[target].attacks_this_round += 1

        return list(next_fx or self.children) + self.terrain_effects


class MultiAttackRoll(effects.NoEffect):
    """ One actor is gonna attack another actor.
        This may be opposed by a succession of defensive rolls.
        If a defensive roll beats the attack roll, its children get returned.
        Otherwise, the penetration score is recorded in the fx_record and
        the children of this effect get returned.
    """

    def __init__(self, att_stat, att_skill, num_attacks=2, children=(), anim=None, accuracy=0, penetration=0,
                 modifiers=(), defenses=(), overwhelm=0, apply_hit_modifier=True, terrain_effects=()):
        self.att_stat = att_stat
        self.att_skill = att_skill
        self.num_attacks = num_attacks
        self.children = list(children)
        self.anim = anim
        self.accuracy = accuracy
        self.penetration = penetration
        self.modifiers = modifiers
        self.defenses = defenses
        self.overwhelm = overwhelm
        self.apply_hit_modifier = apply_hit_modifier
        self.terrain_effects = list(terrain_effects)

    def get_multi_bonus(self):
        # Launching multiple attacks results in a bonus to hit. Of course,
        # not all of these attacks are likely to hit.
        return min(self.num_attacks, 10) * 2

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat, self.att_skill)
            if self.apply_hit_modifier:
                att_bonus += self.get_multi_bonus()
        else:
            att_bonus = random.randint(1, 100)
        att_roll = random.randint(1, 100)

        for m in self.modifiers:
            att_bonus += m.calc_modifier(camp, originator, pos)

        targets = camp.scene.get_operational_actors(pos)
        next_fx = []
        for target in targets:
            hi_def_roll = 50
            failed = False
            for defense in list(self.defenses.values()):
                if defense and defense.can_attempt(originator, target):
                    next_fx, def_roll = defense.make_roll(self, originator, target, att_bonus, att_roll, fx_record)
                    hi_def_roll = max(def_roll, hi_def_roll)
                    if next_fx:
                        failed = True
                        break
            penetration = att_roll + att_bonus + self.penetration - hi_def_roll
            if self.apply_hit_modifier:
                penetration -= self.get_multi_bonus()
            if hasattr(target, 'ench_list'):
                penetration += target.ench_list.get_funval(target, 'get_penetration_bonus')
            fx_record[FX_PENETRATION] = penetration

            if failed:
                if self.overwhelm > 0:
                    target.spend_stamina(random.randint(0, self.overwhelm))
            else:
                if originator and hasattr(originator, "dole_experience"):
                    originator.dole_experience(3, self.att_skill)
                if self.num_attacks <= 10:
                    num_hits = max(int(min(min(att_roll + att_bonus - hi_def_roll, 45) // 5 + 1, self.num_attacks)), 1)
                else:
                    num_hits = max(int(max((min(att_roll + att_bonus - hi_def_roll, 50) * self.num_attacks) // 50, 1)),
                                   1)
                fx_record['number_of_hits'] = num_hits
                anims.append(animobs.Caption('x{}'.format(num_hits), pos=pos, delay=delay,
                                             y_off=camp.scene.model_altitude(target, pos[0], pos[1]) - 15))
                if self.overwhelm > 2:
                    target.spend_stamina(random.randint(0, self.overwhelm // 3))

            if camp.fight:
                camp.fight.cstat[target].attacks_this_round += 1 + random.randint(0, self.overwhelm) // 5

        return list(next_fx or self.children) + self.terrain_effects

    def get_odds(self, camp, originator, target):
        # Return the percent chance that this attack will hit and the modifiers.
        modifiers = list()
        if self.apply_hit_modifier:
            modifiers.append((self.get_multi_bonus(), 'Multi-attack'))
        if originator:
            att_bonus = originator.get_skill_score(self.att_stat, self.att_skill) + self.get_multi_bonus()
        else:
            att_bonus = 50 + self.get_multi_bonus()
        for m in self.modifiers:
            mval = m.calc_modifier(camp, originator, target.pos)
            att_bonus += mval
            if mval != 0:
                modifiers.append((mval, m.name))
        odds = 1.0
        for defense in list(self.defenses.values()):
            if defense and defense.can_attempt(originator, target):
                odds *= defense.get_odds(self, originator, target, att_bonus)
        return odds, modifiers


class SkillRoll(effects.NoEffect):
    """ A single actor makes a skill roll unopposed.
    """

    def __init__(self, stat, skill, on_success=(), on_failure=(), anim=None, roll_mod=0, min_chance=5, max_chance=95):
        self.stat = stat
        self.skill = skill
        self.on_success = list(on_success)
        self.on_failure = list(on_failure)
        self.anim = anim
        self.roll_mod = roll_mod
        self.min_chance = min_chance
        self.max_chance = max_chance

    def _calc_percent(self, camp, originator):
        if originator:
            percent = originator.get_skill_score(self.stat, self.skill) + self.roll_mod
        else:
            percent = self.roll_mod
        return max(min(percent, self.max_chance), self.min_chance)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        odds = self._calc_percent(camp, originator)
        if random.randint(1, 100) <= odds:
            if originator and hasattr(originator, "dole_experience"):
                originator.dole_experience(max((75 - odds) // 5, 2), self.skill)
            return self.on_success
        else:
            return self.on_failure

    def get_odds(self, camp, originator, target):
        # Return the percent chance that this attack will hit and the list of
        # modifiers in (value,name) form.
        modifiers = [(self.roll_mod, 'Base Modifier')]
        return self._calc_percent(camp, originator) / 100.0, modifiers


class OpposedSkillRoll(effects.NoEffect):
    """ Two actors make a skill roll. One will succeed, one will fail.
    """

    def __init__(self, att_stat, att_skill, def_stat, def_skill, on_success=(), on_failure=(), on_no_target=(),
                 anim=None, roll_mod=0, min_chance=5, max_chance=95):
        self.att_stat = att_stat
        self.att_skill = att_skill
        self.def_stat = def_stat
        self.def_skill = def_skill
        if not on_success:
            on_success = list()
        self.on_success = list(on_success)
        if not on_failure:
            on_failure = list()
        self.on_failure = list(on_failure)
        if not on_no_target:
            on_no_target = list()
        self.on_no_target = list(on_no_target)
        self.anim = anim
        self.roll_mod = roll_mod
        self.min_chance = min_chance
        self.max_chance = max_chance

    def _calc_percent(self, camp, originator, target):
        if originator:
            percent = originator.get_skill_score(self.att_stat, self.att_skill) + self.roll_mod
        else:
            percent = self.roll_mod
        if target:
            percent -= target.get_skill_score(self.def_stat, self.def_skill)
        return max(min(percent, self.max_chance), self.min_chance)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        target = camp.scene.get_main_actor(pos)
        if target:
            odds = self._calc_percent(camp, originator, target)
            if random.randint(1, 100) <= odds:
                if originator and hasattr(originator, "dole_experience"):
                    originator.dole_experience(max((75 - odds) // 5, 2), self.att_skill)
                return self.on_success
            else:
                if hasattr(target, "dole_experience"):
                    target.dole_experience(max((odds - 25) // 5, 2), self.def_skill)
                return self.on_failure
        else:
            return self.on_no_target

    def get_odds(self, camp, originator, target):
        # Return the percent chance that this attack will hit and the list of
        # modifiers in (value,name) form.
        modifiers = [(self.roll_mod, 'Base Modifier')]
        return self._calc_percent(camp, originator, target) / 100.0, modifiers


class ResistanceRoll(effects.NoEffect):
    """ Two actors make a skill roll based on defense skill. One will succeed, one will fail.
    """

    def __init__(self, att_stat, def_stat, on_success=(), on_failure=(), on_no_target=(), anim=None, roll_mod=0,
                 min_chance=5, max_chance=95):
        self.att_stat = att_stat
        self.def_stat = def_stat
        if on_success:
            self.on_success = list(on_success)
        else:
            self.on_success = list()
        if on_failure:
            self.on_failure = list(on_failure)
        else:
            self.on_failure = list()
        if on_no_target:
            self.on_no_target = list(on_no_target)
        else:
            self.on_no_target = list()
        self.anim = anim
        self.roll_mod = roll_mod
        self.min_chance = min_chance
        self.max_chance = max_chance

    def _get_dodge_skill(self, npc):
        if hasattr(npc, "DODGE_SKILL"):
            return npc.DODGE_SKILL
        else:
            return stats.Concentration

    def _calc_percent(self, camp, originator, target):
        if originator:
            percent = originator.get_skill_score(self.att_stat, self._get_dodge_skill(originator)) + self.roll_mod
        else:
            percent = self.roll_mod
        if target:
            percent -= target.get_skill_score(self.def_stat, self._get_dodge_skill(target))
        return max(min(percent, self.max_chance), self.min_chance)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        target = camp.scene.get_main_actor(pos)
        if target:
            odds = self._calc_percent(camp, originator, target)
            if random.randint(1, 100) <= odds:
                if originator and hasattr(originator, "dole_experience"):
                    originator.dole_experience(max((75 - odds) // 5, 2), self._get_dodge_skill(originator))
                return self.on_success
            else:
                if hasattr(target, "dole_experience"):
                    target.dole_experience(max((odds - 25) // 5, 2), self._get_dodge_skill(target))
                return self.on_failure
        else:
            return self.on_no_target

    def get_odds(self, camp, originator, target):
        # Return the percent chance that this attack will hit and the list of
        # modifiers in (value,name) form.
        modifiers = [(self.roll_mod, 'Base Modifier')]
        return self._calc_percent(camp, originator, target) / 100.0, modifiers


class CheckConditions(effects.NoEffect):
    """ This tile will be checked for something.
        conditions is a list of conditions in the same format as the aitargeter conditions;
        each condition is a callable that takes (camp,originator,target)
    """

    def __init__(self, conditions, on_success=(), on_failure=(), anim=None):
        self.conditions = conditions
        if not on_success:
            on_success = list()
        self.on_success = list(on_success)
        if not on_failure:
            on_failure = list()
        self.on_failure = list(on_failure)
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        target = camp.scene.get_main_actor(pos)
        if all(con(camp, originator, target) for con in self.conditions):
            return self.on_success
        else:
            return self.on_failure


class StealthSkillRoll(effects.NoEffect):
    """ The originator makes a skill roll against the highest enemy in range.
    """

    def __init__(self, att_stat=None, att_skill=None, def_stat=None, def_skill=None, on_success=(), on_failure=(),
                 radius=15, anim=None, roll_mod=50, min_chance=5, max_chance=95):
        self.att_stat = att_stat or stats.Speed
        self.att_skill = att_skill or stats.Stealth
        self.def_stat = def_stat or stats.Perception
        self.def_skill = def_skill or stats.Scouting
        if not on_success:
            on_success = list()
        self.on_success = list(on_success)
        if not on_failure:
            on_failure = list()
        self.on_failure = list(on_failure)
        self.anim = anim
        self.roll_mod = roll_mod
        self.min_chance = min_chance
        self.max_chance = max_chance
        self.radius = radius

    def _calc_percent(self, camp, originator, pos):
        if originator:
            percent = originator.get_skill_score(self.att_stat, self.att_skill) + self.roll_mod
        else:
            percent = self.roll_mod
        observation_area = pfov.PointOfView(camp.scene, pos[0], pos[1], self.radius).tiles
        enemy_skills = [npc.get_skill_score(self.def_stat, self.def_skill) for npc in
                        camp.scene.get_operational_actors() if
                        camp.scene.are_hostile(originator, npc) and npc.pos in observation_area]
        if enemy_skills:
            percent -= max(enemy_skills)
        return max(min(percent, self.max_chance), self.min_chance)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        odds = self._calc_percent(camp, originator, pos)
        if random.randint(1, 100) <= odds:
            if originator and hasattr(originator, "dole_experience"):
                originator.dole_experience(max((75 - odds) // 5, 2), self.att_skill)
            return self.on_success
        else:
            return self.on_failure


class DoDamage(effects.NoEffect):
    """ Whatever is in this tile is going to take damage.
    """
    DESTROY_TARGET_XP = 45
    MAX_DESTROY_TARGET_XP = 100

    def __init__(self, damage_n, damage_d, children=(), anim=None, scale=None, hot_knife=False, scatter=False,
                 damage_bonus=0, is_brutal=False, can_be_divided=True, affected_by_armor=True):
        self.damage_n = damage_n
        self.damage_d = damage_d
        self.damage_bonus = damage_bonus
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim
        self.scale = scale
        self.hot_knife = hot_knife
        self.is_brutal = is_brutal
        self.scatter = scatter
        self.can_be_divided = can_be_divided
        self.affected_by_armor = affected_by_armor

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        targets = camp.scene.get_operational_actors(pos)
        penetration = fx_record.get(FX_PENETRATION, random.randint(1, 100))
        damage_percent = fx_record.get("damage_percent", 100)
        number_of_hits = fx_record.get("number_of_hits", 1)
        for target in targets:
            scale = self.scale or target.scale

            if self.scatter:
                raw_damage = sum(
                    [max(sum(random.randint(1, self.damage_d) for n in range(self.damage_n)) + self.damage_bonus +
                         fx_record.get(FX_DAMAGE_BONUS, 0), 1) for
                     t in range(number_of_hits)])
                hits = list()
                while raw_damage > 0:
                    myhit = random.randint(1, 4)
                    raw_damage -= myhit
                    hits.append(max(scale.scale_health(myhit, materials.DamageMat) * damage_percent // 100, 1))
            else:
                hits = [max(int(scale.scale_health(
                    max(sum(random.randint(1, self.damage_d) for n in range(self.damage_n)) + self.damage_bonus +
                        fx_record.get(FX_DAMAGE_BONUS, 0), 1),
                    materials.DamageMat) * damage_percent // 100), 1) for t in range(number_of_hits)]
            mydamage = damage.Damage(
                camp, hits, penetration, target, anims, hot_knife=self.hot_knife,
                is_brutal=self.is_brutal,
                can_be_divided=self.can_be_divided, affected_by_armor=self.affected_by_armor,
                critical_hit=fx_record.get(FX_CRITICAL_HIT, False)
            )
            # Hidden targets struck by an attack get revealed.
            myanim = animobs.RevealModel(target, delay=delay)
            anims.append(myanim)

            # If the target is destroyed, give experience to the originator.
            if originator and hasattr(originator, "dole_experience") and camp.scene.are_hostile(originator, target):
                if mydamage.operational_at_start and not target.is_operational():
                    xp = min(
                        max(self.DESTROY_TARGET_XP * target.battle_cost() * target.scale.XP_MULTIPLIER // originator.battle_cost(),
                            10), self.MAX_DESTROY_TARGET_XP)
                    originator.dole_experience(xp)
                elif mydamage.damage_done > 0:
                    originator.dole_experience(3)
                else:
                    originator.dole_experience(1)
            if camp.fight:
                camp.fight.activate_foe(target)

        return self.children


class SceneryChewing(effects.NoEffect):
    def __init__(self, power, anim=None, children=(), scale=None):
        self.power = power
        self.children = list(children)
        self.anim = anim
        self.scale = scale

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if self.scale is camp.scene.scale and self.power > 0:
            terrain_was_broken = False
            myterrain = camp.scene.get_floor(*pos)
            if myterrain and hasattr(myterrain, "breaker") and myterrain.breaker:
                if myterrain.breaker.deal_with_damage(
                    anims, camp.scene, pos, self.power,
                    pbge.scenes.animobs.SetFloorAnim
                ):
                    terrain_was_broken = True
            myterrain = camp.scene.get_wall(*pos)
            if myterrain and hasattr(myterrain, "breaker") and myterrain.breaker:
                if myterrain.breaker.deal_with_damage(
                    anims, camp.scene, pos, self.power, 
                    pbge.scenes.animobs.SetWallAnim
                ):
                    terrain_was_broken = True
            myterrain = camp.scene.get_decor(*pos)
            if myterrain and hasattr(myterrain, "breaker") and myterrain.breaker:
                if myterrain.breaker.deal_with_damage(
                    anims, camp.scene, pos, self.power, 
                    pbge.scenes.animobs.SetDecorAnim
                ):
                    terrain_was_broken = True
            if terrain_was_broken:
                if random.randint(1,2) == 1:
                    anims.append(animobs.AddAreaEnchantment(pos, camp.scene, SmokeAreaEnchantment, duration=3))
                if random.randint(1,3) == 1 and camp.scene.tile_is_flammable(*pos):
                    anims.append(animobs.AddAreaEnchantment(pos, camp.scene, FireAreaEnchantment))

        #anims.append(animobs.AddAreaEnchantment(pos, camp.scene, SmokeAreaEnchantment, duration=1))
        return self.children


class DoCrash(effects.NoEffect):
    """ Whatever is in this tile is going to fall down.
    """

    def __init__(self, children=()):
        super().__init__(children)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        targets = camp.scene.get_operational_actors(pos)
        for t in targets:
            if hasattr(t, "mmode"):
                anims.append(AnnounceCrashAnim(pos=pos, delay=delay))
                final_altitude = camp.scene.tile_altitude(*t.pos)
                anims.append(CrashAnim(t, delay, final_altitude))

                if camp.fight:
                    camp.fight.cstat[t].spend_ap(1)

        return self.children


class DoHealing(effects.NoEffect):
    """ Whatever is in this tile is going to get healed. Maybe.
    """

    def __init__(self, damage_n, damage_d, children=(), anim=None, scale=None, repair_type=materials.RT_REPAIR):
        self.damage_n = damage_n
        self.damage_d = damage_d
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim
        self.scale = scale
        self.repair_type = repair_type

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        targets = camp.scene.get_operational_actors(pos)
        for target in targets:
            scale = self.scale or target.scale
            damaged_parts = [part for part in target.get_all_parts() if hasattr(part,
                                                                                "hp_damage") and part.hp_damage > 0 and part.material.repair_type == self.repair_type]
            hp_to_restore = max(scale.scale_health(
                sum(random.randint(1, self.damage_d) for n in range(self.damage_n)),
                materials.DamageMat) // 2, 1)
            hp_restored = 0
            while damaged_parts and hp_restored < hp_to_restore:
                part = random.choice(damaged_parts)
                part.hp_damage -= 1
                hp_restored += 1
                if part.hp_damage < 1:
                    damaged_parts.remove(part)
            myanim = animobs.Caption(str(hp_restored),
                                     pos=target.pos, delay=delay,
                                     y_off=-camp.scene.model_altitude(target, *target.pos))
            anims.append(myanim)

            if originator and hasattr(originator, "dole_experience") and self.repair_type in stats.REPAIR_SKILLS:
                originator.dole_experience(max(hp_restored // (scale.SIZE_FACTOR ** 2), 5),
                                           stats.REPAIR_SKILLS[self.repair_type])

            if hasattr(target, "ench_list"):
                target.ench_list.tidy(self.repair_type)

        return self.children


class RestoreMP(effects.NoEffect):
    """ Restore mental points to the target.
    """
    def __init__(self, roll_n, roll_d, children=(), anim=None):
        self.roll_n = roll_n
        self.roll_d = roll_d
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        targets = camp.scene.get_operational_actors(pos)
        for target in targets:
            tpilot = target.get_pilot()
            if hasattr(tpilot, "mp_spent"):
                roll = sum(random.randint(1, self.roll_d) for n in range(self.roll_n))
                tpilot.mp_spent = max(0, tpilot.mp_spent - roll)
                myanim = animobs.Caption("+{}MP".format(roll)
                                         , pos=target.pos
                                         , delay=delay
                                         , y_off=-camp.scene.model_altitude(target, *target.pos)
                                         )
                anims.append(myanim)

        return self.children


class RestoreSP(effects.NoEffect):
    """ Restore stamina points to the target.
    """
    def __init__(self, roll_n, roll_d, children=(), anim=None):
        self.roll_n = roll_n
        self.roll_d = roll_d
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        targets = camp.scene.get_operational_actors(pos)
        for target in targets:
            tpilot = target.get_pilot()
            if hasattr(tpilot, "sp_spent"):
                roll = sum(random.randint(1, self.roll_d) for n in range(self.roll_n))
                tpilot.sp_spent = max(0, tpilot.sp_spent - roll)
                myanim = animobs.Caption("+{}SP".format(roll)
                                         , pos=target.pos
                                         , delay=delay
                                         , y_off=-camp.scene.model_altitude(target, *target.pos)
                                         )
                anims.append(myanim)

        return self.children


class DoEncourage(effects.NoEffect):
    """Increase the MP of the target based on skill and
    stat of the originator.
    Also checks the compatibility of the originiator and
    the target's personalities.
    """

    def __init__(self, stat, skill, **keywords):
        super().__init__(**keywords)
        self.stat = stat
        self.skill = skill

    def _get_personality_compatibility(self, o_char, t_char):
        if not (isinstance(o_char, base.Character) and isinstance(t_char, base.Character)):
            return 0
        compat = 0
        for p in o_char.personality:
            if p in t_char.personality:
                compat += 1
        return compat

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if originator:
            score = originator.get_skill_score(self.stat, self.skill)
        else:
            score = 0

        o_char = originator.get_pilot()

        for target in camp.scene.get_operational_actors(pos):
            if not hasattr(target, 'partially_restore_mental'):
                continue

            t_char = target.get_pilot()
            if not isinstance(t_char, base.Character):
                continue

            if originator is target:
                # Trying to psych yourself up?  Please.
                to_heal = 0
                if random.randint(1, 100) <= score // 2:
                    to_heal += 1
            else:
                to_heal = 2

                # Negotiation skill gives base MP restoration.
                if random.randint(1, 100) <= score:
                    to_heal += 1
                if random.randint(1, 100) <= score:
                    to_heal += 1

                # Based on how compatible the originator and the
                # target are, give bonus healing.
                compat = self._get_personality_compatibility(o_char, t_char)
                to_heal += random.randint(0, compat)

                # cap to 5.
                to_heal = min(to_heal, 5)

            target.partially_restore_mental(to_heal)
            myanim = animobs.Caption('+{} MP'.format(to_heal),
                                     pos=target.pos,
                                     delay=delay,
                                     y_off=-camp.scene.model_altitude(target, *target.pos))
            anims.append(myanim)

        return super().handle_effect(camp, fx_record, originator, pos, anims, delay, data)


class SetHidden(effects.NoEffect):
    """An effect that hides a model."""

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        """Do whatever is required of effect; return list of child effects."""
        targets = camp.scene.get_operational_actors(pos)
        for target in targets:
            myanim = animobs.HideModel(target, delay=delay)
            anims.append(myanim)
        return self.children


class SetVisible(effects.NoEffect):
    """An effect that reveals a model."""

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        """Do whatever is required of effect; return list of child effects."""
        targets = camp.scene.get_operational_actors(pos)
        for target in targets:
            myanim = animobs.RevealModel(target, delay=delay)
            anims.append(myanim)
        return self.children


class CallAnimalCompanion(effects.NoEffect):
    """ Gonna do the ranger thing and summon a pet.
    """

    def __init__(self, fx_stat, fx_skill, monster_tags, children=(), anim=None):
        self.fx_stat = fx_stat
        self.fx_skill = fx_skill
        self.monster_tags = monster_tags
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if originator:
            threat_bonus = originator.get_skill_score(self.fx_stat, self.fx_skill) + 10
        else:
            originator = camp.pc
            threat_bonus = random.randint(1, max(camp.pc.rank, 15))
        threat_bonus += random.randint(1, 20)
        candidates = list()
        for mon in MONSTER_LIST:
            if mon.can_be_pet and camp.pc_suits_map(mon, camp.scene.scale, camp.scene.environment):
                candidates += [mon, ] * len(mon.type_tags.intersection(self.monster_tags))
        if candidates:
            if len(candidates) > 10:
                candidates = random.sample(candidates, len(candidates) // 2)
            candidates.sort(key=lambda m: -m.threat)
            n = min(5, len(candidates))
            nupet = copy.deepcopy(random.choice(candidates[:n]))
            nupet.pet_data = pets.PetData(originator)
            camp.party.append(nupet)
            camp.activate_pet(nupet)
            anims.append(pbge.scenes.animobs.Caption(str(nupet), pos=nupet.pos, delay=delay))
        else:
            anims.append(pbge.scenes.animobs.Caption("Failed!", pos=pos, delay=delay))
        return self.children


class IfEnchantmentOK(effects.NoEffect):
    """
    Go to either on_success or on_failure depending on whether the target can be affected.
    """

    def __init__(self, enchant_type, on_success=(), on_failure=(), anim=None):
        self.enchant_type = enchant_type
        self.on_success = list(on_success)
        self.on_failure = list(on_failure)
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        target = camp.scene.get_main_actor(pos)
        if target and hasattr(target, 'ench_list') and self.enchant_type.can_affect(target):
            return self.on_success
        else:
            return self.on_failure


class AddEnchantment(effects.NoEffect):
    """ Apply an enchantment to the actor in this tile.
    """

    def __init__(self, enchant_type, enchant_params=None, dur_n=None, dur_d=None, children=(), anim=None):
        self.enchant_type = enchant_type
        self.enchant_params = dict()
        if enchant_params:
            self.enchant_params.update(enchant_params)
        self.dur_n = dur_n
        self.dur_d = dur_d
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        target = camp.scene.get_main_actor(pos)
        if target and hasattr(target, 'ench_list') and self.enchant_type.can_affect(target):
            params = self.enchant_params.copy()
            if self.dur_n and self.dur_d:
                params['duration'] = sum(random.randint(1, self.dur_d) for n in range(self.dur_n))
            target.ench_list.add_enchantment(target, self.enchant_type, params)
            # Adding a particular enchantment can dispel other enchantments.
            target.ench_list.tidy(self.enchant_type)
        return self.children


class RandomEffect(effects.NoEffect):
    """ Randomly applies one of the given effects.
    """

    def __init__(self, possible_fx, **keywords):
        super().__init__(**keywords)
        self.possible_fx = possible_fx

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        return [random.choice(self.possible_fx)] + self.children


class DispelEnchantments(effects.NoEffect):
    """ Trigger dispelling enchantments with a specific dispel type.
    Usually used with enchantments.ON_DISPEL_NEGATIVE or
    enchantments.ON_DISPEL_POSITIVE.
    """

    def __init__(self, dispel_this=None, **keywords):
        super().__init__(**keywords)
        self.dispel_this = dispel_this or ON_DISPEL_NEGATIVE

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        camp.scene.tidy_enchantments(self.dispel_this, pos)
        return super().handle_effect(camp, fx_record, originator, pos, anims, delay, data)


class DoDrainPower(effects.NoEffect):
    """ Drain the power of the target.
    """

    def __init__(self, **keywords):
        super().__init__(**keywords)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        for target in camp.scene.get_operational_actors(pos):
            if not hasattr(target, 'get_current_and_max_power'):
                continue
            if not hasattr(target, 'consume_power'):
                continue
            c, m = target.get_current_and_max_power()
            if c <= 0:
                continue
            # Determine the limit.
            if random.randint(1, 2) == 1:
                limit = c
            else:
                limit = max(1, c // 2)
            drain = random.randint(1, limit)
            target.consume_power(drain)
            myanim = animobs.Caption("-{}Pw".format(drain)
                                     , pos=target.pos
                                     , delay=delay
                                     , y_off=-camp.scene.model_altitude(target, *target.pos)
                                     )
            anims.append(myanim)
        return super().handle_effect(camp, fx_record, originator, pos, anims, delay, data)


class DoDrainStamina(effects.NoEffect):
    """ Drain the stamina of the target.
    """

    def __init__(self, drain_n=1, drain_d=6, **keywords):
        self.drain_n = drain_n
        self.drain_d = drain_d
        super().__init__(**keywords)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        for target in camp.scene.get_operational_actors(pos):
            if not hasattr(target, 'spend_stamina'):
                continue
            elif target.get_current_stamina() < 1:
                continue

            drain = min(sum(random.randint(1, self.drain_d) for n in range(self.drain_n)), target.get_current_stamina())

            target.spend_stamina(drain)
            myanim = animobs.Caption("-{}SP".format(drain)
                                     , pos=target.pos
                                     , delay=delay
                                     , y_off=-camp.scene.model_altitude(target, *target.pos)
                                     )
            anims.append(myanim)
        return super().handle_effect(camp, fx_record, originator, pos, anims, delay, data)


class DoReload(effects.NoEffect):
    """ Reload the provided firearm.
    """

    def __init__(self, target_weapon, **keywords):
        self.target_weapon = target_weapon
        super().__init__(**keywords)

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay=0, data=None):
        if data:
            ammo = data.get("AMMO")
            pc = self.target_weapon.get_root()
            if ammo and self.target_weapon.is_good_ammo(ammo):
                self.target_weapon.reload(ammo)
            del data["AMMO"]
        return super().handle_effect(camp, fx_record, originator, pos, anims, delay, data)


#  ***************************
#  ***   Roll  Modifiers   ***
#  ***************************
#
# Modular roll modifiers.

class RangeModifier(object):
    name = 'Range'

    def __init__(self, range_step):
        self.range_step = range_step

    def calc_modifier(self, camp, attacker, pos):
        my_range = camp.scene.distance(attacker.pos, pos)
        my_mod = ((my_range - 1) // self.range_step) * -10
        self.name = "Too Far"
        if my_range < (self.range_step - 3):
            my_mod += (self.range_step - 3 - my_range) * -10
            self.name = "Too Close"
        return my_mod


class CoverModifier(object):
    name = 'Cover'

    def __init__(self, vision_type=movement.Vision):
        self.vision_type = vision_type

    def calc_modifier(self, camp, attacker, pos):
        my_mod = -camp.scene.get_cover(attacker.pos[0], attacker.pos[1], pos[0], pos[1])
        target = camp.scene.get_main_actor(pos)
        attacker_flying = attacker and hasattr(attacker, "mmode") and attacker.mmode is pbge.scenes.movement.Flying
        target_flying = target and hasattr(target, "mmode") and target.mmode is pbge.scenes.movement.Flying

        mod_modifier = 0
        if hasattr(target, "ench_list"):
            mod_modifier += target.ench_list.get_funval(target, "get_cover_bonus")
        if hasattr(attacker, "ench_list"):
            mod_modifier += attacker.ench_list.get_funval(attacker, "get_cover_negation")
        if mod_modifier != 0:
            my_mod = (my_mod * (mod_modifier + 100))//100

        if attacker_flying and target_flying:
            my_mod = 0
        elif attacker_flying or target_flying:
            my_mod = my_mod // 2
        return my_mod


class MeleeFlyingModifier(object):
    name = 'Flying'

    def __init__(self, weapon_reach=1):
        self.weapon_reach = weapon_reach

    def calc_modifier(self, camp, attacker, pos):
        my_mod = min(-55 + self.weapon_reach * 15, -10)
        target = camp.scene.get_main_actor(pos)
        attacker_flying = attacker and hasattr(attacker, "mmode") and attacker.mmode is pbge.scenes.movement.Flying
        attacker_jumping = attacker and hasattr(attacker, "get_speed") and attacker.get_speed(tags.Jumping) > 0

        target_flying = target and hasattr(target, "mmode") and target.mmode is pbge.scenes.movement.Flying

        if target_flying and attacker_jumping:
            return -5
        elif not (target_flying or attacker_flying):
            return 0
        elif attacker_flying and target_flying:
            return -5
        else:
            return my_mod


class SpeedModifier(object):
    name = 'Target Movement'
    MOD_PER_TILE = -3

    def calc_modifier(self, camp, attacker, pos):
        targets = camp.scene.get_operational_actors(pos)
        my_mod = 0
        if camp.fight:
            for t in targets:
                my_mod += camp.fight.cstat[t].moves_this_round * self.MOD_PER_TILE
        return my_mod


class ImmobileModifier(object):
    name = 'Target Immobile'
    IMMOBILE_MODIFIER = 25

    def calc_modifier(self, camp, attacker, pos):
        targets = camp.scene.get_operational_actors(pos)
        my_mod = 0
        for t in targets:
            if hasattr(t, "get_current_speed") and t.get_current_speed() < 1:
                my_mod += self.IMMOBILE_MODIFIER
        return my_mod


class SensorModifier(object):
    name = 'Sensor Range'
    PENALTY = -5

    def calc_modifier(self, camp, attacker, pos):
        my_range = camp.scene.distance(attacker.pos, pos)
        my_sensor = attacker.get_sensor_range(camp.scene.scale)
        my_target = camp.scene.get_main_actor(pos)
        if my_range > my_sensor:
            if hasattr(my_target, "ench_list") and my_target.ench_list.get_enchantment_of_class(SensorLock):
                return 0
            else:
                return (my_range - my_sensor) * self.PENALTY
        else:
            return 0


class OverwhelmModifier(object):
    # Every time you are attacked, the next attack gets a bonus to hit.
    name = 'Overwhelmed'
    MOD_PER_ATTACK = 4

    def calc_modifier(self, camp, attacker, pos):
        my_mod = 0
        if camp.fight:
            targets = camp.scene.get_operational_actors(pos)
            for t in targets:
                my_mod += camp.fight.cstat[t].attacks_this_round * self.MOD_PER_ATTACK
        return my_mod


class GenericBonus(object):
    def __init__(self, name, bonus):
        self.name = name
        self.bonus = bonus

    def calc_modifier(self, camp, attacker, pos):
        return self.bonus


class ModuleBonus(object):
    def __init__(self, wmodule):
        self.name = '{} Mod'.format(wmodule)
        self.wmodule = wmodule

    def calc_modifier(self, camp, attacker, pos):
        if self.wmodule:
            it = self.wmodule.form.AIM_BONUS
            for i in self.wmodule.inv_com:
                if hasattr(i, "get_aim_bonus"):
                    it += i.get_aim_bonus()
            return it
        else:
            return 0


class SneakAttackBonus(object):
    name = 'Sneak Attack'
    BONUS = 20

    def calc_modifier(self, camp, attacker, pos):
        if attacker and attacker.hidden:
            return self.BONUS
        else:
            return 0


class HiddenModifier(object):
    name = 'Hidden'
    BONUS = -25

    def calc_modifier(self, camp, attacker, pos):
        target = camp.scene.get_main_actor(pos)
        if target and target.hidden:
            return self.BONUS
        else:
            return 0

#  **************************
#  ***   Defense  Rolls   ***
#  **************************
#
# Each defense roll takes the attack roll effect, the attacker, defender,
# attack bonus, and attack roll.
# It returns the roll result fx (None if the roll was unsuccessful)
# and the defense target (def roll + def bonus), which is used to calculate
# penetration if the attack hits.

class DodgeRoll(object):
    def make_roll(self, atroller, attacker, defender, att_bonus, att_roll, fx_record):
        # If the attack roll + attack bonus + accuracy is higher than the
        # defender's defense bonus + maneuverability + 20, or if the attack roll
        # is greater than 95, the attack hits.
        def_target = defender.get_dodge_score() + 50
        if defender.get_current_stamina() < 1:
            def_target -= 25

        if att_roll > 95:
            # A roll greater than 95 always hits.
            if attacker and hasattr(attacker, "dole_experience"):
                attacker.dole_experience(1)
            return (None, def_target)
        elif att_roll <= 5:
            # A roll of 5 or less always misses.
            if defender and hasattr(defender, "dole_experience") and hasattr(defender, "DODGE_SKILL"):
                defender.dole_experience(3, defender.DODGE_SKILL)
            return (self.CHILDREN, def_target)
        elif (att_roll + att_bonus + atroller.accuracy) > (def_target + defender.calc_mobility()):
            return (None, def_target)
        else:
            if defender and hasattr(defender, "dole_experience") and hasattr(defender, "DODGE_SKILL"):
                defender.dole_experience(2, defender.DODGE_SKILL)
            defender.spend_stamina(1)
            return (self.CHILDREN, def_target)

    def can_attempt(self, attacker, defender):
        return True

    def get_odds(self, atroller, attacker, defender, att_bonus):
        # Return the odds as a float.
        def_target = defender.get_dodge_score()
        if defender.get_current_stamina() < 1:
            def_target -= 25
        # The chance to hit is clamped between 5% and 95%.
        percent = min(max(50 + (att_bonus + atroller.accuracy) - (def_target + defender.calc_mobility()), 5), 95)
        return float(percent) / 100

    CHILDREN = (effects.NoEffect(anim=MissAnim),)


class ReflexSaveRoll(object):
    # Taking the name from d20... Unlike a regular dodge roll, a reflex save
    # can't entirely avoid an attack, but it can reduce the damage done.
    def make_roll(self, atroller, attacker, defender, att_bonus, att_roll, fx_record):
        # If the attack roll + attack bonus + accuracy is higher than the
        # defender's defense bonus + maneuverability + 20, or if the attack roll
        # is greater than 95, the attack hits.
        def_target = defender.get_dodge_score() + random.randint(1, 100)
        diff = (def_target + defender.calc_mobility()) - (att_roll + att_bonus + atroller.accuracy)
        if diff >= 0:
            # Record a damage reduction.
            fx_record['damage_percent'] = max(75 - diff, 25)
            if defender and hasattr(defender, "dole_experience") and hasattr(defender, "DODGE_SKILL"):
                defender.dole_experience(2, defender.DODGE_SKILL)
        return (None, def_target)

    def can_attempt(self, attacker, defender):
        return True

    def get_odds(self, atroller, attacker, defender, att_bonus):
        return 1.0


class BlockRoll(object):
    def __init__(self, weapon_to_block):
        self.weapon_to_block = weapon_to_block

    def make_roll(self, atroller, attacker, defender, att_bonus, att_roll, fx_record):
        # First, locate the defender's shield.
        shield = self.get_shield(defender)
        if shield:
            def_roll = random.randint(1, 100)
            def_bonus = shield.get_block_bonus() + defender.get_skill_score(stats.Speed, shield.scale.MELEE_SKILL)

            if def_roll > 95:
                # A roll greater than 95 always defends.
                shield.pay_for_block(defender, self.weapon_to_block)
                if defender and hasattr(defender, "dole_experience"):
                    defender.dole_experience(3, shield.scale.MELEE_SKILL)
                return (self.CHILDREN, def_roll + def_bonus)
            elif def_roll <= 5:
                # A roll of 5 or less always fails.
                return (None, def_roll + def_bonus)
            elif (att_roll + att_bonus + atroller.accuracy) > (def_roll + def_bonus):
                return (None, def_roll + def_bonus)
            else:
                shield.pay_for_block(defender, self.weapon_to_block)
                if defender and hasattr(defender, "dole_experience"):
                    defender.dole_experience(2, shield.scale.MELEE_SKILL)
                return (self.CHILDREN, def_roll + def_bonus)
        else:
            return (None, 0)

    def get_shield(self, defender):
        shields = [part for part in defender.descendants() if
                   hasattr(part, 'get_block_bonus') and part.is_operational()]
        if shields:
            return max(shields, key=lambda s: s.get_block_bonus())

    def can_attempt(self, attacker, defender):
        return self.get_shield(defender) and (defender.get_current_stamina() > 0)

    def get_odds(self, atroller, attacker, defender, att_bonus):
        # Return the odds as a float.
        shield = self.get_shield(defender)
        if shield:
            def_target = shield.get_block_bonus() + defender.get_skill_score(stats.Speed, shield.scale.MELEE_SKILL)
            # The chance to hit is clamped between 5% and 95%.
            percent = min(max(50 + (att_bonus + atroller.accuracy) - def_target, 5), 95)
            return float(percent) / 100
        else:
            return 1.0

    CHILDREN = (effects.NoEffect(anim=BlockAnim),)


class ParryRoll(object):
    def __init__(self, weapon_to_parry):
        self.weapon_to_parry = weapon_to_parry

    def make_roll(self, atroller, attacker, defender, att_bonus, att_roll, fx_record):
        # First, locate the defender's parrier.
        parrier = self.get_parrier(defender)
        if parrier:
            def_roll = random.randint(1, 100)
            def_bonus = parrier.get_parry_bonus() + defender.get_skill_score(stats.Speed, parrier.scale.MELEE_SKILL)

            if def_roll > 95:
                # A roll greater than 95 always defends.
                parrier.pay_for_parry(defender, self.weapon_to_parry)
                if defender and hasattr(defender, "dole_experience"):
                    defender.dole_experience(3, parrier.scale.MELEE_SKILL)
                return (self.CHILDREN, def_roll + def_bonus)
            elif def_roll <= 5:
                # A roll of 5 or less always fails.
                return (None, def_roll + def_bonus)
            elif (att_roll + att_bonus + atroller.accuracy) > (def_roll + def_bonus):
                return (None, def_roll + def_bonus)
            else:
                parrier.pay_for_parry(defender, self.weapon_to_parry)
                if defender and hasattr(defender, "dole_experience"):
                    defender.dole_experience(2, parrier.scale.MELEE_SKILL)
                return (self.CHILDREN, def_roll + def_bonus)
        else:
            return (None, 0)

    def get_parrier(self, defender):
        parriers = [part for part in defender.descendants() if
                    hasattr(part, 'can_parry') and part.can_parry() and part.is_operational()]
        if parriers:
            return max(parriers, key=lambda s: s.get_parry_bonus())

    def can_attempt(self, attacker, defender):
        return self.get_parrier(defender) and (defender.get_current_stamina() > 0)

    def get_odds(self, atroller, attacker, defender, att_bonus):
        # Return the odds as a float.
        parrier = self.get_parrier(defender)
        if parrier:
            def_target = parrier.get_parry_bonus() + defender.get_skill_score(stats.Speed, parrier.scale.MELEE_SKILL)
            # The chance to hit is clamped between 5% and 95%.
            percent = min(max(50 + (att_bonus + atroller.accuracy) - def_target, 5), 95)
            return float(percent) / 100
        else:
            return 1.0

    CHILDREN = (effects.NoEffect(anim=ParryAnim),)


class InterceptRoll(object):
    def __init__(self, weapon_to_intercept):
        self.weapon_to_intercept = weapon_to_intercept

    def make_roll(self, atroller, attacker, defender, att_bonus, att_roll, fx_record):
        # First, locate the defender's interceptors.
        interceptors = self.get_interceptors(defender)
        highest_def_roll = 0
        for interceptor in interceptors:
            # Interception is worse than other defenses, but you can stack
            # multiple Interceptors.
            if random.randint(1, 2) == 1:
                # Sometimes it just.... fails.  No reason.
                # I mean you are trying to hit a flying target
                # that's much tinier than an 18-meter mecha,
                # you think *you* can do that?
                continue

            def_roll = random.randint(1, 100)
            # Same reason, you think *you* can hit a tiny flying
            # target that's much tinier than an 18-meter mecha
            # using *just* your skills?
            def_bonus = (interceptor.get_intercept_bonus() + defender.get_skill_score(stats.Speed,
                                                                                      interceptor.scale.RANGED_SKILL)) // 2

            if highest_def_roll < def_roll + def_bonus:
                highest_def_roll = def_roll + def_bonus

            # I removed the 5%/95% thing temporarily, because I
            # couldn't figure out how to handle that with the
            # above coin toss in the `get_odds` function.
            if (att_roll + att_bonus + atroller.accuracy) > (def_roll + def_bonus):
                # Attacker is too good.
                continue
            else:
                interceptor.pay_for_intercept(defender, self.weapon_to_intercept)
                if defender and hasattr(defender, "dole_experience"):
                    # Given the reduced chances of actually intercepting, we
                    # get more experience with it.
                    defender.dole_experience(5, interceptor.scale.RANGED_SKILL)
                return (self.CHILDREN, highest_def_roll)
        return (None, highest_def_roll)

    def get_interceptors(self, defender):
        return [part for part in defender.descendants() if
                hasattr(part, 'can_intercept') and part.can_intercept() and part.is_operational()]

    def can_attempt(self, attacker, defender):
        return len(self.get_interceptors(defender)) > 0 and (defender.get_current_stamina() > 0)

    def get_odds(self, atroller, attacker, defender, att_bonus):
        # Return the odds as a float.
        interceptors = self.get_interceptors(defender)
        base = 1.0
        for interceptor in interceptors:
            def_target = (interceptor.get_intercept_bonus() + defender.get_skill_score(stats.Speed,
                                                                                       interceptor.scale.RANGED_SKILL)) // 2
            defense_percent = max(0, 50 + def_target - (att_bonus + atroller.accuracy))
            # There's a 50-50 chance the interception just does not work.
            defense_percent = float(defense_percent) / 2.0
            # Now get the hit percent.
            base = base * float(100 - defense_percent) / 100
        return base

    CHILDREN = (effects.NoEffect(anim=InterceptAnim),)


# ECMRoll

#  *****************
#  ***   PRICE   ***
#  *****************

class AmmoPrice(object):
    def __init__(self, ammo_source, ammo_amount):
        self.ammo_source = ammo_source
        self.ammo_amount = ammo_amount

    def pay(self, chara):
        self.ammo_source.spent += self.ammo_amount

    def can_pay(self, chara):
        return self.ammo_source.quantity >= (self.ammo_source.spent + self.ammo_amount)


class ItemPrice(object):
    def __init__(self, item_source):
        self.item_source = item_source

    def pay(self, chara):
        self.item_source.spent += 1
        if self.item_source.quantity <= self.item_source.spent and self.item_source.parent:
            if self.item_source in self.item_source.parent.inv_com:
                self.item_source.parent.inv_com.remove(self.item_source)
            elif self.item_source in self.item_source.parent.sub_com:
                self.item_source.parent.sub_com.remove(self.item_source)

    def can_pay(self, chara):
        return self.item_source.quantity > self.item_source.spent


class PowerPrice(object):
    def __init__(self, power_amount):
        self.power_amount = power_amount

    @classmethod
    def describe(cls, prices):
        total = sum(p.power_amount for p in prices)
        return '{}Pw'.format(total)

    def pay(self, chara):
        chara.consume_power(self.power_amount)

    def can_pay(self, chara):
        cp, mp = chara.get_current_and_max_power()
        return cp >= self.power_amount


class MentalPrice(object):
    def __init__(self, amount):
        self.amount = amount

    @classmethod
    def describe(cls, prices):
        total = sum(p.amount for p in prices)
        return '{}MP'.format(total)

    def pay(self, chara):
        chara.spend_mental(self.amount)

    def can_pay(self, chara):
        return chara.get_current_mental() >= self.amount


class StaminaPrice(object):
    def __init__(self, amount):
        self.amount = amount

    @classmethod
    def describe(cls, prices):
        total = sum(p.amount for p in prices)
        return '{}SP'.format(total)

    def pay(self, chara):
        chara.spend_stamina(self.amount)

    def can_pay(self, chara):
        return chara.get_current_stamina() >= self.amount


class RevealPositionPrice(object):
    def __init__(self, weapon_flash):
        self.weapon_flash = weapon_flash

    def pay(self, chara):
        stealth_skill = min(chara.get_skill_score(stats.Ego, stats.Stealth) - self.weapon_flash * 25 + 50, 75)
        if random.randint(1, 100) > stealth_skill:
            chara.hidden = False

    def can_pay(self, chara):
        return True


class StatValuePrice(object):
    # Not so much a price as a prerequisite; you must have a minimum stat value
    # (or a skill, which is also stored in the statline) to use this invocation.
    def __init__(self, statid, minvalue):
        self.statid = statid
        self.minvalue = minvalue

    @classmethod
    def describe(cls, prices):
        minvalues = dict()
        for p in prices:
            minvalues[p.statid] = max(minvalues.get(p.statid, 0), p.minvalue)
        descs = list()
        for statid in minvalues.keys():
            descs.append('{}+{}'.format(statid.name, minvalues[statid]))
        return ', '.join(descs)

    def pay(self, chara):
        chara.dole_experience(self.minvalue, self.statid)

    def can_pay(self, chara):
        pc = chara.get_pilot()
        if pc:
            return pc.statline.get(self.statid, 0) >= self.minvalue


#  ************************
#  ***   ENCHANTMENTS   ***
#  ************************
# Existing funval types:
#   get_mobility_bonus
#   get_penetration_bonus
#   get_cover_bonus
#   get_cover_negation


# Enchantments should derive from either PositiveEnchantment
# or NegativeEnchantment based on whether it is beneficial
# or detrimental to the target.

class PositiveEnchantment(Enchantment):
    def __init__(self, **kwargs):
        dispel = kwargs.pop('dispel', self.DEFAULT_DISPEL)
        dispel += (ON_DISPEL_POSITIVE,)
        super().__init__(dispel=dispel, **kwargs)


class NegativeEnchantment(Enchantment):
    def __init__(self, **kwargs):
        dispel = kwargs.pop('dispel', self.DEFAULT_DISPEL)
        dispel += (ON_DISPEL_NEGATIVE,)
        super().__init__(dispel=dispel, **kwargs)


class Burning(NegativeEnchantment):
    name = 'Burning'
    DEFAULT_DURATION = 3

    def update(self, camp, owner):
        burn = effects.Invocation(
            name='Burn',
            fx=DoDamage(2, 4, scale=owner.scale, scatter=True,
                        anim=BurnAnim, ),
            area=pbge.scenes.targetarea.SingleTarget(), )
        burn.invoke(camp, None, [owner.pos, ], pbge.my_state.view.anim_list)
        pbge.my_state.view.handle_anim_sequence()


class Disintegration(NegativeEnchantment):
    name = 'Disintegrating'
    DEFAULT_DURATION = 3

    def update(self, camp, owner):
        burn = effects.Invocation(
            name='Disintegrate',
            fx=DoDamage(3, 6, scale=owner.scale, scatter=True,
                        anim=DisintegrationAnim, affected_by_armor=False),
            area=pbge.scenes.targetarea.SingleTarget(), )
        burn.invoke(camp, None, [owner.pos, ], pbge.my_state.view.anim_list)
        pbge.my_state.view.handle_anim_sequence()

    def get_penetration_bonus(self, owner):
        return 15


class HaywireStatus(NegativeEnchantment):
    name = 'Haywire'
    # The only top 10 status effect from Prince Edward Island
    DEFAULT_DURATION = 3
    DEFAULT_DISPEL = (END_COMBAT, materials.RT_REPAIR, DISPEL_NEGATIVE_ELECTRONIC)
    ALT_AI = 'HaywireAI'

    @classmethod
    def can_affect(cls, target):
        return hasattr(target, "material") and target.material in (materials.Metal, materials.Ceramic, materials.Advanced)


class OverloadStatus(NegativeEnchantment):
    name = 'Overloaded'
    DEFAULT_DISPEL = (END_COMBAT, DISPEL_NEGATIVE_ELECTRONIC)
    DEFAULT_DURATION = 5

    def get_mobility_bonus(self, owner):
        return -(max(self.duration // 2, 1) * 5)

    @classmethod
    def can_affect(cls, target):
        return isinstance(target, base.Mecha)


class SensorLock(NegativeEnchantment):
    name = 'Sensor Lock'
    DEFAULT_DISPEL = (END_COMBAT, DISPEL_NEGATIVE_ELECTRONIC)
    DEFAULT_DURATION = 5

    def get_mobility_bonus(self, owner):
        return -25


class Poisoned(NegativeEnchantment):
    name = 'Poisoned'
    DEFAULT_DURATION = 6
    DEFAULT_DISPEL = (USE_ANTIDOTE,)

    def update(self, camp, owner):
        burn = effects.Invocation(
            name='Poison',
            fx=SkillRoll(stats.Ego, stats.Vitality, max_chance=75,
                         on_failure=(
                             DoDamage(1, 6, scale=owner.scale, can_be_divided=False,
                                      anim=PoisonDamageBoom, affected_by_armor=False),
                         )
                         ),
            area=pbge.scenes.targetarea.SingleTarget(), )
        burn.invoke(camp, None, [owner.pos, ], pbge.my_state.view.anim_list)
        pbge.my_state.view.handle_anim_sequence()

    @classmethod
    def can_affect(cls, target):
        return hasattr(target, "material") and target.material in (materials.Meat,)


class Prescience(PositiveEnchantment):
    # +2 bonus to dodge skills while active.
    name = 'Prescience'
    DEFAULT_DISPEL = (END_COMBAT,)
    DEFAULT_DURATION = 5

    def get_stat(self, stat):
        if stat in (stats.MechaPiloting, stats.Dodge):
            return 2
        else:
            return 0


class WeakPoint(NegativeEnchantment):
    name = 'Weak Point'
    DEFAULT_DISPEL = (END_COMBAT,)
    DEFAULT_DURATION = 5

    def get_penetration_bonus(self, owner):
        return 20


class TakingCover(PositiveEnchantment):
    name = 'On the Hunt'
    DEFAULT_DISPEL = (END_COMBAT,)
    DEFAULT_DURATION = 3

    def __init__(self, percent_bonus=50, **kwargs):
        super().__init__(**kwargs)
        self.percent_bonus = percent_bonus

    def merge_enchantment(self, **kwargs):
        new_percent_bonus = kwargs.pop("percent_bonus")
        super().merge_enchantment(**kwargs)
        # Select larger bonus.
        if new_percent_bonus and new_percent_bonus > self.percent_bonus:
            self.percent_bonus = new_percent_bonus

    def get_cover_bonus(self, owner):
        return self.percent_bonus

    def get_cover_negation(self, owner):
        return -50


class BreakingCover(NegativeEnchantment):
    name = 'Cover Broken'
    DEFAULT_DISPEL = (END_COMBAT,)
    DEFAULT_DURATION = 2

    def __init__(self, percent_malus=100, **kwargs):
        super().__init__(**kwargs)
        self.percent_malus = percent_malus

    def get_cover_bonus(self, owner):
        return -self.percent_malus


class AIAssisted(PositiveEnchantment):
    name = 'AI Assisted'
    DEFAULT_DISPEL = (END_COMBAT, HaywireStatus)
    DEFAULT_DURATION = None

    def __init__(self, percent_prob=100, **kwargs):
        super().__init__(**kwargs)
        self.percent_prob = percent_prob
        self.in_effect = True

    def merge_enchantment(self, **kwargs):
        new_percent_prob = kwargs.pop('percent_prob')
        super().merge_enchantment(**kwargs)
        # Select larger probability.
        if new_percent_prob and new_percent_prob > self.percent_prob:
            self.percent_prob = new_percent_prob
        # Force being enabled.
        self.in_effect = True

    def update(self, camp, owner):
        # Roll if we will take effect, based on percent_prob.
        self.in_effect = random.randint(1, 100) <= self.percent_prob
        # If we took effect, animate it.
        if self.in_effect:
            assist = effects.Invocation(
                name='AI Assist',
                fx=effects.NoEffect(anim=AIAssistAnim),
                area=pbge.scenes.targetarea.SingleTarget())
            assist.invoke(camp, None, [owner.pos, ], pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence()

    def get_stat(self, stat):
        # If not currently in effect, no bonus.
        if not self.in_effect:
            return 0
        elif stat in (
                stats.MechaFighting, stats.MechaGunnery, stats.MechaPiloting, stats.RangedCombat, stats.CloseCombat,
                stats.Dodge):
            return 1
        else:
            return 0

    # Cannot be AI-assisted if the mecha is Haywire.
    @classmethod
    def can_affect(cls, target):
        if not hasattr(target, 'ench_list'):
            return False
        for ench in target.ench_list:
            if isinstance(ench, HaywireStatus):
                return False
        return True


class Demoralized(NegativeEnchantment):
    name = 'Demoralized'
    DEFAULT_DURATION = None

    def __init__(self, **kwargs):
        # Inspired and Demoralized cancel each other, but we
        # cannot set DEFAULT_DISPEL since Inspired is not
        # yet defined.
        super().__init__(dispel=(END_COMBAT, Inspired), **kwargs)

    def get_stat(self, stat):
        if isinstance(stat, stats.Stat):
            return -1
        else:
            return 0


class Inspired(PositiveEnchantment):
    name = 'Inspired'
    DEFAULT_DISPEL = (END_COMBAT, Demoralized)
    DEFAULT_DURATION = None

    def get_stat(self, stat):
        if isinstance(stat, stats.Stat):
            return 1
        else:
            return 0
