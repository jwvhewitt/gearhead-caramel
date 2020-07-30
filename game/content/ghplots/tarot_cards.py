import gears
from game.content import plotutility, backstory
from game.content.mechtarot import TarotCard, CONSEQUENCE_WIN, ME_AUTOREVEAL, TarotSignal, TarotSocket, TarotTransformer
import random
from game import ghdialogue

MT_CRIME = "CRIME"
MT_FACTION = "FACTION"
MT_HEROIC = "HEROIC"
MT_INCRIMINATING = "INCRIMINATING"
MT_PERSON = "PERSON"
MT_THREAT = "THREAT"

ME_FACTION = "ME_FACTION"
ME_PERSON = "ME_PERSON"
ME_ACTOR = "ME_ACTOR"  # The performer of an action; a character or faction
ME_PUZZLEITEM = "ME_PUZZLEITEM"
ME_CRIME = "ME_CRIME"
ME_LIABILITY = "ME_LIABILITY"
ME_POSITION = "ME_POSITION"   # Used in the SIG_HIRE signal
ME_PROBLEM = "ME_PROBLEM"     # A problem/solution that can be solved with technobabble
ME_LOCATION = "ME_LOCATION"
ME_BOOSTSOURCE = "ME_BOOSTSOURCE"   # The source of a SCIENCEBOOST signal. Not the band that wrote "Masterstroke".

SIG_INCRIMINATE = "SIG_INCRIMINATE"  # Looks like someone did crime
SIG_ACCUSE = "SIG_ACCUSE"  # Bring the hammer of justice against the evil-doer; uses ME_CRIME
SIG_CANCEL = "SIG_CANCEL"  # The power and/or influence of this card is taken away; uses ME_LIABILITY
SIG_AMPLIFY = "SIG_AMPLIFY"  # A secret has been revealed but needs amplification; uses ME_LIABILITY
SIG_EXTORT = "SIG_EXTORT"   # A ME_LIABILITY is known, and may be served to the target for nefarious purposes
SIG_CRIME = "SIG_CRIME"     # Signal broadcast by a raw crime.
SIG_DECRYPT = "SIG_DECRYPT"
SIG_HIRE = "SIG_HIRE"
SIG_CURE = "SIG_CURE"       # Cure a disease using a techno solution
SIG_INGREDIENTS = "SIG_INGREDIENTS"
SIG_APPLY = "SIG_APPLY"     # Solve a problem using a techno solution; analagous to SIG_CURE
SIG_SCIENCEBOOST = "SIG_SCIENCEBOOST"   # You have a resource that can boost scientific effort, no questions asked
SIG_FOODBOOST = "SIG_FOODBOOST"       # Have some food, maybe that will solve your problem.


#   *************************************
#   ***   TAROT  UTILITY  FUNCTIONS   ***
#   *************************************

def get_element_effect(elem, elem_id, script_list):
    myeffect = gears.QualityOfLife()
    for card in script_list:
        if card.elements.get(elem_id) is elem and hasattr(card, "QOL"):
            myeffect.add(card.QOL)
    return myeffect


class TechnoProblem(object):
    def __init__(self,problem,solution="",tags=()):
        self.problem = problem
        self.solution = solution
        self.tags = set(tags)

    def update(self, other):
        self.problem = other.problem
        self.solution = other.solution
        self.tags = set(other.tags)

    def __str__(self):
        return self.problem



class PersonalLiability(object):
    def __init__(self,npc,camp):
        self.text = None
        self.npc = npc
        self.camp = camp

    def __str__(self):
        if not self.text:
            myeffect = get_element_effect(self.npc, ME_PERSON, list(self.camp.active_plots()))
            mystory = backstory.Backstory(("ME_LIABILITY_FOR_PERSON",), {ME_PERSON: self.npc}, myeffect.get_keywords())
            self.text = mystory.get()
        return self.text


class CrimeObject(object):
    def __init__(self, text, ed):
        # text is the noun form of the crime; "Barney's murder"
        # ed is the verb phrase form of the crime; "murdered Barney"
        self.text = text
        self.ed = ed

    def update(self, other):
        self.text = other.text
        self.ed = other.ed

    def __str__(self):
        return self.text


class PositionObject(object):
    def __init__(self, job_title):
        self.job_title = job_title

    def update(self, other):
        self.job_title = other.job_title

    def __str__(self):
        return self.job_title


