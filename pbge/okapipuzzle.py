import random
from . import widgets, INFO_HILIGHT, ENEMY_RED, INFO_GREEN, image, my_state, wait_event, TIMEREVENT, frects
import pygame

# This unit is called "Okapi Puzzle" because the puzzles it generates are not Zebra Puzzles exactly but they are sort
# of related. Puzzle generation and solving are accomplished through brute force algorithms. I've seen examples
# (=cough= RosettaCode =cough=) which use linear algebra or external dependencies to solve puzzles. Well I say, screw
# that. Brute force checking of every solution against every clue is fast enough, doesn't take up a lot of memory on
# modern computers, is more understandable + extensible, and gives me the sensation of hitting math with a hammer.
# Remember that it is harder to debug a program than to write it, so if you write the cleverest code you are capable of
# then you are clearly incapable of troubleshooting that code.

# Noun Roles
SUS_SUBJECT = "SUBJECT"
SUS_LOCATION = "LOCATION"

# Verb Roles
SUS_VERB = "VERB"
SUS_MOTIVE = "MOTIVE"

# Triggers
MYSTERY_SOLVED = "SOLVED"


class NounSusCard:
    # The description of a suspect- one of a number of items the player must choose between to form a hypothesis.
    # Despite the name, the SusCard doesn't need to refer to a person- it could be a place, an action, a motive, or
    # anything else that forms part of the mystery. Kind of like the clue cards in the board game Cluedo. But that
    # name has been taken, so SusCard it is.
    # gameob is the game object this card refers to, if applicable.
    # Data is a dict containing possible game-specific information.
    def __init__(self, name, gameob=None, role=SUS_SUBJECT, data=None):
        self.name = name
        self.gameob = gameob
        self.role = role
        self.data = dict()
        if data:
            self.data.update(data)

    def __str__(self):
        return self.name


class VerbSusCard:
    # The description of a suspect- one of a number of items the player must choose between to form a hypothesis.
    # Despite the name, the SusCard doesn't need to refer to a person- it could be a place, an action, a motive, or
    # anything else that forms part of the mystery. Kind of like the clue cards in the board game Cluedo. But that
    # name has been taken, so SusCard it is.
    # gameob is a game object this card refers to, if applicable.
    # Data is a dict containing possible game-specific information.
    def __init__(self, name, to_verb, verbed, did_not_verb, gameob=None, role=SUS_VERB, data=None):
        self.name = name
        self.to_verb = to_verb
        self.verbed = verbed
        self.did_not_verb = did_not_verb
        self.gameob = gameob
        self.role = role
        self.data = dict()
        if data:
            self.data.update(data)

    def __str__(self):
        return self.name


class SusDeck:
    # A collection of SusCards with some organizational information.
    def __init__(self, name, cards):
        self.name = name
        self.cards = tuple(cards)

    def __str__(self):
        return self.name


class ABTogetherClue:
    CLUE_FORMATS = {
        SUS_SUBJECT: {
            SUS_SUBJECT: "{a.name} and {b.name} worked together",
            SUS_LOCATION: "{a.name} was seen at {b.name}",
            SUS_VERB: "{a.name} {b.verbed}",
            SUS_MOTIVE: "{a.name} wanted {b.to_verb}"
        },
        SUS_LOCATION: {
            SUS_SUBJECT: "Someone at {a.name} saw {b.name}",
            SUS_LOCATION: "{a.name} is connected to {b.name} somehow",
            SUS_VERB: "A person at {a.name} {b.verbed}",
            SUS_MOTIVE: "Someone went to {a.name} {b.to_verb}"
        },
        SUS_VERB: {
            SUS_SUBJECT: "{b.name} {a.verbed}",
            SUS_LOCATION: "Someone {a.verbed} at {b.name}",
            SUS_VERB: "The person who {a.verbed} also {b.verbed}",
            SUS_MOTIVE: "A person {a.verbed} {b.to_verb}"
        },
        SUS_MOTIVE: {
            SUS_SUBJECT: "{b.name} desired {a.to_verb}",
            SUS_LOCATION: "{b.name} is a good place {a.to_verb}",
            SUS_VERB: "Somebody {b.verbed} in order {a.to_verb}",
            SUS_MOTIVE: "The same person wanted {a.to_verb} and {b.to_verb}"
        }
    }

    def __init__(self, acard, bcard, mystery):
        cards = [acard, bcard]
        random.shuffle(cards)
        self.acard = cards[0]
        self.bcard = cards[1]
        try:
            self.text = self.CLUE_FORMATS[self.acard.role][self.bcard.role].format(a=self.acard, b=self.bcard,
                                                                                   mystery=mystery)
        except KeyError:
            self.text = "{a} is involved with {b}".format(a=self.acard, b=self.bcard, mystery=mystery)

    def matches(self, solution):
        if self.acard in solution or self.bcard in solution:
            return self.acard in solution and self.bcard in solution
        else:
            return True

    def is_involved(self, gameob):
        # Return True if this gameob is involved with this card.
        if gameob:
            return gameob is self.acard.gameob or gameob is self.bcard.gameob

    def __str__(self):
        return self.text


