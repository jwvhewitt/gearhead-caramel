import gears
from game.content import plotutility, backstory
from game.content.mechtarot import TarotCard, CONSEQUENCE_WIN, ME_AUTOREVEAL, TarotSignal, TarotSocket, TarotTransformer

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
ME_CRIMED = "ME_CRIMED"
ME_LIABILITY = "ME_LIABILITY"

SIG_INCRIMINATE = "SIG_INCRIMINATE"  # Looks like someone did crime
SIG_ACCUSE = "SIG_ACCUSE"  # Bring the hammer of justice against the evil-doer; uses ME_CRIME
SIG_CANCEL = "SIG_CANCEL"  # The power and/or influence of this card is taken away; uses ME_LIABILITY
SIG_AMPLIFY = "SIG_AMPLIFY"  # A secret has been revealed but needs amplification; uses ME_LIABILITY
SIG_EXTORT = "SIG_EXTORT"   # A ME_LIABILITY is known, and may be served to the target for nefarious purposes


#   *************************************
#   ***   TAROT  UTILITY  FUNCTIONS   ***
#   *************************************

def get_element_effect(elem, elem_id, script_list):
    myeffect = gears.QualityOfLife()
    for card in script_list:
        if card.elements.get(elem_id) is elem and hasattr(card, "QOL"):
            myeffect.add(card.QOL)
    return myeffect


class PersonalLiability(object):
    def __init__(self,npc,camp):
        self.text = None
        self.npc = npc
        self.camp = camp

    def __str__(self):
        if not self.text:
            myeffect = get_element_effect(self.npc, ME_PERSON, list(self.camp.active_plots()))
            print(myeffect.get_keywords())
            mystory = backstory.Backstory(("ME_LIABILITY_FOR_PERSON",), {ME_PERSON: self.npc}, myeffect.get_keywords())
            self.text = mystory.get()
        return self.text


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

    AUTO_MEMO = "{ME_PERSON} is a media figure with a large audience in {METROSCENE}."

    def custom_init(self, nart):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_TheMedia", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]

        return True


class BadPress(TarotCard):
    # A person's liability has become widely known. Too late to shut this can of worms.
    TAGS = ()
    active = True

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
            self.memo = "You learned that {ME_LIABILITY}.".format(**self.elements)

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
        print("Demagogue'd")
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

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheDisbanded", (ME_FACTION,), (ME_CRIME, ME_CRIMED))
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
            self.elements[ME_CRIMED] = sp.elements[ME_CRIMED]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, "a crime")
            if not self.elements.get(ME_CRIMED):
                self.register_element(ME_CRIMED, "committed crimes")
            self.memo = "You learned that {ME_FACTION} {ME_CRIMED}.".format(**self.elements)

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
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof", (ME_FACTION,), (ME_CRIME, ME_CRIMED))
            }
        ),
    )

    def custom_init(self, nart):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_ClueItem", ident="REVEAL")
            self.elements[ME_PUZZLEITEM] = sp.elements[ME_PUZZLEITEM]
        return True


class FactionInvestigator(TarotCard):
    TAGS = (MT_PERSON,)
    active = True
    ONE_USE = True
    AUTO_MEMO = "{ME_PERSON} at {MEP_LOC} is investigating {ME_FACTION}."

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Investigate", TarotSignal(SIG_INCRIMINATE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof", [], (ME_FACTION, ME_CRIME, ME_CRIMED))
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
        self.elements["MEP_LOC"] = sp.elements[ME_PERSON].get_scene()
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
            self.elements[ME_CRIMED] = sp.elements[ME_CRIMED]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME, "an atrocity")
            if not self.elements.get(ME_CRIMED):
                self.register_element(ME_CRIMED, "committed atrocities")
            self.memo = "You learned that {ME_FACTION} {ME_CRIMED}.".format(**self.elements)

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
        print("{} is at {}".format(npc,npc.get_scene()))
        self.visible = True
        return True

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
        sp = self.add_sub_plot(nart, "MT_REVEAL_TEST", ident="REVEAL")
        return True

    def REVEAL_WIN(self,camp):
        print("Test scenario REVEAL activated")
        self.reveal(camp)


