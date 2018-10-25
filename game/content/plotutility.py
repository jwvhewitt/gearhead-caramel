import ghwaypoints
import random
import pbge
import gears

class SceneConnection(object):
    DEFAULT_ROOM_1 = pbge.randmaps.rooms.FuzzyRoom
    DEFAULT_ROOM_1_W = 3
    DEFAULT_ROOM_1_H = 3
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.FuzzyRoom
    DEFAULT_ROOM_2_W = 5
    DEFAULT_ROOM_2_H = 5
    DEFAULT_DOOR_1 = ghwaypoints.Exit
    DEFAULT_DOOR_2 = ghwaypoints.Exit
    def __init__(self,plot,scene1,scene2,room1=None,room1_id=None,room2=None,room2_id=None,anchor1=None,anchor2=None,door1=None,door1_id=None,door2=None,door2_id=None):
        self.scene1 = scene1
        self.scene2 = scene2
        if not room1:
            room1 = plot.register_element(room1_id,self.DEFAULT_ROOM_1(self.DEFAULT_ROOM_1_W,self.DEFAULT_ROOM_1_H,parent=scene1,anchor=anchor1 or self.get_room1_anchor()))
            plot.move_element(room1,scene1)
        self.room1 = room1
        if not room2:
            room2 = plot.register_element(room2_id,self.DEFAULT_ROOM_2(self.DEFAULT_ROOM_2_W,self.DEFAULT_ROOM_2_H,parent=scene2,anchor=anchor2 or self.get_room2_anchor()))
            plot.move_element(room2, scene2)
        self.room2 = room2
        if not door1:
            door1 = plot.register_element(door1_id,self.get_door1())
        plot.move_element(door1,room1)
        self.door1 = door1
        if not door2:
            door2 = plot.register_element(door2_id,self.get_door2())
        plot.move_element(door2,room2)
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
    CHART_A = ("Brutal","Cruel","Desert","Deadly","Frenzied","Angry","Despicable","Evil","Freaky","Greedy",
               "Glorious","Hellbound","Horrid","Invincible","Jolly","Killer","Lucky","Larcenous","Murderous",
               "Merciless","Nasty","Pierced","Rancid","Razor","Speed","Savage","Terrible","Thunder","Jugular",
               "Unbeatable","Vicious","Violent","Red","Bloody","Wanton","Xtreem","Heavy Metal","Blood Pact")
    CHART_B = ("Warriors","Bandits","Pirates","Demons","Gang","Hooligans","Destroyers","Raiders","Droogs","Modez",
               "Breakers","Bruisers","Crashers","Executors","Frenz","Grabberz","Hammers","Jokerz","Killerz",
               "Mob","Ogres","Queenz","Kingz","Raptors","Slashers","Titanz","Vizigoths","Freakz","Junk Ratz",
               "Rippers","Gougers","Horde")
    def __init__(self):
        parent_faction = random.choice([gears.factions.BoneDevils,gears.factions.BoneDevils,gears.factions.BladesOfCrihna,None])
        name = "the {} {}".format(random.choice(self.CHART_A),random.choice(self.CHART_B))
        super(RandomBanditCircle,self).__init__(name=name,parent_faction=parent_faction)
