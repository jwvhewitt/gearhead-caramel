# This unit doesn't start fights, but it finishes them...
#
# After combat is over, a bunch of jobs need to get done. The Finisher widget
# will handle all end-of-combat cleanup and UI before removing the Combat object
# from the campaign.
import pbge
from pbge import my_state, scenes
import gears
from game import fieldhq
from game.content import ghcutscene
import random


# Cleanup jobs should have a "handle" method that takes the finisher widget as its only parameter.
# The widget gets passed so if the cleanup job needs its own widgets, the finisher can be pushed,
# and if the job doesn't need any kind of UI wotsit then the finisher can just be ignored.

class PostCombatCleanup:
    def __init__(self, camp: gears.GearHeadCampaign):
        self.camp = camp

    def handle(self, _fwid):
        # Make sure everyone in the party is standing somewhere appropriate.
        party = list(self.camp.get_active_party())
        if self.camp.entered_via and party:
            strays = list()

            self.guide = scenes.pathfinding.NavigationGuide(
                self.camp.scene, self.camp.entered_via.pos, 100000, 
                self.camp.scene.environment.LEGAL_MOVEMODES[0]
            )
            cx = 0
            cy = 0
            for pc in party:
                if pc.pos not in self.guide.cost_to_tile:
                    strays.append(pc)
                cx += pc.pos[0]
                cy += pc.pos[1]
            cx = cx/len(party)
            cy = cy/len(party)

            if strays:
                candidates = list(set(self.guide.cost_to_tile.keys()).difference(self.camp.scene.get_blocked_tiles()))
                candidates.sort(key=lambda pos: self.camp.scene.distance((cx,cy), pos))
                for pc in strays:
                    dest = candidates.pop(0)
                    pbge.my_state.view.play_anims(pbge.scenes.animobs.MoveModel(pc, pc.pos, dest, speed=0.5))

        for m in self.camp.scene.contents:
            if hasattr(m, "hidden") and m.hidden:
                m.hidden = False

        self.camp.scene.tidy_enchantments(gears.enchantments.END_COMBAT)


class HandleMKill:
    def __init__(self, camp, mkill):
        self.camp = camp
        self.mkill = mkill

    def _try_to_fix_mkill(self, wid, _ev):
        party, mkpc = wid.data
        
        total = 0
        if mkpc.material is gears.materials.Biotech:
            used_skill = gears.stats.Biotechnology
        else:
            used_skill = gears.stats.Repair
        for pc in party:
            if pc.get_current_mental() > 0:
                pc.spend_mental(random.randint(1,4)+random.randint(1,4))
                total += max(pc.get_skill_score(gears.stats.Craft, used_skill), random.randint(1, 5))
        my_invo = pbge.effects.Invocation(
            name = 'Repair',
            fx=gears.geffects.DoHealing(
                1, max(total,5), repair_type=mkpc.material.repair_type,
                anim = gears.geffects.RepairAnim,
                ),
            area=pbge.scenes.targetarea.SingleTarget(),
            targets=1)
        _=my_invo.invoke(self.camp, None, [mkpc.pos], pbge.my_state.view.anim_list)
        pbge.my_state.view.handle_anim_sequence()

        mkpc.gear_up(self.camp.scene)
        if mkpc.get_current_speed() > 0:
            _=pbge.alerts.TextAlert("The repairs are successful; {} is able to move again.".format(mkpc.get_pilot()))
        else:
            _=pbge.alerts.TextAlert("The repairs failed. You are forced to leave {} behind.".format(mkpc.get_pilot()))
            self.camp.scene.contents.remove(mkpc)

    def _abandon_mkill(self, wid, _ev):
        _party, mkpc = wid.data
        _=pbge.alerts.TextAlert("You leave {} behind.".format(mkpc.get_pilot()))
        self.camp.scene.contents.remove(mkpc)

    def handle(self, fwid):
        myparty = self.camp.get_active_party()

        if self.mkill.get_pilot() is self.camp.pc:
            mymenu = pbge.widgetmenu.AlertMenuWidget("Your {} has been immobilized. You can either try to repair the damage, or let the mission continue without you.".format(self.mkill.get_full_name()), pop_when_clicked=True, on_escape=self._abandon_mkill)
        else:
            mymenu = ghcutscene.SimpleMonologueMenu("[I_HAVE_BEEN_IMMOBILIZED] [HELP_WITH_MOBILITY_KILL]", self.mkill, self.camp)
        if any([m.get_current_mental() > 0 for m in myparty]):
            _=mymenu.add_item("Attempt to repair the damage.", self._try_to_fix_mkill, data=(myparty, self.mkill))
        _=mymenu.add_item("Leave {} behind.".format(self.mkill), self._abandon_mkill, data=(myparty, self.mkill))

        mymenu.push_and_deploy(fwid)


