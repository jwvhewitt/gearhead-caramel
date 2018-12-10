from pbge import Singleton


# Environments

class GroundEnv(Singleton):
    name = "Ground"


class UrbanEnv(Singleton):
    name = "Urban"


class SpaceEnv(Singleton):
    name = "Space"


class AquaticEnv(Singleton):
    name = "Aquatic"


# Battlefield Roles

class Trooper(Singleton):
    name = "Trooper"


class Commander(Singleton):
    name = "Commander"


class Support(Singleton):
    name = "Support"


# Job tags
class Academic(Singleton):
    name = "Academic"


class Adventurer(Singleton):
    name = "Adventurer"


class Craftsperson(Singleton):
    name = "Craftsperson"


class Criminal(Singleton):
    name = "Criminal"

class Media(Singleton):
    name = "Media"

class Military(Singleton):
    name = "Military"

class Police(Singleton):
    name = "Police"

class Politician(Singleton):
    name = "Politician"

# Scene Tags
class Village(Singleton):
    name = "Village"