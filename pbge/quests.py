# A Quest is the opposite of a story- it is a randomly generated narrative with a defined ending.

from . import plots, dialogue
import random
import collections
from types import MethodType

VERB_DEFEAT = "DEFEAT"

DEFAULT_QUEST_CONCLUSION = "QUEST_CONCLUSION"
DEFAULT_QUEST_TASK = "QUEST_TASK"
DEFAULT_QUEST_INTRO = "QUEST_INTRO"

DEFAULT_QUEST_ELEMENT_ID = "QUEST"
DEFAULT_OUTCOME_ELEMENT_ID = "QUEST_OUTCOME"


GRAM_QUEST_INFO = "[QUEST_INFO]"        # A brief overview of the quest.
GRAM_QUEST_DETAIL = "[QUEST_DETAIL]"    # Some slightly more specific info about the quest
GRAM_OUTCOME_INFO = "[OUTCOME_INFO]"    # A brief overview of the challenge
GRAM_OUTCOME_REASON = "[OUTCOME_REASON]"    # The reason for wanting to complete the current challenge
GRAM_TASK_INFO = "[TASK_INFO]"      # A brief overview of the current task
GRAM_TASK_REASON = "[TASK_REASON]"  # A reason for wanting to perform the current task
GRAM_TASK_TOPIC = "[TASK_TOPIC]"    # The string that will appear in the ask about... reply to the rumor.

GRAM_OUTCOME_TARGET = "[OUTCOME_TARGET]"    # The target of the challenge. Will be automatically filled in.
    # Can be used by any of the above grammar tags to reference the topic.

DEFAULT_QUEST_INTRO_GRAMMAR = {
    "[RUMOR]": (
        "[QUEST_INFO]; [OUTCOME_INFO]",
        "[OUTCOME_REASON]; [TASK_REASON]",
        "[OUTCOME_INFO]; [TASK_REASON]",
        "[TASK_REASON]", "[OUTCOME_REASON]",
        "[OUTCOME_INFO]", "[QUEST_INFO]; [OUTCOME_REASON]"
    ),
    "[SUBJECT]": (
        "[TASK_TOPIC]",
    ),
    "[OFFER]": (
        "[TASK_INFO].", "[TASK_REASON]- [TASK_INFO].",
        "[OUTCOME_REASON]; [TASK_INFO].", "[QUEST_DETAIL]; [TASK_INFO]."
    )
}



class QuestPlot(plots.Plot):
    active = False
    QUEST_DATA = None
    quest_record = None

    def t_UPDATE(self, camp):
        if not self.quest_record.started:
            self.quest_record.started = True
            self.start_quest_task(camp)

    def start_quest_task(self, camp):
        pass

    def end_quest_task(self, camp):
        pass

    def get_quest_intro_priority(self):
        it = self.QUEST_DATA.priority
        if self.quest_record.leads_to and self.QUEST_DATA.blocks_progress:
            it += self.quest_record.leads_to.get_quest_intro_priority()
        return it



class QuestIntroPlot(QuestPlot):
    LABEL = DEFAULT_QUEST_INTRO

    def get_rumor_offer_subject(self, starting_grammar=None):
        my_quest: Quest = self.quest_record.quest
        my_challenge = self.elements.get(my_quest.outcome_element_id, None)
        my_data = self.QUEST_DATA
        my_task = self.quest_record.leads_to.QUEST_DATA

        mygram = dialogue.grammar.Grammar()
        if starting_grammar:
            mygram.absorb(starting_grammar)
        else:
            mygram.absorb(DEFAULT_QUEST_INTRO_GRAMMAR)
        mygram[GRAM_OUTCOME_TARGET] = [str(my_challenge.target),]
        mygram.absorb(my_quest.grammar)
        mygram.absorb(my_challenge.grammar)
        mygram.absorb(my_data.grammar)
        mygram.absorb(my_task.grammar)

        rumor = dialogue.grammar.convert_tokens("[RUMOR]", mygram, start_on_capital=False).format(**self.elements)
        offer = dialogue.grammar.convert_tokens("[OFFER]", mygram).format(**self.elements)
        subject = dialogue.grammar.convert_tokens("[SUBJECT]", mygram, start_on_capital=False).format(**self.elements)

        return rumor, offer, subject


