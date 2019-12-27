from . import ghwaypoints
import random
import pbge
import gears
from game.content import GHNarrativeRequest,PLOT_LIST


class SceneConnection(object):
    DEFAULT_ROOM_1 = pbge.randmaps.rooms.FuzzyRoom
    DEFAULT_ROOM_1_W = 3
    DEFAULT_ROOM_1_H = 3
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.FuzzyRoom
    DEFAULT_ROOM_2_W = 5
    DEFAULT_ROOM_2_H = 5
    DEFAULT_DOOR_1 = ghwaypoints.Exit
    DEFAULT_DOOR_2 = ghwaypoints.Exit

    def __init__(self, plot, scene1, scene2, room1=None, room1_id=None, room2=None, room2_id=None, anchor1=None,
                 anchor2=None, door1=None, door1_id=None, door2=None, door2_id=None, move_door1=True, move_door2=True):
        self.scene1 = scene1
        self.scene2 = scene2
        if not room1:
            room1 = plot.register_element(room1_id, self.DEFAULT_ROOM_1(self.DEFAULT_ROOM_1_W, self.DEFAULT_ROOM_1_H,
                                                                        parent=scene1,
                                                                        anchor=anchor1 or self.get_room1_anchor()))
            plot.place_element(room1, scene1)
        self.room1 = room1
        if not room2:
            room2 = plot.register_element(room2_id, self.DEFAULT_ROOM_2(self.DEFAULT_ROOM_2_W, self.DEFAULT_ROOM_2_H,
                                                                        parent=scene2,
                                                                        anchor=anchor2 or self.get_room2_anchor()))
            plot.place_element(room2, scene2)
        self.room2 = room2
        if not door1:
            door1 = plot.register_element(door1_id, self.get_door1())
        if move_door1:
            plot.place_element(door1, room1)
        self.door1 = door1
        if not door2:
            door2 = plot.register_element(door2_id, self.get_door2())
        if move_door2:
            plot.place_element(door2, room2)
        self.door2 = door2
        self.door1.dest_scene, self.door1.dest_entrance = self.scene2, self.door2
        self.door2.dest_scene, self.door2.dest_entrance = self.scene1, self.door1

    def get_room1_anchor(self):
        return None

    def get_room2_anchor(self):
        return None

    def get_door1(self):
        return self.DEFAULT_DOOR_1(anchor=pbge.randmaps.anchors.middle)

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.middle)

class TownBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.ClosedRoom

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMCommTowerConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDWCommTower
    r2anchor = pbge.randmaps.anchors.middle

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class IntCommTowerConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDCommTower

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMConcreteBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDWConcreteBuilding
    r2anchor = None

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class IntConcreteBuildingConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDConcreteBuilding

    def get_room2_anchor(self):
        return pbge.randmaps.anchors.south

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=pbge.randmaps.anchors.south)


class WMDZTownConnection(SceneConnection):
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_DOOR_1 = ghwaypoints.DZDTown
    r2anchor = None

    def get_room2_anchor(self):
        self.r2anchor = random.choice(pbge.randmaps.anchors.EDGES)
        return self.r2anchor

    def get_door2(self):
        return self.DEFAULT_DOOR_2(anchor=self.r2anchor)


class RandomBanditCircle(gears.factions.Circle):
    CHART_A = ("Brutal", "Cruel", "Desert", "Deadly", "Frenzied", "Angry", "Despicable", "Evil", "Freaky", "Greedy",
               "Glorious", "Hellbound", "Horrid", "Invincible", "Jolly", "Killer", "Lucky", "Larcenous", "Murderous",
               "Merciless", "Nasty", "Pierced", "Rancid", "Razor", "Speed", "Savage", "Terrible", "Thunder", "Jugular",
               "Unbeatable", "Vicious", "Violent", "Red", "Bloody", "Wanton", "Xtreem", "Heavy Metal", "Blood Pact")
    CHART_B = (
    "Warriors", "Bandits", "Pirates", "Demons", "Gang", "Hooligans", "Destroyers", "Raiders", "Droogs", "Modez",
    "Breakers", "Bruisers", "Crashers", "Executors", "Frenz", "Grabberz", "Hammers", "Jokerz", "Killerz",
    "Mob", "Ogres", "Queenz", "Kingz", "Raptors", "Slashers", "Titanz", "Vizigoths", "Freakz", "Junk Ratz",
    "Rippers", "Gougers", "Horde")

    def __init__(self):
        parent_faction = random.choice(
            [gears.factions.BoneDevils, gears.factions.BoneDevils, gears.factions.BladesOfCrihna, None])
        name = "the {} {}".format(random.choice(self.CHART_A), random.choice(self.CHART_B))
        super(RandomBanditCircle, self).__init__(name=name, parent_faction=parent_faction)


