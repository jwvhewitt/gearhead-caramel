
import pbge
from pbge.dialogue import Offer, ContextTag
from . import ghgrammar, context
from . import context
from . import ghdview
from . import ghreplies
from . import ghoffers
import gears
import random

def trait_absorb(mygram,nugram,traits):
    for pat,gramdic in nugram.items():
        for k,v in gramdic.items():
            if k is ghgrammar.Default:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v
            elif k in traits:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v


def build_grammar( mygram, camp, speaker, audience ):
    speaker = speaker.get_pilot()
    tags = speaker.get_tags()
    if speaker.relationship and not speaker.relationship.met_before:
        tags.append(ghgrammar.FIRST_TIME)
    else:
        tags.append(ghgrammar.MET_BEFORE)
    if audience:
        audience = audience.get_pilot()
        react = speaker.get_reaction_score(audience,camp)
        if react > 60:
            tags += [ghgrammar.LIKE,ghgrammar.LOVE]
        elif react > 20:
            tags += [ghgrammar.LIKE,]
        elif react < -60:
            tags += [ghgrammar.DISLIKE,ghgrammar.HATE]
        elif react < -20:
            tags += [ghgrammar.DISLIKE,]
    trait_absorb(mygram,ghgrammar.DEFAULT_GRAMMAR,tags)
    for p in camp.active_plots():
        pgram = p.get_dialogue_grammar( speaker, camp )
        if pgram:
            mygram.absorb( pgram )

    mygram.absorb({"[speaker]":(str(speaker),),"[audience]":(str(audience),)})

def harvest( mod, class_to_collect ):
    mylist = []
    for name in dir( mod ):
        o = getattr( mod, name )
        if isinstance( o , class_to_collect ):
            mylist.append( o )
    return mylist

pbge.dialogue.GRAMMAR_BUILDER = build_grammar
pbge.dialogue.STANDARD_REPLIES = harvest(ghreplies,pbge.dialogue.Reply)
pbge.dialogue.STANDARD_OFFERS = harvest(ghoffers,pbge.dialogue.Offer)
pbge.dialogue.GENERIC_OFFERS.append(ghoffers.GOODBYE)
pbge.dialogue.GENERIC_OFFERS.append(ghoffers.CHAT)

HELLO_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.HELLO,)))
ATTACK_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.ATTACK,)))

class SkillBasedPartyReply(object):
    def __init__(
            self,myoffer,camp,mylist,stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_EASY, no_random=True,
            message_format = '{} says {}',**kwargs
    ):
        # Check the skill of each party member against a target number. If any party member can
        # make the test, they get to say the line of dialogue.
        # If nobody makes the test, don't add myoffer to mylist.
        self.camp = camp
        self.offer = myoffer
        self.message_format = message_format
        pc = camp.make_skill_roll(stat_id,skill_id,rank,no_random=no_random,difficulty=difficulty,**kwargs)
        if pc:
            if pc.get_pilot() is camp.pc:
                mylist.append(myoffer)
            else:
                mylist.append(myoffer)
                myoffer.custom_menu_fun = self.custom_menu_fun
                self.pc = pc

    def format_text( self, text ):
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,self.camp,self.pc,None)
        if self.offer:
            text = text.format(**self.offer.data)
        text = pbge.dialogue.grammar.convert_tokens( text, mygrammar )
        if self.offer:
            text = text.format(**self.offer.data)
        return text

    def custom_menu_fun(self,reply,mymenu,pcgrammar):
        mymenu.items.append(ghdview.LancemateConvoItem(
            self.format_text(reply.msg),self.offer,None,mymenu,self.pc,msg_form=self.message_format
        ))


class TagBasedPartyReply(SkillBasedPartyReply):
    def __init__(self,myoffer,camp,mylist,needed_tags):
        # Check the skill of each party member against a target number. If any party member can
        # make the test, they get to say the line of dialogue.
        # If nobody makes the test, don't add myoffer to mylist.
        self.camp = camp
        self.offer = myoffer
        needed_tags = set(needed_tags)
        winners = [pc for pc in camp.get_active_party() if needed_tags.issubset( pc.get_pilot().get_tags())]
        if winners:
            pc = random.choice(winners)
            if pc.get_pilot() is camp.pc:
                mylist.append(myoffer)
            else:
                mylist.append(myoffer)
                myoffer.custom_menu_fun = self.custom_menu_fun
                self.pc = pc


def start_conversation(camp,pc,npc,cue=HELLO_STARTER):
    # If this NPC has no relationship with the PC, create that now.
    realnpc = npc.get_pilot()
    if realnpc and not realnpc.relationship:
        realnpc.relationship = camp.get_relationship(realnpc)
    cviz = ghdview.ConvoVisualizer(npc,camp,pc=pc)
    cviz.rollout()
    convo = pbge.dialogue.DynaConversation(camp,realnpc,pc,cue,visualizer=cviz)
    convo.converse()
    if realnpc:
        realnpc.relationship.met_before = True


class OneShotInfoBlast(object):
    def __init__(self, subject, message):
        self.subject = subject
        self.message = message
        self.active = True

    def build_offer(self):
        return Offer(msg=self.message, context=ContextTag((context.INFO,)), effect=self.blast_that_info,
                     subject=self.subject, data={"subject": self.subject}, no_repeats=True)

    def blast_that_info(self, *args):
        self.active = False