class QuestOutcome:
    def __init__(self, verb=VERB_DEFEAT, target=None, participants=None, effect=None, loss_effect=None, grammar=None):
        # verb is what's gonna happen in this outcome.
        # target is the Quest Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # participants is a challenge involvement checker which checks to see what factions/NPCs might offer missions
        #   leading to this outcome.
        # effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        # loss_effect is a callable of form "loss_effect(camp)" which is called if/when this outcome fails
        self.verb = verb
        self.target = target
        self.participants = participants
        self.effect = effect
        self.loss_effect = loss_effect
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)


    def __str__(self):
        return "{}: {}".format(self.verb, self.target)


class QuestConclusionMethodWrapper:
    def __init__(self, root_plot: plots.Plot, outcome_fun, end_plot=True):
        self.root_plot = root_plot
        self.outcome_fun = outcome_fun
        self.end_plot = end_plot

    def __call__(self, camp):
        if self.outcome_fun:
            self.outcome_fun(camp)
        if self.end_plot:
            self.root_plot.end_plot(camp)


class Quest:
    # The constructor is passed a list of possible outcomes. It will then attempt to construct a web of plots with
    # the provided maximum chain length which connects all the outcomes to a single beginning state.
    # The plot creating the quest needs to call the build function.
    # The quest plots need to call the extend function.
    def __init__(
        self, outcomes, quest_element_id=DEFAULT_QUEST_ELEMENT_ID, outcome_element_id=DEFAULT_OUTCOME_ELEMENT_ID,
        task_type=DEFAULT_QUEST_TASK, conclusion_type=DEFAULT_QUEST_CONCLUSION, intro_type=DEFAULT_QUEST_INTRO,
        course_length=3, end_on_loss=True, grammar=None
    ):
        self.outcomes = list(outcomes)
        self.quest_element_id = quest_element_id
        self.outcome_element_id = outcome_element_id
        self.task_type = task_type
        self.conclusion_type = conclusion_type
        self.intro_type = intro_type
        self.course_length = course_length
        self.outcome_plots = dict()
        self.all_plots = list()
        self.end_on_loss = end_on_loss
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)

    def build(self, nart, root_plot: plots.Plot):
        # Start constructing a quest starting with root_plot as the main controller.
        root_plot.elements[self.quest_element_id] = self
        random.shuffle(self.outcomes)
        for numb, outc in enumerate(self.outcomes):
            frontier = dict()
            used_tasks = set()
            if self.conclusion_type.isidentifier():
                ident = "{}_{}".format(self.conclusion_type, str(numb))
            else:
                ident = "CONCLUSION_{}".format(numb)
            nuplot = root_plot.add_sub_plot(
                nart, self.conclusion_type, elements={self.outcome_element_id: outc}, ident=ident
            )
            self.outcome_plots[outc] = nuplot
            setattr(root_plot, "{}_WIN".format(ident), QuestConclusionMethodWrapper(root_plot, outc.effect, True))
            setattr(root_plot, "{}_LOSE".format(ident), QuestConclusionMethodWrapper(root_plot, outc.loss_effect,
                                                                                     self.end_on_loss))
            self._prep_quest_plot(root_plot, nuplot)
            if nuplot.QUEST_DATA.potential_tasks:
                frontier[nuplot] = list(nuplot.QUEST_DATA.potential_tasks)
                random.shuffle(frontier[nuplot])

            # Add some tasks to this conclusion.
            # Don't repeat the same task for the same outcome.
            t = self.course_length
            while t > 0 and frontier:
                mykey = random.choice(list(frontier.keys()))
                sub_plot_ident = frontier[mykey].pop()
                if not frontier[mykey]:
                    del frontier[mykey]
                if sub_plot_ident not in used_tasks:
                    used_tasks.add(sub_plot_ident)
                    new_task = self.extend(nart, mykey, sub_plot_ident)
                    if new_task:
                        t -= 1
                        if new_task.QUEST_DATA.potential_tasks:
                            frontier[new_task] = list(new_task.QUEST_DATA.potential_tasks)
                            random.shuffle(frontier[new_task])

        self.check_quest_plot_intros(nart)

    def check_quest_plot_intros(self, nart):
        plots_needing_intros = list()
        plots_by_outcome = collections.defaultdict(list)
        intro_by_plot = dict()
        for oc_plot in self.all_plots:
            if oc_plot.quest_record.should_be_active():
                plots_needing_intros.append(oc_plot)
                plots_by_outcome[oc_plot.elements[self.outcome_element_id]].append(oc_plot)
        for pni in plots_needing_intros:
            nuplot = self.extend(nart, pni, self.intro_type)
            if not nuplot:
                # If no intro is available, automatically activate the task. I mean what else are you supposed to do
                # in this situation?
                pni.active = True
            else:
                intro_by_plot[pni] = nuplot
        # Finally- some intros might get a higher priority than others. For example, if your enemy has a secret that
        # turns out to be a hidden fortress, it would be kind of useful to know that before you learn that the
        # fortress is protected by a giant monster. So, lower priority intros get the highest priority intro as a
        # required task.
        for plot_list in plots_by_outcome.values():
            plot_list.sort(key=lambda a: a.get_quest_intro_priority())
            max_priority = plot_list[-1].get_quest_intro_priority()
            for pni in plot_list[:-1]:
                if pni.get_quest_intro_priority() < max_priority:
                    pni.quest_record.tasks.append(plot_list[:-1])

        # Finally, check and activate the plots that should be active.
        self.check_quest_plot_activation()

    def check_quest_plot_activation(self, camp=None):
        for oc_plot in self.all_plots:
            if oc_plot.quest_record.should_be_active():
                oc_plot.active = True
        if camp:
            camp.check_trigger('UPDATE')

    def extend(self, nart, current_plot: QuestPlot, splabel):
        nuplot = current_plot.add_sub_plot(nart, splabel, necessary=False)
        if nuplot:
            self._prep_quest_plot(current_plot, nuplot)
            current_plot.quest_record.tasks.append(nuplot)

        return nuplot

    def _prep_quest_plot(self, current_plot, nuplot: QuestPlot):
        if not (hasattr(nuplot, "QUEST_DATA") and nuplot.QUEST_DATA):
            nuplot.QUEST_DATA = QuestData()
        if not isinstance(current_plot, QuestPlot):
            current_plot = None
        nuplot.quest_record = QuestRecord(self, current_plot)
        self.all_plots.append(nuplot)


