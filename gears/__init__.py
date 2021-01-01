import pbge
import random
import copy

from . import base
from . import calibre
from . import damage
from . import materials
from . import scale
from . import stats
from . import geffects
from . import info
from . import color
from . import attackattributes
from . import personality
from . import factions
from . import tags
from . import selector
from . import enchantments
from . import programs
from . import portraits
from . import genderobj
from . import usables
from . import meritbadges

import inspect
import os
import glob
from .color import ALL_COLORS, CLOTHING_COLORS, SKIN_COLORS, HAIR_COLORS, MECHA_COLORS, DETAIL_COLORS, METAL_COLORS, \
    random_character_colors, random_mecha_colors
from . import eggs
from . import relationships

GEAR_TYPES = dict()
SINGLETON_TYPES = dict()
SINGLETON_REVERSE = dict()
ALL_CALIBRES = list()
ALL_FACTIONS = list()

def harvest(mod, subclass_of, dict_to_add_to, exclude_these, list_to_add_to=None):
    for name in dir(mod):
        o = getattr(mod, name)
        if inspect.isclass(o) and issubclass(o, subclass_of) and o not in exclude_these:
            dict_to_add_to[o.__name__] = o
            if dict_to_add_to is SINGLETON_TYPES:
                SINGLETON_REVERSE[o] = o.__name__
            if list_to_add_to is not None:
                list_to_add_to.append(o)


harvest(base, base.BaseGear, GEAR_TYPES, (base.BaseGear, base.MovementSystem, base.Weapon, base.Usable))
harvest(scale, scale.MechaScale, SINGLETON_TYPES, ())
harvest(base, base.ModuleForm, SINGLETON_TYPES, (base.ModuleForm,))
harvest(materials, materials.Material, SINGLETON_TYPES, (materials.Material,))
harvest(calibre, calibre.BaseCalibre, SINGLETON_TYPES, (calibre.BaseCalibre,),list_to_add_to=ALL_CALIBRES)
harvest(base, base.MT_Battroid, SINGLETON_TYPES, ())
SINGLETON_TYPES['None'] = None
harvest(stats, stats.Stat, SINGLETON_TYPES, (stats.Stat,))
harvest(stats, stats.Skill, SINGLETON_TYPES, (stats.Skill,))
harvest(geffects, pbge.scenes.animobs.AnimOb, SINGLETON_TYPES, ())
harvest(attackattributes, pbge.Singleton, SINGLETON_TYPES, ())
harvest(factions, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,factions.Faction),list_to_add_to=ALL_FACTIONS)
harvest(tags, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))
harvest(programs, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))
harvest(personality, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))
harvest(usables, pbge.Singleton, SINGLETON_TYPES, (pbge.Singleton,))


def harvest_color(dict_to_add_to):
    for name in dir(color):
        o = getattr(color, name)
        if isinstance(o, color.GHGradient):
            dict_to_add_to[name] = o
            ALL_COLORS.append(o)
            if color.CLOTHING in o.sets:
                CLOTHING_COLORS.append(o)
            if color.SKIN in o.sets:
                SKIN_COLORS.append(o)
            if color.HAIR in o.sets:
                HAIR_COLORS.append(o)
            if color.MECHA in o.sets:
                MECHA_COLORS.append(o)
            if color.DETAILS in o.sets:
                DETAIL_COLORS.append(o)
            if color.METAL in o.sets:
                METAL_COLORS.append(o)
    ALL_COLORS.sort(key=lambda c: c.family)

from . import oldghloader
from . import jobs

harvest_color(SINGLETON_TYPES)
SINGLETON_TYPES.update(jobs.ALL_JOBS)
jobs.SINGLETON_TYPES = SINGLETON_TYPES

from . import colorstyle
from . import champions

def harvest_styles(mod):
    for name in dir(mod):
        o = getattr(mod, name)
        if isinstance(o,colorstyle.Style):
            colorstyle.ALL_STYLES.append(o)

