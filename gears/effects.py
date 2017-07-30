# Base invocation gear.

class Invocation( object ):
    """ An invocation describes an effect that may be invoked by a character.
        In GearHead, this usually means an attack, but anything built by the
        effects system is invokable."""
    def __init__( self, name=None, fx=None, com_tar=None, exp_tar=None, shot_anim=None, ai_tar=None, targets=1, price=None ):
        self.name=name
        self.fx = fx
        self.com_tar = com_tar
        self.exp_tar = exp_tar
        self.ai_tar = ai_tar
        self.shot_anim = shot_anim
        self.targets = targets
        self.price = price

    def can_be_invoked( self, chara, in_combat=False ):
        if in_combat:
            return self.com_tar and self.fx
        else:
            return self.exp_tar and self.fx

    def pay_invocation_price( self, chara ):
        self.price( chara )

    def menu_str( self ):
        return self.name

    def __str__( self ):
        return self.name

#  *****************
#  ***   RULES   ***
#  *****************

# Area of Effect attack: Roll for target point deviation
#   Check for enemy defenses, like antimissile or ECM
# Basic attack roll, compare with target's defense roll
#   Target may get additional defenses: block, parry, ECM, antimissile
# Crashing mecha take additional damage plus action loss
# A destroyed fusion engine may explode

class EffectRequest( object ):

    def invoke_effect( self, effect, originator, area_of_effect, opening_anim = None, delay_point=None ):
        all_anims = list()
        if opening_anim:
            all_anims.append( opening_anim )
            anims = opening_anim.children
        else:
            anims = all_anims
        delay = 1
        for p in area_of_effect:
            if delay_point:
                delay = self.scene.distance( p, delay_point ) * 2 + 1
            effect( self.camp, originator, p, anims, delay )
        animobs.handle_anim_sequence( self.screen, self.view, all_anims, self.record_anim )
        self.record_anim = False

        # Remove dead models from the map, and handle probes and mitoses.
        for m in list(self.scene.contents):
            if hasattr( m, "probe_me" ) and m.probe_me:
                self.probe( m )
                m.probe_me = False
            if isinstance( m, characters.Character ) and not m.is_alright():
                self.check_trigger( "DEATH", m )
                if not m.is_alright():
                    # There may be a script keeping this model alive...
                    self.scene.contents.remove( m )
                    if m.is_dead():
                        # Drop all held items.
                        m.drop_everything( self.scene )
            elif hasattr( m, "mitose_me" ) and m.mitose_me:
                self.mitose( m )
                del( m.mitose_me )


#  *******************
#  ***   EFFECTS   ***
#  *******************

class NoEffect( object ):
    """An effect that does nothing. Good for placing anims, superclass of the rest."""
    def __init__(self, children=(), anim=None ):
        if not children:
            children = list()
        self.children = children
        self.anim = anim

    def handle_effect( self, camp, originator, pos, anims, delay=0 ):
        """Do whatever is required of effect; return list of child effects."""
        return self.children

    def __call__( self, camp, originator, pos, anims, delay=0 ):
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
        next_fx = self.handle_effect( camp, originator, pos, o_anims, o_delay )
        for nfx in next_fx:
            anims = nfx( camp, originator, pos, anims, delay )
        return anims

