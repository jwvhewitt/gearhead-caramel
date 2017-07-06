import container
import materials
import calibre

class MechaScale( object ):
    SIZE_FACTOR = 10
    COST_FACTOR = 2
    @classmethod
    def scale_mass( self, mass, material ):
        # Scale mass based on scale and material.
        # The universal mass unit is 100 grams.
        return int( ( mass * pow( self.SIZE_FACTOR, 3 ) * material.mass_scale ) // 10 )
    @classmethod
    def scale_cost( self, cost , material ):
        # Scale mass based on scale and material.
        return ( cost * self.SIZE_FACTOR*self.COST_FACTOR * material.cost_scale ) // 10
    @classmethod
    def scale_health( self, hp , material ):
        # Scale mass based on scale and material.
        return ( hp * ( self.SIZE_FACTOR ** 2 ) * material.damage_scale ) // 2

class HumanScale( MechaScale ):
    SIZE_FACTOR = 1
    COST_FACTOR = 5

#
# Damage Handlers
#
#  Each "practical" gear should subclass one of the damage handlers.
#

class StandardDamageHandler( object ):
    # This gear type has health and takes damage. It is destroyed when the
    # amount of damage taken exceeds its maximum capacity.
    def __init__( self ):
        self.hp_damage = 0

    base_health = 1

    @property
    def max_health( self ):
        """Returns the scaled maximum health of this gear."""
        return self.scale.scale_health( self.base_health, self.material )

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

    def is_operational( self ):
        """ Returns True if this gear is okay and all of its necessary subcoms
            are operational too. In other words, return True if this gear is
            ready to be used.
        """
        return self.is_not_destroyed()

    def is_active( self ):
        """ Returns True if this gear is okay and capable of independent action.
        """
        return False

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
    def can_be_damaged( self ):
        """ Returns True if this gear can be damaged.
        """
        return False
    def is_not_destroyed( self ):
        """ Returns True if this gear is not destroyed.
            Note that this doesn't indicate the part is functional- just that
            it would be functional if installed correctly, provided with power,
            et cetera.
        """
        return True

class ContainerDamageHandler( StandardDamageHandler ):
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


class BaseGear( object ):
    DEFAULT_NAME = "Gear"
    DEFAULT_MATERIAL = materials.METAL
    def __init__(self, **keywords ):
        self.name = keywords.get( "name" , self.DEFAULT_NAME )
        self.desig = keywords.get( "desig", None )
        self.scale = keywords.get( "scale" , MechaScale )
        self.material = keywords.get( "material" , self.DEFAULT_MATERIAL )
        self.hp_damage = 0

        self.sub_com = container.ContainerList( owner = self )
        sc_to_add = keywords.get( "sub_com", [] )
        for i in sc_to_add:
            if self.can_install( i ):
                self.sub_com.append( i )
            else:
                print( "ERROR: {} cannot be installed in {}".format(i,self) )

        self.inv_com = container.ContainerList( owner = self )
        ic_to_add = keywords.get( "inv_com", [] )
        for i in ic_to_add:
            if self.can_equip( i ):
                self.inv_com.append( i )
            else:
                print( "ERROR: {} cannot be equipped in {}".format(i,self) )

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
        """Returns the true mass of this gear including children."""
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
        if hasattr( self, "container" ) and isinstance( self.container.owner, Gear ):
            yield self.container.owner
            for p in self.container.owner.ancestors():
                yield p

    def find_module( self ):
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



class Stackable( object ):
    def can_merge_with( self, part ):
        return ( self.__class__ is part.__class__ and self.scale is part.scale
            and self.name is part.name and self.desig is part.desig
            and not self.inv_com and not self.sub_com )


#   *****************
#   ***   ARMOR   ***
#   *****************

class Armor( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Armor"
    def __init__(self, size=1, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        BaseGear.__init__( self, **keywords )

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


#   ****************************
#   ***   SUPPORT  SYSTEMS   ***
#   ****************************

class Engine( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Engine"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 750 )
        if size < 100:
            size = 100
        elif size > 2000:
            size = 2000
        self.size = size
        BaseGear.__init__( self, **keywords )
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
        return isinstance( part , Armor )
    volume = 2
    base_cost = 5
    base_health = 2

class Sensor( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Sensor"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 5:
            size = 5
        self.size = size
        BaseGear.__init__( self, **keywords )
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
    def __init__(self, **keywords ):
        BaseGear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        self.size = size
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
    def __init__(self, **keywords ):
        BaseGear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        self.size = size
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
#   ***   USABLES   ***
#   *******************

class Usable( BaseGear ):
    DEFAULT_NAME = "Do Nothing Usable"

#   *******************
#   ***   WEAPONS   ***
#   *******************

class Weapon( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Weapon"
    DEFAULT_CALIBRE = None
    # Note that this class doesn't implement any MIN_*,MAX_* constants, so it
    # cannot be instantiated. Subclasses should do that.
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        reach = keywords.get( "reach" , 1 )
        if reach < self.__class__.MIN_REACH:
            reach = self.__class__.MIN_REACH
        elif reach > self.__class__.MAX_REACH:
            reach = self.__class__.MAX_REACH
        self.reach = reach

        damage = keywords.get( "damage" , 1 )
        if damage < self.__class__.MIN_DAMAGE:
            damage = self.__class__.MIN_DAMAGE
        elif damage > self.__class__.MAX_DAMAGE:
            damage = self.__class__.MAX_DAMAGE
        self.damage = damage

        accuracy = keywords.get( "accuracy" , 1 )
        if accuracy < self.__class__.MIN_ACCURACY:
            accuracy = self.__class__.MIN_ACCURACY
        elif accuracy > self.__class__.MAX_ACCURACY:
            accuracy = self.__class__.MAX_ACCURACY
        self.accuracy = accuracy

        penetration = keywords.get( "penetration" , 1 )
        if penetration < self.__class__.MIN_PENETRATION:
            penetration = self.__class__.MIN_PENETRATION
        elif penetration > self.__class__.MAX_PENETRATION:
            penetration = self.__class__.MAX_PENETRATION
        self.penetration = penetration

        self.integral = keywords.get( "integral" , False )

        self.ammo_type = keywords.get( "calibre" , self.DEFAULT_CALIBRE )

        # Finally, call the gear initializer.
        BaseGear.__init__( self, **keywords )

    @property
    def base_mass(self):
        return ( self.damage + self.penetration ) * 5 + self.accuracy + self.reach

    @property
    def volume(self):
        v = self.reach + self.accuracy + 1
        if self.integral:
            v -= 1
        return v

    @property
    def energy(self):
        return 1

    @property
    def base_cost(self):
        # Multiply the stats together, squaring damage and range because it's so important.
        return self.COST_FACTOR * ( self.damage ** 2 ) * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * (( self.reach**2 - self.reach )/2 + 1)

    def is_legal_sub_com(self,part):
        if isinstance( part , Weapon ):
            # In theory weapons should be able to install weapons which are integral.
            # However, since I haven't yet implemented integralness... ^^;
            return False
        else:
            return False

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.base_mass


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

class Ammo( BaseGear, Stackable ):
    DEFAULT_NAME = "Ammo"
    STACK_CRITERIA = ("ammo_type",)
    def __init__(self, **keywords ):
        BaseGear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        self.ammo_type = keywords.get( "calibre" , calibre.Shells_150mm )
        self.quantity = max( keywords.get( "quantity" , 12 ), 1 )

        # Finally, call the gear initializer.
        BaseGear.__init__( self, **keywords )
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
            # In theory weapons should be able to install weapons which are integral.
            # However, since I haven't yet implemented integralness... ^^;
            return False
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

class Missile( BaseGear ):
    DEFAULT_NAME = "Missile"
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5
    STACK_CRITERIA = ("reach","damage","accuracy","penetration")
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        reach = keywords.get( "reach" , 1 )
        if reach < self.__class__.MIN_REACH:
            reach = self.__class__.MIN_REACH
        elif reach > self.__class__.MAX_REACH:
            reach = self.__class__.MAX_REACH
        self.reach = reach

        damage = keywords.get( "damage" , 1 )
        if damage < self.__class__.MIN_DAMAGE:
            damage = self.__class__.MIN_DAMAGE
        elif damage > self.__class__.MAX_DAMAGE:
            damage = self.__class__.MAX_DAMAGE
        self.damage = damage

        accuracy = keywords.get( "accuracy" , 1 )
        if accuracy < self.__class__.MIN_ACCURACY:
            accuracy = self.__class__.MIN_ACCURACY
        elif accuracy > self.__class__.MAX_ACCURACY:
            accuracy = self.__class__.MAX_ACCURACY
        self.accuracy = accuracy

        penetration = keywords.get( "penetration" , 1 )
        if penetration < self.__class__.MIN_PENETRATION:
            penetration = self.__class__.MIN_PENETRATION
        elif penetration > self.__class__.MAX_PENETRATION:
            penetration = self.__class__.MAX_PENETRATION
        self.penetration = penetration

        self.quantity = max( keywords.get( "quantity" , 12 ), 1 )

        # Finally, call the gear initializer.
        BaseGear.__init__( self, **keywords )

    @property
    def base_mass(self):
        return ( ( self.damage + self.penetration ) * 5 + self.accuracy + self.reach * self.quantity ) //25

    @property
    def volume(self):
        return ( ( self.reach + self.accuracy + 1 ) * self.quantity + 49 ) // 50

    @property
    def base_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        return ((self.damage**2) * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * ( self.reach**2 - self.reach + 2)) * self.quantity / 8

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.volume // 2 + 1


class Launcher( BaseGear ):
    DEFAULT_NAME = "Launcher"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 20:
            size = 20
        self.size = size
        BaseGear.__init__( self, **keywords )
    @property
    def base_mass(self):
        return self.size
    @property
    def volume(self):
        return self.size
    @property
    def base_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        return self.size * 25
    def is_legal_sub_com( self, part ):
        return isinstance( part , Missile )


#   *******************
#   ***   HOLDERS   ***
#   *******************

class Hand( BaseGear ):
    DEFAULT_NAME = "Hand"
    base_mass = 5
    def is_legal_inv_com(self,part):
        return isinstance( part, (Weapon,Launcher) )
    base_cost = 50
    base_health = 2

class Mount( BaseGear ):
    DEFAULT_NAME = "Weapon Mount"
    base_mass = 5
    def is_legal_inv_com(self,part):
        return isinstance( part, ( Weapon,Launcher ) )
    base_cost = 50
    base_health = 2

#   *******************
#   ***   MODULES   ***
#   *******************


class ModuleForm( object ):
    def is_legal_sub_com( self, part ):
        return False
    def is_legal_inv_com( self, part ):
        return False
    MULTIPLICITY_LIMITS = {
        Engine:1,Hand:1,Mount:1,Cockpit:1,Gyroscope:1
    }
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
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher,Armor,Sensor,Cockpit,Mount,MovementSystem,PowerSource,Usable ) )

class MF_Torso( ModuleForm ):
    name = "Torso"
    MULTIPLICITY_LIMITS = {
        Engine:1,Mount:2,Cockpit:1,Gyroscope:1
    }
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher,Armor,Sensor,Cockpit,Mount,MovementSystem,PowerSource,Usable,Engine,Gyroscope ) )
    VOLUME_X = 4
    MASS_X = 2

class MF_Arm( ModuleForm ):
    name = "Arm"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Launcher, Armor, Hand, Mount,MovementSystem,PowerSource,Sensor,Usable ) )

