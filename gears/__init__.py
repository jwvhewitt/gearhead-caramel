import pbge
import random

import base
import calibre
import damage
import materials
import scale
import stats
import geffects
import info
import color
import attackattributes
import personality
import factions
import tags
import selector
import enchantments
import programs
import portraits
import genderobj

import inspect
import os
import glob
from color import ALL_COLORS, CLOTHING_COLORS, SKIN_COLORS, HAIR_COLORS, MECHA_COLORS, DETAIL_COLORS, METAL_COLORS, \
    random_character_colors, random_mecha_colors
import eggs
import relationships

GEAR_TYPES = dict()
SINGLETON_TYPES = dict()


def harvest(mod, subclass_of, dict_to_add_to, exclude_these):
    for name in dir(mod):
        o = getattr(mod, name)
        if inspect.isclass(o) and issubclass(o, subclass_of) and o not in exclude_these:
            dict_to_add_to[o.__name__] = o


harvest(base, base.BaseGear, GEAR_TYPES, (base.BaseGear, base.MovementSystem, base.Weapon, base.Usable))
harvest(scale, scale.MechaScale, SINGLETON_TYPES, ())
harvest(base, base.ModuleForm, SINGLETON_TYPES, (base.ModuleForm,))
harvest(materials, materials.Material, SINGLETON_TYPES, (materials.Material,))
harvest(calibre, calibre.BaseCalibre, SINGLETON_TYPES, (calibre.BaseCalibre,))
harvest(base, base.MT_Battroid, SINGLETON_TYPES, ())
SINGLETON_TYPES['None'] = None
harvest(stats, stats.Stat, SINGLETON_TYPES, (stats.Stat,))
harvest(stats, stats.Skill, SINGLETON_TYPES, (stats.Skill,))
harvest(geffects, pbge.scenes.animobs.AnimOb, SINGLETON_TYPES, ())
harvest(attackattributes, pbge.Singleton, SINGLETON_TYPES, ())
harvest(factions, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,factions.Faction))
harvest(tags, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))
harvest(programs, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))
harvest(personality, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))


def harvest_color(dict_to_add_to):
    for name in dir(color):
        o = getattr(color, name)
        if inspect.isclass(o) and issubclass(o, color.GHGradient) and o is not color.GHGradient:
            dict_to_add_to[o.__name__] = o
            ALL_COLORS.append(o)
            if color.CLOTHING in o.SETS:
                CLOTHING_COLORS.append(o)
            if color.SKIN in o.SETS:
                SKIN_COLORS.append(o)
            if color.HAIR in o.SETS:
                HAIR_COLORS.append(o)
            if color.MECHA in o.SETS:
                MECHA_COLORS.append(o)
            if color.DETAILS in o.SETS:
                DETAIL_COLORS.append(o)
            if color.METAL in o.SETS:
                METAL_COLORS.append(o)
    ALL_COLORS.sort(key=lambda c: c.FAMILY)

import oldghloader
import jobs

harvest_color(SINGLETON_TYPES)
SINGLETON_TYPES.update(jobs.ALL_JOBS)
jobs.SINGLETON_TYPES = SINGLETON_TYPES

import colorstyle

def harvest_styles(mod):
    for name in dir(mod):
        o = getattr(mod, name)
        if isinstance(o,colorstyle.Style):
            colorstyle.ALL_STYLES.append(o)

harvest_styles(colorstyle)


class MetroData(object):
    def __init__(self):
        self.tarot = pbge.container.ContainerDict()
        self.scripts = pbge.container.ContainerList(owner=self)

