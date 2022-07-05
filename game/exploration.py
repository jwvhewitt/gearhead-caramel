from pbge import scenes
import pbge
import pygame
import gears
from gears import stats,geffects
from . import combat
from . import ghdialogue
from . import configedit
from . import invoker
from pbge import memos
from . import fieldhq
import random

import json
import inspect

class GHEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        self.__uid_lookup__ = dict()
        super().__init__(*args, **kwargs)
    def default(self, obj):
        if inspect.isclass(obj) and obj in gears.SINGLETON_REVERSE:
            return True
        if obj and not isinstance(obj, (str, int, float, bool)):
            # Check the __uid_lookup__ dict.
            if repr(obj) in self.__uid_lookup__:
                return True
            else:
                self.__uid_lookup__[repr(obj)] = "bla"
                mydict = dir(obj)
                return mydict
        if isinstance(obj, pbge.container.ContainerList):
            return list(obj)
        if isinstance(obj, pbge.container.ContainerDict):
            return dict(obj)
        if isinstance(obj, pbge.container.Container):
            return None

        return json.JSONEncoder.default(self, obj)

    @classmethod
    def save_by_json(cls, camp):
        with open( pbge.util.user_dir( "rpg_" + camp.name + ".json" ) , "wt" ) as f:
            json.dump(camp, f, cls=cls)

# Commands should be callable objects which take the explorer and return a value.
# If untrue, the command stops.

current_explo = None

class MoveTo( object ):
    """A command for moving to a particular point."""
    def __init__( self, explo, pos, party=None ):
        """Move the party to pos."""
        self.dest = pos
        if not party:
            # Always party.
            party = self._get_pc_party(explo)
        self.party = party
        pc = self.first_living_pc()
        #blocked_tiles = set( m.pos for m in explo.scene.contents )
        self.path = scenes.pathfinding.AStarPath(explo.scene,pc.pos,pos,pc.mmode)
        self.step = 0
    def _get_pc_party( self, explo ):
        party = [pc for pc in explo.camp.party if pc in explo.scene.contents]
        pc = explo.camp.pc.get_root()
        if pc in party:
            party.remove(pc)
            party.insert(0,pc)
        return party

    def first_living_pc( self ):
        first_pc = None
        for pc in self.party:
            if pc.is_operational():
                first_pc = pc
                break
        return first_pc

    def is_earlier_model( self, party, pc, npc ):
        """Return True if npc is a party member ahead of pc in marching order."""
        # This movement routine assumes you can walk around/past any NPCs without
        # causing a fuss, unless they're hostile in which case combat will be
        # triggered so we don't have to worry about it anyhow. The one exception
        # is other party members ahead in marching order- you can't walk in
        # front of them, because that'd defeat the whole point of having a
        # marching order, wouldn't it?
        return ( pc in party ) and ( npc in party ) \
            and party.index( pc ) > party.index( npc )

    def move_pc( self, exp, pc, dest, first=False ):
        # Move the PC one step along the path.
        targets = exp.scene.get_actors( dest )
        if exp.scene.tile_blocks_movement(dest[0],dest[1],pc.mmode):
            # There's an obstacle in the way.
            if first:
                wp = exp.scene.get_bumpable(dest)
                if wp:
                    wp.bump(exp.camp,pc)
            return False
        else:
            move_ok = True
            for t in targets:
                if not self.is_earlier_model( self.party, pc, t ):
                    t.pos = pc.pos
                else:
                    move_ok = False
            if move_ok:
                pc.pos = dest
            else:
                return not first
        return True

    def __call__( self, exp ):
        pc = self.first_living_pc()
        self.step += 1

        if (not pc) or ( self.dest == pc.pos ) or ( self.step >
         len(self.path.results) ) or not exp.scene.on_the_map( *self.dest ):
            return False
        else:
            first = True
            keep_going = True
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map( *pc.pos ):
                    if first:
                        keep_going = self.move_pc( exp, pc, self.path.results[self.step], True )
                        f_pos = pc.pos
                        first = False
                    else:
                        path = scenes.pathfinding.AStarPath(exp.scene,pc.pos,f_pos,pc.mmode)
                        for t in range( min(3,len(path.results)-1)):
                            self.move_pc( exp, pc, path.results[t+1] )

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position( exp.camp )

            return keep_going

