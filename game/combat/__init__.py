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
from . import pcaction
from . import aihaywire
import random
import gears
from . import aibrain
from . import finisher


ALT_AIS = {
    "HaywireAI": aihaywire.HaywireTurn
}

WTAG_COMBATHANDLER = "WTAG_COMBATHANDLER"


def enter_combat(camp, npc):
    # Activate this foe, starting combat if it hasn't already started.
    if camp.fight:
        camp.fight.activate_foe(npc)
    else:
        camp.fight = Combat(camp)
        camp.fight.activate_foe(npc)


def start_continuous_combat(camp):
    # Start a combat that will not end even if there are no active enemies. In this case, it's up to the script
    # controlling the combat to end combat.
    if camp.fight:
        camp.fight.keep_going_without_enemies = True
    else:
        camp.fight = Combat(camp, keep_going_without_enemies=True)


class CombatStat(object):
    """Keep track of some stats that only matter during combat."""

    def __init__(self, combatant: gears.base.Combatant):
        self.combatant = combatant
        self.aoo_readied = False
        self.attacks_this_round = 0
        self.moves_this_round = 0
        self._mp_spent = 0
        self._ap_remaining = 0
        self.has_started_turn = False
        self.last_weapon_used = None
        self.last_program_used = None
        self.extra_actions_taken = 0

    @property
    def mp_remaining(self):
        if hasattr(self.combatant, "get_current_speed"):
            return max(self.combatant.get_current_speed() - self._mp_spent, 0)
        else:
            return 0

    @property
    def action_points(self):
        return self._ap_remaining

    def can_act(self):
        return self.action_points > 0

    def spend_ap(self, ap):
        self._ap_remaining -= ap

    def spend_mp(self, mp):
        self._mp_spent += mp

    def reset_movement(self):
        if self._mp_spent > 0:
            self._mp_spent = 99999999

    def start_turn(self, chara):
        self._ap_remaining += chara.get_action_points()
        self.has_started_turn = True
        self.moves_this_round = 0
        self.attacks_this_round = 0
        self._mp_spent = 0
        self.extra_actions_taken = 0

    def end_turn(self):
        if self._ap_remaining > 0:
            self._ap_remaining = 0
        self._mp_spent = 0

    def bonus_action_cost(self):
        return max(self.extra_actions_taken * 5 + self.combatant.scale.BONUS_ACTION_BASE_COST - self.combatant.get_bonus_action_cost_mod(), 5)

    def can_buy_bonus_action(self):
        return isinstance(self.combatant, (gears.base.Character, gears.base.Mecha)) and self.combatant.get_current_stamina() >= self.bonus_action_cost()

    def buy_bonus_action(self):
        if self.can_buy_bonus_action():
            self.combatant.spend_stamina(self.bonus_action_cost())
            self._ap_remaining += 1
            self.extra_actions_taken += 1
            pbge.my_state.view.play_anims(gears.geffects.BonusActionAnim(pos=self.combatant.pos), pbge.scenes.animobs.Caption(txt="+1 Action", pos=self.combatant.pos))



class CombatDict:
    def __init__(self):
        self._entries = dict()

    def __getitem__(self, key) -> CombatStat:
        if key in self._entries:
            return self._entries[key]
        else:
            val = CombatStat(key)
            self._entries[key] = val
            return val

    @classmethod
    def from_dict(cls, my_dict):
        nu_dict = cls()
        for k, v in my_dict.items():
            v = CombatStat(k)
            nu_dict._entries[k] = v
        return nu_dict


