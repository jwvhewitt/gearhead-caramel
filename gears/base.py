import materials
import scale
import calibre
import pbge
from pbge import container, scenes, KeyObject, Singleton
import random
import collections
import stats
import copy
import geffects
import attackattributes


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

    @property
    def current_health( self ):
        """Returns the scaled maximum health of this gear."""
        return self.max_health - self.hp_damage

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

class WithPortrait( pbge.scenes.PlaceableThing ):
    def __init__(self, portrait=None, **keywords ):
        self.portrait = portrait
        super(WithPortrait, self).__init__(**keywords)
    SAVE_PARAMETERS = ('portrait',)
    FRAMES = ((0,0,400,600),(0,600,100,100),(100,600,64,64))
    def get_sprite(self):
        """Generate the sprite for this thing."""
        if self.portrait and self.portrait.startswith('card_'):
            self.frame = 2
            return pbge.image.Image(self.portrait,self.imagewidth,self.imageheight,self.colors,custom_frames=self.FRAMES)
        else:
            return pbge.image.Image(self.imagename,self.imagewidth,self.imageheight,self.colors)
    def get_portrait(self):
        if self.portrait:
            if self.portrait.startswith('card_'):
                return pbge.image.Image(self.portrait,self.imagewidth,self.imageheight,self.colors,custom_frames=self.FRAMES)
            else:
                return pbge.image.Image(self.portrait,400,600,self.colors)


class Mover( KeyObject ):
    # A mover is a gear that moves under its own power, like a character or mecha.
    def __init__(self, **keywords ):
        self.mmode = None
        super(Mover, self).__init__(**keywords)
    def calc_walking( self ):
        # Count the number of leg points, divide by mass.
        return 0

    def calc_skimming( self ):
        norm_mass = self.scale.unscale_mass( self.mass )
        thrust = self.count_thrust_points( geffects.Skimming )

        if thrust > (norm_mass*20):
            return thrust // norm_mass
        else:
            return 0

    def get_speed(self,mmode):
        # This method returns the mover's movement points; under normal conditions
        # it costs 2MP to move along a cardinal direction or 3MP to move diagonally.
        # This cost will be adjusted for terrain and scale.
        if mmode is scenes.movement.Walking:
            return self.calc_walking()
        elif mmode is geffects.Skimming:
            return self.calc_skimming()
        else:
            return 0

    def get_current_speed(self):
        return self.get_speed(self.mmode)

    def count_module_points( self, module_form ):
        # Count the number of active module points, reducing rating for damage taken.
        total = 0
        for m in self.sub_com:
            if isinstance(m,Module) and (m.scale is self.scale) and (m.form == module_form) and m.is_not_destroyed():
                total += ( m.size * m.current_health + m.max_health - 1 )//m.max_health
        return total

    def count_modules( self, module_form ):
        # Returns the number of modules of the given type and the number
        # of them that are not destroyed.
        total,active = 0,0
        for m in self.sub_com:
            if isinstance(m,Module) and (m.scale is self.scale) and (m.form == module_form):
                total += 1
                if m.is_not_destroyed():
                    active += 1
        return total, active

    def count_thrust_points( self, move_mode ):
        total = 0
        for g in self.sub_com.get_undestroyed():
            if (g.scale is self.scale) and hasattr(g,'get_thrust'):
                total += g.get_thrust(move_mode)
        return total

    def get_attack_library( self ):
        my_invos = list()
        for p in self.descendants():
            if hasattr(p, 'get_attacks'):
                p_list = geffects.AttackLibraryShelf(p,p.get_attacks(self))
                if p_list.has_at_least_one_working_invo(self,True):
                    my_invos.append(p_list)
        return my_invos

    MOVEMODE_LIST = (scenes.movement.Walking,geffects.Rolling,geffects.Skimming,scenes.movement.Flying,geffects.SpaceFlight)
    def gear_up(self):
        for mm in self.MOVEMODE_LIST:
            if self.get_speed(mm) > 0:
                self.mmode = mm
                break


# Custom Containers
# For subcomponents and invcomponents with automatic error checking

