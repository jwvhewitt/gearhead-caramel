# Combat Actions:
# - Move
# - Attack
# - Skill (including talents, talking, etc)
# - EW Attack
# - Cover (overwatch)
# - Use usable gear
# - Access inventory

import pbge
import collections
import pygame


class CombatStat( object ):
    """Keep track of some stats that only matter during combat."""
    def __init__( self ):
        self.action_points = 0
        self.aoo_readied = False
        self.attacks_this_round = 0
    def can_act( self ):
        return self.action_points > 0



class PlayerTurn( object ):
    # It's the player's turn. Allow the player to control this PC.
    def __init__( self, pc, explo ):
        self.pc = pc
        self.explo = explo

    def go( self ):
        # Perform this character's turn.
        #Start by making a hotmap centered on PC, to see how far can move.
        #hm = hotmaps.MoveMap( self.scene, chara )

        # How this is gonna work: There are several modes that can be switched
        #  between: movement, attack, use skill, etc. Each mode is gonna get
        #  a handler. The radio buttons widget determines what mode is current.
        #  Then, this routine routes the input to the correct UI handler.

        my_radio_buttons = pbge.widgets.RadioButtonWidget( 8, 8, 220, 40,
         sprite=pbge.image.Image('sys_combat_mode_buttons.png',40,40),
         buttons=((0,1,None),(2,3,None),(0,1,None),(2,3,None),(4,5,None)),
         anchor=pbge.frects.ANCHOR_UPPERLEFT )

        keep_going = True
        while keep_going:
            # Get input and process it.
            gdi = pbge.wait_event()

            if gdi.type == pbge.TIMEREVENT:
                #explo.view.overlays.clear()
                #explo.view.overlays[ chara.pos ] = maps.OVERLAY_CURRENTCHARA
                #explo.view.overlays[ explo.view.mouse_tile ] = maps.OVERLAY_CURSOR
                self.explo.view()

                pbge.my_state.do_flip()

            else:
                if gdi.type == pygame.KEYDOWN:
                    if gdi.unicode == u"Q":
                        keep_going = False
                        self.explo.camp.fight.no_quit = False
                    elif gdi.unicode == u" ":
                        self.end_turn( chara )
                #elif gdi.type == pygame.MOUSEBUTTONUP:
                #    if gdi.button == 1:
                #        # Left mouse button.
                #        if ( explo.view.mouse_tile != chara.pos ) and self.scene.on_the_map( *explo.view.mouse_tile ):
                #            tacred.hmap = None
                #            target = explo.view.modelmap.get( explo.view.mouse_tile, None )
                #            if target and target.is_hostile( self.camp ):
                #                if chara.can_attack():
                #                    self.move_to_attack( explo, chara, target, tacred )
                #                else:
                #                    explo.alert( "You are out of ammunition!" )
                #            else:
                #                self.move_player_to_spot( explo, chara, explo.view.mouse_tile, tacred )
                #            tacred.hmap = hotmaps.MoveMap( self.scene, chara )
                #    else:
                #        self.pop_combat_menu( explo, chara )
        my_radio_buttons.remove()


class Combat( object ):
    def __init__( self, camp, foe_zero=None ):
        self.active = []
        self.scene = camp.scene
        self.camp = camp
        self.ap_spent = collections.defaultdict( int )
        self.cstat = collections.defaultdict( CombatStat )
        self.no_quit = True
        self.n = 0

        if foe_zero:
            self.activate_foe( foe_zero )

        # Sort based on initiative roll.
        #self.active.sort( key = characters.roll_initiative, reverse=True )

    def activate_foe( self, foe ):
        m0team = self.scene.local_teams.get(foe)
        for m in self.scene._contents:
            if m in self.camp.party:
                self.active.append( m )

    def still_fighting( self ):
        """Keep playing as long as there are enemies, players, and no quit."""
        return self.no_quit and not pbge.my_state.got_quit and not self.camp.destination

    def do_combat_turn( self, explo, chara ):
        if chara in self.camp.party:
            # Outsource the turn-taking.
            my_turn = PlayerTurn( chara, explo )
            my_turn.go()

    def go( self, explo ):
        """Perform this combat."""

        while self.still_fighting():
            if self.n >= len( self.active ):
                # It's the end of the round.
                self.n = 0
                #self.ap_spent.clear()
                #explo.update_monsters()
            if self.active[self.n].is_operational():
                chara = self.active[self.n]
                self.do_combat_turn( explo, chara )
                # After action, invoke enchantments and renew attacks of opportunity
                #explo.invoke_enchantments( chara )
                self.cstat[chara].aoo_readied = True
                self.cstat[chara].attacks_this_round = 0
            self.n += 1

        #if self.no_quit and not pygwrap.GOT_QUIT:
            # Combat is over. Deal with things.
            #explo.check_trigger( "COMBATOVER" )
            #if self.camp.num_pcs() > 0:
            #    # Combat has ended because we ran out of enemies. Dole experience.
            #    self.give_xp_and_treasure( explo )
            #    # Provide some end-of-combat first aid.
            #    #self.do_first_aid(explo)
            #    self.recover_fainted(explo)

        # PCs stop hiding when combat ends.
        #for pc in self.camp.party:
        #    pc.hidden = False
        #    pc.condition.tidy( enchantments.COMBAT )

        # Tidy up any combat enchantments.
        #for m in self.scene.contents[:]:
        #    if hasattr( m, "condition" ):
        #        m.condition.tidy( enchantments.COMBAT )
        #    if hasattr( m, "combat_only" ) and m.combat_only:
        #        self.scene.contents.remove( m )
        #    elif hasattr( m, "mitose" ) and hasattr( m, "hp_damage" ):
        #        # Slimes regenerate after battle, to prevent split/flee exploit.
        #        m.hp_damage = 0


