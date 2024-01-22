import random

TAG_MASC = "Masculine"
TAG_FEMME = "Feminine"


class Gender(object):
    def __init__(self, noun="person", adjective="nonbinary", subject_pronoun="ze", object_pronoun="zem",
                 possessive_determiner="zir", absolute_pronoun="zirs", reflexive_pronoun="zirself", card_pattern="card_*_*.png",
                 tags=(TAG_MASC, TAG_FEMME)):
        self.noun = noun
        self.adjective = adjective
        self.subject_pronoun = subject_pronoun
        self.object_pronoun = object_pronoun
        self.possessive_determiner = possessive_determiner
        self.absolute_pronoun = absolute_pronoun
        self.reflexive_pronoun = reflexive_pronoun
        self.card_pattern = card_pattern
        self.tags = set(tags)

    DEF_FEMALE_PARAMS = dict(
        noun="woman", adjective="female", subject_pronoun="she", object_pronoun="her",
        possessive_determiner="her", absolute_pronoun="hers", reflexive_pronoun="herself",
        card_pattern="card_f_*.png", tags={TAG_FEMME,}
    )

    DEF_MALE_PARAMS = dict(
        noun="man", adjective="male", subject_pronoun="he", object_pronoun="him",
        possessive_determiner="his", absolute_pronoun="his", reflexive_pronoun="himself",
        card_pattern="card_m_*.png", tags={TAG_MASC,}
    )

    DEF_NONBINARY_PARAMS = dict(
        noun="person", adjective="nonbinary", subject_pronoun="ze", object_pronoun="zem",
        possessive_determiner="zir", absolute_pronoun="zirs", reflexive_pronoun="zirself",
        card_pattern="card_*_*.png", tags={TAG_FEMME, TAG_MASC,}
    )

    @classmethod
    def get_default_female(cls):
        return cls(**cls.DEF_FEMALE_PARAMS)

    @classmethod
    def get_default_male(cls):
        return cls(**cls.DEF_MALE_PARAMS)

    @classmethod
    def get_default_nonbinary(cls):
        return cls(**cls.DEF_NONBINARY_PARAMS)

    @classmethod
    def random_gender(cls):
        if random.randint(1, 20) == 20:
            # Nonbinary it is.
            return cls()
        elif random.randint(1, 2) == 1:
            return cls.get_default_female()
        else:
            return cls.get_default_male()
