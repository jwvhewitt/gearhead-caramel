import materials
import scale
import calibre
import pbge
from pbge import container, scenes, KeyObject, Singleton
import random

#
# Damage Handlers
#
#  Each "practical" gear should subclass one of the damage handlers.
#

class StandardDamageHandler( KeyObject ):
    # This gear type has health and takes damage. It is destroyed when the
    # amount of damage taken exceeds its maximum capacity.
    def __init__( self, **keywords ):
        self.hp_damage = 0
        super(StandardDamageHandler, self).__init__(**keywords)


    base_health = 1

    @property
    def max_health( self ):
        """Returns the scaled maximum health of this gear."""
        return self.scale.scale_health( self.base_health, self.material )

    def get_damage_status( self ):
        """Returns a percent value showing how damaged this gear is."""
        return (self.hp_damage*100)/self.max_health

    def is_not_destroyed( self ):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        if self.can_be_damaged():
            return self.max_health > self.hp_damage
        else:
            return True

    def is_destroyed( self ):
        return not self.is_not_destroyed()

    def is_operational( self ):
        """ Returns True if this gear is okay and its conditions for use are
            met. In other words, return True if this gear is
            ready to be used.
        """
        return self.is_not_destroyed()

    def can_be_damaged( self ):
        """ Returns True if this gear can be damaged.
        """
        return True

    def wipe_damage( self ):
        self.hp_damage = 0
        for p in self.sub_com:
            p.wipe_damage()
        for p in self.inv_com:
            p.wipe_damage()

class InvulnerableDamageHandler( StandardDamageHandler ):
    # This gear cannot be damaged or destroyed.
    def can_be_damaged( self ):
        """ Returns True if this gear can be damaged.
        """
        return False
    def get_damage_status( self ):
        """Returns a percent value showing how damaged this gear is."""
        return 0
    def is_not_destroyed( self ):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        return True

class ContainerDamageHandler( StandardDamageHandler ):
    # This gear just contains other gears; it is operational as long as it
    # has at least one subcom which is operational.
    base_health = 0
    def is_not_destroyed( self ):
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
    def get_damage_status( self ):
        """Returns a percent value showing how damaged this gear is."""
        mysubs = [sc.get_damage_status() for sc in self.sub_com]
        if mysubs:
            return sum(mysubs)/len(mysubs)
        else:
            return 0
    def can_be_damaged( self ):
        """ Returns True if this gear can be damaged.
        """
        return False

# Gear Ingredients
# Subclass one of these to get extra stuff for your gear class.
# These are purely optional.

class Stackable( KeyObject ):
    def __init__(self, **keywords ):
        super(Stackable, self).__init__(**keywords)
    def can_merge_with( self, part ):
        return ( self.__class__ is part.__class__ and self.scale is part.scale
            and self.name is part.name and self.desig is part.desig
            and not self.inv_com and not self.sub_com )


# Custom Containers
# For subcomponents and invcomponents with automatic error checking

class SubComContainerList( container.ContainerList ):
    def _set_container(self, item):
        if self.owner.can_install( item ):
            super( SubComContainerList, self )._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot subcom {}".format(self.owner,item))

class InvComContainerList( container.ContainerList ):
    def _set_container(self, item):
        if self.owner.can_equip( item ):
            super( InvComContainerList, self )._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot invcom {}".format(self.owner,item))

# The Base Gear itself.
# Note that the base gear is not usable by itself; a gear class should
# subclass BaseGear and also one of the damage handlers, plus any desired
# ingredients.

