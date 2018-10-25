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


# Job tags
class Military(Singleton):
    name = "Military"

