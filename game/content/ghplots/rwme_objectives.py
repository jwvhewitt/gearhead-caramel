from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder
from gears import champions

RWMO_DISTRESS_CALL = "RWMO_DISTRESS_CALL"
RWMO_FIGHT_RANDOS = "RWMO_FIGHT_RANDOS"
RWMO_MAYBE_AVOID_FIGHT = "RWMO_MAYBE_AVOID_FIGHT"

RWMO_TEST_OBJECTIVE = "RWMO_TEST_OBJECTIVE"


#   ****************************
#   ***  RWMO_DISTRESS_CALL  ***
#   ****************************

class RWMO_RescueSomeone(missionbuilder.BAM_RescueSomeone):
    LABEL = RWMO_DISTRESS_CALL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.seek_element(nart, "PILOT", self._npc_is_good, backup_seek_func=self._npc_is_okay,
                                  must_find=False, lock=True)
        if mynpc:
            self.register_element("PILOT", mynpc, lock=True)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
            mek = mynpc.get_root()
            self.register_element("SURVIVOR", mek)
            self.add_sub_plot(nart,"MT_TEAMUP_DEVELOPMENT",ident="NPC_TALK",elements={"NPC":mynpc,})
        else:
            mysurvivor = self.register_element("SURVIVOR", gears.selector.generate_ace(self.rank, self.elements.get(
                "ALLIED_FACTION", None), myscene.environment))
            mynpc = mysurvivor.get_pilot()
            self.register_element("PILOT", mynpc)
            team3.contents.append(mysurvivor)
            self.add_sub_plot(nart,"MT_NDDEV",ident="NPC_TALK",elements={"NPC":mynpc,})

        self.obj = adventureseed.MissionObjective("Rescue {}".format(self.elements["PILOT"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.choice_ready = True
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False
        self.intimidation_primed = False

        return True

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and \
               nart.camp.is_favorable_to_pc(candidate) and candidate not in nart.camp.party and \
               not nart.camp.is_unfavorable_to_pc(candidate)

    def _npc_is_okay(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and \
               not nart.camp.is_unfavorable_to_pc(candidate) and candidate not in nart.camp.party

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.choice_ready:
            self.choice_ready = False
            # Allow the PC to decide whether or not to respond to the distress call.
            npc = self.elements["PILOT"]
            pbge.alert("While traveling, you receive a distress call from {}.".format(npc))

            mymenu = game.content.ghcutscene.SimpleMonologueMenu("[DISTRESS_CALL]", self.elements["SURVIVOR"], camp)

            self.intimidating_npc = game.content.ghcutscene.AddSkillBasedLancemateMenuItem(
                mymenu, "Those [enemy_meks] don't look so brave to me. Follow my lead and we can end this quickly.",
                self.do_intimidation, camp,
                gears.stats.Ego, gears.stats.MechaFighting, self.rank, gears.stats.DIFFICULTY_HARD
            )

            mymenu.add_item("Go help {}".format(npc), None)
            mymenu.add_item("Ignore distress call", self.abandon_distress_call)

            choice = mymenu.query()
            if choice:
                choice(camp)

    def do_intimidation(self, camp):
        self.intimidation_primed = True

    def cancel_the_adventure(self,camp):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)

    def abandon_distress_call(self, camp: gears.GearHeadCampaign):
        # Any lancemates with Fellowship won't like this decision.
        candidates = [npc for npc in camp.get_active_party() if isinstance(npc.get_pilot(), gears.base.Character) and
                      gears.personality.Fellowship in npc.get_pilot().personality and npc.get_pilot() is not camp.pc]
        if candidates:
            npc = random.choice(candidates).get_pilot()
            npc.relationship.reaction_mod -= random.randint(6,10)
            game.content.ghcutscene.SimpleMonologueDisplay("[WE_SHOULD_HAVE_HELPED_THEM]", npc)(camp)
        self.cancel_the_adventure(camp)

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                if self.intimidation_primed:
                    pbge.alert("The hostile mecha freeze at the sight of {} striding confidently into battle.".format(self.intimidating_npc))
                    ghcutscene.SimpleMonologueDisplay("[THREATEN]", self.intimidating_npc)(camp)
                    pbge.alert("The hostile mecha flee the battlefield.")
                    self.elements["_eteam"].retreat(camp)
                else:
                    npc = self.elements["PILOT"]
                    camp.check_trigger("START",npc)
                    camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False


class FavorableDistressCall(missionbuilder.BAM_RescueSomeone):
    LABEL = RWMO_DISTRESS_CALL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.seek_element(nart, "PILOT", self._npc_is_good, lock=True)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
        mek = mynpc.get_root()
        self.register_element("SURVIVOR", mek)
        self.add_sub_plot(nart,"MT_TEAMUP_DEVELOPMENT",ident="NPC_TALK",elements={"NPC":mynpc,})

        self.obj = adventureseed.MissionObjective("Respond to {}'s distress call".format(self.elements["PILOT"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.choice_ready = True
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and \
               nart.camp.is_favorable_to_pc(candidate) and candidate not in nart.camp.party

    def PILOT_offers(self,camp):
        mylist = list()
        mylist.append( Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                context=ContextTag([context.HELLO, ]),))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] Good luck fighting those [enemy_meks]!",
                      context=ContextTag([context.CUSTOM,]),data={"reply":"Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.choice_ready:
            self.choice_ready = False
            # Allow the PC to decide whether or not to respond to the distress call.
            npc = self.elements["PILOT"]
            pbge.alert("While traveling, you receive a distress call from {}.".format(npc))

            mymenu = game.content.ghcutscene.SimpleMonologueMenu("[DISTRESS_CALL]", self.elements["SURVIVOR"], camp)

            if npc.faction and camp.is_unfavorable_to_pc(npc.faction):
                game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu, "We have no duty to aid an enemy combatant.",
                    self.cancel_the_adventure, camp, (gears.personality.Duty,)
                )

            self.glory_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                mymenu, "You realize there'll probably be a cash reward for helping out.",
                self.go_for_glory, camp, (gears.personality.Glory,)
            )

            self.fellowship_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                mymenu, "Helping {} is the right thing to do.".format(npc),
                self.go_for_fellowship, camp, (gears.personality.Fellowship,)
            )

            mymenu.add_item("Go help {}".format(npc), None)
            mymenu.add_item("Ignore distress call", self.abandon_distress_call)

            choice = mymenu.query()
            if choice:
                choice(camp)

    def go_for_glory(self, camp):
        self.glory_npc.relationship.reaction_mod += random.randint(1,6)

    def go_for_fellowship(self, camp):
        self.fellowship_npc.relationship.reaction_mod += random.randint(1,6)

    def abandon_distress_call(self, camp: gears.GearHeadCampaign):
        # Any lancemates with Fellowship won't like this decision.
        candidates = [npc for npc in camp.get_active_party() if isinstance(npc.get_pilot(), gears.base.Character) and
                      gears.personality.Fellowship in npc.get_pilot().personality and npc.get_pilot() is not camp.pc]
        if candidates:
            npc = random.choice(candidates).get_pilot()
            npc.relationship.reaction_mod -= random.randint(6,10)
            game.content.ghcutscene.SimpleMonologueDisplay("[WE_SHOULD_HAVE_HELPED_THEM]", npc)(camp)
        self.cancel_the_adventure(camp)

    def cancel_the_adventure(self,camp):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)


class TruckerDistressCall(missionbuilder.BAM_ExtractTrucker):
    LABEL = RWMO_DISTRESS_CALL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        ok = super().custom_init(nart)
        if ok:
            self.choice_ready = True
        return ok

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.choice_ready:
            self.choice_ready = False
            # Allow the PC to decide whether or not to respond to the distress call.
            npc = self.elements["PILOT"]
            pbge.alert("While traveling, you receive a distress call from {}.".format(npc))

            mymenu = game.content.ghcutscene.SimpleMonologueMenu("[DISTRESS_CALL]", self.elements["SURVIVOR"], camp)

            if npc.faction and camp.is_unfavorable_to_pc(npc.faction):
                game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu, "This trucker works for {}; we're under no obligation to help.".format(npc.faction),
                    self.cancel_the_adventure, camp, (gears.personality.Duty,)
                )
            else:
                self.duty_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu, "As cavaliers, we are duty-bound to help {}.".format(npc),
                    self.go_for_duty, camp, (gears.personality.Duty,)
                )

            self.justice_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                mymenu, "Those bandits need to be brought to justice.",
                self.go_for_justice, camp, (gears.personality.Justice,)
            )

            self.criminal_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                mymenu, "Meh, the bandits need to earn a living too. Let's just leave...",
                self.go_for_criminal, camp, (gears.tags.Criminal,)
            )

            mymenu.add_item("Go help {}".format(npc), None)
            mymenu.add_item("Ignore distress call", self.abandon_distress_call)

            choice = mymenu.query()
            if choice:
                choice(camp)

    def cancel_the_adventure(self,camp):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)

    def go_for_criminal(self, camp):
        self.criminal_npc.relationship.reaction_mod += random.randint(6,10)
        # Any lancemates with Justice won't like this decision.
        candidates = [npc for npc in camp.get_active_party() if isinstance(npc.get_pilot(), gears.base.Character) and
                      gears.personality.Justice in npc.get_pilot().personality and
                      npc.get_pilot() not in (camp.pc, self.criminal_npc)]
        if candidates:
            npc = random.choice(candidates).get_pilot()
            npc.relationship.reaction_mod -= random.randint(1,6)
            game.content.ghcutscene.SimpleMonologueDisplay("[WE_SHOULD_HAVE_HELPED_THEM]", npc)(camp)
        self.cancel_the_adventure(camp)

    def go_for_duty(self, camp):
        self.duty_npc.relationship.reaction_mod += random.randint(1,6)

    def go_for_justice(self, camp):
        self.justice_npc.relationship.reaction_mod += random.randint(6,10)
        # Any criminal lancemates won't like this decision.
        candidates = [npc for npc in camp.get_active_party() if isinstance(npc.get_pilot(), gears.base.Character) and
                      gears.tags.Criminal in npc.get_pilot().get_tags() and
                      npc.get_pilot() not in (camp.pc, self.justice_npc)]
        if candidates:
            npc = random.choice(candidates).get_pilot()
            npc.relationship.reaction_mod -= random.randint(1,6)
            game.content.ghcutscene.SimpleMonologueDisplay("If your idea of justice is protecting the corporations at the expense of the rest of us, then I want no part in it.", npc)(camp)

    def abandon_distress_call(self, camp: gears.GearHeadCampaign):
        # Any non-criminal lancemates won't like this decision.
        candidates = [npc for npc in camp.get_active_party() if isinstance(npc.get_pilot(), gears.base.Character) and
                      gears.tags.Criminal not in npc.get_pilot().get_tags() and npc.get_pilot() is not camp.pc]
        if candidates:
            npc = random.choice(candidates).get_pilot()
            npc.relationship.reaction_mod -= random.randint(6,10)
            game.content.ghcutscene.SimpleMonologueDisplay("[WE_SHOULD_HAVE_HELPED_THEM]", npc)(camp)
        self.cancel_the_adventure(camp)


