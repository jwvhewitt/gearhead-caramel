from pbge.plots import Plot, PlotState
from game.content import ghwaypoints,ghterrain,plotutility,backstory
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from . import dd_main,dd_customobjectives
from . import tarot_cards
from .tarot_cards import ME_FACTION,ME_PERSON,ME_CRIME,ME_PUZZLEITEM,ME_ACTOR,ME_LIABILITY,CrimeObject,ME_POSITION, ME_PROBLEM
from game.content import mechtarot
from game.content.mechtarot import CONSEQUENCE_WIN,CONSEQUENCE_LOSE
import game.content.plotutility
import game.content.gharchitecture
from . import dd_combatmission
import collections
from . import missionbuilder


#   **************************
#   ***  MT_SOCKET_Accuse  ***
#   **************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_CARD
#   ME_SOCKET

class PriceyHeadMk3(Plot):
    # - Make sure there's a Bounty Hunter in town at all times.
    # - Speak to the Bounty Hunter, or an ally, to activate your incrimination.
    # - As a bonus, entering the same room as the NPC also triggers the mission.
    LABEL = "MT_SOCKET_Accuse"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PERSON in pstate.elements and pstate.elements[ME_PERSON]

    def custom_init(self, nart):
        # Ensure there will always be at least one Guardian here.
        self.add_sub_plot(nart,"ENSURE_JOB_REPRESENTATION", elements={"JOB": gears.jobs.ALL_JOBS["Bounty Hunter"]})
        if not self.elements[ME_PERSON].combatant:
            self.elements[ME_PERSON].combatant = True
            self.elements[ME_PERSON].job.scale_skills(self.elements[ME_PERSON],self.elements[ME_PERSON].renown)
        self.mission_seed = None
        self.card = None
        self.see_exit = False
        return True

    def is_appropriate_judge(self,npc,camp):
        return camp.are_faction_allies(npc, self.elements["METROSCENE"]) or gears.tags.Police in npc.job.tags

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if npc is not self.elements[ME_PERSON] and self.is_appropriate_judge(npc,camp) and not self.mission_seed:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig:
                card = mysig[0][0]
                # Alright, we have someone with the power to incriminate. Harvest some information.
                crime = card.elements.get(ME_CRIME)
                if not crime:
                    crimed = "did something terrible"
                else:
                    crimed = crime.ed
                goffs.append(Offer(
                    "[I_ALREADY_KNOW] A bounty just went out for {ME_PERSON}'s arrest... if you're fast, you might be the one to claim it.".format(**self.elements),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(self.elements[ME_PERSON],crimed),}
                ))
                self.card = card

        return goffs

    def t_START(self,camp):
        if self.elements[ME_PERSON] in camp.scene.contents and not self.see_exit:
            mycard = self.elements[mechtarot.ME_CARD]
            mysocket = self.elements[mechtarot.ME_SOCKET]
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig:
                self.card = mysig[0][0]
                pbge.alert("As you enter {}, you see {ME_PERSON} and {ME_PERSON.gender.possessive_determiner} aides making a hasty exit by the back door.".format(camp.scene,**self.elements))
                self.see_exit = True
                self._start_mission(camp)

    def _start_mission(self,camp):
        if not self.mission_seed:
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                camp, "Capture {}".format(self.elements[ME_PERSON]),
                (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
                enemy_faction=self.elements.get(ME_FACTION), rank=self.rank,
                objectives=(missionbuilder.BAMO_DEFEAT_NPC,),
                cash_reward=500, experience_reward=250,
                on_win=self._win_mission,on_loss=self._lose_mission,
                custom_elements={missionbuilder.BAME_NPC:self.elements[ME_PERSON]},
                win_message = "With {ME_PERSON} in custody, peace can return to {METROSCENE}.".format(**self.elements),
                loss_message = "Although you failed to catch {ME_PERSON}, {ME_PERSON.gender.subject_pronoun} probably won't be returning to {METROSCENE} any time soon.".format(**self.elements),
            )
            self.memo = "You have been authorized to capture {ME_PERSON} for {METROSCENE}.".format(**self.elements)
            missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])
            camp.freeze(self.elements[ME_PERSON])
            if ME_FACTION in self.elements:
                self.elements["METROSCENE"].purge_faction(camp,self.elements[ME_FACTION])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def _win_mission(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)

    def _lose_mission(self, camp):
        self.mission_seed = None
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_LOSE in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_LOSE](camp,mycard,self.card)
        self.elements[ME_PERSON].relationship.role = gears.relationships.R_ADVERSARY
        self.end_plot(camp)