class TalkTo( MoveTo ):
    """A command for moving to a particular model, then talking with them."""
    def __init__( self, explo, npc, party=None ):
        """Move the party to pos."""
        self.npc = npc
        if not party:
            # Always party.
            party = self._get_pc_party(explo)
        self.party = party
        self.step = 0

    def __call__( self, exp ):
        pc = self.first_living_pc()
        self.step += 1

        if (not pc) or self.step > 50:
            return False
        elif self.npc.pos in scenes.pfov.PointOfView( exp.scene, pc.pos[0], pc.pos[1], 3 ).tiles:
            ghdialogue.start_conversation(exp.camp,pc,self.npc)
            return False
        else:
            f_pos = self.npc.pos
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map( *pc.pos ):
                    path = scenes.pathfinding.AStarPath(exp.scene,pc.pos,f_pos,pc.mmode)
                    self.move_pc( exp, pc, path.results[1] )
                    f_pos = pc.pos

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position( exp.camp )

            return True

class BumpTo( MoveTo ):
    """A command for moving to a particular waypoint, then activating it."""
    def __init__( self, explo, wayp, party=None ):
        """Move the party to pos."""
        self.wayp = wayp
        if not party:
            # Always party.
            party = self._get_pc_party(explo)
        self.party = party
        self.step = 0

    def __call__( self, exp ):
        pc = self.first_living_pc()
        self.step += 1

        if (not pc) or self.step > 50:
            return False
        elif self.wayp.pos in scenes.pfov.PointOfView( exp.scene, pc.pos[0], pc.pos[1], 1 ).tiles:
            self.wayp.bump(exp.camp,pc)
            return False
        else:
            f_pos = self.wayp.pos
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map( *pc.pos ):
                    path = scenes.pathfinding.AStarPath(exp.scene,pc.pos,f_pos,pc.mmode)
                    self.move_pc( exp, pc, path.results[1] )
                    f_pos = pc.pos

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position( exp.camp )

            return True

class DoInvocation( MoveTo ):
    """A command for moving to a particular spot, then invoking."""
    def __init__( self, explo, pc, pos, invo, target_list, record=False ):
        """Move the pc to pos, then invoke the invocation."""
        self.party = [pc,]
        self.pos = pos
        self.path = scenes.pathfinding.AStarPath(explo.scene,pc.pos,pos,pc.mmode)
        self.step = 0
        self.record = record
        self.invo = invo
        self.target_list = target_list
    def __call__( self, exp ):
        pc = self.party[0]
        self.step += 1

        if self.pos == pc.pos:
            # Invoke the invocation from here.
            self.invo.invoke(exp.camp, pc, self.target_list, pbge.my_state.view.anim_list )
            pbge.my_state.view.handle_anim_sequence(self.record)
            return False
        elif (not pc.is_operational()) or ( self.step > len(self.path.results) ) or not exp.scene.on_the_map( *self.pos ):
            return False
        else:
            first = True
            keep_going = True
            for pc in self.party:
                if pc.is_operational() and exp.scene.on_the_map( *pc.pos ):
                    if first:
                        keep_going = self.move_pc( exp, pc, self.path.results[self.step], True )
                        f_pos = pc.pos
                        first = False
                    else:
                        path = scenes.pathfinding.AStarPath(exp.scene,pc.pos,f_pos,pc.mmode)
                        for t in range( min(3,len(path.results)-1)):
                            self.move_pc( exp, pc, path.results[t+1] )

            # Now that all of the pcs have moved, check the tiles_in_sight for
            # hidden models.
            exp.scene.update_party_position( exp.camp )

            return keep_going
            
class InvoMenuCall( object ):
    def __init__(self,explo,pc,source=None):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.explo = explo
        self.pc = pc
        self.source = source
    def __call__(self):
        self.explo.order = invoker.InvocationUI.explo_invoke(self.explo,self.pc,self.pc.get_skill_library,self.source)