class SubComContainerList( container.ContainerList ):
    def _set_container(self, item):
        if self.owner.can_install( item ):
            super( SubComContainerList, self )._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot subcom {}".format(self.owner,item))
    def get_undestroyed(self):
        # Return all non-destroyed gears, including descendants.
        for g in self:
            if g.is_not_destroyed():
                yield g
                for p in g.sub_com.get_undestroyed():
                    yield p
                for p in g.inv_com.get_undestroyed():
                    yield p

class InvComContainerList( container.ContainerList ):
    def _set_container(self, item):
        if self.owner.can_equip( item ):
            super( InvComContainerList, self )._set_container(item)
        else:
            raise container.ContainerError("Error: {} cannot invcom {}".format(self.owner,item))
    def get_undestroyed(self):
        # Return all non-destroyed gears, including descendants.
        for g in self:
            if g.is_not_destroyed():
                yield g
                for p in g.sub_com.get_undestroyed():
                    yield p
                for p in g.inv_com.get_undestroyed():
                    yield p

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

    def descendants(self):
        for part in self.sub_com:
            yield part
            for p in part.descendants():
                yield p
        for part in self.inv_com:
            yield part
            for p in part.descendants():
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

    def calc_average_armor( self ):
        alist = list()
        for part in self.sub_com:
            armor = part.get_armor()
            if part:
                alist.append(armor.get_rating())
            else:
                alist.append(0)
        if len(alist) > 0:
            return sum(alist)//len(alist)
        else:
            return 0

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

    def __deepcopy__( self, memo ):
        # Regular deepcopy chokes on gears, so here's a custom deepcopy.
        # Go through the ancestors, see what attributes need passing to constructor.
        my_params = set()
        for ancestor in self.__class__.__mro__:
            if hasattr( ancestor, 'SAVE_PARAMETERS' ):
                my_params.update( ancestor.SAVE_PARAMETERS )

        # Copy the sub_com and inv_com
        dcsubcom = [copy.deepcopy(sc) for sc in self.sub_com]
        dcinvcom = [copy.deepcopy(sc) for sc in self.inv_com]

        # Go through this gear's dict, copying stuff 
        initdict = dict()
        afterdict = dict()
        for k,v in self.__dict__.items():
            if k in my_params:
                initdict[k] = copy.deepcopy(v)
            elif k not in ('sub_com','inv_com','container'):
                afterdict[k] = copy.deepcopy(v)

        initdict["sub_com"] = dcsubcom
        initdict["inv_com"] = dcinvcom

        newgear = type(self)(**initdict)
        newgear.__dict__.update(afterdict)
        memo[id(self)] = newgear

        return newgear


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
    def on_destruction( self, camp, anim_list ):
        my_root = self.get_root()
        my_invo = pbge.effects.Invocation(
            fx=geffects.DoDamage(2,self.size//200+2,anim=geffects.SuperBoom,scale=self.scale),
            area=pbge.scenes.targetarea.SelfCentered(radius=self.size//600+1,delay_from=-1) )
        my_invo.invoke(camp,None,[my_root.pos,],anim_list)



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
    def get_sensor_rating( self ):
        return self.size * self.scale.RANGE_FACTOR

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
    def get_thrust( self, move_mode ):
        if move_mode is geffects.Skimming:
            return (self.size*4000*self.current_health+self.max_health-1)//self.max_health
        elif move_mode is geffects.SpaceFlight:
            return (self.size*3700*self.current_health+self.max_health-1)//self.max_health
        elif move_mode is scenes.movement.Flying:
            return (self.size*500*self.current_health+self.max_health-1)//self.max_health
        else:
            return 0

class HeavyActuators( MovementSystem, StandardDamageHandler ):
    DEFAULT_NAME = "Heavy Actuators"
    MOVESYS_COST = 100
    @property
    def base_health(self):
        """Returns the unscaled maximum health of this gear."""
        return self.size
    def get_thrust( self, move_mode ):
        if move_mode is scenes.movement.Walking:
            return (self.size*1250*self.current_health+self.max_health-1)//self.max_health
        else:
            return 0


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
    SAVE_PARAMETERS = ('reach','damage','accuracy','penetration','integral','attack_stat','shot_anim','attributes')
    DEFAULT_SHOT_ANIM = None
    LEGAL_ATTRIBUTES = ()
    # Note that this class doesn't implement any MIN_*,MAX_* constants, so it
    # cannot be instantiated. Subclasses should do that.
    def __init__(self, reach=1, damage=1, accuracy=1, penetration=1, attack_stat=stats.Reflexes, shot_anim=None, attributes=(), **keywords ):
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

        self.attack_stat = attack_stat
        self.shot_anim = shot_anim or self.DEFAULT_SHOT_ANIM
        self.integral = keywords.pop( "integral" , False )
        self.attributes = list()
        for a in attributes:
            if a in self.LEGAL_ATTRIBUTES:
                self.attributes.append(a)

        # Finally, call the gear initializer.
        super(Weapon, self).__init__(**keywords)

    @property
    def base_mass(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.MASS_MODIFIER
        return int((( self.damage + self.penetration ) * 5 + self.accuracy + self.reach) * mult)

    @property
    def volume(self):
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.VOLUME_MODIFIER
        v = max(self.reach + self.accuracy + ( self.damage + self.penetration )/2,1)
        if self.integral:
            v -= 1
        return int(v*mult)

    @property
    def energy(self):
        return 1

    @property
    def base_cost(self):
        # Multiply the stats together, squaring damage and range because they're so important.
        mult = 1.0
        for aa in self.attributes:
            mult *= aa.COST_MODIFIER
        return int((self.COST_FACTOR * ( self.damage ** 2 ) * ( self.accuracy + 1 ) * ( self.penetration + 1 ) * (( self.reach**2 - self.reach )/2 + 1))*mult)

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

    def get_attack_skill(self):
        return self.scale.RANGED_SKILL

    def get_defenses( self ):
        return [geffects.DodgeRoll(),]

    def get_modifiers( self ):
        return [geffects.RangeModifier(self.reach),geffects.CoverModifier(),geffects.SpeedModifier(),geffects.SensorModifier(),geffects.OverwhelmModifier()]

    def get_basic_attack( self ):
        return pbge.effects.Invocation(
                name = 'Basic Attack', 
                fx=geffects.AttackRoll(
                    self.attack_stat, self.get_attack_skill(),
                    children = (geffects.DoDamage(self.damage,6,scale=self.scale),),
                    accuracy=self.accuracy*10, penetration=self.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers()
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=self.reach*3),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=self.shot_anim,
                data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),0),
                targets=1)

    def get_attacks( self, user ):
        # Return a list of invocations associated with this weapon.
        # Being a weapon, the invocations are likely to all be attacks.
        my_invos = list()
        my_invos.append(self.get_basic_attack())

        for aa in self.attributes:
            if hasattr(aa,'get_attacks'):
                my_invos += aa.get_attacks(self,user)

        return my_invos

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
    def get_attack_skill(self):
        return self.scale.MELEE_SKILL
    def get_modifiers( self ):
        return [geffects.CoverModifier(),geffects.SpeedModifier(),geffects.SensorModifier(),geffects.OverwhelmModifier()]
    def get_basic_attack( self ):
        return pbge.effects.Invocation(
                name = 'Basic Attack', 
                fx=geffects.AttackRoll(
                    self.attack_stat, self.get_attack_skill(),
                    children = (geffects.DoDamage(self.damage,6,scale=self.scale),),
                    accuracy=self.accuracy*10, penetration=self.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers()
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=self.reach),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=self.shot_anim,
                data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),0),
                targets=1)
    def get_weapon_desc( self ):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}'.format(self)

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
    def get_attack_skill(self):
        return self.scale.MELEE_SKILL
    def get_modifiers( self ):
        return [geffects.CoverModifier(),geffects.SpeedModifier(),geffects.SensorModifier(),geffects.OverwhelmModifier()]
    def get_basic_attack( self ):
        return pbge.effects.Invocation(
                name = 'Basic Attack', 
                fx=geffects.AttackRoll(
                    self.attack_stat, self.get_attack_skill(),
                    children = (geffects.DoDamage(self.damage,6,scale=self.scale),),
                    accuracy=self.accuracy*10, penetration=self.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers()
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=self.reach),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=self.shot_anim,
                data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),0),
                targets=1)
    def get_weapon_desc( self ):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}'.format(self)

