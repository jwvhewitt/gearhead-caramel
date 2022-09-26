from pbge.plots import Plot, PlotState, Rumor, TimeExpiration
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility, ghcutscene, ghchallenges
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed, GHNarrativeRequest
from . import missionbuilder, rwme_objectives, campfeatures
from pbge.challenges import Challenge, AutoOffer


# The plots in this unit create challenges. All of these plots start out deactivated until activated by their parent
# plot, at which point in time the challenge should also get activated. In general, all of these plots will require
# the following elements:
#    METROSCENE, METRO, MISSION_GATE
#
# Remember to use the activate method rather than just setting the active property. I should really make that property
# private or something

class ChallengeStarterPlot(Plot):
    scope = "METRO"
    active = False

    DEFAULT_CHALLENGE_STEP = 2

    def activate(self, camp):
        super().activate(camp)
        self.elements["CHALLENGE"].activate(camp)

    def CHALLENGE_WIN(self, camp):
        pbge.BasicNotification("Challenge complete!", count=160)
        camp.check_trigger("WIN", self)
        self.end_plot(camp)

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, self.DEFAULT_CHALLENGE_STEP)

    def end_plot(self, camp, total_removal=False):
        super().end_plot(camp, total_removal)
        self.elements["CHALLENGE"].deactivate(camp)


#   **************************************
#   ***  DETHRONE_BY_POPULAR_UPRISING  ***
#   **************************************
#
#   Get rid of NPC by starting a popular uprising.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, NPC
#
# Optional Elements:
#   VIOLATED_VIRTUES = A list of virtues that this mystery violates.
#   REASONS_TO_DETHRONE
#   REASONS_TO_SUPPORT
#   UPHELD_VIRTUE
#
# Triggers:
#   This plot will send a WIN signal if won, or a LOSE signal if it becomes unwinnable.

