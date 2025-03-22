#!./venv/bin/python3

# Lunar Recipe: dune.txt roman.txt roman_consuls.txt roman_gods.txt roman_misc.txt
# Earth Recipe: battleangel.txt dragonball.txt GundamNames.txt hokuto_male.txt hokuto_female.txt
# Deadzone Recipe: battleangel.txt dune.txt old_earth.txt hokuto_female.txt hokuto_male.txt characters.txt
# Orbitals Recipe: characters.txt GundamNames.txt jojo.txt roman.txt
# Mars Recipe: clanwolf.txt sarna.txt
# Venus Recipe: lotr_aelves.txt egypt1.txt neareast1.txt neareast2.txt oz.txt ulster.txt

import collections
from eng_syl.syllabify import Syllabel
from eng_syl.onceler import Onceler
import random
import json

syllabler = Syllabel()

onc = Onceler()

print(onc.onc_split("charle"))

ALLOWED_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
PROSCRIBED_NAMES = ("and", "the", "of")

class Grap:
    def __init__(self):
        self.next_syllables = collections.defaultdict(int)

    def get_next_candidates(self):
        candidates = list()
        for k,v in self.next_syllables.items():
            candidates += [k,] * v
        return candidates
        
    def gen_next_syllable(self):
        candidates = self.get_next_candidates()
        if candidates:
            return random.choice(candidates)
        else:
            return " "

    def get_dict(self):
        return {
            "next_syllables": self.next_syllables
        }

class Syllable(Grap):
    def __init__(self):
        super().__init__()
        self.nuco_prime = None
        self.nuco_secondary = None
        self.last_letter = None
        self.onset = None

    def record_nuco(self, nuco):
        if not self.nuco_prime:
            self.nuco_prime = nuco
        else:
            self.nuco_secondary = nuco
            
    def get_dict(self):
        return {
            "next_syllables": self.next_syllables,
            "nuco_prime": self.nuco_prime,
            "nuco_secondary": self.nuco_secondary,
            "onset": self.onset
        }

START = " "

class NameTrainer:
    def __init__(self, fname):
        with open(fname) as f:
            raw_names = f.read()

        self.name_set = set()
        self.prep_samples(raw_names.splitlines())
        self.syllables = collections.defaultdict(Syllable)
        # nuco will try to match syllables with the nucleus+coda of
        # preceding syllables.
        self.nuco = collections.defaultdict(Grap)
        self.onsets = collections.defaultdict(Grap)
        self.create_database()

    def prep_samples(self, name_list):
        for rawline in name_list:
            if not rawline.startswith("Category:") and not rawline.startswith("Concept:") and not rawline.startswith("List of "):
                myline = rawline.lower()
                # Get rid of slashes and parenthesis that often appear in wiki article titles
                myline = myline.split("/")[0]
                myline = myline.split("(")[0]

                for name in myline.split():
                    if name not in PROSCRIBED_NAMES:
                        letters = list()
                        for letter in name:
                            if letter in ALLOWED_CHARACTERS:
                                letters.append(letter)
                        if letters:
                            new_name = "".join(letters)
                            self.name_set.add(new_name)
                            #print(new_name)

    def create_database(self):
        for name in list(self.name_set):
            prev_s = START
            raw_s = syllabler.syllabify(name)
            if raw_s:
                for s in raw_s.split("-"):
                    self.syllables[prev_s].next_syllables[s] += 1
                    if prev_s != START:
                        raw_onc = onc.onc_split(prev_s)
                        if raw_onc:
                            my_parts = [p for p in raw_onc.split("-") if p]
                            if not self.syllables[prev_s].onset:
                                self.syllables[prev_s].onset = my_parts[0]
                            self.onsets[my_parts[0]].next_syllables[prev_s] += 1
                            if len(my_parts) > 1:
                                nuco = "".join(my_parts[1:])
                                self.syllables[prev_s].record_nuco(nuco)
                                self.nuco[nuco].next_syllables[s] += 1
                                if len(my_parts) > 2:
                                    nuco = my_parts[-1]
                                    self.syllables[prev_s].record_nuco(nuco)
                                    self.nuco[nuco].next_syllables[s] += 1
                        if len(prev_s) > 1:
                            if not self.syllables[prev_s].last_letter:
                                self.syllables[prev_s].last_letter = prev_s[-1]
                            self.nuco[prev_s[-1]].next_syllables[s] += 1
                    prev_s = s
                self.syllables[prev_s].next_syllables[START] += 5

    def gen_syllable(self, prev_syllable):
        candidates = self.syllables[prev_syllable].get_next_candidates()
        onset_candidates = list()
        for can in candidates:
            if self.syllables[can].onset:
                onset_candidates += self.onsets[self.syllables[can].onset].get_next_candidates()
        candidates = candidates * 10 + onset_candidates
        if self.syllables[prev_syllable].nuco_prime:
            candidates += self.nuco[self.syllables[prev_syllable].nuco_prime].get_next_candidates() * 7
        if self.syllables[prev_syllable].nuco_secondary:
            candidates += self.nuco[self.syllables[prev_syllable].nuco_secondary].get_next_candidates() * 5
        if self.syllables[prev_syllable].last_letter:
            candidates += self.nuco[self.syllables[prev_syllable].last_letter].get_next_candidates() * 2
        if candidates:
            return random.choice(candidates)
        else:
            return "X"

    def gen_word(self):
        my_name = ""
        prev_syllable = " "
        while len(my_name) < 6:
            new_syllable = self.gen_syllable(prev_syllable)
            my_name = my_name + new_syllable
            prev_syllable = new_syllable
        return my_name

    def get_dict(self):
        mydict = {"min_length": min([len(a) for a in self.name_set]), "max_length": max([len(a) for a in self.name_set]), "syllables": dict(), "nuco": dict(), "onsets": dict()}
        for k,v in self.syllables.items():
            mydict["syllables"][k] = v.get_dict()
        for k,v in self.nuco.items():
            mydict["nuco"][k] = v.get_dict()
        for k,v in self.onsets.items():
            mydict["onsets"][k] = v.get_dict()

        return mydict

    def save(self, fname):
        mydict = self.get_dict()
        with open("{}.json".format(fname), "w") as f:
            json.dump(mydict, f, indent=4)

    def test_generator(self):
        duplicates = 0
        clones = 0
        generated_names = set()
        for t in range(10000):
            myname = self.gen_word()
            if myname in generated_names:
                duplicates += 1
            if myname in self.name_set:
                clones += 1
            generated_names.add(myname)
        print("Unique Names: {}".format(len(generated_names)))
        print("Clones: {}".format(clones))
        print("Duplicates: {}".format(duplicates))
                


#mnt = NameTrainer("t_gztowns.txt")
#for t in range(100):
#    print(mnt.gen_word())
#mnt.save("ng_gztowns")

#mnt.test_generator()
