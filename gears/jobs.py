import glob
import json
import pbge
from . import stats, tags
import random
import collections

SINGLETON_TYPES = dict()
ALL_JOBS = dict()

class Job(object):
    MINIMUM_STATS_BY_JOB_TAG = {
        tags.Academic: {
            stats.Reflexes: 7, stats.Body: 5, stats.Speed: 7, stats.Perception: 8,
            stats.Craft: 10, stats.Ego: 8, stats.Knowledge: 12, stats.Charm: 8
        },
        tags.Adventurer: {
            stats.Reflexes: 9, stats.Body: 9, stats.Speed: 9, stats.Perception: 9,
            stats.Craft: 8, stats.Ego: 8, stats.Knowledge: 8, stats.Charm: 8
        },
        tags.CorporateWorker: {
            stats.Reflexes: 7, stats.Body: 5, stats.Speed: 7, stats.Perception: 7,
            stats.Craft: 8, stats.Ego: 8, stats.Knowledge: 8, stats.Charm: 8
        },
        tags.Craftsperson: {
            stats.Reflexes: 5, stats.Body: 5, stats.Speed: 5, stats.Perception: 9,
            stats.Craft: 12, stats.Ego: 5, stats.Knowledge: 9, stats.Charm: 5
        },
        tags.Criminal: {
            stats.Reflexes: 8, stats.Body: 5, stats.Speed: 10, stats.Perception: 10,
            stats.Craft: 10, stats.Ego: 5, stats.Knowledge: 5, stats.Charm: 5
        },
        tags.Faithworker: {
            stats.Reflexes: 5, stats.Body: 7, stats.Speed: 5, stats.Perception: 7,
            stats.Craft: 8, stats.Ego: 9, stats.Knowledge: 9, stats.Charm: 8
        },
        tags.Laborer: {
            stats.Reflexes: 8, stats.Body: 10, stats.Speed: 8, stats.Perception: 5,
            stats.Craft: 9, stats.Ego: 5, stats.Knowledge: 5, stats.Charm: 5
        },
        tags.Media: {
            stats.Reflexes: 7, stats.Body: 5, stats.Speed: 7, stats.Perception: 5,
            stats.Craft: 5, stats.Ego: 12, stats.Knowledge: 5, stats.Charm: 12
        },
        tags.Medic: {
            stats.Reflexes: 5, stats.Body: 5, stats.Speed: 5, stats.Perception: 7,
            stats.Craft: 10, stats.Ego: 8, stats.Knowledge: 10, stats.Charm: 5
        },
        tags.Merchant: {
            stats.Reflexes: 5, stats.Body: 5, stats.Speed: 5, stats.Perception: 9,
            stats.Craft: 10, stats.Ego: 10, stats.Knowledge: 7, stats.Charm: 9
        },
        tags.Military: {
            stats.Reflexes: 10, stats.Body: 10, stats.Speed: 10, stats.Perception: 10,
            stats.Craft: 5, stats.Ego: 5, stats.Knowledge: 5, stats.Charm: 5
        },
        tags.Police: {
            stats.Reflexes: 7, stats.Body: 8, stats.Speed: 7, stats.Perception: 9,
            stats.Craft: 5, stats.Ego: 10, stats.Knowledge: 5, stats.Charm: 5
        },
        tags.Politician: {
            stats.Reflexes: 5, stats.Body: 5, stats.Speed: 5, stats.Perception: 5,
            stats.Craft: 5, stats.Ego: 10, stats.Knowledge: 8, stats.Charm: 10
        },
    }

    def __init__(self,name="Job",skills=(),tags=(),always_combatant=False,skill_modifiers=None,local_requirements=()):
        self.name = name
        self.skills = set()
        for sk in skills:
            if sk in SINGLETON_TYPES:
                self.skills.add(SINGLETON_TYPES[sk])
            else:
                print("Unidentified skill: {} in {}".format(sk,self.name))
        self.tags = set()
        for t in tags:
            if t in SINGLETON_TYPES:
                self.tags.add(SINGLETON_TYPES[t])
            else:
                print("Unidentified tag: {} in {}".format(sk, self.name))
        self.always_combatant = always_combatant
        self.skill_modifiers = dict()
        if skill_modifiers:
            for sk,mod in list(skill_modifiers.items()):
                self.skill_modifiers[SINGLETON_TYPES[sk]] = mod
        self.local_requirements = set()
        for t in local_requirements:
            if t in SINGLETON_TYPES:
                self.local_requirements.add(SINGLETON_TYPES[t])
            else:
                # A city tag might be a string, so don't make a fuss if it isn't found in SINGLETON_TYPES. Unless dev
                # mode is on; then you can print a warning.
                if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                    print("Warning: {} in {} is not a singleton.".format(t, self.name))
                self.local_requirements.add(t)
        ALL_JOBS[name] = self
        #print "{} -> {}".format(name,[s.name for s in self.skills])

    def scale_skills(self,pc,rank):
        base_skill_rank = max((rank + 20) // 10, 1)
        if pc.combatant or self.always_combatant:
            for sk in stats.FUNDAMENTAL_COMBATANT_SKILLS:
                pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk,0),1, pc.statline[sk])
            for sk in stats.EXTRA_COMBAT_SKILLS:
                pc.statline[sk] = max(base_skill_rank//3 + self.skill_modifiers.get(sk, 0), 1, pc.statline[sk])
        for sk in self.skills:
            pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk, 0),1, pc.statline[sk])
        pc.renown = rank

    def get_minimum_statline(self) -> dict:
        my_stats = dict()
        stat_sums = collections.defaultdict(list)
        for t in self.tags:
            if t in self.MINIMUM_STATS_BY_JOB_TAG:
                for st in stats.PRIMARY_STATS:
                    stat_sums[st].append(self.MINIMUM_STATS_BY_JOB_TAG[t][st])
        # Construct the my_stats dict
        for st in stats.PRIMARY_STATS:
            if stat_sums[st]:
                my_stats[st] = sum(stat_sums[st])//len(stat_sums[st])
            else:
                my_stats[st] = 5
                    
        return my_stats

    def __str__(self):
        return self.name

def choose_random_job(needed_tags=(),local_tags=()):
    lt_set = set(local_tags)
    candidates = [job for job in list(ALL_JOBS.values()) if job.tags.issuperset(needed_tags) and lt_set.issuperset(job.local_requirements)]
    if candidates:
        return random.choice(candidates)
    else:
        return random.choice(list(ALL_JOBS.values()))

def init_jobs():
    protojobs = list()
    myfiles = glob.glob(pbge.util.data_dir( "jobs_*.json"))
    for f in myfiles:
        with open(f, 'rt') as fp:
            mylist = json.load(fp)
            if mylist:
                protojobs += mylist
    for j in protojobs:
        Job(**j)