class DethroneByPopularUprising(ChallengeStarterPlot):
    LABEL = "DETHRONE_BY_POPULAR_UPRISING"
    scope = "METRO"
    active = False

    REASONS_TO_DETHRONE = {
        gears.personality.Justice: (
            "{NPC} ought to be locked behind bars",
            "{NPC} is corrupt and everybody knows"
        ),
        gears.personality.Peace: (
            "{NPC} has blood on {NPC.gender.possessive_determiner} hands",
        ),
        gears.personality.Fellowship: (
            "{NPC} is dividing {METROSCENE}'s community",
        ),
        gears.personality.Glory: (
            "{NPC} is a total loser",
        ),
        gears.personality.Duty: (
            "{NPC} has abandoned {NPC.gender.possessive_determiner} duty",
        ),
    }

    REASONS_TO_SUPPORT = {
        gears.personality.Justice: (
            "{NPC} hasn't broken any laws",
        ),
        gears.personality.Peace: (
            "{NPC} has kept {METROSCENE} safe",
        ),
        gears.personality.Fellowship: (
            "{NPC} is an upstanding member of the community",
        ),
        gears.personality.Glory: (
            "{NPC} has brought glory to {METROSCENE}",
        ),
        gears.personality.Duty: (
            "we must support {NPC} regardless",
        ),
    }

    def custom_init(self, nart):
        violated_virtues = self.elements.get("VIOLATED_VIRTUES", [random.choice(gears.personality.VIRTUES)])
        upheld_virtue = self.elements.get("UPHELD_VIRTUE", gears.personality.Duty)
        if upheld_virtue in violated_virtues:
            upheld_virtue = None
        reasons_to_dethrone = ["{METROSCENE} is being harmed by {NPC}".format(**self.elements)] + \
            self.elements.get("REASONS_TO_DETHRONE", [])
        for v in violated_virtues:
            for reason in self.REASONS_TO_DETHRONE[v]:
                reasons_to_dethrone.append(reason.format(**self.elements))
        reasons_to_support = ["{NPC} is doing great things for {METROSCENE}".format(**self.elements)] + \
            self.elements.get("REASONS_TO_SUPPORT", [])
        if upheld_virtue:
            for reason in self.REASONS_TO_SUPPORT[upheld_virtue]:
                reasons_to_support.append(reason.format(**self.elements))

        npc = self.elements["NPC"]
        self.register_element("CHALLENGE", Challenge(
            "Popular Uprising", ghchallenges.DETHRONE_CHALLENGE, (npc,),
            ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"], exclude=[npc]),
            active=False, data={
                "reasons_to_dethrone": reasons_to_dethrone,
                "reasons_to_support": reasons_to_support,
                "violated_virtue": random.choice(violated_virtues),
                "upheld_virtue": upheld_virtue
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[YOU_COULD_BE_RIGHT] Maybe {NPC} should be removed from power.".format(**self.elements),
                        context=ContextTag([context.CUSTOM, ]), effect=self._advance_challenge,
                        data={
                            "reply": "{}.".format(random.choice(reasons_to_dethrone))
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "You have agreed to help remove {NPC} from power in {METROSCENE}.".format(**self.elements)
            ), memo_active=True

        ))

        return True


#   ********************************
#   ***  DIPLOMACY_TO_DISCREDIT  ***
#   ********************************
#
#   Discredit a troublemaker (NPC) by peaceful methods.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, NPC
#
# Optional Elements:
#   FACTION_TO_BE_SWAYED, FACTION_DOING_SWAYING
#   VIOLATED_VIRTUE = A single virtue being violated, this time.
#   UPHELD_VIRTUE
#   CHALLENGE_SUBJECT
#   CHALLENGE_STATEMENTS
#   NPC_AGREEMENT
#   NPC_DISAGREEMENT
#
# Triggers:
#   This plot will send a WIN signal if won, or a LOSE signal if it becomes unwinnable.

class DiplomacyToDiscredit(ChallengeStarterPlot):
    LABEL = "DIPLOMACY_TO_DISCREDIT"
    scope = "METRO"
    active = False

    CHALLENGE_SUBJECTS = {
        None: (
            "{NPC}'s odious behaviour", "{NPC}'s troublemaking", "the problem with {NPC}"
        ),
        gears.personality.Justice: (
            "{NPC}'s crimes",
        ),
        gears.personality.Peace: (
            "the damage caused by {NPC}",
        ),
        gears.personality.Fellowship: (
            "the chaos caused by {NPC}",
        ),
        gears.personality.Glory: (
            "{NPC}'s countless failures",
        ),
        gears.personality.Duty: (
            "{NPC}'s betrayal of {METROSCENE}'",
        ),
    }

    CHALLENGE_STATEMENTS = {
        None: (
            "{NPC} is good actually", "I fully support {NPC}"
        ),
        gears.personality.Justice: (
            "{NPC} stands for justice",
        ),
        gears.personality.Peace: (
            "{NPC} has never hurt anyone",
        ),
        gears.personality.Fellowship: (
            "{NPC} has united {METROSCENE}",
        ),
        gears.personality.Glory: (
            "{NPC} is a born winner",
        ),
        gears.personality.Duty: (
            "{NPC} has always done {NPC.gender.possessive_determiner} duty",
        ),
    }

    REVERSE_CHALLENGE_STATEMENTS = {
        None: (
            "{NPC} is good actually", "I fully support {NPC}"
        ),
        gears.personality.Justice: (
            "{NPC}'s crimes have been exaggerated", "{NPC} is just doing what needs to be done"
        ),
        gears.personality.Peace: (
            "sometimes you need to break a few eggs to make an omelette", "{NPC} has only hurt people I don't like"
        ),
        gears.personality.Fellowship: (
            "{NPC} makes a lot of good points that are worth considering",
            "we'd have a better society if everyone listened to {NPC}"
        ),
        gears.personality.Glory: (
            "say what you will, at least {NPC} is trying",
        ),
        gears.personality.Duty: (
            "I don't care if {NPC} is a slacker", "{NPC} is the sort of maverick {METROSCENE needs right now}"
        ),
    }

    PC_REBUTTALS = {
        None: (
            "{NPC} is bad actually", "{METROSCENE} would be better off without {NPC}"
        ),
        gears.personality.Justice: (
            "{NPC} must be brought to justice", "{NPC} is utterly corrupt"
        ),
        gears.personality.Peace: (
            "{NPC} has put {METROSCENE} in danger",
            "{NPC} doesn't care about the harm {NPC.gender.subject_pronoun} causes"
        ),
        gears.personality.Fellowship: (
            "{NPC} is tearing {METROSCENE} apart",
            "{NPC} only preaches division and hatred"
        ),
        gears.personality.Glory: (
            "{NPC} is dragging {METROSCENE} down with {NPC.gender.object_pronoun}",
            "{NPC} is on a downward path",
        ),
        gears.personality.Duty: (
            "{NPC} has betrayed {METROSCENE}", "{NPC} has no loyalty to anyone but {NPC.gender.reflexive_pronoun}"
        ),
    }

    NPC_AGREEMENT = (
        "[YOU_COULD_BE_RIGHT] I will reconsider my position on {NPC}.",
        ""
    )

    NPC_DISAGREEMENT = (
        "[YOU_DONT_UNDERSTAND] {METROSCENE} needs {NPC}!",
        "[DISAGREE] I will not abandon {NPC}!"
    )

    def custom_init(self, nart):
        violated_virtue = self.elements.get("VIOLATED_VIRTUE", [random.choice(gears.personality.VIRTUES)])
        upheld_virtue = self.elements.get("UPHELD_VIRTUE", [random.choice(gears.personality.VIRTUES)])
        if upheld_virtue is violated_virtue:
            upheld_virtue = None

        metroscene = self.elements["METROSCENE"]
        faction_to_be_swayed = self.elements.get("FACTION_TO_BE_SWAYED", metroscene.faction)
        faction_doing_swaying = self.elements.get("FACTION_DOING_SWAYING", None)

        challenge_subject = self.elements.get("CHALLENGE_SUBJECT", None)
        if not challenge_subject:
            challenge_subject = random.choice(self.CHALLENGE_SUBJECTS[violated_virtue]).format(**self.elements)

        challenge_statements = [s.format(**self.elements) for s in self.elements.get("CHALLENGE_STATEMENTS", []) +
            list(self.CHALLENGE_STATEMENTS[upheld_virtue] + self.REVERSE_CHALLENGE_STATEMENTS[violated_virtue])]

        pc_rebuttals = [s.format(**self.elements) for s in self.elements.get("PC_REBUTTALS", []) +
            list(self.PC_REBUTTALS[violated_virtue])]

        npc_agreement = [s.format(**self.elements) for s in self.elements.get("NPC_AGREEMENT", []) +
            list(self.NPC_AGREEMENT)]

        npc_disagreement = [s.format(**self.elements) for s in self.elements.get("NPC_DISAGREEMENT", []) +
            list(self.NPC_DISAGREEMENT)]


        npc = self.elements["NPC"]
        self.register_element("CHALLENGE", Challenge(
            "Discredit {NPC}".format(**self.elements),
            ghchallenges.DIPLOMACY_CHALLENGE, [faction_to_be_swayed, faction_doing_swaying],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"]), active=False,
            data={
                "challenge_subject": challenge_subject,
                "challenge_statements": challenge_statements,
                "pc_rebuttals": pc_rebuttals,
                "npc_agreement": npc_agreement,
                "npc_disagreement": npc_disagreement,
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] I will no longer support {NPC.gender.object_pronoun}.".format(**self.elements),
                        context=ContextTag([context.CUSTOM,]), effect=self._advance_challenge,
                        data={
                            "reply": "I think {NPC} is causing trouble in {METROSCENE}.".format(**self.elements),
                            "opinion": "{NPC} is no good".format(**self.elements)
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "You have agreed to help discredit {NPC}.".format(**self.elements)
            ), memo_active=True

        ))

        return True


#   **************************
#   ***  EPIDEMIC_STARTER  ***
#   **************************
#
#   Just a starter for the Epidemic challenge.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, DISEASE, THECURE

class EpidemicStarter(ChallengeStarterPlot):
    LABEL = "EPIDEMIC_STARTER"
    scope = "METRO"
    active = False

    def custom_init(self, nart):
        self.register_element("CHALLENGE", Challenge(
            "Treat {DISEASE}".format(**self.elements),
            ghchallenges.EPIDEMIC_CHALLENGE, [self.elements["DISEASE"], self.elements["THECURE"]],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"]), active=False,
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[I_DONT_FEEL_WELL] Could you check me out?".format(**self.elements),
                        context=ContextTag([context.CUSTOM,]),
                        data={
                            "reply": "How are you feeling? You look like you might be coming down with {DISEASE}.".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    # No access fun here because InvolvedIfInfected already checks the party's Medicine skill.
                    involvement=ghchallenges.InvolvedIfInfected(self.elements["METROSCENE"]),
                    npc_effect=self.attempt_treatment
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "Many people in {METROSCENE} are infected with {DISEASE}.".format(**self.elements)
            ), memo_active=True
        ))

        return True

    def attempt_treatment(self, camp: gears.GearHeadCampaign, npc: gears.base.Character):
        pbge.alert("You attempt to treat {} for {}...".format(npc, self.elements["DISEASE"]))
        if camp.do_skill_test(
            gears.stats.Knowledge, gears.stats.Medicine, self.rank, difficulty=gears.stats.DIFFICULTY_HARD,
        ):
            pbge.alert("{} is cured!".format(npc))
            camp.dole_xp(50)
            npc.relationship.history.append(gears.relationships.Memory(
                "you cured me of {DISEASE}".format(**self.elements),
                "I cured you of {DISEASE}".format(**self.elements),
                reaction_mod=15, memtags=(gears.relationships.MEM_AidedByPC,)
            ))
            self._advance_challenge(camp)
        else:
            pbge.alert("You fail. {} goes home to rest.".format(npc))
            myvac = game.content.load_dynamic_plot(
                camp, "NPC_VACATION", PlotState().based_on(self, update_elements={"NPC": npc})
            )
            myvac.freeze_now(camp)


#   *******************************
#   ***  MAKE_BUILDING_STARTER  ***
#   *******************************
#
#   A starter for a MAKE challenge where the thing being made is a building or some type of infrastructure.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, BUILDING_NAME, BUILDING_NEED
# BUILDING_NAME is just what it sounds like.
# BUILDING_NEED is a string describing why_make_it

class MakeBuildingStarter(ChallengeStarterPlot):
    LABEL = "MAKE_BUILDING_STARTER"
    scope = "METRO"
    active = False

    def custom_init(self, nart):
        myscene = self.elements["METROSCENE"]
        if myscene.faction:
            invo = ghchallenges.InvolvedMetroFactionNPCs(myscene)
        else:
            invo = ghchallenges.InvolvedMetroResidentNPCs(myscene)
        self.register_element("CHALLENGE", Challenge(
            "Make {BUILDING_NAME}".format(**self.elements),
            ghchallenges.MAKE_CHALLENGE, [self.elements["BUILDING_NAME"],],
            involvement=invo, active=False,
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[THANKS_FOR_HELP] We'll be able to finish {BUILDING_NAME} soon.".format(**self.elements),
                        context=ContextTag([context.CUSTOM,]),
                        data={
                            "reply": "Do you need help building {BUILDING_NAME}?".format(**self.elements)
                        }, dead_end=True, effect=self._advance_challenge
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSkillRoll(gears.stats.Body, gears.stats.Repair, self.rank, untrained_ok=True),
                    involvement=ghchallenges.InvolvedMetroTaggedNPCs(self.elements["METROSCENE"], (gears.tags.Laborer, gears.tags.Craftsperson))
                ),
            ), data={"why_make_it": "{BUILDING_NEED}".format(**self.elements)},
            memo=pbge.challenges.ChallengeMemo(
                "{METROSCENE} has started constructing {BUILDING_NAME}; {BUILDING_NEED}.".format(**self.elements)
            ), memo_active=True
        ))

        return True