def find_npc_antivirtues(npc, metro):
    mylist = list()
    myeffect = get_element_effect(npc, ME_PERSON, metro.scripts)
    if myeffect.stability < 0:
        mylist.append(gears.personality.Justice)
    if myeffect.community < 0:
        mylist.append(gears.personality.Fellowship)
    if myeffect.health < 0:
        mylist.append(gears.personality.Peace)
    if myeffect.defense < 0:
        mylist.append(gears.personality.Duty)
    if myeffect.prosperity < 0:
        mylist.append(gears.personality.Glory)
    return mylist or gears.personality.VIRTUES


#   ************************
#   ***   TAROT  CARDS   ***
#   ************************


class FeetOfClay(TarotCard):
    # A liability of ME_PERSON is revealed
    TAGS = ()
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_AMPLIFY, [ME_PERSON, ME_LIABILITY]
        ),
        TarotSignal(
            SIG_EXTORT, [ME_PERSON, ME_LIABILITY]
        ),
    )

    AUTO_MEMO = "People in {METROSCENE} are turning against {ME_PERSON}. {ME_LIABILITY}."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_FeetOfClay", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
            if ME_LIABILITY not in self.elements:
                self.elements[ME_LIABILITY] = sp.elements[ME_LIABILITY]
        return True


class TheMedia(TarotCard):
    # A person that has the power to amplify a message
    TAGS = (MT_PERSON,)
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Amplify", TarotSignal(SIG_AMPLIFY, ),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("BadPress", ((ME_ACTOR, ME_PERSON),), (ME_PERSON, ME_LIABILITY))
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} is a {ME_PERSON.job} with a large audience in {METROSCENE}."

    def custom_init(self, nart):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_TheMedia", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class WannabeReporter(TarotCard):
    # A journalist seeking a platform
    TAGS = (MT_PERSON,)
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_HireMe", TarotSignal(SIG_HIRE, (ME_POSITION,)),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheMedia", (ME_PERSON,), ())
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} at {ME_PERSON.scene} is a reporter looking for a job."

    def custom_init(self, nart):
        if ME_POSITION not in self.elements:
            self.elements[ME_POSITION] = PositionObject("Reporter")
        else:
            self.elements[ME_POSITION].job_title = "Reporter"
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_WannabeReporter", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class HelpWanted(TarotCard):
    # Looking for a job? This person is hiring.
    TAGS = (MT_PERSON,)
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_HIRE, [ME_POSITION, ]
        ),
    )

    AUTO_MEMO = "{ME_PERSON} at {ME_PERSON.scene} is planning to hire a {ME_POSITION}."

    def custom_init(self, nart):
        if ME_POSITION not in self.elements:
            self.elements[ME_POSITION] = PositionObject("Assistant")

        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_HelpWanted", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class BadPress(TarotCard):
    # A person's liability has become widely known. Too late to shut this can of worms.
    TAGS = ()
    active = True
    AUTO_MEMO = "Everyone in {METROSCENE} now knows that {ME_LIABILITY}."

    SIGNALS = (
        TarotSignal(
            SIG_CANCEL, [ME_PERSON, ]
        ),
    )

    def custom_init(self, nart):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_BadPress", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
            if ME_LIABILITY not in self.elements:
                self.elements[ME_LIABILITY] = sp.elements[ME_LIABILITY]
            if ME_ACTOR not in self.elements:
                self.elements[ME_ACTOR] = sp.elements[ME_ACTOR]
        else:
            if not self.elements.get(ME_LIABILITY):
                self.register_element(ME_LIABILITY, "{ME_PERSON} is utterly terrible".format(**self.elements))

        return True


class TheExiled(TarotCard):
    # A person has been driven out due to their real or perceived crimes.
    TAGS = (ME_PERSON,)
    QOL = gears.QualityOfLife(stability=1)
    active = True


class HasBeen(TarotCard):
    # A person's influence has been spent, reducing them to an empty punchline.
    TAGS = (ME_PERSON,)
    QOL = gears.QualityOfLife(community=1)
    active = True


class CultHierophant(TarotCard):
    # This character has become an untouchable and poisonous presence.
    TAGS = (ME_PERSON,)
    QOL = gears.QualityOfLife(stability=-3, community=-3)
    active = True


