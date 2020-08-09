
def dungeon_cleaner(scene):
    # Vacuum up all the dead monsters.
    for bit in list(scene.contents):
        if hasattr(bit,"is_operational") and not bit.is_operational():
            scene.contents.remove(bit)


class DungeonMaker(object):
    def __init__(self):
        pass
