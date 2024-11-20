import random

import gears
from game.content.ghplots import missionbuilder

DEFAULT = "DEFAULT"

MOTIVE_ATTACK = "ATTACK"
MOTIVE_DEFEND = "DEFEND"
MOTIVE_GREED = "GREED"
MOTIVE_REVENGE = "REVENGE"
MOTIVE_RECON = "RECON"

MEANS_OFFENSE = "OFFENSE"
MEANS_STEAL = "STEAL"
MEANS_INFILTRATE = "INFILTRATE"
MEANS_FORTIFY = "FORTIFY"

OB_ALLIED_FORCES = "OB_ALLIED_FORCES"
OB_ALLIED_TARGET = "OB_ALLIED_TARGET"
OB_ENEMY_TERRITORY = "OB_ENEMY_TERRITORY"
OB_INFORMATION = "INFORMATION"
OB_LOCATION = "LOCATION"
OB_MACGUFFIN = "MACGUFFIN"

ALLIED_FACTION_TAG = "ALLIED_FACTION_TAG"
ENEMY_FACTION_TAG = "ENEMY_FACTION_TAG"

ALLIED_FACTION_EXISTS = "ALLIED_FACTION_EXISTS"
ALLY_IS_METRO_ALLY = "ALLY_IS_METRO_ALLY"
ALLY_IS_METRO_ENEMY = "ALLY_IS_METRO_ENEMY"
ENEMY_FACTION_EXISTS = "ENEMY_FACTION_EXISTS"
ENEMY_IS_METRO_ALLY = "ENEMY_IS_METRO_ALLY"
ENEMY_IS_METRO_ENEMY = "ENEMY_IS_METRO_ENEMY"


class MTVerb:
    def __init__(self, simple_present,  simple_past, neg_present, neg_past, objects=(), obvious_motives=(),  needed_tags=(), forbidden_tags=()):
        # The negative form of the verb needs to take the same object
        self.simple_present = simple_present
        self.simple_past = simple_past
        self.neg_present = neg_present
        self.neg_past = neg_past
        self.objects = objects
        self.obvious_motives = obvious_motives
        self.needed_tags = set(needed_tags)
        self.forbidden_tags = set(forbidden_tags)
        
    def matches(self, context):
        if self.needed_tags.issubset(context) and not self.forbidden_tags.intersection(context):
            return True


class MTNoun:
    def __init__(self, name,  needed_tags=(), forbidden_tags=()):
        self.name = name
        self.needed_tags = set(needed_tags)
        self.forbidden_tags = set(forbidden_tags)

    def matches(self, context):
        if self.needed_tags.issubset(context) and not self.forbidden_tags.intersection(context):
            return True

        
MOTIVE_VERBS = {
    DEFAULT: (
        MTVerb("steal",  "stole", "guard", "guarded", objects=(OB_MACGUFFIN, OB_INFORMATION ), needed_tags={MEANS_STEAL}), 
    ), 
    MOTIVE_ATTACK: (
        MTVerb("destroy",  "destroyed",  "protect",  "protected",  objects=(OB_ALLIED_TARGET, ), forbidden_tags={MEANS_FORTIFY, MEANS_STEAL}), 
        MTVerb("occupy", "occupied", "defend", "defended", objects=(OB_LOCATION), needed_tags={MEANS_FORTIFY}), 
    ), 
    MOTIVE_DEFEND: (
        MTVerb("defend", "defended", "capture", "captured", objects=(OB_ENEMY_TERRITORY, ),  forbidden_tags={MEANS_OFFENSE}),
        MTVerb("eliminate", "eliminated", "fight for", "fought for",  objects=(OB_ALLIED_FORCES, OB_ALLIED_TARGET)),  
    ), 
    MOTIVE_GREED: (
        MTVerb("obtain",  "obtained", "secure", "secured", objects=(OB_MACGUFFIN, OB_INFORMATION ),), 
    ), 
    MOTIVE_REVENGE: (
        MTVerb("humiliate", "humiliated", "fight for", "scored a victory for", objects=(OB_ALLIED_FORCES, ),  needed_tags={}), 
    ), 
    MOTIVE_RECON: (
        MTVerb("learn about", "learned about", "secure", "secured", objects=(OB_ALLIED_TARGET, OB_INFORMATION)),
    )
}


