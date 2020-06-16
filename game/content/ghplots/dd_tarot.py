from game.content import mechtarot,plotutility
from game.content.mechtarot import TarotCard, ME_TAROTPOSITION, CONSEQUENCE_WIN, CONSEQUENCE_LOSE, \
    ME_AUTOREVEAL,CardCaller, CardDeactivator, TarotSignal, TarotSocket,TarotTransformer
import pbge
import gears
from game.ghdialogue import context
from pbge.dialogue import Offer
import random
import collections
from . import actionscenes
from . import missionbuilder

MT_CRIME = "CRIME"
MT_FACTION = "FACTION"
MT_HEROIC = "HEROIC"
MT_INCRIMINATING = "INCRIMINATING"
MT_PERSON = "PERSON"
MT_THREAT = "THREAT"

ME_FACTION = "ME_FACTION"
ME_PERSON = "ME_PERSON"
ME_PUZZLEITEM = "ME_PUZZLEITEM"
ME_CRIME = "ME_CRIME"
ME_CRIMED = "ME_CRIMED"

SIG_INCRIMINATE = "SIG_INCRIMINATE" # Looks like someone did crime
SIG_ACCUSE = "SIG_ACCUSE"           # Bring the hammer of justice against the evil-doer
SIG_CANCEL = "SIG_CANCEL"           # The power and/or influence of this card is taken away by popular sentiment


class HasBeen(TarotCard):
    TAGS = (ME_PERSON,)
    QOL = gears.QualityOfLife(community=1)
    active = True


class Demagogue(TarotCard):
    # A character exploiting local divisions for personal gain
    TAGS = (MT_THREAT,ME_PERSON)
    QOL = gears.QualityOfLife(community=-3)
    active = True
    NEGATIONS = ("HasBeen",)

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Cancel", TarotSignal(SIG_CANCEL, [ME_PERSON]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("HasBeen",(ME_PERSON,))
            }
        ),
    )

    def custom_init( self, nart ):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart, "MT_REVEAL_Demagogue", ident="REVEAL")
            if ME_PERSON not in self.elements:
                self.elements[ME_PERSON] = sp.elements[ME_PERSON]
        else:
            self.memo = "You learned that {} is a demagogue.".format(self.elements[ME_PERSON])
        print("Demagogue'd")
        return True


class TheDisbanded(TarotCard):
    TAGS = (ME_FACTION,)
    QOL = gears.QualityOfLife(stability=1)
    active = True


class HateClub(TarotCard):
    TAGS = (MT_THREAT,ME_FACTION)
    QOL = gears.QualityOfLife(stability=-2,community=-2)
    active = True
    NEGATIONS = ("TheDisbanded",)

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Accuse", TarotSignal(SIG_ACCUSE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("TheDisbanded",(ME_FACTION,),(ME_CRIME,ME_CRIMED))
            }
        ),
    )

    def custom_init( self, nart ):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart,"MT_REVEAL_HateClub",ident="REVEAL")
            if ME_FACTION not in self.elements:
                self.elements[ME_FACTION] = sp.elements[ME_FACTION]
        else:
            self.memo = "You learned that {} has been taken over by extremists.".format(self.elements[ME_FACTION])

        return True


class FactionCrimesProof(TarotCard):
    TAGS = (MT_INCRIMINATING,)
    active = True
    ONE_USE = True

    SIGNALS = (
        TarotSignal(
            SIG_ACCUSE,[ME_FACTION, ]
        ),
    )

    def custom_init( self, nart ):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not ME_FACTION in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle()
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart,"MT_REVEAL_WarCrime",ident="REVEAL")
            self.elements[ME_CRIME] = sp.elements[ME_CRIME]
            self.elements[ME_CRIMED] = sp.elements[ME_CRIMED]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME,"a crime")
            if not self.elements.get(ME_CRIMED):
                self.register_element(ME_CRIMED,"committed crimes")
            self.memo = "You learned that {ME_FACTION} {ME_CRIMED}.".format(**self.elements)

        return True



class FactionClue(TarotCard):
    TAGS = ()
    active = True
    ONE_USE = True

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_SearchClue", TarotSignal(SIG_INCRIMINATE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof",(ME_FACTION,),(ME_CRIME,ME_CRIMED))
            }
        ),
    )

    def custom_init( self, nart ):
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart,"MT_REVEAL_ClueItem",ident="REVEAL")
            self.elements[ME_PUZZLEITEM] = sp.elements[ME_PUZZLEITEM]
        return True


class FactionInvestigator(TarotCard):
    TAGS = (MT_PERSON)
    active = True
    ONE_USE = True
    ON_REVEAL_MEMO = "{ME_PERSON} at {MEP_LOC} is investigating {ME_FACTION}."

    SOCKETS = (
        TarotSocket(
            "MT_SOCKET_Investigate", TarotSignal(SIG_INCRIMINATE, [ME_FACTION]),
            consequences={
                CONSEQUENCE_WIN: TarotTransformer("FactionCrimesProof",[],(ME_FACTION,ME_CRIME,ME_CRIMED))
            }
        ),
    )

    def custom_init( self, nart ):
        if not ME_FACTION in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle()
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart,"MT_REVEAL_Investigator",ident="REVEAL",elements={"INVESTIGATION_SUBJECT":str(self.elements[ME_FACTION])})
            self.elements[ME_PERSON] = sp.elements[ME_PERSON]
            self.elements["MEP_LOC"] = sp.elements[ME_PERSON].get_scene()
            self.memo = self.ON_REVEAL_MEMO.format(**self.elements)
        return True


class Atrocity(TarotCard):
    # A faction made a war crime.
    TAGS = (MT_CRIME,)
    QOL = gears.QualityOfLife(stability=-3)
    active = True
    ONE_USE = True

    SIGNALS = (
        TarotSignal(
            SIG_INCRIMINATE,[ME_FACTION, ]
        ),
    )

    def custom_init( self, nart ):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not ME_FACTION in self.elements:
            self.elements[ME_FACTION] = plotutility.RandomBanditCircle()
        if not self.elements.get(ME_AUTOREVEAL):
            sp = self.add_sub_plot(nart,"MT_REVEAL_WarCrime",ident="REVEAL")
            self.elements[ME_CRIME] = sp.elements[ME_CRIME]
            self.elements[ME_CRIMED] = sp.elements[ME_CRIMED]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME,"an atrocity")
            if not self.elements.get(ME_CRIMED):
                self.register_element(ME_CRIMED,"committed atrocities")
            self.memo = "You learned that {ME_FACTION} {ME_CRIMED}.".format(**self.elements)

        return True

