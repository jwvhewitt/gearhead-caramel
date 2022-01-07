import gears

FIGHT_CHALLENGE = "FIGHT_CHALLENGE"
# The Key for a fight challenge is (Faction_to_be_fought,)

class InvolvedMetroFactionNPCs(object):
    # Return True if ob is an NPC allied with the given faction and in the same Metro area.
    def __init__(self, metroscene, faction=None):
        self.metroscene = metroscene
        self.faction = faction or metroscene.faction

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.are_faction_allies(ob, self.faction))