class ABNotTogetherClue:
    CLUE_FORMATS = {
        SUS_SUBJECT: {
            SUS_SUBJECT: "{a.name} and {b.name} didn't work together",
            SUS_LOCATION: "{a.name} was not at {b.name}",
            SUS_VERB: "{a.name} {b.did_not_verb}",
            SUS_MOTIVE: "{a.name} doesn't want {b.to_verb}"
        },
        SUS_LOCATION: {
            SUS_SUBJECT: "{a.name} is not where {b.name} was",
            SUS_LOCATION: "{a.name} is not connected to {b.name}",
            SUS_VERB: "Nobody at {a.name} {b.verbed}",
            SUS_MOTIVE: "Nobody at {a.name} wanted {b.to_verb}"
        },
        SUS_VERB: {
            SUS_SUBJECT: "{b.name} {a.did_not_verb}",
            SUS_LOCATION: "Nobody {a.verbed} at {b.name}",
            SUS_VERB: "The person who {a.verbed} {b.did_not_verb}",
            SUS_MOTIVE: "Whoever {a.verbed} didn't want {b.to_verb}"
        },
        SUS_MOTIVE: {
            SUS_SUBJECT: "{b.name} doesn't want {a.to_verb}",
            SUS_LOCATION: "{b.name} is not a good place {a.to_verb}",
            SUS_VERB: "Nobody {b.verbed} in order {a.to_verb}",
            SUS_MOTIVE: "Nobody wants {a.to_verb} and {b.to_verb}"
        }
    }

    def __init__(self, acard, bcard, mystery):
        cards = [acard, bcard]
        random.shuffle(cards)
        self.acard = cards[0]
        self.bcard = cards[1]
        try:
            self.text = self.CLUE_FORMATS[self.acard.role][self.bcard.role].format(a=self.acard, b=self.bcard,
                                                                                   mystery=mystery)
        except KeyError:
            self.text = "{a} is not involved with {b}".format(a=self.acard, b=self.bcard, mystery=mystery)

    def matches(self, solution):
        return not (self.acard in solution and self.bcard in solution)

    def is_involved(self, gameob):
        # Return True if this gameob is involved with this card.
        if gameob:
            return gameob is self.acard.gameob or gameob is self.bcard.gameob

    def __str__(self):
        return self.text


class ANotSolutionClue:
    CLUE_FORMATS = {
        SUS_SUBJECT: "{a.name} is not involved in {mystery}",
        SUS_LOCATION: "{mystery} did not happen at {a}",
        SUS_VERB: "Nobody {a.verbed}",
        SUS_MOTIVE: "Nobody wanted {a.to_verb}"
    }

    def __init__(self, acard, mystery):
        self.acard = acard
        try:
            self.text = self.CLUE_FORMATS[self.acard.role].format(a=self.acard, mystery=mystery)
        except KeyError:
            self.text = "{a} has nothing to do with {mystery}".format(a=self.acard, mystery=mystery)

    def matches(self, solution):
        return self.acard not in solution

    def is_involved(self, gameob):
        # Return True if this gameob is involved with this card.
        return gameob and gameob is self.acard.gameob

    def __str__(self):
        return self.text


class AIsSolutionClue:
    CLUE_FORMATS = {
        SUS_SUBJECT: "{a.name} is involved in {mystery}",
        SUS_LOCATION: "{mystery} happened at {a}",
        SUS_VERB: "Somebody {a.verbed}",
        SUS_MOTIVE: "Somebody wants {a.to_verb}"
    }

    def __init__(self, acard, mystery):
        self.acard = acard
        try:
            self.text = self.CLUE_FORMATS[self.acard.role].format(a=self.acard, mystery=mystery)
        except KeyError:
            self.text = "{a} has something to do with {mystery}".format(a=self.acard, mystery=mystery)

    def matches(self, solution):
        return self.acard in solution

    def is_involved(self, gameob):
        # Return True if this gameob is involved with this card.
        return gameob and gameob is self.acard.gameob

    def __str__(self):
        return self.text


