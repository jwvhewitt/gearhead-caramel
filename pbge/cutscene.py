import random
from . import alert
import collections
import glob
import json


# Note: Cutscenes must be initialized after all other modules have been loaded!!! Because of this, they aren't
# initialized in the pbge.init function and should instead be initialized using pbge.cutscene.init(file_pattern)
# after everything else has been loaded.

PRESENTATION_TEMPLATES = list()
PRESENTATION_SUBCLASSES = dict()
REQUIREMENT_SUBCLASSES = dict()
OPPOSITE_TAGS = dict()


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
    def __init__(self, topic, elements=None, prev_node=None, tags=(), start_beats=(), mid_beats=(), final_beats=(), info_blocks=()):
        self.topic = topic
        self.elements = dict()
        if elements:
            self.elements.update(elements)
        self.prev_node = prev_node
        self.tags = set(tags)
        self.start_beats = list(start_beats)
        self.mid_beats = list(mid_beats)
        self.final_beats = list(final_beats)
        self.info_blocks = list(info_blocks)

    def _get_current_beats(self):
        return self.start_beats or self.mid_beats or self.final_beats or ()

    def get_priority_and_optional_info_blocks(self, camp):
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
        current_beats = self._get_current_beats()
        all_beats = self.start_beats + self.mid_beats + self.final_beats
        for can in candidates:
            if can.beat:
                if can.beat in current_beats:
                    priority_info.append(can)
                elif can.beat not in all_beats:
                    optional_info.append(can)
            else:
                optional_info.append(can)
        return priority_info, optional_info

    def apply_info(self, ib: InfoBlock):
        if ib in self.info_blocks:
            self.info_blocks.remove(ib)
        if ib.beat:
            if ib.beat in self.start_beats:
                self.start_beats.remove(ib.beat)
            elif ib.beat in self.mid_beats:
                self.mid_beats.remove(ib.beat)
            elif ib.beat in self.final_beats:
                self.final_beats.remove(ib.beat)
        if ib.tags:
            for k,v in OPPOSITE_TAGS.items():
                if k in ib.tags and v in self.tags:
                    self.tags.remove(v)
        self.tags.update(ib.tags)

    def clone(self, current_node=None):
        return self.__class__(
            topic=self.topic, elements=self.elements, prev_node=current_node or self.prev_node, tags=self.tags,
            start_beats=self.start_beats, mid_beats=self.mid_beats, final_beats=self.final_beats,
            info_blocks=self.info_blocks
        )

    def is_finished(self):
        return not (self.start_beats or self.mid_beats or self.final_beats)

    @property
    def prev_state(self):
        if self.prev_node:
            return self.prev_node.node_state

    @property
    def prev_state_tags(self):
        if self.prev_node:
            return self.prev_node.node_state.tags
        else:
            return set()


class CutscenePlan:
    def __init__(self, topic, elements=None, start_beats=(), mid_beats=(), final_beats=(), info_blocks=()):
        # topic is a string describing the overall function of this cutscene
        # elements is a list of named things that might get used by Presentation Nodes or to format text.
        # ordered_beats is a list of beats that must be included in the cutscene; they must appear in the order given
        # unordered_beats must also appear in the cutscene; these can appear in any order
        # info_blocks is a list of InfoBlock objects from which the cutscene will be created.
        self.topic = topic
        self.elements = dict()
        if elements:
            self.elements.update(elements)
        self.start_beats = list(start_beats)
        self.mid_beats = list(mid_beats)
        self.final_beats = list(final_beats)
        self.info_blocks = list(info_blocks)

    def _get_next_nodes(self, camp, previous_state: CutsceneState, previous_node=None):
        current_state = previous_state.clone(previous_node)
        premium_nodes = list()
        regular_nodes = list()
        for pt in PRESENTATION_TEMPLATES:
            can_node = pt.create_candidate_for_situation(camp, current_state)
            if can_node and can_node.premium:
                premium_nodes.append(can_node)
            elif can_node:
                regular_nodes.append(can_node)
        while premium_nodes or regular_nodes:
            if premium_nodes:
                next_node = random.choice(premium_nodes)
                premium_nodes.remove(next_node)
            else:
                next_node = random.choice(regular_nodes)
                regular_nodes.remove(next_node)
            if next_node.node_state.is_finished():
                return [next_node]
            else:
                followup = self._get_next_nodes(camp, next_node.node_state, next_node)
                if followup:
                    return [next_node] + followup

    def build(self, camp):
        camp.expand_cutscene(self)
        current_state = CutsceneState(topic=self.topic, elements=self.elements, start_beats=self.start_beats,
                                      mid_beats=self.mid_beats, final_beats=self.final_beats,
                                      info_blocks=self.info_blocks)
        return self._get_next_nodes(camp, current_state)

    def play(self, camp):
        presentation = self.build(camp)
        for pn in presentation:
            pn.play(camp)


