# A Quest is the opposite of a story- it is a randomly generated narrative with a defined ending.

from . import plots, dialogue
import random
import collections
from types import MethodType

VERB_DEFEAT = "DEFEAT"

DEFAULT_QUEST_CONCLUSION = "QUEST_CONCLUSION"
DEFAULT_QUEST_TASK = "QUEST_TASK"
DEFAULT_QUEST_LORE_HANDLER = "QUEST_LORE_HANDLER"

QUEST_ELEMENT_ID = "QUEST"
_QD_LEADS_TO_ELEMENT_ID = "_QUEST_LEADS_TO"  # Private use for this module; if writing your own quests, don't worry
# about it. Don't even question what this constant is. Or what it means. Or what it may be doing to your precious code.
# - The Illuminati
DEFAULT_OUTCOME_ELEMENT_ID = "QUEST_OUTCOME"
LORE_SET_ELEMENT_ID = "QUEST_LORE_SET"

TEXT_LORE_HINT = "[QUEST_LORE_HINT]"    # May be used as a rumor for learning this lore; independent clause
TEXT_LORE_INFO = "[QUEST_LORE_INFO]"    # The lore is revealed to the PC; independent clause
TEXT_LORE_TOPIC = "[QUEST_LORE_TOPIC]"  # The topic for the PC's inquiry into the lore; noun phrase
TEXT_LORE_SELFDISCOVERY = "[QUEST_LORE_SELFDISCOVERY]"  # A sentence for when the PC discovers the info themselves




class QuestPlot(plots.Plot):
    active = False
    QUEST_DATA = None
    quest_record = None

    def __init__(self, nart, pstate):
        leads_to = pstate.elements.pop(_QD_LEADS_TO_ELEMENT_ID, None)
        self.quest_record = QuestRecord(pstate.elements.get(QUEST_ELEMENT_ID), leads_to)
        if not self.QUEST_DATA:
            self.QUEST_DATA = QuestData()
        super().__init__(nart, pstate)

    def t_UPDATE(self, camp):
        if not self.quest_record.started:
            self.quest_record.started = True
            self.start_quest_task(camp)

    def start_quest_task(self, camp):
        pass

    def end_quest_task(self, camp):
        pass


class QuestLore:
    # Lore is information about a quest that is used to unlock quest tasks and different branches of a quest.
    def __init__(self, category, outcome=None, texts=None, involvement=None, effect=None):
        # category is used for sorting lore bits into different lore revelation routines, maybe.
        # outcome is the outcome of the questline that this lore refers to, if appropriate.
        # texts is a dict of strings that contains text about the lore
        # involvement is a challenge involvement checker
        # effect is a callable with signature (camp) that gets called when this lore is revealed
        self.category = category
        self.outcome = outcome
        self.texts = dict()
        if texts:
            self.texts.update(texts)
        self.involvement = involvement
        self.effect = effect

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)


class LoreRevealer:
    def __init__(self, lores, quest, loreset=None):
        self.lores = lores
        self.quest = quest
        self.loreset = loreset

    def __call__(self, camp):
        for l in self.lores:
            self.quest.reveal_lore(camp, l)
            if self.loreset and l in self.loreset:
                self.loreset.remove(l)


