import random
import math
import copy

import gears
from . import attackattributes
from . import base
from . import materials

class UpgradeTheme( object ):
    ''' Base class for an upgrade theme.
    For example an upgrade theme might put more movesystems.
    '''
    name = "???"

    def pre_upgrade(self, mek, items):
        # Called after the driver has gotten all items that could be
        # upgraded, but before sorting the list or doing any upgrading.
        # mek = the mecha being upgraded.
        # items = the items that would be upgraded.
        # Return nothing.
        return

    def upgrade_sort_index(self, item):
        # Given the item, determine priority of what the theme
        # should process for upgrading first.
        # For example, a theme which sacrifices armor for move
        # systems might prioritize armors for upgrading
        # (really downgrading).
        # Lower-valued number is higher priority.

        # By default, delay armor upgrades.
        # This lets installed items in the same module be upgraded first.
        if isinstance(item, base.Armor):
            return 1
        else:
            return 0

    def attempt_upgrade(self, holder, item, is_installed):
        # holder = the gear containing the item.
        # item = the item being upgraded.
        # If the item is installed, the theme must ensure that the
        # modifications do not violate the size limits!
        # Only the specific item is allowed to be modified.
        # is_installed = convenience argument: True if item is
        # in holder.sub_com, False if item is in holder.inv_com.
        #
        # This function returns True if it did any modification to
        # the item, False otherwise.
        #
        # Default action is that torso armor is upgraded by at least 1.
        if isinstance(holder, base.Torso) and isinstance(item, base.Armor) and is_installed:
            was_integral = item.integral
            upgrade_limit = holder.free_volume
            if not was_integral:
                upgrade_limit += 1

            if upgrade_limit == 0:
                # No scope for upgrading it anyway.
                return False

            # Randomly upgrade.
            to_upgrade = random.randint(1, upgrade_limit)
 
            if not was_integral and to_upgrade == upgrade_limit:
                item.integral = True
            item.size += to_upgrade

            return True

        else:
            return False

    def install_sort_index(self, module):
        # Like upgrade_sort_index, except modules that are
        # candidates for insertion of things.
        #
        # By default, prioritize turrets, then tails, then
        # arms, then everything else, because the most common
        # thing to install is new weaponry.
        if isinstance(module, base.Turret):
            return 0
        elif isinstance(module, base.Tail):
            return 1
        elif isinstance(module, base.Arm):
            return 2
        else:
            return 3

    def attempt_install_item(self, module):
        # Called once for each module with non-zero free volume.
        # Do NOT insert the item in the module.sub_com!
        # Instead, return the item you are adding.
        # Make sure the returned item fits in the module!
        return None

class RandomTheme( UpgradeTheme ):
    def __init__(self):
        self._delegate = random.choice(THEMES)()

    @property
    def name(self):
        return self._delegate.name

    def pre_upgrade(self, mek, items):
        return self._delegate.pre_upgrade(mek, items)

    def upgrade_sort_index(self, item):
        return self._delegate.upgrade_sort_index(item)

    def attempt_upgrade(self, holder, item, is_installed):
        return self._delegate.attempt_upgrade(holder, item, is_installed)

    def install_sort_index(self, item):
        return self._delegate.install_sort_index(item)

    def attempt_install_item(self, module):
        return self._delegate.attempt_install_item(module)

###############################################################################

