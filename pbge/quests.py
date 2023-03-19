# A Quest is the opposite of a story- it is a randomly generated narrative with a defined ending.

from . import plots
import random
import collections
from types import MethodType

VERB_DEFEAT = "DEFEAT"

DEFAULT_QUEST_CONCLUSION = "QUEST_CONCLUSION"
DEFAULT_QUEST_TASK = "QUEST_TASK"

DEFAULT_QUEST_ELEMENT_ID = "QUEST"
DEFAULT_OUTCOME_ELEMENT_ID = "QUEST_OUTCOME"


class QuestPlot(plots.Plot):
    active = False
    QUEST_DATA = None
    quest_record = None

    def t_UPDATE(self, camp):
        if not self.quest_record.started:
            if not self.active:
                if self.quest_record.should_be_active:
                    self.activate(camp)
                    self.start_quest_task(camp)
                    self.quest_record.started = True
            else:
                self.activate(camp)
                self.start_quest_task(camp)
                self.quest_record.started = True

    def start_quest_task(self, camp):
        pass

    def end_quest_task(self, camp):
        pass


class QuestOutcome:
    def __init__(self, verb=VERB_DEFEAT, target=None, participants=None, effect=None, loss_effect=None):
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
        task_type=DEFAULT_QUEST_TASK, conclusion_type=DEFAULT_QUEST_CONCLUSION, course_length=3, end_on_loss=True
    ):
        self.outcomes = list(outcomes)
        self.quest_element_id = quest_element_id
        self.outcome_element_id = outcome_element_id
        self.task_type = task_type
        self.conclusion_type = conclusion_type
        self.course_length = course_length
        self.outcome_plots = dict()
        self.end_on_loss = end_on_loss

    def build(self, nart, root_plot: plots.Plot):
        # Start constructing a quest starting with root_plot as the main controller.
        root_plot.elements[self.quest_element_id] = self
        random.shuffle(self.outcomes)
        for numb, outc in enumerate(self.outcomes):
            frontier = dict()
            all_plots = list()
            if self.conclusion_type.isidentifier():
                ident = "{}_{}".format(self.conclusion_type, str(numb))
            else:
                ident = "CONCLUSION_{}".format(numb)
            nuplot = root_plot.add_sub_plot(
                nart, self.conclusion_type, elements={self.outcome_element_id: outc}, ident=ident
            )
            self.outcome_plots[outc] = nuplot
            all_plots.append(nuplot)
            setattr(root_plot, "{}_WIN".format(ident), QuestConclusionMethodWrapper(root_plot, outc.effect, True))
            setattr(root_plot, "{}_LOSE".format(ident), QuestConclusionMethodWrapper(root_plot, outc.loss_effect,
                                                                                     self.end_on_loss))
            self._prep_quest_plot(nuplot)
            if nuplot.QUEST_DATA.potential_tasks:
                frontier[nuplot] = list(nuplot.QUEST_DATA.potential_tasks)
                random.shuffle(frontier[nuplot])

            # Add some tasks to this conclusion.
            t = self.course_length
            while t > 0 and frontier:
                mykey = random.choice(list(frontier.keys()))
                sub_plot_ident = frontier[mykey].pop()
                if not frontier[mykey]:
                    del frontier[mykey]
                new_task = self.extend(nart, mykey, sub_plot_ident)
                if new_task:
                    t -= 1
                    frontier[new_task] = list(nuplot.QUEST_DATA.potential_tasks)
                    random.shuffle(frontier[new_task])
                    all_plots.append(new_task)

            for oc_plot in all_plots:
                if oc_plot.quest_record.should_be_active():
                    oc_plot.active = True

    def extend(self, nart, current_plot: QuestPlot, splabel):
        nuplot = current_plot.add_sub_plot(nart, splabel, necessary=False)
        if nuplot:
            self._prep_quest_plot(nuplot)
            current_plot.quest_record.tasks.append(nuplot)

        return nuplot

    def _prep_quest_plot(self, nuplot: QuestPlot):
        if not (hasattr(nuplot, "QUEST_DATA") and nuplot.QUEST_DATA):
            nuplot.QUEST_DATA = QuestData()
        nuplot.quest_record = QuestRecord(self)


class QuestData:
    def __init__(self, potential_tasks=(), blocks_progress=True):
        # Every quest plot should define this data structure as QUEST_DATA property. It gets used by the quest
        # builder.
        # potential_tasks are tasks that may be added to this task or conclusion.
        # blocks_progress means this subquest must be completed before its parent will be activated.
        self.potential_tasks = tuple(potential_tasks)
        self.blocks_progress = blocks_progress


class QuestRecord:
    # A quest record created by a quest plot which contains its relationship to other quest plots.
    WIN = 1
    LOSS = -1
    IN_PROGRESS = 0

    def __init__(self, quest: Quest):
        self.quest = quest
        self.completion = self.IN_PROGRESS
        self.tasks = list()
        self.started = False

    def deactivate_children(self, camp):
        for task in self.tasks:
            task.end_quest_task(camp)
            task.deactivate(camp)
            task.quest_record.deactivate_children(camp)

    def win_obstacle(self, myplot: QuestPlot, camp):
        self.completion = self.WIN
        self.deactivate_children(camp)
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)

    def lose_obstacle(self, myplot: QuestPlot, camp):
        self.completion = self.LOSS
        self.deactivate_children(camp)
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)

    def should_be_active(self):
        for sq in self.tasks:
            if sq.QUEST_DATA.blocks_progress and sq.quest_record.completion == self.IN_PROGRESS:
                return False
        return True