class CombatControlWidget(pbge.widgets.Widget):
    TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_EXPLORATIONMODE,}

    def __init__(self, camp: gears.GearHeadCampaign):
        super().__init__(0,0,0,0,tags={WTAG_COMBATHANDLER,})
        self.camp = camp
        self._current_combatant = None
        if self.camp.scene.combat_music:
            pbge.my_state.start_music(self.camp.scene.combat_music)

    def get_next_combatant(self):
        for chara in self.camp.fight.active:
            cdata = self.camp.fight.cstat[chara]
            if not cdata.has_started_turn:
                return chara
            elif cdata.can_act():
                return chara

    def on_activate(self):
        # When control returns to the combat controller, do the end-of-turn upkeep for
        # the most recent combatant.
        if self._current_combatant and self.camp.fight:
            self.camp.fight.cstat[self._current_combatant].aoo_readied = True
            self.camp.fight.cstat[self._current_combatant].attacks_this_round = 0
            self._current_combatant.renew_power()

    def do_combat_turn(self, chara):
        self._current_combatant = chara
        if chara in self.camp.party and not (isinstance(chara, gears.base.Monster) and not pbge.util.config.getboolean("DIFFICULTY", "directly_control_pets")):
            # Outsource the turn-taking.
            turn_widget = pcaction.PlayerTurn(pc=chara, camp=self.camp)
        else:
            turn_widget = aibrain.NonPlayerTurn(pc=chara, camp=self.camp)

        if not self.camp.fight.cstat[chara].has_started_turn:
            self.camp.fight.cstat[chara].start_turn(chara)
            if hasattr(chara, 'ench_list') and chara.ench_list and chara.is_operational():
                chara.ench_list.update(self.camp, chara)  # pyright: ignore[reportUnusedCallResult]
                alt_ais = chara.ench_list.get_tags('ALT_AI')
                if alt_ais:
                    current_ai = random.choice(alt_ais)
                    if current_ai in ALT_AIS:
                        turn_widget.actions += ALT_AIS[current_ai](chara, self.camp).get_actions()

        if chara.is_operational():
            turn_widget.push_and_deploy(self)
        else:
            self.camp.fight.cstat[chara].end_turn()

    def update(self, delta):
        super().update(delta)
        if self.camp.fight:
            if self.snapshot.is_current():
                if not self.camp.fight.checked_start_trigger:
                    _=self.camp.check_trigger("STARTCOMBAT")
                    self.camp.fight.checked_start_trigger = True
                    return
                if self.camp.fight.still_fighting():
                    # Find the next active combatant and deploy their turn widget.
                    chara = self.get_next_combatant()

                    if chara:
                        self.do_combat_turn(chara)
                    else:
                        # No combatants to act? Start the next round.
                        self.camp.fight.end_round()
                        self._current_combatant = None
                        _=self.camp.check_trigger("COMBATLOOP")

                else:
                    if self.camp.fight.is_concluded():
                        _=self.camp.check_trigger("COMBATLOOP")
                        finisher.Finisher.push_state_and_instantiate(self, camp=self.camp)
                    else:
                        self.pop()
        else:
            self.pop()


