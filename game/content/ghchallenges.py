import gears
import random

#   ************************************
#   ***  DETHRONE  CHALLENGE  STUFF  ***
#   ************************************
import pbge.okapipuzzle

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


#   *************************************
#   ***  EPIDEMIC  CHALLENGE  STUFF  ***
#   *************************************

EPIDEMIC_CHALLENGE = "EPIDEMIC_CHALLENGE"


# The involvement for a diplomacy challenge identifies the NPCs in the town with the epidemic.
# The key for a diplomacy challenge is (Disease Name, Cure Name)
# No particular data required beyond the key.
#

class InvolvedIfInfected(object):
    # This Involvement is used for the epidemic autooffer. Returns True if this NPC's "secret number" matches.
    def __init__(self, metroscene):
        self.metroscene = metroscene
        self.infectiousness = random.randint(3, 6)

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.is_not_lancemate(ob) and self._is_infected(ob)) and camp.party_has_skill(gears.stats.Medicine)

    def _is_infected(self, npc):
        secret_number = sum([npc.statline[s] for s in gears.stats.PRIMARY_STATS]) + npc.birth_year + ord(npc.name[-1])
        return secret_number % self.infectiousness == 0


#   *********************************
#   ***  FIGHT  CHALLENGE  STUFF  ***
#   *********************************

FIGHT_CHALLENGE = "FIGHT_CHALLENGE"

# The involvement for a fight challenge lists the NPCs who might give the PC a combat mission
# The key for a fight challenge is (Faction_to_be_fought,)
# The data for a fight challenge should include:
#   challenge_objectives = A list of objectives that can be given by the challenge-givers; infinitive verb phrase
#   challenge_fears = A list of things that the challenge-givers can accuse the enemy faction of planning; infinitive verb phrase
#   enemy_objectives = A list of objectives that can be given by the enemy faction (key[0]); infinitive verb phrase
#   mission_intros = A list of things for mission-givers to say; primary clause
#   mission_objectives = A list of custom DescribedObjectives
#

class DescribedObjective(object):
    # objective is an objective from the missionbuilder.py unit or equivalent
    # mission_desc is a primary clause that might be used to describe this mission; may include {ENEMY_FACTION}
    def __init__(self, objective, mission_desc,
                 objective_pp="[defeat_you]", objective_ep="[defeat_you]",
                 win_pp="I defeated you", win_ep="you defeated me",
                 lose_pp="you defeated me", lose_ep="I defeated you"):
        self.objective = objective
        self.mission_desc = mission_desc
        self.objective_pp = objective_pp
        self.objective_ep = objective_ep
        self.win_pp = win_pp
        self.win_ep = win_ep
        self.lose_pp = lose_pp
        self.lose_ep = lose_ep


#   *****************************************
#   ***  GATHER  INTEL  CHALLENGE  STUFF  ***
#   *****************************************

GATHER_INTEL_CHALLENGE = "GATHER_INTEL_CHALLENGE"

# The PC needs to gather intelligence about a faction, character, scene, or whatever. This is different from a mystery
# in that the PC will mostly just be talking to people. And maybe doing a few mecha missions.
# The key for an intel challenge is (String_to_ask_people_about (noun phrase),)
# The data for a gather intel challenge should include:
#  clues: An ordered list to clues. Should be as long as the # of points needed.
#  conclusion_told: The final conclusion reached, as told to the PC by an NPC.
#  conclusion_discovered: The final conclusion as discovered by the PC on their own.
#  enemy_faction (optional): If not None, you may be offered intel missions regarding the given faction.


#   ************************************
#   ***  LOCATE  ENEMY  BASE  STUFF  ***
#   ************************************
# The involvement for a LEB challenge lists the NPCs who might give the PC a combat mission against the base
# The key for a LEB challenge is (Faction_to_be_fought,)
# The data for a locate enemy base challenge should include:
#   base_name = Is it a base? A fortress? A factory? Defaults to base.
#

LOCATE_ENEMY_BASE_CHALLENGE = "LOCATE_ENEMY_BASE_CHALLENGE"


