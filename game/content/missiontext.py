import random

import gears
from game.content.ghplots import missionbuilder

MOTIVE_ATTACK = "ATTACK"
MOTIVE_DEFEND = "DEFEND"
MOTIVE_GREED = "GREED"
MOTIVE_REVENGE = "REVENGE"
MOTIVE_RECON = "RECON"

MEANS_OFFENSE = "OFFENSE"
MEANS_STEAL = "STEAL"
MEANS_INFILTRATE = "INFILTRATE"
MEANS_FORTIFY = "FORTIFY"


class MissionText:

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

