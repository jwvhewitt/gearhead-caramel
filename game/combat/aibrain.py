import random
import pbge

class CrapAI( object ):
    def __init__( self, npc ):
        self.npc = npc
        self.target = None

    def select_target( self, camp ):
        # Choose a possible target.
        # For now, we're just choosing a random target.
        candidates = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar)]
        if candidates:
            return random.choice( candidates )

    def choose_attack( self, camp ):
        my_library = self.npc.get_attack_library()
        invos = list()
        for shelf in my_library:
            for i in shelf.invo_list:
                if i.can_be_invoked( self.npc, True ):
                    invos.append(i)
        return random.choice(invos)

    def move_to( self, camp, mynav, dest ):
        if self.npc.get_current_speed() > 10:
            camp.fight.move_model_to(self.npc,mynav,dest)
        else:
            # Can't move if you're immobilized. Just wait here.
            camp.fight.cstat[self.npc].spend_ap(1)

    def act( self, camp ):
        while camp.fight.still_fighting() and camp.fight.cstat[self.npc].action_points > 0:
            # If we don't have a target, pick a target.
            if not ( self.target and self.target.is_operational() ):
                self.target = self.select_target(camp)

            # Select an attack for that particular target.
            my_invo = self.choose_attack(camp)

            if my_invo:
                # Move to a better tile if appropriate.
                my_firing_points = pbge.scenes.pfov.AttackReach( camp.scene, self.target.pos[0], self.target.pos[1], my_invo.area.reach ).tiles

                if self.npc.pos not in my_firing_points:
                    mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,camp.fight.cstat[self.npc].action_points*self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
                    target_spaces = set(mynav.cost_to_tile.keys()) & my_firing_points
                    if target_spaces:
                        # Move to a firing position.
                        self.move_to(camp,mynav,random.choice(list(target_spaces)))
                    else:
                        # Can't move into position this round. Ummm...
                        self.move_to(camp,mynav,random.choice(mynav.cost_to_tile.keys()))
                else:
                    my_invo.invoke(camp, self.npc, [self.target.pos,], pbge.my_state.view.anim_list )
                    pbge.my_state.view.handle_anim_sequence()
                    camp.fight.cstat[self.npc].spend_ap(1)
            else:
                # Can't move into position this round. Ummm...
                mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,camp.fight.cstat[self.npc].action_points*self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
                self.move_to(camp,mynav,random.choice(mynav.cost_to_tile.keys()))


                