class OkapiPuzzle:
    ALPHA_KEYS = "abcdefghijklmnopqrstuvwzxyz"
    def __init__(self, name, decks, solution_form, solution=None):
        self.name = name
        self.decks = decks
        self.solution_form = solution_form
        self.solution = solution or [random.choice(d.cards) for d in decks]

        mydict = dict([(self.ALPHA_KEYS[n], card) for n,card in enumerate(self.solution)])
        self.solution_text = solution_form.format(**mydict)

        tries = 0

        while tries < 20:
            self.unknown_clues = self.generate_all_clues()
            self.known_clues = list()
            all_solutions = self.generate_all_solutions()
            t = len(self.decks) * 4
            while t > 0 or len(self.unknown_clues) > 10:
                i = 1
                while i < len(self.unknown_clues) and self.number_of_matches(self.unknown_clues[:i], all_solutions) > 1:
                    i += 1
                self.unknown_clues = self.unknown_clues[:i]
                random.shuffle(self.unknown_clues)
                if len(self.unknown_clues) < 6:
                    break
                t -= 1
                if t < -10:
                    break
            if len(self.unknown_clues) <= min(tries+3, 10):
                break
            tries += 1

        self.solved = False

    def generate_all_solutions(self, deck_n=0):
        mylist = list()
        if deck_n < len(self.decks) - 1:
            later_solutions = self.generate_all_solutions(deck_n + 1)
            for card in self.decks[deck_n].cards:
                for ls in later_solutions:
                    mylist.append([card] + ls)
        else:
            mylist = [[card] for card in self.decks[deck_n].cards]
        return mylist

    def generate_all_clues(self):
        # Generate all possible clues for this puzzle.
        myclues = list()

        mydecks = list(self.decks)
        random.shuffle(mydecks)

        for t in range(len(self.solution) - 1):
            for tt in range(t + 1, len(self.solution)):
                myclues.append(ABTogetherClue(self.solution[t], self.solution[tt], self))

        for t in range(len(mydecks)):
            for card in mydecks[t].cards:
                if card not in self.solution:
                    myclues.append(ANotSolutionClue(card, self))
                    for c2 in mydecks[t - 1].cards:
                        myclues.append(ABNotTogetherClue(card, c2, self))
                else:
                    myclues.append(AIsSolutionClue(card, self))

        random.shuffle(myclues)

        return myclues

    def clues_match_solution(self, clues, solution):
        return all([c.matches(solution) for c in clues]) or None in solution

    def number_of_matches(self, clues, all_solutions=None):
        if not all_solutions:
            all_solutions = self.generate_all_solutions()
        n = 0
        for s in all_solutions:
            if self.clues_match_solution(clues, s):
                n += 1
        return n

    def known_clues_match_solution(self, solution):
        return self.clues_match_solution(self.known_clues, solution)

    def number_of_known_matches(self):
        return self.number_of_matches(self.known_clues)

    def __str__(self):
        return self.name


class ImageDeckWidget(widgets.ColumnWidget):
    DEFAULT_HEIGHT = 164

    def __init__(self, mydeck: SusDeck, on_select, **kwargs):
        super().__init__(0, 0, 100, self.DEFAULT_HEIGHT, **kwargs)
        self.add_interior(widgets.LabelWidget(0, 0, self.w, 0, mydeck.name, justify=0))
        self._on_select = on_select

        self.mystery_sprite = image.Image("sys_mystery.png")
        self.my_image = widgets.ButtonWidget(0, 0, 100, 100, self.mystery_sprite, 0)
        self.add_interior(self.my_image)

        self.my_dropdown = widgets.DropdownWidget(0, 0, self.w, 0, draw_border=True, on_select=self.on_select)
        self.add_interior(self.my_dropdown)
        self.my_dropdown.add_item("==None==", None)

        self.sprites = dict()
        for card in mydeck.cards:
            self.my_dropdown.add_item(card.name, card)
            try:
                if "image_fun" in card.data:
                    self.sprites[card] = card.data["image_fun"]()
                elif "image_name" in card.data:
                    self.sprites[card] = image.Image(card.data["image_name"], 100, 100)
            except FileNotFoundError:
                self.sprites[card] = self.mystery_sprite

    def on_select(self, *args):
        card = self.my_dropdown.menu.get_current_value()
        if card:
            self.my_image.sprite = self.sprites.get(card, self.mystery_sprite)
            self.my_image.frame = card.data.get("frame", 0)
        else:
            self.my_image.sprite = self.mystery_sprite
            self.my_image.frame = 0
        if self._on_select:
            self._on_select(card)

    @property
    def value(self):
        return self.my_dropdown.menu.get_current_value()


