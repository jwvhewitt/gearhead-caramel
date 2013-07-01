import container

class Gear( object ):

    def __init__(self, name = "Gear", scale = 0):
        self.sub_com = container.ContainerList()
        self.inv_com = container.ContainerList()
        self.name = name
        self.scale = scale

    @property
    def self_mass(self):
        return 10 ^ self.scale

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

    value = 1

    def is_legal_sub_com(self,part):
        return False

    def is_legal_inv_com(self,part):
        return False

    def sub_sub_coms(self):
        yield self
        for part in self.sub_com:
            for p in part.sub_sub_coms():
                yield p


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

