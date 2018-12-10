import pbge
import gears
from gears import personality,tags,stats
from gears.meritbadges import TagReactionBadge
import pygame
from .. import ghdialogue
from ..ghdialogue.ghgrammar import Default

BADGE_ACADEMIC = TagReactionBadge("Academic","You are familiar with the language and culture of academia.",remods={tags.Academic:10})
BADGE_CRIMINAL = TagReactionBadge("Criminal","",remods={tags.Police:-10,tags.Criminal:10})
BADGE_GEARHEAD = TagReactionBadge("Gearhead","You are obsessed with mecha and anything having to do with mecha.",remods={tags.Craftsperson:10})
BADGE_POPSTAR = TagReactionBadge("Pop Star","You released a few songs and attained some notoriety as a pop star.",remods={tags.Media:10})
BADGE_SOLDIER = TagReactionBadge("Soldier","Your time in the army taught you camraderie with all who serve.",remods={tags.Military:10})

# Character generation is lifepath based.

class LifePathOption(object):
    def __init__(self,name,desc,personality_tags=(),stat_mods=None,badges=(),biomessage="",biogram=None):
        self.name = name
        self.desc = desc
        self.personality_tags = list(personality_tags)
        self.stat_mods = dict()
        if stat_mods:
            self.stat_mods.update(stat_mods)
        self.badges = list(badges)
        self.biomessage = biomessage
        self.biogram = dict()
        if biogram:
            self.biogram.update(biogram)
    def apply(self,cgen):
        ghdialogue.trait_absorb(cgen.biogram,self.biogram,cgen.pc.get_tags())
        if self.biomessage:
            cgen.pc.bio += pbge.dialogue.grammar.convert_tokens(self.biomessage,cgen.biogram,allow_maybe=False)

class LPIdealistBonus(object):
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc

class LPRandomMutation(object):
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc


CHOOSE_PEACE = LifePathOption("Peace", "You vow to protect the weak, and prevent tragedies like those you've witnessed from happening again.", personality_tags = (personality.Peace,))
CHOOSE_GLORY = LifePathOption("Glory", "", personality_tags = (personality.Glory,))
CHOOSE_JUSTICE = LifePathOption("Justice", "", personality_tags = (personality.Justice,))
CHOOSE_FELLOWSHIP = LifePathOption("Fellowship", "", personality_tags=(personality.Fellowship,))
CHOOSE_DUTY = LifePathOption("Duty", "", personality_tags = (personality.Duty,))

class LifePathChoice(object):
    def __init__(self,prompt,options=()):
        self.prompt = prompt
        self.options = options

class LifePathNode(object):
    def __init__(self,name,desc,choices=(),next=(),next_prompt='',auto_fx=None):
        self.name = name
        self.desc = desc
        self.choices = choices
        self.next = next
        self.next_prompt = next_prompt
        self.auto_fx = auto_fx

FAIL_POPSTAR = LifePathOption("My music career went nowhere.","Performance skill, Pop Star merit badge.",
                              stat_mods={stats.Performance:1},badges=(BADGE_POPSTAR,))
FAIL_FRIENDDIED = LifePathOption("My friend died and I couldn't save them.","Medicine skill, Grim trait",
                                 stat_mods={stats.Medicine:1},personality_tags=(personality.Grim,))

D_FAILURE = LifePathNode(
    "Failure","You failed at an important task, and now bear the responsibility for the consequences.",
    choices=(
        LifePathChoice("What sort of failure did you experience?",(FAIL_POPSTAR,FAIL_FRIENDDIED)),
        LifePathChoice("How do you choose to deal with this failure?",(CHOOSE_PEACE,CHOOSE_JUSTICE,CHOOSE_DUTY)),
    )
)

BETR_MENTOR = LifePathOption("My mentor. I never saw it coming.","Scouting skill",
                             stat_mods={stats.Scouting:1})

BETR_LABMATE = LifePathOption("My high school lab partner. No idea why.","Science skill",
                             stat_mods={stats.Science:1})