#   ***************************
#   ***  RWMO_FIGHT_RANDOS  ***
#   ***************************

class FightSomeRandos(Plot):
    LABEL = RWMO_FIGHT_RANDOS
    active = True
    scope = "LOCALE"
    INTRO_ALERT = "You are attacked by a force of hostile mecha."

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat hostile mecha".format(myfac), missionbuilder.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            pbge.alert(self.INTRO_ALERT.format(**self.elements))
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class FightSomeAlmostRandos(FightSomeRandos):
    # As above, but you're facing a faction you have already pissed off.
    LABEL = RWMO_FIGHT_RANDOS
    active = True
    scope = "LOCALE"
    INTRO_ALERT = "You confront a patrol sent by {ENEMY_FACTION}."

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()

        candidates = [f for f in nart.camp.faction_relations.keys() if nart.camp.is_unfavorable_to_pc(f)]
        if candidates:
            myfac = random.choice(candidates)
            self.elements["ENEMY_FACTION"] = myfac

            self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

            team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            team2.contents += myunit.mecha_list

            self.obj = adventureseed.MissionObjective("Defeat {}".format(myfac), missionbuilder.MAIN_OBJECTIVE_VALUE)
            self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return candidates


#   ********************************
#   ***  RWMO_MAYBE_AVOID_FIGHT  ***
#   ********************************

class RWMO_SkilledAvoidance( Plot ):
    LABEL = RWMO_MAYBE_AVOID_FIGHT
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        self.intro_ready = True
        return True

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.intro_ready:
            self.intro_ready = False
            candidates = list()
            if camp.party_has_skill(gears.stats.Scouting):
                candidates.append(self.attempt_scouting)
            if camp.party_has_skill(gears.stats.Stealth):
                candidates.append(self.attempt_stealth)
            if camp.party_has_skill(gears.stats.Wildcraft):
                candidates.append(self.attempt_wildcraft)
            if candidates:
                random.choice(candidates)(camp)

    def attempt_scouting(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Scouting,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You detect hostile mecha on the road ahead. They are still far enough away that you can avoid them if you want to.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[I_HAVE_DETECTED_ENEMIES] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_stealth(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Stealth,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You encounter a group of hostile mecha, but manage to remain unseen.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[ENEMIES_HAVE_NOT_DETECTED_US] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_wildcraft(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Wildcraft,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You find tracks belonging to enemy mecha. It would be a simple matter to find an alternate route around them.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[THERE_ARE_ENEMY_TRACKS] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def cancel_the_adventure(self,camp):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)
