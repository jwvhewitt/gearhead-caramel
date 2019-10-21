import glob
import pbge
import json
import collections
import gears
import random
from game import ghdialogue

ALL_BITS = list()
BITS_BY_COMMAND = collections.defaultdict(list)

class BackstoryState(object):
    def __init__(self,elements,keywords):
        self.elements = dict()
        if elements:
            self.elements.update(elements)
        self.keywords = list(keywords)

    def get_format_dict(self):
        fdic = dict()
        #ghdialogue.trait_absorb(fdic,ghdialogue.ghgrammar.DEFAULT_GRAMMAR,())
        for k,v in self.elements.items():
            fdic[str(k)] = str(v)
            if isinstance(v,gears.base.Character):
                fdic["{}_job".format(k)] = str(v.job)
                fdic["{}_gender_noun".format(k)] = str(v.gender.noun)
                fdic["{}_gender_adjective".format(k)] = str(v.gender.adjective)
                fdic["{}_subject_pronoun".format(k)] = str(v.gender.subject_pronoun)
                fdic["{}_object_pronoun".format(k)] = str(v.gender.object_pronoun)
                fdic["{}_possessive_determiner".format(k)] = str(v.gender.possessive_determiner)
                fdic["{}_absolute_pronoun".format(k)] = str(v.gender.absolute_pronoun)
        return fdic

    def copy(self):
        return self.__class__(self.elements,self.keywords)


class Backstory(object):
    def __init__(self,commands=(),elements=None,keywords=(),generate_now=True):
        self.commands = commands
        self.initial_state = BackstoryState(elements,keywords)
        self.generated_state = None
        self.bits = list()
        self.results = collections.defaultdict(list)
        if generate_now:
            self.generate()

    def choose_bit(self,command,bsstate):
        candidates = [bsb for bsb in BITS_BY_COMMAND.get(command,()) if bsb.matches_context(command,bsstate)]
        if candidates:
            return random.choice(candidates)

    def generate(self):
        self.bits = list()
        self.generated_state = self.initial_state.copy()
        self.results.clear()
        for kw in self.commands:
            mycmd = kw
            while mycmd:
                mybit = self.choose_bit(mycmd,self.generated_state)
                print mycmd, str(mybit)
                if mybit:
                    mybit.alter_state(self,self.generated_state)
                    mycmd = mybit.next_command
                else:
                    mycmd = None


class BackstoryBit(object):
    def __init__(self,name, command,requires=(),any_of=(),none_of=(),requires_elements=(),not_these_elements=(),
                 add_elements=None,remove_elements=(),add_keywords=(),remove_keywords=(),results=None,
                 data=None,next_command=""):
        self.name = name
        self.command = command
        self.requires = set(requires)
        self.any_of = set(any_of)
        self.none_of = set(none_of)
        self.requires_elements = set(requires_elements)
        self.not_these_elements = set(not_these_elements)
        self.add_elements = dict()
        if add_elements:
            self.add_elements.update(add_elements)
        self.remove_elements = remove_elements
        self.add_keywords = add_keywords
        self.remove_keywords = remove_keywords
        self.results = dict()
        if results:
            self.results.update(results)
        self.data = dict()
        if data:
            self.data.update(data)
        self.next_command = next_command

    def alter_state(self,mystory,mystate):
        for k in self.remove_elements:
            if k in mystate.elements:
                del mystate.elements[k]
        for k,v in self.add_elements.items():
            if v[0] == "CHARACTER":
                v = gears.selector.random_character(**v[1])
            mystate.elements[k] = v
        mystate.keywords += self.add_keywords
        mystate.keywords.append(self.command)
        for k in self.remove_keywords:
            if k in mystate.keywords:
                mystate.keywords.remove(k)
        mytextdict = mystate.get_format_dict()
        mygram = dict()
        ghdialogue.trait_absorb(mygram, ghdialogue.ghgrammar.DEFAULT_GRAMMAR, ())
        for k,v in self.results.items():
            mystory.results[k].append(pbge.dialogue.grammar.convert_tokens(v.format(**mytextdict),mygram))

    def matches_context(self,command,bsstate):
        return (
                self.command == command and
                (self.requires.issubset(bsstate.keywords) or not self.requires) and
                (self.requires_elements.issubset(bsstate.elements.keys()) or not self.requires_elements) and
                (self.any_of.intersection(bsstate.keywords) or not self.any_of) and
                not self.none_of.intersection(bsstate.keywords) and
                not self.not_these_elements.intersection(bsstate.elements.keys())
                )

    def __str__(self):
        return self.name

def init_backstory():
    protobits = list()
    myfiles = glob.glob(pbge.util.data_dir( "bs_*.json"))
    for f in myfiles:
        with open(f, 'rb') as fp:
            mylist = json.load(fp)
            if mylist:
                protobits += mylist
    for j in protobits:
        mybit = BackstoryBit(**j)
        ALL_BITS.append(mybit)
        BITS_BY_COMMAND[mybit.command].append(mybit)
