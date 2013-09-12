import container
import materials

def scale_mass( mass , scale , material ):
    # Scale mass based on scale and material.
    return ( mass * 10^scale * material.mass_scale ) / 5

def scale_cost( cost , scale , material ):
    # Scale mass based on scale and material.
    return ( cost * 10^scale * material.cost_scale ) / 5

class Gear( object ):

    def __init__(self, name = "Gear", scale = 0, material = materials.METAL ):
        self.sub_com = container.ContainerList()
        self.inv_com = container.ContainerList()
        self.name = name
        self.scale = scale
        self.material = material


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

class Armor( Gear ):
    def __init__(self, name="Armor", scale=0, material=materials.METAL, size = 1 ):
        Gear.__init__( self, name = name , scale = scale , material = material )
        # Check the range of all parameters before applying.
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
    def __init__(self, name="Weapon", scale=0, material=materials.METAL, reach=1, damage=1, accuracy=1, penetration=1 ):
        Gear.__init__( self, name , scale , material )
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
    def __init__(self, name = None, scale = 2, material = materials.METAL, size = 1, form=None):
        if form == None:
            form = MF_Storage()
        if name == None:
            name = form.name
        Gear.__init__( self, name = name , scale = scale , material = material )
        # Check the range of all parameters before applying.
        if size < 1:
            size = 1
        elif size > 10:
            size = 10
        self.size = size
        self.form = form

    @property
    def self_mass(self):
        return scale_mass( 2  * self.form.MASS_X , self.scale , self.material )

    @property
    def volume(self):
        return self.size * self.form.VOLUME_X

    def is_legal_sub_com( self, part ):
        return self.form.is_legal_sub_com( part )

    def is_legal_inv_com( self, part ):
        return self.form.is_legal_inv_com( part )

class Battroid( object ):
    name = "Battroid"
    def is_legal_sub_com( self, part ):
        if isinstance( part , Module ):
            return not isinstance( part.form , MF_Turret )
        else:
            return False


class Mecha(Gear):
    def __init__(self, name = "Mecha", scale = 2, material = materials.METAL, form=None):
        if form == None:
            form = Battroid()
        if name == None:
            name = form.name
        Gear.__init__( self, name , scale , material )
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

