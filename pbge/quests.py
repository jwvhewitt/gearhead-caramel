# A Quest is the opposite of a story- it is a randomly generated narrative with a defined ending.

from . import plots, widgets, my_state, frects, image, wait_event, TIMEREVENT, util
import pygame
import random

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
TEXT_LORE_MEMO = "[TEXT_LORE_MEMO]"     # A sentence for use in the lore browser.

# Optional Lore
TEXT_LORE_TARGET_TOPIC = "[QUEST_LORE_TARGET_TOPIC]"    # Why are the lore keys formatted like grammar tokens?
    # Because originally I was going to use the grammar system, but there were problems and so I decided to just
    # use strings. Anyhow this text contains a single noun phrase having to do with the target of this quest's
    # activities.



class QuestPlot(plots.Plot):
    active = False
    quest_record = None

    def __init__(self, nart, pstate):
        self.quest_record = QuestRecord(pstate.elements.get(QUEST_ELEMENT_ID), pstate)
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
    def __init__(self, category, outcome=None, texts=None, involvement=None, effect=None, priority=False, tags=()):
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
        self.tags = set(tags)

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)

    def __str__(self):
        return "LORE:{}".format(self.texts.get(TEXT_LORE_SELFDISCOVERY))


class LoreRevealer:
    # An object that can be used as the "effect" for a waypoint or dialogue offer that will reveal the provided lore.
    # lores should be a list. Hence the "s". This way, a single conversation offer can reveal multiple pieces of lore.
    # loreset is a set of lore to reveal, usually the list of "orphaned" lore held by the lore handler plot. As lore
    # gets revealed it is removed from this set. When all the lore is revealed, the lore handler will typically
    # deactivate itself.
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
    def __init__(self, verb=VERB_DEFEAT, target=None, involvement=None, win_effect=None, loss_effect=None, lore=(), prioritize_lore=True):
        # verb is what's gonna happen in this outcome.
        # target is the Quest Element ID of the object of the verb. Except you can't say object in Python because that
        #   word has a different meaning here than it does in English grammar.
        # involvement is a challenge involvement checker which checks to see what factions/NPCs might offer missions
        #   leading to this outcome.
        # win_effect is a callable of form "effect(camp)" which is called if/when this outcome comes to pass
        # loss_effect is a callable of form "loss_effect(camp)" which is called if/when this outcome fails or
        #   bcomes unwinnable.
        # lore is a list of lore that may be selected by a conclusion leading to this outcome.
        # prioritize_lore is True if the lore should be pushed at the player as strongly as possible.
        #   Set this to True if you have a quest with narrow involvement and don't want the player to be chasing down
        #   rumors for a long time.
        self.verb = verb
        self.target = target
        self.involvement = involvement
        self.win_effect = win_effect
        self.loss_effect = loss_effect
        self.lore = list(lore)
        for l in self.lore:
            if not l.outcome:
                l.outcome = self
        self.prioritize_lore = prioritize_lore

    def is_involved(self, camp, npc):
        if not self.involvement:
            return True
        else:
            return self.involvement(camp, npc)

    def __str__(self):
        return "{}: {}".format(self.verb, self.target)