class GearHeadScene(pbge.scenes.Scene):
    def __init__(self, width=128, height=128, name="", player_team=None, civilian_team=None, faction=None,
                 scale=scale.MechaScale, environment=tags.GroundEnv, attributes=(), is_metro=False):
        # A metro scene is one which will contain plots and tarot cards local to it and its children.
        #   Generally it should be placed at root, as a direct child of the GHCampaign.
        super(GearHeadScene, self).__init__(width, height, name, player_team)
        self.civilian_team = civilian_team
        self.faction = faction
        self.scale = scale
        self.environment = environment
        self.script_rooms = list()
        self.attributes = set(attributes)
        if is_metro:
            self.metrodat = MetroData()

    def get_metro_scene(self):
        myscene = self
        while hasattr(myscene, "container") and myscene.container and not hasattr(myscene, "metrodat"):
            myscene = myscene.container.owner
        if hasattr(myscene, "metrodat"):
            return myscene

    @staticmethod
    def is_an_actor(model):
        return isinstance(model, (base.Mecha, base.Being, base.Prop, base.Squad))

    def get_actors(self, pos):
        return [a for a in self.contents if (self.is_an_actor(a) and (a.pos == pos))]

    def get_operational_actors(self, pos=None):
        return [a for a in self.contents if
                (self.is_an_actor(a) and a.is_operational() and (pos is None or a.pos == pos))]

    def get_main_actor(self, pos):
        # In theory, a tile should only ever have one operational actor
        # in it. Check the tile, return the first operational actor found.
        mylist = self.get_operational_actors(pos)
        if mylist:
            return mylist[0]

    def get_blocked_tiles(self):
        return {a.pos for a in self.contents if (self.is_an_actor(a) and a.is_operational())}

    def are_hostile(self, a, b):
        if a and b:
            team_a = self.local_teams.get(a)
            return team_a and team_a.is_enemy(self.local_teams.get(b))

    def are_allies(self, a, b):
        if a and b:
            team_a = self.local_teams.get(a)
            return team_a and team_a.is_ally(self.local_teams.get(b))

    def update_party_position(self, camp):
        self.in_sight = set()
        first = True
        for pc in camp.party:
            if pc.is_operational() and pc in self.contents:
                self.in_sight |= pbge.scenes.pfov.PCPointOfView(self, pc.pos[0], pc.pos[1],
                                                                pc.get_sensor_range(self.scale)).tiles
                if first and self.script_rooms:
                    # Check the position of this PC against the script rooms.
                    for r in self.script_rooms:
                        if r.area.collidepoint(*pc.pos):
                            camp.check_trigger("ENTER", r)
                    first = False
        camp.check_trigger("PCMOVE")

    def get_tile_info(self, pos):
        """Return an InfoPanel for the contents of this tile, if appropriate."""
        if self.get_visible(*pos) and pos in self.in_sight:
            # mmecha = pbge.my_state.view.modelmap.get(pos)
            mmecha = self.get_main_actor(pos)
            if mmecha and (self.local_teams.get(mmecha) == self.player_team or not mmecha.hidden):
                return info.get_status_display(model=mmecha)
            elif pbge.my_state.view.waypointmap.get(pos):
                wp = pbge.my_state.view.waypointmap.get(pos)
                return info.ListDisplay(items=wp)

    def place_actor(self, actor, x0, y0, team=None):
        entry_points = pbge.scenes.pfov.WalkReach(self, x0, y0, 5, True).tiles
        entry_points = entry_points.difference(self.get_blocked_tiles())
        entry_points = list(entry_points)
        if entry_points:
            actor.place(self, random.choice(entry_points), team)
        else:
            actor.place(self, (x0, y0), team)
        actor.gear_up()