class Combat(object):
    def __init__(self, camp: gears.GearHeadCampaign, keep_going_without_enemies=False):
        self.active = list(camp.get_active_party())
        self.scene: gears.GearHeadScene = camp.scene
        self.camp = camp
        self.ap_spent = collections.defaultdict(int)
        self.cstat = CombatDict()
        self.ai_brains = dict()
        self.n = 0
        self.keep_going_without_enemies = keep_going_without_enemies
        self.cooldowns = collections.defaultdict(int)
        self.checked_start_trigger = False

    def roll_initiative(self):
        # Sort based on initiative roll.
        self.active.sort(key=self._get_npc_initiative, reverse=True)

    def _get_npc_initiative(self, chara):
        return chara.get_stat(gears.stats.Speed) + random.randint(1, 20)

    def activate_foe(self, foe):
        # If the foe is already active, our work here is done.
        if foe in self.active:
            return

        foeteam = self.scene.local_teams.get(foe)
        team_frontier = [foeteam, self.scene.player_team]
        while team_frontier:
            myteam = team_frontier.pop()
            _=self.camp.check_trigger('ACTIVATETEAM', myteam)
            activation_area = set()
            # Add team members
            for m in self.scene.contents:
                if m not in self.active and self.scene.local_teams.get(m) is myteam and isinstance(m,
                                                                                                   gears.base.Combatant):
                    _=self.camp.check_trigger('ACTIVATE', m)
                    myview = scenes.pfov.PointOfView(self.scene, m.pos[0], m.pos[1], 5)
                    activation_area.update(myview.tiles)
                    if not hasattr(m, "combatant") or m.combatant:
                        self.active.append(m)
                    else:
                        pbge.my_state.view.anim_list.append(gears.geffects.SmokePoof(pos=m.pos))
                        m.pos = None

            # Check for further activations
            for m in self.scene.contents:
                if m not in self.active and m.pos in activation_area:
                    ateam = self.scene.local_teams.get(m)
                    if ateam and ateam not in team_frontier:
                        team_frontier.append(ateam)

        self.roll_initiative()

    def check_party_activation(self):
        # Add party members who became party members after combat already started. They might be active and they might
        # not be.
        for m in self.scene.contents:
            if m not in self.active and self.scene.local_teams.get(m) is self.scene.player_team and isinstance(m,
                                                                                               gears.base.Combatant):
                _=self.camp.check_trigger('ACTIVATE', m)
                self.active.append(m)

    def num_enemies(self):
        """Return the number of active, hostile characters."""
        n = 0
        for m in self.active:
            if m in self.scene.contents and self.scene.is_an_actor(
                    m) and m.is_operational() and self.scene.player_team.is_enemy(self.scene.local_teams.get(m)):
                n += 1
        return n

    def is_not_concluded(self):
        # Return True if this combat has not ended. Note that the combat may get suspended
        # temporarily- say, if the player quits and later reloads.
        return (
            (self.num_enemies() or self.keep_going_without_enemies) and
            self.camp.first_active_pc() and self.camp.scene is self.scene
        )

    def is_concluded(self):
        # Return True if this combat is over and should be removed from the campaign.
        return not self.is_not_concluded()

    def still_fighting(self):
        """Keep playing as long as there are enemies, players, and no quit."""
        return (
            self.is_not_concluded() and not pbge.my_state.session_data.get(pbge.campaign.SDAT_GOT_QUIT)
            and not pbge.my_state.got_quit and self.camp.egg
        )

    def step(self, chara, dest):
        """Move chara to dest directly."""
        chara.move(dest, pbge.my_state.view, 0.4)
        self.cstat[chara].moves_this_round += 1
        self.camp.invoke_area_effects(dest)

    def get_action_nav(self, pc):
        # Return the navigation guide for this character.
        if hasattr(pc, 'get_current_speed'):
            return pbge.scenes.pathfinding.NavigationGuide(
                self.camp.scene, pc.pos, self.cstat[pc].mp_remaining, pc.mmode,
                self.camp.scene.get_blocked_tiles()
            )

    def can_move_and_invoke(self, chara, nav, invo, target_pos):
        # If this invocation can be used on this target pos this round, return a set of firing
        # positions.
        if hasattr(invo.area, 'MOVE_AND_FIRE') and not invo.area.MOVE_AND_FIRE:
            return False
        else:
            firing_points = invo.area.get_firing_points(self.camp, target_pos)
            if nav:
                return firing_points.intersection(list(nav.cost_to_tile.keys()))
            else:
                return {chara.pos}.intersection(firing_points)

    def end_round(self):
        for chara in self.active:
            self.cstat[chara].end_turn()
            self.cstat[chara].has_started_turn = False
        for k in list(self.cooldowns.keys()):
            self.cooldowns[k] -= 1
            if self.cooldowns[k] <= 0:
                del self.cooldowns[k]
        self.camp.update_area_enchantments()
        _=self.camp.check_trigger("COMBATROUND")

    def __setstate__(self, state):
        # For saves from V0.905 or earlier, make sure the CombatDict is used.
        mydict = state.get("cstat")
        if not isinstance(mydict, CombatDict):
            state["cstat"] = CombatDict.from_dict(mydict)
        self.__dict__.update(state)
        if "keep_going_without_enemies" not in state:
            self.keep_going_without_enemies = False
        if "cooldowns" not in state:
            self.cooldowns = collections.defaultdict(int)