class BaseGear( scenes.PlaceableThing ):
    # To create a usable gear class, you need to subclass BaseGear, one of the
    # damage handlers from above, and maybe another ingredient like Stackable.
    DEFAULT_NAME = "Gear"
    DEFAULT_MATERIAL = materials.Metal
    DEFAULT_SCALE = scale.MechaScale
    SAVE_PARAMETERS = ('name','desig','scale','material','imagename','colors')
    def __init__(self, **keywords ):
        self.name = keywords.pop( "name" , self.DEFAULT_NAME )
        self.desig = keywords.pop( "desig", None )
        self.scale = keywords.pop( "scale" , self.DEFAULT_SCALE )
        self.material = keywords.pop( "material" , self.DEFAULT_MATERIAL )
        self.imagename = keywords.pop( "imagename", "iso_item.png" )
        self.colors = keywords.pop( "colors", None )


        self.sub_com = SubComContainerList( owner = self )
        sc_to_add = keywords.pop( "sub_com", [] )
        for i in sc_to_add:
            try:
                self.sub_com.append( i )
            except container.ContainerError as err:
                print( "ERROR: {}".format(err) )

        self.inv_com = InvComContainerList( owner = self )
        ic_to_add = keywords.pop( "inv_com", [] )
        for i in ic_to_add:
            if self.can_equip( i ):
                self.inv_com.append( i )
            else:
                print( "ERROR: {} cannot be equipped in {}".format(i,self) )

        super(BaseGear, self).__init__(**keywords)

    @property
    def base_mass(self):
        """Returns the unscaled mass of this gear, ignoring children."""
        return 1

    @property
    def self_mass( self ):
        """Returns the properly scaled mass of this gear, ignoring children."""
        return self.scale.scale_mass( self.base_mass , self.material )

    @property
    def mass(self):
        """Returns the true mass of this gear including children. Units is 0.1kg."""
        m = self.self_mass
        for part in self.sub_com:
            m = m + part.mass
        for part in self.inv_com:
            m = m + part.mass
        return m

    # volume is likely to be a property in more complex gear types, but here
    # it's just a constant value.
    volume = 1

    @property
    def free_volume(self):
        return self.volume - sum( i.volume for i in self.sub_com )

    energy = 1

    base_cost = 0

    @property
    def self_cost(self):
        return self.scale.scale_cost( self.base_cost , self.material )

    @property
    def cost(self):
        m = self.self_cost
        for part in self.sub_com:
            m = m + part.cost
        for part in self.inv_com:
            m = m + part.cost
        return m

    def is_legal_sub_com(self,part):
        return False

    MULTIPLICITY_LIMITS = {}
    def check_multiplicity( self, part ):
        """Returns True if part within acceptable limits for its kind."""
        ok = True
        for k,v in self.MULTIPLICITY_LIMITS.items():
            if isinstance( part, k ):
                ok = ok and len( [item for item in self.sub_com if isinstance( item, k )]) < v
        return ok

    def can_install(self,part):
        """Returns True if part can be legally installed here under current conditions"""
        return self.is_legal_sub_com(part) and part.scale <= self.scale and part.volume <= self.free_volume and self.check_multiplicity( part )

    def is_legal_inv_com(self,part):
        return False

    def can_equip(self,part):
        """Returns True if part can be legally installed here under current conditions"""
        return self.is_legal_inv_com(part) and part.scale == self.scale and not self.inv_com

    def sub_sub_coms(self):
        yield self
        for part in self.sub_com:
            for p in part.sub_sub_coms():
                yield p

    def ancestors(self):
        if hasattr( self, "container" ) and isinstance( self.container.owner, BaseGear ):
            yield self.container.owner
            for p in self.container.owner.ancestors():
                yield p

    def get_root(self):
        """Return the top level parent of this gear."""
        if hasattr( self, "container" ) and isinstance( self.container.owner, BaseGear ):
            return self.container.owner.get_root()
        else:
            return self

    def get_module( self ):
        for g in self.ancestors():
            if isinstance( g, Module ):
                return g


    def get_armor( self ):
        """Returns the armor protecting this gear."""
        for part in self.sub_com:
            if isinstance( part, Armor ):
                return part


    def __str__( self ):
        return self.name

    def termdump( self , prefix = ' ' , indent = 1 ):
        """Dump some info about this gear to the terminal."""
        print " " * indent + prefix + self.name + ' mass:' + str( self.mass ) + ' cost:$' + str( self.cost ) + " vol:" + str( self.free_volume ) + "/" + str( self.volume )
        for g in self.sub_com:
            g.termdump( prefix = '>' , indent = indent + 1 )
        for g in self.inv_com:
            g.termdump( prefix = '+' , indent = indent + 1 )

    def statusdump( self , prefix = ' ' , indent = 1 ):
        """Dump some info about this gear to the terminal."""
        print " " * indent + prefix + self.name + ' HP:{1}/{0}'.format(self.max_health,self.max_health-self.hp_damage)
        for g in self.sub_com:
            g.statusdump( prefix = '>' , indent = indent + 1 )
        for g in self.inv_com:
            g.statusdump( prefix = '+' , indent = indent + 1 )

#
#  Practical Gears
#

#   *****************
#   ***   ARMOR   ***
#   *****************

