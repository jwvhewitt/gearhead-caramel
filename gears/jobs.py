import glob
import json
import pbge
import stats
import random

SINGLETON_TYPES = dict()
ALL_JOBS = dict()

class Job(object):
    def __init__(self,name="Job",skills=(),tags=(),always_combatant=False,skill_modifiers=None,local_requirements=()):
        self.name = name
        self.skills = set()
        for sk in skills:
            if sk in SINGLETON_TYPES:
                self.skills.add(SINGLETON_TYPES[sk])
            else:
                print "Unidentified symbol: {} in {}".format(sk,self.name)
        self.tags = set()
        for t in tags:
            if t in SINGLETON_TYPES:
                self.tags.add(SINGLETON_TYPES[t])
            else:
                print "Unidentified symbol: {} in {}".format(t,self.name)
        self.always_combatant = always_combatant
        self.skill_modifiers = dict()
        if skill_modifiers:
            for sk,mod in skill_modifiers.items():
                self.skill_modifiers[SINGLETON_TYPES[sk]] = mod
        self.local_requirements = set()
        for t in local_requirements:
            if t in SINGLETON_TYPES:
                self.local_requirements.add(SINGLETON_TYPES[t])
            else:
                print "Unidentified symbol: {} in {}".format(t,self.name)
        ALL_JOBS[name] = self

    def scale_skills(self,pc,rank):
        base_skill_rank = max((rank + 20) // 10, 1)
        if pc.combatant or self.always_combatant:
            for sk in stats.COMBATANT_SKILLS:
                pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk,0),1)
        for sk in self.skills:
            pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk, 0),1)
        pc.renown = rank

    def __str__(self):
        return self.name

def choose_random_job(needed_tags=(),local_tags=()):
    lt_set = set(local_tags)
    candidates = [job for job in ALL_JOBS.values() if job.tags.issuperset(needed_tags) and lt_set.issuperset(job.local_requirements)]
    if candidates:
        return random.choice(candidates)
    else:
        return random.choice(ALL_JOBS.values())

def init_jobs():
    protojobs = list()
    myfiles = glob.glob(pbge.util.data_dir( "jobs_*.json"))
    for f in myfiles:
        with open(f, 'rb') as fp:
            mylist = json.load(fp)
            if mylist:
                protojobs += mylist
    for j in protojobs:
        Job(**j)