class GuardianJudgment(Plot):
    # - Make sure there's a Guardian in town at all times.
    # - Speak to the Guardian, or an ally, to activate your incrimination.
    LABEL = "MT_SOCKET_Accuse"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return (
            "METROSCENE" in pstate.elements and pstate.elements["METROSCENE"] and
            pstate.elements["METROSCENE"].faction.get_faction_tag() in
            (gears.factions.TerranFederation,gears.factions.DeadzoneFederation) and
            ME_FACTION in pstate.elements and pstate.elements[ME_FACTION]
        )

    def custom_init(self, nart):
        # Ensure there will always be at least one Guardian here.
        self.add_sub_plot(nart,"ENSURE_LOCAL_REPRESENTATION",PlotState(elements={"FACTION":gears.factions.Guardians}).based_on(self))
        self.mission_seed = None
        self.card = None
        return True

    def is_appropriate_judge(self,npc,camp):
        if npc.faction is not self.elements.get(ME_FACTION):
            return camp.are_faction_allies(npc, gears.factions.Guardians) or camp.are_faction_allies(npc,self.elements["METROSCENE"])

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if self.is_appropriate_judge(npc,camp) and not self.mission_seed:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig:
                card = mysig[0][0]
                    # Alright, we have someone with the power to incriminate. Harvest some information.
                villain = card.elements.get(ME_FACTION) or card.elements.get(ME_PERSON) or "Somebody"
                crime = card.elements.get(ME_CRIME)
                if not crime:
                    crimed = "did something illegal"
                else:
                    crimed = crime.ed
                goffs.append(Offer(
                    "[THIS_IS_TERRIBLE_NEWS] [FACTION_MUST_BE_PUNISHED] You are authorized to launch a mecha strike against {}'s command center.".format(self._get_villain()),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crimed),"faction":str(villain)}
                ))
                self.card = card
            elif mycard.visible:
                villain = self._get_villain()
                goffs.append(Offer(
                    "I'd like to help you, but without incriminating proof there's nothing I can do.",
                    context=ContextTag([context.REVEAL]),
                    data={"reveal":"{} {}".format(villain,"did something wrong"),}
                ))

        return goffs

    def _get_villain(self):
        if self.card:
            return self.card.elements.get(ME_FACTION) or self.card.elements.get(ME_PERSON) or "Somebody"
        else:
            return self.elements.get(ME_FACTION) or self.elements.get(ME_PERSON) or "Somebody"

    def _start_mission(self,camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "Strike {}'s command center".format(self._get_villain()),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=self.elements.get(ME_FACTION), rank=self.rank,
            objectives=(missionbuilder.BAMO_STORM_THE_CASTLE,),
            cash_reward=500, experience_reward=250,
            on_win=self._win_mission,on_loss=self._lose_mission,
            win_message = "With their command center destroyed, the forces of {} are quickly brought to justice.".format(self._get_villain()),
            loss_message = "Following the attack on their command center, the forces of {} scatter to the wind. They will continue to be a thorn in the side of {} for years to come.".format(self._get_villain(),self.elements["LOCALE"]),
        )
        self.memo = "You have been authorized to take action against {}'s command center.".format(self._get_villain())
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])
        if ME_FACTION in self.elements:
            self.elements["METROSCENE"].purge_faction(camp,self.elements[ME_FACTION])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def _win_mission(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)

    def _lose_mission(self, camp):
        self.mission_seed = None
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_LOSE in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_LOSE](camp,mycard,self.card)
        self.end_plot(camp)


#   ***************************
#   ***  MT_SOCKET_Amplify  ***
#   ***************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person doing the amplification
#   ME_CARD
#   ME_SOCKET


class AmplifyThisSecret(Plot):
    LABEL = "MT_SOCKET_Amplify"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PERSON in pstate.elements

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            sigsec = sig[0].elements.get(ME_LIABILITY)
            goffs.append(Offer(
                "[THATS_INTERESTING] So {}... I will broadcast this to all of my listeners at once.".format(sigsec),
                context=ContextTag([context.CUSTOM]),
                effect=mechtarot.CardCaller(mycard,sig[0],mysocket.consequences[CONSEQUENCE_WIN]),
                data={"reply":"I have some news for you: {}!".format(sigsec)}, dead_end=True
            ))

        return goffs


