from . import materials
from . import scale
from . import calibre
import pbge
from . import genderobj
from pbge import container, scenes, KeyObject, Singleton
import random
import collections
from . import stats
import copy
from . import geffects
from . import attackattributes
from . import tags
from . import aitargeters
from . import enchantments
from . import portraits
import pygame
from . import personality
import uuid
import math


class Restoreable(object):
    def restore(self):
        # Remove all damage and other stuff. Return the restoration cost in credits.
        return 0


#
# Damage Handlers
#
#  Each "practical" gear should subclass one of the damage handlers.
#

class StandardDamageHandler(KeyObject, Restoreable):
    # This gear type has health and takes damage. It is destroyed when the
    # amount of damage taken exceeds its maximum capacity.
    def __init__(self, **keywords):
        self.hp_damage = 0
        super(StandardDamageHandler, self).__init__(**keywords)

    base_health = 1

    @property
    def max_health(self):
        """Returns the scaled maximum health of this gear."""
        return self.scale.scale_health(self.base_health, self.material)

    @property
    def current_health(self):
        """Returns the scaled maximum health of this gear."""
        return self.max_health - self.hp_damage

    def get_damage_status(self):
        """Returns a percent value showing how damaged this gear is."""
        return (self.hp_damage * 100) // self.max_health

    def get_total_damage_status(self):
        dstats = list()
        for part in self.get_all_parts():
            dstats.append(part.get_damage_status())
        return sum(dstats) // len(dstats)

    def get_total_damage_and_health(self, destroyed_branch=False):
        health = self.max_health
        if destroyed_branch or self.is_destroyed():
            dmg = health
            destroyed_branch = True
        else:
            dmg = self.hp_damage
        for part in self.sub_com:
            pd, ph = part.get_total_damage_and_health(destroyed_branch)
            dmg += pd
            health += ph
        return dmg, health

    def get_percent_damage_over_health(self):
        dmg, health = self.get_total_damage_and_health()
        return (dmg * 100) // max(health, 1)

    def is_not_destroyed(self):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        if self.can_be_damaged():
            return self.max_health > self.hp_damage
        else:
            return True

    def is_destroyed(self):
        return not self.is_not_destroyed()

    def is_operational(self):
        """ Returns True if this gear is okay and its conditions for use are
            met. In other words, return True if this gear is
            ready to be used.
        """
        return self.is_not_destroyed()

    def can_be_damaged(self):
        """ Returns True if this gear can be damaged.
        """
        return True

    def get_repair_cost(self, repairdict=None, check_descendants=True):
        if not repairdict:
            repairdict = collections.defaultdict(int)
        repairdict[self.material.repair_type] += self.hp_damage * self.material.repair_cost
        if check_descendants:
            for p in self.sub_com:
                p.get_repair_cost(repairdict)
            for p in self.inv_com:
                p.get_repair_cost(repairdict)
        return repairdict

    def wipe_damage(self):
        self.hp_damage = 0
        if hasattr(self, "ench_list"):
            del self.ench_list[:]
        for p in self.sub_com:
            p.wipe_damage()
        for p in self.inv_com:
            p.wipe_damage()

    def restore(self):
        # Remove all damage and other stuff. Return the restoration cost in credits.
        rdic = self.get_repair_cost(check_descendants=False)
        self.hp_damage = 0
        if hasattr(self, "ench_list"):
            del self.ench_list[:]
        return sum(rdic.values()) + super(StandardDamageHandler, self).restore()


class InvulnerableDamageHandler(StandardDamageHandler):
    # This gear cannot be damaged or destroyed.
    def can_be_damaged(self):
        """ Returns True if this gear can be damaged.
        """
        return False

    def get_damage_status(self):
        """Returns a percent value showing how damaged this gear is."""
        return 0

    def is_not_destroyed(self):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        return True


class ContainerDamageHandler(StandardDamageHandler):
    # This gear just contains other gears; it is operational as long as it
    # has at least one subcom which is operational.
    base_health = 0

    def is_not_destroyed(self):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        working_subcoms = False
        for subcom in self.sub_com:
            if subcom.is_not_destroyed():
                working_subcoms = True
                break
        return working_subcoms

    def get_damage_status(self):
        """Returns a percent value showing how damaged this gear is."""
        mysubs = [sc.get_damage_status() for sc in self.sub_com]
        if mysubs:
            return sum(mysubs) // len(mysubs)
        else:
            return 0

    def can_be_damaged(self):
        """ Returns True if this gear can be damaged.
        """
        return False


# Gear Ingredients
# Subclass one of these to get extra stuff for your gear class.
# These are purely optional.

class Stackable(KeyObject):
    def __init__(self, **keywords):
        super(Stackable, self).__init__(**keywords)

    def can_merge_with(self, part):
        return (self.__class__ is part.__class__ and self.scale is part.scale
                and self.name is part.name and self.desig is part.desig
                and not self.inv_com and not self.sub_com)


class VisibleGear(pbge.scenes.PlaceableThing):
    # This gear has the GearHead-specific sprite modifications.
    # - If destroyed, use the destroyed image
    # - If hidden, hide it
    # - May have a portrait
    def __init__(self, portrait=None, portrait_gen=None, **keywords):
        self.portrait = portrait
        self.portrait_gen = portrait_gen
        self.destroyed_pose = False
        super().__init__(**keywords)

    SAVE_PARAMETERS = ('portrait',)
    DESTROYED_FRAME = 1

    def get_sprite(self):
        """Generate the sprite for this thing."""
        if self.portrait and self.portrait.startswith('card_'):
            self.frame = 2
            return pbge.image.Image(self.portrait, self.imagewidth, self.imageheight, self.colors,
                                    custom_frames=portraits.FRAMES)
        elif self.portrait_gen:
            self.frame = 2
            return self.portrait_gen.build_portrait(self)
        else:
            return pbge.image.Image(self.imagename, self.imagewidth, self.imageheight, self.colors)

    def get_portrait(self, add_color=True, force_rebuild=False):
        if self.portrait:
            if add_color:
                colorz = self.colors
            else:
                colorz = None
            if self.portrait.startswith('card_'):
                return pbge.image.Image(self.portrait, self.imagewidth, self.imageheight, colorz,
                                        custom_frames=portraits.FRAMES)
            else:
                return pbge.image.Image(self.portrait, color=colorz)
        elif self.portrait_gen:
            return self.portrait_gen.build_portrait(self, add_color=add_color, force_rebuild=force_rebuild)

    def render(self, foot_pos, view):
        if self.destroyed_pose:
            self.render_destroyed(foot_pos, view)
        else:
            self.render_shadow(foot_pos, view)
            if not self.hidden:
                self.render_visible(foot_pos, view)

    def render_shadow(self, foot_pos, view):
        spr = view.get_named_sprite('sys_shadow.png', transparent=50)
        mydest = spr.get_rect(0)
        x, y = self.pos
        mydest.topleft = (view.relative_x(x, y) + view.x_off,
                          view.relative_y(x, y) + view.y_off - view.scene.tile_altitude(x, y))
        spr.render(mydest, 0)

    def render_destroyed(self, foot_pos, view):
        spr = view.get_named_sprite('sys_destroyed.png')
        mydest = spr.get_rect(0)
        mydest.midbottom = foot_pos
        mydest.top += 8
        spr.render(mydest, self.DESTROYED_FRAME)

    def update_graphics(self):
        self.destroyed_pose = not self.is_operational()


