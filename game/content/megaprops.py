from game import teams
import gears

class MegaProp(teams.Team):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def predeploy(self, gb, room):
        for p in self.contents:
            pass

