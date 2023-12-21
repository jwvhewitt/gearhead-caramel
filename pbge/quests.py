# A Quest is the opposite of a story- it is a randomly generated narrative with a defined ending.

from . import plots, dialogue
import random
import collections
from types import MethodType

VERB_DEFEAT = "DEFEAT"

DEFAULT_QUEST_BAD_CONCLUSION = "QUEST_BAD_CONCLUSION"
DEFAULT_QUEST_CONCLUSION = "QUEST_CONCLUSION"
DEFAULT_QUEST_GOOD_CONCLUSION = "QUEST_GOOD_CONCLUSION"

DEFAULT_QUEST_CONCLUSION_SERIES = (DEFAULT_QUEST_BAD_CONCLUSION, DEFAULT_QUEST_CONCLUSION, DEFAULT_QUEST_GOOD_CONCLUSION)

DEFAULT_QUEST_TASK = "QUEST_TASK"
DEFAULT_QUEST_LORE_HANDLER = "QUEST_LORE_HANDLER"

QUEST_ELEMENT_ID = "QUEST"

OUTCOME_ELEMENT_ID = "QUEST_OUTCOME"
LORE_SET_ELEMENT_ID = "QUEST_LORE_SET"

# Mandatory Lore
TEXT_LORE_HINT = "[QUEST_LORE_HINT]"    # May be used as a rumor for learning this lore; independent clause
TEXT_LORE_INFO = "[QUEST_LORE_INFO]"    # The lore is revealed to the PC; independent clause
TEXT_LORE_TOPIC = "[QUEST_LORE_TOPIC]"  # The topic for the PC's inquiry into the lore; noun phrase
TEXT_LORE_SELFDISCOVERY = "[QUEST_LORE_SELFDISCOVERY]"  # A sentence for when the PC discovers the info themselves

# Optional Lore
TEXT_LORE_TARGET_TOPIC = "[QUEST_LORE_TARGET_TOPIC]"    # Why are the lore keys formatted like grammar tokens?
    # Because originally I was going to use the grammar system, but there were problems and so I decided to just
    # use strings. Anyhow this text contains a single noun phrase having to do with the target of this quest's
    # activities.



class QuestPlot(plots.Plot):
    active = False
    quest_record = None

    def __init__(self, nart, pstate):
        self.quest_record = QuestRecord(pstate.elements.get(QUEST_ELEMENT_ID))
        super().__init__(nart, pstate)

    def t_UPDATE(self, camp):
        # Remember to super() this trigger if you need to in subclass plots!
        if not self.quest_record.started:
            self.quest_record.started = True
            self.start_quest_task(camp)

    def start_quest_task(self, camp):
        # Because starting/ending is controlled by the quest_record and revealed lore, this utility function stub
        # was added to activate subplots or challenges when needed.
        pass

    def end_quest_task(self, camp):
        # See above, but for ending this task.
        pass


class QuestLore:
    # Lore is information about a quest that is used to unlock quest tasks and different branches of a quest.
    def __init__(self, category, outcome=None, texts=None, involvement=None, effect=None, priority=False):
        # category is used for sorting lore bits into different lore revelation routines, maybe.
        # outcome is the outcome of the questline that this lore refers to, if appropriate.
        # texts is a dict of strings that contains text about the lore
        # involvement is a challenge involvement checker
        # effect is a callable with signature (camp) that gets called when this lore is revealed
        # priority is True if extra effort should be made to get this lore to the PC
        self.category = category
        self.outcome = outcome
        self.texts = dict()
        if texts:
            self.texts.update(texts)
        self.involvement = involvement
        self.effect = effect
        self.priority = priority

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)


class LoreRevealer:
    # An object that can be used as the "effect" for a waypoint or dialogue offer that will reveal the provided lore.
    # TODO: What is loreset all about? Find out and describe its use in a comment.
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
    def __init__(self, verb=VERB_DEFEAT, target=None, involvement=None, win_effect=None, loss_effect=None, lore=()):
        # verb is what's gonna happen in this outcome.
        # target is the Quest Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # involvement is a challenge involvement checker which checks to see what factions/NPCs might offer missions
        #   leading to this outcome.
        # win_effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        # loss_effect is a callable of form "loss_effect(camp)" which is called if/when this outcome fails or
        #   bcomes unwinnable.
        # lore is a list of lore that may be selected by a conclusion leading to this outcome.
        self.verb = verb
        self.target = target
        self.involvement = involvement
        self.win_effect = win_effect
        self.loss_effect = loss_effect
        self.lore = list(lore)

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)

    def __str__(self):
        return "{}: {}".format(self.verb, self.target)


class QuestConclusionMethodWrapper:
    # An object that automatically gets added to the root plot to listen for conclusions being concluded.
    # TODO: Figure out if this class is really necessary. It doesn't seem to do much.
    def __init__(self, root_plot: plots.Plot, outcome_fun, end_plot=True):
        self.root_plot = root_plot
        self.outcome_fun = outcome_fun
        self.end_plot = end_plot

    def __call__(self, camp):
        if self.outcome_fun:
            self.outcome_fun(camp)
        if self.end_plot:
            self.root_plot.end_plot(camp, True)


