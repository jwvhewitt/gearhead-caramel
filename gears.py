import container
import materials

def scale_mass( mass , scale , material ):
    # Scale mass based on scale and material.
    # The universal mass unit is 100 grams.
    return int( ( mass * pow( 10 , scale ) * material.mass_scale ) // 5 )

def scale_cost( cost , scale , material ):
    # Scale mass based on scale and material.
    return ( cost * pow( 10 , scale ) * material.cost_scale ) // 5

class Gear( object ):

    DEFAULT_NAME = "Gear"
    DEFAULT_MATERIAL = materials.METAL
    def __init__(self, **keywords ):
        self.inv_com = container.ContainerList( keywords.get( "inv_com", [] ), owner = self )
        self.name = keywords.get( "name" , self.DEFAULT_NAME )
        self.desig = keywords.get( "desig", None )
        self.scale = keywords.get( "scale" , 3 )
        self.material = keywords.get( "material" , self.DEFAULT_MATERIAL )

        self.sub_com = container.ContainerList( owner = self )
        sc_to_add = keywords.get( "sub_com", [] )
        for i in sc_to_add:
            if self.can_install( i ):
                self.sub_com.append( i )
            else:
                print( "ERROR: {} cannot be installed in {}".format(i,self) )

    @property
    def self_mass(self):
        return scale_mass( 1 , self.scale , self.material )

    @property
    def mass(self):
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

    @property
    def self_cost(self):
        return scale_cost( 1 , self.scale , self.material )

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

    def can_install(self,part):
        return self.is_legal_sub_com(part) and part.scale <= self.scale and part.volume <= self.free_volume

    def is_legal_inv_com(self,part):
        return False

    def sub_sub_coms(self):
        yield self
        for part in self.sub_com:
            for p in part.sub_sub_coms():
                yield p

    def can_be_installed( self , part ):
        """Returns True if part can be legally installed here under current conditions"""
        return self.is_legal_sub_com( part )

    def __str__( self ):
        return self.name

    def termdump( self , prefix = ' ' , indent = 1 ):
        """Dump some info about this gear to the terminal."""
        print " " * indent + prefix + self.name + "  SF:" + str( self.scale ) + ' mass:' + str( self.mass ) + " vol:" + str( self.free_volume ) + "/" + str( self.volume )
        for g in self.sub_com:
            g.termdump( prefix = '>' , indent = indent + 1 )
        for g in self.inv_com:
            g.termdump( prefix = '+' , indent = indent + 1 )

class Armor( Gear ):
    DEFAULT_NAME = "Armor"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        Gear.__init__( self, **keywords )

    @property
    def self_mass(self):
        return scale_mass( 9 * self.size , self.scale , self.material )

    @property
    def volume(self):
        return self.size

class Engine( Gear ):
    DEFAULT_NAME = "Engine"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 750 )
        if size < 100:
            size = 100
        elif size > 2000:
            size = 2000
        self.size = size
        Gear.__init__( self, **keywords )
    @property
    def self_mass(self):
        return scale_mass( self.size // 100 + 10 , self.scale , self.material )
    @property
    def volume(self):
        return self.size // 400 + 1
    def is_legal_sub_com(self,part):
        return isinstance( part , Armor )

class Gyroscope( Gear ):
    DEFAULT_NAME = "Gyroscope"
    @property
    def self_mass(self):
        return scale_mass( 10 , self.scale , self.material )
    def is_legal_sub_com(self,part):
        return isinstance( part , Armor )
    volume = 2

class Cockpit( Gear ):
    DEFAULT_NAME = "Cockpit"
    @property
    def self_mass(self):
        return scale_mass( 5 , self.scale , self.material )
    def is_legal_sub_com(self,part):
        return isinstance( part , Armor )
    volume = 2

class Sensor( Gear ):
    DEFAULT_NAME = "Sensor"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 5:
            size = 5
        self.size = size
        Gear.__init__( self, **keywords )
    @property
    def self_mass(self):
        return scale_mass( self.size * 5 , self.scale , self.material )
    @property
    def self_cost(self):
        return scale_cost( self.size * self.size * 10 , self.scale , self.material )
    @property
    def volume(self):
        return self.size

class HoverJets( Gear ):
    DEFAULT_NAME = "Hover Jets"
    def __init__(self, **keywords ):
        Gear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        self.size = size

    @property
    def self_mass(self):
        return scale_mass( 10 * self.size , self.scale , self.material )

    @property
    def volume(self):
        return self.size


class Weapon( Gear ):
    DEFAULT_NAME = "Weapon"
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

        # Finally, call the gear initializer.
        Gear.__init__( self, **keywords )

    @property
    def self_mass(self):
        return scale_mass( ( self.damage + self.penetration ) * 5 + self.accuracy + self.reach , self.scale , self.material )

    @property
    def volume(self):
        return self.reach + self.accuracy + 1

    @property
    def energy(self):
        return 1

    @property
    def self_cost(self):
        # Multiply the stats together, squaring range because it's so important.
        return scale_cost( self.damage * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * (( self.range^2 - self.range )/2 + 1) , self.scale , self.material )

    def is_legal_sub_com(self,part):
        if isinstance( part , Weapon ):
            # In theory weapons should be able to install weapons which are integral.
            # However, since I haven't yet implemented integralness... ^^;
            return False
        else:
            return False

class MeleeWeapon( Weapon ):
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5

class EnergyWeapon( Weapon ):
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5

class BallisticWeapon( Weapon ):
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5

class BeamWeapon( Weapon ):
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5

class Launcher( Gear ):
    DEFAULT_NAME = "Launcher"
    def __init__(self, **keywords ):
        # Check the range of all parameters before applying.
        size = keywords.get( "size" , 1 )
        if size < 1:
            size = 1
        elif size > 20:
            size = 20
        self.size = size
        Gear.__init__( self, **keywords )
    @property
    def self_mass(self):
        return scale_mass( self.size , self.scale , self.material )
    @property
    def volume(self):
        return self.size


class Hand( Gear ):
    DEFAULT_NAME = "Hand"
    @property
    def self_mass(self):
        return scale_mass( 5 , self.scale , self.material )
    def is_legal_inv_com(self,part):
        return isinstance( part, Weapon )

class Mount( Gear ):
    DEFAULT_NAME = "Weapon Mount"
    @property
    def self_mass(self):
        return scale_mass( 5 , self.scale , self.material )
    def is_legal_inv_com(self,part):
        return isinstance( part, Weapon )


class ModuleForm( object ):
    def is_legal_sub_com( self, part ):
        return False
    def is_legal_inv_com( self, part ):
        return False
    VOLUME_X = 2
    MASS_X = 1

class MF_Head( ModuleForm ):
    name = "Head"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Armor,Sensor,Cockpit,Mount ) )