class Mover(KeyObject):
    # A mover is a gear that moves under its own power, like a character or mecha.
    def __init__(self, **keywords):
        self.mmode = None
        super(Mover, self).__init__(**keywords)

    def apply_speed_bonus(self, base_speed):
        speed_percent = self.count_speed_bonus_percent()
        return max(base_speed, int(base_speed * float(100 + speed_percent) / 100.0))

    def calc_walking(self):
        # Count the number of leg points, divide by mass.
        return 0

    def calc_skimming(self):
        norm_mass = self.scale.unscale_mass(self.mass)
        thrust = self.count_thrust_points(geffects.Skimming)

        if thrust > (norm_mass * 20):
            return self.apply_speed_bonus(thrust // norm_mass)
        else:
            return 0

    def calc_rolling(self):
        norm_mass = self.scale.unscale_mass(self.mass)
        thrust = self.count_thrust_points(geffects.Rolling)

        if thrust > (norm_mass * 20):
            return self.apply_speed_bonus(thrust // norm_mass)
        else:
            return 0

    def get_speed(self, mmode):
        # This method returns the mover's movement points; under normal conditions
        # it costs 2MP to move along a cardinal direction or 3MP to move diagonally.
        # This cost will be adjusted for terrain and scale.
        if mmode is scenes.movement.Walking:
            return self.calc_walking()
        elif mmode is geffects.Skimming:
            return self.calc_skimming()
        elif mmode is geffects.Rolling:
            return self.calc_rolling()
        else:
            return 0

    def get_current_speed(self):
        return self.get_speed(self.mmode)

    def get_max_speed(self):
        return max(self.get_speed(scenes.movement.Walking), self.get_speed(geffects.Skimming),
                   self.get_speed(geffects.Rolling))

    def count_module_points(self, module_form):
        # Count the number of active module points, reducing rating for damage taken.
        total = 0
        for m in self.sub_com:
            if isinstance(m, Module) and (m.scale is self.scale) and (m.form == module_form) and m.is_not_destroyed():
                total += (m.size * m.current_health + m.max_health - 1) // m.max_health
        return total

    def count_modules(self, module_form):
        # Returns the number of modules of the given type and the number
        # of them that are not destroyed.
        total, active = 0, 0
        for m in self.sub_com:
            if isinstance(m, Module) and (m.scale is self.scale) and (m.form == module_form):
                total += 1
                if m.is_not_destroyed():
                    active += 1
        return total, active

    def count_thrust_points(self, move_mode):
        total = 0
        for g in self.sub_com.get_undestroyed():
            if (g.scale is self.scale) and hasattr(g, 'get_thrust'):
                total += g.get_thrust(move_mode)
        return total

    def count_speed_bonus_percent(self):
        total = 0
        for g in self.sub_com.get_undestroyed():
            if (g.scale is self.scale) and hasattr(g, 'get_speed_bonus_percent'):
                total += g.get_speed_bonus_percent()
        return total

    MOVEMODE_LIST = (
        scenes.movement.Walking, geffects.Rolling, geffects.Skimming, scenes.movement.Flying, geffects.SpaceFlight)

    def gear_up(self):
        #self.mmode = None
        for mm in self.MOVEMODE_LIST:
            if self.get_speed(mm) > self.get_current_speed():
                self.mmode = mm
        if not self.mmode:
            print("Warning: No movemode for {}".format(self))


class Combatant(KeyObject):
    def __init__(self, **keywords):
        self.ench_list = enchantments.EnchantmentList()
        super(Combatant, self).__init__(**keywords)

    def get_attack_library(self):
        my_invos = list()
        for p in self.descendants(include_pilot=False):
            if p.is_operational() and hasattr(p, 'get_attacks'):
                p_list = geffects.InvoLibraryShelf(p, p.get_attacks())
                if p_list.has_at_least_one_working_invo(self, True):
                    my_invos.append(p_list)
        my_invos.sort(key=lambda shelf: -shelf.get_average_thrill_power(self))
        return my_invos

    def get_primary_attack(self):
        mylibrary = self.get_attack_library()
        if not mylibrary:
            return None
        return max(mylibrary, key=lambda a: a.get_average_thrill_power(self, True))

    def get_skill_library(self, in_combat=False):
        my_invo_dict = collections.defaultdict(list)
        pilot = self.get_pilot()
        for p in list(pilot.get_all_skills()):
            if hasattr(p, 'add_invocations'):
                p.add_invocations(pilot, my_invo_dict)
        my_invos = list()
        for k, v in list(my_invo_dict.items()):
            p_list = geffects.InvoLibraryShelf(k, v)
            if p_list.has_at_least_one_working_invo(self, in_combat):
                my_invos.append(p_list)
        return my_invos

    def get_program_library(self, in_combat=True):
        my_invo_dict = dict()
        for p in self.descendants(include_pilot=False):
            if p.is_operational() and hasattr(p, 'add_program_invocations'):
                p.add_program_invocations(self, my_invo_dict)
        my_invos = list()
        for k, v in list(my_invo_dict.items()):
            p_list = geffects.InvoLibraryShelf(k, v)
            if p_list.has_at_least_one_working_invo(self, in_combat):
                my_invos.append(p_list)
        return my_invos

    def has_program(self, wanted_prog):
        has_it = False
        for p in self.descendants(include_pilot=False):
            if p.is_operational() and hasattr(p, 'programs'):
                has_it = wanted_prog in p.programs
            if has_it:
                break
        return has_it

    def get_action_points(self):
        return 3


class HasPower(KeyObject):
    # This is a gear that has, and can use, power sources.
    def get_current_and_max_power(self):
        sources = [p for p in self.descendants() if (hasattr(p, "max_power") and p.is_operational())]
        current_power = 0
        max_power = 0
        for p in sources:
            current_power += p.current_power()
            max_power += p.max_power()
        return current_power, max_power

    def consume_power(self, amount):
        sources = [p for p in self.descendants() if (hasattr(p, "spend_power") and p.is_operational())]
        random.shuffle(sources)
        while (amount > 0) and sources:
            ps = sources.pop()
            amount = ps.spend_power(amount)

    def renew_power(self):
        for p in self.descendants():
            if hasattr(p, 'regen_power') and p.is_operational():
                p.regen_power()


class HasInfinitePower(HasPower):
    def get_current_and_max_power(self):
        return 1000000, 1000000

    def consume_power(self, amount):
        pass


class MakesPower(KeyObject, Restoreable):
    # In addition to this inheritance, the subclass needs to define a max_power
    # method.
    def __init__(self, **keywords):
        self.spent = 0
        super(MakesPower, self).__init__(**keywords)

    def max_power(self):
        return self.scale.scale_power(1)

    def current_power(self):
        return self.max_power() - self.spent

    def spend_power(self, amount):
        # Take power from this device. Return any unspent power.
        leftover = amount - self.current_power()
        self.spent = min(self.spent + amount, self.max_power())
        return max(leftover, 0)

    def regen_power(self):
        if self.spent > 0:
            self.spent = max(self.spent - self.scale.SIZE_FACTOR, 0)

    def restore(self):
        # Remove all damage and other stuff. Return the restoration cost in credits.
        self.spent = 0
        return 0 + super(MakesPower, self).restore()


# Custom Containers
# For subcomponents and invcomponents with automatic error checking

class SubComContainerList(container.ContainerList):
    def _set_container(self, item):
        # If no owner, that means we're probably loading a file from disk and so assume this part is legal.
        if not hasattr(self, "owner") or self.owner.can_install(item):
            super()._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot subcom {}".format(self.owner, item))

    def get_undestroyed(self):
        # Return all non-destroyed gears, including descendants.
        for g in self:
            if g.is_not_destroyed():
                yield g
                for p in g.sub_com.get_undestroyed():
                    yield p
                for p in g.inv_com.get_undestroyed():
                    yield p


class InvComContainerList(container.ContainerList):
    def _set_container(self, item):
        # If no owner, that means we're probably loading a file from disk and so assume this part is legal.
        if not hasattr(self, "owner") or self.owner.can_equip(item):
            super(InvComContainerList, self)._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot invcom {}".format(self.owner, item))

    def get_undestroyed(self):
        # Return all non-destroyed gears, including descendants.
        for g in self:
            if g.is_not_destroyed():
                yield g
                for p in g.sub_com.get_undestroyed():
                    yield p
                for p in g.inv_com.get_undestroyed():
                    yield p


# The Base Gear itself.
# Note that the base gear is not usable by itself; a gear class should
# subclass BaseGear and also one of the damage handlers, plus any desired
# ingredients.

class BaseGear(scenes.PlaceableThing):
    # To create a usable gear class, you need to subclass BaseGear, one of the
    # damage handlers from above, and maybe another ingredient like Stackable.
    DEFAULT_NAME = "Gear"
    DEFAULT_MATERIAL = materials.Metal
    DEFAULT_SCALE = scale.MechaScale
    DEFAULT_SLOT = tags.SLOT_ITEM
    SAVE_PARAMETERS = (
        'name', 'desig', 'scale', 'material', 'imagename', 'colors', 'uniqueid', 'shop_tags', 'desc', 'slot',
        'faction_list')

    def __init__(self, uniqueid=None, shop_tags=(), desc="", slot=None, faction_list=(None,), **keywords):
        self.__base_gear_pos = None
        self.name = keywords.pop("name", self.DEFAULT_NAME)
        self.desig = keywords.pop("desig", None)
        self.scale = keywords.pop("scale", self.DEFAULT_SCALE)
        self.material = keywords.pop("material", self.DEFAULT_MATERIAL)
        self.imagename = keywords.pop("imagename", "iso_item.png")
        self.colors = keywords.pop("colors", None)
        self.uniqueid = uniqueid
        self.shop_tags = list(shop_tags)
        self.desc = desc
        self.slot = slot or self.DEFAULT_SLOT
        self.faction_list = faction_list

        self.sub_com = SubComContainerList(owner=self)
        sc_to_add = keywords.pop("sub_com", [])
        for i in sc_to_add:
            try:
                self.sub_com.append(i)
            except container.ContainerError as err:
                print(("ERROR: {}".format(err)))

        self.inv_com = InvComContainerList(owner=self)
        ic_to_add = keywords.pop("inv_com", [])
        for i in ic_to_add:
            if self.can_equip(i):
                self.inv_com.append(i)
            else:
                print(("ERROR: {} cannot be equipped in {}".format(i, self)))

        super(BaseGear, self).__init__(**keywords)

    @property
    def pos(self):
        return self.__base_gear_pos

    @pos.setter
    def pos(self, nextpos):
        if not hasattr(self, 'ench_list'):
            self.__base_gear_pos = nextpos
            return
        curpos = self.__base_gear_pos
        self.__base_gear_pos = nextpos
        if not (nextpos is curpos):
            self.ench_list.tidy(enchantments.ON_MOVE)

    def get_full_name(self):
        if self.desig:
            return "{} {}".format(self.desig, self.name)
        else:
            return self.name

    @property
    def base_mass(self):
        """Returns the unscaled mass of this gear, ignoring children."""
        return 1

    @property
    def self_mass(self):
        """Returns the properly scaled mass of this gear, ignoring children."""
        return self.scale.scale_mass(self.base_mass, self.material)

    @property
    def mass(self):
        """Returns the true mass of this gear including children. Units is 0.1kg."""
        m = self.self_mass
        for part in self.sub_com:
            m = m + part.mass
        for part in self.inv_com:
            m = m + part.mass
        return m

    def get_inv_mass(self, is_inv=False):
        if is_inv:
            m = self.mass
            for part in self.sub_com:
                m += part.mass
        else:
            m = 0
            for part in self.sub_com:
                m += part.get_inv_mass(False)
        for part in self.inv_com:
            m += part.mass
        return m

    # volume is likely to be a property in more complex gear types, but here
    # it's just a constant value.
    base_volume = 1

    @property
    def volume(self):
        return self.base_volume

    @property
    def free_volume(self):
        return self.volume - sum(i.volume for i in self.sub_com)

    base_cost = 0

    @property
    def self_cost(self):
        return self.scale.scale_cost(self.base_cost, self.material)

    @property
    def cost(self):
        m = self.self_cost
        for part in self.sub_com:
            m = m + part.cost
        for part in self.inv_com:
            m = m + part.cost
        return m

    def battle_cost(self):
        # Return the cost, ignoring treasure.
        m = self.self_cost
        for part in self.sub_com:
            if not isinstance(part,Treasure):
                m = m + part.cost
        for part in self.inv_com:
            if not isinstance(part,Treasure):
                m = m + part.cost
        return m

    def is_legal_sub_com(self, part):
        return False

    MULTIPLICITY_LIMITS = {}

    def check_multiplicity(self, part):
        """Returns True if part within acceptable limits for its kind."""
        ok = True
        for k, v in list(self.MULTIPLICITY_LIMITS.items()):
            if isinstance(part, k):
                ok = ok and len([item for item in self.sub_com if isinstance(item, k)]) < v
        return ok

    # Called by the gear editor if the gear can be removed in the
    # normal in-game Mecha Engineering Terminal.
    def can_normally_remove(self):
        return True

    def can_install(self, part, check_volume=True):
        """Returns True if part can be legally installed here under current conditions"""
        if check_volume:
            return self.is_legal_sub_com(
                part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR and part.volume <= self.free_volume and self.check_multiplicity(
                part)
        else:
            return self.is_legal_sub_com(part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR

    def is_legal_inv_com(self, part):
        return False

    def can_equip(self, part, check_slots=True):
        """Returns True if part can be legally installed here under current conditions"""
        if check_slots:
            return self.is_legal_inv_com(part) and part.scale.SIZE_FACTOR == self.scale.SIZE_FACTOR and not bool(
                [i for i in self.inv_com if i.slot == part.slot])
        else:
            return self.is_legal_inv_com(part) and part.scale.SIZE_FACTOR == self.scale.SIZE_FACTOR

    def sub_sub_coms(self):
        yield self
        for part in self.sub_com:
            for p in part.sub_sub_coms():
                yield p

    def sub_sub_coms(self):
        yield self
        for part in self.sub_com:
            for p in part.sub_sub_coms():
                yield p

    def ok_sub_sub_coms(self):
        if self.is_not_destroyed():
            yield self
            for part in self.sub_com:
                for p in part.ok_sub_sub_coms():
                    yield p

    def get_all_parts(self):
        yield self
        for part in self.sub_com:
            yield part
            for p in part.descendants():
                yield p
        for part in self.inv_com:
            yield part
            for p in part.descendants():
                yield p

    def descendants(self, include_pilot=True):
        for part in self.sub_com:
            yield part
            if include_pilot or not isinstance(part, Cockpit):
                for p in part.descendants(include_pilot):
                    yield p
        for part in self.inv_com:
            yield part
            if include_pilot or not isinstance(part, Cockpit):
                for p in part.descendants(include_pilot):
                    yield p

    def ok_descendants(self, include_pilot=True):
        for part in self.sub_com:
            if part.is_not_destroyed():
                yield part
                if include_pilot or not isinstance(part, Cockpit):
                    for p in part.ok_descendants(include_pilot):
                        yield p
        for part in self.inv_com:
            if part.is_not_destroyed():
                yield part
                if include_pilot or not isinstance(part, Cockpit):
                    for p in part.ok_descendants(include_pilot):
                        yield p

    def ancestors(self):
        if hasattr(self, "container") and self.container and isinstance(self.container.owner, BaseGear):
            yield self.container.owner
            for p in self.container.owner.ancestors():
                yield p

    @property
    def parent(self):
        if hasattr(self, "container") and self.container and isinstance(self.container.owner, BaseGear):
            return self.container.owner

    def get_root(self):
        """Return the top level parent of this gear."""
        if hasattr(self, "container") and self.container and isinstance(self.container.owner, BaseGear):
            return self.container.owner.get_root()
        else:
            return self

    def get_scene(self):
        # Return the scene this gear is in, if it can be found. None otherwise.
        rgear = self.get_root()
        if rgear and hasattr(rgear, "container") and rgear.container:
            return rgear.container.owner

    @property
    def scene(self):
        return self.get_scene()

    def get_module(self):
        for g in self.ancestors():
            if isinstance(g, Module):
                return g

    def calc_average_armor(self):
        alist = list()
        for part in self.sub_com:
            armor = part.get_armor()
            if armor:
                alist.append(armor.get_armor_rating())
            else:
                alist.append(0)
        if len(alist) > 0:
            return sum(alist) // len(alist)
        else:
            return 0

    def get_armor(self, destroyed_ok=False):
        """Returns the armor protecting this gear."""
        candidates = [part for part in self.sub_com if
                      isinstance(part, Armor) and (destroyed_ok or part.is_not_destroyed())]
        candidates.sort(key=lambda a: a.get_armor_rating())
        if candidates:
            return candidates[0]

    def __str__(self):
        return self.name

    def termdump(self, prefix=' ', indent=1):
        """Dump some info about this gear to the terminal."""
        print(" " * indent + prefix + self.name + ' mass:' + str(self.mass) + ' cost:$' + str(
            self.cost) + " vol:" + str(self.free_volume) + "/" + str(self.volume))
        for g in self.sub_com:
            g.termdump(prefix='>', indent=indent + 1)
        for g in self.inv_com:
            g.termdump(prefix='+', indent=indent + 1)

    def statusdump(self, prefix=' ', indent=1):
        """Dump some info about this gear to the terminal."""
        print(" " * indent + prefix + self.name + ' HP:{1}/{0}'.format(self.max_health,
                                                                       self.max_health - self.hp_damage))
        for g in self.sub_com:
            g.statusdump(prefix='>', indent=indent + 1)
        for g in self.inv_com:
            g.statusdump(prefix='+', indent=indent + 1)

    def __deepcopy__(self, memo):
        # Regular deepcopy chokes on gears, so here's a custom deepcopy.
        # Go through the ancestors, see what attributes need passing to constructor.
        my_params = set()
        for ancestor in self.__class__.__mro__:
            if hasattr(ancestor, 'SAVE_PARAMETERS'):
                my_params.update(ancestor.SAVE_PARAMETERS)

        # Copy the sub_com and inv_com
        dcsubcom = [copy.deepcopy(sc, memo) for sc in self.sub_com]
        dcinvcom = [copy.deepcopy(sc, memo) for sc in self.inv_com]

        # Go through this gear's dict, copying stuff 
        initdict = dict()
        afterdict = dict()
        for k, v in list(self.__dict__.items()):
            if k in my_params:
                initdict[k] = copy.deepcopy(v, memo)
            elif k not in ('sub_com', 'inv_com', 'container'):
                afterdict[k] = copy.deepcopy(v, memo)
        if hasattr(self, "DEEP_COPY_PARAMS"):
            initdict.update(self.DEEP_COPY_PARAMS)

        initdict["sub_com"] = dcsubcom
        initdict["inv_com"] = dcinvcom

        newgear = type(self)(**initdict)
        newgear.__dict__.update(afterdict)
        memo[id(self)] = newgear

        return newgear

    #################
    ### Modifiers ###
    #################
    def get_common_modifiers(self, module):
        ''' Modifiers that we expect affect all things.
        '''
        return [geffects.SensorModifier()
            , geffects.OverwhelmModifier()
            , geffects.ModuleBonus(module)
            , geffects.SneakAttackBonus()
            , geffects.HiddenModifier()
            , geffects.ImmobileModifier()
            , geffects.CoverModifier()
            , geffects.CoverEnhanceModifier()
            , geffects.CoverPierceModifier()
                ]

    def get_ranged_modifiers(self, reach):
        ''' Modifiers that only affect ranged weapons.
        '''
        return [geffects.RangeModifier(reach)
            , geffects.SpeedModifier()
                ]

    def get_melee_modifiers(self):
        ''' Modifiers that only affect melee weapons.
        '''
        return [
        ]

    def restore_all(self):
        total = 0
        for part in self.get_all_parts():
            total += part.restore()
        return total


# Component gears can be installed into modules,
# or possibly other components.
# Such components might be integral to the module
# it is installed in.
# Integral components can be cheaper, lighter-weight,
# and smaller, but cannot be removed in-game.
class Component(BaseGear):
    DEFAULT_NAME = "Component"
    SAVE_PARAMETERS = ('integral',)

    # If the component is integral, what is the cost and
    # weight reduction, in percentage?
    # Practical gears an adjust these.
    INTEGRAL_COST_REDUCTION = 0.0
    INTEGRAL_MASS_REDUCTION = 0.0

    INTEGRAL_BY_DEFAULT = False

    def __init__(self, **keywords):
        self.integral = keywords.pop('integral', self.INTEGRAL_BY_DEFAULT)
        super(Component, self).__init__(**keywords)

    def can_normally_remove(self):
        return not self.integral

    @property
    def self_cost(self):
        normal_cost = super(Component, self).self_cost
        if not self.integral:
            return normal_cost
        return int((normal_cost * (100.0 - self.INTEGRAL_COST_REDUCTION)) / 100.0)

    @property
    def self_mass(self):
        normal_mass = super(Component, self).self_mass
        if not self.integral:
            return normal_mass
        return int((normal_mass * (100.0 - self.INTEGRAL_MASS_REDUCTION)) / 100.0)

    @property
    def volume(self):
        normal_volume = super(Component, self).volume
        if not self.integral or normal_volume <= 1:
            return normal_volume
        return normal_volume - 1


# Size-classed components are Components which
# append their size, material, and integral-ness
# to their full names
class SizeClassedComponent(Component):
    def __init__(self, **keywords):
        super(SizeClassedComponent, self).__init__(**keywords)

    def get_full_name(self):
        basename = super(SizeClassedComponent, self).get_full_name()
        code = str(self.size)
        if not ((self.material is None) or (self.material is materials.Metal)):
            if hasattr(self.material, 'desig'):
                code = code + self.material.desig
        if self.integral:
            code = code + 'i'
        return '{} {}'.format(basename, code)


#
#  Practical Gears
#

#   *****************
#   ***   ARMOR   ***
#   *****************

class Armor(SizeClassedComponent, StandardDamageHandler):
    DEFAULT_NAME = "Armor"
    SAVE_PARAMETERS = ('size',)
    MIN_SIZE = 1
    MAX_SIZE = 25

    # Armor that is shaped specifically to the module it's on
    # can be cheaper/require less material than armor that
    # can be removed and installed elsewhere.
    INTEGRAL_COST_REDUCTION = 20.0

    def __init__(self, size=1, **keywords):
        # Check the range of all parameters before applying.
        if size < self.MIN_SIZE:
            size = self.MIN_SIZE
        elif size > self.MAX_SIZE:
            size = self.MAX_SIZE
        self.size = size
        super(Armor, self).__init__(**keywords)

    @property
    def base_mass(self):
        return 9 * self.size

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    @property
    def base_volume(self):
        return self.size

    @property
    def base_cost(self):
        return 55 * self.size

    def get_armor(self):
        """Returns the armor protecting this gear."""
        return self

    def get_armor_rating(self):
        """Returns the penetration rating of this armor."""
        arat = (self.size * 10) * (self.max_health - self.hp_damage) // self.max_health
        myroot = self.get_root()
        if myroot and hasattr(myroot, "form") and hasattr(myroot.form, "modify_armor"):
            arat = myroot.form.modify_armor(arat)
        return arat

    def reduce_damage(self, dmg, dmg_request):
        """Armor reduces damage taken, but gets damaged in the process."""
        if dmg_request.is_brutal:
            max_absorb = min(self.scale.scale_health(3, self.material), dmg)
            absorb_amount = random.randint(max_absorb // 2, max_absorb)
        else:
            max_absorb = min(self.scale.scale_health(2, self.material), dmg)
            absorb_amount = random.randint(max_absorb // 5, max_absorb)
        if absorb_amount > 0:
            self.hp_damage = min(self.hp_damage + absorb_amount, self.max_health)
            dmg -= 2 * absorb_amount
        return dmg


class Shield(BaseGear, StandardDamageHandler):
    DEFAULT_NAME = "Shield"
    DEFAULT_SLOT = tags.SLOT_SHIELD
    SAVE_PARAMETERS = ('size', 'bonus')
    MIN_SIZE = 1
    MAX_SIZE = 10
    MIN_BONUS = 0
    MAX_BONUS = 5

    def __init__(self, size=3, bonus=0, **keywords):
        # Check the range of all parameters before applying.
        if size < self.MIN_SIZE:
            size = self.MIN_SIZE
        elif size > self.MAX_SIZE:
            size = self.MAX_SIZE
        self.size = size
        if bonus < self.MIN_BONUS:
            bonus = self.MIN_BONUS
        elif bonus > self.MAX_BONUS:
            bonus = self.MAX_BONUS
        self.bonus = bonus
        super(Shield, self).__init__(**keywords)

    @property
    def base_mass(self):
        return 8 * self.size

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    @property
    def base_volume(self):
        return max(self.size - self.bonus + 1, 1)

    @property
    def base_cost(self):
        return (100 * self.size * (1 + self.bonus)) // 2

    def is_legal_sub_com(self, part):
        if isinstance(part, Weapon):
            return part.integral
        else:
            return False

    def get_block_bonus(self):
        return self.bonus * 5

    def pay_for_block(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        if weapon_being_blocked:
            self.hp_damage += random.randint(1, weapon_being_blocked.scale.scale_health(1, materials.Metal))

    def is_operational(self):
        """ To be operational, a shield must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def get_aim_bonus(self):
        return -5 * (self.bonus + 1)

    def get_item_stats(self):
        return (('Block Bonus', str(self.get_block_bonus()))
                ,
                )


class BeamShield(Shield):
    # Just like a shield, but beamier.
    DEFAULT_NAME = "Beam Shield"

    @property
    def base_mass(self):
        return 4 * self.size

    @property
    def base_cost(self):
        return (250 * self.size * (1 + self.bonus)) // 2

    def is_legal_sub_com(self, part):
        return False

    def pay_for_block(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        if weapon_being_blocked:
            self.hp_damage += random.randint(1, weapon_being_blocked.scale.scale_health(1, materials.Metal))
            if isinstance(weapon_being_blocked, (MeleeWeapon, EnergyWeapon, Module)):
                weapon_being_blocked.hp_damage += random.randint(1, self.scale.scale_health(2, materials.Metal))


#   ****************************
#   ***   SUPPORT  SYSTEMS   ***
#   ****************************

class Engine(Component, StandardDamageHandler, MakesPower):
    DEFAULT_NAME = "Engine"
    SAVE_PARAMETERS = ('size',)

    MIN_SIZE = 100
    MAX_SIZE = 2000

    # We save on cooling tubes and power cables when we integrate
    # the engine directly to the mecha, so give cost and mass reduction.
    INTEGRAL_COST_REDUCTION = 25.0
    INTEGRAL_MASS_REDUCTION = 25.0

    def __init__(self, size=750, **keywords):
        # Check the range of all parameters before applying.
        if size < self.MIN_SIZE:
            size = self.MIN_SIZE
        elif size > self.MAX_SIZE:
            size = self.MAX_SIZE
        self.size = size
        super(Engine, self).__init__(**keywords)

    @property
    def base_mass(self):
        return self.size // 100 + 10

    @property
    def base_volume(self):
        return self.size // 400 + 1

    @property
    def base_cost(self):
        return (self.size ** 3) // 100000 + (self.size ** 2) // 80 - 2 * self.size + 100

    base_health = 3

    def is_legal_sub_com(self, part):
        return isinstance(part, Armor)

    def on_destruction(self, camp, anim_list):
        my_root = self.get_root()
        my_invo = pbge.effects.Invocation(
            fx=geffects.DoDamage(3, self.size // 200 + 2, anim=geffects.SuperBoom, scale=self.scale, is_brutal=True),
            area=pbge.scenes.targetarea.SelfCentered(radius=self.size // 600 + 1, delay_from=-1))
        my_invo.invoke(camp, None, [my_root.pos, ], anim_list)

    def is_operational(self):
        """ To be operational, an engine must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def max_power(self):
        return self.scale.scale_power(self.size // 25)

    def get_item_stats(self):
        return (("Rating", str(self.size))
                , ("Power", str(self.max_power()))
                )


class Gyroscope(Component, StandardDamageHandler):
    DEFAULT_NAME = "Gyroscope"
    base_mass = 10
    INTEGRAL_BY_DEFAULT = True

    def is_legal_sub_com(self, part):
        return isinstance(part, Armor)

    base_volume = 3
    base_cost = 10
    base_health = 2


class Cockpit(Component, StandardDamageHandler):
    DEFAULT_NAME = "Cockpit"
    base_mass = 5

    def is_legal_sub_com(self, part):
        return isinstance(part, (Armor, Character))

    def can_install(self, part, check_volume=True):
        if isinstance(part, Character):
            # Only one character per cockpit.
            return len([item for item in self.sub_com if isinstance(item, Character)]) < 1
        else:
            if check_volume:
                return self.is_legal_sub_com(
                    part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR and self.check_multiplicity(
                    part) and self.free_volume >= part.volume
            else:
                return self.is_legal_sub_com(part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR

    base_volume = 2
    base_cost = 5
    base_health = 2


class Sensor(SizeClassedComponent, StandardDamageHandler):
    DEFAULT_NAME = "Sensor"
    SAVE_PARAMETERS = ('size',)
    MIN_SIZE = 1
    MAX_SIZE = 5

    def __init__(self, size=1, **keywords):
        # Check the range of all parameters before applying.
        if size < self.MIN_SIZE:
            size = self.MIN_SIZE
        elif size > self.MAX_SIZE:
            size = self.MAX_SIZE
        self.size = size
        super(Sensor, self).__init__(**keywords)

    @property
    def base_mass(self):
        return self.size * 5

    @property
    def base_cost(self):
        return self.size * self.size * 10

    @property
    def base_volume(self):
        return self.size

    base_health = 2

    def get_sensor_rating(self):
        it = self.size
        mymod = self.get_module()
        if mymod:
            it += mymod.form.SENSOR_BONUS
        return it * self.scale.RANGE_FACTOR


#   *****************************
#   ***   MOVEMENT  SYSTEMS   ***
#   *****************************

class MovementSystem(SizeClassedComponent):
    DEFAULT_NAME = "MoveSys"
    SAVE_PARAMETERS = ('size',)

    def __init__(self, size=1, **keywords):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        self.size = size
        super(MovementSystem, self).__init__(**keywords)

    @property
    def base_mass(self):
        size = min(21, self.size)
        return 10 * size - ((size * (size - 1) + 3) // 4)

    @property
    def base_volume(self):
        return self.size

    @property
    def base_cost(self):
        return ( self.size * self.MOVESYS_COST
               + self.size * (self.size - 1) * self.MOVESYS_COST // 10
               )

    def get_item_stats(self):
        stat = [('Thrust ({})'.format(mode.get_short_name()), str(self.get_thrust(mode)))
                for mode in [scenes.movement.Walking
                    , geffects.Rolling
                    , geffects.Skimming
                    , scenes.movement.Flying
                    , geffects.SpaceFlight
                             ]
                if self.get_thrust(mode) > 0
                ]
        if hasattr(self, 'get_speed_bonus_percent'):
            stat += [('Speed Bonus', '+{}%'.format(self.get_speed_bonus_percent()))]
        return stat


class HoverJets(MovementSystem, StandardDamageHandler):
    DEFAULT_NAME = "Hover Jets"
    MOVESYS_COST = 56

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    def get_thrust(self, move_mode):
        if move_mode is geffects.Skimming:
            return (self.size * 4000 * self.current_health + self.max_health - 1) // self.max_health
        elif move_mode is geffects.SpaceFlight:
            return (self.size * 3700 * self.current_health + self.max_health - 1) // self.max_health
        elif move_mode is scenes.movement.Flying:
            return (self.size * 500 * self.current_health + self.max_health - 1) // self.max_health
        else:
            return 0


class Wheels(MovementSystem, StandardDamageHandler):
    DEFAULT_NAME = "Wheels"
    MOVESYS_COST = 10

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    def get_thrust(self, move_mode):
        if move_mode is geffects.Rolling:
            return (self.size * 4000 * self.current_health + self.max_health - 1) // self.max_health
        else:
            return 0

    @property
    def base_mass(self):
        normal_mass = super().base_mass
        return normal_mass // 2


class Tracks(MovementSystem, StandardDamageHandler):
    DEFAULT_NAME = "Tracks"
    MOVESYS_COST = 10

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size * 2

    def get_thrust(self, move_mode):
        if move_mode is geffects.Rolling:
            return (self.size * 4000 * self.current_health + self.max_health - 1) // self.max_health
        else:
            return 0


class HeavyActuators(MovementSystem, StandardDamageHandler):
    DEFAULT_NAME = "Heavy Actuators"
    MOVESYS_COST = 100

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    def get_thrust(self, move_mode):
        if move_mode is scenes.movement.Walking:
            return (self.size * 1250 * self.current_health + self.max_health - 1) // self.max_health
        else:
            return 0

    def get_melee_damage_bonus(self):
        return max(self.size//2, 1)


class Overchargers(MovementSystem, StandardDamageHandler):
    DEFAULT_NAME = "Overchargers"
    MOVESYS_COST = 250

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return max(1, self.size // 2)

    @property
    def base_mass(self):
        normal_mass = super().base_mass
        return normal_mass // 2

    def get_thrust(self, move_mode):
        return 0

    def get_speed_bonus_percent(self):
        return 7 * self.size


#   *************************
#   ***   POWER  SOURCE   ***
#   *************************

class PowerSource(Component, StandardDamageHandler, MakesPower):
    DEFAULT_NAME = "Power Source"
    SAVE_PARAMETERS = ('size',)

    def __init__(self, size=1, **keywords):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        self.size = size
        super().__init__(**keywords)

    @property
    def base_mass(self):
        return 5 * self.size

    @property
    def base_volume(self):
        return self.size

    @property
    def base_cost(self):
        return self.size * 75

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    def is_operational(self):
        """ To be operational, a power source must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def max_power(self):
        return self.scale.scale_power(self.size * 5)

    def get_item_stats(self):
        return (('Power', str(self.max_power())),)


#   *********************************
#   ***   COMPUTERS AND EW GEAR   ***
#   *********************************

class EWSystem(Component, StandardDamageHandler):
    DEFAULT_NAME = "EW System"
    SAVE_PARAMETERS = ('size', 'programs')

    def __init__(self, size=1, programs=(), **keywords):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        self.size = size
        self.programs = list(programs)
        if len(self.programs) > self.size:
            self.programs = self.programs[:self.size]
        super(EWSystem, self).__init__(**keywords)

    @property
    def base_mass(self):
        return 2 * self.size

    @property
    def base_volume(self):
        return self.size

    @property
    def base_cost(self):
        return self.size * 125 + sum(p.COST for p in self.programs if hasattr(p, 'COST'))

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

    def is_operational(self):
        """ To be operational, an EW System must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def add_program_invocations(self, pc, invodict):
        for p in self.programs:
            if p not in invodict:
                invodict[p] = p.get_invocations(pc)

    def get_ewar_rating(self):
        return self.size


#   *******************
#   ***   WEAPONS   ***
#   *******************

class Weapon(Component, StandardDamageHandler):
    DEFAULT_NAME = "Weapon"
    SAVE_PARAMETERS = (
        'reach', 'damage', 'accuracy', 'penetration', 'attack_stat', 'shot_anim', 'area_anim', 'attributes')
    DEFAULT_SHOT_ANIM = None
    DEFAULT_AREA_ANIM = geffects.BigBoom
    LEGAL_ATTRIBUTES = ()

    # Note that this class doesn't implement any MIN_*,MAX_* constants, so it
    # cannot be instantiated. Subclasses should do that.
    def __init__(self, reach=1, damage=1, accuracy=1, penetration=1, attack_stat=stats.Reflexes, shot_anim=None,
                 area_anim=None, attributes=(), **keywords):
        # Check the range of all parameters before applying.
        if reach < self.__class__.MIN_REACH:
            reach = self.__class__.MIN_REACH
        elif reach > self.__class__.MAX_REACH:
            reach = self.__class__.MAX_REACH
        self.reach = reach

        if damage < self.__class__.MIN_DAMAGE:
            damage = self.__class__.MIN_DAMAGE
        elif damage > self.__class__.MAX_DAMAGE:
            damage = self.__class__.MAX_DAMAGE
        self.damage = damage

        if accuracy < self.__class__.MIN_ACCURACY:
            accuracy = self.__class__.MIN_ACCURACY
        elif accuracy > self.__class__.MAX_ACCURACY:
            accuracy = self.__class__.MAX_ACCURACY
        self.accuracy = accuracy

        if penetration < self.__class__.MIN_PENETRATION:
            penetration = self.__class__.MIN_PENETRATION
        elif penetration > self.__class__.MAX_PENETRATION:
            penetration = self.__class__.MAX_PENETRATION
        self.penetration = penetration

        self.attack_stat = attack_stat
        self.shot_anim = shot_anim or self.DEFAULT_SHOT_ANIM
        self.area_anim = area_anim or self.DEFAULT_AREA_ANIM
        self.attributes = list()
        for a in attributes:
            if a in self.LEGAL_ATTRIBUTES:
                self.attributes.append(a)

        # Finally, call the gear initializer.
        super(Weapon, self).__init__(**keywords)

    @property
    def base_mass(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.MASS_MODIFIER
        return int(((self.damage + self.penetration) * 5 + self.accuracy + self.reach) * mult)

    ## Should not happen, since Weapon overrides volume directly.
    @property
    def base_volume(self):
        raise Exception('Weapon.base_volume called!')

    @property
    def volume(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.VOLUME_MODIFIER
        v = max(self.reach + self.accuracy + (self.damage + self.penetration) // 2, 1)
        # Our own handling of integral weapon volume.
        if self.integral:
            v -= 1
        return max((int(v * mult) + 1) // 2, 1)

    @property
    def base_cost(self):
        # Multiply the stats together, squaring damage and range because they're so important.
        reach = self.reach

        mult = 1.0
        for aa in self.attributes:
            mult *= aa.COST_MODIFIER
            if hasattr(aa, 'COST_EFFECTIVE_REACH_MIN') and reach < aa.COST_EFFECTIVE_REACH_MIN:
                reach = aa.COST_EFFECTIVE_REACH_MIN
        return int(
            (self.COST_FACTOR * (self.damage ** 2) *
             (self.accuracy ** 2 // 10 + self.accuracy + 1) *
             (self.penetration ** 2 // 5 + self.penetration + 1) *
             ((reach ** 2 - reach) // 2 + 1)) * mult
        )

    def is_legal_sub_com(self, part):
        if isinstance(part, Weapon):
            return part.integral
        else:
            return False

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return max(self.base_mass // 5, 2)

    def is_operational(self):
        """ To be operational, a weapon must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def get_attack_skill(self):
        return self.scale.RANGED_SKILL

    def get_defenses(self):
        return {geffects.DODGE: geffects.DodgeRoll(), geffects.BLOCK: geffects.BlockRoll(self)}

    def get_modifiers(self):
        return (self.get_common_modifiers(self.get_module())
                + self.get_ranged_modifiers(self.reach)
                )

    def get_basic_attack(self):
        ba = pbge.effects.Invocation(
            name='Basic Attack',
            fx=geffects.AttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale),),
                accuracy=self.accuracy * 10, penetration=self.penetration * 10,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach * 3),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.shot_anim,
            price=[geffects.RevealPositionPrice(self.damage)],
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 0,
                                     thrill_power=self.damage * 2 + self.penetration),
            targets=1)
        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def get_attributes(self):
        return self.attributes

    def get_primary_attacks(self):
        # Normally, the primary attack will be the basic attack as above.
        # However, certain attack attributes may replace the primary attack...
        # If more than one replacement exists, provide them all.
        default = [self.get_basic_attack()]
        modified = list()
        for aa in self.get_attributes():
            if hasattr(aa, 'replace_primary_attack'):
                modified += aa.replace_primary_attack(self)
        return modified or default

    def get_attacks(self):
        # Return a list of invocations associated with this weapon.
        # Being a weapon, the invocations are likely to all be attacks.
        my_invos = self.get_primary_attacks()

        for aa in self.attributes:
            if hasattr(aa, 'get_attacks'):
                my_invos += aa.get_attacks(self)

        return my_invos

    def get_area_anim(self):
        return self.area_anim

    def get_reach_str(self):
        rstr = None
        for aa in self.get_attributes():
            if hasattr(aa, "get_reach_str"):
                rstr = aa.get_reach_str(self)
                break
        if not rstr:
            rstr = '{}-{}-{}'.format(self.reach, self.reach * 2, self.reach * 3)
        return rstr


class MeleeWeapon(Weapon):
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 3
    LEGAL_ATTRIBUTES = (attackattributes.Accurate, attackattributes.Brutal, attackattributes.IgnitesAmmo,
                        attackattributes.ChargeAttack,
                        attackattributes.Defender, attackattributes.FastAttack, attackattributes.Flail,
                        attackattributes.HaywireAttack,
                        attackattributes.OverloadAttack, attackattributes.Smash, attackattributes.DrainsPower,
                        attackattributes.MultiWielded)

    def get_attack_skill(self):
        return self.scale.MELEE_SKILL

    def get_modifiers(self):
        return (self.get_common_modifiers(self.get_module())
                + self.get_melee_modifiers()
                )

    def get_damage_bonus(self):
        myroot = self.get_root()
        if hasattr(myroot, "get_melee_damage_bonus"):
            return myroot.get_melee_damage_bonus(self)

    def get_basic_attack(self, name='Basic Attack', attack_icon=0, targets=1):
        ba = pbge.effects.Invocation(
            name=name,
            fx=geffects.MeleeAttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale, damage_bonus=self.get_damage_bonus()),),
                accuracy=self.accuracy * 10, penetration=self.penetration * 10,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.shot_anim,
            price=[geffects.RevealPositionPrice(self.damage - 1)],
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), attack_icon,
                                     thrill_power=(self.damage * 2 + self.penetration) * targets),
            targets=targets)
        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def get_defenses(self):
        return {geffects.DODGE: geffects.DodgeRoll(), geffects.BLOCK: geffects.BlockRoll(self),
                geffects.PARRY: geffects.ParryRoll(self)}

    def get_weapon_desc(self):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}'.format(
            self)

    def can_parry(self):
        it = True
        for aa in self.get_attributes():
            if hasattr(aa, 'NO_PARRY') and aa.NO_PARRY:
                it = False
                break
        return it

    def get_parry_bonus(self):
        it = self.accuracy * 10
        for aa in self.get_attributes():
            if hasattr(aa, 'PARRY_BONUS'):
                it += aa.PARRY_BONUS
        return it

    def pay_for_parry(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        if weapon_being_blocked:
            self.hp_damage += random.randint(1, weapon_being_blocked.scale.scale_health(1, materials.Metal))

    def get_reach_str(self):
        rstr = None
        for aa in self.get_attributes():
            if hasattr(aa, "get_reach_str"):
                rstr = aa.get_reach_str(self)
                break
        if not rstr:
            rstr = '{}'.format(self.reach)
        return rstr


class EnergyWeapon(Weapon):
    # Energy weapons do "hot knife" damage. It gets reduced by, but not stopped
    # by, armor.
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 12
    LEGAL_ATTRIBUTES = (attackattributes.Accurate, attackattributes.IgnitesAmmo, attackattributes.ChargeAttack,
                        attackattributes.Defender, attackattributes.FastAttack, attackattributes.Flail,
                        attackattributes.Intercept, attackattributes.OverloadAttack, attackattributes.DrainsPower,
                        attackattributes.MultiWielded)

    def get_attack_skill(self):
        return self.scale.MELEE_SKILL

    def get_modifiers(self):
        return (self.get_common_modifiers(self.get_module())
                + self.get_melee_modifiers()
                )

    def get_basic_power_cost(self):
        mult = 0.25
        for aa in self.get_attributes():
            mult *= aa.POWER_MODIFIER
        return max(int(self.scale.scale_power(self.damage) * mult), 1)

    def get_damage_bonus(self):
        myroot = self.get_root()
        if hasattr(myroot, "get_melee_damage_bonus"):
            return myroot.get_melee_damage_bonus(self)

    def get_basic_attack(self, name='Basic Attack', attack_icon=0):
        ba = pbge.effects.Invocation(
            name=name,
            fx=geffects.MeleeAttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale, hot_knife=True, damage_bonus=self.get_damage_bonus()),),
                accuracy=self.accuracy * 10, penetration=self.penetration * 10,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.shot_anim,
            price=[geffects.PowerPrice(self.get_basic_power_cost()), geffects.RevealPositionPrice(self.damage)],
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), attack_icon,
                                     thrill_power=self.damage * 2 + self.penetration + 3),
            targets=1)
        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def get_defenses(self):
        return {geffects.DODGE: geffects.DodgeRoll(), geffects.BLOCK: geffects.BlockRoll(self),
                geffects.PARRY: geffects.ParryRoll(self)}

    def get_weapon_desc(self):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}'.format(
            self)

    def can_parry(self):
        it = True
        for aa in self.get_attributes():
            if hasattr(aa, 'NO_PARRY') and aa.NO_PARRY:
                it = False
                break
        return it

    def get_parry_bonus(self):
        it = self.accuracy * 10
        for aa in self.get_attributes():
            if hasattr(aa, 'PARRY_BONUS'):
                it += aa.PARRY_BONUS
        return it

    def pay_for_parry(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        if weapon_being_blocked:
            self.hp_damage += random.randint(1, weapon_being_blocked.scale.scale_health(1, materials.Metal))
            if isinstance(weapon_being_blocked, (MeleeWeapon, EnergyWeapon, Module)):
                weapon_being_blocked.hp_damage += random.randint(1, self.scale.scale_health(2, materials.Metal))

    def can_intercept(self):
        it = False
        for aa in self.get_attributes():
            if hasattr(aa, 'CAN_INTERCEPT') and aa.CAN_INTERCEPT:
                it = True
                break
        if it:
            actor = self.get_root()
            c, m = actor.get_current_and_max_power()
            if c < self.get_basic_power_cost():
                it = False
        return it

    def get_intercept_bonus(self):
        it = self.accuracy * 10
        return it

    def pay_for_intercept(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        defender.consume_power(self.get_basic_power_cost())

    def get_reach_str(self):
        rstr = None
        for aa in self.get_attributes():
            if hasattr(aa, "get_reach_str"):
                rstr = aa.get_reach_str(self)
                break
        if not rstr:
            rstr = '{}'.format(self.reach)
        return rstr


class Ammo(BaseGear, Stackable, StandardDamageHandler, Restoreable):
    DEFAULT_NAME = "Ammo"
    STACK_CRITERIA = ("ammo_type", 'attributes')
    SAVE_PARAMETERS = ('ammo_type', 'quantity', 'area_anim', 'attributes')
    LEGAL_ATTRIBUTES = (attackattributes.Blast1, attackattributes.Blast2, attackattributes.Brutal,
                        attackattributes.BurnAttack, attackattributes.HaywireAttack,
                        attackattributes.OverloadAttack, attackattributes.Scatter,
                        )

    def __init__(self, ammo_type=calibre.Shells_150mm, quantity=12, area_anim=None, attributes=(), **keywords):
        # Check the range of all parameters before applying.
        self.ammo_type = ammo_type
        self.quantity = max(quantity, 1)
        self.spent = 0
        self.area_anim = area_anim
        self.attributes = list()
        for a in attributes:
            if a in self.LEGAL_ATTRIBUTES:
                self.attributes.append(a)

        # Finally, call the gear initializer.
        super(Ammo, self).__init__(**keywords)

    @property
    def base_mass(self):
        mult = 1.0
        for aa in self.attributes:
            # Gonna cube the mass multiplier since ammo doesn't usually weigh that much,
            # and we need this modifier to make a difference.
            mult *= max(aa.MASS_MODIFIER ** 3, 1.0)
        return int(mult * self.ammo_type.bang * (self.quantity - self.spent) // 25)

    @staticmethod
    def ammo_volume(ammo_type, quantity):
        return int((ammo_type.bang * quantity + 49) // 50)

    @property
    def base_volume(self):
        # Ammo volume is not adjusted for attack attributes- instead, that goes tacked onto the cost.
        return self.ammo_volume(self.ammo_type, self.quantity)

    @property
    def base_cost(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.COST_MODIFIER * max(aa.VOLUME_MODIFIER, 1.0)
        return int(mult * self.ammo_type.bang * self.quantity // 10)

    base_health = 1

    def get_item_stats(self):
        # Provide info on the ammo.
        return (('Ammo', '{}/{}'.format(self.quantity - self.spent, self.quantity)),)

    def get_reload_cost(self):
        return (self.cost * self.spent) // self.quantity

    def restore(self):
        ac = self.get_reload_cost()
        self.spent = 0
        return ac + super(Ammo, self).restore()


class BallisticWeapon(Weapon):
    MIN_REACH = 2
    MAX_REACH = 9
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 5
    SAVE_PARAMETERS = ('ammo_type', 'magazine')
    DEFAULT_CALIBRE = calibre.Shells_150mm
    DEFAULT_SHOT_ANIM = geffects.BigBullet
    LEGAL_ATTRIBUTES = (attackattributes.Accurate, attackattributes.Automatic, attackattributes.BurstFire2,
                        attackattributes.BurstFire3, attackattributes.BurstFire4, attackattributes.BurstFire5,
                        attackattributes.VariableFire3, attackattributes.VariableFire4, attackattributes.VariableFire5,
                        attackattributes.Intercept, attackattributes.LinkedFire
                        )

    def __init__(self, ammo_type=None, magazine=None, **keywords):
        self.ammo_type = ammo_type or self.DEFAULT_CALIBRE

        if magazine:
            self.magazine = magazine
        else:
            self.magazine = 20
            # Check the sub-coms, see if a magazine has been added.
            sc = keywords.get("sub_com")
            if sc:
                for a in sc:
                    if isinstance(a, Ammo):
                        self.magazine = a.quantity
                        break

        # Finally, call the gear initializer.
        super(BallisticWeapon, self).__init__(**keywords)

    def is_legal_sub_com(self, part):
        if isinstance(part, Weapon):
            return part.integral
        else:
            return isinstance(part, Ammo) and part.ammo_type is self.ammo_type and part.quantity <= self.magazine

    def get_ammo(self):
        for maybe_ammo in self.sub_com:
            if isinstance(maybe_ammo, Ammo):
                return maybe_ammo

    def get_attributes(self):
        ammo = self.get_ammo()
        if ammo:
            return self.attributes + ammo.attributes
        else:
            return self.attributes

    def get_needed_bang(self):
        return self.damage * max(self.penetration, 1)

    def get_basic_attack(self, targets=1, name='Basic Attack', ammo_cost=1, attack_icon=0):
        # Check the ammunition. If it doesn't have enough bang, downgrade the attack.
        my_ammo = self.get_ammo()
        penetration = self.penetration * 10
        if my_ammo.ammo_type.bang < self.get_needed_bang():
            penetration -= (self.damage * max(self.penetration, 1) - my_ammo.ammo_type.bang) * 15

        ba = pbge.effects.Invocation(
            name=name,
            fx=geffects.AttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale),),
                accuracy=self.accuracy * 10, penetration=penetration,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach * 3),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.shot_anim,
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), attack_icon,
                                     thrill_power=((self.damage * 2 + self.penetration)* (targets+1))//2),
            price=[geffects.AmmoPrice(my_ammo, ammo_cost), geffects.RevealPositionPrice(self.damage)],
            targets=targets)

        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def get_ammo_string(self):
        ammo = self.get_ammo()
        if ammo:
            return 'Ammo: {}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)
        else:
            return 'Ammo: 0'

    def get_weapon_desc(self):
        ammo = self.get_ammo()
        it = 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {1}\n {2}'.format(
            self,
            self.get_reach_str(), self.get_ammo_string())

        return it

    def get_item_stats(self):
        # Provide info on the ammo.
        ammo = self.get_ammo()
        if ammo:
            return (('Ammo', '{}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)),)
        else:
            return (('Ammo', '0'),)

    def can_intercept(self):
        it = False
        for aa in self.get_attributes():
            if hasattr(aa, 'CAN_INTERCEPT') and aa.CAN_INTERCEPT:
                it = True
                break
        if it:
            ammo = self.get_ammo()
            if not ammo or ammo.spent >= ammo.quantity:
                it = False
        return it

    def get_intercept_bonus(self):
        it = self.accuracy * 10
        return it

    def pay_for_intercept(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        ammo = self.get_ammo()
        if ammo:
            ammo.spent += 1

    def get_area_anim(self):
        ammo = self.get_ammo()
        if ammo and ammo.area_anim:
            return ammo.area_anim
        else:
            return self.area_anim

    @property
    def volume(self):
        base = super().volume
        return max(base, Ammo.ammo_volume(self.ammo_type, self.magazine))


class BeamWeapon(Weapon):
    MIN_REACH = 2
    MAX_REACH = 9
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 15
    DEFAULT_SHOT_ANIM = geffects.GunBeam
    LEGAL_ATTRIBUTES = (attackattributes.Accurate, attackattributes.Automatic, attackattributes.Brutal,
                        attackattributes.BurstFire2,
                        attackattributes.BurstFire3, attackattributes.BurstFire4, attackattributes.BurstFire5,
                        attackattributes.OverloadAttack, attackattributes.LinkedFire,
                        attackattributes.Scatter, attackattributes.VariableFire3, attackattributes.VariableFire4,
                        attackattributes.VariableFire5,
                        attackattributes.Intercept, attackattributes.SwarmFire2, attackattributes.SwarmFire3
                        )

    def get_weapon_desc(self):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {1}'.format(self,
                                                                                                                self.get_reach_str())

    def get_basic_power_cost(self):
        mult = 0.5
        for aa in self.get_attributes():
            mult *= aa.POWER_MODIFIER
        return max(int(self.scale.scale_power(self.damage) * mult), 1)

    def get_basic_attack(self, targets=1, name='Basic Attack', ammo_cost=1, attack_icon=0):
        # Check the ammunition. If it doesn't have enough bang, downgrade the attack.
        ba = pbge.effects.Invocation(
            name=name,
            fx=geffects.AttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale),),
                accuracy=self.accuracy * 10, penetration=self.penetration * 10,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach * 3),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.shot_anim,
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), attack_icon,
                                     thrill_power=((self.damage * 2 + self.penetration)* (targets+1))//2),
            price=[geffects.PowerPrice(self.get_basic_power_cost() * ammo_cost),
                   geffects.RevealPositionPrice(self.damage)],
            targets=targets)
        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def can_intercept(self):
        it = False
        for aa in self.get_attributes():
            if hasattr(aa, 'CAN_INTERCEPT') and aa.CAN_INTERCEPT:
                it = True
                break
        if it:
            actor = self.get_root()
            c, m = actor.get_current_and_max_power()
            if c < self.get_basic_power_cost():
                it = False
        return it

    def get_intercept_bonus(self):
        it = self.accuracy * 10
        return it

    def pay_for_intercept(self, defender, weapon_being_blocked):
        defender.spend_stamina(1)
        defender.consume_power(self.get_basic_power_cost())


class Missile(BaseGear, StandardDamageHandler, Restoreable):
    DEFAULT_NAME = "Missile"
    SAVE_PARAMETERS = ('reach', 'damage', 'accuracy', 'penetration', 'quantity', 'area_anim', 'attributes')
    MIN_REACH = 2
    MAX_REACH = 10
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    STACK_CRITERIA = ("reach", "damage", "accuracy", "penetration")
    LEGAL_ATTRIBUTES = (attackattributes.Blast1, attackattributes.Blast2, attackattributes.Brutal,
                        attackattributes.BurnAttack, attackattributes.HaywireAttack, attackattributes.OverloadAttack,
                        attackattributes.Scatter,
                        )

    def __init__(self, reach=1, damage=1, accuracy=1, penetration=1, quantity=12, area_anim=None, attributes=(),
                 **keywords):
        # Check the range of all parameters before applying.
        if reach < self.__class__.MIN_REACH:
            reach = self.__class__.MIN_REACH
        elif reach > self.__class__.MAX_REACH:
            reach = self.__class__.MAX_REACH
        self.reach = reach

        if damage < self.__class__.MIN_DAMAGE:
            damage = self.__class__.MIN_DAMAGE
        elif damage > self.__class__.MAX_DAMAGE:
            damage = self.__class__.MAX_DAMAGE
        self.damage = damage

        if accuracy < self.__class__.MIN_ACCURACY:
            accuracy = self.__class__.MIN_ACCURACY
        elif accuracy > self.__class__.MAX_ACCURACY:
            accuracy = self.__class__.MAX_ACCURACY
        self.accuracy = accuracy

        if penetration < self.__class__.MIN_PENETRATION:
            penetration = self.__class__.MIN_PENETRATION
        elif penetration > self.__class__.MAX_PENETRATION:
            penetration = self.__class__.MAX_PENETRATION
        self.penetration = penetration

        self.quantity = max(quantity, 1)
        self.spent = 0
        self.area_anim = area_anim

        self.attributes = list()
        for a in attributes:
            if a in self.LEGAL_ATTRIBUTES:
                self.attributes.append(a)

        # Finally, call the gear initializer.
        super(Missile, self).__init__(**keywords)

    @property
    def base_mass(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.MASS_MODIFIER

        return int(((((self.damage + self.penetration) * 5 + self.accuracy + self.reach) * (
                self.quantity - self.spent)) // 25) * mult)

    @property
    def base_volume(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.VOLUME_MODIFIER
        return max(1, int(
            (((self.reach * self.damage * (self.accuracy + self.penetration) + 1) * self.quantity) / 100) * mult))

    @property
    def base_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.COST_MODIFIER
        return int((((self.damage ** 2) * (self.accuracy + 1) * (self.penetration + 1) * (
                self.reach ** 2 - self.reach + 2)) * self.quantity // 8) * mult)

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.volume // 2 + 1

    def get_item_stats(self):
        # Provide info on the ammo.
        return (('Missiles', '{}/{}'.format(self.quantity - self.spent, self.quantity)),)

    def get_reach_str(self):
        rstr = None
        for aa in self.attributes:
            if hasattr(aa, "get_reach_str"):
                rstr = aa.get_reach_str(self)
                break
        if not rstr:
            rstr = '{}-{}-{}'.format(self.reach, self.reach * 2, self.reach * 3)
        return rstr

    def get_reload_cost(self):
        return (self.cost * self.spent) // self.quantity

    def restore(self):
        ac = self.get_reload_cost()
        self.spent = 0
        return ac + super(Missile, self).restore()


class Launcher(BaseGear, ContainerDamageHandler):
    DEFAULT_NAME = "Launcher"
    SAVE_PARAMETERS = ('size', 'attack_stat')
    MIN_SIZE = 1
    MAX_SIZE = 20

    def __init__(self, size=5, attack_stat=stats.Perception, **keywords):
        # Check the range of all parameters before applying.
        if size < self.MIN_SIZE:
            size = self.MIN_SIZE
        elif size > self.MAX_SIZE:
            size = self.MAX_SIZE
        self.size = size
        self.attack_stat = attack_stat
        super(Launcher, self).__init__(**keywords)

    @property
    def base_mass(self):
        return self.size

    @property
    def base_volume(self):
        return self.size

    @property
    def base_cost(self):
        return self.size * 25

    def is_legal_sub_com(self, part):
        return isinstance(part, Missile) and part.volume <= self.volume

    def get_attack_skill(self):
        return self.scale.RANGED_SKILL

    def get_ammo(self):
        for maybe_ammo in self.sub_com:
            if isinstance(maybe_ammo, Missile):
                return maybe_ammo

    def is_operational(self):
        """ To be operational, a launcher must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def get_defenses(self):
        return {geffects.DODGE: geffects.DodgeRoll(), geffects.BLOCK: geffects.BlockRoll(self),
                geffects.INTERCEPT: geffects.InterceptRoll(self)}

    def get_modifiers(self, ammo):
        return (self.get_common_modifiers(self.get_module())
                + self.get_ranged_modifiers(ammo.reach)
                )

    def get_attributes(self):
        ammo = self.get_ammo()
        if ammo:
            return ammo.attributes or []
        else:
            return []

    def get_basic_attack(self):
        ammo = self.get_ammo()
        if ammo:
            ba = pbge.effects.Invocation(
                name='Single Shot',
                fx=geffects.AttackRoll(
                    self.attack_stat, self.scale.RANGED_SKILL,
                    children=(geffects.DoDamage(2*ammo.damage, 4, scale=ammo.scale),),
                    accuracy=ammo.accuracy * 10, penetration=ammo.penetration * 10,
                    defenses=self.get_defenses(),
                    modifiers=self.get_modifiers(ammo)
                ),
                area=pbge.scenes.targetarea.SingleTarget(reach=ammo.reach * 3),
                used_in_combat=True, used_in_exploration=False,
                ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
                shot_anim=geffects.Missile1,
                price=[geffects.AmmoPrice(ammo, 1), geffects.RevealPositionPrice(ammo.damage)],
                data=geffects.AttackData(pbge.image.Image('sys_attackui_missiles.png', 32, 32), 0,
                                         thrill_power=ammo.damage + ammo.penetration),
                targets=1)
            for aa in self.get_attributes():
                if hasattr(aa, 'modify_basic_attack'):
                    aa.modify_basic_attack(self, ba)
            return ba

    def get_multi_attack(self, num_missiles, frame):
        ammo = self.get_ammo()
        if ammo:
            ba = pbge.effects.Invocation(
                name='Fire x{}'.format(num_missiles),
                fx=geffects.MultiAttackRoll(
                    self.attack_stat, self.scale.RANGED_SKILL, num_attacks=num_missiles,
                    children=(geffects.DoDamage(2*ammo.damage, 4, scale=ammo.scale),),
                    accuracy=ammo.accuracy * 10, penetration=ammo.penetration * 10,
                    defenses=self.get_defenses(),
                    modifiers=self.get_modifiers(ammo)
                ),
                area=pbge.scenes.targetarea.SingleTarget(reach=ammo.reach * 3),
                used_in_combat=True, used_in_exploration=False,
                ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
                shot_anim=geffects.MissileFactory(num_missiles),
                price=[geffects.AmmoPrice(ammo, num_missiles), geffects.RevealPositionPrice(ammo.damage * 2)],
                data=geffects.AttackData(pbge.image.Image('sys_attackui_missiles.png', 32, 32), frame,
                                         thrill_power=ammo.damage * 2 + ammo.penetration),
                targets=1)
            for aa in self.get_attributes():
                if hasattr(aa, 'modify_basic_attack'):
                    aa.modify_basic_attack(self, ba)
            return ba

    def get_attacks(self):
        # Return a list of invocations associated with this weapon.
        # Being a weapon, the invocations are likely to all be attacks.
        my_invos = list()
        ammo = self.get_ammo()
        if ammo:
            my_invos.append(self.get_basic_attack())
            last_n = int(ammo.quantity // 4)
            if last_n > 1:
                my_invos.append(self.get_multi_attack(last_n, 3))
            if 0 < last_n < int(ammo.quantity // 2):
                my_invos.append(self.get_multi_attack(int(ammo.quantity // 2), 6))
            if ammo.quantity > 1:
                my_invos.append(self.get_multi_attack(max(ammo.quantity - ammo.spent, 2), 9))
        return my_invos

    def get_shelf_name(self):
        ammo = self.get_ammo()
        if ammo:
            return ammo.name
        else:
            return self.name

    def get_ammo_string(self):
        ammo = self.get_ammo()
        if ammo:
            return 'Ammo: {}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)
        else:
            return 'Empty'

    def get_weapon_desc(self):
        ammo = self.get_ammo()
        if ammo:
            # noinspection PyPep8
            return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}-{1}-{2}\n Ammo: {3}/{0.quantity}'.format(
                ammo, ammo.reach * 2, ammo.reach * 3, ammo.quantity - ammo.spent)
        else:
            return 'Empty'

    def get_item_stats(self):
        # Provide info on the ammo.
        ammo = self.get_ammo()
        if ammo:
            return (('Ammo', '{}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)),)
        else:
            return (('Ammo', '0'),)

    def get_area_anim(self):
        ammo = self.get_ammo()
        if ammo and ammo.area_anim:
            return ammo.area_anim
        else:
            return geffects.BigBoom


class Chem(BaseGear, Stackable, StandardDamageHandler, Restoreable):
    DEFAULT_NAME = "Chem"
    STACK_CRITERIA = ('attributes',)
    SAVE_PARAMETERS = ('quantity', 'attributes', 'shot_anim', 'area_anim')
    LEGAL_ATTRIBUTES = (attackattributes.Brutal, attackattributes.BurnAttack,)

    def __init__(self, quantity=20, shot_anim=None, area_anim=None, attributes=(), **keywords):
        # Check the range of all parameters before applying.
        self.quantity = max(quantity, 1)
        self.spent = 0
        self.shot_anim = shot_anim
        self.area_anim = area_anim
        self.attributes = list()
        for a in attributes:
            if a in self.LEGAL_ATTRIBUTES:
                self.attributes.append(a)

        # Finally, call the gear initializer.
        super(Chem, self).__init__(**keywords)

    @property
    def base_mass(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.MASS_MODIFIER
        return int(mult * 10 * (self.quantity - self.spent) // 25)

    @property
    def base_volume(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.VOLUME_MODIFIER
        return int((mult * 5 * self.quantity + 49) // 50)

    @property
    def base_cost(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.COST_MODIFIER
        return int(10 * self.quantity * mult // 10)

    def get_item_stats(self):
        # Provide info on the ammo.
        return (('Chem', '{}/{}'.format(self.quantity - self.spent, self.quantity)),)

    base_health = 1

    def get_reload_cost(self):
        return (self.cost * self.spent) // self.quantity

    def restore(self):
        ac = self.get_reload_cost()
        self.spent = 0
        return ac + super(Chem, self).restore()


class ChemThrower(Weapon):
    MIN_REACH = 2
    MAX_REACH = 5
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 5
    DEFAULT_SHOT_ANIM = geffects.BigBullet
    DEFAULT_AREA_ANIM = geffects.Fireball
    LEGAL_ATTRIBUTES = (attackattributes.Blast1, attackattributes.Blast2, attackattributes.LineAttack,
                        attackattributes.ConeAttack, attackattributes.LinkedFire
                        )

    def is_legal_sub_com(self, part):
        if isinstance(part, Weapon):
            return part.integral
        else:
            return isinstance(part, Chem)

    def get_ammo(self):
        for maybe_ammo in self.sub_com:
            if isinstance(maybe_ammo, Chem):
                return maybe_ammo

    def get_attributes(self):
        ammo = self.get_ammo()
        if ammo:
            return self.attributes + ammo.attributes
        else:
            return self.attributes

    def get_defenses(self):
        return {geffects.DODGE: geffects.ReflexSaveRoll(), geffects.BLOCK: geffects.BlockRoll(self)}

    def get_modifiers(self):
        return (self.get_common_modifiers(self.get_module())
                + self.get_ranged_modifiers(self.reach)
                )

    def get_chem_cost(self):
        mult = 1.0
        for aa in self.get_attributes():
            mult *= aa.POWER_MODIFIER
        return int(mult * self.damage * max(self.penetration, 1))

    def get_basic_attack(self, targets=1, name='Basic Attack', ammo_cost=1, attack_icon=0):
        my_ammo = self.get_ammo()

        ba = pbge.effects.Invocation(
            name=name,
            fx=geffects.AttackRoll(
                self.attack_stat, self.get_attack_skill(),
                children=(geffects.DoDamage(2*self.damage, 4, scale=self.scale, scatter=True),),
                accuracy=self.accuracy * 10, penetration=self.penetration * 10,
                defenses=self.get_defenses(),
                modifiers=self.get_modifiers()
            ),
            area=pbge.scenes.targetarea.SingleTarget(reach=self.reach * 3),
            used_in_combat=True, used_in_exploration=False,
            ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
            shot_anim=self.get_shot_anim(),
            data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 0,
                                     thrill_power=((self.damage * 2 + self.penetration)* (targets+1))//2),
            price=[geffects.AmmoPrice(my_ammo, ammo_cost * self.get_chem_cost()),
                   geffects.RevealPositionPrice(self.damage)],
            targets=targets)

        for aa in self.get_attributes():
            if hasattr(aa, 'modify_basic_attack'):
                aa.modify_basic_attack(self, ba)
        return ba

    def get_ammo_string(self):
        ammo = self.get_ammo()
        if ammo:
            return 'Chem: {}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)
        else:
            return 'Chem: 0'

    def get_weapon_desc(self):
        ammo = self.get_ammo()
        it = 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {1}\n {2}'.format(
            self,
            self.get_reach_str(), self.get_ammo_string())
        return it

    def get_item_stats(self):
        # Provide info on the ammo.
        ammo = self.get_ammo()
        if ammo:
            return (('Chem', '{}/{}'.format(ammo.quantity - ammo.spent, ammo.quantity)),)
        else:
            return (('Chem', '0'),)

    def get_shot_anim(self):
        ammo = self.get_ammo()
        if ammo and ammo.shot_anim:
            return ammo.shot_anim
        else:
            return self.shot_anim

    def get_area_anim(self):
        ammo = self.get_ammo()
        if ammo and ammo.area_anim:
            return ammo.area_anim
        else:
            return self.area_anim


#   *******************
#   ***   HOLDERS   ***
#   *******************

class Hand(BaseGear, StandardDamageHandler):
    DEFAULT_NAME = "Hand"
    base_mass = 5

    def is_legal_inv_com(self, part):
        return isinstance(part, (Weapon, Launcher))

    base_cost = 50
    base_health = 2

    def can_normally_remove(self):
        # Human-scale hands cannot be removed at Cyberdoc Terminal.
        return not (self.scale is scale.HumanScale)


class Mount(BaseGear, StandardDamageHandler):
    DEFAULT_NAME = "Weapon Mount"
    base_mass = 5

    def is_legal_inv_com(self, part):
        return isinstance(part, (Weapon, Launcher))

    base_cost = 50
    base_health = 2


#   *******************
#   ***   USABLES   ***
#   *******************

class Usable(BaseGear, StandardDamageHandler):
    # No usable gears yet, but I wanted to include this class definition
    # because it's needed by the construction rules below.
    DEFAULT_NAME = "Do Nothing Usable"


#   *****************
#   *** CYBERWARE ***
#   *****************

class BaseCyberware(BaseGear, StandardDamageHandler):
    DEFAULT_MATERIAL = materials.Biotech
    DEFAULT_SCALE = scale.HumanScale
    SAVE_PARAMETERS = ("statline",)

    # Override in your derived class.
    location = '???'
    base_trauma = 2
    cost_factor = 1.0

    def __init__(self, statline=None, **keywords):
        self.statline = collections.defaultdict(int)
        if statline:
            self.statline.update(statline)
        self._dna_sequence = None
        super().__init__(**keywords)

    @property
    def dna_sequence(self):
        # back compatibility with existing savefiles.
        if not hasattr(self, '_dna_sequence'):
            return None
        return self._dna_sequence

    @dna_sequence.setter
    def dna_sequence(self, next_dna_sequence):
        self._dna_sequence = next_dna_sequence

    base_volume = 0

    @property
    def base_cost(self):
        # Used cyberware has 0 value because it has the first
        # user's cells in it and it can no longer be safely
        # implanted in anyone else without risking rejection
        # and other symptoms commonly called "cyberdisfunction".
        # Also, eww.
        if self.dna_sequence:
            return 0
        benefit = 0
        for s in self.statline.keys():
            value = self.statline.get(s, 0)
            if value < 0:
                value = -1
            elif s in stats.PRIMARY_STATS:
                value *= 3
            elif s in stats.NONCOMBAT_SKILLS:
                value *= 5
            else:
                value *= 4
            benefit += value
        return int(benefit * 805 * self.cost_factor)

    @property
    def trauma(self):
        benefit = self.base_trauma
        for s in self.statline.keys():
            value = self.statline.get(s, 0)
            if value < 0:
                value *= 1
            elif s in stats.PRIMARY_STATS:
                value *= 1
            else:
                value *= 2
            benefit += value // 2
        return int(max(benefit, self.base_trauma))

    def get_item_stats(self):
        return (("Location", self.location)
                , ("Trauma/Sta", str(self.trauma))
                )


class EyesCyberware(BaseCyberware):
    location = 'Eyes'
    base_trauma = 1
    cost_factor = 1.1


class EarsCyberware(BaseCyberware):
    location = 'Ears'
    base_trauma = 1
    cost_factor = 0.9


class ForebrainCyberware(BaseCyberware):
    location = 'Forebrain'
    base_trauma = 3
    cost_factor = 1.3


class BrainstemCyberware(BaseCyberware):
    location = 'Brainstem'
    base_trauma = 3
    cost_factor = 1.3


class HeartCyberware(BaseCyberware):
    location = 'Heart'
    base_trauma = 3


class SpineCyberware(BaseCyberware):
    location = 'Spine'


class TorsoMusclesCyberware(BaseCyberware):
    location = 'Torso Muscles'


class ArmMusclesCyberware(BaseCyberware):
    location = 'Arm Muscles'


class ArmBonesCyberware(BaseCyberware):
    location = 'Arm Bones'


class LegMusclesCyberware(BaseCyberware):
    location = 'Leg Muscles'


class LegBonesCyberware(BaseCyberware):
    location = 'Leg Bones'


#   *******************
#   ***   MODULES   ***
#   *******************

class ModuleForm(Singleton):
    @classmethod
    def is_legal_sub_com(cls, part):
        return False

    @classmethod
    def is_legal_inv_com(self, part):
        return False

    MULTIPLICITY_LIMITS = {
        Engine: 1, Hand: 1, Mount: 1, Cockpit: 1, Gyroscope: 1, Armor: 1
    }

    @classmethod
    def check_multiplicity(self, mod, part):
        """Returns True if part within acceptable limits for its kind."""
        ok = True
        for k, v in list(self.MULTIPLICITY_LIMITS.items()):
            if isinstance(part, k):
                ok = ok and len([item for item in mod.sub_com if isinstance(item, k)]) < v
        return ok

    VOLUME_X = 2
    MASS_X = 1
    AIM_BONUS = 0
    CAN_ATTACK = False
    ACCURACY = 0
    PENETRATION = 0
    SENSOR_BONUS = 0


class MF_Head(ModuleForm):
    name = "Head"
    SENSOR_BONUS = 1

    MULTIPLICITY_LIMITS = {
        EyesCyberware: 1, EarsCyberware: 1, ForebrainCyberware: 1, BrainstemCyberware: 1,
        **ModuleForm.MULTIPLICITY_LIMITS
    }

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (
            Weapon, Launcher, Armor, Sensor, Cockpit, Mount, MovementSystem, PowerSource, Usable, EWSystem,
            EyesCyberware, EarsCyberware, ForebrainCyberware, BrainstemCyberware))


class MF_Torso(ModuleForm):
    name = "Torso"
    MULTIPLICITY_LIMITS = {
        Engine: 1, Mount: 2, Cockpit: 1, Gyroscope: 1, Armor: 1,
        HeartCyberware: 1, SpineCyberware: 1, TorsoMusclesCyberware: 1
    }

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (
            Weapon, Launcher, Armor, Sensor, Cockpit, Mount, MovementSystem, PowerSource, Usable, Engine, Gyroscope,
            EWSystem, HeartCyberware, SpineCyberware, TorsoMusclesCyberware))

    VOLUME_X = 4
    MASS_X = 2


class MF_Arm(ModuleForm):
    name = "Arm"
    AIM_BONUS = 5
    CAN_ATTACK = True
    ACCURACY = 1

    MULTIPLICITY_LIMITS = {
        ArmMusclesCyberware: 1, ArmBonesCyberware: 1,
        **ModuleForm.MULTIPLICITY_LIMITS
    }

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part,
                          (Weapon, Launcher, Armor, Hand, Mount, MovementSystem, PowerSource, Sensor, Usable, EWSystem,
                           ArmMusclesCyberware, ArmBonesCyberware))

    @classmethod
    def is_legal_inv_com(self, part):
        return isinstance(part, Shield)


class MF_Leg(ModuleForm):
    name = "Leg"
    CAN_ATTACK = True
    PENETRATION = 1

    MULTIPLICITY_LIMITS = {
        LegBonesCyberware: 1, LegMusclesCyberware: 1,
        **ModuleForm.MULTIPLICITY_LIMITS
    }

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (
            Weapon, Launcher, Armor, MovementSystem, Mount, Sensor, PowerSource, Usable, EWSystem, LegMusclesCyberware,
            LegBonesCyberware))


class MF_Wing(ModuleForm):
    name = "Wing"

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (Weapon, Launcher, Armor, MovementSystem, Mount, Sensor, PowerSource, Usable, EWSystem))


class MF_Turret(ModuleForm):
    name = "Turret"
    AIM_BONUS = 5

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (Weapon, Launcher, Armor, MovementSystem, Mount, Sensor, PowerSource, Usable, EWSystem))


class MF_Tail(ModuleForm):
    name = "Tail"
    AIM_BONUS = 5
    CAN_ATTACK = True
    ACCURACY = 1
    PENETRATION = 1

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (Weapon, Launcher, Armor, MovementSystem, Mount, Sensor, PowerSource, Usable, EWSystem))


class MF_Storage(ModuleForm):
    name = "Storage"

    @classmethod
    def is_legal_sub_com(self, part):
        return isinstance(part, (Weapon, Launcher, Armor, MovementSystem, Mount, Sensor, PowerSource, Usable, EWSystem))

    VOLUME_X = 4
    MASS_X = 0


class Module(BaseGear, StandardDamageHandler):
    SAVE_PARAMETERS = ('form', 'size', 'info_tier')

    def __init__(self, form=MF_Storage, size=1, info_tier=None, **keywords):
        keywords["name"] = keywords.pop("name", form.name)
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form
        if info_tier not in (None, 1, 2, 3):
            info_tier = None
        self.info_tier = info_tier
        super().__init__(**keywords)

    @property
    def base_mass(self):
        return 2 * self.form.MASS_X * self.size

    @property
    def base_cost(self):
        return self.size * 25

    @property
    def base_volume(self):
        return self.size * self.form.VOLUME_X

    def check_multiplicity(self, part):
        return self.form.check_multiplicity(self, part)

    def is_legal_sub_com(self, part):
        return self.form.is_legal_sub_com(part)

    def is_legal_inv_com(self, part):
        if isinstance(part, Clothing):
            return part.form is self.form
        else:
            return self.form.is_legal_inv_com(part)

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return 1 + self.form.MASS_X * self.size

    def get_armor(self, destroyed_ok=False):
        """Returns the armor protecting this gear."""
        # Modules might have externally mounted armor in clothing or whatnot.
        candidates = [part for part in self.sub_com if
                      isinstance(part, Armor) and (destroyed_ok or part.is_not_destroyed())]
        for part in self.inv_com:
            if part.is_not_destroyed():
                armor = part.get_armor()
                if armor and armor.is_not_destroyed():
                    candidates.append(armor)
        candidates.sort(key=lambda a: a.get_armor_rating())
        if candidates:
            return candidates[0]

    def get_defenses(self):
        return {geffects.DODGE: geffects.DodgeRoll(), geffects.BLOCK: geffects.BlockRoll(self),
                geffects.PARRY: geffects.ParryRoll(self)}

    def get_modifiers(self):
        return (self.get_common_modifiers(module=self)
                + self.get_melee_modifiers()
                )

    def get_damage_bonus(self):
        myroot = self.get_root()
        if hasattr(myroot, "get_melee_damage_bonus"):
            return myroot.get_melee_damage_bonus(self)

    def get_attacks(self):
        # Return a list of invocations associated with this module.
        my_invos = list()
        if self.form.CAN_ATTACK:
            ba = pbge.effects.Invocation(
                name='Basic Attack',
                fx=geffects.MeleeAttackRoll(
                    stats.Body, self.scale.MELEE_SKILL,
                    children=(geffects.DoDamage(2, self.size + 1, scale=self.scale, damage_bonus=self.get_damage_bonus(), is_brutal=True),),
                    accuracy=self.form.ACCURACY * 10, penetration=self.form.PENETRATION * 10,
                    defenses=self.get_defenses(),
                    modifiers=self.get_modifiers()
                ),
                area=pbge.scenes.targetarea.SingleTarget(reach=1),
                used_in_combat=True, used_in_exploration=False,
                price=[geffects.RevealPositionPrice(self.size // 3)],
                ai_tar=aitargeters.AttackTargeter(targetable_types=(BaseGear,), ),
                shot_anim=None,
                data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png', 32, 32), 0),
                targets=1)
            my_invos.append(ba)

        return my_invos

    def can_normally_remove(self):
        # Human-scale modules cannot be removed at Cyberdoc Terminal.
        return not (self.scale is scale.HumanScale)

    def can_install(self, part, check_volume=True):
        if super().can_install(part, check_volume):
            if isinstance(part, BaseCyberware):
                # Cyberware has to have correct scale.
                if not self.scale is part.scale:
                    return False
                parent = self.parent
                if parent and isinstance(parent, Being):
                    # Cyberware has to have the same genetic markers as
                    # whoever is being installed into.
                    if part.dna_sequence and part.dna_sequence != parent.dna_sequence:
                        return False
                if check_volume:
                    # Check trauma specs.

                    # Normally, only Beings can install cyberware.
                    # However, while loading, the subcom is being
                    # built without a parent for this module yet,
                    # so we just pass this test.
                    # The only other callers of can_install is the
                    # geareditor, which gets the fully constructed
                    # gear already.
                    if not parent or not isinstance(parent, Being):
                        return True
                    # Make sure the being can take the trauma.
                    if parent.current_trauma + part.trauma > parent.max_trauma:
                        return False
            return True
        else:
            return False


class Head(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Head
        super(Head, self).__init__(**keywords)


class Torso(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Torso
        super(Torso, self).__init__(**keywords)


class Arm(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Arm
        super(Arm, self).__init__(**keywords)


class Leg(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Leg
        super(Leg, self).__init__(**keywords)


class Wing(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Wing
        super(Wing, self).__init__(**keywords)


class Turret(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Turret
        Module.__init__(self, **keywords)


class Tail(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Tail
        super(Tail, self).__init__(**keywords)


class Storage(Module):
    def __init__(self, **keywords):
        keywords["form"] = MF_Storage
        super(Storage, self).__init__(**keywords)


#   ********************
#   ***   CLOTHING   ***
#   ********************

class Clothing(BaseGear, ContainerDamageHandler):
    SAVE_PARAMETERS = ('form',)

    def __init__(self, form=MF_Torso, **keywords):
        # Check the range of all parameters before applying.
        self.form = form
        super(Clothing, self).__init__(**keywords)

    @property
    def base_mass(self):
        return 1

    @property
    def base_cost(self):
        return 25

    @property
    def base_volume(self):
        return 5 * self.form.VOLUME_X

    def is_legal_sub_com(self, part):
        return isinstance(part, (Armor, MovementSystem, PowerSource, Weapon))


class HeadClothing(Clothing):
    def __init__(self, **keywords):
        keywords["form"] = MF_Head
        super(HeadClothing, self).__init__(**keywords)


class TorsoClothing(Clothing):
    def __init__(self, **keywords):
        keywords["form"] = MF_Torso
        super().__init__(**keywords)


class ArmClothing(Clothing):
    def __init__(self, **keywords):
        keywords["form"] = MF_Arm
        super().__init__(**keywords)


class LegClothing(Clothing):
    def __init__(self, **keywords):
        keywords["form"] = MF_Leg
        super(LegClothing, self).__init__(**keywords)


#   *****************
#   ***   MECHA   ***
#   *****************

class MT_Battroid(Singleton):
    name = "Battroid"
    desc = "Standard mecha form, no turrets."

    PROTOTYPE_IMAGENAME = "mav_buruburu.png"
    PROTOTYPE_PORTRAIT = "mecha_buruburu.png"

    @classmethod
    def is_legal_sub_com(self, part):
        if isinstance(part, Module):
            return part.form not in (MF_Turret,)
        else:
            return False

    @classmethod
    def modify_speed(self, base_speed, move_mode):
        # Return the modified speed.
        return base_speed


class MT_Arachnoid(MT_Battroid):
    name = "Arachnoid"
    desc = "+20% walk speed, can have turrets, no arms, wings or tails."

    PROTOTYPE_IMAGENAME = "mav_kojedo.png"
    PROTOTYPE_PORTRAIT = "mecha_kojedo.png"

    @classmethod
    def is_legal_sub_com(self, part):
        if isinstance(part, Module):
            return part.form not in (MF_Arm, MF_Wing, MF_Tail)
        else:
            return False

    @classmethod
    def modify_speed(self, base_speed, move_mode):
        # Return the modified speed.
        if move_mode == pbge.scenes.movement.Walking:
            return int(base_speed * 1.2)
        else:
            return 0


class MT_Groundhugger(MT_Battroid):
    name = "Groundhugger"
    desc = "+25% armor, can have turrets, -20 mobility, no arms, wings, tails, or legs."

    PROTOTYPE_IMAGENAME = "mav_ultari.png"
    PROTOTYPE_PORTRAIT = "mecha_ultari.png"

    @classmethod
    def is_legal_sub_com(self, part):
        if isinstance(part, Module):
            return part.form not in (MF_Arm, MF_Wing, MF_Tail, MF_Leg)
        else:
            return False

    @classmethod
    def modify_speed(self, base_speed, move_mode):
        # Return the modified speed.
        if move_mode in {geffects.Rolling, geffects.Skimming}:
            return base_speed
        else:
            return 0

    @classmethod
    def modify_mobility(cls, base_mobility):
        return max(base_mobility - 20, 0)

    @classmethod
    def modify_armor(cls, base_armor):
        return int(base_armor * 1.25)


MECHA_FORMS = (MT_Battroid, MT_Arachnoid, MT_Groundhugger)


class Mecha(BaseGear, ContainerDamageHandler, Mover, VisibleGear, HasPower, Combatant):
    SAVE_PARAMETERS = ('name', 'form', 'environment_list', 'role_list', 'family')
    DODGE_SKILL = stats.MechaPiloting

    def __init__(self, form=MT_Battroid,
                 environment_list=(tags.GroundEnv, tags.UrbanEnv, tags.SpaceEnv), role_list=(tags.Trooper,),
                 family='None', **keywords):
        name = keywords.get("name")
        if name is None:
            keywords["name"] = form.name
        self.form = form
        self.environment_list = environment_list
        self.role_list = role_list
        self.family = family
        super(Mecha, self).__init__(**keywords)
        if tags.ST_MECHA not in self.shop_tags:
            self.shop_tags.append(tags.ST_MECHA)
        self.pilot = None

    def is_legal_sub_com(self, part):
        return self.form.is_legal_sub_com(part)

    def is_legal_inv_com(self, part):
        return not isinstance(part, (Mover, Combatant))

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    base_mass = 0

    def check_multiplicity(self, part):
        # A mecha can have only one torso module.
        if isinstance(part, Module) and part.form == MF_Torso:
            n = 0
            for i in self.sub_com:
                if isinstance(i, Module) and i.form == MF_Torso:
                    n += 1
            return n == 0
        else:
            return True

    def can_install(self, part, check_volume=True):
        if check_volume:
            return self.is_legal_sub_com(
                part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR and self.check_multiplicity(part)
        else:
            return self.is_legal_sub_com(part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR

    def can_equip(self, part, check_volume=True):
        """Returns True if part can be legally equipped under current conditions"""
        return self.is_legal_inv_com(part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR

    @property
    def base_volume(self):
        return sum(i.volume for i in self.sub_com)

    def is_not_destroyed(self):
        """ A mecha must have a notdestroyed body with a notdestroyed engine
            in it.
        """
        # Check out the body.
        for m in self.sub_com:
            if isinstance(m, Torso) and m.is_not_destroyed():
                for e in m.sub_com:
                    if isinstance(e, Engine) and e.is_not_destroyed() and e.scale is self.scale:
                        return True

    def check_design(self):
        # Return True if this is a usable mecha design.
        # That basically means it has an engine, a gyro, and a cockpit.
        er, gs = self.get_engine_rating_and_gyro_status()
        if er > 0 and gs:
            num_cockpits = 0
            for g in self.sub_sub_coms():
                if isinstance(g, Cockpit):
                    num_cockpits += 1
            return num_cockpits == 1

    def is_operational(self):
        """ To be operational, a mecha must have a pilot.
        """
        pilot = self.get_pilot()
        return self.is_not_destroyed() and pilot and pilot.is_operational()

    def get_pilot(self):
        """Return the character who is operating this mecha."""
        for m in self.ok_sub_sub_coms():
            if isinstance(m, Character):
                return m

    def get_cockpit(self):
        '''Return whichever cockpit the pilot will use to board the mecha.'''

        # For back-compatibility with existing saves.
        # It's possible we will change which cockpit is returned
        # by this function when the mecha has multiple cockpits.
        # If so, existing savefiles might have the pilot already
        # riding a different cockpit than what the later algorithm
        # would return.
        # What cockpit the pilot is currently riding should take
        # precedence over which one the pilot will enter the *next*
        # time zey board the mek.
        pilot = self.get_pilot()
        if pilot:
            return pilot.parent

        # Select the last listed cockpit.
        cpit = None
        for m in self.sub_sub_coms():
            if isinstance(m, Cockpit):
                cpit = m
        return cpit

    def load_pilot(self, pilot):
        """Stick the pilot into the mecha."""
        cpit = self.get_cockpit()
        cpit.sub_com.append(pilot)

    def free_pilots(self):
        pilots = list()
        for m in self.sub_sub_coms():
            if isinstance(m, Cockpit):
                for pilot in list(m.sub_com):
                    if isinstance(pilot, Character):
                        m.sub_com.remove(pilot)
                        pilots.append(pilot)
        return pilots

    def get_engine_rating_and_gyro_status(self):
        has_gyro = False
        engine_rating = 0
        for m in self.sub_com:
            if isinstance(m, Torso) and m.is_not_destroyed():
                for e in m.sub_com:
                    if isinstance(e, Engine) and e.is_not_destroyed() and e.scale is self.scale:
                        engine_rating = e.size
                    elif isinstance(e, Gyroscope) and e.is_not_destroyed() and e.scale is self.scale:
                        has_gyro = True
                break
        return engine_rating, has_gyro

    def calc_mobility(self):
        """Calculate the mobility ranking of this mecha.
        """
        mass_factor = (self.mass ** 2) // (10000 * self.scale.SIZE_FACTOR ** 6)
        engine_rating, has_gyro = self.get_engine_rating_and_gyro_status()
        # It is possible for mass_factor to drop to 0
        # if the mecha is massless, e.g. if all modules
        # are removed.
        # mass_factor is always a non-negative integer.
        if mass_factor == 0:
            mass_factor = 1
        # We now have the mass_factor, engine_rating, and has_gyro.
        it = engine_rating // mass_factor
        if not has_gyro:
            it -= 30
        # Head mounted cockpits provide a bonus.
        cpit = self.get_cockpit()
        if cpit:
            cmod = cpit.get_module()
            if cmod and cmod.form == MF_Head:
                it += 10
        # Add form modifiers
        if hasattr(self.form, "modify_mobility"):
            it = self.form.modify_mobility(it)
        # Add emchantment modifiers.
        it += self.ench_list.get_funval(self, 'get_mobility_bonus')

        if it > 50:
            it = min(it, 50 + int(math.log(it - 50, 1.2)))

        return it

    def calc_walking(self):
        norm_mass = self.scale.unscale_mass(self.mass)
        engine_rating, has_gyro = self.get_engine_rating_and_gyro_status()
        # In order to walk, a mecha needs both an engine and a gyroscope.
        if (engine_rating > 0) and has_gyro:
            # If the number of legs is less than half plus one,
            # the mecha will fall over.
            total_legs, active_legs = self.count_modules(MF_Leg)
            if active_legs < ((total_legs // 2) + 1):
                return 0

            speed = (1125 - norm_mass + engine_rating // 5) // 15

            # Depending on the mecha's mass, it needs a minimum number of
            # leg points to support it. If it has less than that number
            # then speed will be reduced.
            min_leg_points = norm_mass // 50 - 2
            actual_leg_points = self.count_module_points(MF_Leg)
            if actual_leg_points < min_leg_points:
                speed = (speed * actual_leg_points) // min_leg_points

            # Add thrust bonus.
            thrust = self.count_thrust_points(scenes.movement.Walking)
            if thrust > norm_mass:
                speed += thrust // norm_mass

            # Add form bonus.
            speed = self.form.modify_speed(speed, scenes.movement.Walking)

            # Don't drop below minimum speed.
            speed = max(speed, 20)

            return Mover.apply_speed_bonus(self, speed)
        else:
            return 0

    def calc_skimming(self):
        engine_rating, has_gyro = self.get_engine_rating_and_gyro_status()
        # In order to skim, a mecha needs both an engine and a gyroscope.
        if (engine_rating > 0) and has_gyro:
            return Mover.calc_skimming(self)
        else:
            return 0

    def get_stat(self, stat_id):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_stat(stat_id) + self.ench_list.get_stat(stat_id)
        else:
            return 0

    def get_skill_score(self, stat_id, skill_id):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_skill_score(stat_id, skill_id) + self.ench_list.get_stat(
                stat_id) + self.ench_list.get_stat(skill_id)
        else:
            return 0

    def has_skill(self, skill_id):
        pilot = self.get_pilot()
        if pilot:
            return skill_id in pilot.statline

    def get_dodge_score(self):
        return self.get_skill_score(stats.Speed, self.DODGE_SKILL)

    def get_sensor_range(self, map_scale):
        it = 3
        for sens in self.sub_sub_coms():
            if hasattr(sens, 'get_sensor_rating') and sens.is_operational():
                it = max((sens.get_sensor_rating() // map_scale.RANGE_FACTOR) * 5, it)
        return it

    def get_ewar_rating(self):
        total = 0
        for ewar in self.sub_sub_coms():
            if ewar is not self and hasattr(ewar, "get_ewar_rating") and ewar.is_operational():
                total += ewar.get_ewar_rating()
        return total

    def get_max_mental(self):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_max_mental()
        else:
            return 0

    def get_max_stamina(self):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_max_stamina()
        else:
            return 0

    def get_current_mental(self):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_current_mental()
        else:
            return 0

    def get_current_stamina(self):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_current_stamina()
        else:
            return 0

    def spend_mental(self, amount):
        pilot = self.get_pilot()
        if pilot:
            pilot.spend_mental(amount)

    def partially_restore_mental(self, amount):
        pilot = self.get_pilot()
        if pilot:
            pilot.partially_restore_mental(amount)

    def spend_stamina(self, amount):
        pilot = self.get_pilot()
        if pilot:
            pilot.spend_stamina(amount)

    def get_action_points(self):
        if self.get_current_speed() > 0:
            return 2
        else:
            return 1

    def dole_experience(self, xp, xp_type=None):
        pilot = self.get_pilot()
        if pilot:
            pilot.dole_experience(xp, xp_type)

    def get_melee_damage_bonus(self, weapon):
        mymod = weapon.get_module()
        if mymod:
            scmods = [sc.get_melee_damage_bonus() for sc in mymod.sub_com if sc.is_not_destroyed() and hasattr(sc,"get_melee_damage_bonus")] + [0,]
            return mymod.size//2 + sum(scmods)
        else:
            return 0


class Being(BaseGear, StandardDamageHandler, Mover, VisibleGear, HasPower, Combatant, Restoreable):
    SAVE_PARAMETERS = ('statline', 'combatant')
    DEFAULT_SCALE = scale.HumanScale
    DEFAULT_MATERIAL = materials.Meat
    DESTROYED_FRAME = 0
    TOTAL_XP = "TOTAL_XP"
    SPENT_XP = "SPENT_XP"
    DODGE_SKILL = stats.Dodge

    def __init__(self, statline=None, combatant=True, **keywords):
        self.statline = collections.defaultdict(int)
        if statline:
            self.statline.update(statline)
        self.combatant = combatant

        self.mp_spent = 0
        self.sp_spent = 0
        self.experience = collections.defaultdict(int)

        self._generate_dna_sequence()

        super(Being, self).__init__(**keywords)

    def _generate_dna_sequence(self):
        self._dna_sequence = str(uuid.uuid4())

    @property
    def dna_sequence(self):
        # back-compatibility with existing savefiles.
        if not hasattr(self, '_dna_sequence'):
            self._generate_dna_sequence()
        return self._dna_sequence

    def is_legal_sub_com(self, part):
        return isinstance(part, Module)

    def is_legal_inv_com(self, part):
        return not isinstance(part, (Mover, Combatant))

    def can_install(self, part, check_volume=True):
        if check_volume:
            return self.is_legal_sub_com(part) and part.scale is self.scale and self.check_multiplicity(part)
        else:
            return self.is_legal_sub_com(part) and part.scale is self.scale

    def can_equip(self, part, check_volume=True):
        """Returns True if part can be legally equipped under current conditions"""
        return self.is_legal_inv_com(part) and part.scale.SIZE_FACTOR <= self.scale.SIZE_FACTOR

    @property
    def base_volume(self):
        return sum(i.volume for i in self.sub_com)

    def is_not_destroyed(self):
        """ A character doesn't need a body or head, but if present must not
            be destroyed.
        """
        is_ok = self.max_health > self.hp_damage
        # Check out the body.
        for m in self.sub_com:
            if isinstance(m, (Torso, Head)) and m.is_destroyed():
                is_ok = False
                break
        return is_ok

    def cyberware(self):
        for part in self.sub_sub_coms():
            if isinstance(part, BaseCyberware):
                yield part

    def get_cyberware_bonus(self, stat_id):
        bonus = 0
        for cw in self.cyberware():
            bonus += cw.statline.get(stat_id, 0)
        return bonus

    @property
    def max_trauma(self):
        # Use the base body.
        return self.statline.get(stats.Body, 0) // 3 + self.statline.get(stats.Cybertech, 0)

    @property
    def current_trauma(self):
        trauma = 0
        for cw in self.cyberware():
            trauma += cw.trauma
        return trauma

    def get_stat(self, stat_id):
        # Cyberware can remove skill by giving them -999,
        # but make sure not to actually affect gameplay
        # beyond removing skills.
        return (max(0, self.statline.get(stat_id, 0) + self.get_cyberware_bonus(stat_id))
                + self.ench_list.get_stat(stat_id)
                )

    def get_all_skills(self):
        effective_statline = self.statline.copy()
        # Add any new skills cyberware gives you.
        for cw in self.cyberware():
            for s in cw.statline.keys():
                effective_statline[s] = effective_statline.get(s, 0) + cw.statline[s]

        # Clear entries that are at 0 or below, if
        # a cyberware removes a skill.
        for s in list(effective_statline.keys()):
            if effective_statline[s] <= 0:
                del effective_statline[s]
        return effective_statline.keys()

    def get_skill_score(self, stat_id, skill_id):
        it = self.get_stat(skill_id) * 5
        if stat_id:
            it += self.get_stat(stat_id) * 2
        return it

    def has_skill(self, skill_id):
        return skill_id in self.get_all_skills()

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this character."""
        return max(self.get_stat(stats.Body) + self.get_stat(stats.Vitality), 3)

    def get_pilot(self):
        """Return the character itself."""
        return self

    def get_mobility_penalty(self):
        inv_mass = self.get_inv_mass()
        ccap = self.get_stat(stats.Body) * 30
        if inv_mass > ccap:
            return (inv_mass - ccap) // 5
        else:
            return 0

    def calc_mobility(self):
        """Calculate the mobility ranking of this character.
        """
        base_m = self.get_stat(stats.Speed) * 3 + 10 - self.get_mobility_penalty()

        # Add emchantment modifiers.
        base_m += self.ench_list.get_funval(self, 'get_mobility_bonus')

        if base_m > 50:
            it = min(base_m, 50 + int(math.log(base_m - 50, 1.2)))

        return max(base_m, 0)

    def get_dodge_score(self):
        return self.get_skill_score(stats.Speed, self.DODGE_SKILL)

    MIN_WALK_SPEED = 20

    def calc_walking(self):
        speed = self.get_stat(stats.Speed) * 5

        # If the number of legs is less than half plus one,
        # the character can only crawl.
        total_legs, active_legs = self.count_modules(MF_Leg)
        if active_legs < ((total_legs // 2) + 1):
            speed = self.MIN_WALK_SPEED
        elif active_legs < total_legs:
            speed = max((speed * active_legs) // total_legs, self.MIN_WALK_SPEED)

        return speed

    def get_sensor_range(self, map_scale):
        return self.get_stat(stats.Perception) * self.scale.RANGE_FACTOR // map_scale.RANGE_FACTOR

    def get_max_mental(self):
        return (self.get_stat(stats.Knowledge) + self.get_stat(stats.Ego) + 5) // 2 + self.get_stat(
            stats.Concentration) * 3

    def _compute_max_stamina(self, body, ego, athletics):
        return (body + ego + 5) // 2 + athletics * 3

    def get_uncybered_max_stamina(self):
        ''' Computes the max stamina if the
        character did not had any cyberware.
        '''
        return self._compute_max_stamina(self.statline.get(stats.Body, 0)
                                         , self.statline.get(stats.Ego, 0)
                                         , self.statline.get(stats.Athletics, 0)
                                         )

    def get_max_stamina(self):
        base = self._compute_max_stamina(self.get_stat(stats.Body)
                                         , self.get_stat(stats.Ego)
                                         , self.get_stat(stats.Athletics)
                                         )
        # Give the character a minimum stamina of 1.
        return max(1, base - self.current_trauma)

    def get_current_mental(self):
        return max(self.get_max_mental() - self.mp_spent, 0)

    def get_current_stamina(self):
        return max(self.get_max_stamina() - self.sp_spent, 0)

    def spend_mental(self, amount):
        self.mp_spent += amount
        self.dole_experience(amount, stats.Concentration)

    def partially_restore_mental(self, amount):
        self.mp_spent = max(self.mp_spent - amount, 0)

    def spend_stamina(self, amount):
        self.sp_spent += amount
        self.dole_experience(amount, stats.Athletics)

    def get_action_points(self):
        if self.get_current_speed() > 0:
            return 2
        else:
            return 1

    @staticmethod
    def random_stats(points=80, base_stats={}):
        statline = dict()
        minstat = max((points - 10) // 24, 0)
        leftovers = points - minstat * 8
        for s in stats.PRIMARY_STATS:
            statline[s] = minstat
        for t in range(leftovers):
            stat_to_improve = random.choice(stats.PRIMARY_STATS)
            if (statline[stat_to_improve] + base_stats.get(stat_to_improve, 0)) >= 15 and random.randint(1, 5) != 5:
                stat_to_improve = random.choice(stats.PRIMARY_STATS)
            statline[stat_to_improve] += 1
        return statline

    def roll_stats(self, points=80, clear_first=True):
        if clear_first:
            nu_stats = self.random_stats(points)
            self.statline.update(nu_stats)
        else:
            nu_stats = self.random_stats(points, self.statline)
            for s in stats.PRIMARY_STATS:
                self.statline[s] += nu_stats[s]

    def get_armor(self):
        return self

    def get_armor_rating(self):
        if self.get_current_stamina() > 0:
            return self.calc_average_armor()
        else:
            return self.calc_average_armor() // 2

    def reduce_damage(self, dmg, dmg_request):
        """Normally armor reduces damage, but gets damaged in the process."""
        max_absorb = min(self.scale.scale_health(1, self.material), dmg)
        absorb_amount = random.randint(max_absorb // 2, max_absorb)
        if absorb_amount > 0:
            dmg -= absorb_amount
            self.spend_stamina(1)
        return dmg

    def restore(self):
        self.mp_spent = 0
        self.sp_spent = 0
        return super(Being, self).restore()

    def dole_experience(self, xp, xp_type=TOTAL_XP):
        self.experience[xp_type or self.TOTAL_XP] += xp
        if xp_type in stats.ALL_SKILLS and xp_type in self.statline and xp_type.improvement_cost(self, self.statline[
            xp_type]) <= self.experience[xp_type]:
            self.experience[xp_type] -= xp_type.improvement_cost(self, self.statline[xp_type])
            self.statline[xp_type] += 1

    def get_melee_damage_bonus(self, weapon):
        return (self.get_stat(stats.Body) - 10) // 2


class Monster(Being, MakesPower):
    SAVE_PARAMETERS = ('threat', 'type_tags', 'families', 'environment_list', 'frame')

    def __init__(self, threat=0, type_tags=(), families=(), frame=0,
                 environment_list=(tags.GroundEnv, tags.UrbanEnv), **keywords):
        super().__init__(**keywords)
        self.threat = threat
        self.type_tags = set(type_tags)
        self.families = set(families)
        self.environment_list = set(environment_list)
        self.frame = frame

    @property
    def self_cost(self):
        # Cribbed from the Selector calc_threat_points, but will probably need to be adjusted for balance.
        if self.threat < 31:
            it = max(self.threat,1) * 300
        else:
            it = 20 * self.threat * self.threat - 900 * self.threat + 19040
        return it

    def matches(self, level, env, type_tags, scale):
        return abs(
            self.threat - level) <= 20 and env in self.environment_list and scale is self.scale and self.type_tags.intersection(
            type_tags)

    def max_power(self):
        return self.scale.scale_power(self.get_stat(stats.Body) * 5)


class Character(Being):
    SAVE_PARAMETERS = (
        'personality', 'gender', 'job', 'birth_year', 'renown', 'faction', 'badges', 'bio', 'relationship',
        "mecha_colors",
        "mecha_pref", 'mnpcid')
    DEEP_COPY_PARAMS = {"add_body": False}

    def __init__(self, personality=(), gender=None, job=None, birth_year=138, faction=None, renown=0, badges=(), bio="",
                 relationship=None, add_body=True, mecha_colors=None, mecha_pref=None, mnpcid=None, **keywords):
        self.personality = set(personality)
        if not gender:
            gender = genderobj.Gender.random_gender()
        elif isinstance(gender, dict):
            gender = genderobj.Gender(**gender)
        self.gender = gender
        self.job = job
        self.birth_year = birth_year
        self.faction = faction
        self.faction_scores = collections.defaultdict(int)
        self.renown = renown
        self.badges = list(badges)
        self.bio = bio
        self.relationship = relationship
        self.mecha_colors = mecha_colors
        self.mecha_pref = mecha_pref
        # Major NPC ID: unique identifier so NPC relationships get carried between scenarios.
        self.mnpcid = mnpcid
        super().__init__(**keywords)
        if add_body:
            self.build_body()
            if job and renown:
                job.scale_skills(self, renown)

    def get_tacit_faction(self, camp):
        # Get this character's effective faction. Normally this will be the faction this character belongs to, but
        # if the character is factionless then it will be the faction of the team this character is a member of.
        faction = self.faction
        if not faction:
            myroot = self.get_root()
            team = camp.scene.local_teams.get(myroot)
            if team:
                faction = team.faction
        return faction

    def get_tags(self):
        # Return all of the character's personality, job, and faction tags.
        mytags = list(self.personality)
        if self.job:
            mytags += list(self.job.tags)
        if self.faction:
            mytags.append(self.faction.get_faction_tag())
        return mytags

    def add_faction_score(self, fac, delta):
        if fac:
            self.faction_scores[fac.get_faction_tag()] += delta

    def get_reaction_score(self, pc, camp):
        if self.relationship and pc is camp.pc:
            rs = self.relationship.reaction_mod
            # Check for local reputation, if no relationship tags.
            if not self.relationship.tags:
                myscene = camp.scene.get_metro_scene()
                if myscene:
                    rs += myscene.metrodat.local_reputation
        else:
            rs = 0
        for a, b in personality.OPPOSED_PAIRS:
            if a in self.personality:
                if a in pc.personality:
                    rs += 10
                elif b in pc.personality:
                    rs -= 10
            elif b in self.personality:
                if a in pc.personality:
                    rs -= 10
                elif b in pc.personality:
                    rs += 10
        for v in personality.VIRTUES:
            if v in self.personality and v in pc.personality:
                rs += 10
        fac = self.get_tacit_faction(camp)
        if fac:
            rs += pc.faction_scores.get(fac.get_faction_tag(), 0)
            pc_fac = pc.get_tacit_faction(camp)
            if pc_fac and camp.are_enemy_factions(fac, pc_fac):
                rs -= 20

        # Add bonuses from PC's merit badges
        for badge in pc.badges:
            rs += badge.get_reaction_modifier(pc, self, camp)

        # Add Charm bonus.
        pc_charm = pc.get_stat(stats.Charm)
        npc_ego = self.get_stat(stats.Ego)
        if pc_charm >= npc_ego:
            rs += (pc_charm - npc_ego + 3) * 5
        return min(max(rs, -100), 100)

    def get_text_desc(self, camp):
        myitems = list()
        myitems.append("{} year old".format(camp.year - self.birth_year))
        if self.gender:
            myitems.append(self.gender.adjective)
        if self.job:
            myitems.append(str(self.job))
        return " ".join(myitems)

    def build_body(self):
        # I've heard of bodybuilding, but this is ridiculous.
        self.sub_com.append(Head(size=5, material=self.material, scale=self.scale))
        self.sub_com.append(Torso(size=5, material=self.material, scale=self.scale))
        rarm = Arm(size=5, name="Right Arm", material=self.material, scale=self.scale)
        rarm.sub_com.append(Hand(name="Right Hand", material=self.material, scale=self.scale))
        self.sub_com.append(rarm)
        larm = Arm(size=5, name="Left Arm", material=self.material, scale=self.scale)
        larm.sub_com.append(Hand(name="Left Hand", material=self.material, scale=self.scale))
        self.sub_com.append(larm)
        self.sub_com.append(Leg(size=5, name="Right Leg", material=self.material, scale=self.scale))
        self.sub_com.append(Leg(size=5, name="Left Leg", material=self.material, scale=self.scale))

    def has_badge(self, badge_name):
        return any(b for b in self.badges if b.name == badge_name)


class Prop(BaseGear, StandardDamageHandler, HasInfinitePower, Combatant):
    SAVE_PARAMETERS = ('size', 'statline', 'frame', 'destroyed_frame', 'action_points')
    DEFAULT_SCALE = scale.MechaScale
    DEFAULT_MATERIAL = materials.Metal
    DODGE_SKILL = stats.MechaPiloting

    def __init__(self, statline=None, size=10, frame=0, destroyed_frame=1, action_points=3, **keywords):
        self.statline = collections.defaultdict(int)
        if statline:
            self.statline.update(statline)
        self.size = size
        self.frame = frame
        self.destroyed_frame = destroyed_frame
        self.destroyed_pose = False
        self.action_points = max(action_points, 1)

        super(Prop, self).__init__(**keywords)

    def is_legal_sub_com(self, part):
        return True

    def is_legal_inv_com(self, part):
        return True

    @property
    def base_volume(self):
        return self.size * 4

    def get_stat(self, stat_id):
        return self.statline.get(stat_id, 0) + self.ench_list.get_stat(stat_id)

    def get_skill_score(self, stat_id, skill_id):
        it = self.get_stat(skill_id) * 5
        if stat_id:
            it += self.get_stat(stat_id) * 2
        return it

    def has_skill(self, skill_id):
        return skill_id in self.statline

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this character."""
        return self.size * 10

    def get_pilot(self):
        """Return the prop itself."""
        return self

    def calc_mobility(self):
        """Calculate the mobility ranking of this character.
        """
        return 0

    def get_dodge_score(self):
        return 0

    def get_sensor_range(self, map_scale):
        return max(15, self.get_stat(stats.Perception) + 5)

    def get_max_mental(self):
        return (self.get_stat(stats.Knowledge) + self.get_stat(stats.Ego) + 5) // 2 + self.get_stat(
            stats.Concentration) * 3

    def get_max_stamina(self):
        return (self.get_stat(stats.Body) + self.get_stat(stats.Ego) + 5) // 2 + self.get_stat(stats.Athletics) * 3

    def get_current_mental(self):
        return self.get_max_mental()

    def get_current_stamina(self):
        return self.get_max_stamina()

    def spend_mental(self, amount):
        pass

    def partially_restore_mental(self, amount):
        pass

    def spend_stamina(self, amount):
        pass

    def get_attack_library(self):
        my_invos = list()
        for p in self.descendants(include_pilot=False):
            if hasattr(p, 'get_attacks') and p.is_not_destroyed():
                p_list = geffects.InvoLibraryShelf(p, p.get_attacks())
                if p_list.has_at_least_one_working_invo(self, True):
                    my_invos.append(p_list)
        my_invos.sort(key=lambda shelf: -shelf.get_average_thrill_power(self))
        return my_invos

    def get_skill_library(self, in_combat=False):
        my_invo_dict = collections.defaultdict(list)
        for p in list(self.statline.keys()):
            if hasattr(p, 'add_invocations'):
                p.add_invocations(self, my_invo_dict)
        my_invos = list()
        for k, v in list(my_invo_dict.items()):
            p_list = geffects.InvoLibraryShelf(k, v)
            if p_list.has_at_least_one_working_invo(self, in_combat):
                my_invos.append(p_list)
        return my_invos

    def get_action_points(self):
        return self.action_points

    def render(self, foot_pos, view):
        spr = view.get_sprite(self)
        mydest = spr.get_rect(self.frame)
        mydest.midbottom = foot_pos
        mydest.top += view.HTH
        if self.destroyed_pose:
            spr.render(mydest, self.destroyed_frame)
        else:
            spr.render(mydest, self.frame)

    def update_graphics(self):
        self.destroyed_pose = not self.is_operational()


class Squad(BaseGear, ContainerDamageHandler, Mover, VisibleGear, HasPower, Combatant):
    DEFAULT_SCALE = scale.WorldScale
    DESTROYED_FRAME = 0

    def is_legal_sub_com(self, part):
        return isinstance(part, (Being, Mecha))

    def is_legal_inv_com(self, part):
        return False

    def can_install(self, part, check_volume=True):
        return self.is_legal_sub_com(part) and part.scale.SIZE_FACTOR < self.scale.SIZE_FACTOR

    @property
    def base_volume(self):
        return sum(i.volume for i in self.sub_com)

    def get_stat(self, stat_id):
        return max([0, ] + [mem.get_stat(stat_id) for mem in self.sub_com if
                            hasattr(mem, "get_stat") and mem.is_operational()])

    def get_skill_score(self, stat_id, skill_id):
        it = self.get_stat(skill_id) * 5
        if stat_id:
            it += self.get_stat(stat_id) * 2
        return it

    def calc_mobility(self):
        """Calculate the mobility ranking of this character.
        """
        return max([0, ] + [mem.calc_mobility() for mem in self.sub_com if
                            hasattr(mem, "calc_mobility") and mem.is_operational()])

    def get_dodge_score(self):
        return self.get_skill_score(stats.Speed, stats.Dodge)

    def calc_walking(self):
        return min([20, ] + [mem.calc_walking() for mem in self.sub_com if
                             hasattr(mem, "calc_walking") and mem.is_operational()])

    def get_sensor_range(self, map_scale):
        return max([0, ] + [mem.get_sensor_range(map_scale) for mem in self.sub_com if
                            hasattr(mem, "get_sensor_range") and mem.is_operational()])

    def get_max_mental(self):
        return 100

    def get_max_stamina(self):
        return 100

    def get_current_mental(self):
        return max(self.get_max_mental() - self.mp_spent, 0)

    def get_current_stamina(self):
        return max(self.get_max_stamina() - self.sp_spent, 0)

    def spend_mental(self, amount):
        self.mp_spent += amount

    def partially_restore_mental(self, amount):
        self.mp_spent = max(self.mp_spent - amount, 0)

    def spend_stamina(self, amount):
        self.sp_spent += amount

    def get_action_points(self):
        return len([mem for mem in self.sub_com if mem.is_operational()])

    MINI_SPRITE_OFFSETS = ((22, 40), (0, 40), (44, 40), (11, 44), (33, 44))

    def get_sprite(self):
        """Generate the sprite for this thing."""
        base_image = pbge.image.Image(frame_width=self.imagewidth, frame_height=self.imageheight)
        for n, mem in enumerate(self.sub_com):
            spr = mem.get_sprite()
            smol_spr = pygame.transform.scale(spr.bitmap, (20, 20))
            base_image.bitmap.blit(smol_spr, self.MINI_SPRITE_OFFSETS[n])
            if n >= 4:
                break
        return base_image

    def get_portrait(self):
        if self.sub_com:
            return self.sub_com[0].get_portrait()

    def free_pilots(self):
        pilots = list()
        for pc in list(self.sub_com):
            self.sub_com.remove(pc)
            pilots.append(pc)
            if hasattr(pc, "free_pilots"):
                pilots += pc.free_pilots()
        return pilots


#   ********************
#   ***   TREASURE   ***
#   ********************

class Treasure(BaseGear, StandardDamageHandler):
    DEFAULT_NAME = "Treasure"
    SAVE_PARAMETERS = (
        'value','weight')
    DEFAULT_SCALE = scale.HumanScale

    def __init__(self, value=1000, weight=10, **keywords):
        self.value = value
        self.weight = weight

        # Finally, call the gear initializer.
        super().__init__(**keywords)

    @property
    def base_mass(self):
        """Returns the unscaled mass of this gear, ignoring children."""
        return self.weight

    base_volume = 1

    @property
    def base_cost(self):
        return self.value