class GearHeadCampaign(pbge.campaign.Campaign):
    fight = None
    pc = None

    def __init__(self, name="GHC Campaign", explo_class=None, year=158, egg=None, num_lancemates=3, faction_relations=factions.DEFAULT_FACTION_DICT_NT158, convoborder="dzd_convoborder.png"):
        super(GearHeadCampaign, self).__init__(name, explo_class)
        self.tarot = pbge.container.ContainerDict()
        self.year = year
        self.num_lancemates = num_lancemates
        self.faction_relations = faction_relations.copy()
        self.history = list()
        self.convoborder = convoborder

        # Some containers for characters who have been either incapacitated or killed.
        # It's the current scenario's responsibility to do something with these lists
        # at an appropriate time.
        self.incapacitated_party = list()
        self.dead_party = list()

        if egg:
            self.egg = egg
            self.party = [egg.pc,]
            if egg.mecha:
                self.party.append(egg.mecha)
                egg.mecha.pilot = egg.pc
            self.pc = egg.pc

    def are_enemy_factions(self,fac1,fac2):
        fac1 = fac1.get_faction_tag()
        fac2 = fac2.get_faction_tag()
        fac1_rel = self.faction_relations.get(fac1)
        fac2_rel = self.faction_relations.get(fac2)
        return (fac1_rel and fac2 in fac1_rel.enemies) or (fac2_rel and fac1 in fac2_rel.enemies)

    def are_ally_factions(self,fac1,fac2):
        fac1 = fac1.get_faction_tag()
        fac2 = fac2.get_faction_tag()
        fac1_rel = self.faction_relations.get(fac1)
        fac2_rel = self.faction_relations.get(fac2)
        return (fac1 is fac2) or (fac1_rel and fac2 in fac1_rel.allies) or (fac2_rel and fac1 in fac2_rel.allies)

    def active_plots(self):
        for p in super(GearHeadCampaign, self).active_plots():
            yield p
        for p in self.tarot.values():
            yield p
        myscene = self.scene.get_metro_scene()
        if myscene:
            for p in myscene.metrodat.scripts:
                yield p
            for p in myscene.metrodat.tarot.values():
                yield p

    def active_tarot_cards(self):
        for p in self.tarot.values():
            yield p
        myscene = self.scene.get_metro_scene()
        if myscene:
            for p in myscene.metrodat.tarot.values():
                yield p

    def first_active_pc(self):
        # The first active PC is the first PC in the party list who is
        # both operational and on the map.
        flp = None
        for pc in self.party:
            if pc.is_operational() and pc in self.scene.contents:
                flp = pc
                break
        return flp

    def get_active_lancemates(self):
        # Return a list of lancemates currently on the map.
        return [pc for pc in self.scene.contents if
                pc in self.party and pc.is_operational() and pc.get_pilot() is not self.pc]

    def get_active_party(self):
        # Return a list of lancemates currently on the map.
        return [pc for pc in self.scene.contents if pc in self.party and pc.is_operational()]

    def can_add_lancemate(self):
        lancemates = [pc for pc in self.party if isinstance(pc,base.Character) and pc is not self.pc]
        return len(lancemates) < self.num_lancemates

    def get_party_skill(self, stat_id, skill_id):
        return max([pc.get_skill_score(stat_id, skill_id) for pc in self.get_active_party()] + [0])

    def get_pc_mecha(self,pc):
        meklist = [mek for mek in self.party if isinstance(mek,base.Mecha) and mek.pilot is pc]
        if meklist:
            if len(meklist) > 1:
                for mek in meklist[1:]:
                    mek.pilot = None
            return meklist[0]

    def assign_pilot_to_mecha(self,pc,mek):
        # either mek or pc can be None, to clear a mecha's assigned pilot.
        for m in self.party:
            if isinstance(m, base.Mecha) and m.pilot is pc:
                m.pilot = None
        if mek:
            mek.pilot = pc

    def keep_playing_campaign(self):
        return self.pc.is_not_destroyed()

    def play(self):
        super(GearHeadCampaign, self).play()
        if self.pc in self.dead_party:
            pbge.alert("Game Over",font=pbge.my_state.hugefont)
            self.delete_save_file()

    def get_usable_party(self,map_scale):
        usable_party = list()
        for pc in self.party:
            if pc.is_not_destroyed() and pc.scale == map_scale:
                if hasattr(pc, "pilot"):
                    if pc.pilot and pc.pilot in self.party and pc.pilot.is_operational():
                        pc.load_pilot(pc.pilot)
                        usable_party.append(pc)
                elif pc.is_operational():
                    usable_party.append(pc)
        if not usable_party:
            usable_party.append(self.pc)
        return usable_party

    def choose_party(self):
        # Generally, if we're entering a mecha scale scene, send in the mecha.
        usable_party = list()
        if self.scene.scale is scale.WorldScale:
            mysquad = base.Squad(name="Party")
            mysquad.sub_com += self.get_usable_party(scale.MechaScale)
            usable_party.append(mysquad)
            self.party.append(mysquad)
        else:
            usable_party += self.get_usable_party(self.scene.scale)
        return usable_party

    def place_party(self):
        """Stick the party close to the waypoint."""
        x0, y0 = self.entrance.pos
        entry_points = pbge.scenes.pfov.WalkReach(self.scene, x0, y0, 3, True).tiles
        entry_points = entry_points.difference(self.scene.get_blocked_tiles())
        entry_points = list(entry_points)
        for pc in self.choose_party():
            if pc.is_operational():
                if entry_points:
                    pos = random.choice(entry_points)
                    entry_points.remove(pos)
                else:
                    pos = self.entrance.pos
                pc.place(self.scene, pos, self.scene.player_team)
                pc.gear_up()
                #pbge.scenes.pfov.PCPointOfView(self.scene, pos[0], pos[1], pc.get_sensor_range(self.scene.scale))
        self.scene.update_party_position(self)

    def bring_out_your_dead(self):
        for pc in list(self.party):
            if pc.is_destroyed():
                self.party.remove(pc)
                skill = self.get_party_skill(stats.Knowledge,pc.material.repair_type) + 50 - pc.get_total_damage_status()
                if pc is self.pc:
                    if pbge.util.config.getboolean("DIFFICULTY","pc_can_die") and random.randint(1,100) > skill:
                        self.dead_party.append(pc)
                    else:
                        self.incapacitated_party.append(pc)
                elif isinstance(pc,base.Character):
                    if pbge.util.config.getboolean("DIFFICULTY","lancemates_can_die") and random.randint(1,100) > skill:
                        self.dead_party.append(pc)
                    else:
                        self.incapacitated_party.append(pc)
                elif random.randint(1,100) <= skill or not pbge.util.config.getboolean("DIFFICULTY","mecha_can_die"):
                    self.incapacitated_party.append(pc)

    def remove_party_from_scene(self):
        # Check for dead and/or incapacitated characters first.
        self.bring_out_your_dead()

        # Now remove the party from the map.
        for pc in list(self.party + self.dead_party + self.incapacitated_party):
            pc.pos = None
            if pc in self.scene.contents:
                self.scene.contents.remove(pc)
            if hasattr(pc, "free_pilots"):
                pc.free_pilots()
            if isinstance(pc,base.Squad):
                self.party.remove(pc)

    # Gonna set up the credits as a property.
    def _get_credits(self):
        return self.egg.credits

    def _set_credits(self,nuval):
        self.egg.credits = max(nuval,0)

    def _del_credits(self):
        self.egg.credits = 0

    credits = property(_get_credits,_set_credits,_del_credits)

    # Gonna set up the renown as a property.
    def _get_renown(self):
        return self.pc.renown

    def _set_renown(self,nuval):
        self.pc.renown = min(max(nuval,-100),100)

    def _del_renown(self):
        self.pc.renown = 0

    renown = property(_get_renown,_set_renown,_del_renown)

    def dole_xp(self,amount,type=base.Being.TOTAL_XP):
        for pc in self.party:
            if hasattr(pc,"experience"):
                pc.experience[type] += amount

    def totally_restore_party(self):
        # Restore the party to health, returning the cost of doing so.
        repair_total = 0
        for pc in self.party + self.incapacitated_party:
            rcdict = pc.get_repair_cost()
            pc.wipe_damage()
            repair_total += sum([v for k,v in rcdict.iteritems()])
            if hasattr(pc, "mp_spent"):
                pc.mp_spent = 0
            if hasattr(pc, "sp_spent"):
                pc.sp_spent = 0

            for part in pc.descendants():
                if hasattr(part,"get_reload_cost"):
                    repair_total += part.get_reload_cost()
                    part.spent = 0
        return repair_total