class HandleTreasure:
    def __init__(self, camp, treasure):
        self.camp = camp
        self.treasure = treasure

    def handle(self, fwid):
        _=pbge.alerts.TextAlert("You acquired some valuables from the battle.", data=fwid, on_close=self._open_item_exchanger)

    def _open_item_exchanger(self, wid, _ev):
        fieldhq.backpack.ItemExchangeWidget.push_state_and_instantiate(
            wid.data,
            camp=self.camp, pc=self.camp.first_active_pc(), conlist=self.treasure
        )

class HandleTrigger:
    def __init__(self, camp, trigger, thing):
        self.camp = camp
        self.trigger = trigger
        self.thing = thing


class Finisher(pbge.widgets.Widget):
    def __init__(self, camp:gears.GearHeadCampaign):
        super().__init__(0,0,0,0, )
        self.cleanup_queue = list()
        self.camp = camp

        # Combat is over. Deal with things.
        treasure = pbge.container.ContainerList()
        self.fainters = list()
        for m in camp.fight.active:
            if m in camp.scene.contents and camp.scene.is_an_actor(m):
                if not m.is_operational():
                    self.fainters.append(m)
                    n = m.get_pilot()
                    if n and m is not n and not n.is_operational():
                        self.fainters.append(m)
                    mteam = camp.scene.local_teams.get(m)
                    if mteam and camp.scene.player_team.is_enemy(mteam) and hasattr(m, "treasure_type") and m.treasure_type:
                        maybe_treasure = m.treasure_type.generate_treasure(self.camp, m, gears.selector.get_design_by_full_name)
                        if maybe_treasure:
                            treasure.append(maybe_treasure)

        # Deal with m-kills now; if someone is immobilized and can't be repaired, they get left behind.
        # I am well aware this might mean the entire party gets taken out of combat.
        myparty = self.camp.get_active_party()
        for pc in myparty:
            pc.hidden = False
            if isinstance(pc, gears.base.Mecha) and pc.pos and (pc.get_current_speed() < 10 or not camp.scene.can_use_movemode_here(pc.mmode, *pc.pos)):
                pc.gear_up(camp.scene)
                if pc.get_current_speed() < 10:
                    # Looks like we have a genuine Mobility Kill.
                    self.cleanup_queue.append(HandleMKill(camp, pc))

        if myparty and treasure:
            self.cleanup_queue.append(HandleTreasure(self.camp, treasure))

        self.cleanup_queue.append(PostCombatCleanup(self.camp))

    def update(self, delta):
        super().update(delta)
        if my_state.widgets_active and self.snapshot.is_current():
            if self.fainters:
                while self.fainters:
                    fnpc = self.fainters.pop()
                    if self.camp.check_trigger("FAINT", fnpc):
                        break

            elif self.cleanup_queue:
                cjob = self.cleanup_queue.pop(0)
                cjob.handle(self)

            else:
                # no cleanup jobs left. Remove the fight from the camp and pop.
                self.camp.fight = None
                self.pop()

