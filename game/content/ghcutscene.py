import collections

from pbge import cutscene
from .. import ghdialogue
import random
import pbge
import gears


PRESENTATION_TEMPLATES = list()

class InfoBlock(dict):
    # Contains info that may need to be expressed during the cutscene.
    def __init__(self, beat=None, requirements=(), tags=(), **kwargs):
        # beat is an optional string describing this InfoBlock's role. Certain cutscenes may require certain beats to
        #   be met.
        # requirements is a list of callables(camp, state), all of which must return True in order for this InfoBlock
        #   to be considered for inclusion in the cutscene.
        # grammar is a list of grammar items giving text associated with this info block.
        # tags is a list of tags describing the mood set and/or function provided by this infoblock.
        # **kwargs are passed to the super method and should contain the representations of this info.
        #   The keys are the labels looked for by presentation templates. The values are usually strings.
        super().__init__(**kwargs)
        self.beat = beat
        self.requirements = list(requirements)
        self.tags = set(tags)


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

    def get_priority_and_optional_info_blocks(self, camp: gears.GearHeadCampaign):
        # This function returns two lists: One of info blocks which have priority (they satisfy one of the beats
        # needed by the cutscene state) and one for other info blocks which can be used now but are optional.
        # I am still recovering from Covid 19 and programming is hard, folks. I don't know if it is brain fog,
        # tiredness, or just all the drugs I'm taking but it is more difficult to complete intensive verbal/language
        # tasks now than usual, which is pretty bad considering that all of my jobs are language-intensive.
        # Anyhow, this comment is left here as a time capsule from December 2022. Also so if there are any really
        # stupid bugs in the following code at least you know I was stoned on codeine when I wrote it.
        candidates = [ib for ib in self.info_blocks if all([req(camp, self) for req in ib.requirements])]
        priority_info = list()
        optional_info = list()
        for can in candidates:
            if can.beat:
                if can.beat in self.ordered_beats:
                    if can.beat == self.ordered_beats[0]:
                        priority_info.append(can)
                elif can.beat in self.unordered_beats:
                    priority_info.append(can)
                else:
                    optional_info.append(can)
            else:
                optional_info.append(can)
        return priority_info, optional_info

    def apply_info(self, ib: InfoBlock):
        if ib in self.info_blocks:
            self.info_blocks.remove(ib)
        if ib.beat:
            if ib.beat in self.ordered_beats:
                self.ordered_beats.remove(ib.beat)
            elif ib.beat in self.unordered_beats:
                self.unordered_beats.remove(ib.beat)
        self.tags.update(ib.tags)

    def clone(self, current_node=None):
        return self.__class__(
            elements=self.elements, prev_node=current_node or self.prev_node, tags=self.tags,
            ordered_beats=self.ordered_beats, unordered_beats=self.unordered_beats, info_blocks=self.info_blocks
        )


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
        self.unordered_beats = list(unordered_beats)
        self.info_blocks = list(info_blocks)

    def _get_next_nodes(self, camp: gears.GearHeadCampaign, previous_state: CutsceneState, presentation: list, previous_node=None):
        current_state = previous_state.clone(previous_node)
        candidate_nodes = [pt for pt in PRESENTATION_TEMPLATES if pt.is_candidate_for_situation(current_state)]

    def build(self, camp: gears.GearHeadCampaign):
        current_state = CutsceneState(elements=self.elements, ordered_beats=self.ordered_beats,
                                      unordered_beats=self.unordered_beats, info_blocks=self.info_blocks)
        presentation = list()
        presentation += self._get_next_nodes(camp, current_state, presentation)

    def play(self, camp: gears.GearHeadCampaign):
        self.build(camp)
        pass


class PresentationNode:
    def __init__(self, template):
        self.template = template
        self.info_blocks = dict()
        self.premium = False
        self.final_state = None


class PresentationTemplate(object):
    # The abstract type from which other Presentation Nodes inherit. Communicates some information from the InfoBlocks
    # to the player. Uses the grammar from the attached info blocks to generate text.
    # node_type is a string describing the type of this node.
    # requirements is a list of callables(camp, current_status), all of which must return True for this template to be selectable now.
    # strings is a list of strings used by the presentation.
    def __init__(self, node_type="Abstract", requirements=(), strings=()):
        self.node_type = node_type
        self.requirements = requirements
        self.strings = strings
        PRESENTATION_TEMPLATES.append(self)

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
        # Keys = infoblock identifiers
        # Values = string labels needed
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

    def create_candidate_for_situation(self, camp: gears.GearHeadCampaign, current_state: CutsceneState):
        # Attempt to create a presentation node for this situation.
        if all([req(camp, current_state) for req in self.requirements]):
            can_node = PresentationNode(self)
            needed_info = self.get_needed_info()
            cloned_state = current_state.clone()
            for k,v in needed_info.items():
                priority_blocks, optional_blocks = cloned_state.get_priority_and_optional_info_blocks(camp)
                candidates = [ib for ib in priority_blocks if all([tag in ib for tag in v])]
                if candidates:
                    can_node.premium = True
                else:
                    candidates = [ib for ib in optional_blocks if all([tag in ib for tag in v])]
                if candidates:
                    new_ib = random.choice(candidates)
                    cloned_state.apply_info(new_ib)
                    can_node.info_blocks[k] = new_ib
                else:
                    return None
            # If we are here, we have a candidate node with info blocks selected.
            can_node.final_state = cloned_state
            return can_node


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