# Why did I create this complicated regular expression to parse lines of
# the form "a = b"? I guess I didn't know about string.partition at the time.
# Anyhow, I'm leaving this here as a comment to remind me of the dangers of
# overengineering. Also in case I ever need it again because I don't really
# remember how regular expressions work and this looks complicated as heck.
# DICT_UNPACKER = re.compile( r'["\']?(\w+)["\']?\s?=\s?([\w"\']+)' )


class ProtoGear(object):
    """Used by the loader to hold gear definitions before creating the actual gear."""

    def __init__(self, gclass):
        self.gclass = gclass
        self.gparam = dict()
        self.sub_com = list()
        self.inv_com = list()


class Loader(object):
    def __init__(self, fname):
        self.fname = fname

    def process_list(self, string):
        # This string describes a list. There may be additional lists in
        # the list. Deal with that.
        current_list = None
        stack = []
        start_token = -1
        for i, c in enumerate(string):
            if c in '([':
                # Begin a new list
                nulist = list()
                if current_list is not None:
                    stack.append(current_list)
                    current_list.append(nulist)
                current_list = nulist
                start_token = i + 1
            elif c in ')]':
                # Pop out to previous list
                if start_token < i:
                    toke = string[start_token:i]
                    current_list.append(self.string_to_object(toke))
                if stack:
                    current_list = stack.pop()
                start_token = i + 1
            elif c == ',':
                # Store the current item in the list
                toke = string[start_token:i]
                if toke:
                    current_list.append(self.string_to_object(toke))
                start_token = i + 1
        return current_list

    def string_to_object(self, string):
        # Given a string, return the game object it represents.
        rawval = string.strip()
        if rawval:
            if rawval[0] in ('"', "'"):
                # This is a literal string. Get rid of the quotes.
                truval = rawval.strip('"\'')
            elif rawval[0] in '([':
                # Happy Happy Joy Joy it's a fucking list
                truval = self.process_list(rawval)
            elif rawval.isdigit():
                # This is presumably a number. Convert.
                truval = int(rawval)

            elif rawval in SINGLETON_TYPES:
                # This is a named constant of some type.
                truval = SINGLETON_TYPES[rawval]
            else:
                # This is a string. Leave it alone.
                truval = rawval
            return truval

    def process_dict(self, dict_desc):
        mydict = dict()
        # Is this really the best way to get rid of the brackets?
        # Probably not. Somebody Python this up, please.
        dict_desc = dict_desc.replace('{', '')
        dict_desc = dict_desc.replace('}', '')
        for line in dict_desc.split(','):
            a, b, c = line.partition('=')
            k = self.string_to_object(a)
            v = self.string_to_object(c)
            if k and v:
                mydict[k] = v
        return mydict

    def load_list(self, g_file):
        """Given an open file, load the text and return the list of proto-gears"""
        # If it is a command, do that command.
        # If it has an =, add it to the dict
        # Otherwise, check to see if it's a Gear
        masterlist = list()
        current_gear = None
        keep_going = True

        while keep_going:
            rawline = g_file.readline()
            line = rawline.strip()
            if len(line) > 0:
                if line[0] == "#":
                    # This line is a comment. Ignore.
                    pass

                elif "{" in line:
                    # This is the start of a dictionary.
                    # Load the rest of the dict from the file,
                    # then pass it to the dictionary expander.
                    a, b, c = line.partition('=')
                    k = self.string_to_object(a)
                    my_dict_lines = [c, ]
                    while "}" not in my_dict_lines[-1]:
                        nuline = g_file.readline()
                        if nuline:
                            my_dict_lines.append(nuline)
                        else:
                            break
                    v = self.process_dict(' '.join(my_dict_lines))
                    if k and v:
                        current_gear.gparam[k] = v

                elif "=" in line:
                    # This is a dict line. Add to the current_dict.
                    a, b, c = line.partition('=')
                    k = self.string_to_object(a)
                    v = self.string_to_object(c)
                    if k and v:
                        current_gear.gparam[k] = v

                elif line in GEAR_TYPES:
                    # This is a new gear.
                    current_gear = ProtoGear(GEAR_TYPES[line])
                    masterlist.append(current_gear)

                elif line == "SUB":
                    # This is a SUB command.
                    current_gear.sub_com = self.load_list(g_file)
                elif line == "INV":
                    # This is a INV command.
                    current_gear.inv_com = self.load_list(g_file)
                elif line == "END":
                    keep_going = False
            elif not rawline:
                keep_going = False

        return masterlist

    def convert(self, protolist,defaults):
        # Convert the provided list to gears.
        mylist = list()
        for pg in protolist:
            for k,v in defaults.items():
                if k not in pg.gparam:
                    pg.gparam[k] = v
            nudefaults = dict()
            if "scale" in pg.gparam:
                nudefaults["scale"] = pg.gparam["scale"]
            if "material" in pg.gparam:
                nudefaults["material"] = pg.gparam["material"]
            my_subs = self.convert(pg.sub_com,nudefaults)
            my_invs = self.convert(pg.inv_com,nudefaults)
            mygear = pg.gclass(sub_com=my_subs, inv_com=my_invs, **pg.gparam)
            mylist.append(mygear)
        return mylist

    def load(self):
        with open(self.fname, 'rb') as f:
            mylist = self.load_list(f)
        return self.convert(mylist,dict())

    @classmethod
    def load_design_file(cls, dfname):
        return cls(os.path.join(pbge.util.game_dir('design'), dfname)).load()