class DragonTheme(UpgradeTheme):
    name = "Dragon"
    def __init__(self):
        if attackattributes.BurnAttack.VOLUME_MODIFIER != 1.0:
            raise RuntimeError('Need to update DragonTheme to check volume after upgrading.')

        self._upgraded_weapons = False
        self._has_flamethrower = False

    def pre_upgrade(self, mek, items):
        self._has_flamethrower = any([self._is_flamethrower(i) for i in items])

    def _is_flamethrower(self, item):
        return( isinstance(item, base.ChemThrower)
            and item.get_ammo()
            and (attackattributes.BurnAttack in item.get_ammo().attributes)
              )

    def attempt_upgrade(self, holder, item, is_installed):
        if isinstance(item, (base.MeleeWeapon, base.EnergyWeapon)):
            if attackattributes.BurnAttack in item.attributes:
                return False
            item.attributes.append(attackattributes.BurnAttack)
            self._minor_upgrade_weapon(holder, item, is_installed)

            self._upgraded_weapons = True
            return True

        elif isinstance(item, (base.BallisticWeapon, base.Launcher)):
            ammo = item.get_ammo()
            if not ammo or attackattributes.BurnAttack in ammo.attributes:
                return False
            ammo.attributes.append(attackattributes.BurnAttack)
            self._minor_upgrade_weapon(holder, item, is_installed)

            self._upgraded_weapons = True
            return True

        # The default behavior is to upgrade Torso armor.
        # But if we didn't upgrade any weapons, then don't
        # upgrade the torso armor, so that the driving function
        # falls back to the generic Champion.
        # Note that the default sorting of items to upgrade
        # is to upgrade non-armor before armor.
        if self._upgraded_weapons:
            return super().attempt_upgrade(holder, item, is_installed)

        return False

    def _minor_upgrade_weapon(self, holder, item, is_installed):
        # Avoid issues with installed weapons growing in volume.
        if is_installed:
            return
        # Increase the weapon penetration if possible.
        weap = _get_statted_weapon(item)
        if weap.penetration < weap.MAX_PENETRATION:
            weap.penetration += 1
        # Launchers may need to be upgraded.
        if isinstance(item, base.Launcher) and item.size < weap.volume:
            item.size = weap.volume

    def _make_flamethrower(self, reach, damage, napalm, integral = False):
        return base.ChemThrower( name = 'Maw'
                               , reach = reach, damage = damage
                               , accuracy = 1, penetration = 1
                               , attributes = (attackattributes.ConeAttack,)
                               , material = materials.Metal
                               , sub_com = [napalm]
                               , integral = integral
                               )
    def _make_napalm(self, size):
        return base.Chem( name = 'Napalm'
                        , attributes = (attackattributes.BurnAttack,)
                        , quantity = size * 10
                        , material = materials.Metal
                        )

    def attempt_install_item(self, module):
        if self._has_flamethrower:
            return None
        if not self._upgraded_weapons:
            return None
        if module.free_volume < 5:
            return None

        self._has_flamethrower = True
        if module.free_volume >= 9:
            return self._make_flamethrower(5, 5, self._make_napalm(9))
        elif module.free_volume == 8:
            return self._make_flamethrower(5, 4, self._make_napalm(8))
        elif module.free_volume == 7:
            return self._make_flamethrower(4, 4, self._make_napalm(7))
        elif module.free_volume == 6:
            return self._make_flamethrower(3, 4, self._make_napalm(6))
        else:
            return self._make_flamethrower(3, 4, self._make_napalm(5), integral = True)
            

