import json
import random

class Grap:
    # I was going to name this class Grapheme, but it's not necessarily
    # a grapheme, so I just named it Grap.
    def __init__(self, next_syllables):
        self.next_syllables = next_syllables

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


class Syllable(Grap):
    def __init__(self, next_syllables, nuco_prime, nuco_secondary, onset):
        super().__init__(next_syllables)
        self.nuco_prime = nuco_prime
        self.nuco_secondary = nuco_secondary
        self.onset = onset


class NameGen:
    def __init__(self, fname, forbidden_names=None):
        # forbidden_names is a set of names that should be rejected if
        # generated. It's passed as a param so multiple name generators
        # can share the same list.
        with open(fname) as f:
            my_dict = json.load(f)
            
        self.syllables = dict()
        self.nuco = dict()
        self.onsets = dict()
        
        self.min_length = max(min(my_dict.get("min_length", 4), 6), 3)
        self.max_length = max(min(my_dict.get("max_length", 8), 12), 8)

        for k,v in my_dict["syllables"].items():
            self.syllables[k] = Syllable(**v)
        
        for k,v in my_dict["nuco"].items():
            self.nuco[k] = Grap(**v)

        for k,v in my_dict["onsets"].items():
            self.onsets[k] = Grap(**v)

        if forbidden_names:
            self.forbidden_names = forbidden_names
        else:
            self.forbidden_names = set()

    def gen_syllable(self, prev_syllable=" "):
        if prev_syllable in self.syllables:
            candidates = self.syllables[prev_syllable].get_next_candidates()
            onset_candidates = list()
            for can in candidates:
                if can in self.syllables and self.syllables[can].onset and self.syllables[can].onset in self.onsets:
                    #print(self.syllables[can].onset)
                    onset_candidates += self.onsets[self.syllables[can].onset].get_next_candidates()
            candidates = candidates * 5 + onset_candidates
            if self.syllables[prev_syllable].nuco_prime and self.syllables[prev_syllable].nuco_prime in self.nuco:
                candidates += self.nuco[self.syllables[prev_syllable].nuco_prime].get_next_candidates() * 4
            if self.syllables[prev_syllable].nuco_secondary and self.syllables[prev_syllable].nuco_secondary in self.nuco:
                candidates += self.nuco[self.syllables[prev_syllable].nuco_secondary].get_next_candidates() * 3
            if prev_syllable[-1] in self.nuco:
                candidates += self.nuco[prev_syllable[-1]].get_next_candidates()
        else:
            candidates = ['0']
        if candidates:
            return random.choice(candidates)
        else:
            return "9"

    def _gen_word_(self, length=0):
        proto_name = ""
        prev_syllable = " "
        if length < 3:
            length = (random.randint(3,8) + random.randint(3,8))//2
            if random.randint(1,23) == 5:
                length += random.randint(1,6)
            if random.randint(1,10) == 1:
                length -= 1
        increased_length = False
        while len(proto_name) < length:
            new_syllable = self.gen_syllable(prev_syllable)
            if new_syllable == " " and len(proto_name) < random.randint(2,3) and random.randint(1,23) != 5:
                new_syllable = self.gen_syllable(prev_syllable)
            if new_syllable == " " and not increased_length:
                length += random.randint(2,3)
                increased_length = True
            proto_name = proto_name + new_syllable
            prev_syllable = new_syllable
        proto_name = proto_name.strip()
        
        verified_letters = list()
        needs_capitalization = True
        prev_char = ""
        repeat_count = 0
        for char in proto_name:
            if char == prev_char:
                repeat_count += 1
                if char == " " or repeat_count > 1:
                    continue
            else:
                prev_char = char
                repeat_count = 0
            if needs_capitalization:
                char = char.upper()
                needs_capitalization = False
            if char == " ":
                needs_capitalization = True
            verified_letters.append(char)
        return "".join(verified_letters)

    def gen_word(self, length=0):
        myword = ""
        while not myword:
            myword = self._gen_word_(length)
            if myword in self.forbidden_names:
                myword = ""
        self.forbidden_names.add(myword)
        return myword

    def test_generator(self):
        dupes = 0
        for t in range(10):
            for _ in range(1000):
                myname = self._gen_word_()
                if myname in self.forbidden_names:
                    dupes += 1
                self.forbidden_names.add(myname)
            print((t+1)*1000)
        print("{}/10000 names duplicated".format(dupes))
        