class Quest:
    # The constructor is passed a list of possible outcomes. It will then attempt to construct a web of plots with
    # the provided maximum chain length which connects all the outcomes to a single beginning state.
    # The plot creating the quest needs to call the build function.
    # The quest plots need to call the extend function.
    def __init__(
        self, outcomes, task_ident=DEFAULT_QUEST_TASK, conclusion_series=DEFAULT_QUEST_CONCLUSION_SERIES,
        course_length=3, end_on_loss=True, lore_handler=DEFAULT_QUEST_LORE_HANDLER
    ):
        self.outcomes = list(outcomes)
        self.task_ident = task_ident
        if not isinstance(conclusion_series, (list, tuple)):
            conclusion_series = (conclusion_series,)
        self.conclusion_series = conclusion_series
        self.course_length = max(course_length, 1)
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
            primary_conclusion = None
            main_quest_line = list()
            for c_label in self.conclusion_series:
                # Attempt to load a conclusion of this type.
                if primary_conclusion:
                    conc = self.extend(nart, primary_conclusion, c_label, {LORE_SET_ELEMENT_ID: primary_conclusion.quest_record.needed_lore, OUTCOME_ELEMENT_ID: outc})
                else:
                    conc = self.extend(nart, root_plot, c_label, {LORE_SET_ELEMENT_ID: set(), OUTCOME_ELEMENT_ID: outc})
                if conc:
                    if not primary_conclusion:
                        primary_conclusion = conc
                        main_quest_line.append(conc)
                        for t in range(self.course_length):
                            nu_parent = random.choice(main_quest_line)
                            nu_comp = self.extend(nart, nu_parent, self.task_ident, {LORE_SET_ELEMENT_ID: nu_parent.quest_record.needed_lore, OUTCOME_ELEMENT_ID: outc})
                            if nu_comp:
                                main_quest_line.append(nu_comp)
                    else:
                        side_quest_line = [conc,]

        self.add_quest_lore_handler(root_plot, nart)

    def _add_conclusion(self, root_plot, nart):
        # The conclusion gets the lore of the provided outcome as its lore_menu
        pass

    def _add_complication(self, current_plot, nart):
        # The complication gets the lore requirements of the current_plot as its lore_menu.
        # Generally a complication locks one of the lore requirements and adds a lore requirement of its own.
        pass

    def _add_side_quest(self, current_plot, nart):
        # A side quest gets the lore requirements of the current plot as its own lore requirements, then
        # adds some extra lore to unlock this branch.
        pass

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
            elif camp and oc_plot.active:
                oc_plot.end_quest_task(camp)
                oc_plot.deactivate(camp)
        if camp:
            camp.check_trigger('UPDATE')

    def extend(self, nart, current_plot: plots.Plot, splabel, elements=None):
        _elements = {QUEST_ELEMENT_ID: self}
        if elements:
            _elements.update(elements)
        nuplot = current_plot.add_sub_plot(
            nart, splabel, necessary=False, elements=_elements
        )
        if nuplot:
            self.all_plots.append(nuplot)

        return nuplot

    def lock_lore(self, myplot: QuestPlot, mylore: QuestLore):
        # Attempt to lock the requested lore. You have to request locking the lore to prevent a loreblock, in which
        # case the quest is made inaccessible by conflicting lore requirements between different branches.
        # If the lore lock fails, a PlotError is thrown so this plot will not be loaded.
        if mylore in self._locked_lore:
            raise plots.PlotError("Lore {} is already locked and so can't be locked by {}.".format(mylore, myplot))
        self._locked_lore.add(mylore)
        if mylore in myplot.quest_record.needed_lore:
            myplot.quest_record.needed_lore.remove(mylore)
        myplot.quest_record.lore_to_reveal.add(mylore)

    def reveal_lore(self, camp, lore: QuestLore):
        if lore not in self._revealed_lore:
            self._revealed_lore.add(lore)
            if lore.effect:
                lore.effect(camp)
            self.check_quest_plot_activation(camp)

    def lore_is_revealed(self, lore):
        return lore in self._revealed_lore

    @property
    # People might want to look at the revealed lore set, but no touching.
    def revealed_lore(self):
        return tuple(self._revealed_lore)


class QuestRecord:
    # A quest record created by a quest plot which contains its relationship to other quest plots.
    WIN = 1
    LOSS = -1
    IN_PROGRESS = 0

    def __init__(self, quest: Quest):
        self.quest = quest
        self.completion = self.IN_PROGRESS
        self.needed_lore = set()
        self.lore_to_reveal = set()
        self.started = False

    def win_task(self, myplot: QuestPlot, camp):
        if self.completion != self.WIN:
            camp.check_trigger("WIN", myplot)
        self.completion = self.WIN
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)
        for lore in self.lore_to_reveal:
            self.quest.reveal_lore(camp, lore)
        self.quest.check_quest_plot_activation(camp)

    def lose_task(self, myplot: QuestPlot, camp):
        if self.completion != self.LOSS:
            camp.check_trigger("LOSE", myplot)
        self.completion = self.LOSS
        myplot.end_quest_task(camp)
        myplot.deactivate(camp)
        self.quest.check_quest_plot_activation(camp)

    def should_be_active(self):
        if self.started and self.completion != self.IN_PROGRESS:
            return False
        for lore in self.needed_lore:
            if not self.quest.lore_is_revealed(lore):
                return False
        if self.lore_to_reveal and all(self.quest.lore_is_revealed(l) for l in self.lore_to_reveal):
            return False
        return True