class UsableMenuCall( object ):
    def __init__(self,explo,pc,source=None):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.explo = explo
        self.pc = pc
        self.source = source
    def __call__(self):
        self.explo.order = invoker.InvocationUI.explo_invoke(self.explo,self.pc,self.pc.get_usable_library,self.source)

class FieldHQCall( object ):
    def __init__(self,camp):
        # Creates a callable that opens the invocation UI and handles
        # its effects.
        self.camp = camp
    def __call__(self):
        fieldhq.FieldHQ.create_and_invoke(self.camp)

class BumpToCall(object):
    def __init__(self,explo,wayp):
        self.explo = explo
        self.wayp = wayp
    def __call__(self):
        self.explo.order = BumpTo(self.explo,self.wayp)

class ExploMenu( object ):
    def __init__(self,explo,pc=None):
        self.explo = explo
        self.pc = pc
        self.query()

    def query( self ):
        mymenu = pbge.rpgmenu.PopUpMenu()

        if self.pc and self.pc in self.explo.camp.party:
            my_invos = self.pc.get_skill_library()
            for i in my_invos:
                if i.has_at_least_one_working_invo(self.pc,False):
                    mymenu.add_item(str(i),InvoMenuCall(self.explo,self.pc,i.source))
            my_invos = self.pc.get_usable_library()
            for i in my_invos:
                if i.has_at_least_one_working_invo(self.pc, False):
                    mymenu.add_item(str(i), UsableMenuCall(self.explo, self.pc, i.source))
        else:
            for pc in self.explo.camp.get_active_party():
                if pc.get_skill_library():
                    mymenu.add_item('{} Use Skill'.format(str(pc)),InvoMenuCall(self.explo,pc,None))
        mymenu.add_item('-----',None)
        # Check for waypoints.
        wayp_list = self.explo.camp.scene.get_bumpables(pbge.my_state.view.mouse_tile)
        for wayp in wayp_list:
            if wayp.name:
                mymenu.add_item('Use {}'.format(str(wayp)),BumpToCall(self.explo,wayp))
        # Add the standard options.
        mymenu.add_item('Field HQ', FieldHQCall(self.explo.camp))
        mymenu.add_item('View Memos', memos.MemoBrowser(self.explo.camp))
        pc = self.explo.camp.first_active_pc()
        if pc:
            mymenu.add_item('Center on {}'.format(pc.get_pilot()), self.center)
        mi = mymenu.query()
        if mi:
            mi()

    def center(self):
        # Center on the PC.
        pc = self.explo.camp.first_active_pc()
        pbge.my_state.view.focus(pc.pos[0], pc.pos[1])