class QuestData:
    def __init__(self, potential_tasks=(), blocks_progress=True, grammar=None, priority=0, theme=None):
        # Every quest plot should define this data structure as QUEST_DATA property. It gets used by the quest
        # builder.
        # potential_tasks are tasks that may be added to this task or conclusion.
        # blocks_progress means this subquest must be completed before its parent will be activated.
        # If theme is defined, no other siblings of this quest task can have the same theme.
        self.potential_tasks = tuple(potential_tasks)
        self.blocks_progress = blocks_progress
        self.grammar = dict()
        if grammar:
            self.grammar.update(grammar)
        self.priority = priority
        self.theme = theme


class QuestRecord:
    # A quest record created by a quest plot which contains its relationship to other quest plots.
    WIN = 1
    LOSS = -1
    IN_PROGRESS = 0

    def __init__(self, quest: Quest, leads_to: QuestPlot):
        self.quest = quest
        self.completion = self.IN_PROGRESS
        self.tasks = list()
        self.started = False
        self.leads_to = leads_to

    def deactivate_children(self, camp):
        for task in self.tasks:
            task.end_quest_task(camp)
            task.deactivate(camp)
            task.quest_record.deactivate_children(camp)

    def win_task(self, myplot: QuestPlot, camp):
        self.completion = self.WIN
        self.deactivate_children(camp)
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)
        self.quest.check_quest_plot_activation(camp)

    def lose_task(self, myplot: QuestPlot, camp):
        self.completion = self.LOSS
        self.deactivate_children(camp)
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)
        self.quest.check_quest_plot_activation(camp)

    def should_be_active(self):
        if self.started and self.completion != self.IN_PROGRESS:
            return False
        for sq in self.tasks:
            if sq.QUEST_DATA.blocks_progress and sq.quest_record.completion != self.WIN:
                return False
        return True

