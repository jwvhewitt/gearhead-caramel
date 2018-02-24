import random
import pbge

# Determine impulses
# Ask if each can be done
# Sort by intensity
# Do one of them

# Impulses:
# - Attack preferred target
# - Attack target of opportunity
# - Get behind cover

# Attack Patterns
#  Evasive Maneuvers: Move once, Attack once
#  Archer Type: Move towards cover, then attack; keep distance from enemy
#  Fighter Type: Attempt to enter close combat, attack as much as possible

#  *****************************
#  ***   TARGET  SELECTORS   ***
#  *****************************

class RandomTargeter( object ):
    # This targeter just picks a random target every time.
    def __init__(self,npc):
        self.npc = npc
    def get_target( self, camp ):
        candidates = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar)]
        if candidates:
            return random.choice( candidates )


#  **********************
#  ***   AI  OBJECT   ***
#  **********************

class BasicAI( object ):
    def __init__( self, npc ):
        self.npc = npc
        self.target = None

    def select_target( self, camp ):
        # Choose a possible target.
        # For now, we're just choosing a random target.
        candidates = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar)]
        if candidates:
            return random.choice( candidates )

    def move_to( self, camp, mynav, dest ):
        if self.npc.get_current_speed() > 10:
            camp.fight.move_model_to(self.npc,mynav,dest)
        else:
            # Can't move if you're immobilized. Just wait here.
            camp.fight.cstat[self.npc].spend_ap(1)
    def get_min_mid_max_range( self, my_library ):
        dist = list()
        for shelf in my_library:
            for i in shelf.invo_list:
                if i.can_be_invoked(self.npc,True):
                    dist += [i.area.get_reach(),]*i.data.thrill_power
        if dist:
            average = sum(dist)//len(dist)
            if average >= 15:
                return (average//3,(average*2)//3,max(dist))
            else:
                return (0,average//2,max(dist))
        else:
            return (0,0,0)

    def calc_tile_desirability( self, camp, tilepos, minrange, midrange, maxrange, target, enemies ):
        # Calculate the desirability of this tile.
        # The ideal tile will be between minrange and maxrange, will
        # have advantageous LOS to the preferred target, and be shielded
        # from other targets.
        dist = camp.scene.distance(tilepos,target.pos)
        if dist > maxrange:
            return 0
        tiles = pbge.scenes.pfov.PointOfView( camp.scene, target.pos[0], target.pos[1], maxrange ).tiles
        if tilepos not in tiles:
            return 0
        points = 80
        # Check to see if this tile has a cover advantage.
        cover_diff = camp.scene.get_cover(target.pos[0],target.pos[1],tilepos[0],tilepos[1]) - camp.scene.get_cover(tilepos[0],tilepos[1],target.pos[0],target.pos[1])
        points += min(max(cover_diff,-50),50)
        # Advantage if close to minrange; disadvantage if below minrange or above midrange
        if dist >= minrange and dist <= midrange:
            points += (midrange - dist) * 2
        elif dist < minrange:
            points -= (minrange-dist)*15
        elif dist > midrange:
            points -= (dist - midrange)*4
        for e in enemies:
            if e is not self.target:
                dist = camp.scene.distance(tilepos,e.pos)
                if e.pos not in tiles:
                    points += 5
                elif dist < minrange:
                    points -= (minrange-dist)*10
        return max(points,1)
    def _desirability( self, pos ):
        # Fill out all the self.* vars before calling this function.
        return self.calc_tile_desirability(self.camp,pos,
            self.minr,self.midr,self.maxr,self.target,self.enemies)

    def choose_invocation_by_odds(self,camp,candidate_invocations,target):
        candidates = list()
        for invo in candidate_invocations:
            if hasattr(invo.fx,"get_odds"):
                odds,modz = invo.fx.get_odds(camp,self.npc,target)
                candidates += [invo,] * max(int((odds-0.25)*25),1)
            else:
                candidates += [invo,]
        return random.choice(candidates)
    def aim_attack(self,camp,myattacks):
        # Attempt to attack self.target. Return an invocation and a list
        # of target tiles.
        candidates = list()
        for shelf in myattacks:
            for invo in shelf.invo_list:
                if invo.can_be_invoked(self.npc,True) and self.target.pos in invo.area.get_targets(camp,self.npc.pos):
                    candidates.append(invo)
        if candidates:
            # Great! Just pick one at random and fire away.
            #invo = random.choice( candidates )
            invo = self.choose_invocation_by_odds(camp,candidates,self.target)
            targets = [self.target.pos]
            if invo.targets > 1:
                los = invo.area.get_targets(camp,self.npc.pos)
                possible_targets = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar) and tar.pos in los]
                for t in range(invo.targets-1):
                    targets.append(random.choice(possible_targets).pos)
            return invo, targets
        else:
            # Crud. See if we can attack anyone else, then.
            invo_x_targets = dict()
            for shelf in myattacks:
                if invo.can_be_invoked(self.npc,True):
                    possible_targets = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar) and tar.pos in invo.area.get_targets(camp,self.npc.pos)]
                    if possible_targets:
                        invo_x_targets[invo] = possible_targets
            if invo_x_targets:
                # Because we can attack someone but not our preferred
                # target, maybe we should pick a new preferred target.
                if random.randint(1,3) != 1:
                    self.target = None
                invo,possible_targets = random.choice(invo_x_targets.items())
                targets = list()
                for t in range(invo.targets):
                    targets.append(random.choice(possible_targets).pos)
                return invo, targets
            else:
                return None,None

    def act( self, camp ):
        # 1. Do I want to move?
        #    - Check to see if there's a better firing position within 1AP
        #    - Check to see if enemies are too close if minimum comfort range
        # 2. Attempt to attack
        #    - Preferred target is usually closest enemy within LOS
        #    - If can't hit preferred target, see if anyone else is in range
        #    - If no attacks possible, move closer
        if hasattr(self.npc,"get_current_speed") and self.npc.get_current_speed > 10:
            # Check for a better tile.
            mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
            sample = random.sample(mynav.cost_to_tile.keys(),max(len(mynav.cost_to_tile)//4,min(5,len(mynav.cost_to_tile))))
            #sample = sample[:len(sample)//4]
            self.camp = camp
            self.minr,self.midr,self.maxr = self.get_min_mid_max_range(self.npc.get_attack_library())
            if not ( self.target and self.target.is_operational() ):
                self.target = self.select_target(camp)
            if self.target and sample:
                self.enemies = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc,tar)]
                best = max(sample,key=self._desirability)
                if best is not self.npc.pos and self._desirability(best) > self._desirability(self.npc.pos):
                    self.move_to(camp,mynav,best)

        # We are now either in a good position, or so far out of the loop it isn't funny.
        while camp.fight.still_fighting() and camp.fight.cstat[self.npc].action_points > 0:
            # If we don't have a target, pick a target.
            if not ( self.target and self.target.is_operational() ):
                self.target = self.select_target(camp)
                
            my_attacks = self.npc.get_attack_library()
            
            # Attempt to attack the target, or failing that anyone
            # within range.
            my_invo,my_targets = self.aim_attack(camp,my_attacks)
            if my_invo:
                my_invo.invoke(camp, self.npc, my_targets, pbge.my_state.view.anim_list )
                pbge.my_state.view.handle_anim_sequence()
                camp.fight.cstat[self.npc].spend_ap(1)
            elif hasattr(self.npc,"get_current_speed") and self.npc.get_current_speed > 10:
                # Attempt to move closer to the target.
                mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
                mypath = pbge.scenes.pathfinding.AStarPath(camp.scene,self.npc.pos,self.target.pos,self.npc.mmode,camp.scene.get_blocked_tiles()).get_path(self.target.pos)
                mypath.reverse()
                dest = None
                for p in mypath:
                    if p in mynav.cost_to_tile:
                        dest = p
                        break
                if dest:
                    self.move_to(camp,mynav,dest)
                else:
                    # Can't move towards this target.
                    # Sit around and consider how you've reached this point in life.
                    self.target = None
                    camp.fight.cstat[self.npc].spend_ap(1)                    
            else:
                # Can't move, can't attack. Might as well do nothing.
                camp.fight.cstat[self.npc].spend_ap(1)
            

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

                if self.npc.pos not in my_firing_points and hasattr(self.npc,"get_current_speed"):
                    mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,camp.fight.cstat[self.npc].action_points*self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
                    target_spaces = set(mynav.cost_to_tile.keys()) & my_firing_points
                    if target_spaces:
                        # Move to a firing position.
                        self.move_to(camp,mynav,random.choice(list(target_spaces)))
                    else:
                        # Can't move into position this round. Ummm...
                        self.move_to(camp,mynav,random.choice(mynav.cost_to_tile.keys()))
                elif self.npc.pos in my_firing_points:
                    my_invo.invoke(camp, self.npc, [self.target.pos,], pbge.my_state.view.anim_list )
                    pbge.my_state.view.handle_anim_sequence()
                    camp.fight.cstat[self.npc].spend_ap(1)
                else:
                    camp.fight.cstat[self.npc].spend_ap(1)
            elif hasattr(self.npc,"get_current_speed"):
                # Can't move into position this round. Ummm...
                mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene,self.npc.pos,camp.fight.cstat[self.npc].action_points*self.npc.get_current_speed()+camp.fight.cstat[self.npc].mp_remaining,self.npc.mmode,camp.scene.get_blocked_tiles())
                self.move_to(camp,mynav,random.choice(mynav.cost_to_tile.keys()))
            else:
                camp.fight.cstat[self.npc].spend_ap(1)


                