harvest_styles(colorstyle)

class QualityOfLife(object):
    # A measurement of a community's quality of life. I'll have you know I was up all night reading Wikipedia
    # articles to come up with these QOL measures. Positive = good, negative = bad.
    # Prosperity: Poverty is low, public works get done.
    # Stability: Expectation of fairness and ability to plan for the future.
    # Health: Medical care and sanitation.
    # Community: Cultural works and sense of togetherness.
    # Defense: Ability to resist external military threats.
    # Tags: Special city-wide status effects not covered by the above indicies.
    def __init__(self,prosperity=0,stability=0,health=0,community=0,defense=0,tags=()):
        self.prosperity = prosperity
        self.stability = stability
        self.health = health
        self.community = community
        self.defense = defense
        self.tags = list(tags)

    def add(self,other):
        self.prosperity += other.prosperity
        self.stability += other.stability
        self.health += other.health
        self.community += other.community
        self.defense += other.defense
        self.tags += other.tags

    def get_keywords(self):
        mylist = list()
        if self.prosperity > 0:
            mylist.append("+prosperity")
        elif self.prosperity < 0:
            mylist.append("-prosperity")
        if self.stability > 0:
            mylist.append("+stability")
        elif self.stability < 0:
            mylist.append("-stability")
        if self.health > 0:
            mylist.append("+health")
        elif self.health < 0:
            mylist.append("-health")
        if self.community > 0:
            mylist.append("+community")
        elif self.community < 0:
            mylist.append("-community")
        if self.defense > 0:
            mylist.append("+defense")
        elif self.defense < 0:
            mylist.append("-defense")
        return mylist


class MetroData(object):
    def __init__(self):
        self.scripts = pbge.container.ContainerList(owner=self)
        self.local_reputation = 0

    def get_quality_of_life(self):
        qol = QualityOfLife()
        for plot in self.scripts:
            if plot.active and hasattr(plot,"QOL"):
                qol.add(plot.QOL)
        return qol


