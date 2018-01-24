
ARE_ENEMIES = -1
ARE_NEUTRAL = 0
ARE_ALLIES = 1

class Team( object ):
    # Teams organize the models on the playing field. 
    def __init__( self, name='', faction=None, enemies=(), allies=() ):
        self.name = name
        self.faction = faction
        self.reactions = dict()
        self.contents = list()
        self.home = None
        for e in enemies:
            self.set_mutual_reaction(e,ARE_ENEMIES)
        for a in allies:
            self.set_mutual_reaction(a,ARE_ALLIES)

    def set_mutual_reaction( self, other_team, reaction ):
        self.reactions[other_team] = reaction
        other_team.reactions[self] = reaction
    def make_enemies( self, other_team ):
        self.set_mutual_reaction(other_team,ARE_ENEMIES)
    def is_enemy( self, other_team ):
        return self.reactions.get(other_team) == ARE_ENEMIES

    def predeploy( self, gb, room ):
        self.home = room.area
        if self.contents:
            for c in self.contents:
                gb.local_teams[c]=self
            room.contents += self.contents

