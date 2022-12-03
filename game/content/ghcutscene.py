import collections

from pbge import cutscene
from .. import ghdialogue
import random
import pbge
import gears


class CutsceneState:
    def __init__(self, elements=None, prev_node=None, tags=(), ordered_beats=(), unordered_beats=(), info_blocks=()):
        self.elements = dict()
        if elements:
            self.elements.update(elements)
        self.prev_node = prev_node
        self.tags = set(tags)
        self.ordered_beats = list(ordered_beats)
        self.unordered_beats = list(unordered_beats)
        self.info_blocks = list(info_blocks)


class CutscenePlan:
    def __init__(self, topic, elements=None, ordered_beats=(), unordered_beats=(), info_blocks=()):
        # topic is a string describing the overall function of this cutscene
        # elements is a list of named things that might get used by Presentation Nodes or to format text.
        # ordered_beats is a list of beats that must be included in the cutscene; they must appear in the order given
        # unordered_beats must also appear in the cutscene; these can appear in any order
        # info_blocks is a list of InfoBlock objects from which the cutscene will be created.
        self.topic = topic
        self.elements = dict()
        if elements:
            self.elements.update(elements)
        self.ordered_beats = list(ordered_beats)
        self.unordered_ordered = list(unordered_beats)
        self.info_blocks = list(info_blocks)

    def build(self, camp: gears.GearHeadCampaign):
        pass

    def play(self, camp: gears.GearHeadCampaign):
        self.build(camp)
        pass


class InfoBlock(dict):
    # Contains info that may need to be expressed during the cutscene.
    def __init__(self, beat=None, requirements=(), tags=(), **kwargs):
        # beat is an optional string describing this InfoBlock's role. Certain cutscenes may require certain beats to
        #   be met.
        # requirements is a list of callables, all of which must return True in order for this InfoBlock to be
        #   considered for inclusion in the cutscene.
        # grammar is a list of grammar items giving text associated with this info block.
        # tags is a list of tags describing the mood set and/or function provided by this infoblock.
        # **kwargs are passed to the super method and should contain the representations of this info.
        #   The keys are the labels looked for by presentation templates. The values are usually strings.
        super().__init__(**kwargs)
        self.beat = beat
        self.requirements = list(requirements)
        self.tags = set(tags)


class PresentationNode:
    def __init__(self, template):
        self.template = template
        self.info_blocks = list()


class PresentationTemplate(object):
    # The abstract type from which other Presentation Nodes inherit. Communicates some information from the InfoBlocks
    # to the player. Uses the grammar from the attached info blocks to generate text.
    # node_type is a string describing the type of this node.
    # requirements is a list of callables(camp), all of which must return True for this template to be selectable now.
    # strings is a list of strings used by the presentation.
    def __init__(self, node_type="Abstract", requirements=(), strings=()):
        self.node_type = node_type
        self.requirements = requirements
        self.strings = strings

    @classmethod
    def get_all_subclasses_as_dict(cls, class_i_wanna_know_about=None):
        if not class_i_wanna_know_about:
            class_i_wanna_know_about = cls
        all_subclasses = dict()

        for subclass in class_i_wanna_know_about.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(cls.get_all_subclasses_as_dict(subclass))

        return all_subclasses

    def get_needed_info(self):
        # Search through the strings. Find all the needed info components.
        my_info = collections.defaultdict(list)
        for my_string in self.strings:
            cursor_pos = 0
            while cursor_pos < len(my_string):
                open_bracket = my_string.find("{", cursor_pos)
                if open_bracket > -1:
                    closed_bracket = my_string.find("}", open_bracket+1)
                    if closed_bracket != -1:
                        my_tag = my_string[open_bracket+1:closed_bracket]
                        # This tag could be needed info from an InfoBlock, or it could be an element passed to this
                        # presentation node. Info block strings will start with InfoBlockX_, where "X" is the ident
                        # of the info block (usually a number, right now I'm not sure it matters).
                        if my_tag.startswith("InfoBlock"):
                            a, b, c = my_tag.partition("_")
                            if c:
                                my_info[a].append(c)
                        cursor_pos = closed_bracket + 1
                    else:
                        break
                else:
                    break
        return my_info


class LancematePrep( object ):
    def __init__(self,id_tag,personality_traits=(),stats=(),exclude=()):
        # Choose a lancemate with the requested personality traits
        # and stats. Any characters marked by an id_tag in exclude
        # will be excluded.
        self.id_tag = id_tag
        self.personality_traits = set(personality_traits)
        self.stats = set(stats)
        self.exclude = exclude
    def matches_criteria(self,pc,cscene):
        ok = True
        if self.personality_traits:
            ok = pc.personality >= self.personality_traits
        if ok and self.stats:
            ok = set(pc.statline.keys()) >= self.stats
        if ok and self.exclude:
            ok = not bool([e for e in self.exclude if cscene.library.get(e,None) is pc])
        return ok
    def __call__(self,camp,cscene):
        candidates = list()
        for mpc in camp.get_active_lancemates():
            pc = mpc.get_pilot()
            if pc is not camp.pc and self.matches_criteria(pc,cscene):
                candidates.append(pc)
        if candidates:
            cscene.library[self.id_tag] = random.choice(candidates)
            return True