class GearHeadScene(pbge.scenes.Scene):
    def __init__(self, width=128, height=128, name="", player_team=None, civilian_team=None, faction=None,
                 scale=scale.MechaScale, environment=tags.GroundEnv, attributes=(), is_metro=False,
                 exploration_music=None,combat_music=None,**kwargs):
        # A metro scene is one which will contain plots and tarot cards local to it and its children.
        #   Generally it should be placed at root, as a direct child of the GHCampaign.
        super().__init__(width, height, name, player_team,**kwargs)
        self.civilian_team = civilian_team
        self.faction = faction
        self.scale = scale
        self.environment = environment
        self.script_rooms = list()
        self.attributes = set(attributes)
        self.exploration_music = exploration_music
        self.combat_music = combat_music
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

    def is_hostile_to_player(self, a):
        if a:
            team_a = self.local_teams.get(a)
            return team_a and team_a.is_enemy(self.player_team)

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
                return info.get_status_display(model=mmecha,scene=self)
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

    def purge_faction(self,camp,fac):
        # Move all the NPCs belonging to this faction to the storage scene.
        for npc in list(self.contents):
            if hasattr(npc,"faction") and npc.faction is fac and npc not in camp.party:
                self.contents.remove(npc)
                camp.storage.contents.append(npc)
        for subscene in self.sub_scenes:
            subscene.purge_faction(camp,fac)

    def list_empty_spots( self, room=None ):
        good_spots = set()
        if not room:
            room = self.get_rect()
        for x in range( room.x, room.x + room.width - 1 ):
            for y in range( room.y, room.y + room.height-1 ):
                if not self.tile_blocks_walking(x,y):
                    good_spots.add( (x,y) )
        good_spots -= self.get_blocked_tiles()
        return good_spots

    def tidy_enchantments(self,dispel_type):
        for thing in self.contents:
            if hasattr(thing, "ench_list"):
                thing.ench_list.tidy(dispel_type)

    def tidy_at_start(self,camp):
        for npc in self.contents:
            if hasattr(npc,"pos"):
                myteam = self.local_teams.get(npc,None)
                if myteam:
                    home = myteam.home
                    if home and npc.pos and not home.collidepoint(npc.pos):
                        npc.pos = None
                else:
                    home = None
                if not npc.pos or not self.on_the_map(*npc.pos):
                    if home:
                        good_spots = self.list_empty_spots(home)
                        if not good_spots:
                            good_spots = self.list_empty_spots()
                    else:
                        good_spots = self.list_empty_spots()
                    if good_spots:
                        npc.pos = random.choice(list(good_spots))
                    else:
                        print("Warning: {} could not be placed in {}".format(npc,self))

    def deploy_team(self, members, team):
        if team.home:
            good_spots = list(self.list_empty_spots(team.home))
            if not good_spots:
                good_spots = list(self.list_empty_spots())
        else:
            good_spots = list(self.list_empty_spots())
        random.shuffle(good_spots)
        for m in members:
            if good_spots:
                p = good_spots.pop()
                m.place(self, pos=p, team=team)
            else:
                print("Warning: {} could not be deployed in {}".format(m, self))

    def deploy_actor(self, actor):
        myteam = self.local_teams.get(actor) or self.civilian_team
        if myteam:
            self.deploy_team([actor,], myteam)
        else:
            good_spots = list(self.list_empty_spots())
            if good_spots:
                p = random.choice(good_spots)
                actor.place(self, pos=p)
            else:
                print("Warning: {} could not be deployed in {}".format(actor, self))

    def get_keywords(self):
        mylist = list()
        for t in self.attributes:
            if hasattr(t,"name"):
                mylist.append(t.name)
            else:
                mylist.append(str(t))
        return mylist

    def place_gears_near_spot(self, x0, y0, team, *models):
        entry_points = pbge.scenes.pfov.WalkReach(self, x0, y0, 1, True).tiles
        entry_points = entry_points.difference(self.get_blocked_tiles())
        if not entry_points:
            entry_points = pbge.scenes.pfov.WalkReach(self, x0, y0, 3, True).tiles
            entry_points = entry_points.difference(self.get_blocked_tiles())
        entry_points = list(entry_points)
        for pc in models:
            if entry_points:
                pos = random.choice(entry_points)
                entry_points.remove(pos)
            else:
                break
            pc.place(self, pos, team)
            pc.gear_up()


