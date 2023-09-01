import pbge
from pbge.dialogue import Offer, ContextTag
from . import ghgrammar, context
from . import context
from . import ghdview
from . import ghreplies
from . import ghoffers
import gears
import random


def trait_absorb(mygram, nugram, traits):
    for pat, gramdic in nugram.items():
        for k, v in gramdic.items():
            if k is ghgrammar.Default:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v
            elif k in traits:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v


def build_grammar(mygram, camp: gears.GearHeadCampaign, speaker, audience):
    speaker = speaker.get_pilot()
    tags = list(speaker.get_tags())
    if speaker.relationship and not speaker.relationship.met_before:
        tags.append(ghgrammar.FIRST_TIME)
    else:
        tags.append(ghgrammar.MET_BEFORE)
    if audience:
        audience = audience.get_pilot()
        react = speaker.get_reaction_score(audience, camp)
        if react > 60:
            tags += [ghgrammar.LIKE, ghgrammar.LOVE]
        elif react > 20:
            tags += [ghgrammar.LIKE, ]
        elif react < -60:
            tags += [ghgrammar.DISLIKE, ghgrammar.HATE]
        elif react < -20:
            tags += [ghgrammar.DISLIKE, ]
        if audience is camp.pc:
            if camp.is_favorable_to_pc(speaker):
                tags.append(ghgrammar.FAVORABLE)
            elif camp.is_unfavorable_to_pc(speaker):
                tags.append(ghgrammar.UNFAVORABLE)

    trait_absorb(mygram, ghgrammar.DEFAULT_GRAMMAR, tags)
    #for p in camp.active_plots():
    #    pgram = p.get_dialogue_grammar(speaker, camp)
    #    if pgram:
    #        mygram.absorb(pgram)
    if speaker.relationship and audience is camp.pc:
        mygram.absorb(speaker.relationship.get_grammar())
    if speaker is camp.pc and audience and audience.relationship:
        mygram.absorb(audience.relationship.get_pc_grammar())

    if hasattr(speaker, "faction") and speaker.faction:
        mygram["[speaker_faction]"] = [str(speaker.faction), ]

    mygram.absorb({"[speaker]": (str(speaker),), "[audience]": (str(audience),)})
    mygram.absorb({"[pc]": (str(camp.pc),)})


def harvest(mod, class_to_collect):
    mylist = []
    for name in dir(mod):
        o = getattr(mod, name)
        if isinstance(o, class_to_collect):
            mylist.append(o)
    return mylist


pbge.dialogue.GRAMMAR_BUILDER = build_grammar
pbge.dialogue.STANDARD_REPLIES = harvest(ghreplies, pbge.dialogue.Reply)
pbge.dialogue.STANDARD_OFFERS = harvest(ghoffers, pbge.dialogue.Offer)
pbge.dialogue.GENERIC_OFFERS.append(ghoffers.GOODBYE)
#pbge.dialogue.GENERIC_OFFERS.append(ghoffers.CHAT)

HELLO_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.HELLO,)))
UNFAVORABLE_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.UNFAVORABLE_HELLO,)))
ATTACK_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.ATTACK,)))


