import random
import pbge
import gears
from . import actions
from game.content import ghcutscene


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

class RandomTargeter(object):
    # This targeter just picks a random target every time.
    def __init__(self, npc):
        self.npc = npc

    def get_target(self, camp, optrange):
        candidates = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc, tar)]
        if candidates:
            return random.choice(candidates)


class DefaultTargeter(object):
    def __init__(self, npc):
        self.npc = npc

    def closest_target_selector(self, camp, target):
        return -camp.scene.distance(self.npc.pos, target.pos)

    def most_damaged_target_selector(self, camp, target):
        return target.get_percent_damage_over_health()

    def easiest_target_selector(self, camp, target):
        myat = self.npc.get_primary_attack()
        if myat:
            myinvo = myat.get_first_working_invo(self.npc)
            if myinvo and hasattr(myinvo.fx, "get_odds"):
                return myinvo.fx.get_odds(camp, self.npc, self.npc.pos, target)
        return -1

    def strongest_target_selector(self, camp, target):
        return target.cost

    def get_target(self, camp, optrange):
        candidates = [tar for tar in camp.scene.get_operational_actors() if
                      camp.scene.are_hostile(self.npc, tar) and not tar.hidden]
        best_candidates = [tar for tar in candidates if camp.scene.distance(self.npc.pos, tar.pos) <= optrange]
        if best_candidates:
            return max(best_candidates, key=lambda a: [
                self.closest_target_selector(camp, a),
                self.easiest_target_selector(camp, a),
                self.most_damaged_target_selector(camp, a),
            ])
        elif candidates:
            return max(candidates, key=lambda a: [
                self.strongest_target_selector(camp, a),
                self.closest_target_selector(camp, a)
            ])
            # return random.choice( candidates )


class MonsterTargeter(DefaultTargeter):
    def get_target(self, camp, optrange):
        candidates = [tar for tar in camp.scene.get_operational_actors() if
                      camp.scene.are_hostile(self.npc, tar) and not tar.hidden]
        best_candidates = [tar for tar in candidates if camp.scene.distance(self.npc.pos, tar.pos) <= optrange]
        if best_candidates:
            return max(best_candidates, key=lambda a: [
                self.closest_target_selector(camp, a) + random.randint(1, 4),
                self.easiest_target_selector(camp, a),
            ])
        elif candidates:
            return max(candidates, key=lambda a: [
                self.closest_target_selector(camp, a) + random.randint(1, 6),
                self.strongest_target_selector(camp, a),
            ])
            # return random.choice( candidates )


#  **********************
#  ***   AI  OBJECT   ***
#  **********************