class Demagogue(TarotCard):
    # A character exploiting local divisions for personal gain
    TAGS = (MT_THREAT, ME_PERSON)
    UNIQUE = True
    QOL = gears.QualityOfLife(community=-3)
    active = True
    NEGATIONS = ("HasBeen",)

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Cancel", TarotSignal(SIG_CANCEL, [ME_PERSON]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("HasBeen", (ME_PERSON,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_Extort", TarotSignal(SIG_EXTORT, [ME_PERSON]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("CultHierophant", (ME_PERSON,)),
                "CONSEQUENCE_GOAWAY": TarotTransformer("TheExiled", (ME_PERSON,)),
            }
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Demagogue", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
        else:
            self.memo = "You learned that {} is a demagogue.".format(self.elements[ME_PERSON])
        return True


class TheDisbanded(TarotCard):
    # This faction has been utterly destroyed; it now exists only as a cautionary tale.
    TAGS = (ME_FACTION,)
    QOL = gears.QualityOfLife(stability=1)
    active = True


class HateClub(TarotCard):
    # A group of people who love to hate.
    TAGS = (MT_THREAT, ME_FACTION)
    QOL = gears.QualityOfLife(stability=-2, community=-2)
    active = True
    NEGATIONS = ("TheDisbanded",)
    UNIQUE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheDisbanded", (ME_FACTION,), (ME_CRIME, ))
            }
        ),
    )

    def custom_init(self, nart):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_HateClub", ident="REVEAL")
            if ME_FACTION not in self.elements:
                self.elements[ME_FACTION] = sp.elements[ME_FACTION]
        else:
            self.memo = "You learned that {} has been taken over by extremists.".format(self.elements[ME_FACTION])

        return True


class FactionCrimesProof(TarotCard):
    # Proof that a faction has committed a crime.
    TAGS = (MT_INCRIMINATING,)
    active = True
    ONE_USE = True

    SIGNALS = (
        TarotSignal(
            SIG_ACCUSE, [ME_FACTION, ]
        ),
    )

    def custom_init(self, nart):
        if ME_FACTION not in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_WarCrime", ident="REVEAL")
            self.elements[ME_CRIME] = sp.elements[ME_CRIME]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, CrimeObject("a crime","committed crimes"))
            self.memo = "You learned that {ME_FACTION} {ME_CRIME.ed}.".format(**self.elements)

        return True

class CharacterCrimesProof(TarotCard):
    # Proof that a character has committed a crime.
    TAGS = (MT_INCRIMINATING,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "You learned that {ME_PERSON} {ME_CRIME.ed}."

    SIGNALS = (
        TarotSignal(
            SIG_ACCUSE, [ME_PERSON, ]
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_PersonalCrime", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
            self.elements[ME_CRIME] = sp.elements[ME_CRIME]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, CrimeObject("a crime","committed crimes"))

        return True


class FactionClue(TarotCard):
    # A clue linking a faction to a crime.
    TAGS = ()
    active = True
    ONE_USE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_SearchClue", TarotSignal(SIG_INCRIMINATE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof", (ME_FACTION,), (ME_CRIME, ))
            }
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_ClueItem", ident="REVEAL")
            self.elements[ME_PUZZLEITEM] = sp.elements[ME_PUZZLEITEM]
        return True


class FactionComputer(TarotCard):
    TAGS = ()
    active = True
    ONE_USE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Decrypt", TarotSignal(SIG_DECRYPT, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionClue", (ME_FACTION, ME_PUZZLEITEM), [])
            }
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_FactionComputer", ident="REVEAL")
            self.elements[ME_PUZZLEITEM] = sp.elements[ME_PUZZLEITEM]
        return True


class FactionPassword(TarotCard):
    # Uncover a password belonging to a faction member.
    TAGS = (MT_FACTION,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "You learned that \"{PASSWORD}\" is a password for {ME_FACTION}."

    SIGNALS = (
        TarotSignal(
            SIG_DECRYPT, [ME_FACTION, ]
        ),
    )

    def custom_init(self, nart):
        if ME_FACTION not in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        self.elements["PASSWORD"] = self.get_random_password()
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Password", ident="REVEAL")

        return True

    def get_noun(self):
        return random.choice(ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Noun]"][ghdialogue.ghgrammar.Default])

    def get_number(self):
        return "".join([str(random.randint(0,9)) for r in range(random.randint(2,5))])

    def get_random_password(self):
        mylist = list()
        for t in range(3):
            if random.randint(1,3) != 1:
                mylist.append(self.get_noun())
            else:
                mylist.append(self.get_number())
        return "".join(mylist)


class FactionInvestigator(TarotCard):
    TAGS = (MT_PERSON,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "{ME_PERSON} at {MEP_LOC} is investigating {ME_FACTION}."

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Investigate", TarotSignal(SIG_INCRIMINATE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof", [ME_FACTION], [ME_CRIME])
            }
        ),
    )

    def custom_init(self, nart):
        if ME_FACTION not in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Investigator", ident="REVEAL",
                                   elements={"INVESTIGATION_SUBJECT": str(self.elements[ME_FACTION])})
            self.elements[ME_PERSON] = sp.elements[ME_PERSON]
        self.elements["MEP_LOC"] = self.elements[ME_PERSON].get_scene()
        return True