class SkillBasedPartyReply(object):
    def __init__(
            self, myoffer: Offer, camp, mylist, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_EASY,
            no_random=True,
            message_format='{} says "{}"', **kwargs
    ):
        # Check the skill of each party member against a target number. If any party member can
        # make the test, they get to say the line of dialogue.
        # If nobody makes the test, don't add myoffer to mylist.
        self.camp = camp
        self.offer = myoffer
        self.message_format = message_format
        self.skill_id = skill_id
        self.stat_id = stat_id
        self.offer.skill_info = self.get_dialogue_info_text()
        pc = camp.do_skill_test(stat_id, skill_id, rank, no_random=no_random, difficulty=difficulty, **kwargs)
        if pc:
            if pc.get_pilot() is camp.pc:
                mylist.append(myoffer)
            else:
                mylist.append(myoffer)
                myoffer.custom_menu_fun = self.custom_menu_fun
                self.pc = pc.get_pilot()

    def get_dialogue_info_text(self):
        my_statz = list()
        if self.skill_id:
            my_statz.append(str(self.skill_id))
        if self.stat_id:
            my_statz.append(str(self.stat_id))
        if my_statz:
            return " [{}]".format(" + ".join(my_statz))

    def format_text(self, text):
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar, self.camp, self.pc, None)
        if self.offer:
            text = text.format(**self.offer.data)
        text = pbge.dialogue.grammar.convert_tokens(text, mygrammar)
        if self.offer:
            text = text.format(**self.offer.data)
        return text

    def custom_menu_fun(self, reply, mymenu: pbge.rpgmenu.Menu, pcgrammar):
        myitem = ghdview.LancemateConvoItem(
            self.format_text(reply.msg), self.offer, None, mymenu, self.pc, msg_form=self.message_format
        )
        mymenu.items.append(myitem)
        return myitem


class TagBasedPartyReply(SkillBasedPartyReply):
    def __init__(self, myoffer, camp, mylist, needed_tags, message_format='{} says "{}"'):
        # Check the skill of each party member against a target number. If any party member can
        # make the test, they get to say the line of dialogue.
        # If nobody makes the test, don't add myoffer to mylist.
        self.camp = camp
        self.offer = myoffer
        self.message_format = message_format
        self.needed_tags = set(needed_tags)
        winners = [pc for pc in camp.get_active_party() if self.needed_tags.issubset(pc.get_pilot().get_tags())]
        self.pc = None
        if winners:
            pc = random.choice(winners)
            if pc.get_pilot() is camp.pc:
                mylist.append(myoffer)
            else:
                mylist.append(myoffer)
                myoffer.custom_menu_fun = self.custom_menu_fun
                self.pc = pc.get_pilot()
        self.offer.skill_info = self.get_dialogue_info_text()

    def get_dialogue_info_text(self):
        mytags = set(self.needed_tags)
        if self.pc and self.pc.mnpcid and self.pc.mnpcid in mytags:
            mytags.remove(self.pc.mnpcid)

        if mytags:
            return " [{}]".format(", ".join([str(t) for t in mytags]))


class MatchingTagPartyReply(SkillBasedPartyReply):
    def __init__(self, myoffer, camp, mylist, npc, needed_tag, npc_tag=None, message_format='{} says "{}"'):
        # Check the skill of each party member against a target number. If any party member can
        # make the test, they get to say the line of dialogue.
        # If nobody makes the test, don't add myoffer to mylist.
        self.camp = camp
        self.offer = myoffer
        self.message_format = message_format
        self.needed_tag = needed_tag
        self.npc_tag = npc_tag or needed_tag
        self.info_text = self.get_dialogue_info_text()
        self.offer.skill_info = self.get_dialogue_info_text()
        winners = [pc for pc in camp.get_active_party() if needed_tag in pc.get_pilot().get_tags()]
        needed_npc_tag = npc_tag or needed_tag
        if winners and needed_npc_tag in npc.get_pilot().get_tags():
            pc = random.choice(winners)
            if pc.get_pilot() is camp.pc:
                mylist.append(myoffer)
            else:
                mylist.append(myoffer)
                myoffer.custom_menu_fun = self.custom_menu_fun
                self.pc = pc.get_pilot()

    def get_dialogue_info_text(self):
        if self.needed_tag:
            return " [{} + NPC: ]".format(self.needed_tag, self.npc_tag)


