import random
import gears

class Damage( object ):
    def __init__( self, hp_damage, penetration, target ):
        self.hp_damage = hp_damage
        self.penetration = penetration
        self.overkill = 0
        self.allocate_damage( target )

    def ejection_check( self, target ):
        # Record the pilot/mecha's team
        # Check if this is an honorable duel. If so, ejection almost guaranteed.
        # Search through the subcoms for characters.
        #  Each character must eject or die.
        #  Head mounted cockpits easier to eject from.
        #  Bad roll = character takes damage on eject, and may die.
        #  Terrible roll = character definitely dies.
        #  Remove the pilot and place offsides.
        # If any characters were found, set a "Number of Units" trigger. (Is this necessary? Why not do this at end of "inflict"?
        pass

    def take_damage( self, target ):
        """Function name inherited from GH2.1; record_damage may be better"""
        # Check to see if the part is ok now
        # Record the damage done
        # If the part has been destroyed...
        #  * Moving up through part and its parents, set a trigger for each
        #    destroyed part.
        #  * Add this part to the list of destroyed stuff.
        pass

    def apply_damage( self, target, dmg ):
        """Function name inherited from GH2.1"""
        # First, make sure this part can be damaged.
        # Calculate overkill- damage above and beyond this part's capacity.
        # Call the take_damage function. What was I thinking?
        # Do special effects if this part is destroyed:
        # - Modules and cockpits do an ejection check
        # - Ammo can cause an explosion
        # - Engines can suffer a critical failure, aka big boom
        dmg_capacity = target.max_health - target.hp_damage
        if dmg > dmg_capacity:
            self.overkill += dmg - dmg_capacity
            dmg = dmg_capacity
        target.hp_damage += dmg

    def _list_thwackable_subcoms( self, target ):
        """Return a list of subcomponents which may take damage."""
        thwackables = list()
        for p in target.sub_com:
            if p.is_not_destroyed():
                thwackables.append( p )
        return thwackables

    def real_damage_gear( self, target, dmg, penetration ):
        """Function name inherited from GH2.1"""
        # As long as we're not ignoring armor, check armor now.
        #    If this is the first dmg iteration and target isn't root, apply parent armor.
        #    Query the gear for its armor.
        #    Reduce damage by armor amount, armor suffers staged penetration.
        # If any damage left...
        #    Apply damage here, or split some to apply to subcoms.
        #    1/23 chance to pass all to a single subcom, or if this gear undamageable.
        #    1/3 chance to split half here, half to a functional subcom.
        #    Otherwise apply all damage here.
        armor = target.get_armor()
        if armor and armor.is_not_destroyed():
            # Reduce penetration by the armor's rating.
            tar = armor.get_rating()
            if tar:
                penetration -= tar
            # Armor that gets used gets damaged.
            dmg = armor.reduce_damage( dmg, self )

        if penetration > 0 and dmg > 0:
            # A damaging strike.
            potential_next_targets = self._list_thwackable_subcoms( target )
            if random.randint(1,23)==1 or not target.can_be_damaged():
                # Assign all damage to a single subcom.
                if potential_next_targets:
                    self.real_damage_gear(random.choice(potential_next_targets),dmg,penetration)
            elif random.randint(1,3)==3 and potential_next_targets and dmg > 2:
                # Half damage here, half damage to a subcom.
                dmg1,dmg2 = dmg//2,(dmg+1)//2
                self.apply_damage( target, dmg1 )
                self.real_damage_gear(random.choice(potential_next_targets),dmg2,penetration)
            else:
                # All damage to this part.
                self.apply_damage(target,dmg)

    def allocate_damage( self, target ):
        """This damage is being inflicted against a gear."""

        # X - Initialize history variables
        # X - Check on the master and the pilot- see if they're currently OK.

        # Determine the number of damage packets and the damage of each packet.
        # Since attack attributes haven't been invented yet, one packet.
        num_hits = 1
        the_hits = [self.hp_damage]

        # Start doling damage depending on whether this is burst or hyper.
        #   Call the real damage routine for each burst.
        for h in the_hits:
            self.real_damage_gear(target,h,self.penetration)

        # Dole out concussion and overkill damage.
        if self.overkill:
            torso = None
            for m in target.sub_com:
                if isinstance( m, gears.Torso ) and m.is_not_destroyed():
                    torso = m
            if torso:
                self.apply_damage( torso, self.overkill )

        # A surrendered master that is damaged will un-surrender.
        # Check for engine explosions and crashing/falling here.
        # Give experience to vitality, if that's still a thing.

class ShakaCannon( object ):
    damage = 4000
    accuracy = 0
    penetration = 30

class Smartgun( object ):
    damage = 4000
    accuracy = 30
    penetration = 0

class Railgun( object ):
    damage = 4000
    accuracy = 10
    penetration = 10

class GlassCow( object ):
    damage = 2000
    accuracy = 0
    penetration = 0

total = 0
def combat_test( mecha, weapon ):
    total = 0
    lowest = 999
    highest = 0
    for trial in range(1000):
        mecha.wipe_damage()

        t = 0
        while mecha.is_operational() and t < 1000:
            t += 1
            hitroll = random.randint(1,100)
            target = random.randint(1,100)
#            if hitroll + weapon.accuracy > target + mecha.calc_mobility():
#                Damage( weapon.damage, hitroll - target + weapon.penetration, mecha )
            Damage( weapon.damage, abs(hitroll - target) + weapon.penetration, mecha )
        if t < lowest:
            lowest = t
        if t > highest:
            highest = t 
        total += t
    print "On average, mecha destroyed in {} shots".format( total/1000.0 )
    print "    Fastest Destruction: {}".format(lowest)
    print "    Slowest Destruction: {}".format(highest)