#   ************************
#   ***  MT_SOCKET_Cure  ***
#   ************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PROBLEM  The disease
#   ME_CARD
#   ME_SOCKET


class WaitingOnACure(Plot):
    LABEL = "MT_SOCKET_Cure"
    active = True
    scope = "METRO"

    def custom_init( self, nart ):
        self.add_sub_plot(nart,"ENSURE_JOB_REPRESENTATION",elements={"JOB":gears.jobs.ALL_JOBS["Doctor"]})
        self.got_memo = False
        return True

    def _get_generic_offers( self, npc, camp ):
        goffs = list()
        if str(npc.job) in ("Doctor", "Cyberdoc", "Nurse", "Paramedic") and npc not in camp.party:
            mycard = self.elements[mechtarot.ME_CARD]
            mysocket = self.elements[mechtarot.ME_SOCKET]
            mysigs = mysocket.get_activating_signals(mycard, camp)
            for sig in mysigs:
                goffs.append(Offer(
                    "[THATS_GOOD] With this {ME_PROBLEM.solution}, we can put an end to the epidemic. [THANKS_FOR_HELP]".format(**self.elements),
                    context=ContextTag([context.CUSTOM]),
                    effect=mechtarot.CardCaller(mycard,sig[0],mysocket.consequences[CONSEQUENCE_WIN]),
                    data={"reply":"I've obtained some {ME_PROBLEM.solution} to cure the {ME_PROBLEM}.".format(**self.elements)}, dead_end=True
                ))
            if not self.got_memo:
                goffs.append(Offer(
                    "This is a serious problem. The only known cure for {ME_PROBLEM} is {ME_PROBLEM.solution}, but we don't have nearly enough available".format(**self.elements),
                    context=ContextTag([context.INFO]),
                    effect=self.get_memo, no_repeats=True,
                    data={"subject":"the epidemic"}
                ))

        return goffs

    def get_memo(self, camp):
        self.got_memo = True
        self.memo = "The only known cure for {ME_PROBLEM} is {ME_PROBLEM.solution}.".format(**self.elements)

#   **************************
#   ***  MT_SOCKET_Cancel  ***
#   **************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person being cancelled
#   ME_CARD
#   ME_SOCKET


class YouAreCancelled(Plot):
    LABEL = "MT_SOCKET_Cancel"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PERSON in pstate.elements

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            sigsub = sig[0].elements.get(ME_ACTOR) or "society"
            goffs.append(Offer(
                "No, not {}! Don't think this means you've seen the last of me... well, I guess you probably have seen the last of me.".format(sigsub),
                context=ContextTag([context.CUSTOM]),
                effect=mechtarot.CardCaller(mycard,sig[0],mysocket.consequences[CONSEQUENCE_WIN]),
                data={"reply":"You've been cancelled by {}!".format(sigsub)}, dead_end=True
            ))

        return goffs


#   *************************************
#   ***  MT_SOCKET_HenchmanLiability  ***
#   *************************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The henchman, who will be encountered in combat
#   ME_ACTOR    The person who hired the henchman
#   ME_CRIME    The crime that the henchman was hired to perform
#   ME_CARD
#   ME_SOCKET


class HenchmanInfo(Plot):
    LABEL = "MT_SOCKET_HenchmanLiability"
    active = True
    scope = "METRO"

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]

        # Set the liability here.
        mycard.elements[ME_LIABILITY] = "{ME_PERSON} {ME_CRIME.ed} for {ME_ACTOR}".format(**self.elements)
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            goffs.append(Offer(
                "Yeah, I {ME_CRIME.ed}. {ME_ACTOR} paid well for that.".format(**self.elements),
                context=ContextTag([context.COMBAT_INFO]),
                effect=mechtarot.CardCaller(mycard, sig[0], mysocket.consequences[CONSEQUENCE_WIN]),
                data={"subject": self.elements[ME_CRIME]}, dead_end=True
            ))
            goffs.append(Offer(
                "Yeah, I {ME_CRIME.ed}. {ME_ACTOR} paid well for that.".format(**self.elements),
                context=ContextTag([context.INFO]),
                effect=mechtarot.CardCaller(mycard, sig[0], mysocket.consequences[CONSEQUENCE_WIN]),
                data={"subject": self.elements[ME_CRIME]}, dead_end=True
            ))

        return goffs



