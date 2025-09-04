from pbge import Singleton


class Cheerful(Singleton):
    name = 'Cheerful'

class Grim(Singleton):
    name = 'Grim'

class Easygoing(Singleton):
    name = 'Easygoing'

class Passionate(Singleton):
    name = 'Passionate'

class Sociable(Singleton):
    name = 'Sociable'

class Shy(Singleton):
    name = 'Shy'


class Glory(Singleton):
    name = 'Glory'


class Peace(Singleton):
    name = 'Peace'


class Justice(Singleton):
    name = 'Justice'


class Duty(Singleton):
    name = 'Duty'


class Fellowship(Singleton):
    name = 'Fellowship'


VIRTUES = (Glory,Peace,Justice,Duty,Fellowship)


class Failure(Singleton):
    name = 'Failure'
    opposite = Glory


class Violent(Singleton):
    name = 'Violent'
    opposite = Peace


class Corrupt(Singleton):
    name = 'Corrupt'
    opposite = Justice


class Irresponsible(Singleton):
    name = 'Irresponsible'
    opposite = Duty


class Heartless(Singleton):
    name = 'Heartless'
    opposite = Fellowship


FAULTS = (Failure, Violent, Corrupt, Irresponsible, Heartless)


TRAITS = ((Cheerful,Cheerful,Grim),(Easygoing,Easygoing,Passionate),(Sociable,Sociable,Shy))
OPPOSED_PAIRS = (
    (Cheerful,Grim),(Easygoing,Passionate),(Sociable,Shy),
    (Peace, Violent), (Failure, Glory), (Corrupt, Justice), (Duty, Irresponsible), (Fellowship, Heartless)
)

OPPOSITES = {
    Sociable: Shy, Shy: Sociable,
    Easygoing: Passionate, Passionate: Easygoing,
    Cheerful: Grim, Grim: Cheerful
}

# Origin Tags- Use one of these to mark the home/culture of a character.

class GreenZone(Singleton):
    name = "Green Zone"


class DeadZone(Singleton):
    name = "Dead Zone"


class L5Spinners(Singleton):
    name = "L5 Spinners"


class L5DustyRing(Singleton):
    name = "L5 Dusty Ring"


class Luna(Singleton):
    name = "Luna"


class Mars(Singleton):
    name = "Mars"


class Venus(Singleton):
    name = "Venus"


ORIGINS = (GreenZone, DeadZone, L5Spinners, L5DustyRing, Luna, Mars, Venus)


# Mutation Tags- Important for the portrait generator.

class Idealist(Singleton):
    name = "Idealist"

