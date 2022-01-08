import gears

FIGHT_CHALLENGE = "FIGHT_CHALLENGE"
# The key for a fight challenge is (Faction_to_be_fought,)
# The data for a fight challenge should include:
#   challenge_objectives = A list of objectives that can be given by the challenge-givers; infinitive verb phrase
#   enemy_objectives = A list of objectives that can be given by the enemy faction (key[0]); infinitive verb phrase
#   mission_intros = A list of things for mission-givers to say; primary clause
#   mission_objectives = A list of custom DescribedObjectives
#

class DescribedObjective(object):
    # objective is an objective from the missionbuilder.py unit or equivalent
    # mission_desc is a primary clause that might be used to describe this mission; may include {ENEMY_FACTION}
    def __init__(self, objective, mission_desc,
                 objective_pp = "[defeat_you]", objective_ep = "[defeat_you]",
                 win_pp = "I defeated you", win_ep = "you defeated me",
                 lose_pp = "you defeated me", lose_ep = "I defeated you"):
        self.objective = objective
        self.mission_desc = mission_desc
        self.objective_pp = objective_pp
        self.objective_ep = objective_ep
        self.win_pp = win_pp
        self.win_ep = win_ep
        self.lose_pp = lose_pp
        self.lose_ep = lose_ep


#   **********************
#   ***  INVOLVEMENTS  ***
#   **********************

class InvolvedMetroFactionNPCs(object):
    # Return True if ob is an NPC allied with the given faction and in the same Metro area.
    def __init__(self, metroscene, faction=None):
        self.metroscene = metroscene
        self.faction = faction or metroscene.faction

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.are_faction_allies(ob, self.faction))

