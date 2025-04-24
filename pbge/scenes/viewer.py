import collections
import weakref
from .. import my_state, anim_delay, WHITE, wrap_multi_line
from .. import util, image
import pygame
from . import waypoints, terrain
import random
import math

OVERLAY_ITEM = 0
OVERLAY_CURSOR = 1
OVERLAY_ATTACK = 2
OVERLAY_MOVETILE = 3
OVERLAY_AOE = 4
OVERLAY_CURRENTCHARA = 5
OVERLAY_HIDDEN = 6

SCROLL_STEP = 12

PARTY_INDICATOR_SPRITE = "sys_partyindicator.png"


class TextTicker(object):
    def __init__(self):
        self.text_images = list()
        self.counter = 0
        self.height = 20
        self.dy_off = 0

    def add(self, text, dy_off=0):
        pad = (self.counter // my_state.anim_font.get_linesize() - len(self.text_images))
        if pad > 0:
            for t in range(pad):
                self.text_images.append(None)
        newlines = wrap_multi_line(text, my_state.anim_font, 128)
        self.text_images += [my_state.anim_font.render(l, False, WHITE) for l in newlines]
        self.dy_off = dy_off

    def tick(self, view, x, y):
        self.counter += 1
        y -= self.counter - self.dy_off + 48
        for img in self.text_images[:4]:
            if img:
                mydest = img.get_rect(midbottom=(x, y))
                my_state.screen.blit(img, mydest)
            y += my_state.anim_font.get_linesize()
        if self.counter >= self.height:
            self.counter = self.height - my_state.anim_font.get_linesize()
            self.text_images.pop(0)

    def needs_deletion(self):
        return not self.text_images


class SceneView(object):
    def __init__(self, scene, postfx=None, cursor=None, party_indicator_spritename=PARTY_INDICATOR_SPRITE):
        self.overlays = dict()
        self.anim_list = list()
        self.anims = collections.defaultdict(list)
        self.tickers = collections.defaultdict(TextTicker)

        self.modelmap = collections.defaultdict(list)
        self.uppermap = collections.defaultdict(list)
        self.undermap = collections.defaultdict(list)
        self.waypointmap = collections.defaultdict(list)
        self.fieldmap = dict()
        self.modelsprite = weakref.WeakKeyDictionary()
        self.namedsprite = dict()
        self.darksprite = dict()

        self.randoms = list()
        seed = ord(scene.name[0])
        for t in range(1237):
            # seed = (( seed * 401 ) + 73 ) % 1024
            # self.randoms.append( seed )
            self.randoms.append(random.randint(1, 10000))

        self.scene = scene
        self._focus_x = 0
        self._focus_y = 0
        self.phase = 0

        # _mouse_tile contains the actual tile the mouse is hovering over. However, in most cases what we really want
        # is the location of the mouse cursor. Time to make a property!
        self._mouse_tile = (-1, -1)

        self.postfx = postfx

        self.cursor = cursor

        self.party_indicator = image.Image(party_indicator_spritename, self.TILE_WIDTH, self.TILE_HEIGHT,
                                           transparent=True)

        my_state.view = self

    @property
    def mouse_tile(self):
        if self.cursor:
            return self.cursor.x, self.cursor.y
        else:
            return self._mouse_tile

    def get_sprite(self, obj):
        """Return the sprite for the requested object. If no sprite exists, try to load one."""
        spr = self.modelsprite.get(obj)
        if not spr:
            spr = obj.get_sprite()
            self.modelsprite[obj] = spr
        return spr

    def get_named_sprite(self, fname, transparent=False, colors=None):
        """Return the requested sprite. If no sprite exists, try to load one."""
        if isinstance(colors, list):
            colors = tuple(colors)
        spr = self.namedsprite.get((fname, transparent, colors))
        if not spr:
            spr = image.Image(fname, self.TILE_WIDTH, self.TILE_WIDTH, color=colors, transparent=transparent)
            self.namedsprite[(fname, transparent, colors)] = spr
        return spr

    def get_terrain_sprite(self, fname, pos, transparent=False, colors=None):
        if colors:
            colors = tuple(colors)
        if self.scene.in_sight:
            if pos in self.scene.in_sight:
                return self.get_named_sprite(fname, transparent=transparent, colors=colors)
            else:
                spr = self.darksprite.get((fname, colors))
                if not spr:
                    spr = self.get_named_sprite(fname, transparent=transparent, colors=colors).copy()
                    spr.bitmap.set_at((0, 0), pygame.Color(0, 0, 255))
                    spr.bitmap.fill((190, 180, 200), special_flags=pygame.BLEND_MULT)
                    spr.bitmap.set_colorkey(spr.bitmap.get_at((0, 0)))
                    self.darksprite[(fname, colors)] = spr
                return spr
        else:
            return self.get_named_sprite(fname, transparent=transparent, colors=colors)

    def get_pseudo_random(self, x, y):
        # self.seed = ( 73 * x + 101 * y + x * y ) % 1024
        # return self.seed
        return self.randoms[(x + y * self.scene.width) % len(self.randoms)]

    def is_same_terrain(self, terr_to_check, terr_prototype):
        if terr_to_check:
            return issubclass(terr_to_check, terr_prototype)

    def calc_wall_score(self, x, y, terr):
        """Return bitmask of visible connected walls at x,y."""
        it = 0
        if self.is_same_terrain(self.scene.get_wall(x, y - 1), terr) and \
                not (self.scene.tile_blocks_vision(x - 1, y - 1) and self.scene.tile_blocks_vision(x - 1, y)
                     and self.scene.tile_blocks_vision(x + 1, y - 1) and self.scene.tile_blocks_vision(x + 1, y)):
            it += 2
        if self.is_same_terrain(self.scene.get_wall(x + 1, y), terr) and \
                not (self.scene.tile_blocks_vision(x + 1, y - 1) and self.scene.tile_blocks_vision(x, y - 1)
                     and self.scene.tile_blocks_vision(x + 1, y + 1) and self.scene.tile_blocks_vision(x, y + 1)):
            it += 4
        if self.is_same_terrain(self.scene.get_wall(x, y + 1), terr) and \
                not (self.scene.tile_blocks_vision(x - 1, y + 1) and self.scene.tile_blocks_vision(x - 1, y)
                     and self.scene.tile_blocks_vision(x + 1, y + 1) and self.scene.tile_blocks_vision(x + 1, y)):
            it += 8
        if self.is_same_terrain(self.scene.get_wall(x - 1, y), terr) and \
                not (self.scene.tile_blocks_vision(x - 1, y - 1) and self.scene.tile_blocks_vision(x, y - 1)
                     and self.scene.tile_blocks_vision(x - 1, y + 1) and self.scene.tile_blocks_vision(x, y + 1)):
            it += 1

        return it

    def calc_decor_score(self, x, y, terr):
        """Return bitmask of how many decors of type terrain border tile x,y."""
        it = 0
        if self.is_same_terrain(self.scene.get_decor(x, y - 1), terr) or not self.scene.on_the_map(x, y - 1):
            it += 2
        if self.is_same_terrain(self.scene.get_decor(x + 1, y), terr) or not self.scene.on_the_map(x + 1, y):
            it += 4
        if self.is_same_terrain(self.scene.get_decor(x, y + 1), terr) or not self.scene.on_the_map(x, y + 1):
            it += 8
        if self.is_same_terrain(self.scene.get_decor(x - 1, y), terr) or not self.scene.on_the_map(x - 1, y):
            it += 1

        return it

    def is_border_wall(self, x, y):
        """Return True if this loc is a wall or off the map."""
        return self.scene.get_wall(x, y) or not self.scene.on_the_map(x, y)

    def calc_border_score(self, x, y):
        """Return the wall border frame for this tile."""
        it = 0
        if self.is_border_wall(x - 1, y - 1) and self.is_border_wall(x - 1, y) and self.is_border_wall(x, y - 1):
            it += 1
        if self.is_border_wall(x + 1, y - 1) and self.is_border_wall(x + 1, y) and self.is_border_wall(x, y - 1):
            it += 2
        if self.is_border_wall(x + 1, y + 1) and self.is_border_wall(x + 1, y) and self.is_border_wall(x, y + 1):
            it += 4
        if self.is_border_wall(x - 1, y + 1) and self.is_border_wall(x - 1, y) and self.is_border_wall(x, y + 1):
            it += 8
        return it

    def space_to_south(self, x, y):
        """Return True if no wall in tile to south."""
        return not self.scene.get_wall(x, y + 1)

    def space_or_door_to_south(self, x, y):
        """Return True if no wall in tile to south."""
        wall = self.scene.get_wall(x, y + 1)
        return not wall or issubclass(wall, terrain.DoorTerrain)

    def space_nearby(self, x, y):
        """Return True if a tile without a wall is adjacent."""
        found_space = False
        for d in self.scene.DELTA8:
            if not self.scene.get_wall(x + d[0], y + d[1]):
                found_space = True
                break
        return found_space

    TILE_HEIGHT = 64
    TILE_WIDTH = 64
    # Half tile width and half tile height
    HTW = 32
    HTH = 16

    def relative_x(self, x, y):
        """Return the relative x position of this tile, ignoring offset."""
        return int((x * float(self.HTW)) - (y * float(self.HTW)))

    def relative_y(self, x, y):
        """Return the relative y position of this tile, ignoring offset."""
        return int(y * float(self.HTH) + x * float(self.HTH))

    def screen_coords(self, x, y, extra_x_offset=0, extra_y_offset=0):
        # Should point to the upper (northwest) corner of an isometric tile.
        x_off, y_off = self.screen_offset()
        return (self.relative_x(x, y) + x_off + extra_x_offset,
                self.relative_y(x, y) + y_off + extra_y_offset)

    def foot_coords(self, x, y):
        # Models get moved down by half tile height so they appear in the center of a tile.
        return self.screen_coords(x, y, extra_y_offset=self.HTH)

    def on_the_screen(self, x, y):
        screen_area = my_state.screen.get_rect()
        return screen_area.collidepoint(self.screen_coords(x, y))

    def screen_offset(self):
        return (my_state.screen.get_width() // 2 - self.relative_x(self._focus_x, self._focus_y),
                my_state.screen.get_height() // 2 - self.relative_y(self._focus_x, self._focus_y) + self.HTH)

    def map_x(self, sx, sy, return_int=True):
        """Return the map x row for the given screen coordinates."""
        x_off, y_off = self.screen_offset()

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        # Calculate the x position of map_x tile 0 at ry.
        ox = float(-ry * self.HTW) / float(self.HTH)

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if rx - ox < 0:
                ox += self.HTW * 2
            return int(math.floor((rx - ox) / (self.HTW * 2)))
        else:
            return (rx - ox) / (self.HTW * 2)

    def map_y(self, sx, sy, return_int=True):
        """Return the map y row for the given screen coordinates."""
        x_off, y_off = self.screen_offset()

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        oy = float(rx * self.HTH) / float(self.HTW)

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if ry - oy < 0:
                oy += self.HTH * 2
            return int(math.floor((ry - oy) / (self.HTH * 2)))
        else:
            return (ry - oy) / (self.HTH * 2)

    def check_origin(self):
        """Make sure the offset point is within map boundaries."""
        self._focus_x, self._focus_y = self.scene.clamp_pos((self._focus_x, self._focus_y))

    def focus(self, x, y):
        self._focus_x, self._focus_y = self.scene.clamp_pos((x, y))

    def regenerate_avatars(self, models):
        """Regenerate the avatars for the listed models."""
        for m in models:
            self.modelsprite[m] = m.get_sprite()

    def draw_caption(self, center, txt):
        myimage = my_state.tiny_font.render(txt, True, (240, 240, 240))
        mydest = myimage.get_rect(center=center)
        myfill = pygame.Rect(mydest.x - 2, mydest.y - 1, mydest.width + 4, mydest.height + 2)
        my_state.screen.fill((36, 37, 36), myfill)
        my_state.screen.blit(myimage, mydest)

    def handle_anim_sequence(self, record_anim=False):
        # Disable widgets while animation playing.
        push_widget_state = my_state.widgets_active
        my_state.widgets_active = False

        tick = 0
        if record_anim:
            self.anims.clear()
            self()
            my_state.do_flip()
            pygame.image.save(my_state.screen, util.user_dir("anim_{:0>3}.png".format(tick)))
            tick += 1

        while self.anim_list or self.tickers:
            should_delay = False
            self.anims.clear()
            for a in list(self.anim_list):
                if a.needs_deletion:
                    self.anim_list.remove(a)
                    self.anim_list += a.children
                else:
                    should_delay = True
                    a.update(self)
            if should_delay or self.tickers:
                self()
                my_state.do_flip()
            if record_anim:
                pygame.image.save(my_state.screen, util.user_dir("anim_{:0>3}.png".format(tick)))

            anim_delay()
            tick += 1
        self.anims.clear()

        # Restore the widgets.
        my_state.widgets_active = push_widget_state

        # Update any placable things that need updates.
        for thing in self.scene.contents:
            if hasattr(thing, 'update_graphics'):
                thing.update_graphics()

    def play_anims(self, *args):
        self.anim_list += args
        self.handle_anim_sequence()

    def pos_to_key(self, pos):
        # Convert the x,y coordinates to a model_map key...
        if pos:
            x, y = pos
            return (int(round(x)), int(round(y)))
        else:
            return "IT'S NOT ON THE MAP ALRIGHT?!"

    def model_depth(self, model):
        return self.relative_y(model.pos[0], model.pos[1]), getattr(model, "sort_priority", 0)

    def show_model_name(self, model, sx, sy):
        myname = my_state.small_font.render(str(model), True, WHITE)
        namedest = myname.get_rect(midbottom=(sx, sy - 60))
        my_state.screen.fill((0, 0, 0), namedest.inflate(2, 2))
        my_state.screen.blit(myname, namedest)

    CAMERA_MOVES = (
        (-0.5, 0), (-0.25, -0.25), (0, -0.5),
        (-0.25, 0.25), (0, 0), (0.25, -0.25),
        (0, 0.5), (0.25, 0.25), (0.5, 0)
    )

    SCROLL_AREA = 15

    def update_camera(self, screen_area, mouse_x, mouse_y):
        # Check for map scrolling, depending on mouse position.
        if mouse_x < self.SCROLL_AREA:
            dx = 0
        elif mouse_x > (screen_area.right - self.SCROLL_AREA):
            dx = 2
        else:
            dx = 1

        if mouse_y < self.SCROLL_AREA:
            dy = 0
        elif mouse_y > (screen_area.bottom - self.SCROLL_AREA):
            dy = 2
        else:
            dy = 1

        nux, nuy = self.CAMERA_MOVES[dx + dy * 3]
        self.focus(float(self._focus_x) + nux, float(self._focus_y) + nuy)

    def get_floor_borders(self, x0, y0, center_floor):
        # Return a list of floor terrain with borders to draw on this tile, in order of border_priority
        my_bordered_floors = list()
        for dx, dy in self.scene.DELTA8:
            myfloor = self.scene.get_floor(x0 + dx, y0 + dy)
            if myfloor and myfloor.border and myfloor.border_priority > center_floor.border_priority and myfloor not in my_bordered_floors:
                my_bordered_floors.append(myfloor)
        my_bordered_floors.sort(key=lambda f: f.border_priority)
        return my_bordered_floors

    def _get_horizontal_line(self, x0, y0, line_number, visible_area):
        mylist = list()
        x = x0 + line_number // 2
        y = y0 + (line_number + 1) // 2

        if self.screen_coords(x, y)[1] > visible_area.bottom:
            return None

        while self.screen_coords(x, y)[0] < visible_area.right:
            if self.scene.on_the_map(x, y):
                mylist.append((x, y))
            x += 1
            y -= 1
        return mylist

    def _get_visible_area(self):
        # The visible area describes the region of the map we need to draw.
        # It is bigger than the physical screen
        # because we probably have to draw cells that are not fully on the map.
        visible_area = my_state.screen.get_rect()

        # - temp disabled inflate op. (web ctx issues)20
        visible_area.inflate_ip(self.HTW * 2, self.HTH * 2)
        visible_area.h += self.HTH * 2

        return visible_area

    def __call__(self):
        """Draws this mapview to the provided screen."""
        screen_area = my_state.screen.get_rect()
        mouse_x, mouse_y = my_state.mouse_pos
        my_state.screen.fill((0, 0, 0))
        visible_area = self._get_visible_area()

        # Check for map scrolling, depending on mouse position.
        if util.config.getboolean("GENERAL", "mouse_scroll_at_map_edges"):
            self.update_camera(screen_area, mouse_x, mouse_y)

        x, y = self.map_x(0, 0) - 2, self.map_y(0, 0) - 1
        x0, y0 = x, y
        keep_going = True
        line_number = 1

        indicate_lance_tiles = util.config.getboolean("GENERAL", "indicate_lance_tiles")

        # Record all of the scene contents for display when their tile comes up.
        self.modelmap.clear()
        self.uppermap.clear()
        self.undermap.clear()
        self.waypointmap.clear()
        for m in self.scene.contents:
            if hasattr(m, 'render') and self.pos_to_key(m.pos) in self.scene.in_sight:
                d_pos = self.pos_to_key(m.pos)
                if not hasattr(m, "hidden") or not m.hidden:
                    self.modelmap[d_pos].append(m)
                if self.scene.model_altitude(m, *d_pos) >= 0:
                    self.uppermap[d_pos].append(m)
                else:
                    self.undermap[d_pos].append(m)
            elif isinstance(m, waypoints.Waypoint) and m.name:
                # Nameless waypoints are hidden. They probably serve some
                # utility purpose, but the player doesn't have to know they're
                # there.
                self.waypointmap[m.pos].append(m)

        show_names = util.config.getboolean("GENERAL", "names_above_heads")
        line_cache = list()

        while keep_going:
            # In order to allow smooth sub-tile movement of stuff, we have
            # to draw everything in a particular order. First, do the predrawing
            # of a tile. Next, draw the models and other stuff in the tile
            # behind this one. When we reach the bottom of the screen, check
            # the next two rows of tiles anyway to finish drawing the models
            # and walls. It's completely nuts! But this is the kind of thing
            # you need to do if you don't have a Z-Buffer. Kinda makes me want
            # to reconsider that resolution to never again use OpenGL.
            nuline = self._get_horizontal_line(x0, y0, line_number, visible_area)
            line_cache.append(nuline)
            current_line = len(line_cache) - 1

            if line_cache[current_line]:
                for x, y in line_cache[current_line]:
                    if self.scene.get_visible(x, y):
                        dest = pygame.Rect(0, 0, self.TILE_WIDTH, self.TILE_WIDTH)
                        mpos = self.screen_coords(x, y)
                        dest.center = mpos

                        self.scene._map[x][y].render_bottom(dest, self, x, y)

                        mlist = self.undermap.get((x, y))
                        if mlist:
                            if len(mlist) > 1:
                                mlist.sort(key=self.model_depth)
                            for m in mlist:
                                mx, my = m.pos
                                footpos = self.foot_coords(mx, my)
                                y_alt = self.scene.model_altitude(m, x, y)
                                mdest = pygame.Rect(0, 0, self.TILE_WIDTH, self.TILE_HEIGHT)
                                mdest.midbottom = footpos
                                mdest.y -= y_alt
                                m.render(mdest, self)
                                if show_names:
                                    self.show_model_name(m, mdest.centerx, mdest.top)

                        self.scene._map[x][y].render_biddle(dest, self, x, y)

                        # Draw any floor borders at this point.
                        myfloor = self.scene.get_floor(x, y)
                        if myfloor:
                            borders = self.get_floor_borders(x, y, myfloor)
                            for b in borders:
                                b.border.render(dest, self, x, y)

                        self.scene._map[x][y].render_middle(dest, self, x, y)


            if current_line > 1 and line_cache[current_line - 2]:
                # After drawing the terrain last time, draw any objects in the previous cell.
                for x, y in line_cache[current_line - 2]:
                    if self.scene.get_visible(x, y):
                        spos = self.screen_coords(x, y)
                        dest = pygame.Rect(0, 0, self.TILE_WIDTH, self.TILE_WIDTH)
                        dest.center = spos
                        self.scene._map[x][y].render_top(dest, self, x, y)

            if current_line > 0 and line_cache[current_line - 1]:
                # After drawing the terrain last time, draw any objects in the previous cell.
                for x, y in line_cache[current_line - 1]:
                    if self.scene.get_visible(x, y):
                        spos = self.screen_coords(x, y)
                        dest = pygame.Rect(0, 0, self.TILE_WIDTH, self.TILE_WIDTH)
                        dest.center = spos

                        if self.overlays.get((x, y), None):
                            o_dest = dest.copy()
                            if self.scene.tile_altitude(x, y) > 0:
                                o_dest.y -= self.scene.tile_altitude(x, y)
                            o_sprite, o_frame = self.overlays[(x, y)]
                            o_sprite.render(o_dest, o_frame)

                        elif indicate_lance_tiles:
                            tile_models = self.modelmap.get((x, y))
                            if tile_models and any(
                                    self.scene.local_teams.get(m) is self.scene.player_team for m in tile_models):
                                o_dest = dest.copy()
                                if self.scene.tile_altitude(x, y) > 0:
                                    o_dest.y -= self.scene.tile_altitude(x, y)
                                self.party_indicator.render(o_dest, 0)

                        if self.cursor and self.cursor.x == x and self.cursor.y == y:
                            c_dest = dest.copy()
                            if self.scene.tile_altitude(x, y) > 0:
                                c_dest.y -= self.scene.tile_altitude(x, y)
                            self.cursor.render(c_dest)

                        mlist = self.uppermap.get((x, y))
                        if mlist:
                            if len(mlist) > 1:
                                mlist.sort(key=self.model_depth)
                            for m in mlist:
                                mx, my = m.pos
                                footpos = self.foot_coords(mx, my)
                                y_alt = self.scene.model_altitude(m, x, y)
                                mdest = pygame.Rect(0, 0, self.TILE_WIDTH, self.TILE_HEIGHT)
                                mdest.midbottom = footpos
                                mdest.y -= y_alt
                                m.render(mdest, self)
                                if show_names:
                                    self.show_model_name(m, mdest.centerx, mdest.top)

                        self.scene._map[x][y].render_top(dest, self, x, y)

                        mlist = self.anims.get((x, y))
                        if mlist:
                            if len(mlist) > 1:
                                mlist.sort(key=self.model_depth)
                            for m in mlist:
                                # mx, my = m.pos
                                sx, sy = self.foot_coords(*m.pos)
                                m.render((sx, sy), self)


            elif len(line_cache) > 2 and line_cache[current_line - 2] is None:
                keep_going = False

            line_number += 1

        for k, v in list(self.tickers.items()):
            x, y = self.foot_coords(*k)
            if v.needs_deletion():
                del self.tickers[k]
            elif x >= 0 and x <= my_state.screen.get_width() and y >= 0 and y <= my_state.screen.get_height():
                v.tick(self, x, y)
            else:
                del self.tickers[k]

        self.phase = (self.phase + 1) % 600
        self._mouse_tile = (self.map_x(mouse_x, mouse_y), self.map_y(mouse_x, mouse_y))

        if self.postfx:
            self.postfx()

    def check_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if my_state.is_key_for_action(ev, "scroll_map_north"):
                self.focus(self._focus_x, self._focus_y - 1)
            elif my_state.is_key_for_action(ev, "scroll_map_west"):
                self.focus(self._focus_x - 1, self._focus_y)
            elif my_state.is_key_for_action(ev, "scroll_map_south"):
                self.focus(self._focus_x, self._focus_y + 1)
            elif my_state.is_key_for_action(ev, "scroll_map_east"):
                self.focus(self._focus_x + 1, self._focus_y)

        if self.cursor:
            self.cursor.update(self, ev)