class BasicAI(object):
    def __init__(self, npc):
        self.npc = npc
        self.target = None
        self.minr, self.midr, self.maxr = 0,0,0
        self.enemies = list()

        # If the NPC is going to use a skill or skills, it will be at the start
        # of their turn.
        self.tried_skills = False
        self.moved_to_firing_position = False
        if isinstance(npc, gears.base.Monster):
            self.targeter = MonsterTargeter(npc)
        else:
            self.targeter = DefaultTargeter(npc)

    def move_to(self, camp, mynav, dest):
        if self.npc.get_current_speed() > 10:
            camp.fight.move_model_to(self.npc, mynav, dest)
        else:
            # Can't move if you're immobilized. Just wait here.
            camp.fight.cstat[self.npc].spend_ap(1)

    def get_min_mid_max_range(self):
        myat = self.npc.get_primary_attack()
        if myat:
            dist = myat.get_first_working_invo(self.npc).area.get_reach()
            if dist >= 10:
                return (dist // 3, (dist * 2) // 3, dist)
            else:
                return (0, dist // 2, dist)
        else:
            return (0, 0, 0)

    def calc_tile_desirability(self, camp, tilepos, minrange, midrange, maxrange, target, enemies):
        # Calculate the desirability of this tile.
        # The ideal tile will be between minrange and maxrange, will
        # have advantageous LOS to the preferred target, and be shielded
        # from other targets.
        dist = camp.scene.distance(tilepos, target.pos)
        if dist > maxrange:
            return 0
        tiles = pbge.scenes.pfov.PointOfView(camp.scene, target.pos[0], target.pos[1], maxrange).tiles
        if tilepos not in tiles:
            return 0
        points = 80
        # Check to see if this tile has a cover advantage.
        cover_diff = camp.scene.get_cover(target.pos[0], target.pos[1], tilepos[0], tilepos[1]) - camp.scene.get_cover(
            tilepos[0], tilepos[1], target.pos[0], target.pos[1])
        points += min(max(cover_diff, -50), 50)
        # Advantage if close to minrange; disadvantage if below minrange or above midrange
        if minrange <= dist <= midrange:
            points += (midrange - dist) * 2
        elif dist < minrange:
            points -= (minrange - dist) * 15
        elif dist > midrange:
            points -= (dist - midrange) * 4
        for e in enemies:
            if e is not self.target:
                dist = camp.scene.distance(tilepos, e.pos)
                if e.pos not in tiles:
                    points += 5
                elif dist < minrange:
                    points -= (minrange - dist) * 10
        return max(points, 1)

    def _desirability(self, pos):
        # Fill out all the self.* raw_vars before calling this function.
        return self.calc_tile_desirability(self.camp, pos,
                                           self.minr, self.midr, self.maxr, self.target, self.enemies)

    def choose_invocation_by_odds(self, camp, candidate_invocations, target):
        candidates = list()
        for invo in candidate_invocations:
            if hasattr(invo.fx, "get_odds"):
                odds, modz = invo.fx.get_odds(camp, self.npc, self.npc.pos, target)
                candidates += [invo, ] * min(max(int((odds - 0.25) * 25), 1), 25)
            else:
                candidates += [invo, ]
        return random.choice(candidates)

    def aim_attack(self, camp, myattacks):
        # Attempt to attack self.target. Return an invocation and a list
        # of target tiles.
        candidates = list()
        for shelf in myattacks:
            for invo in shelf.invo_list:
                if invo.can_be_invoked(self.npc, True) and self.target.pos in invo.area.get_targets(camp, self.npc.pos):
                    candidates.append(invo)
        if candidates:
            # Great! Just pick one at random and fire away.
            # invo = random.choice( candidates )
            invo = self.choose_invocation_by_odds(camp, candidates, self.target)
            targets = [self.target.pos]
            if invo.targets > 1:
                los = invo.area.get_targets(camp, self.npc.pos)
                possible_targets = [tar for tar in camp.scene.get_operational_actors() if
                                    camp.scene.are_hostile(self.npc, tar) and tar.pos in los]
                for t in range(invo.targets - 1):
                    targets.append(random.choice(possible_targets).pos)
            return invo, targets
        else:
            # Crud. See if we can attack anyone else, then.
            invo_x_targets = dict()
            for shelf in myattacks:
                if invo.can_be_invoked(self.npc, True):
                    possible_targets = [tar for tar in camp.scene.get_operational_actors() if
                                        camp.scene.are_hostile(self.npc, tar) and tar.pos in invo.area.get_targets(camp,
                                                                                                                   self.npc.pos) and not tar.hidden]
                    if possible_targets:
                        invo_x_targets[invo] = possible_targets
            if invo_x_targets:
                # Because we can attack someone but not our preferred
                # target, maybe we should pick a new preferred target.
                if random.randint(1, 3) != 1:
                    self.target = None
                invo, possible_targets = random.choice(list(invo_x_targets.items()))
                targets = list()
                for t in range(invo.targets):
                    targets.append(random.choice(possible_targets).pos)
                return invo, targets
            else:
                return None, None

    def attempt_move_to_better_position(self, camp):
        if camp.fight.cstat[self.npc].mp_remaining > 5:
            # Check for a better tile.
            mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene, self.npc.pos,
                                                            camp.fight.cstat[self.npc].mp_remaining, self.npc.mmode,
                                                            camp.scene.get_blocked_tiles())
            sample = random.sample(list(mynav.cost_to_tile.keys()),
                                   max(len(mynav.cost_to_tile) // 2, min(5, len(mynav.cost_to_tile))))
            # sample = sample[:len(sample)//4]
            self.camp = camp
            if self.target and sample:
                best = max(sample, key=self._desirability)
                if best is not self.npc.pos and self._desirability(best) > self._desirability(self.npc.pos):
                    return actions.MoveModelToPos(self.camp, self.npc, mynav, best)

    def attempt_jump_to_better_position(self, camp):
        # Check for a better tile.
        jump_points = list(actions.get_jump_points(camp, self.npc))
        sample = random.sample(jump_points, max(len(jump_points) // 3, min(10, len(jump_points))))
        self.camp = camp
        self.minr, self.midr, self.maxr = self.get_min_mid_max_range()
        if self.target and sample:
            best = max(sample, key=self._desirability)
            if best is not self.npc.pos and self._desirability(best) > self._desirability(self.npc.pos):
                return actions.JumpModelToPos(self.camp, self.npc, best)

    def attempt_attack(self, camp):
        # Check all of this model's attacks.
        # - Can I move+attack my preferred target? Stick that in "premium" attacks.
        # - Can I move+attack a secondary target? Stick that in "backup" attacks.
        # If a premium or backup attack exists, choose the best one by this NPC's weighting function
        # Choose the tile to move to based on tile desirability
        # Attack if possible, which is should be, since we handled those calculations up there

        my_actions = list()

        # We are now either in a good position, or so far out of the loop it isn't funny.
        if camp.fight.cstat[self.npc].can_act():
            my_attacks = self.npc.get_attack_library()

            # Attempt to attack the target, or failing that anyone
            # within range.
            my_invo, my_targets = self.aim_attack(camp, my_attacks)
            if my_invo:
                return [actions.InvokeInvocation(camp, my_invo, self.npc.pos, self.npc, my_targets, None),]
            elif hasattr(self.npc, "get_current_speed") and self.npc.get_current_speed() > 10:
                # Attempt to move closer to the target.
                mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene, self.npc.pos,
                                                                camp.fight.cstat[self.npc].mp_remaining,
                                                                self.npc.mmode, camp.scene.get_blocked_tiles())
                mypath = pbge.scenes.pathfinding.AStarPath(camp.scene, self.npc.pos, self.target.pos, self.npc.mmode,
                                                           camp.scene.get_blocked_tiles()).get_path(self.target.pos)
                mypath.reverse()
                dest = None
                for p in mypath:
                    if p in mynav.cost_to_tile:
                        dest = p
                        break
                if dest and dest != self.npc.pos:
                    return [actions.MoveModelToPos(camp, self.npc, mynav, dest),]
                    
        return my_actions

    def try_to_use_a_skill(self, camp):
        # Check to see if any skills are usable.
        # Return the actions to perform if appropriate.
        my_skills = list()
        my_targets = dict()
        my_nav = camp.fight.get_action_nav(self.npc)
        my_library = self.npc.get_skill_library(True)
        pilot = self.npc.get_pilot()
        if gears.stats.Computers in pilot.statline or random.randint(1, 5) == 1:
            my_library += self.npc.get_program_library(True)
        for shelf in my_library:
            for invo in shelf.invo_list:
                if invo.can_be_invoked(self.npc, True) and invo.ai_tar and invo.ai_tar.get_impulse(invo, camp,
                                                                                                   self.npc) > 0:
                    potar = [tar for tar in invo.ai_tar.get_potential_targets(invo, camp, self.npc) if
                             camp.fight.can_move_and_invoke(self.npc, my_nav, invo, tar.pos)]
                    if potar:
                        my_skills += [invo, ] * invo.ai_tar.get_impulse(invo, camp, self.npc)
                        my_targets[invo] = potar
        if my_skills:
            my_actions = list()
            invo = random.choice(my_skills)
            tar = random.choice(my_targets[invo])
            legal_targets = invo.area.get_targets(camp, self.npc.pos)
            if tar.pos not in legal_targets:
                firing_pos = random.choice(list(camp.fight.can_move_and_invoke(self.npc, my_nav, invo, tar.pos)))
                my_actions.append(actions.MoveModelToPos(camp, self.npc, camp.fight.get_action_nav(self.npc), firing_pos))
            else:
                firing_pos = self.npc.pos
            my_actions.append(actions.InvokeInvocation(camp, invo, firing_pos, self.npc, [tar.pos], data=None))
            return my_actions

    def fail_ejection_check(self, camp):
        # Return True if this mecha has ejected.
        # Might be time to eject.
        perseverence = self.npc.get_skill_score(gears.stats.Ego, gears.stats.MechaPiloting)
        base_mod = 125
        if self.npc.get_current_speed() < 10:
            base_mod = 50
        intimidating_pc = camp.do_skill_test(
            gears.stats.Ego, gears.stats.Negotiation, self.npc.get_pilot().renown,
            modifier=perseverence - self.npc.get_percent_damage_over_health() + base_mod,
            synergy_skill=gears.stats.MechaPiloting, difficulty=gears.stats.DIFFICULTY_HARD
        )
        ejected = False
        if intimidating_pc:
            _=ghcutscene.SimpleMonologueDisplay("[INTIMIDATION_MECHA_COMBAT]", intimidating_pc, camp)
            _=ghcutscene.SimpleMonologueDisplay("[EJECT_AFTER_INTIMIDATION]", self.npc, camp, False)
            ejected = True
        elif self.npc.get_current_speed() < 10 and perseverence + random.randint(-25,50) < self.npc.get_percent_damage_over_health():
            _=ghcutscene.SimpleMonologueDisplay("[EJECT]", self.npc, camp)
            ejected = True

        if ejected:
            # TODO: Turn the ejection into an Alert widget too
            _=pbge.alerts.AnimAlert(gears.geffects.AnnounceEjectAnim(pos=self.npc.pos), gears.geffects.CrashAnim(self.npc))
            _=self.npc.free_pilots()
            return True

    def start_turn(self, camp) -> list:
        # Reset the per-turn properties
        self.tried_skills = False
        self.moved_to_firing_position = False
        self.minr, self.midr, self.maxr = self.get_min_mid_max_range()
        self.enemies = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc, tar)]

        # Maybe buy an extra action or two?
        my_actions = list()
        if camp.fight.cstat[self.npc].can_buy_bonus_action():
            while random.randint(1,10) == 5 and (self.npc.get_current_stamina() - camp.fight.cstat[self.npc].bonus_action_cost()) > random.randint(10,20):
                my_actions.append(actions.BuyBonusActions(camp, self.npc))
        return my_actions

    def move_to_firing_position(self, camp: gears.GearHeadCampaign):
        # The range bands have been calculated at the beginning of the turn. See if we have a better place
        # to go.
        my_actions = list()

        if (
                hasattr(self.npc, "get_speed") and self.npc.get_speed(gears.tags.Jumping) > 10 and
                camp.fight.cstat[self.npc].action_points > random.randint(1, 3) and
                camp.scene.can_use_movemode(gears.tags.Jumping)
        ):
            move = self.attempt_jump_to_better_position(camp)
            if move:
                return [move,]
        else:
            move = self.attempt_move_to_better_position(camp)
            if move:
                return [move,]

        return my_actions


    def act(self, camp: gears.GearHeadCampaign):
        # New rules in effect. The "act" method takes the camp and returns a list of actions to the
        # npc handler. If no actions are returned, this NPC's turn is over.
        if hasattr(self.npc, "gear_up"):
            self.npc.gear_up(camp.scene)

        if isinstance(self.npc, gears.base.Mecha) and camp.scene.is_hostile_to_player(self.npc) and (self.npc.get_percent_damage_over_health() > 40 or self.npc.get_current_speed() < 10):
            if self.fail_ejection_check(camp):
                return ()

        # Attempt to use a skill.
        if camp.fight.cstat[self.npc].action_points > 0 and random.randint(1, 2) == 1 and not self.tried_skills:
            actions = self.try_to_use_a_skill(camp)
            self.tried_skills = True
            if actions:
                return actions

        if not (self.target and self.target in camp.scene.contents and self.target.is_operational()):
            self.target = self.targeter.get_target(camp, self.midr)
        elif random.randint(1, 3) != 1:
            self.target = self.targeter.get_target(camp, self.midr)

        if camp.fight.cstat[self.npc].mp_remaining > 0 and not self.moved_to_firing_position:
            actions = self.move_to_firing_position(camp)
            if actions:
                self.moved_to_firing_position = True
                return actions

        if self.target:
            return self.attempt_attack(camp)



class NonPlayerTurn(pbge.widgets.Widget):
    # It's the non player character's turn.
    def __init__(self, pc, camp):
        super().__init__(0,0,0,0,)
        self.pc = pc
        self.camp = camp
        self.actions = list()

        if pc not in camp.fight.ai_brains:
            self.brain = BasicAI(pc)
            camp.fight.ai_brains[pc] = self.brain
        else:
            self.brain = camp.fight.ai_brains[pc]

        self.actions += self.brain.start_turn(camp)

    def update(self, delta):
        super().update(delta)
        if self.active and pbge.my_state.widgets_active:
            if self.actions:
                if not pbge.my_state.view.has_animations():
                    # It shouldn't be necessary to check this, since this
                    # widget deactivates during animations. But, this is me
                    # future-proofing stuff in case that changes.
                    act = self.actions[0]
                    if not act():
                        self.actions.pop(0)
            elif not self.camp.fight.still_fighting():
                self.pop()
            elif not self.camp.fight.cstat[self.pc].can_act():
                self.pop()
            else:
                actions = self.brain.act(self.camp)
                if actions:
                    self.actions += actions
                else:
                    self.camp.fight.cstat[self.pc].end_turn()
                    self.pop()