#   ***************************
#   ***  MT_SOCKET_Decrypt  ***
#   ***************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PUZZLEITEM
#   ME_CARD
#   ME_SOCKET

class EnterPassword(Plot):
    # - We have a puzzle item? Just search it.
    LABEL = "MT_SOCKET_Decrypt"
    active = True
    scope = "METRO"

    def ME_PUZZLEITEM_menu(self, camp, thingmenu):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysig = mysocket.get_activating_signals(mycard, camp)
        thingmenu.desc = "{} It is locked.".format(thingmenu.desc)
        if mysig:
            sig = random.choice(mysig)
            mypass = sig[0].elements.get("PASSWORD","password")
            thingmenu.add_item("Enter {}".format(mypass), self._win_mission)

    def _win_mission(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        if mysigs:
            beta = random.choice(mysigs)[0]
        else:
            beta = None
        pbge.alert("You successfully unlock the {}.".format(self.elements[ME_PUZZLEITEM]))
        mysocket.consequences[CONSEQUENCE_WIN](camp, mycard, beta)
        self.end_plot(camp)



#   **************************
#   ***  MT_SOCKET_Extort  ***
#   **************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person to be extorted
#   ME_CARD
#   ME_SOCKET
#
#   CONSEQUENCE_WIN: The extortee will pay the PC to keep things quiet
#   CONSEQUENCE_GOAWAY: The extortee will leave this city


class BasicExtortionPlot(Plot):
    LABEL = "MT_SOCKET_Extort"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PERSON in pstate.elements

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        self.cash_offer = gears.selector.calc_threat_points(self.rank,500)//5
        for sig in mysigs:
            sigsec = sig[0].elements.get(ME_LIABILITY)
            goffs.append(Offer(
                "[THATS_INTERESTING] This news could cause a lot of damage if it were to spread... I can offer you ${} to forget about it right now.".format(self.cash_offer),
                context=ContextTag([context.CUSTOM]),
                data={"reply":"People are saying that {}.".format(sigsec)},
                subject=sigsec, subject_start=True
            ))
            goffs.append(Offer(
                "[PLEASURE_DOING_BUSINESS]".format(sigsec),
                context=ContextTag([context.CUSTOMREPLY]),
                effect=mechtarot.CardCaller(mycard, sig[0], self._accept_offer),
                data={"reply": "[PROPOSAL:ACCEPT]"},
                subject=sigsec, dead_end=True
            ))
            goffs.append(Offer(
                "[UNDERSTOOD] Just don't do anything foolish with this information before you've had a chance to accept my offer.",
                context=ContextTag([context.CUSTOMREPLY]),
                data={"reply": "[PROPOSAL:DENY]"},
                subject=sigsec, dead_end=True, no_repeats=True
            ))
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "You leave me little choice...",
                    context=ContextTag([context.CUSTOMREPLY]),
                    effect=mechtarot.CardCaller(mycard, sig[0], self._alt_offer),
                    data={"reply": "Here's my counteroffer. You leave town and never come back."},
                    subject=sigsec, dead_end=True
                ),camp,goffs,gears.stats.Ego,gears.stats.Negotiation,self.rank,gears.stats.DIFFICULTY_AVERAGE,
            )


        return goffs

    def _accept_offer(self, camp, alpha, beta, **kwargs):
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysocket.consequences[CONSEQUENCE_WIN](camp,alpha,beta,**kwargs)
        camp.credits += self.cash_offer

    def _alt_offer(self, camp, alpha, beta, **kwargs):
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysocket.consequences["CONSEQUENCE_GOAWAY"](camp,alpha,beta,**kwargs)


#   **************************
#   ***  MT_SOCKET_HireMe  ***
#   **************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person who wants to be hired
#   ME_CARD
#   ME_SOCKET