#   ********************************
#   ***  MAKE  CHALLENGE  STUFF  ***
#   ********************************

MAKE_CHALLENGE = "MAKE_CHALLENGE"


# The involvement for a make challenge identifies the NPCs who want this thing made
# The key for a make challenge is (thing_to_be_made)
# The data for a make challenge should include:
#   why_make_it: A string describing why the stuff is being made; independent clause
#


#   ***********************************
#   ***  MISSION  CHALLENGE  STUFF  ***
#   ***********************************

MISSION_CHALLENGE = "MISSION_CHALLENGE"


# Hold on, sez you, didn't we just have a fight challenge a few challenges ago? Well yes we did. The mission challenge
# is a more flexible version of the fight challenge in that mission creation is controlled directly by whoever made
# the challenge. Also, only one mission-giver will be giving the mission at a time.
# The involvement for a mission challenge lists the NPCs who might give the PC a combat mission
# The key for a mission challenge is (Faction_to_be_fought,)
# The data for a mission challenge should include:
#   challenge_objectives = A list of objectives that can be given by the challenge-givers; infinitive verb phrase
#   challenge_rumors = A list of rumors going around town about the mission; primary clause
#   challenge_summaries = A list of descriptions of what this challenge is about; infinitive verb phrase
#       Used for memos and general talking about the challenge.
#   challenge_subject = A list of subjects to be used when asking about the rumor; noun phrase
#   mission_intros = A list of rough descriptions of mission for mission-giver to give; primary clause
#   mission_builder = A function with signature (camp, npc) that builds the mission
#


#   ***********************************
#   ***  MYSTERY  CHALLENGE  STUFF  ***
#   ***********************************


class NPCSusCard(pbge.okapipuzzle.NounSusCard):
    def __init__(self, npc, role=pbge.okapipuzzle.SUS_SUBJECT, data=None):
        super().__init__(str(npc), gameob=npc, role=role, data=data)
        self.data["image_fun"] = npc.get_portrait
        self.data["frame"] = 1


class VerbSusCardFeaturingNPC(pbge.okapipuzzle.VerbSusCard):
    def __init__(self, name, to_verb, verbed, did_not_verb, npc, role=pbge.okapipuzzle.SUS_VERB, data=None):
        super().__init__(name, to_verb, verbed, did_not_verb, npc, role, data)
        self.data["image_fun"] = npc.get_portrait
        self.data["frame"] = 1


class InvolvedIfCluesRemainAnd(object):
    # This Involvement returns True if there are unknown clue cards remaining and some other inolvement also returns
    # True.
    def __init__(self, puzzle, other_involvement=None):
        self.puzzle = puzzle
        self.other_involvement = other_involvement

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        if self.other_involvement:
            return self.puzzle.unknown_clues and self.other_involvement(camp, ob)
        else:
            return self.puzzle.unknown_clues


class InvolvedIfAssociatedCluesRemainAnd(object):
    # This Involvement returns True if there are unknown clue cards remaining which involve ob and some other
    # inolvement also returns True.
    def __init__(self, puzzle, deck_to_check, other_involvement=None):
        self.puzzle = puzzle
        self.deck_to_check = deck_to_check
        self.other_involvement = other_involvement

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        if self.other_involvement:
            return (self.puzzle.unknown_clues and any([c.is_involved(ob) for c in self.puzzle.unknown_clues]) and
                    any([c.gameob is ob for c in self.deck_to_check.cards]) and self.other_involvement(camp, ob))
        else:
            return (self.puzzle.unknown_clues and any([c.is_involved(ob) for c in self.puzzle.unknown_clues]) and
                    any([c.gameob is ob for c in self.deck_to_check.cards]))


