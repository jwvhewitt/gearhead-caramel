import random

TAG_MASC = "Masculine"
TAG_FEMME = "Feminine"


class Gender(object):
    def __init__(self, noun="person", adjective="nonbinary", subject_pronoun="ze", object_pronoun="zem",
                 possessive_determiner="zir", absolute_pronoun="zirs", card_pattern="card_*_*.png",
                 tags=(TAG_MASC, TAG_FEMME)):
        self.noun = noun
        self.adjective = adjective
        self.subject_pronoun = subject_pronoun
        self.object_pronoun = object_pronoun
        self.possessive_determiner = possessive_determiner
        self.absolute_pronoun = absolute_pronoun
        self.card_pattern = card_pattern
        self.tags = list(tags)

    @classmethod
    def get_default_female(cls):
        return cls("woman", "female", "she", "her", "her", "hers", "card_f_*.png", (TAG_FEMME,))

    @classmethod
    def get_default_male(cls):
        return cls("man", "male", "he", "him", "his", "his", "card_m_*.png", (TAG_MASC,))

    @classmethod
    def get_default_nonbinary(cls):
        return cls()

    @classmethod
    def random_gender(cls):
        if random.randint(1, 20) == 20:
            # Nonbinary it is.
            return cls()
        elif random.randint(1, 2) == 1:
            return cls.get_default_female()
        else:
            return cls.get_default_male()