class RaiderTheme(UpgradeTheme):
    name = "Raider"
    def __init__(self):
        self._movesys = ()
        self._largest = 0
        self._weapon_upgraded = False

    def pre_upgrade(self, mek, items):
        # Determine what the mek's main movement is.
        walk_speed = mek.calc_walking()
        skim_speed = mek.calc_skimming()
        roll_speed = mek.calc_rolling()
        if walk_speed > skim_speed and walk_speed > roll_speed:
            self._movesys = (base.HeavyActuators,)
        elif roll_speed > skim_speed and roll_speed > walk_speed:
            self._movesys = (base.Wheels, base.Tracks)
        else:
            self._movesys = (base.HoverJets,)

    def upgrade_sort_index(self, item):
        # Sort armor before everything else: we might actually *downgrade*
        # armor to increase or insert movement systems.
        # Also, sort sensors after everything else: only upgrade sensors
        # if at least one weapon got upgraded.
        if isinstance(item, base.Armor):
            return 0
        elif isinstance(item, base.Sensor):
            return 999
        else:
            return 1

    def _is_movesys(self, item):
        ''' Determine if the item is the appropriate
        movement system.
        '''
        return isinstance(item, self._movesys)

    def _upgrade_weapon(self, item):
        weap = _get_statted_weapon(item);

        upgraded = False
        # Increase reach if not a melee weapon.
        if not isinstance(weap, (base.MeleeWeapon, base.EnergyWeapon)):
            if weap.reach < weap.MAX_REACH:
                weap.reach += 1
                upgraded = True
        # Increase accuracy.
        if weap.accuracy < weap.MAX_ACCURACY:
            weap.accuracy += 1
            upgraded = True

        # Launchers may need to be upgraded.
        if isinstance(item, base.Launcher) and item.size < weap.volume:
            item.size = weap.volume

        return upgraded

    def attempt_upgrade(self, holder, item, is_installed):
        if isinstance(item, base.Armor):
            assert is_installed
            # If the holder has any movement system of the correct
            # type, and the holder has no free volume, have to
            # downgrade!
            if holder.free_volume == 0 and any([self._is_movesys(i) for i in holder.sub_com]):
                # Need to give one extra space to the movement system.
                if not item.integral:
                    item.integral = True
                    _improve_material(item)
                    return True
                else:
                    # Already integral, so make it one size smaller.
                    # Force it to be Advanced material.
                    item.size -= 1
                    item.material = materials.Advanced
                    return True
            else:
                # Improving the material usually lightens it.
                return _improve_material(item)

        if self._is_movesys(item):
            assert is_installed

            self._largest = max(self._largest, item.size)

            upgraded = False
            # Increase the size of the movesys and make it advanced.
            if holder.free_volume > 0:
                item.size += 1
                upgraded = True
            if not item.material is materials.Advanced:
                item.material = materials.Advanced
                upgraded = True

            return upgraded

        # Upgrade weapons.
        weap = _get_statted_weapon(item)
        if weap:
            upgraded = _try_upgrade(holder, item, is_installed, self._upgrade_weapon)
            if upgraded:
                self._weapon_upgraded = True
            return upgraded

        # Upgrade sensors, if at least one weapon was upgraded.
        if self._weapon_upgraded and isinstance(item, base.Sensor):
            # Sensors are always installed.
            if holder.free_volume == 0:
                if item.integral:
                    # cannot upgrade.
                    return False
                item.integral = True
            item.size += 1
            return True

        return False

    def _new_movesys(self, size):
        ''' Construct a new movement system.
        '''
        ctor = self._movesys[0]
        return ctor(size = size, material = materials.Advanced)

    def _attempt_install_movesys(self, module):
        # Install only if module has no movesys
        if any([isinstance(i, base.MovementSystem) for i in module.sub_com]):
            return None
        # At least size 2.
        if module.free_volume < 2:
            return None
        if self._largest < 2:
            self._largest = 2

        return self._new_movesys(min(module.free_volume, self._largest))

    def attempt_install_item(self, module):
        # Install a movesys if no movesys.
        item = self._attempt_install_movesys(module)
        if item:
            return item

        # Install overchargers if not exist yet.
        if any([isinstance(i, base.Overchargers) for i in module.sub_com]):
            return None
        return base.Overchargers( material = materials.Advanced
                                , size = min(3, module.free_volume)
                                )

class GunslingerTheme(UpgradeTheme):
    ''' More Dakka '''
    name = "Gunslinger"

    def __init__(self):
        self._upgraded_weapons = False

    def _upgrade_burst(self, item):
        # If maxed, cannot upgrade.
        if attackattributes.BurstFire5 in item.attributes:
            return False
        if attackattributes.VariableFire5 in item.attributes:
            return False
        if attackattributes.SwarmFire3 in item.attributes:
            return False
        if attackattributes.Automatic in item.attributes:
            return False

        if attackattributes.BurstFire2 in item.attributes:
            self._replace_attrib(item, attackattributes.BurstFire2, attackattributes.BurstFire3)
        elif attackattributes.BurstFire3 in item.attributes:
            self._replace_attrib(item, attackattributes.BurstFire3, attackattributes.BurstFire4)
        elif attackattributes.BurstFire4 in item.attributes:
            self._replace_attrib(item, attackattributes.BurstFire4, attackattributes.BurstFire5)
        elif attackattributes.VariableFire2 in item.attributes:
            self._replace_attrib(item, attackattributes.VariableFire2, attackattributes.VariableFire3)
        elif attackattributes.VariableFire3 in item.attributes:
            self._replace_attrib(item, attackattributes.VariableFire3, attackattributes.VariableFire4)
        elif attackattributes.VariableFire4 in item.attributes:
            self._replace_attrib(item, attackattributes.VariableFire4, attackattributes.VariableFire5)
        elif attackattributes.SwarmFire2 in item.attributes:
            self._replace_attrib(item, attackattributes.SwarmFire2, attackattributes.SwarmFire3)
        else:
            item.attributes.append(attackattributes.BurstFire2)

        self._upgrade_ammo(item)
        return True

    def _replace_attrib(self, item, old, new):
        item.attributes.remove(old)
        item.attributes.append(new)

    def _upgrade_ammo(self, item):
        if not isinstance(item, base.BallisticWeapon):
            return
        magazine = item.magazine
        magazine = math.ceil(magazine * 1.5)
        item.magazine = magazine
        ammo = item.get_ammo()
        if ammo:
            ammo.quantity = magazine

    def _upgrade_quantity(self, item):
        ammo = item.get_ammo()
        if not ammo:
            return False

        # Upgrade quantity but not too much.
        orig_quantity = ammo.quantity
        new_quantity = min(60, orig_quantity * 2)
        if new_quantity <= orig_quantity:
            return False

        ammo.quantity = new_quantity
        item.size = ammo.volume
        return True

    def _do_upgrade(self, item):
        if isinstance(item, base.Launcher):
            return self._upgrade_quantity(item)
        else:
            return self._upgrade_burst(item)

    def attempt_upgrade(self, holder, item, is_installed):
        if isinstance(item, (base.BallisticWeapon, base.BeamWeapon, base.Launcher)):
            if _try_upgrade(holder, item, is_installed, self._do_upgrade):
                self._upgraded_weapons = True
                return True
            else:
                return False

        # Do default upgrades if appropriate.
        if self._upgraded_weapons:
            return super().attempt_upgrade(holder, item, is_installed)

        return False