class MF_Torso( ModuleForm ):
    name = "Torso"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon,Armor,Gyroscope,Sensor,Engine,Cockpit,Mount ) )
    VOLUME_X = 4
    MASS_X = 2

class MF_Arm( ModuleForm ):
    name = "Arm"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon, Armor, Hand, Mount ) )

class MF_Leg( ModuleForm ):
    name = "Leg"
    def is_legal_sub_com( self, part ):
        return isinstance( part , (Weapon, Armor, HoverJets ) )

class MF_Wing( ModuleForm ):
    name = "Wing"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon, Armor ) )

class MF_Turret( ModuleForm ):
    name = "Turret"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon, Armor ) )

class MF_Tail( ModuleForm ):
    name = "Tail"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon, Armor ) )

class MF_Storage( ModuleForm ):
    name = "Storage"
    def is_legal_sub_com( self, part ):
        return isinstance( part , ( Weapon, Armor ) )
    VOLUME_X = 4
    MASS_X = 0


class Module( Gear ):
    def __init__(self, **keywords ):
        form = keywords.get(  "form" )
        if form == None:
            form = MF_Storage()
        name = keywords.get(  "name" )
        if name == None:
            keywords[ "name" ] = form.name
        # Check the range of all parameters before applying.
        size = keywords.get(  "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form
        Gear.__init__( self, **keywords )

    @property
    def self_mass(self):
        return scale_mass( 2  * self.form.MASS_X * self.size , self.scale , self.material )

    @property
    def volume(self):
        return self.size * self.form.VOLUME_X

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return self.form.is_legal_inv_com( part )

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




class MT_Battroid( object ):
    name = "Battroid"
    def is_legal_sub_com( self, part ):
        if isinstance( part , Module ):
            return not isinstance( part.form , MF_Turret )
        else:
            return False


class Mecha(Gear):
    def __init__(self, **keywords ):
        form = keywords.get(  "form" )
        if form == None:
            form = MT_Battroid()
        name = keywords.get(  "name" )
        if name == None:
            keywords[ "name" ] = form.name
        self.form = form
        Gear.__init__( self, **keywords )

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return True

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    self_mass = 0

    def can_install(self,part):
        return self.is_legal_sub_com(part) and part.scale <= self.scale

    @property
    def volume(self):
        return sum( i.volume for i in self.sub_com )


        
if __name__=='__main__':

    G1 = Gear()
    G2 = Armor( size = 5 )

    G1.sub_com.append(G2)

    G1.name = "Bob"

    print G1
    print repr( G2 )

    print "Hello Windows"