class Ammo( BaseGear, Stackable, StandardDamageHandler ):
    DEFAULT_NAME = "Ammo"
    STACK_CRITERIA = ("ammo_type",)
    SAVE_PARAMETERS = ('ammo_type','quantity')
    def __init__(self, ammo_type=calibre.Shells_150mm, quantity=12, **keywords ):
        # Check the range of all parameters before applying.
        self.ammo_type = ammo_type
        self.quantity = max( quantity, 1 )
        self.spent = 0

        # Finally, call the gear initializer.
        super(Ammo, self).__init__(**keywords)
    @property
    def base_mass(self):
        return self.ammo_type.bang * (self.quantity-self.spent) //25
    @property
    def volume(self):
        return ( self.ammo_type.bang * self.quantity + 49 ) // 50

    @property
    def base_cost(self):
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
    SAVE_PARAMETERS = ('ammo_type',)
    DEFAULT_CALIBRE = calibre.Shells_150mm
    DEFAULT_SHOT_ANIM = geffects.BigBullet
    LEGAL_ATTRIBUTES = (attackattributes.Automatic,)
    def __init__(self, ammo_type=None, **keywords ):
        self.ammo_type = ammo_type or self.DEFAULT_CALIBRE

        # Finally, call the gear initializer.
        super(BallisticWeapon, self).__init__(**keywords)

    def is_legal_sub_com(self,part):
        if isinstance( part , Weapon ):
            return part.integral
        else:
            return isinstance( part, Ammo ) and part.ammo_type is self.ammo_type
    def get_ammo( self ):
        for maybe_ammo in self.sub_com:
            if isinstance(maybe_ammo,Ammo):
                return maybe_ammo
    def get_basic_attack( self, targets=1, name='Basic Attack', ammo_cost=1, attack_icon=0 ):
        return pbge.effects.Invocation(
                name = name, 
                fx=geffects.AttackRoll(
                    self.attack_stat, self.get_attack_skill(),
                    children = (geffects.DoDamage(self.damage,6,scale=self.scale),),
                    accuracy=self.accuracy*10, penetration=self.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers()
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=self.reach*3),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=self.shot_anim,
                data=geffects.AttackData(pbge.image.Image('sys_attackui_default.png',32,32),attack_icon),
                price=geffects.AmmoPrice(self.get_ammo(),ammo_cost),
                targets=targets)
    def get_weapon_desc( self ):
        ammo = self.get_ammo()
        it = 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}-{1}-{2}'.format(self,self.reach*2,self.reach*3)
        if ammo:
            it = it + '\n Ammo: {}/{}'.format(ammo.quantity-ammo.spent,ammo.quantity)
        else:
            it = it + '\n Ammo: 0'
        return it

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
    DEFAULT_SHOT_ANIM = geffects.GunBeam
    def get_weapon_desc( self ):
        return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}-{1}-{2}'.format(self,self.reach*2,self.reach*3)


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
        self.spent = 0

        # Finally, call the gear initializer.
        super(Missile, self).__init__(**keywords)

    @property
    def base_mass(self):
        return ((( self.damage + self.penetration ) * 5 + self.accuracy + self.reach ) * (self.quantity-self.spent) ) //25

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
    def get_ammo( self ):
        for maybe_ammo in self.sub_com:
            if isinstance(maybe_ammo,Missile):
                return maybe_ammo
    def is_operational( self ):
        """ To be operational, a launcher must be in an operational module.
        """
        mod = self.get_module()
        return self.is_not_destroyed() and mod and mod.is_operational()

    def get_defenses( self ):
        return [geffects.DodgeRoll(),]

    def get_modifiers( self, ammo ):
        return [geffects.RangeModifier(ammo.reach),geffects.CoverModifier(),geffects.SpeedModifier(),geffects.SensorModifier(),geffects.OverwhelmModifier()]

    def get_basic_attack( self ):
        ammo = self.get_ammo()
        if ammo:
            return pbge.effects.Invocation(
                name = 'Single Shot', 
                fx=geffects.AttackRoll(
                    stats.Perception, self.scale.RANGED_SKILL,
                    children = (geffects.DoDamage(ammo.damage,6,scale=ammo.scale),),
                    accuracy=ammo.accuracy*10, penetration=ammo.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers(ammo)
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=ammo.reach*3),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=geffects.Missile1,
                price=geffects.AmmoPrice(ammo,1),
                data=geffects.AttackData(pbge.image.Image('sys_attackui_missiles.png',32,32),0),
                targets=1)
    def get_multi_attack( self, num_missiles, frame ):
        ammo = self.get_ammo()
        if ammo:
            return pbge.effects.Invocation(
                name = 'Fire x{}'.format(num_missiles), 
                fx=geffects.MultiAttackRoll(
                    stats.Perception, self.scale.RANGED_SKILL,num_attacks=num_missiles,
                    children = (geffects.DoDamage(ammo.damage,6,scale=ammo.scale),),
                    accuracy=ammo.accuracy*10, penetration=ammo.penetration*10, 
                    defenses = self.get_defenses(),
                    modifiers = self.get_modifiers(ammo)
                    ),
                area=pbge.scenes.targetarea.SingleTarget(reach=ammo.reach*3),
                used_in_combat = True, used_in_exploration=False,
                shot_anim=geffects.MissileFactory(num_missiles),
                price=geffects.AmmoPrice(ammo,num_missiles),
                data=geffects.AttackData(pbge.image.Image('sys_attackui_missiles.png',32,32),frame),
                targets=1)
    def get_attacks( self, user ):
        # Return a list of invocations associated with this weapon.
        # Being a weapon, the invocations are likely to all be attacks.
        my_invos = list()
        ammo = self.get_ammo()
        if ammo:
            my_invos.append(self.get_basic_attack())
            last_n = int(ammo.quantity/4)
            if last_n > 1:
                my_invos.append(self.get_multi_attack(last_n,3))
            if last_n > 0 and int(ammo.quantity/2) > last_n:
                my_invos.append(self.get_multi_attack(int(ammo.quantity/2),6))
            if ammo.quantity > 1:
                my_invos.append(self.get_multi_attack(max(ammo.quantity-ammo.spent,2),9))
        return my_invos
    def get_weapon_desc( self ):
        ammo = self.get_ammo()
        if ammo:
            return 'Damage: {0.damage}\n Accuracy: {0.accuracy}\n Penetration: {0.penetration}\n Reach: {0.reach}-{1}-{2}\n Ammo: {3}/{0.quantity}'.format(ammo,ammo.reach*2,ammo.reach*3,ammo.quantity-ammo.spent)
        else:
            return 'Empty'


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

