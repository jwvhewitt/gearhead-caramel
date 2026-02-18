from pbge import scenes
import pbge
import pygame
import gears
from gears import stats, geffects
from . import combat
from . import ghdialogue
from . import configedit
from . import invoker
from pbge import memos
from . import fieldhq
import random


# Commands should be callable objects which take the explorer and return a value.
# If untrue, the command stops.

current_explo = None


class MoveTo(object):
    """A command for moving to a particular point."""
    EXCLUDE_LAST_STEP = False

    def __init__(self, explo, pos, party=None, dest_fun=None):
        # dest_fun is a function that takes the exploration object as a parameter that is called when the party
        # reaches its destination.
        """Move the party to pos."""
        self.dest = pos
        if not party:
            # Always party.
            party = self._get_pc_party(explo)
        self.party = party
        pc = self.first_living_pc()
        # blocked_tiles = set( m.pos for m in explo.scene.contents )
        self.pmm = self._get_party_mmode(explo)
        self.path = scenes.pathfinding.AStarPath(explo.scene, pc.pos, pos, self.pmm, blocked_tiles=explo.scene.get_immovable_positions())
        if self.EXCLUDE_LAST_STEP:
            self.path.results.pop(-1)
            #self.dest = self.path.results[-1]
        self.step = 0
        self.dest_fun = dest_fun

    def _get_pc_party(self, explo):
        party = [pc for pc in explo.camp.party if pc in explo.scene.contents]
        pc = explo.camp.pc.get_root()
        if pc in party:
            party.remove(pc)
            party.insert(0, pc)
        return party

    def _get_party_mmode(self, explo):
        env = explo.scene.environment
        pc_maxmms = []
        for pc in self.party:
            if pc.is_operational():
                maxmm = 0
                for n, lmm in enumerate(env.LEGAL_MOVEMODES):
                    if pc.get_speed(lmm) > 0:
                        maxmm = n
                pc_maxmms.append(maxmm)
        if pc_maxmms:
            return env.LEGAL_MOVEMODES[min(pc_maxmms)]
        else:
            return env.LEGAL_MOVEMODES[0]

    def first_living_pc(self):
        first_pc = None
        for pc in self.party:
            if pc.is_operational():
                first_pc = pc
                break
        return first_pc

    def is_earlier_model(self, party, pc, npc):
        """Return True if npc is a party member ahead of pc in marching order."""
        # This movement routine assumes you can walk around/past any NPCs without
        # causing a fuss, unless they're hostile in which case combat will be
        # triggered so we don't have to worry about it anyhow. The one exception
        # is other party members ahead in marching order- you can't walk in
        # front of them, because that'd defeat the whole point of having a
        # marching order, wouldn't it?
        return (pc in party) and (npc in party) \
               and party.index(pc) > party.index(npc)

    def move_pc(self, exp, pc, dest, first=False):
        # Move the PC one step along the path.
        targets = exp.scene.get_actors(dest)
        if exp.scene.tile_blocks_movement(dest[0], dest[1], self.pmm):
            # There's an obstacle in the way.
            if first:
                if self.dest_fun:
                    self.dest_fun(exp)
                else:
                    wp = exp.scene.get_bumpable(dest)
                    if wp:
                        wp.bump(exp.camp, pc)
            return False
        else:
            move_ok = True
            for t in targets:
                if t.IMMOVABLE:
                    move_ok = False
                elif not self.is_earlier_model(self.party, pc, t):
                    t.pos = pc.pos
                else:
                    move_ok = False
            if move_ok:
                pc.pos = dest
            else:
                return not first
        return True

    def __call__(self, exp):
        pc = self.first_living_pc()
        self.step += 1

        if (not pc) or (self.dest == pc.pos) or (self.step >=
                                                 len(self.path.results)) or not exp.scene.on_the_map(*self.dest):
            if self.dest_fun:
                self.dest_fun(exp)
            return False
        else:
            first = True
            keep_going = True
            f_pos = self.party[0].pos
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map(*pc.pos):
                    if first:
                        keep_going = self.move_pc(exp, pc, self.path.results[self.step], True)
                        f_pos = pc.pos
                        first = False
                    elif not isinstance(pc, gears.base.Monster):
                        path = scenes.pathfinding.AStarPath(exp.scene, pc.pos, f_pos, self.pmm, blocked_tiles=exp.scene.get_immovable_positions())
                        for t in range(min(3, len(path.results) - 1)):
                            _=self.move_pc(exp, pc, path.results[t + 1])

            for pc in self.party:
                if isinstance(pc, gears.base.Monster) and pc.pet_data and pc.pet_data.trainer in self.party:
                    path = scenes.pathfinding.AStarPath(exp.scene, pc.pos, pc.pet_data.trainer.pos,
                                                        self.pmm,
                                                        blocked_tiles=exp.scene.get_blocked_tiles())
                    for t in range(min(3, len(path.results) - 1)):
                        _=self.move_pc(exp, pc, path.results[t + 1])

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position(exp.camp)

            if self.dest_fun and not keep_going:
                self.dest_fun(exp)
            return keep_going