class QuestOutcome:
    def __init__(self, verb=VERB_DEFEAT, target=None, involvement=None, effect=None, loss_effect=None, lore=()):
        # verb is what's gonna happen in this outcome.
        # target is the Quest Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # involvement is a challenge involvement checker which checks to see what factions/NPCs might offer missions
        #   leading to this outcome.
        # effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        # loss_effect is a callable of form "loss_effect(camp)" which is called if/when this outcome fails
        # lore is a list of lore that will be inherited by the conclusion leading to this outcome. Note that if any
        #   lore has "None" as its outcome, it will automatically be set to this outcome. So if you want some lore
        #   with no outcome set the outcome to "False" instead. It ain't pretty but it should work.
        self.verb = verb
        self.target = target
        self.involvement = involvement
        self.effect = effect
        self.loss_effect = loss_effect
        self.lore = list(lore)
        for l in self.lore:
            if l.outcome is None:
                l.outcome = self

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)

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
        self, outcomes, outcome_element_id=DEFAULT_OUTCOME_ELEMENT_ID,
        task_type=DEFAULT_QUEST_TASK, conclusion_type=DEFAULT_QUEST_CONCLUSION,
        course_length=3, end_on_loss=True, lore_handler=DEFAULT_QUEST_LORE_HANDLER
    ):
        self.outcomes = list(outcomes)
        self.outcome_element_id = outcome_element_id
        self.task_type = task_type
        self.conclusion_type = conclusion_type
        self.course_length = course_length
        self.outcome_plots = dict()
        self.all_plots = list()
        self.end_on_loss = end_on_loss
        self._locked_lore = set()
        self._revealed_lore = set()
        self.lore_handler = lore_handler

    def build(self, nart, root_plot: plots.Plot):
        # Start constructing a quest starting with root_plot as the main controller.
        random.shuffle(self.outcomes)
        for numb, outc in enumerate(self.outcomes):
            frontier = dict()
            used_tasks = set()
            if self.conclusion_type.isidentifier():
                ident = "{}_{}".format(self.conclusion_type, str(numb))
            else:
                ident = "CONCLUSION_{}".format(numb)
            nuplot = root_plot.add_sub_plot(
                nart, self.conclusion_type,
                elements={QUEST_ELEMENT_ID: self, self.outcome_element_id: outc}, ident=ident
            )
            self.outcome_plots[outc] = nuplot
            setattr(root_plot, "{}_WIN".format(ident), QuestConclusionMethodWrapper(root_plot, outc.effect, True))
            setattr(root_plot, "{}_LOSE".format(ident), QuestConclusionMethodWrapper(root_plot, outc.loss_effect,
                                                                                     self.end_on_loss))
            self._prep_quest_plot(root_plot, nuplot)
            if nuplot.QUEST_DATA.potential_tasks:
                frontier[nuplot] = list(nuplot.QUEST_DATA.potential_tasks)
                random.shuffle(frontier[nuplot])
            nuplot.quest_record.needed_lore.update(outc.lore)

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

        self.add_quest_lore_handler(root_plot, nart)

    def add_quest_lore_handler(self, root_plot, nart):
        lore_set = set()

        for oc_plot in self.all_plots:
            for lore in oc_plot.quest_record.needed_lore:
                if lore not in self._locked_lore:
                    lore_set.add(lore)

        if lore_set:
            nuplot = root_plot.add_sub_plot(
                nart, self.lore_handler,
                elements={QUEST_ELEMENT_ID: self, LORE_SET_ELEMENT_ID: lore_set}, necessary=False
            )

            if not nuplot:
                print("Lore handler failed to load.")
                self._revealed_lore.update(lore_set)

        # Finally, check and activate the plots that should be active.
        self.check_quest_plot_activation()

    def check_quest_plot_activation(self, camp=None):
        for oc_plot in self.all_plots:
            if oc_plot.quest_record.should_be_active():
                oc_plot.active = True
        if camp:
            camp.check_trigger('UPDATE')

    def extend(self, nart, current_plot: QuestPlot, splabel):
        nuplot = current_plot.add_sub_plot(
            nart, splabel, necessary=False,
            elements={_QD_LEADS_TO_ELEMENT_ID: current_plot}
        )
        if nuplot:
            self._prep_quest_plot(current_plot, nuplot)
            current_plot.quest_record.tasks.append(nuplot)

        return nuplot

    def lock_lore(self, myplot: QuestPlot, mylore: QuestLore):
        # Attempt to lock the requested lore. You have to request locking the lore to prevent a loreblock, in which
        # case the quest is made inaccessible by conflicting lore requirements between different branches. When lore is
        # locked it will not be revealed normally; instead, the task that requested the lock needs to reveal the lore
        # manually. THIS POINT IS VERY IMPORTANT.
        # Anyhow, the rules to prevent loreblock are as follows:
        #  - Lore may not be locked if it was inherited from a parent plot and any other lore requirements of this plot
        #    are already locked.
        #  - Eat lots of fibre.
        # This algorithm will result in a lot of false positives- cases where there is no loreblock, but get disallowed
        # anyways. But it shouldn't produce any false negatives, which could be game-breaking bugs, and my covid brain
        # fog is back something fierce. Which you might be able to tell by this lengthy rambling comment.
        # If the lore lock fails, a PlotError is thrown so this plot will not be loaded.
        if myplot.quest_record.leads_to and mylore in myplot.quest_record.leads_to.quest_record.needed_lore:
            if any([lore in self._locked_lore for lore in myplot.quest_record.needed_lore]):
                raise plots.PlotError("Lore {} cannot be locked by {}.".format(mylore, myplot))
        self._locked_lore.add(mylore)
        if mylore in myplot.quest_record.needed_lore:
            myplot.quest_record.needed_lore.remove(mylore)

    def _prep_quest_plot(self, current_plot, nuplot: QuestPlot):
        #if not (hasattr(nuplot, "QUEST_DATA") and nuplot.QUEST_DATA):
        #    nuplot.QUEST_DATA = QuestData()
        #if not (hasattr(nuplot, "quest_record") and nuplot.quest_record):
        #    nuplot.quest_record = QuestRecord(self, current_plot)
        self.all_plots.append(nuplot)

    def reveal_lore(self, camp, lore: QuestLore):
        self._revealed_lore.add(lore)
        if lore.effect:
            lore.effect(camp)
        self.check_quest_plot_activation(camp)

    def lore_is_revealed(self, lore):
        return lore in self._revealed_lore


class QuestData:
    def __init__(self, potential_tasks=(), blocks_progress=True, theme=None):
        # Every quest plot should define this data structure as QUEST_DATA property. It gets used by the quest
        # builder.
        # potential_tasks are tasks that may be added to this task or conclusion.
        # blocks_progress means this subquest must be completed before its parent will be activated.
        # If theme is defined, no other siblings of this quest task can have the same theme.
        self.potential_tasks = tuple(potential_tasks)
        self.blocks_progress = blocks_progress
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
        self.needed_lore = set()
        self.started = False
        self.leads_to = leads_to
        if leads_to:
            self.needed_lore.update(leads_to.quest_record.needed_lore)

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
        for lore in self.needed_lore:
            if not self.quest.lore_is_revealed(lore):
                return False
        return True

