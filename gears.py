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

class MeleeWeapon( Gear ):

    def __init__(self, name = "Gear", scale = 0, material = materials.METAL, reach=1, damage=1, accuracy=1, penetration=1 ):
        Gear.__init__( self, name , scale , material )
        # Check the range of all parameters before applying.
        if reach < 1:
            reach = 1
        elif reach > 3:
            reach = 3
        self.reach = reach
        if damage < 1:
            damage = 1
        elif damage > 5:
            damage = 5
        self.damage = damage
        if accuracy < 1:
            accuracy = 1
        elif accuracy > 5:
            accuracy = 5
        self.accuracy = accuracy
        if penetration < 1:
            penetration = 1
        elif penetration > 5:
            penetration = 5
        self.penetration = penetration

    @property
    def self_mass(self):
        return scale_mass( ( self.damage + self.penetration ) * 5 , self.scale , self.material )

    @property
    def volume(self):
        return self.reach + self.accuracy

    @property
    def energy(self):
        return 1

    @property
    def self_cost(self):
        return scale_cost( self.damage * self.accuracy * self.penetration * self.range * 5 , self.scale , self.material )


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