class TalkTo(MoveTo):
    """A command for moving to a particular model, then talking with them."""

    def __init__(self, explo, npc, party=None):
        """Move the party to pos."""
        self.npc = npc
        if not party:
            # Always party.
            party = self._get_pc_party(explo)
        self.party = party
        self.step = 0
        self.pmm = self._get_party_mmode(explo)

    def __call__(self, exp):
        pc = self.first_living_pc()
        self.step += 1

        if (not pc) or self.step > 50:
            return False
        elif self.npc.pos in scenes.pfov.PointOfView(exp.scene, pc.pos[0], pc.pos[1], 3).tiles:
            ghdialogue.start_conversation(exp.camp, pc, self.npc)
            return False
        else:
            f_pos = self.npc.pos
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map(*pc.pos):
                    path = scenes.pathfinding.AStarPath(exp.scene, pc.pos, f_pos, self.pmm, blocked_tiles=exp.scene.get_immovable_positions())
                    if len(path.results) > 1:
                        _=self.move_pc(exp, pc, path.results[1])
                        f_pos = pc.pos
                    else:
                        return False

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position(exp.camp)

            return True


class BumpTo(MoveTo):
    """A command for moving to a particular waypoint, then activating it."""
    EXCLUDE_LAST_STEP = True
    def __init__(self, explo, wayp, party=None):
        super().__init__(explo, wayp.pos, party, dest_fun=self._bump_wayp)
        self.wayp = wayp

    def _bump_wayp(self, explo):
        pc = self.first_living_pc()
        if self.wayp.pos in scenes.pfov.PointOfView(explo.scene, pc.pos[0], pc.pos[1], 1).tiles:
            self.wayp.bump(explo.camp, pc)


class DoInvocation(MoveTo):
    """A command for moving to a particular spot, then invoking."""

    def __init__(self, explo, pc, pos, invo, target_list, record=False, data=None):
        """Move the pc to pos, then invoke the invocation."""
        self.party = [pc, ]
        self.pos = pos
        self.path = scenes.pathfinding.AStarPath(explo.scene, pc.pos, pos, self._get_party_mmode(explo), blocked_tiles=explo.scene.get_immovable_positions())
        self.step = 0
        self.record = record
        self.invo = invo
        self.target_list = target_list
        self.pmm = self._get_party_mmode(explo)
        self.data = data

    def __call__(self, exp):
        pc = self.party[0]
        self.step += 1

        if self.pos == pc.pos:
            # Invoke the invocation from here.
            self.invo.invoke(exp.camp, pc, self.target_list, pbge.my_state.view.anim_list, data=self.data)
            #pbge.my_state.view.handle_anim_sequence(self.record)
            return False
        elif (not pc.is_operational()) or (self.step > len(self.path.results)) or not exp.scene.on_the_map(*self.pos):
            return False
        else:
            first = True
            keep_going = True
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map(*pc.pos):
                    if first:
                        keep_going = self.move_pc(exp, pc, self.path.results[self.step], True)
                        f_pos = pc.pos
                        first = False
                    else:
                        path = scenes.pathfinding.AStarPath(exp.scene, pc.pos, f_pos, self._get_party_mmode(exp), blocked_tiles=exp.scene.get_immovable_positions())  # pyright: ignore[reportPossiblyUnboundVariable]
                        for t in range(min(3, len(path.results) - 1)):
                            _=self.move_pc(exp, pc, path.results[t + 1])

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position(exp.camp)

            return keep_going