ALL_OBJECTS = {
    OB_ALLIED_FORCES: (
        MTNoun("{ALLIED_FACTION}", needed_tags={ALLIED_FACTION_EXISTS, }), 
        MTNoun("{METROSCENE}'s defenders", needed_tags=(ENEMY_IS_METRO_ENEMY, )), 
        MTNoun("{METROSCENE}'s enemies", needed_tags=(ENEMY_IS_METRO_ALLY, )), 
    ), 
    OB_ALLIED_TARGET: (
        MTNoun("{ALLIED_FACTION}'s base", needed_tags={ALLIED_FACTION_EXISTS, }), 
        MTNoun("the armory"),  MTNoun("the {METROSCENE} power plant", needed_tags={ENEMY_IS_METRO_ENEMY, }), 
    ), 
    OB_ENEMY_TERRITORY: (
        MTNoun("{ENEMY_FACTION}'s base",  needed_tags=(ENEMY_FACTION_EXISTS, )), 
        MTNoun("this position"), MTNoun("{ENEMY_FACTION}'s hideout",  needed_tags=(ENEMY_FACTION_EXISTS, (ENEMY_FACTION_TAG, gears.tags.Criminal)))
    ), 
    OB_INFORMATION: (
        MTNoun("{ALLIED_FACTION}'s new mecha design",  needed_tags={ALLIED_FACTION_EXISTS, }), 
        MTNoun("some secret information"), 
    ), 
    OB_LOCATION: (
        MTNoun("{METROSCENE}", ), 
    ), 
    OB_MACGUFFIN: (
        MTNoun("{ALLIED_FACTION}'s new prototype",  needed_tags={ALLIED_FACTION_EXISTS, }), 
        MTNoun("the shipment of {RESOURCE}"), 
    ), 
}


MEANS_VERBS = {
    DEFAULT: (
        MTVerb("enter","trespassed into","defend","defended", objects=(OB_LOCATION,), forbidden_tags=(ENEMY_IS_METRO_ALLY,)), 
        MTVerb("blockade","blockaded","patrol","patrolled", objects=(OB_LOCATION,), forbidden_tags=(ENEMY_IS_METRO_ENEMY,)), 
        MTVerb("invade", "invaded", "defend", "defended", objects=(OB_LOCATION, OB_ALLIED_TARGET), needed_tags=(ENEMY_IS_METRO_ENEMY,)),
    ), 
    MEANS_OFFENSE: (
        MTVerb("attack","defeated","fight for","defended", objects=(OB_ALLIED_FORCES,)), 
        MTVerb("sow chaos", "wrought destruction", "stop the destruction", "prevented disaster", needed_tags=(MOTIVE_REVENGE,), forbidden_tags=(ENEMY_IS_METRO_ALLY,)),
    ), 
    MEANS_STEAL: (
        MTVerb("raid","raided","protect","protected", objects=(OB_LOCATION,)), 
    ), 
    MEANS_INFILTRATE: (
        MTVerb("scout","scouted","patrol","defended", objects=(OB_LOCATION,)), 
    ), 
    MEANS_FORTIFY: (
        MTVerb("secure","secured","clear","cleared", objects=(OB_LOCATION,)), 
    ), 
}

RESOURCE_NOUNS = (
    MTNoun("impervium ore"), MTNoun("mecha parts"), MTNoun("PreZero technology"), MTNoun("spare parts"), 
    MTNoun("weapons"),  MTNoun("ammunition"), MTNoun("luxury goods",  needed_tags={MOTIVE_GREED, (ENEMY_FACTION_TAG, gears.tags.Criminal)}), 
)