D_BETRAYAL = LifePathNode(
    "Betrayal","You were betrayed by someone close to you.",
    choices=(
        LifePathChoice("Who betrayed you?",(BETR_MENTOR,BETR_LABMATE)),
        LifePathChoice("How do you choose to deal with this betrayal?",(CHOOSE_PEACE,CHOOSE_JUSTICE,CHOOSE_FELLOWSHIP)),
    )
)

DEST_MECHALOVE = LifePathOption("I was born to pilot mecha.","Repair skill, Gearhead badge",
                                stat_mods={stats.Repair:1},badges=(BADGE_GEARHEAD,))
DEST_GOLDENTONGUE = LifePathOption("I am both a problem solver and a troublemaker.","Negotiation skill",
                                   stat_mods={stats.Negotiation:1})

D_DESTINY = LifePathNode(
    "Destiny","",
    choices=(
        LifePathChoice("What is your great destiny?",(DEST_MECHALOVE,DEST_GOLDENTONGUE)),
        LifePathChoice("How do you choose to deal with this destiny?",(CHOOSE_GLORY,CHOOSE_JUSTICE,CHOOSE_FELLOWSHIP)),
    )
)

POVE_CRIME = LifePathOption("I stole what I needed to survive.","Stealth skill, Criminal badge",
                            stat_mods={stats.Stealth:1},badges=(BADGE_CRIMINAL,))
POVE_SURVIVALIST = LifePathOption("I lived off the land, aided by my animal companions.","Dominate Animal skill",
                                  stat_mods={stats.DominateAnimal:1})

D_POVERTY = LifePathNode(
    "Poverty","You lost whatever money you may once have had, and are now in dire straits.",
    choices=(
        LifePathChoice("How did you survive during this time?",(POVE_CRIME,POVE_SURVIVALIST)),
        LifePathChoice("How do you choose to deal with your poverty?",(CHOOSE_GLORY,CHOOSE_DUTY,CHOOSE_FELLOWSHIP)),
    )
)

WAR_SPECIALIST = LifePathOption("I fought, using my talents as an EW specialist.","Computers skill",
                                stat_mods={stats.Computers:1})
WAR_BIOTECH = LifePathOption("I sought info about PreZero bioweapons to aid my side.","Biotechnology skill",
                             stat_mods={stats.Biotechnology:1})

D_WAR = LifePathNode(
    "War","",
    choices=(
        LifePathChoice("What did you do during the war?",(WAR_SPECIALIST,WAR_BIOTECH)),
        LifePathChoice("How do you choose to deal with this conflict?",(CHOOSE_GLORY,CHOOSE_DUTY,CHOOSE_PEACE)),
    )
)

SURV_PET = LifePathOption("I had a dog who kept me safe.","Dominate Animal skill",
                          stat_mods={stats.DominateAnimal:1})
SURV_TALK = LifePathOption("I learned to talk my way out of bad situations.","Negotiation skill",
                           stat_mods={stats.Negotiation:1})

