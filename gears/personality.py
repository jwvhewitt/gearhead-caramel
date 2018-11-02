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

TRAITS = ((Cheerful,Cheerful,Grim),(Easygoing,Easygoing,Passionate),(Sociable,Sociable,Shy))
OPPOSED_PAIRS = ((Cheerful,Grim),(Easygoing,Passionate),(Sociable,Shy))

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

ORIGINS = (GreenZone,DeadZone,L5Spinners,L5DustyRing,Luna,Mars)