class GearHeadConversation(pbge.dialogue.DynaConversation):
    CDATA_TODAYS_RUMORS = "CDATA_TODAYS_RUMORS"
    CDATA_RUMOR_EXPIRATION = "CDATA_RUMOR_EXPIRATION"

    def __init__(self, camp: gears.GearHeadCampaign, *args, **kwargs):
        self.rumors = list()
        self._gathered_rumors = False
        self.chat_limit = 0
        super().__init__(camp, *args, **kwargs)

    def _get_dialogue_data(self):
        if self.pc:
            self.pc = self.pc.get_pilot()
        if self.npc:
            self.npc = self.npc.get_pilot()
        super()._get_dialogue_data()
        if not self._gathered_rumors:
            if self.npc and self.camp.is_not_lancemate(self.npc):
                cdata = self.camp.get_campdata(self.npc)
                all_rumors = self.npc_grammar.get("[News]", ())
                current_rumors = cdata.get(self.CDATA_TODAYS_RUMORS, ())
                rumor_expiration = cdata.get(self.CDATA_RUMOR_EXPIRATION, -1)
                react = self.npc.get_reaction_score(self.pc, self.camp)
                self.chat_limit = max(react//10 + random.randint(-2,2), 1)
                if all_rumors and (rumor_expiration < self.camp.time or not current_rumors):
                    num_rumors = min(max(react//5 + random.randint(0, 5) - random.randint(0, 5), random.randint(1, 5)), len(all_rumors))
                    current_rumors = random.sample(all_rumors, num_rumors)
                    cdata[self.CDATA_TODAYS_RUMORS] = current_rumors
                    cdata[self.CDATA_RUMOR_EXPIRATION] = self.camp.time

                if current_rumors:
                    self.rumors = [r for r in current_rumors if r in all_rumors]
                    random.shuffle(self.rumors)

            self._gathered_rumors = True

        if self.rumors:
            self.npc_offers.append(Offer(
                '[chat_lead_in] {}'.format(self.rumors[0]),
                context=ContextTag([context.CHAT,]), is_generic=True,
                prefx=self._display_first_rumor
            ))
        elif self.chat_limit > 0:
            self.npc_offers.append(Offer(
                '[CHAT]',
                context=ContextTag([context.CHAT,]), is_generic=True,
                prefx=self._random_chat
            ))

    def _display_first_rumor(self, _camp):
        self.rumors.pop(0)

    def _random_chat(self, _camp):
        self.chat_limit -= 1


def start_conversation(camp: gears.GearHeadCampaign, pc, npc, cue=None):
    # If this NPC has no relationship with the PC, create that now.
    realnpc = npc.get_pilot()
    if realnpc and not realnpc.relationship:
        realnpc.relationship = camp.get_relationship(realnpc)
    if not cue:
        npcteam = camp.scene.local_teams.get(npc)
        if npcteam and camp.scene.player_team.is_enemy(npcteam):
            cue = ATTACK_STARTER
        elif camp.is_favorable_to_pc(realnpc):
            cue = HELLO_STARTER
        elif npc not in camp.party and camp.is_unfavorable_to_pc(realnpc):
            cue = UNFAVORABLE_STARTER
        else:
            cue = HELLO_STARTER
    cviz = ghdview.ConvoVisualizer(npc, camp, pc=pc)
    cviz.rollout()
    convo = GearHeadConversation(camp, realnpc, pc, cue, visualizer=cviz)
    convo.converse()
    if realnpc:
        realnpc.relationship.met_before = True


class OneShotInfoBlast(object):
    def __init__(self, subject, message, subject_text=""):
        self.subject = subject
        self.subject_text = subject_text or subject
        self.message = message
        self.active = True

    def build_offer(self):
        return Offer(msg=self.message, context=ContextTag((context.INFO,)), effect=self.blast_that_info,
                     subject=self.subject, data={"subject": self.subject_text}, no_repeats=True)

    def blast_that_info(self, *args):
        self.active = False


class NPCInclusiveOfferEffect(object):
    def __init__(self, npc, effect):
        self.npc = npc
        self.effect = effect

    def __call__(self, camp):
        self.effect(camp, self.npc)