class SlasherTheme(UpgradeTheme):
    name = 'Slasher'

    def __init__(self):
        self._num_melee = 0
        self._has_charge = False
        self._upgraded_specific = False

    def pre_upgrade(self, mek, items):
        self._num_melee = len([0 for i in items if isinstance(i, (base.MeleeWeapon, base.EnergyWeapon))])
        self._has_charge = any([isinstance(i, (base.MeleeWeapon, base.EnergyWeapon)) and attackattributes.ChargeAttack in i.attributes for i in items])

    def upgrade_sort_index(self, item):
        # Prioritize weapons and shields.
        if isinstance(item, (base.MeleeWeapon, base.EnergyWeapon, base.Shield)):
            return 0
        else:
            return 1

    def _upgrade_weapon(self, item):
        upgraded = False
        if not self._has_charge:
            item.attributes.append(attackattributes.ChargeAttack)
            item.name = 'Halberd'
            upgraded = True
        if item.damage < item.MAX_DAMAGE:
            item.damage += 1
            upgraded = True
        return upgraded

    def _upgrade_shield(self, item):
        # Increase bonus by 2.
        if item.bonus == item.MAX_BONUS:
            return False
        item.bonus = min(item.bonus + 2, item.MAX_BONUS)
        # Reduce size by 1.
        if item.size > item.MIN_SIZE:
            item.size -= 1
        return True

    def attempt_upgrade(self, holder, item, is_installed):
        if isinstance(item, (base.MeleeWeapon, base.EnergyWeapon)):
            if _try_upgrade(holder, item, is_installed, self._upgrade_weapon):
                self._upgraded_specific = True
                if not self._has_charge and attackattributes.ChargeAttack in item.attributes:
                    self._has_charge = True
                return True
            return False
        elif isinstance(item, base.Shield):
            if _try_upgrade(holder, item, is_installed, self._upgrade_shield):
                self._upgraded_specific = True
                return True
            return False

        if self._upgraded_specific:
            upgraded = False
            upgraded = super().attempt_upgrade(holder, item, is_installed)
            # Lighten armor.
            if isinstance(item, base.Armor):
                if _improve_material(item):
                    upgraded = True
            return upgraded
        else:
            return False

    def _create_weapon(self, name, damage, accuracy, penetration, attrib):
        return base.EnergyWeapon( name = name, reach = 1
                                , damage = damage
                                , accuracy = accuracy
                                , penetration = penetration
                                , attributes = [attrib]
                                , material = materials.Advanced
                                )

    def attempt_install_item(self, module):
        if not self._upgraded_specific:
            return None
        if self._num_melee >= 2:
            return None

        item = None
        if self._has_charge:
            if module.free_volume >= 5:
                item = self._create_weapon('Blade', 5, 5, 1, attackattributes.FastAttack)
            elif module.free_volume == 4:
                item = self._create_weapon('Blade', 4, 4, 1, attackattributes.FastAttack)
            elif module.free_volume == 3:
                item = self._create_weapon('Blade', 3, 3, 1, attackattributes.FastAttack)
            elif module.free_volume == 2:
                item = self._create_weapon('Blade', 2, 2, 1, attackattributes.FastAttack)
        else:
            if module.free_volume >= 5:
                item = self._create_weapon('Pike', 4, 1, 4, attackattributes.ChargeAttack)
            elif module.free_volume == 4:
                item = self._create_weapon('Pike', 3, 1, 3, attackattributes.ChargeAttack)
            elif module.free_volume == 3:
                item = self._create_weapon('Pike', 3, 1, 2, attackattributes.ChargeAttack)
            elif module.free_volume == 2:
                item = self._create_weapon('Pike', 2, 1, 1, attackattributes.ChargeAttack)

        if item:
            if not self._has_charge and attackattributes.ChargeAttack in item.attributes:
                self._has_charge = True
            self._num_melee +=1

        return item

