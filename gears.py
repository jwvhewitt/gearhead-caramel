import container
import materials

def scale_mass( mass , scale , material ):
    # Scale mass based on scale and material.
    return int( ( mass * pow( 10 , scale ) * material.mass_scale ) / 5 )

def scale_cost( cost , scale , material ):
    # Scale mass based on scale and material.
    return ( cost * pow( 10 , scale ) * material.cost_scale ) / 5

class Gear( object ):

    def __init__(self, **keywords ):
        self.sub_com = container.ContainerList( owner = self )
        self.inv_com = container.ContainerList( owner = self )
        self.name = self.get_keyval( keywords , "name" , "Gear" )
        if "desig" in keywords:
            self.desig = keywords["desig"]
        self.scale = self.get_keyval( keywords , "scale" , 2 )
        self.material = self.get_keyval( keywords , "material" , materials.METAL )

    def get_keyval( self , keywords , kw , default = None ):
        if kw in keywords:
            return keywords[ kw ]
        else:
            return default

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

    def termdump( self , prefix = ' ' , indent = 1 ):
        """Dump some info about this gear to the terminal."""
        print " " * indent + prefix + self.name + "  SF:" + str( self.scale ) + ' mass:' + str( self.mass )
        for g in self.sub_com:
            g.termdump( prefix = '>' , indent = indent + 1 )
        for g in self.inv_com:
            g.termdump( prefix = '+' , indent = indent + 1 )

class Armor( Gear ):
    def __init__(self, **keywords ):
        Gear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        size = self.get_keyval( keywords , "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size

    @property
    def self_mass(self):
        return scale_mass( 8 * self.size , self.scale , self.material )

    @property
    def volume(self):
        return self.size


class Weapon( Gear ):
    # Note that this class doesn't implement any MIN_*,MAX_* constants, so it
    # cannot be instantiated. Subclasses should do that.
    def __init__(self, **keywords ):
        Gear.__init__( self, **keywords )

        # Check the range of all parameters before applying.
        reach = self.get_keyval( keywords , "reach" , 1 )
        if reach < self.__class__.MIN_REACH:
            reach = self.__class__.MIN_REACH
        elif reach > self.__class__.MAX_REACH:
            reach = self.__class__.MAX_REACH
        self.reach = reach

        damage = self.get_keyval( keywords , "damage" , 1 )
        if damage < self.__class__.MIN_DAMAGE:
            damage = self.__class__.MIN_DAMAGE
        elif damage > self.__class__.MAX_DAMAGE:
            damage = self.__class__.MAX_DAMAGE
        self.damage = damage

        accuracy = self.get_keyval( keywords , "accuracy" , 1 )
        if accuracy < self.__class__.MIN_ACCURACY:
            accuracy = self.__class__.MIN_ACCURACY
        elif accuracy > self.__class__.MAX_ACCURACY:
            accuracy = self.__class__.MAX_ACCURACY
        self.accuracy = accuracy

        penetration = self.get_keyval( keywords , "penetration" , 1 )
        if penetration < self.__class__.MIN_PENETRATION:
            penetration = self.__class__.MIN_PENETRATION
        elif penetration > self.__class__.MAX_PENETRATION:
            penetration = self.__class__.MAX_PENETRATION
        self.penetration = penetration

    @property
    def self_mass(self):
        return scale_mass( ( self.damage + self.penetration ) * 5 , self.scale , self.material )

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
    MIN_REACH = 1
    MAX_REACH = 3
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5


class ModuleForm( object ):
    def is_legal_sub_com( self, part ):
        return False
    def is_legal_inv_com( self, part ):
        return False
    VOLUME_X = 1
    MASS_X = 1

class MF_Head( ModuleForm ):
    name = "Head"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Torso( ModuleForm ):
    name = "Torso"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )
    VOLUME_X = 2
    MASS_X = 2

class MF_Arm( ModuleForm ):
    name = "Arm"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Leg( ModuleForm ):
    name = "Leg"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Wing( ModuleForm ):
    name = "Wing"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Turret( ModuleForm ):
    name = "Turret"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Tail( ModuleForm ):
    name = "Tail"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )

class MF_Storage( ModuleForm ):
    name = "Storage"
    def is_legal_sub_com( self, part ):
        return isinstance( part , Weapon ) or isinstance( part , Armor )
    VOLUME_X = 2
    MASS_X = 0


class Module( Gear ):
    def __init__(self, **keywords ):
        form = self.get_keyval( keywords , "form" )
        if form == None:
            form = MF_Storage()
        name = self.get_keyval( keywords , "name" )
        if name == None:
            keywords[ "name" ] = form.name
        Gear.__init__( self, **keywords )
        # Check the range of all parameters before applying.
        size = self.get_keyval( keywords , "size" , 1 )
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form

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
        form = self.get_keyval( keywords , "form" )
        if form == None:
            form = Battroid()
        name = self.get_keyval( keywords , "name" )
        if name == None:
            keywords[ "name" ] = form.name
        Gear.__init__( self, **keywords )
        self.form = form

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return True

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    self_mass = 0




        
if __name__=='__main__':

    G1 = Gear()
    G2 = Armor( size = 5 )

    G1.sub_com.append(G2)

    G1.name = "Bob"

    print G1
    print repr( G2 )

    print "Hello Windows"

