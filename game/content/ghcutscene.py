from pbge import cutscene
from .. import ghdialogue
import random
import pbge
import gears


TOPIC_CITY_INTRO = "city_intro"
TOPIC_DEBRIEFING = "debriefing"

CSTEXT_ALERT_OPINION = "ALERT_OPINION"
CSTEXT_ALERT_MISSION = "ALERT_MISSION"
CSTEXT_ALERT_PHYSICALDESC = "ALERT_PHYSICALDESC"
CSTEXT_CITY_EPITHET = "CITY_EPITHET"
CSTEXT_SPEAK_CHEERFUL = "SPEAK_CHEERFUL"
CSTEXT_SPEAK_OPINION = "SPEAK_OPINION"
CSTEXT_SPEAK_MISSION = "SPEAK_MISSION"



class MonologuePresentation(cutscene.PresentationTemplate):
    SPEAKING_HAS_OCCURRED = "SPEAKING_HAS_OCCURRED"
    def __init__(self, speaker_id="_SPEAKER", **kwargs):
        self.speaker_id = speaker_id
        super().__init__(**kwargs)

    def _generate_current_state(self, start_state: cutscene.CutsceneState):
        cloned_state = super()._generate_current_state(start_state)
        cloned_state.tags.add(self.SPEAKING_HAS_OCCURRED)
        return cloned_state

    def play(self, camp, info_blocks, node_state: cutscene.CutsceneState):
        msg = self.strings[0].format(**self.get_info_strings(info_blocks, node_state))
        npc = node_state.elements.get(self.speaker_id, None)
        if npc:
            _=SimpleMonologueDisplay(msg, npc, camp, self.SPEAKING_HAS_OCCURRED not in node_state.prev_state_tags)
        else:
            print("Error: No NPC found for monologue presentation {}".format(self.name))

class AlertThenMonologuePresentation(MonologuePresentation):
    def play(self, camp, info_blocks, node_state: cutscene.CutsceneState):
        pbge.alerts.TextAlert(self.strings[0].format(**self.get_info_strings(info_blocks, node_state)))
        msg = self.strings[1].format(**self.get_info_strings(info_blocks, node_state))
        npc = node_state.elements.get(self.speaker_id, None)
        if npc:
            _=SimpleMonologueDisplay(msg, npc, camp, self.SPEAKING_HAS_OCCURRED not in node_state.prev_state_tags)
        else:
            print("Error: No NPC found for monologue presentation {}".format(self.name))


class LMSpeakerRequirement(cutscene.CutsceneRequirement):
    # Find a lancemate to speak the monologue. Store the lancemate, if found, as "_SPEAKER" in current_state.elements
    def __init__(self, speaker_id="_SPEAKER", needed_tags=(), forbidden_tags=()):
        self.speaker_id = speaker_id
        self.needed_tags = gears.string_tags_to_singletons(needed_tags)
        self.forbidden_tags = gears.string_tags_to_singletons(forbidden_tags)

    def __call__(self, camp: gears.GearHeadCampaign, current_state: cutscene.CutsceneState):
        candidates = list()
        for base_lm in camp.get_active_lancemates():
            true_lm = base_lm.get_pilot()
            if isinstance(true_lm, gears.base.Character):
                npc_tags = true_lm.get_tags(True)
                if self.needed_tags.issubset(npc_tags) and not self.forbidden_tags.intersection(npc_tags):
                    candidates.append(base_lm)
        if candidates:
            lm = random.choice(candidates)
            current_state.elements[self.speaker_id] = lm
            return True


class PCTagRequirement(cutscene.CutsceneRequirement):
    def __init__(self, needed_tags=(), forbidden_tags=()):
        self.needed_tags = gears.string_tags_to_singletons(needed_tags)
        self.forbidden_tags = gears.string_tags_to_singletons(forbidden_tags)

    def __call__(self, camp: gears.GearHeadCampaign, current_state):
        pc_tags = camp.pc.get_tags(True)
        return self.needed_tags.issubset(pc_tags) and not self.forbidden_tags.intersection(pc_tags)


class StatusTagRequirement(PCTagRequirement):
    def __call__(self, camp: gears.GearHeadCampaign, current_state: cutscene.CutsceneState):
        return self.needed_tags.issubset(current_state.tags) and not \
            self.forbidden_tags.intersection(current_state.tags)


class SpeakerTagRequirement(PCTagRequirement):
    def __call__(self, camp: gears.GearHeadCampaign, current_state):
        npc = current_state.elements.get("_SPEAKER", None)
        if npc:
            npc = npc.get_pilot()
            if isinstance(npc, gears.base.Character):
                npc_tags = npc.get_tags(True)
                return self.needed_tags.issubset(npc_tags) and not self.forbidden_tags.intersection(npc_tags)
        else:
            pc_tags = camp.pc.get_tags(True)
            return self.needed_tags.issubset(pc_tags) and not self.forbidden_tags.intersection(pc_tags)


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
            _=SimpleMonologueDisplay(self.text, npc, camp, )


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


