# Combat Actions:
# - Move
# - Attack
# - Skill (including talents, talking, etc)
# - EW Attack
# - Cover (overwatch)
# - Use usable gear
# - Access inventory

import pbge
from pbge import scenes
import collections
import pygame
from . import movementui
from . import targetingui
from . import programsui
from . import aibrain
from . import aihaywire
import random
import gears
from .. import configedit,invoker


ALT_AIS = {
    "HaywireAI": aihaywire.HaywireTurn
}


class CombatStat( object ):
    """Keep track of some stats that only matter during combat."""
    def __init__( self ):
        self.action_points = 0
        self.aoo_readied = False
        self.attacks_this_round = 0
        self.moves_this_round = 0
        self.mp_remaining = 0
        self.has_started_turn = False
        self.last_weapon_used = None
        self.last_program_used = None
    def can_act( self ):
        return self.action_points > 0
    def spend_ap( self, ap, mp_remaining=0 ):
        self.action_points -= ap
        self.mp_remaining = mp_remaining
    def start_turn( self, chara ):
        self.action_points += chara.get_action_points()
        self.has_started_turn = True
        self.moves_this_round = 0
        self.attacks_this_round = 0


class PlayerTurn( object ):
    # It's the player's turn. Allow the player to control this PC.
    def __init__( self, pc, camp ):
        self.pc = pc
        self.camp = camp

    def end_turn( self, button, ev ):
        self.camp.fight.cstat[self.pc].action_points = 0
        self.camp.fight.cstat[self.pc].mp_remaining = 0

    def switch_movement( self, button=None, ev=None ):
        if self.active_ui != self.movement_ui:
            self.active_ui.deactivate()
            self.movement_ui.activate()
            self.active_ui = self.movement_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_attack( self, button=None, ev=None ):
        if self.active_ui != self.attack_ui and self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_attack_library():
            self.active_ui.deactivate()
            self.attack_ui.activate()
            self.active_ui = self.attack_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[1])
        else:
            # If the attack UI can't be activated, switch back to movement UI.
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_skill( self, button=None, ev=None ):
        if self.active_ui != self.skill_ui and self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_skill_library(True):
            self.active_ui.deactivate()
            self.skill_ui.activate()
            self.active_ui = self.skill_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[2])
        else:
            # If the attack UI can't be activated, switch back to movement UI.
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_programs( self, button=None, ev=None ):
        if self.active_ui != self.program_ui and self.camp.fight.cstat[self.pc].action_points > 0 and self.pc.get_program_library():
            self.active_ui.deactivate()
            self.program_ui.activate()
            self.active_ui = self.program_ui
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[3])
        else:
            # If the attack UI can't be activated, switch back to movement UI.
            self.my_radio_buttons.activate_button(self.my_radio_buttons.buttons[0])

    def switch_top_shelf(self):
        if self.active_ui in self.top_shelf_funs:
            self.top_shelf_funs[self.active_ui]()

    def switch_bottom_shelf(self):
        if self.active_ui in self.bottom_shelf_funs:
            self.bottom_shelf_funs[self.active_ui]()

    def go( self ):
        # Perform this character's turn.
        #Start by making a hotmap centered on PC, to see how far can move.
        #hm = hotmaps.MoveMap( self.scene, chara )

        # How this is gonna work: There are several modes that can be switched
        #  between: movement, attack, use skill, etc. Each mode is gonna get
        #  a handler. The radio buttons widget determines what mode is current.
        #  Then, this routine routes the input to the correct UI handler.

        buttons_to_add = [(6,7,self.switch_movement,'Movement'),(2,3,self.switch_attack,'Attack'),]
        has_skills = self.pc.get_skill_library(True)
        if has_skills:
            buttons_to_add.append((8,9,self.switch_skill,'Skills'))
        has_programs = self.pc.get_program_library()
        if has_programs:
            buttons_to_add.append((10, 11, self.switch_programs, 'Programs'))
        buttons_to_add.append((4,5,self.end_turn,'End Turn'))
        self.my_radio_buttons = pbge.widgets.RadioButtonWidget( 8, 8, 220, 40,
         sprite=pbge.image.Image('sys_combat_mode_buttons.png',40,40),
         buttons=buttons_to_add,
         anchor=pbge.frects.ANCHOR_UPPERLEFT )
        pbge.my_state.widgets.append(self.my_radio_buttons)

        self.top_shelf_funs = dict()
        self.bottom_shelf_funs = dict()
        self.movement_ui = movementui.MovementUI( self.camp, self.pc,top_shelf_fun=self.switch_top_shelf,bottom_shelf_fun=self.switch_bottom_shelf )
        self.bottom_shelf_funs[self.movement_ui] = self.switch_attack
        self.attack_ui = targetingui.TargetingUI(self.camp,self.pc,top_shelf_fun=self.switch_top_shelf,bottom_shelf_fun=self.switch_bottom_shelf)
        self.top_shelf_funs[self.attack_ui] = self.switch_movement
        if has_skills:
            self.bottom_shelf_funs[self.attack_ui] = self.switch_skill
        elif has_programs:
            self.bottom_shelf_funs[self.attack_ui] = self.switch_programs
        #self.attack_ui.deactivate()
        self.skill_ui = invoker.InvocationUI(self.camp,self.pc,self._get_skill_library,top_shelf_fun=self.switch_top_shelf,bottom_shelf_fun=self.switch_bottom_shelf)
        self.top_shelf_funs[self.skill_ui] = self.switch_attack
        if has_programs:
            self.bottom_shelf_funs[self.skill_ui] = self.switch_programs
        self.program_ui = programsui.ProgramsUI(self.camp,self.pc,top_shelf_fun=self.switch_top_shelf,bottom_shelf_fun=self.switch_bottom_shelf)
        if has_skills:
            self.top_shelf_funs[self.program_ui] = self.switch_skill
        else:
            self.top_shelf_funs[self.program_ui] = self.switch_attack

        self.active_ui = self.movement_ui

        keep_going = True
        while self.camp.fight.still_fighting() and (self.pc in self.camp.scene.contents) and (self.camp.fight.cstat[self.pc].action_points > 0 or self.camp.fight.cstat[self.pc].mp_remaining > 0):
            # Get input and process it.
            gdi = pbge.wait_event()

            self.active_ui.update( gdi, self )

            if gdi.type == pygame.KEYDOWN:
                if gdi.unicode == "Q":
                    keep_going = False
                    self.camp.fight.no_quit = False
                elif gdi.unicode == "c":
                    pbge.my_state.view.focus( self.pc.pos[0], self.pc.pos[1] )
                elif gdi.key == pygame.K_ESCAPE:
                    mymenu = configedit.PopupGameMenu()
                    mymenu(self.camp.fight)


        pbge.my_state.widgets.remove(self.my_radio_buttons)
        pbge.my_state.view.overlays.clear()
        self.movement_ui.dispose()
        self.attack_ui.dispose()
        self.skill_ui.dispose()
        self.program_ui.dispose()

    def _get_skill_library(self):
        return self.pc.get_skill_library(True)