class HypothesisWidget(widgets.ColumnWidget):
    def __init__(self, mystery: OkapiPuzzle, on_change, on_solution, deck_widget_class=ImageDeckWidget, **kwargs):
        # on_change and on_solution are methods that get called when the hypothesis changes or when the correct
        # hypothesis is formed.
        super().__init__(0, 0, 500, 100, draw_border=True, padding=10, **kwargs)
        self.mystery = mystery
        self.on_change = on_change
        self.on_solution = on_solution
        self.set_header(
            widgets.LabelWidget(0, 0, justify=0, text=mystery.name, font=my_state.big_font, draw_border=True))
        self.myrow = widgets.RowWidget(0, 0, self.w, deck_widget_class.DEFAULT_HEIGHT)
        for deck in mystery.decks:
            self.myrow.add_center(deck_widget_class(deck, self.on_select))
        self.add_interior(self.myrow)
        self.result_label = widgets.LabelWidget(0, 0, self.w, 0, "Possible", font=my_state.big_font, color=INFO_GREEN,
                                                justify=0)
        self.add_interior(self.result_label)

    def get_hypothesis(self):
        return tuple([w.value for w in self.myrow._center_widgets])

    def on_select(self, choice):
        hypo = self.get_hypothesis()
        if self.mystery.known_clues_match_solution(hypo):
            if self.mystery.number_of_known_matches() == 1 and hypo == tuple(self.mystery.solution):
                self.result_label.text = "Solved!"
                self.result_label.color = INFO_HILIGHT
                self.on_solution()
            else:
                self.result_label.text = "Possible"
                self.result_label.color = INFO_GREEN
                self.on_change()
        else:
            self.result_label.text = "Impossible"
            self.result_label.color = ENEMY_RED
            self.on_change()


class OkapiPuzzleWidget(widgets.ColumnWidget):
    def __init__(self, mystery: OkapiPuzzle, camp, on_solution, deck_widget_class=ImageDeckWidget, **kwargs):
        super().__init__(-250, -200, 500, 400, center_interior=True, padding=16, **kwargs)
        self.mystery = mystery
        self.camp = camp
        self._solution_fun = on_solution
        self.hywidget = HypothesisWidget(mystery, self.update_clues, self.on_solution,
                                         deck_widget_class=deck_widget_class)
        self.add_interior(self.hywidget)

        up_arrow = widgets.ButtonWidget(0, 0, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                        on_frame=0, off_frame=1)
        down_arrow = widgets.ButtonWidget(0, 0, 128, 16, sprite=image.Image("sys_updownbuttons.png", 128, 16),
                                          on_frame=2, off_frame=3)
        self.myclues = widgets.ScrollColumnWidget(0, 0, 350, 350 - self.hywidget.h, up_arrow, down_arrow,
                                                  draw_border=True)
        self.add_interior(up_arrow)
        self.add_interior(self.myclues)
        self.add_interior(down_arrow)

        self.keep_going = True
        closebuttonsprite = image.Image('sys_closeicon.png')

        self.close_button = widgets.ButtonWidget(
            -closebuttonsprite.frame_width // 2, -closebuttonsprite.frame_height // 2, closebuttonsprite.frame_width,
            closebuttonsprite.frame_height, closebuttonsprite, 0, on_click=self.close_browser, parent=self,
            anchor=frects.ANCHOR_UPPERRIGHT)
        self.children.append(self.close_button)

        self.update_clues()

    def close_browser(self, button=None, ev=None):
        self.keep_going = False
        my_state.widgets.remove(self)

    def update_clues(self):
        self.myclues.clear()
        ok_clues = list()
        contradictions = list()
        hypo = self.hywidget.get_hypothesis()

        # Sort the clues between those that contradict the current hypothesis and those that don't.
        for clue in self.mystery.known_clues:
            if not self.mystery.clues_match_solution([clue], hypo):
                contradictions.append(clue)
            else:
                ok_clues.append(clue)

        contradictions.sort(key=lambda c: c.text)
        ok_clues.sort(key=lambda c: c.text)
        for c in contradictions:
            self.myclues.add_interior(widgets.LabelWidget(0, 0, 350, 0, c.text, ENEMY_RED))
        for c in ok_clues:
            self.myclues.add_interior(widgets.LabelWidget(0, 0, 350, 0, c.text, INFO_GREEN))

    def on_solution(self):
        self.update_clues()
        if self._solution_fun:
            self._solution_fun()
        self.mystery.solved = True
        self.camp.check_trigger(MYSTERY_SOLVED, self.mystery)

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