class MF_Leg( ModuleForm ):
    name = "Leg"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Wing( ModuleForm ):
    name = "Wing"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Turret( ModuleForm ):
    name = "Turret"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Tail( ModuleForm ):
    name = "Tail"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )

class MF_Storage( ModuleForm ):
    name = "Storage"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon,Launcher,Armor,MovementSystem,Mount,Sensor,PowerSource,Usable) )
    VOLUME_X = 4
    MASS_X = 0


class Module( BaseGear ):
    def __init__(self, **keywords ):
        form = keywords.get( "form" )
        if form == None:
            form = MF_Storage()
        keywords[ "name" ] = keywords.get( "name", form.name )
        # Check the range of all parameters before applying.
        size = keywords.get(  "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form
        BaseGear.__init__( self, **keywords )
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
        keywords[ "form" ] = MF_Head()
        Module.__init__( self , **keywords )

class Torso( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Torso()
        Module.__init__( self , **keywords )

class Arm( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Arm()
        Module.__init__( self , **keywords )

class Leg( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Leg()
        Module.__init__( self , **keywords )

class Wing( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Wing()
        Module.__init__( self , **keywords )

class Turret( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Turret()
        Module.__init__( self , **keywords )

class Tail( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Tail()
        Module.__init__( self , **keywords )

class Storage( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Storage()
        Module.__init__( self , **keywords )


#   *****************
#   ***   MECHA   ***
#   *****************

class MT_Battroid( object ):
    name = "Battroid"
    def is_legal_sub_com( self, part ):
        if isinstance( part , Module ):
            return not isinstance( part.form , MF_Turret )
        else:
            return False


class Mecha(BaseGear,StandardDamageHandler):
    def __init__(self, **keywords ):
        form = keywords.get(  "form" )
        if form == None:
            form = MT_Battroid()
        name = keywords.get(  "name" )
        if name == None:
            keywords[ "name" ] = form.name
        self.form = form
        BaseGear.__init__( self, **keywords )

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return True

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    base_mass = 0

    def check_multiplicity( self, part ):
        # A mecha can have only one torso module.
        if isinstance( part , Module ) and isinstance( part.form , MF_Torso ):
            n = 0
            for i in self.sub_com:
                if isinstance( i, Module ) and isinstance( i.form , MF_Torso ):
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
        """ To be operational, a mecha must have an operational engine.
        """
        return self.is_not_destroyed()

    def is_active( self ):
        """ To be active, a mecha must be operational and have an operational
            pilot.
        """
        return self.is_operational()

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


        
if __name__=='__main__':

    G1 = Gear()
    G2 = Armor( size = 5 )

    G1.sub_com.append(G2)

    G1.name = "Bob"

    print G1
    print repr( G2 )

    print "Hello Windows"

