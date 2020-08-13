from . import plotutility

def dungeon_cleaner(scene):
    # Vacuum up all the dead monsters.
    for bit in list(scene.contents):
        if hasattr(bit,"is_operational") and not bit.is_operational():
            scene.contents.remove(bit)


class ProtoDLevel(object):
    def __init__(self, depth, branch=0, gen="DUNGEON_GENERIC"):
        self.depth = depth
        self.branch = branch
        self.gen = gen

class DungeonMaker(object):
    # Create a set of dungeon levels. Connect them to one another.
    def __init__(self, nart, parent_plot, parent_scene, name, architecture, rank,
                 scene_tags = (), monster_tags = (), temporary = False,
                 connector=plotutility.StairsDownToStairsUpConnector,
                 goal_room=None, goal_item=None):
        self.name = name
        self.architecture = architecture
        self.rank = rank
        self.connector = connector