class Saver(object):
    """Used to save a gear structure to disk in a human-readable format."""

    def __init__(self, fname):
        self.fname = fname

    def hashable_to_string(self, wotzit):
        # Given wotzit, return the string to be output to the file.
        if wotzit is None:
            return 'None'
        elif wotzit in SINGLETON_TYPES.values():
            return wotzit.__name__
        elif isinstance(wotzit, str) and wotzit not in SINGLETON_TYPES and ' ' not in wotzit:
            return wotzit
        elif isinstance(wotzit, dict):
            mylist = list()
            for k, v in wotzit.iteritems():
                mylist.append(self.hashable_to_string(k) + ' = ' + self.hashable_to_string(v))
            return '{' + ', '.join(mylist) + '}'
        else:
            return repr(wotzit)

    def save_list(self, f, glist, indent=''):
        for save_the_gear in glist:
            if save_the_gear.__class__.__name__ in GEAR_TYPES:
                # We only save things we can reconstruct.
                f.write('{}{}\n'.format(indent, save_the_gear.__class__.__name__))

                # Go through the ancestors, see what attributes need saving.
                my_params = set()
                for ancestor in save_the_gear.__class__.__mro__:
                    if hasattr(ancestor, 'SAVE_PARAMETERS'):
                        my_params.update(ancestor.SAVE_PARAMETERS)

                for p in my_params:
                    k = self.hashable_to_string(p)
                    if hasattr(save_the_gear, k):
                        v = self.hashable_to_string(getattr(save_the_gear, k))
                        f.write('{}  {} = {}\n'.format(indent, k, v))

                if save_the_gear.sub_com:
                    f.write('{}  SUB\n'.format(indent))
                    self.save_list(f, save_the_gear.sub_com, indent + '    ')
                    f.write('{}  END\n'.format(indent))

                if save_the_gear.inv_com:
                    f.write('{}  SUB\n'.format(indent))
                    self.save_list(f, save_the_gear.inv_com, indent + '    ')
                    f.write('{}  END\n'.format(indent))

    def save(self, glist):
        with open(self.fname, 'wb') as f:
            self.save_list(f, glist)