class CargoContainer(gears.base.Prop):
    DEFAULT_COLORS = (gears.color.White,gears.color.Aquamarine,gears.color.DeepGrey,gears.color.Black,gears.color.GullGrey)
    def __init__(self,name="Shipping Container",size=1,colors=None,imagename="prop_shippingcontainer.png",**kwargs):
        super(CargoContainer, self).__init__(name=name,size=size,imagename=imagename,**kwargs)
        self.colors = colors or self.DEFAULT_COLORS

    @staticmethod
    def random_fleet_colors():
        return [random.choice(gears.color.MECHA_COLORS),
                random.choice(gears.color.DETAIL_COLORS),
                random.choice(gears.color.METAL_COLORS),
                gears.color.Black,
                random.choice(gears.color.MECHA_COLORS)]
    @classmethod
    def generate_cargo_fleet(cls,rank,colors=None):
        if not colors:
            colors = cls.random_fleet_colors()
        myfleet = [cls(colors=colors) for t in range(random.randint(2,3)+max(0,rank//25))]
        return myfleet


class AutoJoiner(object):
    # A callable to handle lancemate join requests. The NPC will join the party,
    # bringing along any mecha and pets they may have.
    def __init__(self,npc):
        """
        Prepare to add the NPC to the party.
        :type npc: gears.base.Character
        """
        self.npc = npc
    def __call__(self,camp):
        """
        Add the NPC to the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc not in camp.party:
            camp.party.append(self.npc)
            mek = self.get_mecha_for_character(self.npc)
            camp.party.append(mek)
            camp.assign_pilot_to_mecha(self.npc,mek)
            for part in mek.get_all_parts():
                part.owner = self.npc
    @staticmethod
    def get_mecha_for_character(npc,choose_new_one=False):
        if npc.mecha_pref and npc.mecha_pref in gears.selector.DESIGN_BY_NAME and not choose_new_one:
            mek = gears.selector.get_design_by_full_name(npc.mecha_pref)
        else:
            level = max(npc.renown, 15)
            if hasattr(npc, "relationship") and npc.relationship:
                level = max(level + npc.relationship.data.get("mecha_level_bonus", 0), 10)
            mek = gears.selector.MechaShoppingList.generate_single_mecha(level, npc.faction, gears.tags.GroundEnv)
            npc.mecha_pref = mek.get_full_name()
        if npc.mecha_colors:
            mek.colors = npc.mecha_colors
        return mek


class AutoLeaver(object):
    # A partner for the above- this NPC will leave the party, along with any mecha + pets.
    def __init__(self,npc):
        """
        Prepare to remove the NPC from the party. This object can be used as a dialogue effect.
        :type npc: gears.base.Character
        """
        self.npc = npc
    def __call__(self,camp):
        """
        Remove the NPC from the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc in camp.party:
            camp.assign_pilot_to_mecha(self.npc,None)
            camp.party.remove(self.npc)
            for mek in list(camp.party):
                if hasattr(mek,"owner") and mek.owner is self.npc:
                    camp.party.remove(mek)
            for mek in list(camp.incapacitated_party):
                if hasattr(mek,"owner") and mek.owner is self.npc:
                    camp.incapacitated_party.remove(mek)

class CharacterMover(object):
    def __init__(self,plot,character,dest_scene,dest_team,allow_death=False):
        # Record the character's original location, move them to the new location.
        if character not in plot.get_locked_elements():
            print("Warning: Character {} should be locked by {} before moving!".format(character,plot))
        if not character.container:
            print("Warning: Character {} moved by {} has no original container!".format(character,plot))
        if not plot.active:
            print("Warning: Plot {} not active")
        if not plot.scope:
            print("Warning: Plot {} has no scope set")

        character.restore_all()
        self.character = character
        self.original_container = character.container

        # Check to see if the character can use a mecha in the destination scene.
        if character.combatant and dest_scene.scale is gears.scale.MechaScale:
            mek = AutoJoiner.get_mecha_for_character(character)
            if mek:
                mek.load_pilot(character)
                character = mek

        character.place(dest_scene,team=dest_team)

        self.allow_death = allow_death
        plot.call_on_end.append(self)
        plot.move_records.append((character,dest_scene.contents))

    def __call__(self,camp):
        if self.character.is_not_destroyed() or not self.allow_death:
            if hasattr(self.character, "container") and self.character.container:
                self.character.container.remove(self.character)
            self.character.restore_all()
            self.original_container.append(self.character)

class LanceStatusReporter(object):
    def __init__(self,camp,metroscene,metro):
        # Go through the injured/dead lists and see who needs help.
        myreports = list()
        if camp.pc not in camp.party:
            # This is serious.
            init = pbge.plots.PlotState(elements={"METRO":metro,"METROSCENE":metroscene})
            nart = GHNarrativeRequest(camp,init,adv_type="RECOVER_PC",plot_list=PLOT_LIST)
            if nart.story:
                nart.build()
                nart.story.start_recovery(camp)
        else:
            pass

