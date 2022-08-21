from . import stats
import random

class TreasureType():
    def __init__(self, skill=None, stat=stats.Craft, treasures=()):
        self.skill = skill
        self.stat = stat
        self.treasures = treasures

    def generate_treasure(self, camp, mon, item_fun):
        # camp is the campaign.
        # mon is the monster whose death triggered treasure generation.
        # item_fun is the get_design_by_full_name function from selector, which I can't import directly due to scope
        #  issues.
        # This method returns either a single piece of treasure or None.
        mon.treasure_type = None
        if not self.treasures:
            print("Error: {} has no treasure. {}".format(mon, self.treasures))
            return None
        if self.skill:
            skill_roll = camp.make_skill_roll(self.stat, self.skill) - (mon.threat + 85)
            if skill_roll > 0:
                max_treasure = min(len(self.treasures), skill_roll//15+1)
                treasure_name = random.choice(self.treasures[:max_treasure])
                if treasure_name:
                    return item_fun(treasure_name)
        else:
            return item_fun(random.choice(self.treasures))

