import random

# This unit is called "Okapi Puzzle" because the puzzles it generates are not Zebra Puzzles exactly but they are sort
# of related. Puzzle generation and solving are accomplished through brute force algorithms. I've seen examples
# (=cough= RosettaCode =cough=) which use linear algebra or external dependencies to solve puzzles. Well I say, screw
# that. Brute force checking of every solution against every clue is fast enough, doesn't take up a lot of memory on
# modern computers, is more understandable + extensible, and gives me the sensation of hitting math with a hammer.
# Remember that it is harder to debug a program than to write it, so if you write the cleverest code you are capable of
# then you are clearly incapable of troubleshooting that code.

class SusCard():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

brands = ("Paris Baguette", "Rencontre", "Lotte", "Orion", "Nong Shim")
flavors = ("Chocolate", "Mint", "Strawberry", "Tiramisu", "Vanilla")
cakes = ("Roll Cake", "Castella", "Cheesecake", "Layer Cake", "Ice Cream Cake")

class ABTogetherClue():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def matches(self, solution):
        if self.a in solution or self.b in solution:
            return self.a in solution and self.b in solution
        else:
            return True

    def __str__(self):
        return "{} and {} go together".format(self.a, self.b)

class ABNotTogetherClue():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def matches(self, solution):
        return not (self.a in solution and self.b in solution)

    def __str__(self):
        return "{} and {} don't go together".format(self.a, self.b)

class ANotSolutionClue():
    def __init__(self, a):
        self.a = a

    def matches(self, solution):
        return self.a not in solution

    def __str__(self):
        return "{} is disgusting".format(self.a)

class AIsSolutionClue():
    def __init__(self, a):
        self.a = a

    def matches(self, solution):
        return self.a in solution

    def __str__(self):
        return "{} is Joe's favorite".format(self.a)


class Mystery():
    def __init__(self):
        print("What kind of cake does Joe like?")
        self.solution = (random.choice(brands), random.choice(flavors), random.choice(cakes))

        all_clues = self.generate_all_clues()
        all_solutions = self.generate_all_solutions()

        t = 10
        while t > 0 or len(all_clues) > 10:
            i = 1
            while i < len(all_clues) and self.number_of_matches(all_clues[:i], all_solutions) > 1:
                i += 1
            all_clues = all_clues[:i]
            random.shuffle(all_clues)
            if len(all_clues) < 6:
                break
            t -= 1
            if t < -10:
                break

        print(self.solution)
        for l in all_clues[:i]:
            print(l)

    def generate_all_solutions(self):
        mylist = list()
        for brand in brands:
            for flavor in flavors:
                for cake in cakes:
                    mylist.append((brand, flavor, cake))
        return mylist

    def generate_all_clues(self):
        # Generate all possible clues for this puzzle.
        myclues = list()

        myclues.append(ABTogetherClue(self.solution[0], self.solution[1]))
        myclues.append(ABTogetherClue(self.solution[1], self.solution[2]))
        myclues.append(ABTogetherClue(self.solution[0], self.solution[2]))

        for b in brands:
            if b not in self.solution:
                myclues.append(ANotSolutionClue(b))
                for f in flavors:
                    myclues.append(ABNotTogetherClue(b, f))
            else:
                myclues.append(AIsSolutionClue(b))
        for f in flavors:
            if f not in self.solution:
                myclues.append(ANotSolutionClue(f))
                for c in cakes:
                    myclues.append(ABNotTogetherClue(f, c))
            else:
                myclues.append(AIsSolutionClue(f))
        for c in cakes:
            if c not in self.solution:
                myclues.append(ANotSolutionClue(c))
                for b in brands:
                    myclues.append(ABNotTogetherClue(c, b))
            else:
                myclues.append(AIsSolutionClue(c))

        random.shuffle(myclues)
        return myclues

    def clues_match_solution(self, clues, solution):
        return all([c.matches(solution) for c in clues])

    def number_of_matches(self, clues, all_solutions):
        n = 0
        for s in all_solutions:
            if self.clues_match_solution(clues, s):
                n += 1
        return n
