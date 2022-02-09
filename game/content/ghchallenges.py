import gears


#   ************************************
#   ***  DETHRONE  CHALLENGE  STUFF  ***
#   ************************************

DETHRONE_CHALLENGE = "DETHRONE_CHALLENGE"
# The involvement for a dethrone challenge identifies the NPCs protecting/supporting the NPC to be dethroned
# The key for a diplomacy challenge is (NPC_to_be_dethroned,)
# The data for a dethrone challenge should include:
#   reasons_to_dethrone: A list of phrases explaining why the NPC should be dethroned; dependent clause
#   reasons_to_support: A list of phrases explaining why the NPC should be supported; dependent clause
#   violated_virtue: The virtue the NPC to be dethroned has violated. May be None.
#   upheld_virtue: The virtue that the NPC's supporters seek to uphold. May also be None.
#


#   *************************************
#   ***  DIPLOMACY  CHALLENGE  STUFF  ***
#   *************************************

DIPLOMACY_CHALLENGE = "DIPLOMACY_CHALLENGE"
# The involvement for a diplomacy challenge identifies the NPCs whose opinion you want to sway
# The key for a diplomacy challenge is (Faction_to_be_swayed, [Faction_doing_swaying])
# The data for a diplomacy challenge should include:
#   challenge_subject: A string identifying the challenge
#   challenge_statements = A list of prevailing opinions that the PC wants to challenge; primary clause
#   pc_rebuttals = A list of replies the PC can give to challenge the statement above; primary clause
#   npc_agreement = A list of positive replies to the PC's rebuttal
#   npc_disagreement = A list of negative replies to the PC's rebuttal
#


#   *********************************
#   ***  FIGHT  CHALLENGE  STUFF  ***
#   *********************************

FIGHT_CHALLENGE = "FIGHT_CHALLENGE"
# The involvement for a fight challenge lists the NPCs who might give the PC a combat mission
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


#   ***************************************
#   ***  RAISE  ARMY  CHALLENGE  STUFF  ***
#   ***************************************

RAISE_ARMY_CHALLENGE = "RAISE_ARMY_CHALLENGE"
# The involvement for a raise_army challenge identifies the NPCs who can potentially join the army
# The key for a raise army challenge is (city_or_faction_that_needs_army,)
# The data for a raise army challenge should include:
#   threat: The faction or NPC that the army needs to be raised to oppose; may be None
#



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


class InvolvedMetroResidentNPCs(object):
    # Return True if ob is a non-lancemate NPC in the provided Metro area.
    def __init__(self, metroscene):
        self.metroscene = metroscene

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                ob not in camp.party and
                (not ob.relationship or gears.relationships.RT_LANCEMATE not in ob.relationship.tags))


#   ***************************
#   ***  ACCESS  FUNCTIONS  ***
#   ***************************

class AccessSocialRoll(object):
    # Return True if the party can pass a social skill roll.
    def __init__(self, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_AVERAGE,
                          untrained_ok=False):
        self.stat_id = stat_id
        self.skill_id = skill_id
        self.rank = rank
        self.difficulty = difficulty
        self.untrained_ok = untrained_ok

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and
                camp.social_skill_roll(ob, self.stat_id, self.skill_id, self.rank, self.difficulty, self.untrained_ok, no_random=True))