class QuestConclusionMethodWrapper:
    # An object that automatically gets added to the root plot to listen for conclusions being concluded.
    # Because we're attaching it after the root plot has been instantiated, it isn't a proper method.
    # I could use the types module to add a bound method, but because this also calls the outcome_fun
    # and ends the plot (usually) I figure this way of doing things is just as good.
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
    # *** A single plot can only build a single quest. This is because the quest modifies the plot. If you need more
    #  than one quest, use more than one plot.
    def __init__(
        self, desc, outcomes, task_ident=DEFAULT_QUEST_TASK, conclusion_series=DEFAULT_QUEST_CONCLUSION_SERIES,
        course_length=3, end_on_loss=True, lore_handler=DEFAULT_QUEST_LORE_HANDLER
    ):
        self.desc = desc.capitalize()
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
        self._not_lockable_lore = set()

    def build(self, nart, root_plot: plots.Plot):
        # Start constructing a quest starting with root_plot as the main controller.
        root_plot.extensions.append(self)
        random.shuffle(self.outcomes)
        for numa, outc in enumerate(self.outcomes):
            primary_conclusion = None
            for numb, c_label in enumerate(self.conclusion_series):
                # Attempt to load a conclusion of this type.
                if c_label.isidentifier():
                    ident = "{}_{}_{}".format(c_label, str(numa), str(numb))
                else:
                    ident = "CONCLUSION_{}_{}".format(numa, numb)

                if primary_conclusion:
                    self._not_lockable_lore.update(primary_conclusion.quest_record._needed_lore)
                    conc = self.extend(nart, primary_conclusion, c_label, {LORE_SET_ELEMENT_ID: primary_conclusion.quest_record._needed_lore, OUTCOME_ELEMENT_ID: outc}, spident=ident)
                else:
                    conc = self.extend(nart, root_plot, c_label, {LORE_SET_ELEMENT_ID: set(), OUTCOME_ELEMENT_ID: outc}, spident=ident)
                if conc:
                    setattr(root_plot, "{}_WIN".format(ident),
                            QuestConclusionMethodWrapper(root_plot, outc.win_effect, True))
                    setattr(root_plot, "{}_LOSE".format(ident),
                            QuestConclusionMethodWrapper(root_plot, outc.loss_effect,
                                                         self.end_on_loss))

                    if not primary_conclusion:
                        primary_conclusion = conc
                        course_length = self.course_length
                    else:
                        course_length = random.randint(1, max(self.course_length, 2))
                    current_plots = [conc,]
                    tries = 0
                    while tries < course_length * 3 and len(current_plots) <= course_length:
                        nu_parent = random.choice(current_plots)
                        nu_comp = self.extend(nart, nu_parent, self.task_ident, {LORE_SET_ELEMENT_ID: nu_parent.quest_record._needed_lore, OUTCOME_ELEMENT_ID: outc})
                        if nu_comp:
                            current_plots.append(nu_comp)
                        tries += 1

        self.add_quest_lore_handler(root_plot, nart)
        del self._not_lockable_lore

    def add_quest_lore_handler(self, root_plot, nart):
        lore_set = set()

        for oc_plot in self.all_plots:
            for lore in oc_plot.quest_record._needed_lore:
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
        for oc_plot in list(self.all_plots):
            if oc_plot.quest_record.should_be_active():
                oc_plot.active = True
            elif camp and oc_plot.active:
                oc_plot.end_quest_task(camp)
                oc_plot.deactivate(camp)
        if camp:
            camp.check_trigger('UPDATE')

    def extend(self, nart, current_plot: plots.Plot, splabel, elements=None, spident=None):
        _elements = {QUEST_ELEMENT_ID: self}
        if elements:
            _elements.update(elements)
        nuplot = current_plot.add_sub_plot(
            nart, splabel, necessary=False, elements=_elements, ident=spident
        )
        if nuplot:
            self.all_plots.append(nuplot)

        return nuplot

    def lock_lore(self, myplot: QuestPlot, mylore: QuestLore):
        # Attempt to lock the requested lore. You have to request locking the lore to prevent a loreblock, in which
        # case the quest is made inaccessible by conflicting lore requirements between different branches.
        # If the lore lock fails, a PlotError is thrown so this plot will not be loaded.
        if not self.will_not_cause_lore_blockage(LoreBlockRecord(myplot.quest_record, new_locked_lore=mylore)):
            raise plots.PlotError("Lore {} will cause blockage if locked by {}.".format(mylore, myplot))
        elif mylore in self._locked_lore or mylore in self._not_lockable_lore:
            raise plots.PlotError("Lore {} is already locked and so can't be locked by {}.".format(mylore, myplot))
        self._locked_lore.add(mylore)
        if mylore in myplot.quest_record._needed_lore:
            myplot.quest_record._needed_lore.remove(mylore)
        myplot.quest_record.lore_to_reveal.add(mylore)

    def reveal_lore(self, camp, lore: QuestLore):
        if lore not in self._revealed_lore:
            self._revealed_lore.add(lore)
            if lore.effect:
                lore.effect(camp)
            self.check_quest_plot_activation(camp)

    def lore_is_revealed(self, lore):
        return lore in self._revealed_lore

    def lore_is_unlocked(self, lore):
        return lore not in self._locked_lore

    def lore_is_lockable(self, lore):
        return lore not in self._locked_lore and lore not in self._not_lockable_lore

    def will_not_cause_lore_blockage(self, new_rec):
        # Make sure this new LoreRecord will not cause a lore blockage. Unfortunately, preventing lore blockage is
        # more complex than just making sure the quest generator is getting enough fibre.
        all_plots = [LoreBlockRecord(p.quest_record) for p in self.all_plots]
        all_plots.append(new_rec)
        all_plots.reverse()

        revealed_lore = set()
        locked_lore = set()
        for p in all_plots:
            revealed_lore.update(p.needed_lore)
            locked_lore.update(p.lore_to_reveal)

        revealed_lore.difference_update(locked_lore)

        while all_plots:
            removed_a_plot = False
            for p in list(all_plots):
                if p.needed_lore <= revealed_lore:
                    revealed_lore.update(p.lore_to_reveal)
                    all_plots.remove(p)
                    removed_a_plot = True
            if not removed_a_plot:
                break

        # I did not mean the final line of this function to sound like something you'd hear a mansplainer say, but...
        return not all_plots

    @property
    # People might want to look at the revealed lore set, but no touching.
    def revealed_lore(self):
        return tuple(self._revealed_lore)

    # ***   MEMO  FUNCTIONS   ***
    def get_memo(self):
        if self._revealed_lore:
            return self

    def open_lore(self, wid, ev):
        # Open the Hypothesis Widget.
        memob, camp = wid.data
        memob.active = False
        BrowseLoreWidget(self._revealed_lore, camp)()
        memob.regen_memo()
        memob.active = True

    def open_debug(self, wid, ev):
        # Open the Hypothesis Widget.
        memob, camp = wid.data
        memob.active = False
        QuestDebugInfoWidget(self, camp)()
        memob.regen_memo()
        memob.active = True

    def get_widget(self, memobrowser, camp):
        mylabel = widgets.LabelWidget(
            memobrowser.dx, memobrowser.dy, memobrowser.w, memobrowser.h, text=str(self),
            data=memobrowser, justify=0, font=my_state.medium_font
        )
        mybutton = widgets.LabelWidget(
            -75, 20, 150, 24, text="Review Lore", draw_border=True, justify=0, border=widgets.widget_border_on,
            on_click=self.open_lore, data=(memobrowser,camp), parent=mylabel, anchor=frects.ANCHOR_BOTTOM,
            font=my_state.big_font
        )
        mylabel.children.append(mybutton)

        if util.config.getboolean("GENERAL", "dev_mode_on"):
            mybutton = widgets.LabelWidget(
                -75, 60, 150, 24, text="View Debug Info", draw_border=True, justify=0, border=widgets.widget_border_on,
                on_click=self.open_debug, data=(memobrowser, camp), parent=mylabel, anchor=frects.ANCHOR_BOTTOM,
                font=my_state.big_font
            )
        mylabel.children.append(mybutton)
        return mylabel

    def __str__(self):
        return self.desc


