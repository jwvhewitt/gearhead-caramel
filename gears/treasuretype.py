
class TreasureType():
    def __init__(self, skill=None, treasures=()):
        self.skill = skill
        self.treasures = treasures

    def generate_treasure(self, camp, mon, item_fun):
        # camp is the campaign.
        # mon is the monster whose death triggered treasure generation.
        # item_fun is the get_design_by_full_name function from selector, which I can't import directly due to scope
        #  issues.
        pass