class PresentationNode:
    def __init__(self, template):
        self.template = template
        self.info_blocks = dict()
        self.premium = False
        self.node_state = None

    def play(self, camp):
        self.template.play(camp, self.info_blocks, self.node_state)


class PresentationTemplate(object):
    # The abstract type from which other Presentation Nodes inherit. Communicates some information from the InfoBlocks
    # to the player. Uses the grammar from the attached info blocks to generate text.
    # node_type is a string describing the type of this node.
    # requirements is a list of callables(camp, current_status), all of which must return True for this template to be selectable now.
    # strings is a list of strings used by the presentation.
    def __init__(self, name="", node_type="Abstract", requirements=(), strings=()):
        self.name = name
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
                        if my_tag.startswith("INFOBLOCK"):
                            a, b, c = my_tag.partition("_")
                            if c:
                                my_info[a].append(c)
                        cursor_pos = closed_bracket + 1
                    else:
                        break
                else:
                    break
        return my_info

    def _generate_current_state(self, start_state: CutsceneState):
        cloned_state = start_state.clone()
        # Don't copy over private elements, same as with plots.
        # The element "_SPEAKER" will generally be used if this presentation node involves someone speaking. The
        # previous speaker can always be found from the node's node_state.prev_node.node_state.elements. Which is an
        # ungainly long reference now that I look at it. Maybe I should add a prev_state property or something.
        for k in start_state.elements.keys():
            if k.startswith("_"):
                del cloned_state.elements[k]
        return cloned_state

    def create_candidate_for_situation(self, camp, start_state: CutsceneState):
        # Attempt to create a presentation node for this situation.
        cloned_state = self._generate_current_state(start_state)
        if all([req(camp, cloned_state) for req in self.requirements]):
            can_node = PresentationNode(self)
            needed_info = self.get_needed_info()
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
            can_node.node_state = cloned_state
            return can_node

    def get_info_strings(self, info_blocks, node_state: CutsceneState):
        info_strings = node_state.elements.copy()
        for k,v in self.get_needed_info().items():
            for info_label in v:
                info_strings["_".join([k, info_label])] = info_blocks[k][info_label]
        return info_strings

    def play(self, camp, info_blocks, node_state):
        raise NotImplementedError("Base PresentationTemplate doesn't define the play method.")

    @staticmethod
    def dict_to_template(param_dict: dict):
        pt_type = param_dict.pop("type", None)
        if pt_type and pt_type in PRESENTATION_SUBCLASSES:
            if "requirements" in param_dict:
                req_dicts = param_dict.pop("requirements")
                req_list = list()
                for req in req_dicts:
                    req_type = req.pop("type", None)
                    if req_type and req_type in REQUIREMENT_SUBCLASSES:
                        req_list.append(REQUIREMENT_SUBCLASSES[req_type](**req))
                    else:
                        print("Error: Requirement type {} not found for {}".format(req_type, req))
                param_dict["requirements"] = req_list
            return PRESENTATION_SUBCLASSES[pt_type](**param_dict)
        else:
            print("Error: No presentation type {} found for {}".format(pt_type, param_dict))


