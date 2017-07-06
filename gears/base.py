import materials
import scale
import calibre
from pbge import container, scenes, KeyObject

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
    # This gear cannot be damaged or destroyed.
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
    def __init__(self, **keywords ):
        self.name = keywords.pop( "name" , self.DEFAULT_NAME )
        self.desig = keywords.pop( "desig", None )
        self.scale = keywords.pop( "scale" , scale.MechaScale )
        self.material = keywords.pop( "material" , self.DEFAULT_MATERIAL )
        self.imagename = keywords.pop( "imagename", "iso_item.png" )
        self.colors = keywords.pop( "colors", "" )


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

#
#  Practical Gears
#

#   *****************
#   ***   ARMOR   ***
#   *****************

class Armor( BaseGear, StandardDamageHandler ):
    DEFAULT_NAME = "Armor"
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

#    def can_install(self,part):
#        """Returns True if part can be legally installed here under current conditions"""
#        return True