class Armor( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Armor"
    SAVE_PARAMETERS = ('size',)
    def __init__(self, size=1, **keywords ):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
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
    def volume(self):
        return self.size

    @property
    def base_cost(self):
        return 55*self.size

    def get_armor( self ):
        """Returns the armor protecting this gear."""
        return self

    def get_rating( self ):
        """Returns the penetration rating of this armor."""
        return (self.size * 10) * ( self.max_health - self.hp_damage ) // self.max_health

    def reduce_damage( self, dmg, dmg_request ):
        """Armor reduces damage taken, but gets damaged in the process."""
        max_absorb = min(self.scale.scale_health( 2, self.material ),dmg)
        absorb_amount = random.randint( max_absorb//5, max_absorb )
        if absorb_amount > 0:
            self.hp_damage = min( self.hp_damage + absorb_amount, self.max_health )
            dmg -= 2 * absorb_amount
        return dmg

#    def can_install(self,part):
#        """Returns True if part can be legally installed here under current conditions"""
#        return True


#   ****************************
#   ***   SUPPORT  SYSTEMS   ***
#   ****************************

class Engine( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Engine"
    SAVE_PARAMETERS = ('size',)
    def __init__(self, size=750, **keywords ):
        # Check the range of all parameters before applying.
        if size < 100:
            size = 100
        elif size > 2000:
            size = 2000
        self.size = size
        super(Engine, self).__init__(**keywords)
    @property
    def base_mass(self):
        return self.size // 100 + 10
    @property
    def volume(self):
        return self.size // 400 + 1
    @property
    def base_cost(self):
        return (self.size**2) // 1000
    base_health = 3
    def is_legal_sub_com(self,part):
        return isinstance( part , Armor )


class Gyroscope( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Gyroscope"
    base_mass = 10
    def is_legal_sub_com(self,part):
        return isinstance( part , Armor )
    volume = 2
    base_cost = 10
    base_health = 2

class Cockpit( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Cockpit"
    base_mass = 5
    def is_legal_sub_com(self,part):
        return isinstance( part , (Armor,Character) )
    def can_install(self,part):
        if isinstance( part, Character ):
            # Only one character per cockpit.
            return len( [item for item in self.sub_com if isinstance( item, Character )]) < 1
        else:
            return self.is_legal_sub_com(part) and part.scale <= self.scale and self.check_multiplicity( part )
    volume = 2
    base_cost = 5
    base_health = 2

class Sensor( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Sensor"
    SAVE_PARAMETERS = ('size',)
    def __init__(self, size=1, **keywords ):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 5:
            size = 5
        self.size = size
        super(Sensor, self).__init__(**keywords)
    @property
    def base_mass(self):
        return self.size * 5
    @property
    def base_cost(self):
        return self.size * self.size * 10
    @property
    def volume(self):
        return self.size
    base_health = 2

#   *****************************
#   ***   MOVEMENT  SYSTEMS   ***
#   *****************************

class MovementSystem( BaseGear ):
    DEFAULT_NAME = "MoveSys"
    SAVE_PARAMETERS = ('size',)
    def __init__(self, size=1, **keywords ):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        self.size = size
        super(MovementSystem, self).__init__(**keywords)
    @property
    def base_mass(self):
        return 10 * self.size
    @property
    def volume(self):
        return self.size
    @property
    def base_cost(self):
        return self.size * self.MOVESYS_COST

class HoverJets( MovementSystem, StandardDamageHandler ):
    DEFAULT_NAME = "Hover Jets"
    MOVESYS_COST = 56
    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

#   *************************
#   ***   POWER  SOURCE   ***
#   *************************

class PowerSource( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Power Source"
    SAVE_PARAMETERS = ('size',)
    def __init__(self,size=1, **keywords ):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        self.size = size
        super(PowerSource, self).__init__(**keywords)
    @property
    def base_mass(self):
        return 5 * self.size
    @property
    def volume(self):
        return self.size
    @property
    def base_cost(self):
        return self.size * 75
    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size

#   *******************
#   ***   WEAPONS   ***
#   *******************

class Weapon( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Weapon"
    DEFAULT_CALIBRE = None
    SAVE_PARAMETERS = ('reach','damage','accuracy','penetration','integral','ammo_type')
    # Note that this class doesn't implement any MIN_*,MAX_* constants, so it
    # cannot be instantiated. Subclasses should do that.
    def __init__(self, reach=1, damage=1, accuracy=1, penetration=1, **keywords ):
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

        self.integral = keywords.pop( "integral" , False )

        self.ammo_type = keywords.pop( "ammo_type" , self.DEFAULT_CALIBRE )

        # Finally, call the gear initializer.
        super(Weapon, self).__init__(**keywords)

    @property
    def base_mass(self):
        return ( self.damage + self.penetration ) * 5 + self.accuracy + self.reach

    @property
    def volume(self):
        v = max(self.reach + self.accuracy + ( self.damage + self.penetration )/2,1)
        if self.integral:
            v -= 1
        return v

    @property
    def energy(self):
        return 1

    @property
    def base_cost(self):
        # Multiply the stats together, squaring damage and range because they're so important.
        return self.COST_FACTOR * ( self.damage ** 2 ) * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * (( self.reach**2 - self.reach )/2 + 1)

    def is_legal_sub_com(self,part):
        if isinstance( part , Weapon ):
            return part.integral
        else:
            return False

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.base_mass

    def is_operational( self ):
        """ To be operational, a weapon must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()



class MeleeWeapon( Weapon ):
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 3

class EnergyWeapon( Weapon ):
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 20

class Ammo( BaseGear, Stackable, StandardDamageHandler ):
    DEFAULT_NAME = "Ammo"
    STACK_CRITERIA = ("ammo_type",)
    SAVE_PARAMETERS = ('ammo_type','quantity')
    def __init__(self, ammo_type=calibre.Shells_150mm, quantity=12, **keywords ):
        # Check the range of all parameters before applying.
        self.ammo_type = ammo_type
        self.quantity = max( quantity, 1 )

        # Finally, call the gear initializer.
        super(Ammo, self).__init__(**keywords)
    @property
    def base_mass(self):
        return self.ammo_type.bang * self.quantity //25
    @property
    def volume(self):
        return ( self.ammo_type.bang * self.quantity + 49 ) // 50

    @property
    def base_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        return self.ammo_type.bang * self.quantity // 10
    base_health = 1

class BallisticWeapon( Weapon ):
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 5
    DEFAULT_CALIBRE = calibre.Shells_150mm
    def is_legal_sub_com(self,part):
        if isinstance( part , Weapon ):
            return part.integral
        else:
            return isinstance( part, Ammo ) and part.ammo_type is self.ammo_type

class BeamWeapon( Weapon ):
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    COST_FACTOR = 15

class Missile( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Missile"
    SAVE_PARAMETERS = ('reach','damage','accuracy','penetration','quantity')
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    STACK_CRITERIA = ("reach","damage","accuracy","penetration")
    def __init__(self, reach=1,damage=1,accuracy=1,penetration=1,quantity=12,**keywords ):
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

        self.quantity = max( quantity, 1 )

        # Finally, call the gear initializer.
        super(Missile, self).__init__(**keywords)

    @property
    def base_mass(self):
        return ((( self.damage + self.penetration ) * 5 + self.accuracy + self.reach ) * self.quantity ) //25

    @property
    def volume(self):
        return ( ( self.reach + self.accuracy + self.damage + self.penetration + 1 ) * self.quantity + 49 ) // 50

    @property
    def base_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        return ((self.damage**2) * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * ( self.reach**2 - self.reach + 2)) * self.quantity / 8

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.volume // 2 + 1


class Launcher( BaseGear, ContainerDamageHandler ):
    DEFAULT_NAME = "Launcher"
    SAVE_PARAMETERS = ('size',)
    def __init__(self, size=5, **keywords ):
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 20:
            size = 20
        self.size = size
        super(Launcher, self).__init__(**keywords)
    @property
    def base_mass(self):
        return self.size
    @property
    def volume(self):
        return self.size
    @property
    def base_cost(self):
        return self.size * 25
    def is_legal_sub_com( self, part ):
        return isinstance( part , Missile ) and part.volume <= self.volume

#   *******************
#   ***   HOLDERS   ***
#   *******************

class Hand( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Hand"
    base_mass = 5
    def is_legal_inv_com(self,part):
        return isinstance( part, (Weapon,Launcher) )
    base_cost = 50
    base_health = 2

class Mount( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Weapon Mount"
    base_mass = 5
    def is_legal_inv_com(self,part):
        return isinstance( part, ( Weapon,Launcher ) )
    base_cost = 50
    base_health = 2

#   *******************
#   ***   USABLES   ***
#   *******************

class Usable( BaseGear ):
    # No usable gears yet, but I wanted to include this class definition
    # because it's needed by the construction rules below.
    DEFAULT_NAME = "Do Nothing Usable"


#   *******************
#   ***   MODULES   ***
#   *******************

class ModuleForm( Singleton ):
    @classmethod
    def is_legal_sub_com( self, part ):
        return False
    @classmethod
    def is_legal_inv_com( self, part ):
        return False
    MULTIPLICITY_LIMITS = {
        Engine:1,Hand:1,Mount:1,Cockpit:1,Gyroscope:1,Armor:1
    }
    @classmethod
    def check_multiplicity( self, mod, part ):
        """Returns True if part within acceptable limits for its kind."""
        ok = True
        for k,v in self.MULTIPLICITY_LIMITS.items():
            if isinstance( part, k ):
                ok = ok and len( [item for item in mod.sub_com if isinstance( item, k ) ] ) < v
        return ok

    VOLUME_X = 2
    MASS_X = 1

class MF_Head( ModuleForm ):
    name = "Head"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher,Armor,Sensor,Cockpit,Mount,MovementSystem,PowerSource,Usable ) )

class MF_Torso( ModuleForm ):
    name = "Torso"
    MULTIPLICITY_LIMITS = {
        Engine:1,Mount:2,Cockpit:1,Gyroscope:1,Armor:1
    }
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher,Armor,Sensor,Cockpit,Mount,MovementSystem,PowerSource,Usable,Engine,Gyroscope ) )
    VOLUME_X = 4
    MASS_X = 2

class MF_Arm( ModuleForm ):
    name = "Arm"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher, Armor, Hand, Mount,MovementSystem,PowerSource,Sensor,Usable ) )

class MF_Leg( ModuleForm ):
    name = "Leg"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Wing( ModuleForm ):
    name = "Wing"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Turret( ModuleForm ):
    name = "Turret"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Tail( ModuleForm ):
    name = "Tail"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Storage( ModuleForm ):
    name = "Storage"
    @classmethod
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )
    VOLUME_X = 4
    MASS_X = 0

class Module( BaseGear, StandardDamageHandler ):
    SAVE_PARAMETERS = ('form','size')
    def __init__(self, form=MF_Storage, size=1, info_tier=None, **keywords ):
        keywords[ "name" ] = keywords.pop( "name", form.name )
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form
        if info_tier not in (None,1,2,3):
            info_tier = None
        self.info_tier = info_tier
        super(Module, self).__init__(**keywords)
    @property
    def base_mass(self):
        return 2  * self.form.MASS_X * self.size
    @property
    def base_cost(self):
        return self.size * 25
    @property
    def volume(self):
        return self.size * self.form.VOLUME_X

    def check_multiplicity( self, part ):
        return self.form.check_multiplicity( self, part )

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return self.form.is_legal_inv_com( part )

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return 1 + self.form.MASS_X * self.size


class Head( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Head
        super(Head, self).__init__(**keywords)

class SuperBoom( pbge.scenes.animobs.AnimOb ):
    def __init__(self, pos=(0,0), loop=0, delay=1, y_off=0 ):
        super(SuperBoom, self).__init__(sprite_name="anim_frogatto_nuke.png",pos=pos,start_frame=0,end_frame=9,loop=loop,ticks_per_frame=1, delay=delay, y_off=y_off)


class Torso( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Torso
        super(Torso, self).__init__(**keywords)
    def on_destruction( self, camp, anim_list ):
        my_root = self.get_root()
        my_invo = pbge.effects.Invocation( fx=pbge.effects.NoEffect(anim=SuperBoom), area=pbge.scenes.targetarea.SelfCentered(delay_from=-1) )
        my_invo.invoke(camp,None,[my_root.pos,],anim_list)

class Arm( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Arm
        super(Arm, self).__init__(**keywords)

class Leg( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Leg
        super(Leg, self).__init__(**keywords)

class Wing( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Wing
        super(Wing, self).__init__(**keywords)

class Turret( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Turret()
        Module.__init__( self , **keywords )

class Tail( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Tail
        super(Tail, self).__init__(**keywords)

class Storage( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Storage
        super(Storage, self).__init__(**keywords)

#   *****************
#   ***   MECHA   ***
#   *****************

class MT_Battroid( Singleton ):
    name = "Battroid"
    @classmethod
    def is_legal_sub_com( self, part ):
        if isinstance( part , Module ):
            return not isinstance( part.form , MF_Turret )
        else:
            return False


class Mecha(BaseGear,ContainerDamageHandler):
    SAVE_PARAMETERS = ('name','form')
    def __init__(self, form=MT_Battroid, **keywords ):
        name = keywords.get(  "name" )
        if name == None:
            keywords[ "name" ] = form.name
        self.form = form
        super(Mecha, self).__init__(**keywords)

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return True

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    base_mass = 0

    def check_multiplicity( self, part ):
        # A mecha can have only one torso module.
        if isinstance( part , Module ) and part.form == MF_Torso:
            n = 0
            for i in self.sub_com:
                if isinstance( i, Module ) and i.form == MF_Torso:
                    n += 1
            return n == 0
        else:
            return True

    def can_install(self,part):
        return self.is_legal_sub_com(part) and part.scale <= self.scale and self.check_multiplicity( part )

    def can_equip(self,part):
        """Returns True if part can be legally equipped under current conditions"""
        return self.is_legal_inv_com(part) and part.scale <= self.scale

    @property
    def volume(self):
        return sum( i.volume for i in self.sub_com )

    def is_not_destroyed( self ):
        """ A mecha must have a notdestroyed body with a notdestroyed engine
            in it.
        """
        # Check out the body.
        for m in self.sub_com:
            if isinstance( m, Torso ) and m.is_not_destroyed():
                for e in m.sub_com:
                    if isinstance( e, Engine ) and e.is_not_destroyed() and e.scale is self.scale:
                        return True

    def is_operational( self ):
        """ To be operational, a mecha must have a pilot.
        """
        pilot = self.get_pilot()
        return self.is_not_destroyed() and pilot and pilot.is_operational()

    def get_pilot( self ):
        """Return the character who is operating this mecha."""
        for m in self.sub_sub_coms():
            if isinstance(m,Character):
                return m

    def load_pilot( self, pilot ):
        """Stick the pilot into the mecha."""
        cpit = None
        for m in self.sub_sub_coms():
            if isinstance(m,Cockpit):
                cpit = m
        cpit.sub_com.append( pilot )

    def calc_mobility( self ):
        """Calculate the mobility ranking of this mecha.
        """
        mass_factor = ( self.mass ** 2 ) // ( 10000 *  self.scale.SIZE_FACTOR ** 6 )
        has_gyro = False
        engine_rating = 0
        for m in self.sub_com:
            if isinstance( m, Torso ) and m.is_not_destroyed():
                for e in m.sub_com:
                    if isinstance( e, Engine ) and e.is_not_destroyed() and e.scale is self.scale:
                        engine_rating = e.size
                    elif isinstance( e, Gyroscope ) and e.is_not_destroyed() and e.scale is self.scale:
                        has_gyro = True
                break
        # We now have the mass_factor, engine_rating, and has_gyro.
        it = engine_rating // mass_factor
        if not has_gyro:
            it -= 30
        return it

class Character(BaseGear,StandardDamageHandler):
    SAVE_PARAMETERS = ('name','form')
    DEFAULT_SCALE = scale.HumanScale
    DEFAULT_MATERIAL = materials.Meat
    def __init__(self, **keywords ):
        super(Character, self).__init__(**keywords)

    def is_legal_sub_com( self, part ):
        return isinstance( part , Module )

    def is_legal_inv_com( self, part ):
        return True

    def can_install(self,part):
        return self.is_legal_sub_com(part) and part.scale is self.scale and self.check_multiplicity( part )

    def can_equip(self,part):
        """Returns True if part can be legally equipped under current conditions"""
        return self.is_legal_inv_com(part) and part.scale <= self.scale

    @property
    def volume(self):
        return sum( i.volume for i in self.sub_com )

    def is_not_destroyed( self ):
        """ A character doesn't need a body or head, but if present must not
            be destroyed.
        """
        is_ok = self.max_health > self.hp_damage
        # Check out the body.
        for m in self.sub_com:
            if isinstance( m, (Torso,Head) ) and m.is_destroyed():
                is_ok = False
                break
        return is_ok

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this character."""
        return self.volume // 2 + 1

    def get_pilot( self ):
        """Return the character itself."""
        return self

    def calc_mobility( self ):
        """Calculate the mobility ranking of this character.
        """
        return 50