class HiringFetch(Plot):
    LABEL = "MT_SOCKET_HireMe"
    active = True
    scope = "METRO"

    JAC_ACCEPTED = 2
    JAC_QUERIED = 1

    def custom_init( self, nart ):
        self.job_state = collections.defaultdict(int)
        return True

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            signpc = sig[0].elements.get(ME_PERSON)
            if signpc:
                if self.job_state[signpc] == self.JAC_ACCEPTED:
                    goffs.append(Offer(
                        "[THANKS_FOR_HELP] I can't wait to start working as a {ME_POSITION}!".format(**self.elements),
                        context=ContextTag([context.CUSTOM]),
                        effect=mechtarot.CardCaller(mycard,sig[0],mysocket.consequences[CONSEQUENCE_WIN]),
                        data={"reply": "{} has agreed to hire you.".format(signpc)}, dead_end=True
                    ))
                elif self.job_state[signpc] == 0:
                    goffs.append(Offer(
                        "[THATS_GOOD] Could you give {} my resume? [I_WOULD_APPRECIATE_IT]".format(signpc.gender.object_pronoun),
                        context=ContextTag([context.CUSTOM]),
                        effect=mechtarot.CardCaller(mycard,sig[0],self._start_job_query),
                        data={"reply": "{} is hiring.".format(signpc)}, dead_end=True
                    ))

        return goffs

    def _start_job_query(self, camp, alpha, beta):
        signpc = beta.elements.get(ME_PERSON)
        mynpc = self.elements[ME_PERSON]
        self.job_state[signpc] = self.JAC_QUERIED
        self.memo = "{} asked you to bring {} {} resume.".format(mynpc, signpc, mynpc.gender.possessive_determiner)

    def _accept_job_query(self, camp, signpc, beta):
        mynpc = self.elements[ME_PERSON]
        self.job_state[signpc] = self.JAC_ACCEPTED
        self.memo = "{} agreed to hire {}.".format(signpc, mynpc)

    def _get_generic_offers( self, npc, camp ):
        goffs = list()
        if self.job_state[npc] == self.JAC_QUERIED:
            goffs.append(Offer(
                "This is impressive... you can tell {ME_PERSON} that {ME_PERSON.gender.subject_pronoun} has the job.".format(**self.elements),
                context=ContextTag([context.CUSTOM]),
                effect=mechtarot.CardCaller(npc, None, self._accept_job_query),
                data={"reply": "{} wanted me to give you this resume.".format(self.elements[ME_PERSON])}, dead_end=True
            ))

        return goffs



#   ******************************
#   ***  MT_SOCKET_InformantF  ***
#   ******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person doing the amplification
#   ME_CRIME    The crime object being informed about
#   ME_FACTION  The faction responsible for the crime
#   ME_CARD
#   ME_SOCKET


class Whistleblower(Plot):
    LABEL = "MT_SOCKET_InformantF"
    active = True
    scope = "METRO"

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            goffs.append(Offer(
                "[THIS_IS_A_SECRET] {ME_FACTION} {ME_CRIME.ed}.".format(**self.elements),
                context=ContextTag([context.INFO]),
                effect=mechtarot.CardCaller(mycard, sig[0], mysocket.consequences[CONSEQUENCE_WIN]),
                data={"subject":str(self.elements[ME_CRIME])}, dead_end=True
            ))

        return goffs


#   *******************************
#   ***  MT_SOCKET_Ingredients  ***
#   *******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The person waiting on ingredients
#   ME_PROBLEM  The problem and solution we need the ingredients for
#   ME_CARD
#   ME_SOCKET


class SupplierDelivery(Plot):
    LABEL = "MT_SOCKET_Ingredients"
    active = True
    scope = "METRO"

    def ME_PERSON_offers(self, camp):
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysigs = mysocket.get_activating_signals(mycard, camp)
        for sig in mysigs:
            goffs.append(Offer(
                "[THATS_GOOD] I will begin working on the {ME_PROBLEM.solution} right away!".format(**self.elements),
                context=ContextTag([context.CUSTOM]),
                effect=mechtarot.CardCaller(mycard, sig[0], mysocket.consequences[CONSEQUENCE_WIN]),
                data={"reply": "I have obtained the materials you need for the {ME_PROBLEM.solution}.".format(**self.elements)}, dead_end=True
            ))
        if not mysigs:
            goffs.append(Offer(
                "[HELLO] I need some materials before I can start work on the {ME_PROBLEM.solution}.".format(**self.elements),
                context=ContextTag([context.HELLO]),
            ))

        return goffs


