# After years of building 'em manually, I have decided to create a standard interface for stories built using Propp's
# Ratchet. This is a random story technique that has been used since GearHead 1.
import collections

from . import plots

VERB_DEFEAT = "DEFEAT"

DEFAULT_STORY_PLOT = "STORY_PLOT"
DEFAULT_STORY_CONCLUSION = "STORY_CONCLUSION"


class ProppKey:
    def __init__(self, name, narratemes=(), takes_params=False):
        self.name = name
        self.narratemes = tuple(narratemes)
        self.takes_element = takes_params

    def __eq__(self, other):
        if isinstance(other, ProppKey):
            return self.name == other.name and self.narratemes == other.narratemes and self.takes_element == other.takes_element

    def __hash__(self):
        return hash((self.name, self.narratemes, self.takes_element))


class ProppValue:
    def __init__(self, narrateme, params=()):
        self.narrateme = narrateme
        self.elements = tuple(params)


class ProppState:
    def __init__(self, values=None):
        # Values is a dict in which the keys are ProppKey objects and the values are ProppValue objects
        self.values = collections.defaultdict(ProppValue)
        if values:
            self.values.update(values)


class Story:
    # The base class for stories; probably should not be used by itself. See "InstantStory" and "OngoingStory" below.
    def __init__(self, state=None, plot_type=DEFAULT_STORY_PLOT, elements=None):
        self.state = state
        self.plot_type = plot_type
        self.elements = dict()
        if elements:
            self.elements.update(elements)


class OutcomeAttitude:
    WANT = "WANT"               # Faction/character in favor of this outcome
    DO_NOT_WANT = "DO_NOT_WANT" # Faction/character opposed to this outcome
    MAYBE = "MAYBE"             # Faction/character can be convinced to back this outcome
    MAYBE_NOT = "MAYBE_NOT"     # Faction/character can be convinced to oppose this outcome

    def __init__(self, attitude=WANT, cooperative=True):
        self.attitude = attitude
        self.cooperative = cooperative


class ISOutcome:
    def __init__(self, verb=VERB_DEFEAT, target=None, participants=None, effect=None):
        # verb is what's gonna happen in this outcome.
        # target is the Story Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # participants is a dict where key = faction/character Story Element ID and value = OutcomeAttitude
        # effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        self.verb = verb
        self.target = target
        self.participants = dict()
        if participants:
            self.participants.update(participants)
        self.effect = effect

    def __str__(self):
        return "{}: {}".format(self.verb, self.target)


class InstantStory(Story):
    # An instant story gets built all at once. All the story components are subplots of the plot that called for the
    # story to be built. Components self-activate when the story state matches their requirements, and deactivate when
    # the story state no longer matches their requirements.
    # In GH1 and GH2, this is what would have been referred to as a "quest".
    # The constructor is passed a list of possible outcomes. It will then attempt to construct a web of plots with
    # the provided maximum chain length which connects all the outcomes to a single beginning state.
    def __init__(self, outcomes, conclusion_type=DEFAULT_STORY_CONCLUSION, num_keys=3, chain_length=3, **kwargs):
        super().__init__(**kwargs)
        self.outcomes = list(outcomes)
        self.conclusion_type = conclusion_type
        self.num_keys = num_keys
        self.chain_length = chain_length

    def _get_conclusion_combo(self, plot_candidates, current_outcome, remaining_outcomes, cumulative_keys=None):
        # For a
        combos = list()
        if not cumulative_keys:
            cumulative_keys = set()
        for nuplot, nustate in plot_candidates[current_outcome].items():
            nu_keys = cumulative_keys | set(nustate.values.keys())
            if len(nu_keys) <= self.num_keys:
                # nuplot doesn't add enough keys to go over the key limit. Continue checking for combos.
                if not remaining_outcomes:
                    # This is the last plot needed. Add it to the list, embedded in a list.
                    combos.append([nuplot])
                else:
                    # Check the remaining outcomes.
                    for rops in self._get_conclusion_combo(plot_candidates, remaining_outcomes[0], remaining_outcomes[1:], nu_keys):
                        # rops stands for "remaining outcomes plot sequences".
                        combos.append([nuplot] + rops)
        return combos

    def build(self, nart: plots.NarrativeRequest, parent_plot=None):
        # Find a pool of candidates for each of the outcomes.
        candidates = collections.defaultdict(dict)
        for outc in self.outcomes:
            for sp in nart.plot_list[self.conclusion_type]:
                req_state = sp.get_conclusion_context(nart, outc)
                if req_state:
                    candidates[outc][sp] = req_state
            if not candidates[outc]:
                print("Plot Error: No conclusion found for outcome {} in {}".format(outc, self))
                raise plots.PlotError("Plot Error: No conclusion found for outcome {} in {}".format(outc, self))

        # Find sets of candidate conclusions that share three ProppValues.
        combos = self._get_conclusion_combo(candidates, self.outcomes[0], self.outcomes[1:])
        print(combos)

#        keep_going = True
#        while keep_going:
#            pass

        # Choose a set at random, and attempt to navigate to a starting point.
        # - For each conclusion, figure out every plot state it can reach within the required number of links.
        # - See if there are initial plot states that satisfy all conclusions.
        #   - If so, build the plot web based on the initial plot state/pathfinding. Make sure to spackle loose ends.


class OngoingStory(Story):
    # An ongoing story is a story that happens one episode at a time. The story may be called to generate a new
    # chapter whenever appropriate.
    def start_next_chapter(self):
        pass


class StoryConclusionPlot(plots.Plot):
    LABEL = DEFAULT_STORY_CONCLUSION
    scope = "METRO"

    @classmethod
    def get_conclusion_context(cls, nart, outcome: ISOutcome):
        # If this conclusion can be used for the provided outcome, return the ProppState describing the conditions
        # of this conclusion. If it can't be used, return None.
        return None