class Combat( object ):
    def __init__( self, camp: gears.GearHeadCampaign ):
        self.active = []
        self.scene = camp.scene
        self.camp = camp
        self.ap_spent = collections.defaultdict( int )
        self.cstat = collections.defaultdict( CombatStat )
        self.ai_brains = dict()
        self.no_quit = True
        self.n = 0

        if hasattr(camp.scene,"combat_music"):
            pbge.my_state.start_music(camp.scene.combat_music)

    def roll_initiative( self ):
        # Sort based on initiative roll.
        self.active.sort( key = self._get_npc_initiative, reverse=True )

    def _get_npc_initiative( self, chara ):
        return chara.get_stat(gears.stats.Speed) + random.randint(1,20)

    def activate_foe( self, foe ):
        # If the foe is already active, our work here is done.
        if foe in self.active:
            return

        foeteam = self.scene.local_teams.get(foe)
        team_frontier = [foeteam, self.scene.player_team]
        while team_frontier:
            myteam = team_frontier.pop()
            self.camp.check_trigger('ACTIVATETEAM', myteam)
            activation_area = set()
            # Add team members
            for m in self.scene.contents:
                if m not in self.active and self.scene.local_teams.get(m) is myteam and isinstance(m,gears.base.Combatant):
                    self.active.append(m)
                    self.camp.check_trigger('ACTIVATE', m)
                    myview = scenes.pfov.PointOfView(self.scene, m.pos[0], m.pos[1], 5)
                    activation_area.update(myview.tiles)

            # Check for further activations
            for m in self.scene.contents:
                if m not in self.active and m.pos in activation_area:
                    ateam = self.scene.local_teams.get(m)
                    if ateam and ateam not in team_frontier:
                        team_frontier.append(ateam)

        self.roll_initiative()

    def num_enemies( self ):
        """Return the number of active, hostile characters."""
        n = 0
        for m in self.active:
            if m in self.scene.contents and self.scene.is_an_actor(m) and m.is_operational() and self.scene.player_team.is_enemy( self.scene.local_teams.get(m) ):
                n += 1
        return n

    def still_fighting( self ):
        """Keep playing as long as there are enemies, players, and no quit."""
        return self.num_enemies() and self.camp.first_active_pc() and self.no_quit and self.camp.scene is self.scene and not pbge.my_state.got_quit and not self.camp.destination

    def step( self, chara, dest ):
        """Move chara according to hmap, return True if movement ended."""
        # See if the movement starts in a threatened area- may be attacked if it ends
        # in a threatened area as well.
        #threat_area = self.get_threatened_area( chara )
        #started_in_threat = chara.pos in threat_area
        chara.move(dest,pbge.my_state.view,0.25)
        pbge.my_state.view.handle_anim_sequence()
        self.cstat[chara].moves_this_round += 1

    def ap_needed( self, mover, nav, dest ):
        # Return how many action points are needed to move to this destination.
        mp_needed = nav.cost_to_tile[dest]-self.cstat[mover].mp_remaining
        if mp_needed < 1:
            return 0
        else:
            return (mp_needed-1)//max(mover.get_current_speed(),1) + 1


    def move_model_to( self, chara, nav, dest ):
        # Move the model along the path. Handle attacks of opportunity and wotnot.
        # Return the tile where movement ends.
        is_player_model = chara in self.camp.party
        path = nav.get_path(dest)[1:]
        for p in path:
            self.step( chara, p )
            if is_player_model:
                self.scene.update_party_position(self.camp)

        # Spend the action points.
        ap = self.ap_needed(chara,nav,chara.pos)
        mp_left = self.cstat[chara].mp_remaining + ap * chara.get_current_speed() - nav.cost_to_tile[chara.pos]
        self.cstat[chara].spend_ap(ap,mp_left)

        # Return the actual end point, which may be different from that requested.
        return chara.pos

    def get_action_nav(self,pc):
        # Return the navigation guide for this character taking into account that you can make
        # half a move while invoking an action.
        if hasattr(pc,'get_current_speed'):
            return pbge.scenes.pathfinding.NavigationGuide(self.camp.scene,pc.pos,(self.cstat[pc].action_points-1)*pc.get_current_speed()+pc.get_current_speed()//2+self.cstat[pc].mp_remaining,pc.mmode,self.camp.scene.get_blocked_tiles())

    def can_move_and_invoke( self, chara, nav, invo, target_pos ):
        if hasattr(invo.area,'MOVE_AND_FIRE') and not invo.area.MOVE_AND_FIRE:
            return False
        else:
            firing_points = invo.area.get_firing_points(self.camp, target_pos)
            if nav:
                return firing_points.intersection(list(nav.cost_to_tile.keys()))
            else:
                return set([chara.pos]).intersection(firing_points)

    def move_and_invoke(self,pc,nav,invo,target_list,firing_points,record=False):
        fp = min(firing_points, key=lambda r: nav.cost_to_tile.get(r, 10000))
        self.cstat[pc].mp_remaining += pc.get_current_speed() // 2
        self.move_model_to(pc, nav, fp)
        if pc.pos == fp:
            pbge.my_state.view.overlays.clear()
            # Launch the effect.
            invo.invoke(self.camp, pc, target_list, pbge.my_state.view.anim_list )
            pbge.my_state.view.handle_anim_sequence(record)
            self.cstat[pc].spend_ap(1)

        else:
            self.cstat[pc].spend_ap(1)

    def do_combat_turn( self, chara ):
        if not self.cstat[chara].has_started_turn:
            self.cstat[chara].start_turn(chara)
            if hasattr(chara,'ench_list'):
                chara.ench_list.update(self.camp,chara)
                alt_ais = chara.ench_list.get_tags('ALT_AI')
                if alt_ais:
                    current_ai = random.choice(alt_ais)
                    if current_ai in ALT_AIS:
                        ALT_AIS[current_ai](chara,self.camp)
        if chara in self.camp.party and chara.is_operational():
            # Outsource the turn-taking.
            my_turn = PlayerTurn( chara, self.camp )
            my_turn.go()
        elif chara.is_operational():
            if chara not in self.ai_brains:
                chara_ai = aibrain.BasicAI(chara)
                self.ai_brains[chara] = chara_ai
            else:
                chara_ai = self.ai_brains[chara]
            chara_ai.act(self.camp)

    def end_round( self ):
        for chara in self.active:
            self.cstat[chara].has_started_turn = False

    def go( self, explo ):
        """Perform this combat."""
        pbge.my_state.view.overlays.clear()

        while self.still_fighting():
            if self.n >= len( self.active ):
                # It's the end of the round.
                self.n = 0
                explo.update_npcs()
                self.end_round()
                self.camp.check_trigger("COMBATROUND")
            if self.active[self.n] in self.camp.scene.contents and self.active[self.n].is_operational():
                chara = self.active[self.n]
                self.do_combat_turn( chara )
                # After action, renew attacks of opportunity
                self.cstat[chara].aoo_readied = True
                self.cstat[chara].attacks_this_round = 0
                chara.renew_power()
            if self.no_quit and not pbge.my_state.got_quit:
                # Only advance to the next character if we are not quitting. If we are quitting,
                # the game will be saved and the player will probably want any APs they have left.
                self.n += 1

        if self.no_quit and not pbge.my_state.got_quit:
            # Combat is over. Deal with things.
            #explo.check_trigger( "COMBATOVER" )
            #if self.camp.num_pcs() > 0:
            #    # Combat has ended because we ran out of enemies. Dole experience.
            #    self.give_xp_and_treasure( explo )
            #    # Provide some end-of-combat first aid.
            #    #self.do_first_aid(explo)
            #    self.recover_fainted(explo)
            self.scene.tidy_enchantments(gears.enchantments.END_COMBAT)