class MissionText:
    
    # Needed Outputs:
    # - Mission_Description
    # - Objective_PP, Objective_EP
    # - Win_PP, Win_EP
    # - Lose_PP, Lose_EP
    # PP = Player Perspective, EP = Enemy Perspective
    # objective is a present tense verb phrase describing each team's mission.
    # win is a clause in simple past describing the outcome if the player wins
    # lose is a clause in simple past describing the outcome if the player loses

    _MISSION_DESCS = (
        "[your_job] {means_vp_npresent}",
        "[your_job] {means_vp_npresent} in order to {motive_vp_npresent}",
        "[enemy_is_going_to] {motive_vp_present}, so [your_job] {means_vp_npresent}",
        "[enemy_is_going_to] {means_vp_present} in order to {motive_vp_present}",
        "[enemy_is_going_to] {means_vp_present}, so [your_job] {motive_vp_npresent}",
    )

    def __init__(self, camp: gears.GearHeadCampaign, objectives, metroscene, allied_faction=None, enemy_faction=None):
        # Give us some text that can be used to generate a MissionGrammar and also some text that can be used by the
        # mission-giver to describe the mission.
        motive_candidates = list()
        means_candidates = list()
        if {
            missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_DEFEAT_ARMY,
            missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_DESTROY_ARTILLERY,
            missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,
        }.intersection(objectives):
            means_candidates.append(MEANS_OFFENSE)
            if enemy_faction and camp.are_faction_allies(metroscene, enemy_faction):
                motive_candidates.append(MOTIVE_DEFEND)
            elif enemy_faction and gears.tags.Criminal in enemy_faction.factags:
                motive_candidates.append(MOTIVE_GREED)

        if {
            missionbuilder.BAMO_DEFEAT_THE_BANDITS, missionbuilder.BAMO_RECOVER_CARGO,
            missionbuilder.BAMO_CAPTURE_THE_MINE, missionbuilder.BAMO_PROTECT_BUILDINGS,
            missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL, missionbuilder.BAMO_SURVIVE_THE_AMBUSH,
        }.intersection(objectives):
            means_candidates.append(MEANS_STEAL)
            motive_candidates.append(MOTIVE_GREED)
            if enemy_faction and {gears.tags.Military, gears.tags.CorporateWorker}.intersection(enemy_faction.factags):
                motive_candidates.append(MOTIVE_RECON)
            if enemy_faction and {gears.tags.Criminal, gears.tags.CorporateWorker}.intersection(enemy_faction.factags):
                means_candidates.append(MEANS_STEAL)

        if {
            missionbuilder.BAMO_EXTRACT_ALLIED_FORCES, missionbuilder.BAMO_AID_ALLIED_FORCES,
            missionbuilder.BAMO_SURVIVE_THE_AMBUSH, missionbuilder.BAMO_LOCATE_ENEMY_FORCES,
            missionbuilder.BAMO_DEFEAT_NPC, missionbuilder.BAMO_RESCUE_NPC, missionbuilder.BAMO_SURVIVE_THE_AMBUSH,
        }.intersection(objectives):
            means_candidates.append(MEANS_INFILTRATE)
            motive_candidates.append(MOTIVE_RECON)
            if enemy_faction and gears.tags.Criminal in enemy_faction.factags:
                motive_candidates.append(MOTIVE_GREED)

        if {
            missionbuilder.BAMO_CAPTURE_BUILDINGS, missionbuilder.BAMO_CAPTURE_THE_MINE,
            missionbuilder.BAMO_DESTROY_ARTILLERY, missionbuilder.BAMO_STORM_THE_CASTLE,
            missionbuilder.BAMO_DEFEAT_ARMY, missionbuilder.BAMO_NEUTRALIZE_ALL_DRONES,
        }.intersection(objectives):
            means_candidates.append(MEANS_FORTIFY)
            if enemy_faction and camp.are_faction_allies(metroscene, enemy_faction):
                motive_candidates.append(MOTIVE_DEFEND)
            else:
                motive_candidates.append(MOTIVE_ATTACK)
            if enemy_faction and {gears.tags.Politician, gears.tags.CorporateWorker}.intersection(enemy_faction.factags):
                motive_candidates.append(MOTIVE_DEFEND)

        if camp.are_faction_enemies(metroscene, enemy_faction):
            motive_candidates.append(MOTIVE_ATTACK)
        elif camp.are_faction_allies(metroscene, enemy_faction):
            motive_candidates.append(MOTIVE_DEFEND)

        if enemy_faction and gears.tags.Military in enemy_faction.factags and not camp.are_faction_allies(enemy_faction, metroscene):
            motive_candidates.append(MOTIVE_ATTACK)

        if camp.are_faction_enemies(allied_faction, enemy_faction):
            motive_candidates.append(MOTIVE_REVENGE)

        if enemy_faction and gears.tags.Criminal in enemy_faction.factags:
            motive_candidates.append(MOTIVE_GREED)

        if not motive_candidates:
            motive_candidates = [MOTIVE_ATTACK, MOTIVE_GREED, MOTIVE_RECON]

        if not means_candidates:
            means_candidates = [MEANS_OFFENSE, MEANS_INFILTRATE]

        motive = random.choice(motive_candidates)
        means = random.choice(means_candidates)

        context = set()
        format_dict = dict()
        if allied_faction:
            format_dict["ALLIED_FACTION"] = allied_faction
            context.add(ALLIED_FACTION_EXISTS)
            for ft in allied_faction.factags:
                context.add((ALLIED_FACTION_TAG, ft))
            context.add((ALLIED_FACTION_TAG, allied_faction.get_faction_tag()))
            if camp.are_faction_enemies(metroscene, allied_faction):
                context.add(ALLY_IS_METRO_ENEMY)
            elif camp.are_faction_allies(metroscene, allied_faction):
                context.add(ALLY_IS_METRO_ALLY)
        if enemy_faction:
            format_dict["ENEMY_FACTION"] = enemy_faction
            context.add(ENEMY_FACTION_EXISTS)
            for ft in enemy_faction.factags:
                context.add((ENEMY_FACTION_TAG, ft))
            context.add((ENEMY_FACTION_TAG, enemy_faction.get_faction_tag()))
            if camp.are_faction_enemies(metroscene, enemy_faction):
                context.add(ENEMY_IS_METRO_ENEMY)
            elif camp.are_faction_allies(metroscene, enemy_faction):
                context.add(ENEMY_IS_METRO_ALLY)
        format_dict["METROSCENE"] = metroscene
        format_dict["RESOURCE"] = self.get_random_item(RESOURCE_NOUNS, context)

        v_candidates = self.get_candidates(MOTIVE_VERBS[DEFAULT], context) + self.get_candidates(MOTIVE_VERBS[motive], context)
        while v_candidates:
            motive_verb = random.choice(v_candidates)
            v_candidates.remove(motive_verb)
            # Start constructing our noun phrases
            self.motive_vp_present = motive_verb.simple_present
            self.motive_vp_past = motive_verb.simple_past
            self.motive_vp_npresent = motive_verb.neg_present
            self.motive_vp_npast = motive_verb.neg_past
            if motive_verb.objects:
                candidates = list()
                for ot in motive_verb.objects:
                    candidates += self.get_candidates(ALL_OBJECTS[ot],  context)
                if candidates:
                    my_ob = random.choice(candidates)
                    self.motive_vp_present += " " + my_ob.name
                    self.motive_vp_past += " " + my_ob.name
                    self.motive_vp_npresent += " " + my_ob.name
                    self.motive_vp_npast += " " + my_ob.name
                else:
                    continue

        v_candidates = self.get_candidates(MEANS_VERBS[DEFAULT], context) + self.get_candidates(MEANS_VERBS[means], context)
        while v_candidates:
            means_verb = random.choice(v_candidates)
            v_candidates.remove(means_verb)
            # Start constructing our noun phrases
            self.means_vp_present = means_verb.simple_present
            self.means_vp_past = means_verb.simple_past
            self.means_vp_npresent = means_verb.neg_present
            self.means_vp_npast = means_verb.neg_past
            if means_verb.objects:
                candidates = list()
                for ot in means_verb.objects:
                    candidates += self.get_candidates(ALL_OBJECTS[ot],  context)
                if candidates:
                    my_ob = random.choice(candidates)
                    self.means_vp_present += " " + my_ob.name
                    self.means_vp_past += " " + my_ob.name
                    self.means_vp_npresent += " " + my_ob.name
                    self.means_vp_npast += " " + my_ob.name
                else:
                    continue

        self.objective_pp = random.choice((self.motive_vp_npresent, self.means_vp_npresent)).format(**format_dict)
        self.objective_ep = random.choice((self.motive_vp_present, "{} to {}".format(self.means_vp_present, self.motive_vp_present))).format(**format_dict)
        self.win_pp = "I {}".format(random.choice((self.motive_vp_npast, self.means_vp_npast))).format(**format_dict)
        self.win_ep = "you {}".format(random.choice((self.motive_vp_npast, self.means_vp_npast))).format(**format_dict)
        self.lose_pp = "you {}".format(random.choice((self.motive_vp_past, self.means_vp_past))).format(**format_dict)
        self.lose_ep = "I {}".format(random.choice((self.motive_vp_past, self.means_vp_past))).format(**format_dict)

        mission_desc_dict = dict(
            motive_vp_present=self.motive_vp_present, means_vp_present=self.means_vp_present,
            motive_vp_past=self.motive_vp_past, means_vp_past=self.means_vp_past,
            motive_vp_npresent=self.motive_vp_npresent, means_vp_npresent = self.means_vp_npresent,
            motive_vp_npast=self.motive_vp_npast, means_vp_npast=self.means_vp_npast,
        )

        self.mission_description = random.choice(self._MISSION_DESCS).format(**mission_desc_dict).format(**format_dict)

    def get_random_item(self, candidates, context):
        return random.choice(self.get_candidates(candidates, context))
    
    @staticmethod
    def get_candidates(full_list, context):
        return [item for item in full_list if item.matches(context)]

    def get_mission_grammar_dict(self):
        return dict(
            objective_pp=self.objective_pp, objective_ep=self.objective_ep, win_pp=self.win_pp,
            win_ep=self.win_ep, lose_pp=self.lose_pp, lose_ep=self.lose_ep
        )
    

def test_mission_text(camp):
    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
        missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL, missionbuilder.BAMO_CAPTURE_BUILDINGS
    )

    for t in range(10):
        my_obs = random.sample(OBJECTIVES, 2)
        my_enemy = random.choice([gears.factions.AegisOverlord, gears.factions.BoneDevils, gears.factions.ClanIronwind])
        mytext = MissionText(camp, my_obs, camp.scene, allied_faction=gears.factions.TerranFederation, enemy_faction=my_enemy)
        print(my_enemy)
        print(my_obs)
        print(mytext.get_mission_grammar_dict())


    