class Atrocity(TarotCard):
    # A faction made a war crime.
    TAGS = (MT_CRIME,)
    QOL = gears.QualityOfLife(stability=-3)
    active = True
    ONE_USE = True

    SIGNALS = (
        TarotSignal(
            SIG_INCRIMINATE, [ME_FACTION, ]
        ),
    )

    def custom_init(self, nart):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if ME_FACTION not in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_WarCrime", ident="REVEAL")
            self.elements[ME_CRIME] = sp.elements[ME_CRIME]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, CrimeObject("an atrocity","committed atrocities"))
            self.memo = "You learned that {ME_FACTION} {ME_CRIME.ed}.".format(**self.elements)

        return True


class Murder(TarotCard):
    # A murder has been committed.
    TAGS = (MT_CRIME,)
    QOL = gears.QualityOfLife(stability=-1, health=-2)
    active = True
    ONE_USE = True
    AUTO_MEMO = "You learned that {ME_CRIME} has taken place."

    SIGNALS = (
        TarotSignal(
            SIG_CRIME, [ME_CRIME, ]
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Murder", ident="REVEAL")
            if not self.elements.get(ME_CRIME):
                self.elements[ME_CRIME] = sp.elements[ME_CRIME]
            else:
                self.elements[ME_CRIME].update(sp.elements[ME_CRIME])
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, CrimeObject("a murder", "murdered someone"))

        return True


class Henchman(TarotCard):
    TAGS = (MT_PERSON,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "{ME_PERSON} has been doing dirty work for {ME_ACTOR}."

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_HenchmanLiability", TarotSignal(SIG_CRIME, [ME_CRIME]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FeetOfClay", [(ME_PERSON, ME_ACTOR), ME_LIABILITY], [ME_CRIME, ])
            }
        ),
    )

    def custom_init(self, nart):
        if ME_CRIME not in self.elements:
            self.elements[ME_CRIME] = CrimeObject("the atrocity", "committed an atrocity")
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Henchman", ident="REVEAL")
            self.elements[ME_PERSON] = sp.elements[ME_PERSON]
        return True


class TheQuitter(TarotCard):
    TAGS = (MT_PERSON,MT_FACTION,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "{ME_PERSON} used to work for {ME_FACTION}."

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_InformantF", TarotSignal(SIG_CRIME, [ME_CRIME]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Atrocity", [ME_FACTION, ME_CRIME], [])
            }
        ),
    )

    def custom_init(self, nart):
        if ME_FACTION not in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        if ME_CRIME not in self.elements:
            self.elements[ME_CRIME] = CrimeObject("the atrocity","committed an atrocity")
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Quitter", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
        return True


class Recovery(TarotCard):
    # From an illness or physical problem
    QOL = gears.QualityOfLife(health=1)
    active = True


class EcologicalBalance(TarotCard):
    # Recovery from pollution or other ecological damage
    QOL = gears.QualityOfLife(prosperity=1)
    active = True


class Epidemic(TarotCard):
    # An illness strikes the area.
    TAGS = (MT_THREAT, )
    QOL = gears.QualityOfLife(health=-4, prosperity=-1)
    active = True
    NEGATIONS = ("Recovery",)
    UNIQUE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Cure", TarotSignal(SIG_CURE, [ME_PROBLEM]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Recovery", (ME_PROBLEM,))
            }
        ),
    )

    AUTO_MEMO = "{METROSCENE} has been afflicted with {ME_PROBLEM}."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name(),("DISEASE",))
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Epidemic", ident="REVEAL")

        return True


class TheCure(TarotCard):
    # A cure for an epidemic.
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_CURE, [ME_PROBLEM, ]
        ),
    )

    AUTO_MEMO = "You've obtained a source of {ME_PROBLEM.solution}, which can cure {ME_PROBLEM}."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name())
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_TheCure", ident="REVEAL")

        return True


