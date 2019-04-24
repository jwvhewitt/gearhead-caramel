import pbge
from game.content import GHNarrativeRequest, PLOT_LIST
from pbge.plots import Adventure


class AdventureSeed(Adventure):
    def __init__(self, camp, name, adv_type, adv_return, pstate=None, auto_set_rank=True, restore_at_end=True):
        # adv_return is a (Destination,Entrance) tuple.
        super(AdventureSeed, self).__init__(name=name, world=None)
        self.pstate = pstate or pbge.plots.PlotState(adv=self,rank=camp.pc.renown)
        self.pstate.adv = self
        self.pstate.elements["ADVENTURE_RETURN"] = adv_return
        self.adv_type = adv_type
        self.auto_set_rank = auto_set_rank
        self.restore_at_end = restore_at_end
        self.started = False

    def __call__(self, camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        if self.auto_set_rank:
            self.pstate.rank = camp.pc.renown
        nart = GHNarrativeRequest(camp, self.pstate, self.adv_type, PLOT_LIST)
        if nart.story:
            nart.build()
            self.started = True
            camp.check_trigger("UPDATE")
        else:
            for e in nart.errors:
                print e

    def restore_party(self, camp):
        """
        Restore the party to health, removing the charge from their credits.
        :type camp: gears.GearHeadCampaign
        """
        # Sort any incapacitated members first.
        camp.bring_out_your_dead()

        # Next, restore the party.
        repair_total = 0
        for pc in camp.party + camp.incapacitated_party:
            rcdict = pc.get_repair_cost()
            pc.wipe_damage()
            repair_total += sum([v for k,v in rcdict.iteritems()])
            if hasattr(pc, "mp_spent"):
                pc.mp_spent = 0
            if hasattr(pc, "sp_spent"):
                pc.sp_spent = 0

            for part in pc.descendants():
                if hasattr(part,"get_reload_cost"):
                    repair_total += part.get_reload_cost()
                    part.spent = 0
        print repair_total

    def end_adventure(self,camp):
        if self.restore_at_end:
            self.restore_party(camp)
        super(AdventureSeed,self).end_adventure(camp)

class MissionObjective(object):
    """
    An optional objectives record for missions to use.
    """
    def __init__(self,name,mo_points,optional=False,secret=False):
        self.name = name
        self.mo_points = mo_points
        self.awarded_points = 0
        self.optional = optional
        self.failed = False
        self.secret = secret
    def win(self,completion=100):
        self.awarded_points = max(( self.mo_points * completion ) // 100,1)

