from . import exploration
from . import combat
from . import teams
from . import content
from . import ghdialogue
from . import configedit
from . import invoker
from . import cosplay
from . import chargen
from . import services
from . import fieldhq
from . import mechabrowser
from . import geareditor
from . import devstuff
from game.fieldhq import backpack
import pbge


#def start_campaign(pc_egg,adv_type="SCENARIO_DEADZONEDRIFTER"):
def start_campaign(pc_egg, adv_type="SCENARIO_MOCHA"):
    pbge.please_stand_by()
    camp = content.narrative_convenience_function(pc_egg,adv_type=adv_type)
    if camp:
        camp.place_party()
        camp.save()
        camp.play()


def init_game():
    content.backstory.init_backstory()
    content.ghplots.init_plots()