class MonologueDisplay( object ):
    def __init__(self,text,id_tag):
        self.text=text
        self.id_tag = id_tag
    def __call__(self,camp,cutscene):
        npc = cutscene.library.get(self.id_tag,None)
        if npc:
            myviz = ghdialogue.ghdview.ConvoVisualizer(npc,camp)
            mygrammar = pbge.dialogue.grammar.Grammar()
            pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,npc,None)
            myviz.text = pbge.dialogue.grammar.convert_tokens(self.text,mygrammar)
            pbge.alert_display(myviz.render)


class ExplosionDisplay(object):
    def __init__(self,dmg_n=2,dmg_d=6,radius=2,target="pc"):
        self.fx = pbge.effects.Invocation(
            fx=gears.geffects.DoDamage(dmg_n,dmg_d,anim=gears.geffects.SuperBoom,scale=None,scatter=True),
            area=pbge.scenes.targetarea.SelfCentered(radius=radius,delay_from=-1) )
        self.target = target
    def __call__(self,camp,cutscene):
        target = cutscene.library.get(self.target)
        if target:
            target = target.get_root()
            self.fx.invoke(camp,None,[target.pos,],pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence()


class SkillRollCutscene(cutscene.Cutscene):
    def __init__( self,stat_id,skill_id,target,library=None,on_success=(),on_failure=()):
        self.stat_id = stat_id
        self.skill_id = skill_id
        self.target = target
        self.library = dict()
        if library:
            self.library.update(library)
        self.on_success = list(on_success)
        self.on_failure = list(on_failure)
        
    def __call__(self,camp):
        if camp.get_party_skill(self.stat_id,self.skill_id) >= self.target:
            self.play_list(camp,self.on_success)
        else:
            self.play_list(camp,self.on_failure)


class SimpleMonologueDisplay( object ):
    def __init__(self,text,npc):
        self.text=text
        self.npc=npc
    def __call__(self,camp,do_rollout=True):
        myviz = ghdialogue.ghdview.ConvoVisualizer(self.npc,camp)
        if do_rollout:
            myviz.rollout()
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,self.npc,camp.pc)
        myviz.text = pbge.dialogue.grammar.convert_tokens(self.text,mygrammar)
        pbge.alert_display(myviz.render)


class SimpleMonologueMenu(pbge.rpgmenu.Menu):
    # Useful for times when you don't want or need to invoke the full conversation thingamajig.
    def __init__(self,text,npc,camp):
        super().__init__(
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.dx,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.dy,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.w,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.h,
            font=pbge.my_state.medium_font, padding=5, no_escape=True
        )
        self.npc = npc
        self.myviz = ghdialogue.ghdview.ConvoVisualizer(self.npc,camp)
        self.predraw = self.myviz.render
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,self.npc,camp.pc)
        self.myviz.text = pbge.dialogue.grammar.convert_tokens(text,mygrammar)


def AddTagBasedLancemateMenuItem(mymenu: pbge.rpgmenu.Menu, msg, value, camp, needed_tags):
    # Add an item to this menu where a lancemate suggests something. Designed to be used with the above
    # SimpleMonologueMenu, but really it can be used with any menu.
    # Returns the lancemate who makes the suggestion, or None if there is no applicable lancemate.
    needed_tags = set(needed_tags)
    winners = [pc for pc in camp.get_active_party() if needed_tags.issubset( pc.get_pilot().get_tags()) and pc.get_pilot() is not camp.pc]
    if winners:
        mylm = random.choice(winners).get_pilot()
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar, camp, mylm, camp.pc)
        true_msg = pbge.dialogue.grammar.convert_tokens(msg, mygrammar)
        mymenu.items.append(ghdialogue.ghdview.LancemateConvoItem(true_msg, value, desc=None, menu=mymenu, npc=mylm))
        return mylm

def AddSkillBasedLancemateMenuItem(mymenu: pbge.rpgmenu.Menu, msg, value, camp: gears.GearHeadCampaign, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_AVERAGE, pc_msg=None, no_random=False):
    # Add an item to this menu where a lancemate suggests something. Designed to be used with the above
    # SimpleMonologueMenu, but really it can be used with any menu.
    # Returns the lancemate who makes the suggestion, or None if there is no applicable lancemate.
    winner = camp.do_skill_test(stat_id, skill_id, rank, difficulty, include_pc=bool(pc_msg), no_random=no_random)
    if winner:
        mylm = winner.get_pilot()
        if mylm is camp.pc and pc_msg:
            mymenu.add_item(pc_msg, value)
        else:
            mygrammar = pbge.dialogue.grammar.Grammar()
            pbge.dialogue.GRAMMAR_BUILDER(mygrammar, camp, mylm, camp.pc)
            true_msg = pbge.dialogue.grammar.convert_tokens(msg, mygrammar)
            mymenu.items.append(ghdialogue.ghdview.LancemateConvoItem(true_msg, value, desc=None, menu=mymenu, npc=mylm))
        return mylm
