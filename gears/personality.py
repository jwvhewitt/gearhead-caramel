from pbge import Singleton
import stats
import color
import random

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


# Mutation Tags- Important for the portrait generator.

class Idealist(Singleton):
    name = "Idealist"

class FelineMutation(Singleton):
    name = "Feline Mutation"
    @staticmethod
    def apply(pc,stats_to_mod=None):
        sl = stats_to_mod or pc.statline
        sl[stats.Speed] += 2
        sl[stats.Body] -= 2
        if pc.portrait_gen and random.randint(1,3) == 1:
            pc.portrait_gen.color_channels[1] = color.HAIR

class DraconicMutation(Singleton):
    name = "Draconic Mutation"
    @staticmethod
    def apply(pc,stats_to_mod=None):
        sl = stats_to_mod or pc.statline
        sl[stats.Charm] -= 2
        sl[stats.Body] += 2
        if pc.portrait_gen:
            pc.portrait_gen.color_channels[1] = color.MECHA
            pc.portrait_gen.color_channels[2] = color.METAL

class GeneralMutation(Singleton):
    name = "Mutation"
    @staticmethod
    def apply(pc,stats_to_mod=None):
        sl = stats_to_mod or pc.statline
        s1,s2 = random.sample(stats.PRIMARY_STATS,2)
        sl[s1] -= 2
        sl[s2] += 2
        if pc.portrait_gen:
            pc.portrait_gen.color_channels[1] = color.DETAILS
            pc.portrait_gen.color_channels[2] = color.DETAILS

MUTATIONS = (FelineMutation,DraconicMutation,GeneralMutation)