#  ******************************
#  ***   UTILITY  FUNCTIONS   ***
#  ******************************

def init_gears():
    selector.EARTH_NAMES = pbge.namegen.NameGen("ng_earth.txt")
    selector.ORBITAL_NAMES = pbge.namegen.NameGen("ng_orbital.txt")
    selector.MARS_NAMES = pbge.namegen.NameGen("ng_mars.txt")
    selector.LUNA_NAMES = pbge.namegen.NameGen("ng_lunar.txt")
    selector.GENERIC_NAMES = pbge.namegen.NameGen("ng_generic.txt")
    selector.DEADZONE_TOWN_NAMES = pbge.namegen.NameGen("ng_dztowns.txt")

    if not os.path.exists(pbge.util.user_dir('design')):
        os.mkdir(pbge.util.user_dir('design'))
    if not os.path.exists(pbge.util.user_dir('image')):
        os.mkdir(pbge.util.user_dir('image'))
    pbge.image.search_path.append(pbge.util.user_dir('image'))
    pbge.POSTERS += glob.glob(os.path.join(pbge.util.user_dir('image'), "eyecatch_*.png"))

    # Load all design files.
    design_files = glob.glob(os.path.join(pbge.util.game_dir('design'), '*.txt')) + glob.glob(
        os.path.join(pbge.util.user_dir('design'), '*.txt'))
    for f in design_files:
        selector.DESIGN_LIST += Loader(f).load()
    # print selector.DESIGN_LIST
    selector.check_design_list()

    portraits.init_portraits()
    jobs.init_jobs()