class FulminateTheme(UpgradeTheme):
    name = 'Fulminate'

    def __init__(self):
        self._upgraded_weapons = False
        self._have_ew = False

    def pre_upgrade(self, mek, items):
        self._have_ew = any([isinstance(i, base.EWSystem) for i in items])

    def _upgrade_ew(self, item):
        if item.size == len(gears.programs.ALL_PROGRAMS):
            return False
        # Get what program we can add.
        candidates = [p for p in gears.programs.ALL_PROGRAMS if not p in item.programs]
        item.size += 1
        item.programs.append(random.choice(candidates))
        return True

    def _upgrade_eweapon(self, item):
        # EnergyWeapon and BeamWeapon.
        if attackattributes.OverloadAttack in item.attributes:
            return False

        if len(item.attributes) == 0:
            item.attributes.append(attackattributes.Accurate)
        item.attributes.append(attackattributes.OverloadAttack)

        return True

    def _upgrade_weapon(self, item):
        # MeleeWeapon and BallisticWeapon
        if isinstance(item, base.BallisticWeapon):
            to_upgrade = item.get_ammo()
        else:
            to_upgrade = item

        if attackattributes.HaywireAttack in to_upgrade.attributes:
            return False

        if len(item.attributes) == 0:
            item.attributes.append(attackattributes.Accurate)

        if attackattributes.OverloadAttack in to_upgrade.attributes:
            to_upgrade.attributes.remove(attackattributes.OverloadAttack)
            to_upgrade.attributes.append(attackattributes.HaywireAttack)
        else:
            to_upgrade.attributes.append(attackattributes.OverloadAttack)

        return True

    def _do_upgrade(self, item):
        if isinstance(item, base.EWSystem):
            return self._upgrade_ew(item)
        elif isinstance(item, (base.EnergyWeapon, base.BeamWeapon)):
            return self._upgrade_eweapon(item)
        elif isinstance(item, (base.MeleeWeapon, base.BallisticWeapon)):
            return self._upgrade_weapon(item)
        return False

    def attempt_upgrade(self, holder, item, is_installed):
        if isinstance(item, (base.EWSystem, base.Weapon)):
            if _try_upgrade(holder, item, is_installed, self._do_upgrade):
                self._upgraded_weapons = True
                return True
            return False

        if self._upgraded_weapons:
            return super().attempt_upgrade(holder, item, is_installed)

        return False

    # Prioritize installing an EW in torso.
    def install_sort_index(self, module):
        if isinstance(module, base.Torso):
            return 0
        else:
            return 1

    def attempt_install_item(self, module):
        if not self._upgraded_weapons:
            return None
        # We are only installing an EW.
        if self._have_ew:
            return None

        size = min(4, module.free_volume, len(gears.programs.ALL_PROGRAMS))
        programs = gears.programs.ALL_PROGRAMS.copy()
        random.shuffle(programs)
        item = base.EWSystem( name = 'Disruptor'
                            , size = size
                            , programs = programs
                            )

        self._have_ew = True

        return item

THEMES = [ t for t in UpgradeTheme.__subclasses__()
        if not t is RandomTheme
         ]

###############################################################################

def _in_mek(mek):
    for s in mek.sub_com:
        yield s
        for i in s.ok_descendants():
            yield i

# Append the theme name to the gear designation.
def _expand_desig(gear, name):
    if isinstance(gear, base.Launcher):
        ammo = gear.get_ammo()
        if ammo:
            _expand_desig(ammo, name)
            return
    if not gear.desig or gear.desig == '':
        gear.desig = name
    else:
        gear.desig = gear.desig + ' ' + name

# Look for items of the specific type.
def _find_item(mek, cls):
    for i in _in_mek(mek):
        if isinstance(i, cls):
            return i
    return None

# Expand the designation for the mek, its engine, and its gyro.
def _expand_core_desigs(mek, name):
    _expand_desig(mek, name)

    engine = _find_item(mek, base.Engine)
    if engine:
        _expand_desig(engine, name)

    gyro = _find_item(mek, base.Gyroscope)
    if gyro:
        _expand_desig(gyro, name)

