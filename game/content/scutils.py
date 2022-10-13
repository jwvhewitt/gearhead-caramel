# Utilities that are useful for the scenario creator and not much else.
import pbge
from . import ghwaypoints, ghrooms


class DialogueOfferHandler:
    # Keeps track of single-use dialogue offers without the scenario designer needing to add new global variables
    # or whatnot.
    def __init__(self, uid, single_use=False):
        self.uid = uid
        self.single_use = single_use
        self.has_been_used = False
        self.effect = None

    def can_add_offer(self):
        return not (self.single_use and self.has_been_used)

    def get_effect(self, effect=None):
        self.effect = effect
        return self

    def __call__(self, camp):
        self.has_been_used = True
        if self.effect:
            self.effect(camp)


class SCSceneConnection(object):
    DEFAULT_ROOM_1 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_ROOM_1_W = 3
    DEFAULT_ROOM_1_H = 3
    DEFAULT_ROOM_2 = pbge.randmaps.rooms.OpenRoom
    DEFAULT_ROOM_2_W = 5
    DEFAULT_ROOM_2_H = 5
    DEFAULT_DOOR_1 = ghwaypoints.Exit
    DEFAULT_DOOR_2 = ghwaypoints.Exit

    def __init__(self, scene1, scene2, room1, room2, door1, door2):
        scene1.contents.append(room1)
        scene2.contents.append(room2)

        if isinstance(room1, pbge.randmaps.terrset.TerrSet):
            room1.waypoints["DOOR"] = door1
        else:
            room1.contents.append(door1)

        if isinstance(room2, pbge.randmaps.terrset.TerrSet):
            room2.waypoints["DOOR"] = door2
        else:
            room2.contents.append(door2)

        door1.dest_wp = door2
        door2.dest_wp = door1

