# Base invocation gear.

# Strict duck typing in effect!
# Make private methods private. An invocation/effect doesn't need to subclass
# these, as long as they have the right public methods.

# price = An object with the following methods.
#   pay(chara): Pay the price
#   can_pay(chara): The character is capable of paying the price

class Invocation( object ):
    """ An invocation describes an effect that may be invoked by a character.
        Or not by a character. Try not to make too many assumptions."""
    def __init__( self, name=None, fx=None, area=None, used_in_combat=None, used_in_exploration=None, shot_anim=None, ai_tar=None, targets=1, price=None, data=None ):
        self.name=name
        self.fx = fx
        self.area = area
        self.used_in_combat = used_in_combat
        self.used_in_exploration = used_in_exploration
        self.ai_tar = ai_tar
        self.shot_anim = shot_anim
        self.targets = targets
        self.price = list()
        if price:
            self.price += price
        self.data = data    # Game-specific info attached to an invocation,
                # such as button images and whatnot.

    def can_be_invoked( self, chara, in_combat=False ):
        if self.price and not all(p.can_pay(chara) for p in self.price):
            return False
        elif in_combat:
            return self.used_in_combat and self.fx
        else:
            return self.used_in_exploration and self.fx

    def __str__( self ):
        return self.name

    def invoke( self, camp, originator, target_points, anim_list, fx_record = None ):
        """ Invoke this effect using the provided target points. Animations
            will be stored in the provided list and displayed afterward.
            camp: The campaign.
            originator: The character using the effect. May be None.
            target_points: List of points targeted. May just be a list of
                           one point.
            anim_list: The list where these animations are going to be stored.
                       If this is a chain reaction effect (eg, engine explosion)
                       this may be the children of a previous effect; otherwise
                       it's probably the root anim list.

            This method will return an fx_record, which is a dict containing
            information about the results of any effects.
        """
        if not fx_record:
            fx_record = dict()
        n = 0
        for tp in target_points:
            if originator:
                origin = originator.pos
            else:
                origin = tp
            if self.shot_anim:
                opening_anim = self.shot_anim(start_pos=origin,end_pos=tp,delay=4*n+1)
                anim_list.append( opening_anim )
                anims = opening_anim.children
                n += 1
            else:
                anims = anim_list
            delay = 1
            area_of_effect = self.area.get_area(camp,origin,tp)
            delay_point = self.area.get_delay_point(origin,tp)
            for p in area_of_effect:
                if delay_point:
                    delay = camp.scene.distance( p, delay_point ) * 2 + 1
                self.fx( camp, fx_record, originator, p, anims, delay )

        for p in self.price:
            p.pay(originator)

        return fx_record



#  *******************
#  ***   EFFECTS   ***
#  *******************

class NoEffect( object ):
    """An effect that does nothing. Good for placing anims, superclass of the rest."""
    def __init__(self, children=(), anim=None ):
        if children:
            self.children = list(children)
        else:
            self.children = list()
        self.anim = anim

    def handle_effect( self, camp, fx_record, originator, pos, anims, delay=0 ):
        """Do whatever is required of effect; return list of child effects."""
        return self.children

    def __call__( self, camp, fx_record, originator, pos, anims, delay=0 ):
        o_anims = anims
        o_delay = delay
        if self.anim:
            this_anim = self.anim( pos = pos, delay=delay )
            anims.append( this_anim )
            # The children of this animob don't get delayed.
            anims = this_anim.children
            delay = 0

        # Send the original anim list and delay to next_fx, in case there are
        # additional anims to be added by the effect itself. "handle_effect" is
        # called after the automatic anim above so that any captions/etc get
        # drawn on top of the base anim.
        next_fx = self.handle_effect( camp, fx_record, originator, pos, o_anims, o_delay )
        for nfx in next_fx:
            anims = nfx( camp, fx_record, originator, pos, anims, delay )
        return anims

class InvokeEffect( NoEffect ):
    """ An effect that causes a given invocation to be invoked.
    """
    def __init__(self, invocation, **keywords):
        super().__init__(**keywords)
        self.invocation = invocation

    def handle_effect(self, camp, fx_record, originator, pos, anims, delay = 0):
        self.invocation.invoke(camp, originator, [pos], anims, fx_record)
        return super().handle_effect(camp, fx_record, originator, pos, anims, delay)