class Torso( Module ):
    def __init__(self, **keywords ):
        keywords[ "form" ] = MF_Torso
        super(Torso, self).__init__(**keywords)

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
    @classmethod
    def modify_speed( self, base_speed, move_mode ):
        # Return the modified speed.
        return base_speed


class Mecha(BaseGear,ContainerDamageHandler,Mover,WithPortrait):
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

    def free_pilots( self ):
        pilots = list()
        for m in self.sub_sub_coms():
            if isinstance(m,Cockpit):
                for pilot in list(m.sub_com):
                    if isinstance(m,Character):
                        m.sub_com.remove(pilot)
                        pilots.append(pilot)
        return pilots

    def get_engine_rating_and_gyro_status( self ):
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
        return engine_rating,has_gyro

    def calc_mobility( self ):
        """Calculate the mobility ranking of this mecha.
        """
        mass_factor = ( self.mass ** 2 ) // ( 10000 *  self.scale.SIZE_FACTOR ** 6 )
        engine_rating,has_gyro = self.get_engine_rating_and_gyro_status()
        # We now have the mass_factor, engine_rating, and has_gyro.
        it = engine_rating // mass_factor
        if not has_gyro:
            it -= 30
        return it


    def calc_walking( self ):
        norm_mass = self.scale.unscale_mass( self.mass )
        engine_rating,has_gyro = self.get_engine_rating_and_gyro_status()
        # In order to walk, a mecha needs both an engine and a gyroscope.
        if (engine_rating>0) and has_gyro:
            # If the number of legs is less than half plus one,
            # the mecha will fall over.
            total_legs,active_legs = self.count_modules(MF_Leg)
            if active_legs < ((total_legs//2)+1):
                return 0

            speed = (1125-norm_mass+engine_rating/5)//15

            # Depending on the mecha's mass, it needs a minimum number of
            # leg points to support it. If it has less than that number
            # then speed will be reduced.
            min_leg_points = norm_mass//50-2
            actual_leg_points = self.count_module_points(MF_Leg)
            if (actual_leg_points < min_leg_points):
                speed = (speed*actual_leg_points)/min_leg_points

            # Add thrust bonus.
            thrust = self.count_thrust_points(scenes.movement.Walking)
            if thrust > norm_mass:
                speed += thrust // norm_mass

            # Add form bonus.
            speed = self.form.modify_speed(speed,scenes.movement.Walking)

            # Don't drop below minimum speed.
            speed = max(speed,20)

            return speed
        else:
            return 0

    def calc_skimming( self ):
        engine_rating,has_gyro = self.get_engine_rating_and_gyro_status()
        # In order to skim, a mecha needs both an engine and a gyroscope.
        if (engine_rating>0) and has_gyro:
            return Mover.calc_skimming(self)
        else:
            return 0


    def get_stat( self, stat_id ):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_stat( stat_id )
        else:
            return 0

    def get_skill_score( self, stat_id, skill_id ):
        pilot = self.get_pilot()
        if pilot:
            return pilot.get_skill_score(stat_id,skill_id)
        else:
            return 0

    def get_dodge_score( self ):
        return self.get_skill_score( stats.Speed, stats.MechaPiloting )

    def get_sensor_range( self, map_scale ):
        it = 0
        for sens in self.sub_sub_coms():
            if hasattr(sens,'get_sensor_rating') and sens.is_operational():
                it = max((sens.get_sensor_rating()/map_scale.RANGE_FACTOR)*5+5,it)
        return it


class Character(BaseGear,StandardDamageHandler,Mover,WithPortrait):
    SAVE_PARAMETERS = ('name','form')
    DEFAULT_SCALE = scale.HumanScale
    DEFAULT_MATERIAL = materials.Meat
    def __init__(self, statline=None, personality=(), **keywords ):
        self.statline = collections.defaultdict(int)
        if statline:
            self.statline.update(statline)
        self.personality = set(personality)

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

    def get_stat( self, stat_id ):
        return self.statline.get( stat_id, 0 )

    def get_skill_score( self, stat_id, skill_id ):
        it = self.get_stat(skill_id) * 5
        if stat_id:
            it += self.get_stat(stat_id) * 2
        return it

    @property
    def base_health(self):
        """Returns the unscaled maximum health of this character."""
        return max(self.get_stat(stats.Body)+self.get_stat(stats.Vitality),6)

    def get_pilot( self ):
        """Return the character itself."""
        return self

    def calc_mobility( self ):
        """Calculate the mobility ranking of this character.
        """
        return self.get_stat( stats.Speed ) * 4

    def get_dodge_score( self ):
        return self.get_skill_score( stats.Speed, stats.Dodge )

    MIN_WALK_SPEED = 20
    def calc_walking( self ):
        speed = self.get_stat(stats.Speed) * 5

        # If the number of legs is less than half plus one,
        # the character can only crawl.
        total_legs,active_legs = self.count_modules(MF_Leg)
        if active_legs < ((total_legs//2)+1):
            speed = self.MIN_WALK_SPEED
        elif active_legs < total_legs:
            speed = max((speed*active_legs )//total_legs, self.MIN_WALK_SPEED)

        return speed

    def get_sensor_range( self, map_scale ):
        return self.get_stat(stats.Perception) * self.scale.RANGE_FACTOR / map_scale.RANGE_FACTOR

