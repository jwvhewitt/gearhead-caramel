import random
import pbge
import gears
from . import jumping
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
                return myinvo.fx.get_odds(camp, self.npc, target)
        return -1

    def closest_target_selector(self, camp, target):
        return -camp.scene.distance(self.npc.pos, target.pos)

    def most_damaged_target_selector(self, camp, target):
        return target.get_percent_damage_over_health()

    def easiest_target_selector(self, camp, target):
        myat = self.npc.get_primary_attack()
        if myat:
            myinvo = myat.get_first_working_invo(self.npc)
            if myinvo and hasattr(myinvo.fx, "get_odds"):
                return myinvo.fx.get_odds(camp, self.npc, target)
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
            if dist >= 15:
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
                odds, modz = invo.fx.get_odds(camp, self.npc, target)
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
        if hasattr(self.npc, "get_current_speed") and self.npc.get_current_speed() > 10 and camp.fight.cstat[
            self.npc].action_points > 1:
            # Check for a better tile.
            mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene, self.npc.pos,
                                                            camp.fight.cstat[self.npc].mp_remaining, self.npc.mmode,
                                                            camp.scene.get_blocked_tiles())
            sample = random.sample(list(mynav.cost_to_tile.keys()),
                                   max(len(mynav.cost_to_tile) // 2, min(5, len(mynav.cost_to_tile))))
            # sample = sample[:len(sample)//4]
            self.camp = camp
            self.minr, self.midr, self.maxr = self.get_min_mid_max_range()
            if self.target and sample:
                self.enemies = [tar for tar in camp.scene.get_operational_actors() if
                                camp.scene.are_hostile(self.npc, tar)]
                best = max(sample, key=self._desirability)
                if best is not self.npc.pos and self._desirability(best) > self._desirability(self.npc.pos):
                    self.move_to(camp, mynav, best)

    def attempt_jump_to_better_position(self, camp):
        # Check for a better tile.
        jump_points = list(jumping.get_jump_points(camp, self.npc))
        sample = random.sample(jump_points, max(len(jump_points) // 3, min(10, len(jump_points))))
        self.camp = camp
        self.minr, self.midr, self.maxr = self.get_min_mid_max_range()
        if self.target and sample:
            self.enemies = [tar for tar in camp.scene.get_operational_actors() if camp.scene.are_hostile(self.npc, tar)]
            best = max(sample, key=self._desirability)
            if best is not self.npc.pos and self._desirability(best) > self._desirability(self.npc.pos):
                jumping.jump(camp, self.npc, best)

    def attempt_attack(self, camp):
        # 1. Do I want to move?
        #    - Check to see if there's a better firing position within 1AP
        #    - Check to see if enemies are too close if minimum comfort range
        # 2. Attempt to attack
        #    - Preferred target is usually closest enemy within LOS
        #    - If can't hit preferred target, see if anyone else is in range
        #    - If no attacks possible, move closer
        if (
                hasattr(self.npc, "get_speed") and self.npc.get_speed(gears.tags.Jumping) > 10 and
                camp.fight.cstat[self.npc].action_points > 1 and random.randint(1, 3) != 2 and
                camp.scene.can_use_movemode(gears.tags.Jumping)
        ):
            self.attempt_jump_to_better_position(camp)
        else:
            self.attempt_move_to_better_position(camp)

        # We are now either in a good position, or so far out of the loop it isn't funny.
        if camp.fight.cstat[self.npc].can_act():
            my_attacks = self.npc.get_attack_library()

            # Attempt to attack the target, or failing that anyone
            # within range.
            my_invo, my_targets = self.aim_attack(camp, my_attacks)
            if my_invo:
                my_invo.invoke(camp, self.npc, my_targets, pbge.my_state.view.anim_list)
                pbge.my_state.view.handle_anim_sequence()
                camp.fight.cstat[self.npc].spend_ap(1)
            elif hasattr(self.npc, "get_current_speed") and self.npc.get_current_speed() > 10:
                # Attempt to move closer to the target.
                mynav = pbge.scenes.pathfinding.NavigationGuide(camp.scene, self.npc.pos,
                                                                camp.fight.cstat[self.npc].total_mp_remaining,
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
                    self.move_to(camp, mynav, dest)
                else:
                    # Can't move towards this target.
                    # Sit around and consider how you've reached this point in life.
                    self.target = None
                    camp.fight.cstat[self.npc].spend_ap(1)
            else:
                # Can't move, can't attack. Might as well do nothing.
                camp.fight.cstat[self.npc].spend_ap(1)

    def try_to_use_a_skill(self, camp):
        # Check to see if any skills are usable.
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
            invo = random.choice(my_skills)
            tar = random.choice(my_targets[invo])
            camp.fight.move_and_invoke(self.npc, my_nav, invo, [tar.pos],
                                       camp.fight.can_move_and_invoke(self.npc, my_nav, invo, tar.pos))
            return True

    def act(self, camp: gears.GearHeadCampaign):
        if hasattr(self.npc, "gear_up"):
            self.npc.gear_up(camp.scene)

        if isinstance(self.npc, gears.base.Mecha) and camp.scene.is_hostile_to_player(self.npc) and (self.npc.get_percent_damage_over_health() > 40 or self.npc.get_current_speed() < 10):
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
                ghcutscene.SimpleMonologueDisplay("[INTIMIDATION_MECHA_COMBAT]", intimidating_pc)(camp)
                ghcutscene.SimpleMonologueDisplay("[EJECT_AFTER_INTIMIDATION]", self.npc)(camp, False)
                ejected = True
            elif self.npc.get_current_speed() < 10 and perseverence + random.randint(-25,50) < self.npc.get_percent_damage_over_health():
                ghcutscene.SimpleMonologueDisplay("[EJECT]", self.npc)(camp)
                ejected = True

            if ejected:
                pbge.my_state.view.play_anims(gears.geffects.AnnounceEjectAnim(pos=self.npc.pos), gears.geffects.CrashAnim(self.npc))
                self.npc.free_pilots()
                return

        self.minr, self.midr, self.maxr = self.get_min_mid_max_range()

        # Maybe buy an extra action or two?
        if camp.fight.cstat[self.npc].can_buy_bonus_action():
            while random.randint(1,10) == 5 and (self.npc.get_current_stamina() - camp.fight.cstat[self.npc].bonus_action_cost()) > random.randint(10,20):
                camp.fight.cstat[self.npc].buy_bonus_action()

        # Attempt to use a skill first.
        if camp.fight.cstat[self.npc].action_points > 0 and random.randint(1, 2) == 1:
            self.try_to_use_a_skill(camp)
        while camp.fight.still_fighting() and camp.fight.cstat[self.npc].can_act():
            # If targets exist, call attack.
            # Otherwise attempt skill use again.
            if not (self.target and self.target in camp.scene.contents and self.target.is_operational()):
                self.target = self.targeter.get_target(camp, self.midr)
            elif random.randint(1, 3) != 1:
                self.target = self.targeter.get_target(camp, self.midr)
            if self.target:
                self.attempt_attack(camp)
            else:
                if not self.try_to_use_a_skill(camp):
                    camp.fight.cstat[self.npc].spend_ap(1)