class LoreBlockRecord:
    def __init__(self, qr, new_needed_lore: QuestLore=None, new_locked_lore: QuestLore=None):
        self.needed_lore = set(qr._needed_lore)
        self.lore_to_reveal = set(qr.lore_to_reveal)
        if new_needed_lore:
            self.needed_lore.add(new_needed_lore)
        if new_locked_lore:
            self.lore_to_reveal.add(new_locked_lore)
            if new_locked_lore in self.needed_lore:
                self.needed_lore.remove(new_locked_lore)


class QuestRecord:
    # A quest record created by a quest plot which contains its relationship to other quest plots.
    WIN = 1
    LOSS = -1
    IN_PROGRESS = 0

    def __init__(self, quest: Quest, pstate: plots.PlotState):
        self.quest = quest
        self.completion = self.IN_PROGRESS
        self._needed_lore = set()
        self.lore_to_reveal = set()
        my_lore = pstate.elements.get(LORE_SET_ELEMENT_ID, ())
        if my_lore:
            # Copy the priority lore from the set.
            priority_lore = [l for l in my_lore if l.priority]
            self._needed_lore.update(priority_lore)
        else:
            # Copy all the lore from the outcome.
            self._needed_lore.update(pstate.elements.get(OUTCOME_ELEMENT_ID).lore)
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
        for lore in self._needed_lore:
            if not self.quest.lore_is_revealed(lore):
                return False
        if self.lore_to_reveal and all(self.quest.lore_is_revealed(l) for l in self.lore_to_reveal):
            return False
        return True

    def add_needed_lore(self, quest, myplot, new_lore):
        if quest.will_not_cause_lore_blockage(LoreBlockRecord(myplot.quest_record, new_needed_lore=new_lore)):
        #if quest.lore_is_unlocked(new_lore):
            self._needed_lore.add(new_lore)
        else:
            raise plots.PlotError("Lore {} will cause lore blockage if claimed by {}.".format(new_lore, myplot))


