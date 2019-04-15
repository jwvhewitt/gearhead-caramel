
import pbge
import ghgrammar
import context
import ghdview
import ghreplies
import ghoffers
import gears

def trait_absorb(mygram,nugram,traits):
    for pat,gramdic in nugram.iteritems():
        for k,v in gramdic.iteritems():
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

def start_conversation(camp,pc,npc,cue=HELLO_STARTER):
    # If this NPC has no relationship with the PC, create that now.
    realnpc = npc.get_pilot()
    if realnpc and not realnpc.relationship:
        realnpc.relationship = gears.relationships.Relationship()
    cviz = ghdview.ConvoVisualizer(npc,camp,pc=pc)
    cviz.rollout()
    convo = pbge.dialogue.DynaConversation(camp,realnpc,pc,cue,visualizer=cviz)
    convo.converse()

class AutoJoiner(object):
    # A callable to handle lancemate join requests. The NPC will join the party,
    # bringing along any mecha and pets they may have.
    def __init__(self,npc):
        """
        Prepare to add the NPC to the party.
        :type npc: gears.base.Character
        """
        self.npc = npc
    def __call__(self,camp):
        """
        Add the NPC to the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc not in camp.party:
            camp.party.append(self.npc)
            level = max(self.npc.renown,15)
            if hasattr(self.npc,"relationship") and self.npc.relationship:
                level = max(level + self.npc.relationship.data.get("mecha_level_bonus",0),10)
            mek = gears.selector.MechaShoppingList.generate_single_mecha(level,self.npc.faction,gears.tags.GroundEnv)
            if self.npc.mecha_colors:
                mek.colors = self.npc.mecha_colors
            camp.party.append(mek)
            camp.assign_pilot_to_mecha(self.npc,mek)
            for part in mek.get_all_parts():
                part.owner = self.npc


class AutoLeaver(object):
    # A partner for the above- this NPC will leave the party, along with any mecha + pets.
    def __init__(self,npc):
        """
        Prepare to remove the NPC from the party. This object can be used as a dialogue effect.
        :type npc: gears.base.Character
        """
        self.npc = npc
    def __call__(self,camp):
        """
        Remove the NPC from the party, including any mecha or pets.
        :type camp: gears.GearHeadCampaign
        """
        if self.npc in camp.party:
            camp.assign_pilot_to_mecha(self.npc,None)
            camp.party.remove(self.npc)
            for mek in list(camp.party):
                if hasattr(mek,"owner") and mek.owner is self.npc:
                    camp.party.remove(mek)