class Chemist(TarotCard):
    # Someone who might be able to make medicine.
    TAGS = (MT_PERSON, )
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Ingredients", TarotSignal(SIG_INGREDIENTS, [ME_PROBLEM]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheCure", (ME_PROBLEM,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_ScienceBoost", TarotSignal(SIG_SCIENCEBOOST, []),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Invention", (ME_PROBLEM,))
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} in {ME_PERSON.scene} may be able to fabricate a cure for {ME_PROBLEM}, given the right ingredients."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name())
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Chemist", ident="REVEAL")
            self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class WannabeChemist(TarotCard):
    # An aspiring techno-alchemist
    TAGS = (MT_PERSON,)
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_HireMe", TarotSignal(SIG_HIRE, (ME_POSITION,)),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Chemist", (ME_PERSON,ME_PROBLEM), ())
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} at {ME_PERSON.scene} wants to set up a chemistry lab in order to combat {ME_PROBLEM}."

    def custom_init(self, nart):
        if ME_POSITION not in self.elements:
            self.elements[ME_POSITION] = PositionObject("Chemist")
        else:
            self.elements[ME_POSITION].job_title = "Chemist"
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_WannabeChemist", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class SecretIngredients(TarotCard):
    # Ingredients are needed to build a solution.
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_INGREDIENTS, [ME_PROBLEM, ]
        ),
    )

    AUTO_MEMO = "You have obtained the ingredients needed for the {ME_PROBLEM.solution}."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name())
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_SecretIngredients", ident="REVEAL")

        return True


class RobberBaron(TarotCard):
    # Exploitation leading to widespread poverty.
    TAGS = (MT_THREAT, MT_PERSON, MT_FACTION)
    QOL = gears.QualityOfLife(prosperity=-4, community=-1)
    active = True
    NEGATIONS = ("TheExiled",)
    UNIQUE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_PERSON,]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheExiled", (ME_PERSON,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_FACTION, ]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheExiled", (ME_PERSON,))
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} practically owns {METROSCENE}."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_RobberBaron", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
            if ME_FACTION in sp.elements:
                self.elements[ME_FACTION] = sp.elements[ME_FACTION]
        if ME_FACTION not in self.elements:
            mynpc = self.elements[ME_PERSON]
            self.elements[ME_FACTION] = gears.factions.Circle(nart.camp,name="{} Industries".format(mynpc))
            mynpc.faction = self.elements[ME_FACTION]
        return True


class DinosaurAttack(TarotCard):
    # Genetically engineered dinosaurs causing problems.
    TAGS = (MT_THREAT, )
    QOL = gears.QualityOfLife(defense=-4, health=-1)
    active = True
    NEGATIONS = ("EcologicalBalance",)
    UNIQUE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_DinosaurSolution", TarotSignal(SIG_APPLY, [ME_PROBLEM]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("EcologicalBalance", (ME_PROBLEM,))
            }
        ),
    )

    AUTO_MEMO = "{METROSCENE} is under constant threat from mutant dinosaurs."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem('mutant dinosaurs', "sonic fence", ("MONSTERS",))
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Dinosaurs", ident="REVEAL")

        return True


class Invention(TarotCard):
    # A solution for a techproblem.
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_APPLY, [ME_PROBLEM, ]
        ),
    )

    AUTO_MEMO = "You've obtained a {ME_PROBLEM.solution} to fix {METROSCENE}'s {ME_PROBLEM} problem."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name())
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Invention", ident="REVEAL")

        return True


class Inventor(TarotCard):
    # Someone who might be able to make an invention.
    TAGS = (MT_PERSON, )
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Ingredients", TarotSignal(SIG_INGREDIENTS, [ME_PROBLEM]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Invention", (ME_PROBLEM,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_ScienceBoost", TarotSignal(SIG_SCIENCEBOOST, []),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Invention", (ME_PROBLEM,))
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} in {ME_PERSON.scene} may be able to build a {ME_PROBLEM.solution} for {ME_PROBLEM}, given the right supplies."

    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem(plotutility.random_disease_name(), plotutility.random_medicine_name())
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Inventor", ident="REVEAL")
            self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class AbandonedLaboratory(TarotCard):
    # There's a laboratory sitting right there, potentially full of PreZero tech.
    active = True
    scope = True

    SIGNALS = (
        TarotSignal(
            SIG_SCIENCEBOOST, []
        ),
    )

    AUTO_MEMO = "You've found {ME_LOCATION}."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Laboratory", ident="REVEAL")
            self.elements[ME_LOCATION] = sp.elements[ME_LOCATION]
            self.elements[ME_BOOSTSOURCE] = str(sp.elements[ME_LOCATION])
        else:
            self.elements[ME_BOOSTSOURCE] = "the abandoned laboratory"

        return True


