
import collections
from pbge.plots import Plot,PlotError
import pbge
import gears
from .. import exploration
import inspect

import ghterrain
import waypoints
import ghcutscene
import mechtarot

import mocha
import dd_main
import dd_tarot

# The list of plots will be stored as a dictionary based on label.
PLOT_LIST = collections.defaultdict( list )
UNSORTED_PLOT_LIST = list()
def harvest( mod ):
    for name in dir( mod ):
        o = getattr( mod, name )
        if inspect.isclass( o ) and issubclass( o , Plot ) and o is not Plot and o is not mechtarot.TarotCard:
            PLOT_LIST[ o.LABEL ].append( o )
            UNSORTED_PLOT_LIST.append( o )
            # print o.__name__

harvest(mocha)
harvest(dd_main)
harvest(dd_tarot)


class GHNarrativeRequest(pbge.plots.NarrativeRequest):
    def generate_tarot_card( self, pstate, tags ):
        """Locate a plot which matches the request, init it, and return it."""
        # Create a list of potential plots.
        candidates = list()
        tagset = set(tags)
        for sp in self.plot_list['TAROT']:
            if tagset.issubset(sp.TAGS) and sp.matches( pstate ):
                candidates.append( sp )
        if candidates:
            cp = None
            while candidates and not cp:
                cpc = self.random_choice_by_weight( candidates )
                candidates.remove( cpc )
                try:
                    cp = cpc(self,pstate)
                except PlotError:
                    cp = None
            if not cp:
                self.errors.append( "No plot accepted for {0}".format( tags ) )
            return cp
        else:
            self.errors.append( "No plot found for {0}".format( tags ) )

    def add_tarot_card( self, myplot, tarot_tags, spstate=None, ident=None, necessary=True ):
        if not spstate:
            spstate = pbge.plots.PlotState().based_on(myplot)
        if not ident:
            ident = "_autoident_{0}".format( len( myplot.subplots ) )
        sp = self.generate_tarot_card( spstate, tarot_tags )
        if necessary and not sp:
            #print "Fail: {}".format(splabel)
            myplot.fail( self )
        elif sp:
            #print "Success: {}".format(splabel)
            myplot.subplots[ident] = sp
        return sp


def narrative_convenience_function( adv_type="SCENARIO_DEADZONEDRIFTER" ):
#def narrative_convenience_function(adv_type="SCENARIO_MOCHA"):
    # Start an adventure.
    init = pbge.plots.PlotState(rank=1)
    camp = gears.GearHeadCampaign(explo_class=exploration.Explorer)
    nart = GHNarrativeRequest(camp,init,adv_type,PLOT_LIST)
    if nart.story:
        nart.build()
        return nart.camp
    else:
        for e in nart.errors:
            print e


def test_mocha_encounters():
    frontier = list()
    possible_states = list()
    move_cost = collections.defaultdict(int)
    for p in PLOT_LIST['MOCHA_MINTRO']:
        frontier.append(p.CHANGES)

    while frontier:
        current = frontier.pop()
        possible_states.append(current)
        # Find the neighbors
        for p in PLOT_LIST['MOCHA_MENCOUNTER']:
            if all( p.REQUIRES[k] == current.get(k,0) for k in p.REQUIRES.iterkeys() ):
                dest = current.copy()
                dest.update(p.CHANGES)
                new_cost = move_cost[repr(current)] + 1
                if new_cost <= 2 and ( repr(dest) not in move_cost or new_cost < move_cost[repr(dest)] ):
                    move_cost[repr(dest)] = new_cost
                    frontier.append(dest)
    # Finally, print an analysis.
    print "Possible States: {}".format(possible_states)
    done_stuff = set()
    for s in possible_states:
        if move_cost[repr(s)] < 2:
            ec = (mocha.ENEMY,s.get(mocha.ENEMY,0),mocha.COMPLICATION,s.get(mocha.COMPLICATION,0))
            EnemyComp = [ p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                            if s.get(mocha.ENEMY,0) == p.REQUIRES.get(mocha.ENEMY,0)
                             and mocha.ENEMY in p.REQUIRES
                             and mocha.COMPLICATION in p.REQUIRES
                             and s.get(mocha.COMPLICATION,0) == p.REQUIRES.get(mocha.COMPLICATION,0)]
            if ec not in done_stuff and not EnemyComp:
                print "No encounter found for Enemy:{} Complication:{}".format(ec[1],ec[3])
            done_stuff.add(ec)

            es = (mocha.ENEMY,s.get(mocha.ENEMY,0),mocha.STAKES,s.get(mocha.STAKES,0))
            EnemyStakes = [ p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                            if s.get(mocha.ENEMY,0) == p.REQUIRES.get(mocha.ENEMY,0)
                             and mocha.ENEMY in p.REQUIRES
                             and mocha.STAKES in p.REQUIRES
                             and s.get(mocha.STAKES,0) == p.REQUIRES.get(mocha.STAKES,0)]
            if es not in done_stuff and not EnemyStakes:
                print "No encounter found for Enemy:{} Stakes:{}".format(es[1],es[3])
            done_stuff.add(es)

            cs = (mocha.COMPLICATION,s.get(mocha.COMPLICATION,0),mocha.STAKES,s.get(mocha.STAKES,0))
            CompStakes = [ p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                            if s.get(mocha.COMPLICATION,0) == p.REQUIRES.get(mocha.COMPLICATION,0)
                             and mocha.COMPLICATION in p.REQUIRES
                             and mocha.STAKES in p.REQUIRES
                             and s.get(mocha.STAKES,0) == p.REQUIRES.get(mocha.STAKES,0)]
            if cs not in done_stuff and not CompStakes:
                print "No encounter found for Complication:{} Stakes:{}".format(cs[1],cs[3])
            done_stuff.add(cs)

    for s in possible_states:
        if move_cost[repr(s)] >= 2:
            choices = [ p for p in PLOT_LIST['MOCHA_MHOICE'] if all( p.REQUIRES[k] == s.get(k,0) for k in p.REQUIRES.iterkeys() )]
            if len(choices) < 4:
                print "Only {} choices for {}".format(len(choices),s)




#test_mocha_encounters()