class SimpleMonologueDisplay( pbge.alerts.AbstractAlert ):
    def __init__(self, text, npc, camp, do_rollout=True, **kwargs):
        self.text=text
        self.npc=npc
        self.viz = ghdialogue.ghdview.ConvoVisualizer(self.npc,camp, do_rollout=do_rollout)
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,self.npc,camp.pc, True)
        self.viz.text = pbge.dialogue.grammar.convert_tokens(self.text,mygrammar)
        self.recorded_message = False
        super().__init__(0, 0, 0, 0, **kwargs)

    def _render(self, delta):
        if not self.recorded_message:
            pbge.my_state.record_message("{}: {}".format(self.npc.get_pilot(), self.viz.text))
            self.recorded_message = True
        self.viz.render(delta)

    def _builtin_responder(self, ev):
        if not self.viz.is_rolling_out:
            super()._builtin_responder(ev)
 

def alert_with_grammar(camp, text):
    # Do an alert display, but with grammar tokens correctly converted.
    mygrammar = pbge.dialogue.grammar.Grammar()
    pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,camp.pc,camp.pc)
    altered_text = pbge.dialogue.grammar.convert_tokens(text,mygrammar)
    _=pbge.alerts.TextAlert(altered_text)


class SimpleMonologueMenu(pbge.widgetmenu.MenuWidget):
    # Useful for times when you don't want or need to invoke the full conversation thingamajig.
    TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_WIDGET,}

    def __init__(self,text,npc,camp, pop_when_clicked=True):
        super().__init__(
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.dx,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.dy,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.w,
            ghdialogue.ghdview.ConvoVisualizer.MENU_AREA.h,
            font=pbge.my_state.medium_font, padding=5, no_escape=True,
            pop_when_clicked=pop_when_clicked
        )
        self.npc = npc
        self.myviz = ghdialogue.ghdview.ConvoVisualizer(self.npc,camp)
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,self.npc,camp.pc)
        self.myviz.text = pbge.dialogue.grammar.convert_tokens(text,mygrammar)

    def _render(self, delta):
        self.myviz.render(delta)
        super()._render(delta)

    def add_dialogue_item(self, camp, pc, raw_msg, on_click, data=None, desc=None, ):
        mygrammar = pbge.dialogue.grammar.Grammar()
        pbge.dialogue.GRAMMAR_BUILDER(mygrammar,camp,pc,self.npc)
        msg = pbge.dialogue.grammar.convert_tokens(raw_msg,mygrammar)
        _=self.add_item(msg, on_click, data=data, desc=desc)


class AlertMonologueMenu(SimpleMonologueMenu):
    # Functions as above, but is added to the alert queue.
    def __init__(self,text,npc,camp, pop_when_clicked=True):
        super().__init__(text, npc, camp, pop_when_clicked=pop_when_clicked)
        self.tags.add(pbge.alerts.WTAG_ALERT)
        pbge.my_state.alert_queue.append(self)


def AddTagBasedLancemateMenuItem(mymenu: pbge.widgetmenu.MenuWidget, msg, on_click: pbge.widgets.On_Click, camp, needed_tags, data=None):
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
        _=mymenu.add_custom(ghdialogue.ghdview.LancemateConvoItem(true_msg, data, desc=None, npc=mylm, on_click=on_click))
        return mylm


def AddSkillBasedLancemateMenuItem(mymenu: pbge.widgetmenu.MenuWidget, msg, on_click: pbge.widgets.On_Click, camp: gears.GearHeadCampaign, stat_id, skill_id, rank, difficulty=gears.stats.DIFFICULTY_AVERAGE, pc_msg=None, no_random=False, data=None):
    # Add an item to this menu where a lancemate suggests something. Designed to be used with the above
    # SimpleMonologueMenu, but really it can be used with any menu.
    # Returns the lancemate who makes the suggestion, or None if there is no applicable lancemate.
    winner = camp.do_skill_test(stat_id, skill_id, rank, difficulty, include_pc=bool(pc_msg), no_random=no_random)
    if winner:
        mylm = winner.get_pilot()
        if mylm is camp.pc and pc_msg:
            _=mymenu.add_item(pc_msg, on_click, data=data)
        else:
            mygrammar = pbge.dialogue.grammar.Grammar()
            pbge.dialogue.GRAMMAR_BUILDER(mygrammar, camp, mylm, camp.pc)
            true_msg = pbge.dialogue.grammar.convert_tokens(msg, mygrammar)
            _=mymenu.add_custom(ghdialogue.ghdview.LancemateConvoItem(true_msg, on_click, desc=None, npc=mylm))
        return mylm