class Shortages(TarotCard):
    TAGS = (MT_THREAT, )
    QOL = gears.QualityOfLife(prosperity=-3, health=-2)
    active = True
    NEGATIONS = ("Recovery",)
    UNIQUE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_FamineRelief", TarotSignal(SIG_FOODBOOST, []),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("Recovery", [])
            }
        ),
    )

    AUTO_MEMO = "{METROSCENE} is suffering from a shortage of basic necessities."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Shortages", ident="REVEAL")

        return True


class TheFarm(TarotCard):
    active = True

    SIGNALS = (
        TarotSignal(
            SIG_FOODBOOST, []
        ),
    )

    AUTO_MEMO = "{ME_BOOSTSOURCE} can provide food for {METROSCENE}."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Farm", ident="REVEAL")
            self.elements[ME_BOOSTSOURCE] = sp.elements[ME_BOOSTSOURCE]
        elif ME_BOOSTSOURCE not in self.elements:
            self.elements[ME_BOOSTSOURCE] = "the farm"

        return True


class CursedEarth(TarotCard):
    active = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_CursedEarthSolution", TarotSignal(SIG_APPLY, [ME_PROBLEM]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheFarm", (ME_PROBLEM,ME_BOOSTSOURCE))
            }
        ),
    )

    AUTO_MEMO = "The land around {METROSCENE} is too damaged to grow anything."
    SOLUTIONS = ("terraforming kit", "soil purifier", "isotope filter")
    def custom_init(self, nart):
        if ME_PROBLEM not in self.elements:
            self.elements[ME_PROBLEM] = TechnoProblem('polluted land', random.choice(self.SOLUTIONS))
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_CursedEarth", ident="REVEAL")

        return True


class Kleptocrat(TarotCard):
    # A politician with their hand in the treasury
    TAGS = (MT_THREAT, ME_PERSON)
    UNIQUE = True
    QOL = gears.QualityOfLife(prosperity=-2, stability=-2)
    active = True
    NEGATIONS = ("HasBeen", "TheExiled")

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_PERSON,]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheExiled", (ME_PERSON,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_Cancel", TarotSignal(SIG_CANCEL, [ME_PERSON]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("HasBeen", (ME_PERSON,))
            }
        ),
        TarotSocket(
            "MT_SOCKET_Extort", TarotSignal(SIG_EXTORT, [ME_PERSON]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("CultHierophant", (ME_PERSON,)),
                "CONSEQUENCE_GOAWAY": TarotTransformer("TheExiled", (ME_PERSON,)),
            }
        ),
    )

    AUTO_MEMO = "{ME_PERSON} at {ME_PERSON.scene} is a corrupt {ME_PERSON.job}."

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Kleptocrat", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True



#   **************************
#   ***   UTILITY  CARDS   ***
#   **************************

class SocketTester(TarotCard):
    LABEL = "TEST_TAROT_SOCKET"
    active = True

    def custom_init(self, nart):
        sp = self.add_sub_plot(nart,"ADD_BORING_NPC",elements={"LOCALE":None})
        npc = sp.elements["NPC"]
        self.elements[ME_PERSON] = npc
        self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        self.elements[ME_CRIME] = CrimeObject("the llama burning", "burned the llama")
        self.visible = True
        return True

    def METROSCENE_ENTER(self,camp):
        npc = self.elements[ME_PERSON]
        print("{} is at {}".format(npc,npc.get_scene()))

    def _test_win(self,camp,alpha,beta=None):
        print("Win signal received")

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_TEST", TarotSignal("TEST_SIGNAL", []),
            consequences={
                CONSEQUENCE_WIN: _test_win
            }
        ),
    )

    SIGNALS = (
        TarotSignal(
            "TEST_SIGNAL", []
        ),
    )

class RevealTester(TarotCard):
    LABEL = "TEST_TAROT_REVEAL"
    active = True

    def custom_init(self, nart):
        self.elements[ME_FACTION] = plotutility.RandomBanditCircle(nart.camp)
        self.elements["INVESTIGATION_SUBJECT"] = "the tarot test"
        self.elements["PASSWORD"] = "HackerC64"
        sp = self.add_sub_plot(nart, "MT_REVEAL_TEST", ident="REVEAL")
        return True

    def REVEAL_WIN(self,camp):
        print("Test scenario REVEAL activated")
        self.reveal(camp)


