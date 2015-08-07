
class Damage( object ):
    def __init__( self, hp_damage, penetration ):
        self.hp_damage = hp_damage
        self.penetration = penetration

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


    def take_damage( self, target ):
        """Function name inherited from GH2.1; record_damage may be better"""
        # Check to see if the part is ok now
        # Record the damage done
        # If the part has been destroyed...
        #  * Moving up through part and its parents, set a trigger for each
        #    destroyed part.
        #  * Add this part to the list of destroyed stuff.

    def apply_damage( self, target ):
        """Function name inherited from GH2.1"""
        # First, make sure this part can be damaged.
        # Calculate overkill- damage above and beyond this part's capacity.
        # Call the take_damage function. What was I thinking?
        # Do special effects if this part is destroyed:
        # - Modules and cockpits do an ejection check
        # - Ammo can cause an explosion
        # - Engines can suffer a critical failure, aka big boom

    def real_damage_gear( self, target ):
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

    def inflict( self, target ):
        """This damage is being inflicted against a gear."""

        # Initialize history variables
        # Check on the master and the pilot- see if they're currently OK.
        # Determine the number of damage packets and the damage of each packet.
        # Start doling damage depending on whether this is burst or hyper.
        #   Call the real damage routine for each burst.
        # Dole out concussion and overkill damage.
        # A surrendered master that is damaged will un-surrender.
        # Check for engine explosions and crashing/falling here.
        # Give experience to vitality, if that's still a thing.