class InvolvedIfUnassociatedCluesRemainAnd(object):
    # This Involvement returns True if there are unknown clue cards remaining which DON'T involve ob and some other
    # inolvement also returns True.
    def __init__(self, puzzle, deck_to_check, other_involvement=None):
        self.puzzle = puzzle
        self.deck_to_check = deck_to_check
        self.other_involvement = other_involvement

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        if self.other_involvement:
            return (self.puzzle.unknown_clues and any([not c.is_involved(ob) for c in self.puzzle.unknown_clues]) and
                    any([c.gameob is ob for c in self.deck_to_check.cards]) and self.other_involvement(camp, ob))
        else:
            return (self.puzzle.unknown_clues and any([not c.is_involved(ob) for c in self.puzzle.unknown_clues]) and
                    any([c.gameob is ob for c in self.deck_to_check.cards]))


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
    def __init__(self, metroscene, faction=None, exclude=()):
        self.metroscene = metroscene
        self.faction = faction or metroscene.faction
        self.exclude = set()
        self.exclude.update(exclude)

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.are_faction_allies(ob, self.faction) and camp.is_not_lancemate(ob) and ob not in self.exclude)


class InvolvedMetroNoFriendToFactionNPCs(object):
    # Return True if ob is an NPC _not_ allied with the given faction and in the same Metro area.
    def __init__(self, metroscene, faction=None, exclude=()):
        self.metroscene = metroscene
        self.faction = faction or metroscene.faction
        self.exclude = set()
        self.exclude.update(exclude)

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (
            isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
            not camp.are_faction_allies(ob, self.faction) and camp.is_not_lancemate(ob) and ob not in self.exclude
        )


class InvolvedMetroResidentNPCs(object):
    # Return True if ob is a non-lancemate NPC in the provided Metro area.
    def __init__(self, metroscene, exclude=()):
        self.metroscene = metroscene
        self.exclude = set()
        self.exclude.update(exclude)

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.is_not_lancemate(ob) and ob not in self.exclude)


class InvolvedMetroTaggedNPCs(object):
    # Return True if ob is a non-lancemate NPC with the required tags in the provided Metro area.
    def __init__(self, metroscene, tags=()):
        self.metroscene = metroscene
        self.tags = set()
        self.tags.update(tags)

    def __call__(self, camp: gears.GearHeadCampaign, ob):
        return (isinstance(ob, gears.base.Character) and ob.scene.get_metro_scene() is self.metroscene and
                camp.is_not_lancemate(ob) and self.tags.intersection(ob.get_tags()))


#   ***************************
#   ***  ACCESS  FUNCTIONS  ***
#   ***************************

class AccessSocialRoll(object):
    # Return truthy if the party can pass a social skill roll.
    def __init__(self, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_AVERAGE,
                 untrained_ok=False):
        self.stat_id = stat_id
        self.skill_id = skill_id
        self.rank = rank
        self.difficulty = difficulty
        self.untrained_ok = untrained_ok

    def __call__(self, camp: gears.GearHeadCampaign, ob, offer_dict: dict = None):
        if isinstance(ob, gears.base.Character):
            pc = camp.social_skill_roll(
                ob, self.stat_id, self.skill_id, self.rank, self.difficulty, self.untrained_ok, no_random=True
            )
            if pc:
                if offer_dict:
                    nudict = offer_dict.copy()
                    nudict["skill_info"] = " [{} + {}]".format(self.skill_id, self.stat_id)
                    return nudict
                else:
                    return True


class AccessSkillRoll(object):
    # Return truthy if the party can pass a social skill roll.
    def __init__(self, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_AVERAGE,
                 untrained_ok=False):
        self.stat_id = stat_id
        self.skill_id = skill_id
        self.rank = rank
        self.difficulty = difficulty
        self.untrained_ok = untrained_ok

    def __call__(self, camp: gears.GearHeadCampaign, ob, offer_dict: dict = None):
        pc = camp.do_skill_test(
            self.stat_id, self.skill_id, self.rank, self.difficulty, self.untrained_ok, no_random=True
        )
        if pc:
            if offer_dict:
                nudict = offer_dict.copy()
                nudict["skill_info"] = " [{} + {}]".format(self.skill_id, self.stat_id)
                return nudict
            else:
                return True