class BrowseLoreWidget(widgets.ScrollColumnWidget):
    def __init__(self, revealed_lore, camp, **kwargs):
        up_arrow = widgets.ButtonWidget(-64, -232, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                        on_frame=0, off_frame=1)
        down_arrow = widgets.ButtonWidget(-64, 216, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                          on_frame=2, off_frame=3)
        super().__init__(-250, -200, 500, 400, center_interior=True, padding=16, up_button=up_arrow, down_button=down_arrow, draw_border=True, **kwargs)
        self.revealed_lore = revealed_lore
        self.camp = camp

        self.children.append(up_arrow)
        self.children.append(down_arrow)

        self.keep_going = True
        closebuttonsprite = image.Image('sys_closeicon.png')

        self.close_button = widgets.ButtonWidget(
            -closebuttonsprite.frame_width // 2, -closebuttonsprite.frame_height // 2, closebuttonsprite.frame_width,
            closebuttonsprite.frame_height, closebuttonsprite, 0, on_click=self.close_browser, parent=self,
            anchor=frects.ANCHOR_UPPERRIGHT)
        self.children.append(self.close_button)

        for rl in revealed_lore:
            if TEXT_LORE_MEMO in rl.texts:
                msg = rl.texts[TEXT_LORE_MEMO]
                msg.capitalize()
                self.add_interior(widgets.LabelWidget(0,0,self.w,0,msg, font=my_state.medium_font))

    def close_browser(self, button=None, ev=None):
        self.keep_going = False
        my_state.widgets.remove(self)

    def __call__(self):
        # Run the UI. Clean up after you leave.
        my_state.widgets.append(self)
        while self.keep_going and not my_state.got_quit:
            ev = wait_event()
            if ev.type == TIMEREVENT:
                my_state.render_and_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.keep_going = False

        if self in my_state.widgets:
            my_state.widgets.remove(self)


class QuestDebugInfoWidget(widgets.ScrollColumnWidget):
    def __init__(self, quest, camp, **kwargs):
        up_arrow = widgets.ButtonWidget(-64, -232, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                        on_frame=0, off_frame=1)
        down_arrow = widgets.ButtonWidget(-64, 216, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                          on_frame=2, off_frame=3)
        super().__init__(-250, -200, 500, 400, center_interior=True, padding=16, up_button=up_arrow, down_button=down_arrow, draw_border=True, **kwargs)
        self.quest = quest
        self.camp = camp

        self.children.append(up_arrow)
        self.children.append(down_arrow)

        self.keep_going = True
        closebuttonsprite = image.Image('sys_closeicon.png')

        self.close_button = widgets.ButtonWidget(
            -closebuttonsprite.frame_width // 2, -closebuttonsprite.frame_height // 2, closebuttonsprite.frame_width,
            closebuttonsprite.frame_height, closebuttonsprite, 0, on_click=self.close_browser, parent=self,
            anchor=frects.ANCHOR_UPPERRIGHT)
        self.children.append(self.close_button)

        for myplot in quest.all_plots:
            self.add_interior(widgets.LabelWidget(0, 0, self.w, 0, str(myplot), font=my_state.big_font, color=pygame.Color("white")))
            for nelore in myplot.quest_record._needed_lore:
                if TEXT_LORE_MEMO in nelore.texts:
                    msg = nelore.texts[TEXT_LORE_MEMO]
                else:
                    msg = nelore.texts[TEXT_LORE_SELFDISCOVERY]
                msg.capitalize()
                if quest.lore_is_revealed(nelore):
                    color=pygame.Color("green")
                elif quest.lore_is_unlocked(nelore):
                    color = pygame.Color("yellow")
                else:
                    color = pygame.Color("red")
                self.add_interior(widgets.LabelWidget(0,0,self.w,0,msg, font=my_state.medium_font, color=color))

    def close_browser(self, button=None, ev=None):
        self.keep_going = False
        my_state.widgets.remove(self)

    def __call__(self):
        # Run the UI. Clean up after you leave.
        my_state.widgets.append(self)
        while self.keep_going and not my_state.got_quit:
            ev = wait_event()
            if ev.type == TIMEREVENT:
                my_state.render_and_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.keep_going = False

        if self in my_state.widgets:
            my_state.widgets.remove(self)