class InvoMenuCall(object):
    def __init__(self, explo, pc, source=None):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.explo = explo
        self.pc = pc
        self.source = source

    def _on_invoke(self, invo, firing_pos, targets, data):
        if invo:
            self.explo.order = DoInvocation(self.explo, self.pc, firing_pos, invo, target_list=targets, data=data)

    def __call__(self, *args):
        invoker.InvocationUI.push_state_and_instantiate(
            camp=self.explo.camp, pc=self.pc, build_library_function=self.pc.get_skill_library,
            source=self.source, on_invoke=self._on_invoke, auto_escape=True
        )


class UsableMenuCall(object):
    def __init__(self, explo: "ExploCommandWidget", pc, source=None):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.explo = explo
        self.pc = pc
        self.source = source

    def _on_invoke(self, invo, firing_pos, targets, data):
        if invo:
            self.explo.order = DoInvocation(self.explo, self.pc, firing_pos, invo, target_list=targets, data=data)

    def __call__(self, *args):
        invoker.InvocationUI.push_state_and_instantiate(
            camp=self.explo.camp, pc=self.pc, build_library_function=self.pc.get_usable_library,
            source=self.source, on_invoke=self._on_invoke, auto_escape=True
        )


class FieldHQCall(object):
    def __init__(self, camp):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.camp = camp

    def __call__(self, *args):
        fieldhq.FieldHQ.push_state_and_instantiate(camp=self.camp)


class BumpToCall(object):
    def __init__(self, explo, wayp):
        self.explo = explo
        self.wayp = wayp

    def __call__(self, *args):
        self.explo.order = BumpTo(self.explo, self.wayp)


class ExploMenu(pbge.widgetmenu.PopupMenuWidget):
    def __init__(self, explo, pc=None):
        super().__init__(auto_escape=True)
        self.explo = explo
        self.pc = pc

        if self.pc and self.pc in self.explo.camp.party:
            my_invos = self.pc.get_skill_library()
            for i in my_invos:
                if i.has_at_least_one_working_invo(self.pc, False):
                    _=self.add_item(str(i), InvoMenuCall(self.explo, self.pc, i.source))
            my_invos = self.pc.get_usable_library()
            for i in my_invos:
                if i.has_at_least_one_working_invo(self.pc, False):
                    _=self.add_item(str(i), UsableMenuCall(self.explo, self.pc, i.source))
        else:
            for pc in self.explo.camp.get_active_party():
                if pc.get_skill_library():
                    _=self.add_item('{} Use Skill'.format(str(pc)), InvoMenuCall(self.explo, pc, None))
        _=self.add_item('-----', None)
        # Check for waypoints.
        wayp_list = self.explo.camp.scene.get_bumpables(pbge.my_state.view.mouse_tile)
        for wayp in wayp_list:
            if wayp.name:
                _=self.add_item('Use {}'.format(str(wayp)), BumpToCall(self.explo, wayp))
        # Add the standard options.
        _=self.add_item('Inventory', self.call_inventory)
        _=self.add_item('Field HQ', FieldHQCall(self.explo.camp))
        _=self.add_item('View Memos',self._open_memo_browser)
        pc = self.explo.camp.first_active_pc()
        if pc:
            _=self.add_item('Center on {}'.format(pc.get_pilot()), self.center)

    def _open_memo_browser(self, _wid, _ev):
        memos.MemoBrowser.push_state_and_instantiate(camp=self.explo.camp)

    def call_inventory(self, _wid, _ev):
        fieldhq.backpack.BackpackWidget.push_state_and_instantiate(camp=self.explo.camp, pc=self.pc or self.explo.camp.pc.get_root())

    def center(self, _wid, _ev):
        # Center on the PC.
        pc = self.explo.camp.first_active_pc()
        pbge.my_state.view.focus(pc.pos[0], pc.pos[1])