# Get the item that has the weapon stats.
def _get_statted_weapon(item):
    if isinstance(item, base.Launcher):
        return item.get_ammo()
    elif isinstance(item, base.Weapon):
        return item
    return None

# Upgrade the material, return True if modified.
def _improve_material(gear):
    if gear.material is materials.Metal:
        gear.material = materials.Ceramic
        return True
    if gear.material is materials.Ceramic:
        gear.material = materials.Advanced
        return True
    return False

# Attempt the given upgrade function on the item.
# The upgrade function must be deterministic.
# It should return false if it cannot upgrade
# the item, true if it did.
# This cancels the upgrade if the resulting item
# would not fit in the holder.
def _try_upgrade(holder, item, is_installed, func):
    if is_installed:
        sample = copy.deepcopy(item)
        if not func(sample):
            return False
        if holder.free_volume < sample.volume - item.volume:
            return False
        func(item)
        return True
    else:
        return func(item)

###############################################################################

def _upgrade_engine(mek):
    engine = _find_item(mek, base.Engine)
    if not engine:
        return

    holder = engine.parent
    is_installed = holder and (engine in holder.sub_com)

    # Figure out how much to upgrade.
    to_increase = int(engine.size * 0.25)
    # Round up to nearest multiple of 5.
    to_increase = ((to_increase + 4) // 5) * 5
    # Upgrade by at least 175.
    to_increase = max(175, to_increase)

    # Create a copy of the engine.
    sample_engine = copy.deepcopy(engine)
    # Upgrade the engine
    sample_engine.size += to_increase
    if is_installed:
        while holder.free_volume < sample_engine.volume - engine.volume:
            # The new size won't fit!
            if not sample_engine.integral and random.randint(1, 5) == 1:
                sample_engine.integral = True
            else:
                sample_engine.size = max(sample_engine.size - 25, engine.size)

    engine.size = sample_engine.size
    engine.integral = sample_engine.integral

def _generic_upgrade(items):
    ''' Fallback in case a theme could not do any upgrades,
    such as a Dragon theme being fed a Nova Storm Buru Buru;
    e.g. Dragon makes everything BurnAttack, but Nova Storm
    has no weapos that can BurnAttack.
    '''
    # Make every installed non-integral SizeClassedComponent
    # an integral item one size higher.
    for item in items:
        holder = item.parent
        # If not installed SizeClassedComponent that is nonintegral, skip
        if not (holder and (item in holder.sub_com)):
            continue
        if not isinstance(item, base.SizeClassedComponent):
            continue
        if item.integral:
            continue
        item.integral = True
        item.size += 1
        _expand_desig(item, 'Champion')

###############################################################################

def upgrade_to_champion(mek, ThemeClass = RandomTheme):
    # First upgrade the engines.
    _upgrade_engine(mek);
    # Make the gyro integral for extra space.
    # Also makes the torso slightly more valuable.
    gyro = _find_item(mek, base.Gyroscope)
    if gyro:
        if gyro.free_volume >= 1:
            gyro.integral = True

    # Build the theme.
    theme = ThemeClass()
    # Gather the items.
    to_upgrade = list([ it for it in _in_mek(mek)
                     if isinstance(it, (base.Component, base.Shield, base.Launcher))
                    and not isinstance(it, (base.Engine, base.Cockpit, base.Gyroscope))
                      ])
    theme.pre_upgrade(mek, to_upgrade)

    # Sort items according to priority that the theme wants.
    to_upgrade.sort(key = theme.upgrade_sort_index)

    # Now upgrade the items.
    did_upgrade = False
    for item in to_upgrade:
        holder = item.parent
        is_installed = holder and (item in holder.sub_com)
        if theme.attempt_upgrade(holder, item, is_installed):
            _expand_desig(item, theme.name)
            did_upgrade = True

    # Try to install items in modules.
    mods = [ mod for mod in _in_mek(mek)
          if isinstance(mod, base.Module)
         and mod.free_volume > 0
           ]
    mods.sort(key = theme.install_sort_index)
    for mod in mods:
        item = theme.attempt_install_item(mod)
        if item and mod.can_install(item):
            _expand_desig(item, theme.name)
            mod.sub_com.append(item)
            did_upgrade = True

    if not did_upgrade:
        # The theme could not upgrade.
        # Do a generic upgrade of items.
        _generic_upgrade(to_upgrade)
        _expand_core_desigs(mek, 'Champion')
        mek.is_champion = True
        return

    # Finally: change the desingation.
    _expand_core_desigs(mek, theme.name)

    mek.is_champion = True