class GearHeadCampaign(pbge.campaign.Campaign):

    def __init__(self, name="GHC Campaign", explo_class=None, year=158, egg=None, num_lancemates=3, faction_relations=factions.DEFAULT_FACTION_DICT_NT158, convoborder="dzd_convoborder.png"):
        super(GearHeadCampaign, self).__init__(name, explo_class)
        self.year = year
        self.num_lancemates = num_lancemates
        self.faction_relations = copy.deepcopy(faction_relations)
        self.history = list()
        self.convoborder = convoborder
        self.fight = None
        self.pc = None

        # Some containers for characters who have been either incapacitated or killed.
        # It's the current scenario's responsibility to do something with these lists
        # at an appropriate time.
        self.incapacitated_party = list()
        self.dead_party = list()

        self.storage = GearHeadScene(name="Storage")
        self.contents.append(self.storage)

        if egg:
            self.egg = egg
            self.party = [egg.pc,]
            if egg.mecha:
                self.party.append(egg.mecha)
                egg.mecha.pilot = egg.pc
            while egg.stuff:
                mek = egg.stuff.pop()
                self.party.append(mek)
            self.pc = egg.pc

    def get_dialogue_offers_and_grammar(self, npc: base.Character):
        doffs, grams = super().get_dialogue_offers_and_grammar(npc)

        return doffs, grams

    def active_plots(self):
        for p in super(GearHeadCampaign, self).active_plots():
            yield p
        myscene = self.scene.get_metro_scene()
        if myscene:
            for p in myscene.metrodat.scripts:
                yield p

    def all_plots(self):
        for ob in self.all_contents(self):
            if hasattr(ob,"scripts"):
                for p in ob.scripts:
                    yield p

    def active_tarot_cards(self):
        for p in self.active_plots():
            if hasattr(p,"tarot_position"):
                yield p

    def get_tarot_card_by_position(self,pos):
        for card in self.active_tarot_cards():
            if card.tarot_position == pos:
                return card

    def first_active_pc(self):
        # The first active PC is the first PC in the party list who is
        # both operational and on the map.
        flp = None
        for pc in self.party:
            if pc.is_operational() and pc in self.scene.contents and hasattr(pc,"pos") and pc.pos and self.scene.on_the_map(*pc.pos):
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

    def get_lancemates(self):
        return [pc for pc in self.party if isinstance(pc,base.Character) and pc is not self.pc]

    def can_add_lancemate(self):
        lancemates = self.get_lancemates()
        return len(lancemates) < self.num_lancemates

    def get_party_skill(self, stat_id, skill_id):
        return max([pc.get_skill_score(stat_id, skill_id) for pc in self.get_active_party()] + [0])

    def make_skill_roll(self, stat_id, skill_id, rank, difficulty=stats.DIFFICULTY_AVERAGE, untrained_ok=False,no_random=False):
        # Make a skill roll against a given difficulty. If successful, return the lancemate
        # who made the roll.
        if untrained_ok:
            myparty = self.get_active_party()
        else:
            myparty = [pc for pc in self.get_active_party() if pc.has_skill(skill_id)]
        if myparty:
            winners = list()
            target = stats.get_skill_target(rank,difficulty)
            for roller in myparty:
                if no_random:
                    roll = 55 + roller.get_skill_score(stat_id,skill_id)
                else:
                    roll = random.randint(1,100) + roller.get_skill_score(stat_id,skill_id)
                if roll >= target:
                    winners.append(roller)
            if winners:
                pc = random.choice(winners)
                pc.dole_experience(max(rank//3,5),skill_id)
                return pc

    def party_has_skill(self,skill_id):
        return any(pc for pc in self.get_active_party() if pc.has_skill(skill_id))

    def get_pc_mecha(self,pc):
        meklist = [mek for mek in self.party if isinstance(mek,base.Mecha) and mek.pilot is pc]
        if meklist:
            if len(meklist) > 1:
                for mek in meklist[1:]:
                    mek.pilot = None
            return meklist[0]

    def get_backup_mek(self,npc):
        for mek in self.party:
            if isinstance(mek,base.Mecha) and hasattr(mek,"owner") and mek.owner is npc:
                return mek

    def assign_pilot_to_mecha(self,pc,mek):
        # either mek or pc can be None, to clear a mecha's assigned pilot.
        for m in self.party:
            if isinstance(m, base.Mecha) and m.pilot is pc:
                m.pilot = None
        if mek:
            mek.pilot = pc

    def keep_playing_campaign(self):
        return self.pc.is_operational() and self.egg

    def play(self):
        super(GearHeadCampaign, self).play()
        if self.pc in self.dead_party:
            pbge.alert("Game Over",font=pbge.my_state.hugefont)
            self.delete_save_file()

    def eject(self):
        # This campaign is over. Eject the egg.
        mek = self.get_pc_mecha(self.pc)
        if mek:
            self.party.remove(mek)
            if hasattr(mek, "container"):
                mek.container = None
            mek.pilot = None
        self.egg.mecha = mek
        for pc in self.party:
            if pc is not self.pc:
                if hasattr(pc, "container") and pc.container:
                    pc.container.remove(pc)
                if isinstance(pc, base.Character):
                    if pc not in self.egg.dramatis_personae and not pc.mnpcid:
                        self.egg.dramatis_personae.append(pc)
                elif pc not in self.egg.stuff and not hasattr(pc, "owner"):
                    self.egg.stuff.append(pc)
                    if hasattr(pc, "pilot"):
                        pc.pilot = None
        self.egg.save()
        self.egg = None
        self.delete_save_file()

    def get_usable_party(self,map_scale,solo_map=False,just_checking=False):
        usable_party = list()
        if not solo_map:
            party_candidates = self.party
        else:
            party_candidates = [pc for pc in self.party if pc is self.pc or (hasattr(pc,"pilot") and pc.pilot is self.pc)]
        for pc in party_candidates:
            if pc.is_not_destroyed() and pc.scale == map_scale and isinstance(pc,(base.Character,base.Mecha)):
                if hasattr(pc, "pilot"):
                    if pc.pilot and pc.pilot in self.party and pc.pilot.is_operational() and pc.check_design():
                        if not just_checking:
                            pc.load_pilot(pc.pilot)
                        usable_party.append(pc)
                elif pc.is_operational():
                    usable_party.append(pc)
        if not usable_party and not just_checking:
            usable_party.append(self.pc)
        return usable_party

    def has_mecha_party(self, solo_map=False):
        party = self.get_usable_party(scale.MechaScale,solo_map=solo_map,just_checking=True)
        return len(party) > 0

    def choose_party(self):
        # Generally, if we're entering a mecha scale scene, send in the mecha.
        usable_party = list()
        if self.scene.scale is scale.WorldScale:
            mysquad = base.Squad(name="Party")
            mysquad.sub_com += self.get_usable_party(scale.MechaScale)
            usable_party.append(mysquad)
            self.party.append(mysquad)
        else:
            usable_party += self.get_usable_party(self.scene.scale,tags.SCENE_SOLO in self.scene.attributes)
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

        # Also update NPC positions when placing the party.
        self.scene.tidy_at_start(self)

    def bring_out_your_dead(self, announce_character_state=False, announce_mecha_state=True):
        for pc in list(self.party):
            if pc.is_destroyed():
                self.party.remove(pc)
                skill = self.get_party_skill(stats.Knowledge,pc.material.repair_type) + 50 - pc.get_percent_damage_over_health()
                if pc is self.pc:
                    if pbge.util.config.getboolean("DIFFICULTY","pc_can_die") and random.randint(1,100) > skill:
                        self.dead_party.append(pc)
                    else:
                        self.incapacitated_party.append(pc)
                        pc.restore_all()
                elif isinstance(pc,base.Being):
                    if pbge.util.config.getboolean("DIFFICULTY","lancemates_can_die") and random.randint(1,100) > skill:
                        self.dead_party.append(pc)
                        if announce_character_state:
                            pbge.alert("{} has died.".format(pc))
                    else:
                        self.incapacitated_party.append(pc)
                        pc.restore_all()
                        if announce_character_state:
                            pbge.alert("{} has been severely injured and is removed to a safe place.".format(pc))
                elif random.randint(1,100) <= skill or not pbge.util.config.getboolean("DIFFICULTY","mecha_can_die") or pc not in self.scene.contents:
                    self.party.append(pc)
                elif announce_mecha_state:
                    pbge.alert("{} was wrecked beyond recovery.".format(pc.get_full_name()))

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
        for pc in self.party:
            if hasattr(pc,"renown") and pc is not self.pc:
                pc.renown = min(max(nuval, -100, pc.renown), 100)

    def _del_renown(self):
        self.pc.renown = 0

    renown = property(_get_renown,_set_renown,_del_renown)

    def dole_xp(self,amount, type=base.Being.TOTAL_XP):
        for pc in self.party:
            if hasattr(pc,"experience"):
                pc.experience[type] += amount

    def totally_restore_party(self):
        # Restore the party to health, returning the cost of doing so.
        repair_total = 0
        for pc in self.party + self.incapacitated_party:
            repair_total += pc.restore_all()
        return repair_total

    def get_relationship(self,npc):
        if npc.mnpcid:
            return self.egg.major_npc_records.setdefault(npc.mnpcid,relationships.Relationship())
        else:
            return relationships.Relationship()

    # Faction Methods
    def get_faction(self,mything):
        if isinstance(mything,factions.Circle):
            return mything
        elif inspect.isclass(mything) and issubclass(mything,factions.Faction):
            return mything
        elif hasattr(mything,"faction"):
            return mything.faction
        elif hasattr(mything,"get_tacit_faction"):
            return mything.get_tacit_faction(self)

    def _get_faction_family(self,myfac):
        facfam = [myfac,]
        while hasattr(myfac,"parent_faction") and myfac.parent_faction:
            facfam.append(myfac.parent_faction)
            myfac = myfac.parent_faction
        return facfam

    def are_faction_allies(self,a,b):
        a_fac,b_fac = self.get_faction(a),self.get_faction(b)
        if a_fac and b_fac:
            a_fam,b_fam = self._get_faction_family(a_fac),self._get_faction_family(b_fac)
            for fac1 in a_fam:
                for fac2 in b_fam:
                    if fac1 is fac2 or (fac1 in self.faction_relations and fac2 in self.faction_relations[fac1].allies) or (fac2 in self.faction_relations and fac1 in self.faction_relations[fac2].allies):
                        return True

    def are_faction_enemies(self,a,b):
        a_fac,b_fac = self.get_faction(a),self.get_faction(b)
        if a_fac and b_fac:
            a_fam,b_fam = self._get_faction_family(a_fac),self._get_faction_family(b_fac)
            for fac1 in a_fam:
                for fac2 in b_fam:
                    if (fac1 in self.faction_relations and fac2 in self.faction_relations[fac1].enemies) or (fac2 in self.faction_relations and fac1 in self.faction_relations[fac2].enemies):
                        return True

    def set_faction_ally(self,a,b):
        if a not in self.faction_relations:
            self.faction_relations[a] = factions.FactionRelations()
        self.faction_relations[a].allies.append(b)
        if b in self.faction_relations[a].enemies:
            self.faction_relations[a].enemies.remove(b)

    def freeze(self,thing):
        # Move something, probably an NPC, into storage.
        if hasattr(thing,"container") and thing.container:
            thing.container.remove(thing)
        self.storage.contents.append(thing)



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

    def build(self,defaults=None):
        if not defaults:
            defaults = dict()
        for k, v in defaults.items():
            if k not in self.gparam:
                self.gparam[k] = v
        nudefaults = dict()
        if "scale" in self.gparam:
            nudefaults["scale"] = self.gparam["scale"]
        if "material" in self.gparam:
            nudefaults["material"] = self.gparam["material"]
        my_subs = [pg.build(nudefaults) for pg in self.sub_com]
        my_invs = [pg.build(nudefaults) for pg in self.inv_com]
        return self.gclass(sub_com=my_subs, inv_com=my_invs, **self.gparam)

class ProtoSTC(object):
    """Used by the loader to hold gear definitions before creating the actual gear."""

    def __init__(self, stc_ident):
        self.stc_ident = stc_ident
        self.gparam = dict()
        self.sub_com = list()
        self.inv_com = list()

    def build(self,defaults=None):
        if not defaults:
            defaults = dict()
        for k, v in defaults.items():
            if k not in self.gparam:
                self.gparam[k] = v
        nudefaults = dict()
        if "scale" in self.gparam:
            nudefaults["scale"] = self.gparam["scale"]
        if "material" in self.gparam:
            nudefaults["material"] = self.gparam["material"]

        mygear = selector.get_design_by_full_name(self.stc_ident)

        mygear.sub_com += [pg.build(nudefaults) for pg in self.sub_com]
        mygear.inv_com += [pg.build(nudefaults) for pg in self.inv_com]
        for k,v in self.gparam.items():
            if hasattr(mygear,k):
                setattr(mygear,k,v)
        return mygear


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
            elif rawval.isdigit() or rawval[0] in "+-":
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

                elif line.startswith("STC "):
                    stc_ident = line[4:]
                    if stc_ident in selector.DESIGN_BY_NAME:
                        current_gear = ProtoSTC(stc_ident)
                        masterlist.append(current_gear)
                    else:
                        print("Unknown STC '{}'".format(stc_ident))

                elif line == "SUB":
                    # This is a SUB command.
                    current_gear.sub_com = self.load_list(g_file)
                elif line == "INV":
                    # This is a INV command.
                    current_gear.inv_com = self.load_list(g_file)
                elif line == "END":
                    keep_going = False
                else:
                    print("Unidentified command: {}".format(line))
            elif not rawline:
                keep_going = False

        return masterlist

    def convert(self, protolist):
        # Convert the provided list to gears.
        mylist = list()
        for pg in protolist:
            mygear = pg.build()
            mylist.append(mygear)
        return mylist

    def load(self):
        with open(self.fname, 'rt') as f:
            mylist = self.load_list(f)
        return self.convert(mylist)

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
        elif isinstance(wotzit,(list,tuple)):
            return "[{}]".format(", ".join([self.hashable_to_string(t) for t in wotzit]))
        elif wotzit in SINGLETON_REVERSE:
            return SINGLETON_REVERSE[wotzit]
        elif isinstance(wotzit, str) and wotzit not in SINGLETON_TYPES and ' ' not in wotzit:
            return wotzit
        elif isinstance(wotzit, dict):
            mylist = list()
            for k, v in wotzit.items():
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
                    f.write('{}  INV\n'.format(indent))
                    self.save_list(f, save_the_gear.inv_com, indent + '    ')
                    f.write('{}  END\n'.format(indent))

    def save(self, glist):
        with open(self.fname, 'wt') as f:
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
    if not os.path.exists(pbge.util.user_dir('content')):
        os.mkdir(pbge.util.user_dir('content'))
    pbge.image.search_path.append(pbge.util.user_dir('image'))
    pbge.POSTERS += glob.glob(os.path.join(pbge.util.user_dir('image'), "eyecatch_*.png"))

    # Load the STC files first.
    design_files = glob.glob(pbge.util.data_dir('stc_*.txt'))
    for f in design_files:
        selector.DESIGN_LIST += Loader(f).load()
    # print selector.DESIGN_LIST
    selector.check_design_list()
    # Copy this list to the STC_LIST.
    selector.STC_LIST = list(selector.DESIGN_LIST)

    for d in selector.DESIGN_LIST:
        if d.get_full_name() in selector.DESIGN_BY_NAME:
            print("Warning: Multiple designs named {}".format(d.get_full_name()))
        selector.DESIGN_BY_NAME[d.get_full_name()] = d
        d.stc = True


    # Load all design files.
    design_files = glob.glob(os.path.join(pbge.util.game_dir('design'), '*.txt')) + glob.glob(
        os.path.join(pbge.util.user_dir('design'), '*.txt'))
    for f in design_files:
        selector.DESIGN_LIST += Loader(f).load()
    # print selector.DESIGN_LIST
    selector.check_design_list()

    for d in selector.DESIGN_LIST:
        if not hasattr(d,"stc"):
            if d.get_full_name() in selector.DESIGN_BY_NAME:
                print("Warning: Multiple designs named {}".format(d.get_full_name()))
            selector.DESIGN_BY_NAME[d.get_full_name()] = d
        if isinstance(d, base.Monster):
            selector.MONSTER_LIST.append(d)

    portraits.init_portraits()
    jobs.init_jobs()

    #for d in selector.DESIGN_LIST:
    #    if isinstance(d, base.Mecha):
    #        print("{} {}".format(d, d.get_primary_attack().source))

