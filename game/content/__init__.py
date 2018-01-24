
import collections
from pbge.plots import Plot
import pbge
import gears
from .. import exploration
import inspect

import ghterrain
import waypoints
import ghcutscene

import mocha

# The list of plots will be stored as a dictionary based on label.
PLOT_LIST = collections.defaultdict( list )
UNSORTED_PLOT_LIST = list()
def harvest( mod ):
    for name in dir( mod ):
        o = getattr( mod, name )
        if inspect.isclass( o ) and issubclass( o , Plot ) and o is not Plot:
            PLOT_LIST[ o.LABEL ].append( o )
            UNSORTED_PLOT_LIST.append( o )
            # print o.__name__

harvest(mocha)

def narrative_convenience_function( adv_type="SCENARIO_MOCHA" ):
    # Start an adventure.
    init = pbge.plots.PlotState(rank=1)
    camp = gears.GearHeadCampaign(explo_class=exploration.Explorer)
    nart = pbge.plots.NarrativeRequest(camp,init,adv_type,PLOT_LIST)
    if nart.story:
        nart.build()
        return nart.camp



