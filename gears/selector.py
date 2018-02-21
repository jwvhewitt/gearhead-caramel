import tags

DESIGN_LIST = list()

def calc_threat_points(level,percent=20):
    # Copied from GH2.
    level = min(max(level,0),300)
    if level < 31:
        it = level * 10000 // 30
    else:
        it = 20 * level * level - 900 * level + 19040
    return it * percent

class MechaShoppingList(object):
    """Examine the DESIGN_LIST, locate mecha that fit the criteria given."""
    def __init__(self,hi_price,fac=None,env=tags.GroundEnv):
        self.hi_price = hi_price
        self.fac = fac
        self.role = role
        self.env = env
        self.best_choices = list()
        self.backup_choices = list()
        self.by_role = dict()

print calc_threat_points(10)
print calc_threat_points(20)
print calc_threat_points(30)
print calc_threat_points(40)
print calc_threat_points(50)
print calc_threat_points(60)
print calc_threat_points(70)
print calc_threat_points(80)
print calc_threat_points(90)
print calc_threat_points(100)