class Explorer( object ):
    # The object which is exploration of a scene. OO just got existential.
    # Note that this does not get saved to disk, but instead gets created
    # anew when the game is loaded.
    def __init__( self, camp: gears.GearHeadCampaign ):
        pbge.please_stand_by()
        self.camp = camp
        self.scene: gears.GearHeadScene = camp.scene
        pc: gears.base.Character = camp.get_active_party()[0]
        self.view = scenes.viewer.SceneView( camp.scene, cursor=pbge.scenes.mapcursor.MapCursor(
            pc.pos[0], pc.pos[1], pbge.image.Image('sys_mapcursor.png',64,64)
        ))
        self.time = 0

        self.threat_tiles = set()
        self.threat_viewer = pbge.scenes.areaindicator.AreaIndicator("sys_threatarea.png")

        self.record_count = 0

        # Preload some portraits and sprites.
        self.preloads = list()
        for pc in self.scene.contents:
            if hasattr(pc,'get_portrait'):
                self.preloads.append(pc.get_portrait())
                if hasattr(pc,'get_pilot'):
                    pcp = pc.get_pilot()
                    if pcp and pcp is not pc and hasattr(pcp,'get_portrait'):
                        self.preloads.append(pcp.get_portrait())
            if hasattr(pc,'get_sprite'):
                self.preloads.append(pc.get_sprite())

        # Preload the music as well.
        if pbge.util.config.getboolean( "GENERAL", "music_on" ):
            if hasattr( self.scene, 'exploration_music'):
                pbge.my_state.locate_music(self.scene.exploration_music)
            if hasattr( self.scene, 'combat_music'):
                pbge.my_state.locate_music(self.scene.combat_music)

        # Update the view of all party members.
        first_pc = None
        for pc in camp.get_active_party():
            if pc.pos and pc.is_operational():
                x,y = pc.pos
                scenes.pfov.PCPointOfView( camp.scene, x, y, pc.get_sensor_range(self.scene.scale) )
                if not first_pc:
                    first_pc = pc

        # Focus on the first PC.
        if first_pc:
            x,y = first_pc.pos
            self.view.focus( x, y )

        # Make sure all graphics are updated.
        for thing in self.scene.contents:
            if hasattr(thing,'update_graphics'):
                thing.update_graphics()

        # Save the game, if the config says to.
        if pbge.util.config.getboolean( "GENERAL", "auto_save" ):
            camp.save()

    def update_scene( self ):
        for npc in self.scene.contents:
            if hasattr(npc,"gear_up"):
                npc.gear_up()

    def keep_exploring( self ):
        return self.camp.first_active_pc() and self.no_quit and not pbge.my_state.got_quit and self.camp.keep_playing_scene() and self.camp.egg

    def npc_inactive( self, mon ):
        return mon not in self.camp.party and (( not self.camp.fight ) or mon not in self.camp.fight.active)

    def activate_foe( self, npc ):
        # Activate this foe, starting combat if it hasn't already started.
        if self.camp.fight:
            self.camp.fight.activate_foe( npc )
        else:
            self.camp.fight = combat.Combat( self.camp )
            self.camp.fight.activate_foe( npc )

    CASUAL_SEARCH_CHECK = geffects.OpposedSkillRoll(stats.Perception, stats.Scouting, stats.Speed, stats.Stealth,
                                                    on_success=[True], on_failure=[], min_chance=10, max_chance=90)

    def update_npcs( self ):
        my_actors = self.scene.get_operational_actors()
        self.threat_tiles.clear()
        for npc in my_actors:
            npc.renew_power()
            if self.npc_inactive(npc) and npc.pos and self.scene.on_the_map(*npc.pos):
                # Find the NPC's team- important for all kinds of things.
                npteam = self.scene.local_teams.get(npc)

                # First handle movement.
                if hasattr(npc,"get_max_speed") and random.randint(1,100) < npc.get_max_speed():
                    dir = random.choice(self.scene.ANGDIR)
                    dest = (npc.pos[0] + dir[0],npc.pos[1]+dir[1])
                    if self.scene.on_the_map(*dest) and not self.scene.tile_blocks_movement(dest[0],dest[1],npc.mmode) and (not npteam or not npteam.home or npteam.home.collidepoint(dest)) and not self.scene.get_operational_actors(dest):
                        npc.pos = dest

                # Next, check visibility to PC.
                if npteam and self.scene.player_team.is_enemy( npteam ):
                    pov = scenes.pfov.PointOfView( self.scene, npc.pos[0], npc.pos[1], npc.get_sensor_range(self.scene.scale)//2+1 )
                    in_sight = False
                    for pc in self.camp.party:
                        if pc.pos in pov.tiles and pc in my_actors:
                            if not pc.hidden:
                                in_sight = True
                                break
                            elif self.time % 75 == 0 and self.CASUAL_SEARCH_CHECK.handle_effect(self.camp,{},npc,pc.pos,list()):
                                pc.hidden = False
                                pbge.my_state.view.anim_list.append(geffects.SmokePoof(pos=pc.pos))
                                pbge.my_state.view.anim_list.append(pbge.scenes.animobs.Caption(txt='Spotted!',pos=pc.pos))
                                pbge.my_state.view.handle_anim_sequence()
                                in_sight = True
                                break
                    if in_sight:
                        self.activate_foe( npc )
                    else:
                        self.threat_tiles.update(pov.tiles)

    def update_enchantments(self):
        for thing in self.scene.contents:
            if hasattr(thing,'ench_list'):
                thing.ench_list.update(self.camp,thing)

    def get_item(self):
        pc = self.camp.pc.get_root()
        candidates = [i for i in self.scene.contents if isinstance(i,gears.base.BaseGear) and i.pos == pc.pos and pc.can_equip(i)]
        if candidates:
            i = candidates.pop()
            pc.inv_com.append(i)
            pbge.alert("{} picks up {}.".format(pc,i))
            self.camp.check_trigger("GET",i)

    def click_left(self):
        # Left mouse button.
        if (self.view.mouse_tile != self.camp.pc.get_root().pos) and self.scene.on_the_map(*self.view.mouse_tile):
            npc = self.view.modelmap.get(self.view.mouse_tile)
            if npc and npc[0].is_operational() and self.scene.is_an_actor(npc[0]):
                npteam = self.scene.local_teams.get(npc[0])
                if npteam and self.scene.player_team.is_enemy(npteam):
                    self.activate_foe(npc[0])
                elif not isinstance(npc[0], (gears.base.Prop, gears.base.Monster)):
                    self.order = TalkTo(self, npc[0])
                    self.view.overlays.clear()
            else:
                self.order = MoveTo(self, self.view.mouse_tile)
                self.view.overlays.clear()
        elif self.scene.on_the_map(*self.view.mouse_tile):
            # Clicking the same tile where the PC is standing; get an item.
            self.get_item()

    def go( self ):
        self.no_quit = True
        self.order = None

        global current_explo
        current_explo = self

        self.update_scene()
        #self.scene.update_party_position(self.camp)

        # Clear the event queue, in case switching scenes took a long time.
        pygame.event.clear([pbge.TIMEREVENT,pygame.KEYDOWN])

        # Do one view first, just to prep the model map and mouse tile.
        self.view()
        pbge.my_state.do_flip()
        #self.record_count = 120

        del pbge.my_state.notifications[:]
        pbge.BasicNotification(str(self.scene))

        # Do a start trigger, unless we're in combat.
        if not self.camp.fight:
            if hasattr(self.scene, "exploration_music"):
                pbge.my_state.start_music(self.scene.exploration_music)
            self.camp.check_trigger( "START" )
            self.camp.check_trigger( "ENTER", self.scene )
        self.camp.check_trigger( "UPDATE" )
        self.update_npcs()

        while self.keep_exploring():
            first_pc_pos=self.camp.first_active_pc().pos
            if self.camp.fight:
                self.camp.check_trigger( "STARTCOMBAT" )
                self.order = None
                self.camp.fight.go(self)
                if pbge.my_state.got_quit or not self.camp.fight.no_quit:
                    self.no_quit = False
                    self.camp.fight.no_quit = True
                    break
                else:
                    self.camp.fight = None
                    self.camp.check_trigger( "ENDCOMBAT" )

            # Get input and process it.
            gdi = pbge.wait_event()

            if not self.keep_exploring():
                pass
            elif gdi.type == pbge.TIMEREVENT:
                self.view.overlays.clear()
                self.threat_viewer.update(self.view, self.threat_tiles)
                self.view()

                # Display info for this tile.
                my_info = self.scene.get_tile_info(self.view.mouse_tile)
                if my_info:
                    pos = self.view.screen_coords(*self.view.mouse_tile)
                    my_info.popup((pos[0]+32, pos[1]+64))

                pbge.my_state.do_flip()

                if self.record_count > 0:
                    pygame.image.save(pbge.my_state.screen, pbge.util.user_dir("exanim_{}.png".format(100000-self.record_count)))
                    self.record_count -= 1

                self.time += 1
                if hasattr(self.scene,"exploration_music"):
                    pbge.my_state.start_music(self.scene.exploration_music)

                if self.order:
                    if not self.order( self ):
                        self.order = None
                    #self.update_npcs()
                    pcpos = {pc.pos for pc in self.camp.get_active_party()}
                    if pcpos.intersection(self.threat_tiles):
                        self.update_npcs()

                if self.time % 50 == 0:
                    self.update_npcs()

                if self.time % 150 == 0:
                    self.update_enchantments()

            elif not self.order:
                # Set the mouse cursor on the map.
                #self.view.overlays[ self.view.mouse_tile ] = maps.OVERLAY_CURSOR

                if gdi.type == pygame.KEYDOWN:
                    if gdi.unicode == "Q":
                        #self.camp.save(self.screen)
                        self.no_quit = False
                    elif gdi.unicode == "c":
                        pc = self.camp.first_active_pc()
                        pbge.my_state.view.focus( pc.pos[0], pc.pos[1] )
                    elif gdi.unicode == "m":
                        memos.MemoBrowser(self.camp)()
                    elif gdi.unicode == "R" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        print(self.camp.renown)
                    elif gdi.unicode == "A" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        self.record_count = 30

                    elif gdi.key in pbge.my_state.get_keys_for("cursor_click"):
                        self.click_left()

                    elif gdi.unicode == "J" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        # Experimenting with JSON serialization. It isn't going well.
                        GHEncoder.save_by_json(self.camp)

                    elif gdi.unicode == "&" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        for x in range(self.scene.width):
                            for y in range(self.scene.height):
                                self.scene.set_visible(x,y,True)

                    elif gdi.unicode == "!" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        self.camp.egg.credits += 1000000
                        for mpc in self.camp.get_active_party():
                            pc = mpc.get_pilot()
                            if pc:
                                for skill in pc.statline:
                                    if skill in gears.stats.ALL_SKILLS:
                                        pc.statline[skill] += 10

                    elif gdi.unicode == "@" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        for thing in self.scene.contents:
                            if hasattr(thing,"pos"):
                                print("{}: {}".format(thing,thing.pos))

                    elif gdi.unicode == "*" and pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
                        for thing in self.camp.all_contents(self.camp):
                            if isinstance(thing, gears.base.Character):
                                print("{}: {}/{}".format(thing, thing.faction, thing.scene.get_root_scene()))

                    elif gdi.unicode == "P" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        for thing in self.camp.active_plots():
                            print("{}".format(thing.__class__.__name__))
                    elif gdi.unicode == "C" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        myfac = self.camp.faction_relations.get(self.scene.get_metro_scene().faction)
                        print(myfac.enemies)
                    elif gdi.unicode == "L" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        for pc in self.camp.get_active_party():
                            if hasattr(pc,"relationship") and pc.relationship:
                                print("{} {} {} OK:{}".format(pc,pc.renown,pc.relationship.hilights(),pc.relationship.can_do_development()))
                    elif gdi.unicode == "V" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        for pc in list(self.camp.party):
                            if pc in self.scene.contents and isinstance(pc,gears.base.Mecha) and not pc.is_operational():
                                pc.free_pilots()
                                print(pc)
                                self.camp.party.remove(pc)
                    elif gdi.unicode == "F" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        for k in self.camp.faction_relations.keys():
                            if self.camp.is_unfavorable_to_pc(k):
                                print("{}: Enemy".format(k))
                            elif self.camp.is_favorable_to_pc(k):
                                print("{}: Ally".format(k))

                    elif gdi.unicode == "E" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        mymenu = pbge.rpgmenu.AlertMenu("Do you want to end this campaign?")
                        mymenu.add_item("Yes, time to quit.", True)
                        mymenu.add_item("No, I pressed the wrong key.", False)
                        if mymenu.query():
                            self.camp.eject()

                    elif gdi.unicode == "O" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        self.camp.version = "v0.100"

                    elif gdi.unicode == "T" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                        for card in self.camp.active_tarot_cards():
                            print(card.__class__.__name__)
                    elif gdi.unicode == "H":
                        fieldhq.FieldHQ.create_and_invoke(self.camp)
                    elif gdi.key == pygame.K_ESCAPE:
                        mymenu = configedit.PopupGameMenu()
                        mymenu(self)

                elif gdi.type == pygame.QUIT:
                    #self.camp.save(self.screen)
                    self.no_quit = False

                elif gdi.type == pygame.MOUSEBUTTONUP:
                    if gdi.button == 1:
                        self.click_left()
                    else:
                        pc = self.scene.get_main_actor(self.view.mouse_tile)
                        ExploMenu(self,pc)


        if not self.no_quit:
            self.camp.save()
        else:
            self.camp.check_trigger("END")

        current_explo = None