class ExploCommandWidget(pbge.widgets.Widget):
    NPC_UPDATE_TIME = 3000
    ENCHANTMENT_TIME = 6000
    def __init__(self, camp: gears.GearHeadCampaign, view):
        super().__init__(
            0,0,0,0,tags={pbge.widgets.WTAG_EXPLORATIONMODE, }
        )
        self.camp = camp
        self.scene = camp.scene
        self.view = view
        self.order = None

        self.npc_update_timer = 0
        self.enchantment_timer = 0

        self.threat_tiles = set()
        self.threat_viewer = pbge.scenes.areaindicator.AreaIndicator("sys_threatarea.png")

        self.update_npcs()

    def pick_up_item(self):
        pc = self.camp.pc.get_root()
        candidates = [i for i in self.scene.contents if
                      isinstance(i, gears.base.BaseGear) and i.pos == pc.pos and pc.can_equip(i)]
        if candidates:
            i = candidates.pop()
            _=pc.inv_com.append(i)
            _=pbge.alerts.TextAlert("{} picks up {}.".format(pc, i))
            self.camp.check_trigger("GET", i)

    def open_inventory(self):
        pc = self.camp.pc.get_root()
        fieldhq.backpack.BackpackWidget.push_state_and_instantiate(camp=self.camp, pc=pc)

    def npc_inactive(self, mon):
        return mon not in self.camp.party and ((not self.camp.fight) or mon not in self.camp.fight.active)

    CASUAL_SEARCH_CHECK = geffects.OpposedSkillRoll(stats.Perception, stats.Scouting, stats.Speed, stats.Stealth,
                                                    on_success=[True], on_failure=[], min_chance=10, max_chance=90)

    def update_npcs(self):
        my_actors = self.scene.get_operational_actors()
        self.threat_tiles.clear()
        for npc in my_actors:
            npc.renew_power()
            if self.npc_inactive(npc) and npc.pos and self.scene.on_the_map(*npc.pos):
                # Find the NPC's team- important for all kinds of things.
                npteam = self.scene.local_teams.get(npc)

                # First handle movement.
                if hasattr(npc, "get_max_speed") and random.randint(1, 100) < npc.get_max_speed():
                    dir = random.choice(self.scene.ANGDIR)
                    dest = (npc.pos[0] + dir[0], npc.pos[1] + dir[1])
                    if self.scene.on_the_map(*dest) and not self.scene.tile_blocks_movement(dest[0], dest[1],
                                                                                            npc.mmode) and (
                            not npteam or not npteam.home or npteam.home.collidepoint(
                            dest)) and not self.scene.get_operational_actors(dest):
                        npc.pos = dest

                # Next, check visibility to PC.
                if npteam and self.scene.player_team.is_enemy(npteam):
                    pov = scenes.pfov.PointOfView(self.scene, npc.pos[0], npc.pos[1],
                                                  npc.get_sensor_range(self.scene.scale) // 2 + 1)
                    in_sight = False
                    for pc in self.camp.party:
                        if pc.pos in pov.tiles and pc in my_actors:
                            if not pc.hidden:
                                in_sight = True
                                break
                            elif self.time % 75 == 0 and self.CASUAL_SEARCH_CHECK.handle_effect(self.camp, {}, npc,
                                                                                                pc.pos, list()):
                                pc.hidden = False
                                pbge.my_state.view.anim_list.append(geffects.SmokePoof(pos=pc.pos))
                                pbge.my_state.view.anim_list.append(
                                    pbge.scenes.animobs.Caption(txt='Spotted!', pos=pc.pos))
                                pbge.my_state.view.handle_anim_sequence()
                                in_sight = True
                                break
                    if in_sight:
                        combat.enter_combat(self.camp, npc)
                    else:
                        self.threat_tiles.update(pov.tiles)

    def update_enchantments(self):
        for thing in self.scene.contents:
            if hasattr(thing, 'ench_list') and hasattr(thing, "is_operational") and thing.is_operational():
                thing.ench_list.update(self.camp, thing)
        self.camp.update_area_enchantments()

    def click_left(self):
        # Left mouse button.
        if (self.view.mouse_tile != self.camp.pc.get_root().pos) and self.scene.on_the_map(*self.view.mouse_tile):
            npc = self.view.modelmap.get(self.view.mouse_tile)
            if npc and npc[0].is_operational() and self.scene.is_an_actor(npc[0]):
                npteam = self.scene.local_teams.get(npc[0])
                if npteam and self.scene.player_team.is_enemy(npteam):
                    combat.enter_combat(self.camp, npc[0])
                elif not isinstance(npc[0], (gears.base.Prop, gears.base.Monster)):
                    self.order = TalkTo(self, npc[0])
                    self.view.overlays.clear()
            else:
                self.order = MoveTo(self, self.view.mouse_tile)
                self.view.overlays.clear()
        elif self.scene.on_the_map(*self.view.mouse_tile):
            # Clicking the same tile where the PC is standing; get an item.
            self.pick_up_item()

    def update(self, delta):
        super().update(delta)
        if self.active and self.visible and pbge.my_state.widgets_active:
            if self.camp.fight:
                # If there's a combat going on, switch this widget out for the combat
                # control widget.
                self.view.overlays.clear()
                combat.CombatControlWidget.push_state_and_instantiate(camp=self.camp)
            else:
                if self.order:
                    if not self.order(self):
                        self.order = None

                    pcpos = {pc.pos for pc in self.camp.get_active_party()}
                    if pcpos.intersection(self.threat_tiles):
                        self.update_npcs()

                self.enchantment_timer += delta
                if self.enchantment_timer >= self.ENCHANTMENT_TIME:
                    self.update_enchantments()
                    self.enchantment_timer = 0
                self.npc_update_timer += delta
                if self.npc_update_timer >= self.NPC_UPDATE_TIME:
                    self.update_npcs()
                    self.npc_update_timer = 0

    def _render(self, _delta):
        super()._render(_delta)

        # Display info for this tile.
        if self.active:
            self.view.overlays.clear()
            self.threat_viewer.update(self.view, self.threat_tiles)
            my_info = self.scene.get_tile_info(self.view)
            if my_info:
                my_info.view_display(self.camp)

    def _builtin_responder(self, ev):
        if not self.order:
            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    self.click_left()
                    self.register_response()
                else:
                    pc = self.scene.get_main_actor(self.view.mouse_tile)
                    ExploMenu.push_state_and_instantiate(explo=self, pc=pc)

            elif ev.type == pygame.KEYDOWN:
                if pbge.my_state.is_key_for_action(ev, "quit_game"):
                    # self.camp.save(self.screen)
                    pbge.my_state.session_data[pbge.campaign.SDAT_GOT_QUIT] = True
                    self.register_response()
                elif pbge.my_state.is_key_for_action(ev, "inventory"):
                    self.open_inventory()
                    self.register_response()
                elif pbge.my_state.is_key_for_action(ev, "field_hq"):
                    fieldhq.FieldHQ.push_state_and_instantiate(camp=self.camp)
                    self.register_response()
                elif pbge.my_state.is_key_for_action(ev, "memo_browser"):
                    memos.MemoBrowser.push_state_and_instantiate(camp=self.camp)

                elif ev.key == pygame.K_ESCAPE:
                    configedit.PopupGameMenu.push_state_and_instantiate()
                    self.register_response()

                # elif ev.unicode == "F":
                #    self.view.play_anims(*[gears.geffects.FleeAnim(pos=pc.pos) for pc in self.camp.get_active_party()])

    def on_activate(self):
        if hasattr(self.scene, 'exploration_music')and not self.camp.fight:
            pbge.my_state.start_music(self.scene.exploration_music)
        pbge.my_state.view.cursor.frame = invoker.InvocationUI.SC_VOIDCURSOR


class Explorer(pbge.campaign.ExploPrototype):
    # The object which is exploration of a scene. OO just got existential.
    # Note that this does not get saved to disk, but instead gets created
    # anew when the game is loaded.
    HEADLINER = False
    def __init__(self, camp: gears.GearHeadCampaign):
        super().__init__(
            0,0,0,0, tags={pbge.campaign.WTAG_SCENEHANDLER,}
        )
        pbge.please_stand_by()
        self.camp = camp
        self.scene: gears.GearHeadScene = camp.scene
        party = camp.get_active_party()
        if party and party[0].pos:
            pc = party[0]
            mycursor = pbge.scenes.mapcursor.MapCursor(
                pc.pos[0], pc.pos[1], pbge.image.Image('sys_mapcursor.png', 64, 64)
            )
        else:
            mycursor = pbge.scenes.mapcursor.MapCursor(0, 0, pbge.image.Image('sys_mapcursor.png', 64, 64))
        self.view = scenes.viewer.SceneView(camp.scene, cursor=mycursor)
        self.children.append(pbge.scenes.viewer.SceneViewWidget(self.view))
        self.thirty_second_timer = 0

        # Preload some portraits and sprites.
        self.preloads = list()
        for pc in self.scene.contents:
            if hasattr(pc, 'get_portrait'):
                self.preloads.append(pc.get_portrait())
                if hasattr(pc, 'get_pilot'):
                    pcp = pc.get_pilot()
                    if pcp and pcp is not pc and hasattr(pcp, 'get_portrait'):
                        self.preloads.append(pcp.get_portrait())
            if hasattr(pc, 'get_sprite'):
                self.preloads.append(pc.get_sprite())

        # Preload the music as well.
        if pbge.util.config.getboolean("GENERAL", "music_on"):
            if hasattr(self.scene, 'exploration_music'):
                _=pbge.my_state.locate_music(self.scene.exploration_music)
                if not camp.fight:
                    pbge.my_state.start_music(self.scene.exploration_music)
            if hasattr(self.scene, 'combat_music'):
                _=pbge.my_state.locate_music(self.scene.combat_music)

        # Update the view of all party members.
        first_pc = None
        for pc in camp.get_active_party():
            if pc.pos and pc.is_operational():
                x, y = pc.pos
                _=scenes.pfov.PCPointOfView(camp.scene, x, y, pc.get_sensor_range(self.scene.scale))
                if not first_pc:
                    first_pc = pc

        # Focus on the first PC.
        if first_pc:
            self.view.focus(*first_pc.pos)

        # Make sure all graphics are updated.
        for thing in self.scene.contents:
            if hasattr(thing, 'update_graphics'):
                thing.update_graphics()

        self.children.append(ExploCommandWidget(camp, self.view))

        # Save the game, if the config says to.
        self.view()
        pygame.display.flip()
        if pbge.util.config.getboolean("GENERAL", "auto_save"):
            camp.save()

        del pbge.my_state.notifications[:]
        _=pbge.BasicNotification(str(self.scene))

        self._initial_triggers_need_checking = True

    def should_stop_exploring(self):
        if self.camp.has_a_destination():
            return True
        elif not (self.camp.egg and self.camp.first_active_pc()):
            return True

    def update(self, delta):
        # The first frame is spent checking start triggers.
        if self._initial_triggers_need_checking:
            self.camp.check_trigger("INITIALIZE")
            if not self.camp.fight:
                self.camp.check_trigger("START")
                self.camp.check_trigger("ENTER", self.scene)
            self._initial_triggers_need_checking = False
            return

        super().update(delta)

        self.thirty_second_timer += delta
        if self.thirty_second_timer > 30000:
            self.camp.check_trigger("HALFMINUTE")
            self.thirty_second_timer = 0

        if pbge.my_state.session_data.get(pbge.campaign.SDAT_GOT_QUIT):
            self.super_pop()
        elif self.should_stop_exploring():
            # Remember that update gets called whether or not the widget is active.
            # So, after the conditions are met to stop exploring, this widget deactivates
            # itself and then waits for the widgets to be empty before popping.
            # Note that it is possible - though highly ill-advised - for the "EXIT" trigger
            # to change things such that should_stop_exploring stops being True. Please don't
            # delete the destination after exiting the scene or resurrect the party outside of
            # a recovery event.
            if self.active:
                self.camp.check_trigger("EXIT")
                self.active = False
            if not pbge.my_state.ui_is_active():
                self.pop()

    def respond_event(self, ev):
        if not self._initial_triggers_need_checking:
            return super().respond_event(ev)

    def _builtin_responder(self, ev):
        if ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "center_on_pc"):
                pc = self.camp.first_active_pc()
                self.view.focus(pc.pos[0], pc.pos[1])
                self.register_response()