class AlertPresentation(PresentationTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def play(self, camp, info_blocks, node_state):
        alert(self.strings[0].format(**self.get_info_strings(info_blocks, node_state)))


class CutsceneRequirement:
    # Subclass requirements from this class so they can be found by dict_to_template when needed.
    # InfoBlock requirements don't have to subclass this because they'll generally be created on the fly. But they can
    #   use these requirement objects, which may contain useful utilities.
    @classmethod
    def get_all_subclasses_as_dict(cls, class_i_wanna_know_about=None):
        if not class_i_wanna_know_about:
            class_i_wanna_know_about = cls
        all_subclasses = dict()

        for subclass in class_i_wanna_know_about.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(cls.get_all_subclasses_as_dict(subclass))

        return all_subclasses

    def __call__(self, camp, current_state):
        return False


class TopicRequirement(CutsceneRequirement):
    def __init__(self, topic=""):
        self.topic = topic

    def __call__(self, camp, current_state: CutsceneState):
        return current_state.topic == self.topic


class MustBeFirstNode(CutsceneRequirement):
    def __call__(self, camp, current_state: CutsceneState):
        return not current_state.prev_node


class MustNotBeFirstNode(CutsceneRequirement):
    def __call__(self, camp, current_state: CutsceneState):
        return bool(current_state.prev_node)


def init_cutscenes(*args):
    # args is a list of file patterns to check for presentation templates. This can be used to split the templates
    # between different folders, for example.
    PRESENTATION_SUBCLASSES.update(PresentationTemplate.get_all_subclasses_as_dict())
    REQUIREMENT_SUBCLASSES.update(CutsceneRequirement.get_all_subclasses_as_dict())
    protobits = list()
    for file_pattern in args:
        myfiles = glob.glob(file_pattern)
        for f in myfiles:
            with open(f, 'rt') as fp:
                mylist = json.load(fp)
                if mylist:
                    protobits += mylist
    for j in protobits:
        PresentationTemplate.dict_to_template(j)


# Old Stuff:

class Beat( object ):
    def __init__(self,display,prep=None,effect=None,children=(),needs_reply=False):
        # "prep" is a callable that takes (camp,cutscene) and returns
        # True if everything went okay.
        # "display" is a callable that takes (camp,cutscene) and handles
        # one part of the cutscene, such as a line of dialogue.
        self.prep = prep
        self.display = display
        self.effect = effect
        self.children = list(children)
        self.needs_reply = needs_reply
        self.reply = None

    def build( self, camp, cutscene ):
        ok = True
        if self.prep:
            ok = self.prep(camp,cutscene)
        if ok:
            candidates = list(self.children)
            random.shuffle(candidates)
            while candidates and not self.reply:
                c = candidates.pop()
                self.reply = c.build(camp,cutscene)
            if self.reply or not self.needs_reply:
                return self
                
    def run( self, camp, cutscene ):
        if self.display:
            self.display(camp,cutscene)
        if self.effect:
            self.effect(camp)

class Cutscene( object ):
    def __init__( self, library=dict(),beats=()):
        self.library = dict()
        self.library.update(library)
        self.beats = list(beats)
    def play_list(self,camp,beats):
        # Generate the beat sequence.
        candidates = list(beats)
        random.shuffle(candidates)
        start_beat = None
        while candidates and not start_beat:
            c = candidates.pop()
            start_beat = c.build(camp,self)
        while start_beat:
            start_beat.run(camp,self)
            start_beat = start_beat.reply
    def __call__( self, camp ):
        self.play_list(camp,self.beats)
        
class AlertDisplay( object ):
    def __init__(self,text):
        self.text=text
    def __call__(self,camp,cutscene):
        alert(self.text.format(**cutscene.library))




