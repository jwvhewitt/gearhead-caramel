import glob
import json
import pbge
import stats

SINGLETON_TYPES = dict()
ALL_JOBS = dict()

class Job(object):
    def __init__(self,name="Job",skills=(),tags=(),always_combatant=False,skill_modifiers=None):
        self.name = name
        self.skills = set()
        for sk in skills:
            if sk in SINGLETON_TYPES:
                self.skills.add(SINGLETON_TYPES[sk])
        self.tags = set()
        for t in tags:
            if t in SINGLETON_TYPES:
                self.tags.add(SINGLETON_TYPES[t])
        self.always_combatant = always_combatant
        self.skill_modifiers = dict()
        if skill_modifiers:
            for sk,mod in skill_modifiers.items():
                self.skill_modifiers[SINGLETON_TYPES[sk]] = mod
        ALL_JOBS[name] = self

    def scale_skills(self,pc,rank):
        base_skill_rank = max((rank + 20) // 10, 1)
        if pc.combatant or self.always_combatant:
            for sk in stats.COMBATANT_SKILLS:
                pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk,0),1)
        for sk in self.skills:
            pc.statline[sk] = max(base_skill_rank + self.skill_modifiers.get(sk, 0),1)

    def __str__(self):
        return self.name


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