#   *******************************
#   ***  MT_SOCKET_Investigate  ***
#   *******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The investigator
#   ME_CARD
#   ME_SOCKET

class InvestigateUsingWords(Plot):
    # - Send the player to Negotiate/Stealth their way into a faction meeting.
    LABEL = "MT_SOCKET_Investigate"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """This plot requires a faction to investigate."""
        return ME_FACTION in pstate.elements

    def custom_init(self, nart):
        # Ensure there will always be at least one faction member here.
        self.add_sub_plot(nart, "ENSURE_LOCAL_REPRESENTATION", elements={"FACTION": self.elements[ME_FACTION]})
        self.card = None
        self.mission_given = False
        self.mission_won = False
        return True

    def ME_PERSON_offers(self, camp):
        """Get offers from the mission-giver."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if not self.mission_given:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig and not self.mission_given:
                card = mysig[0][0]
                villain = self.elements[ME_FACTION]
                crime = card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME,CrimeObject("illegal acts","did something illegal"))
                goffs.append(Offer(
                    "[MAYBE_YOU_COULD_HELP] I've been trying to infiltrate one of their meetings to find out more, but they all know me. You, on the other hand, could easily sneak in and record what they're planning.".format(villain),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crime.ed)}
                ))
                self.card = card
        else:
            goffs.append(Offer(
                "Come back after you have infiltrated the meeting.".format(**self.elements),
                context=ContextTag([context.HELLO]),
            ))
            if self.mission_won:
                goffs.append(Offer(
                    "[THANK_YOU] This is perfect; these recordings will prove exactly what's been going on. Hopefully now {} can be brought to justice.".format(self.elements[ME_FACTION]),
                    context=ContextTag([context.CUSTOM]), effect=self._win_investigation, no_repeats=True,
                    data={"reply":"I infiltrated the meeting and brought back this recording."}
                ))

        return goffs

    def _start_mission(self,camp):
        self.mission_given = True
        self.memo = "{} at {} asked you to investigate {} by sneaking into one of their meetings.".format(self.elements[ME_PERSON],self.elements[ME_PERSON].get_scene(),self.elements[ME_FACTION])

    def t_START(self,camp):
        # If the investigator dies, end this plot.
        if self.elements[ME_PERSON].is_destroyed():
            if not self.mission_given:
                if self.card:
                    mycard = self.elements[mechtarot.ME_CARD]
                    mysocket = self.elements[mechtarot.ME_SOCKET]
                    if CONSEQUENCE_LOSE in mysocket.consequences:
                        mysocket.consequences[CONSEQUENCE_LOSE](camp, mycard, self.card)
                self.end_plot(camp,True)
            elif self.mission_won:
                verb = self.card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME,CrimeObject("terrible things","did terrible things"))
                pbge.alert("Your recordings from the meeting prove that {} {}.".format(self.elements[ME_FACTION],verb))
                self._win_investigation(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if self.mission_given and npc.faction is self.elements[ME_FACTION] and not self.mission_won:
            villain = self.elements.get(ME_FACTION)
            goffs.append(Offer(
                "Our next meeting? Why would you be interested in that?",
                ContextTag([context.INFO,]),subject=self,subject_start=True,
                no_repeats=True,data={"subject":"your next meeting"}
            ))
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "It's always a pleasure to meet someone who sees the world in the right way. Come along, then... I'm heading to the meeting now.",
                    ContextTag([context.CUSTOM,]),subject=self,no_repeats=True,dead_end=True,
                    data={"reply":"I have read your newsletter and found the ideas genuinely stimulating."},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Negotiation, self.rank, gears.stats.DIFFICULTY_AVERAGE
            )
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Oh, how wonderful! I've heard you've done great things over there. Well, the meeting is going to start soon, so let's get over there.",
                    ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                    data={"reply": "Actually I'm a member of the Ipshil branch but just moved here."},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Stealth, self.rank, gears.stats.DIFFICULTY_AVERAGE
            )
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Oh, right... Sorry, I guess I'm just bad with faces. Well, the meeting is going to start in a little while, so let's go there together.",
                    ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                    data={"reply": "Don't you remember me? We met at the {} picnic last month.".format(self.elements[ME_FACTION])},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Performance, self.rank, gears.stats.DIFFICULTY_HARD
            )
            goffs.append(Offer(
                "[GOODBYE]",
                ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                data={"reply": "Um, no reason..."}
            ))
        return goffs

    def _attend_meeting(self,camp):
        crime = self.card.elements.get(ME_CRIME) or self.elements.get(ME_CRIME) or "crime"
        pbge.alert("You attend the meeting of {ME_FACTION}. There is a lot of talk about reforging the world and purging the unworthy. It gets pretty repetitive after a while.".format(**self.elements))
        pbge.alert("Fortunately, there is also some talk of {}, and you get it all on tape.".format(crime))
        self.mission_won = True

    def _win_investigation(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp,total_removal=True)


class InvestigateUsingGiantRobots(Plot):
    # - Send the player to capture a building so it can be investigated.
    LABEL = "MT_SOCKET_Investigate"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.mission_seed = None
        self.card = None
        return True

    def ME_PERSON_offers(self, camp):
        """Get offers from the mission-giver."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if not self.mission_seed:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig and not self.mission_seed:
                card = mysig[0][0]
                    # Alright, we have someone with the power to incriminate. Harvest some information.
                villain = card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or card.elements.get(ME_PERSON) or "Somebody"
                crime = card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME,CrimeObject("crime","did crimes"))
                goffs.append(Offer(
                    "[MAYBE_YOU_COULD_HELP] I've been trying to get info about {}, but their facility is heavily guarded. If you could get me in, I could find all the information we need.".format(villain),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crime.ed)}
                ))
                self.card = card
        else:
            villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or self.card.elements.get(
               ME_PERSON) or "Somebody"
            if self.mission_seed.is_won():
                crime = self.card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME,CrimeObject("crime","did crimes"))
                goffs.append(Offer(
                    "We did it! I've found the proof that {} {}! Now we just need to alert someone with the power to do something about it...".format(villain,crime.ed),
                    context=ContextTag([context.HELLO]), effect=self._win_investigation
                ))
            else:
                goffs.append(Offer(
                    "[HELLO] Get back to me after you've secured the base belonging to {}.".format(villain),
                    context=ContextTag([context.HELLO]), effect=self._win_investigation
                ))

        return goffs

    def _start_mission(self,camp):
        villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION)
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "Infiltrate {}'s base".format(self.elements[ME_FACTION]),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=villain, rank=self.rank,
            objectives=(missionbuilder.BAMO_CAPTURE_BUILDINGS,missionbuilder.BAMO_LOCATE_ENEMY_FORCES),
            cash_reward=500, experience_reward=250, one_chance=False,
            win_message = "Having captured their base, you can begin searching for information.".format(self.elements[ME_FACTION]),
        )
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def t_START(self,camp):
        if self.elements[ME_PERSON].is_destroyed():
            if not self.mission_seed:
                if self.card:
                    mycard = self.elements[mechtarot.ME_CARD]
                    mysocket = self.elements[mechtarot.ME_SOCKET]
                    if CONSEQUENCE_LOSE in mysocket.consequences:
                        mysocket.consequences[CONSEQUENCE_LOSE](camp, mycard, self.card)
                self.end_plot(camp)
            elif self.mission_seed.is_won():
                villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or "Someone"
                crime = self.card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME,CrimeObject("crime","did crimes"))
                pbge.alert("While searching the base, you discover proof that {} {}.".format(villain,crime.ed))
                self._win_investigation(camp)

    def _win_investigation(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)



#   ******************************
#   ***  MT_SOCKET_SearchClue  ***
#   ******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_CARD
#   ME_SOCKET

class LibraryScience2099(Plot):
    # - We have a puzzle item? Just search it.
    LABEL = "MT_SOCKET_SearchClue"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PUZZLEITEM in pstate.elements

    def ME_PUZZLEITEM_menu(self, camp, thingmenu):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysig = mysocket.get_activating_signals(mycard, camp)

        if mysig:
            self.card = mysig[0][0]
            subject = self.card.elements.get(ME_CRIME) or self.elements.get(ME_CRIME) or "illegal activities"
            thingmenu.add_item("Search for {}".format(subject),self._win_mission)

    def _win_mission(self,camp):
        crime = self.card.elements.get(ME_CRIME) or self.elements.setdefault(ME_CRIME, CrimeObject("crime", "did crimes"))
        pbge.alert("You discover evidence that {} {}.".format(self.elements[ME_FACTION],crime.ed))
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)


