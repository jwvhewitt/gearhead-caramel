from pbge import scenes
import pbge
import pygame
import gears
from gears import stats,geffects
import combat
import ghdialogue
import configedit
import invoker
import memobrowser
import fieldhq

# Commands should be callable objects which take the explorer and return a value.
# If untrue, the command stops.

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
        else:
            for pc in self.explo.camp.get_active_party():
                if pc.get_skill_library():
                    mymenu.add_item('{} Use Skill'.format(str(pc)),InvoMenuCall(self.explo,pc,None))
        mymenu.add_item('-----',None)
        # Check for waypoints.
        wayp_list = self.explo.camp.scene.get_bumpables(pbge.my_state.view.mouse_tile)
        for wayp in wayp_list:
            mymenu.add_item('Use {}'.format(str(wayp)),BumpToCall(self.explo,wayp))
        # Add the standard options.
        mymenu.add_item('Field HQ', FieldHQCall(self.explo.camp))
        mi = mymenu.query()
        if mi:
            mi()

class Explorer( object ):
    # The object which is exploration of a scene. OO just got existential.
    # Note that this does not get saved to disk, but instead gets created
    # anew when the game is loaded.
    def __init__( self, camp ):
        pbge.please_stand_by()
        self.camp = camp
        self.scene = camp.scene
        self.view = scenes.viewer.SceneView( camp.scene )
        self.mapcursor = pbge.image.Image('sys_mapcursor.png',64,64)
        self.time = 0

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


    def update_scene( self ):
        for npc in self.scene.contents:
            if hasattr(npc,"gear_up"):
                npc.gear_up()

    def keep_exploring( self ):
        return self.camp.first_active_pc() and self.no_quit and not pbge.my_state.got_quit and not self.camp.destination

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
                                                    on_success=True, on_failure=False, min_chance=10, max_chance=90)

    def update_npcs( self ):
        my_actors = self.scene.get_operational_actors()
        for npc in my_actors:
            npc.renew_power()
            if self.npc_inactive(npc):
                # First handle movement.

                # Next, check visibility to PC.
                npteam = self.scene.local_teams.get(npc)
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

    def update_enchantments(self):
        for thing in self.scene.contents:
            if hasattr(thing,'ench_list'):
                thing.ench_list.update(self.camp,thing)

    def go( self ):
        self.no_quit = True
        self.order = None

        self.update_scene()
        #self.scene.update_party_position(self.camp)

        # Clear the event queue, in case switching scenes took a long time.
        pygame.event.clear([pbge.TIMEREVENT,pygame.KEYDOWN])

        # Do one view first, just to prep the model map and mouse tile.
        self.view()
        pbge.my_state.do_flip()

        # Do a start trigger, unless we're in combat.
        if not self.camp.fight:
            self.camp.check_trigger( "START" )
            self.camp.check_trigger( "ENTER", self.scene )


        while self.keep_exploring():
            first_pc_pos=self.camp.first_active_pc().pos
            if self.camp.fight:
                self.camp.check_trigger( "STARTCOMBAT" )
                self.order = None
                self.camp.fight.go()
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
                self.view.overlays[ self.view.mouse_tile ] = (self.mapcursor,0)
                self.view()

                # Display info for this tile.
                my_info = self.scene.get_tile_info(self.view.mouse_tile)
                if my_info:
                    my_info.popup()

                pbge.my_state.do_flip()

                self.time += 1
                if hasattr(self.scene,"exploration_music"):
                    pbge.my_state.start_music(self.scene.exploration_music)

                if self.order:
                    if not self.order( self ):
                        self.order = None

                self.update_npcs()
                if self.time % 150 == 0:
                    self.update_enchantments()

            elif not self.order:
                # Set the mouse cursor on the map.
                #self.view.overlays[ self.view.mouse_tile ] = maps.OVERLAY_CURSOR

                if gdi.type == pygame.KEYDOWN:
                    if gdi.unicode == u"Q":
                        #self.camp.save(self.screen)
                        self.no_quit = False
                    elif gdi.unicode == u"c":
                        pc = self.camp.first_active_pc()
                        pbge.my_state.view.focus( pc.pos[0], pc.pos[1] )
                    elif gdi.unicode == u"X":
                        self.camp.save()
                    elif gdi.unicode == u"m":
                        memobrowser.MemoBrowser.browse(self.camp)
                    elif gdi.unicode == u"&":
                        for x in range(self.scene.width):
                            for y in range(self.scene.height):
                                self.scene.set_visible(x,y,True)
                    elif gdi.unicode == u"H":
                        fieldhq.FieldHQ.create_and_invoke(self.camp)
                    elif gdi.key == pygame.K_ESCAPE:
                        mymenu = configedit.PopupGameMenu()
                        mymenu(self)

                elif gdi.type == pygame.QUIT:
                    #self.camp.save(self.screen)
                    self.no_quit = False

                elif gdi.type == pygame.MOUSEBUTTONUP:
                    if gdi.button == 1:
                        # Left mouse button.
                        if ( self.view.mouse_tile != self.camp.pc.get_root().pos ) and self.scene.on_the_map( *self.view.mouse_tile ):
                            npc = self.view.modelmap.get(self.view.mouse_tile)
                            if npc and npc[0].is_operational() and self.scene.is_an_actor(npc[0]):
                                npteam = self.scene.local_teams.get(npc[0])
                                if npteam and self.scene.player_team.is_enemy(npteam):
                                    self.activate_foe(npc[0])
                                elif not isinstance(npc[0],gears.base.Prop):
                                    self.order = TalkTo( self, npc[0] )
                                    self.view.overlays.clear()
                            else:
                                self.order = MoveTo( self, self.view.mouse_tile )
                                self.view.overlays.clear()
                    else:
                        pc = self.scene.get_main_actor(self.view.mouse_tile)
                        ExploMenu(self,pc)

        if not self.no_quit:
            self.camp.check_trigger("END")
            self.camp.save()