#   ****************************
#   ***  MAKE_DRUGS_STARTER  ***
#   ****************************
#
#   A starter for a MAKE challenge where the thing being made is drugs. Or medicine, I guess.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, DISEASE, THECURE

class MakeDrugsStarter(ChallengeStarterPlot):
    LABEL = "MAKE_DRUGS_STARTER"
    scope = "METRO"
    active = False

    def custom_init(self, nart):
        self.register_element("CHALLENGE", Challenge(
            "Make {THECURE}".format(**self.elements),
            ghchallenges.MAKE_CHALLENGE, [self.elements["THECURE"],],
            involvement=ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"]), active=False,
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[THANKS_FOR_HELP] We'll be able to defeat {DISEASE} soon.".format(**self.elements),
                        context=ContextTag([context.CUSTOM,]),
                        data={
                            "reply": "I can help you to synthesize {THECURE}.".format(**self.elements)
                        }, dead_end=True, effect=self._advance_challenge
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSkillRoll(gears.stats.Craft, gears.stats.Science, self.rank),
                    involvement=ghchallenges.InvolvedMetroTaggedNPCs(self.elements["METROSCENE"], (gears.tags.Medic,))
                ),
            ), data={"why_make_it": "we need {THECURE} to treat {DISEASE}".format(**self.elements)},
            memo=pbge.challenges.ChallengeMemo(
                "Doctors in {METROSCENE} are working hard to synthesize {THECURE} to treat {DISEASE}.".format(**self.elements)
            ), memo_active=True
        ))

        return True

