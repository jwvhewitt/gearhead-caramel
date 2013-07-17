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

class BallisticWeapon( Weapon ):
    MIN_REACH = 2
    MAX_REACH = 7
    MIN_DAMAGE = 1
    MAX_DAMAGE = 5
    MIN_ACCURACY = 0
    MAX_ACCURACY = 5
    MIN_PENETRATION = 0
    MAX_PENETRATION = 5



class ModuleForm( object ):
    def __init__( self, name ):
        self.name = name

class Head( ModuleForm ):
    def is_legal_inv_com( self, part ):
        return False

class Module( Gear ):
    def __init__(self, name = "Mecha", scale = 2, form=None):
        Gear.__init__( self, name , scale )
        self.form = form


class Mecha(Gear):
    def __init__(self, name = "Mecha", scale = 2):
        Gear.__init__( self, name , scale )

    # Overwriting a property with a value... isn't this the opposite of how
    # things are usually done?
    self_mass = 0

    def is_legal_sub_com(self,part):
        # A mecha may have modules as subcomponents.
        return isinstance( part , Module )




        
if __name__=='__main__':

    G1 = Gear()
    G2 = Mecha()

    G1.sub_com.append(G2)

    G1.name = "Bob"

    print G1

    print "Hello Windows"