C_SURVIVAL = LifePathNode(
    "Survival","Life was tough. All you could do was to survive, and then just barely.",
    choices=(
        LifePathChoice("What allowed you to get through this period?",(SURV_PET,SURV_TALK)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_WAR,D_FAILURE,D_BETRAYAL),
    auto_fx = LifePathOption("Survival Bonus","Vitality + 2",
                             stat_mods={stats.Vitality:2})
)

HAKN_THIEF = LifePathOption("I was a shoplifter.","Stealth skill",
                            stat_mods={stats.Stealth:1})
HAKN_HACKER = LifePathOption("I was a computer hacker.","Computers skill",
                             stat_mods={stats.Computers:1})

C_HARDKNOCKS = LifePathNode(
    "Hard Knocks","As a youth, you got mixed up in some dangerous times.",
    choices=(
        LifePathChoice("What sort of criminal activity were you involved in?",(HAKN_HACKER,HAKN_THIEF)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_FAILURE,D_BETRAYAL,D_DESTINY),
    auto_fx=LifePathOption("Hard Knocks Bonus", "Athletics + 2",
                           stat_mods={stats.Athletics: 2}, badges=(BADGE_CRIMINAL,))
)

AUTO_SCIENCE = LifePathOption("Science, especially the lost art of biotech.","Biotechnology skill",
                                stat_mods={stats.Biotechnology:1})
AUTO_ART = LifePathOption("Art, especially music.","Performance skill",
                          stat_mods={stats.Performance:1})

C_AUTODIDACT = LifePathNode(
    "Autodidact","You taught yourself everything you know, and were a very good teacher.",
    choices=(
        LifePathChoice("What subject captivated your interest?",(AUTO_ART,AUTO_SCIENCE)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_BETRAYAL,D_DESTINY,D_POVERTY),
    auto_fx=LifePathOption("Autodidact Bonus", "Concentration + 2",
                           stat_mods={stats.Concentration: 2})
)

UNI1_SCIENCE = LifePathOption("Science.","Science skill",
                              stat_mods={stats.Science:1})
UNI1_MEDICINE = LifePathOption("Medicine.","Medicine skill",
                              stat_mods={stats.Medicine:1})

UNI2_ENGINEERING = LifePathOption("Engineering.","Repair skill",
                                  stat_mods={stats.Repair:1})
UNI2_COMPSCI = LifePathOption("Computer Science.","Computers skill",
                                  stat_mods={stats.Computers:1})
UNI2_MUSIC = LifePathOption("Music.","Performance skill",
                                  stat_mods={stats.Performance:1})
UNI2_POLYSCI = LifePathOption("Management.","Negotiation skill",
                                  stat_mods={stats.Negotiation:1})
UNI2_PHYSED = LifePathOption("Physical Education.","Athletics skill bonus",
                                  stat_mods={stats.Athletics:1})

C_UNIVERSITY = LifePathNode(
    "University","You studied at a prestigious university.",
    choices=(
        LifePathChoice("What was your major in university?",(UNI1_SCIENCE,UNI1_MEDICINE)),
        LifePathChoice("What was your minor in university?", (UNI2_COMPSCI,UNI2_ENGINEERING,UNI2_MUSIC,UNI2_PHYSED,UNI2_POLYSCI)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_DESTINY,D_POVERTY,D_WAR),
    auto_fx=LifePathOption("University Bonus", "Academics badge",
                           badges=(BADGE_ACADEMIC,),
                           )
)

MILI_SCOUT = LifePathOption("I was a scout pilot.","Scouting skill",
                            stat_mods={stats.Scouting:1})
MILI_TECH = LifePathOption("I was a field tech.","Repair skill",
                            stat_mods={stats.Repair:1})
MILI_GRUNT = LifePathOption("I was just a grunt.","Mecha Gunnery bonus",
                            stat_mods={stats.MechaGunnery:1})


C_MILITIA = LifePathNode(
    "Militia","You joined the military and learned how to fight.",
    choices=(
        LifePathChoice("What was your position in the army?",(MILI_SCOUT,MILI_TECH,MILI_GRUNT)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_POVERTY,D_WAR,D_FAILURE),
    auto_fx=LifePathOption("Militia Bonus", "Soldier badge",
                           badges=(BADGE_SOLDIER,),
                           )
)

ORPH_LONER = LifePathOption("I became a loner, and still don't get close to people.","Shy trait",
                                 personality_tags=(personality.Shy,))

ORPH_SOCIABLE = LifePathOption("I took comfort in my friends and caretakers.","Sociable trait",
                                 personality_tags=(personality.Shy,))

B_ORPHAN = LifePathNode(
    "Orphan","You lost your parents at a young age.",
    choices=(
        LifePathChoice("How did you cope with the loss of your parents?",(ORPH_LONER,ORPH_SOCIABLE)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_MILITIA,C_SURVIVAL,C_HARDKNOCKS),
    auto_fx=LifePathOption("Orphan Bonus", "+1 Ego, +1 Speed",
                           stat_mods={stats.Ego:1,stats.Speed:1},
                           )
)

OUTC_MUTANT = LPRandomMutation("I have visible genetic mutations.", "Mutant trait",
                             )

OUTC_CRIMINAL = LifePathOption("I got started in crime at a young age.", "Criminal badge",
                             badges=(BADGE_CRIMINAL,))

B_OUTCAST = LifePathNode(
    "Outcast","You have always lived on the fringes of society.",
    choices=(
        LifePathChoice("What is it that set you apart from your peers?",(OUTC_CRIMINAL,OUTC_MUTANT)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_SURVIVAL,C_HARDKNOCKS,C_AUTODIDACT),
    auto_fx=LifePathOption("Outcast Bonus", "+1 Reflexes, +1 Craft",
                           stat_mods={stats.Reflexes:1,stats.Craft:1},
                           )
)

IDEA_EASY = LifePathOption("My natural talents made me lazy at school.","Easygoing trait",
                                 personality_tags=(personality.Easygoing,))

IDEA_HARD = LifePathOption("I was very competitive; Every subject was a challenge to be mastered.","Passionate trait",
                                 personality_tags=(personality.Passionate,))

B_IDEALIST = LifePathNode(
    "Idealist","Your heritage includes a significant amount of genetic engineering.",
    choices=(
        LifePathChoice("How did you perform in school?",(IDEA_EASY,IDEA_HARD)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_HARDKNOCKS,C_AUTODIDACT,C_UNIVERSITY),
    auto_fx=LPIdealistBonus("Idealist Bonus", "+1 to three random stats",
                           )
)

CITY_PROSPEROUS = LifePathOption("I lived on the good side of town.","Cheerful trait",
                                 personality_tags=(personality.Cheerful,))

CITY_SLUMS = LifePathOption("I lived in the slums.", "Grim trait",
                 personality_tags=(personality.Grim,))

B_CITY = LifePathNode(
    "City","You were born in a city and led an average life there.",
    choices=(
        LifePathChoice("What part of the city were you raised in?",(CITY_PROSPEROUS,CITY_SLUMS)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_AUTODIDACT,C_UNIVERSITY,C_MILITIA),
    auto_fx=LifePathOption("City Bonus", "+1 Knowledge, +1 Charm",
                           stat_mods={stats.Knowledge:1,stats.Charm:1},
                           )
)

FRON_WARZONE = LifePathOption("Our village was always under attack by bandits or raiders.","Grim trait",
                                 personality_tags=(personality.Grim,))

FRON_BORING = LifePathOption("Mostly it was boring; I longed to escape.","Passionate trait",
                                 personality_tags=(personality.Passionate,))

FRON_COMMUNITY = LifePathOption("Life was hard, but everyone helped everyone else out.","Sociable trait",
                                 personality_tags=(personality.Sociable,))

B_FRONTIER = LifePathNode(
    "Frontier","You were born in a small town on the edge of civilization.",
    choices=(
        LifePathChoice("How was growing up in your frontier town?",(FRON_BORING,FRON_COMMUNITY,FRON_WARZONE)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_UNIVERSITY,C_MILITIA,C_SURVIVAL),
    auto_fx=LifePathOption("Frontier Bonus", "+1 Body, +1 Perception",
                           stat_mods={stats.Body:1,stats.Perception:1},
                           )
)

EART_GREENZONE = LifePathOption("The Terran Federation green zone.","GreenZone origin",
                                 personality_tags=(personality.GreenZone,))

EART_DEADZONE = LifePathOption("A fortress in the dead zone.","DeadZone origin",
                                 personality_tags=(personality.DeadZone,))

A_EARTH = LifePathNode(
    "Earth","You are from Earth.",
    choices=(
        LifePathChoice("Which part of Earth are you from?",(EART_DEADZONE,EART_GREENZONE)),
    ),
    next_prompt="How was your early life?",
    next=(B_CITY,B_FRONTIER,B_IDEALIST,B_ORPHAN,B_OUTCAST),
)

STARTING_CHOICES = (A_EARTH,)

class BioBlock( object ):
    def __init__(self,model,width=220,**kwargs):
        self.model = model
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT,model.bio,width,justify=0)
        self.height = self.image.get_height()
    def render(self,x,y):
        pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))


class LifePathStatusPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.NameBlock,BioBlock)
