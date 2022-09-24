# Contains plots for adding a town hall to your city or whatever.

import game.ghdialogue.ghgrammar
import gears.tags
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services
from game.ghdialogue import context
import gears
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, ghrooms
from .shops_plus import get_building

#   ******************
#   ***  TOWNHALL  ***
#   ******************
#
# We say "Town Hall" but this can be used for all kinds of government buildings. Embassies, DMVs, you name it.
#
# Required Elements:
#  LOCALE, METRO, MISSION_GATE
#
#  LOCALE is where the town hall is to be placed; it will be used to generate the name if no HALL_NAME is given.
#
# Guaranteed Elements:
#  INTERIOR, LEADER, DEFENDER, HALL_FACTION, DEFENSE_FACTION, FOYER
#
# The Leader and Defender are NPCs in this building. The Leader will typically be a Politician type while the defender
# will usually be a Military type.
#
# Optional Elements:
# - An INTERIOR_TAGS element may be passed; this value defaults to (SCENE_PUBLIC,).
# - LEADER_NAME, DEFENDER_NAME, and HALL_NAME may be passed; these will be used instead of the randomly generated ones.
# - LEADER_JOB may be passed, to set the leader as an Ambassador or something.
# - HALL_FACTION may be passed if the hall has a different faction from LOCALE.
# - DEFENSE_FACTION may be passed if you want to set a specific defense faction.
# - A CITY_COLORS element may be passed; if it exists, a custom palette will be used for building exteriors.
# - NOT_METRO_LEADER = set this element to True if you don't want the Leader set as Metro leader
# - DOOR_SIGN = set the door sign to this

class BasicTownHall(Plot):
    LABEL = "TOWNHALL"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        hallfaction = self.elements.get("HALL_FACTION") or self.elements["LOCALE"].faction
        self.elements["HALL_FACTION"] = hallfaction

        deffaction = self.elements.get("DEFENSE_FACTION") or self._get_defense_faction(nart, hallfaction)
        self.elements["DEFENSE_FACTION"] = deffaction

        # Create the leader
        npc1 = self.register_element("LEADER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes, faction=hallfaction,
            job=self._get_leader_job(hallfaction)))
        npc1.name = self.elements.get("LEADER_NAME", "") or npc1.name
        if not self.elements.get("NOT_METRO_LEADER"):
            self.elements["METRO"].city_leader = npc1

        self._hallname = self.elements.get("HALL_NAME", "") or self._generate_hall_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.BrickBuilding,
            waypoints={"DOOR": ghwaypoints.GlassDoor(name=self._hallname)},
            door_sign=self.elements.get("DOOR_SIGN") or (ghterrain.GoldTownHallSignEast, ghterrain.GoldTownHallSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self._hallname, player_team=team1, civilian_team=team2, faction=self.elements.get("HALL_FACTION"),
            attributes=self.elements.get("INTERIOR_TAGS", (gears.tags.SCENE_PUBLIC,)) + (
                gears.tags.SCENE_BUILDING, gears.tags.SCENE_GOVERNMENT),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.DefaultBuilding(
            wall_terrain=ghterrain.DefaultWall))
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")

        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")
        team3 = self.register_element("FOYER_TEAM", teams.Team("Foyer Team", allies=(team2,)), dident="FOYER")

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.add_sub_plot(nart, "TOWNHALL_DEFENDER")

        return True

    def _get_defense_faction(self, nart, hallfaction):
        myfac = None
        bossfac = hallfaction
        while bossfac and not myfac:
            myfacrel = nart.camp.faction_relations.get(bossfac)
            if myfacrel:
                candidates = [a for a in myfacrel.allies if {gears.tags.Military, gears.tags.Police}.intersection(a.factags)]
                if candidates:
                    myfac = random.choice(candidates)
            if hasattr(bossfac, "parent_faction"):
                bossfac = bossfac.parent_faction
                print(bossfac, bossfac.parent_faction)
            else:
                bossfac = None
        return myfac or hallfaction

    def _get_leader_job(self, hallfaction):
        if "LEADER_JOB" in self.elements and isinstance(self.elements["LEADER_JOB"], gears.jobs.Job):
            return self.elements["LEADER_JOB"]
        elif random.randint(1,23) <= 5:
            return gears.jobs.ALL_JOBS["Mayor"]
        elif hallfaction:
            return hallfaction.choose_job(gears.tags.Commander)
        else:
            return gears.jobs.ALL_JOBS["Mayor"]

    DEFAULT_TITLES = ("{LOCALE} Hall", "{LOCALE} Town Hall")
    CITY_TITLES = (
        "{LOCALE} City Hall", "{LOCALE} Metroplex"
    )
    VILLAGE_TITLES = (
        "{LOCALE} Community Hall", "{LEADER}'s Office"
    )

    def _generate_hall_name(self):
        mylocale = self.elements["LOCALE"]
        candidates = list(self.DEFAULT_TITLES)
        if gears.tags.City in mylocale.attributes:
            candidates += self.CITY_TITLES
        if gears.tags.Village in mylocale.attributes:
            candidates += self.VILLAGE_TITLES
        return random.choice(candidates).format(**self.elements)


#   ***************************
#   ***  TOWNHALL_DEFENDER  ***
#   ***************************

class DefaultDefender(Plot):
    LABEL = "TOWNHALL_DEFENDER"
    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        deffaction = self.elements["DEFENSE_FACTION"]

        # Create the defender
        npc = self.register_element("DEFENDER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes, faction=deffaction,
            job=self._get_defender_job(deffaction)))
        npc.name = self.elements.get("DEFENDER_NAME", "") or npc.name

        defroom = self.register_element('DEFROOM', pbge.randmaps.rooms.ClosedRoom(), dident="INTERIOR")
        team3 = self.register_element("DEFTEAM", teams.Team(name="Defroom Team", allies=[self.elements["LOCALE"].civilian_team]), dident="DEFROOM")
        team3.contents.append(npc)

        # Add a guard to the foyer.
        npc = self.register_element("GUARD", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes, faction=deffaction,
            job=self._get_guard_job(deffaction)), dident="FOYER_TEAM")

        return True

    def _get_defender_job(self, deffaction):
        if "DEFENDER_JOB" in self.elements and isinstance(self.elements["DEFENDER_JOB"], gears.jobs.Job):
            return self.elements["DEFENDER_JOB"]
        elif deffaction:
            return deffaction.choose_job(gears.tags.Commander)
        else:
            return gears.jobs.ALL_JOBS["Commander"]

    def _get_guard_job(self, deffaction):
        if deffaction:
            return deffaction.choose_job(gears.tags.Trooper)
        else:
            return gears.jobs.ALL_JOBS["Security Guard"]
