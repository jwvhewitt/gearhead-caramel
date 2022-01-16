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

RWMO_A_CHALLENGER_APPROACHES = "RWMO_A_CHALLENGER_APPROACHES"
RWMO_DISTRESS_CALL = "RWMO_DISTRESS_CALL"
RWMO_FIGHT_RANDOS = "RWMO_FIGHT_RANDOS"
RWMO_MAYBE_AVOID_FIGHT = "RWMO_MAYBE_AVOID_FIGHT"
RWMO_SECURITY_CHECK = "RWMO_SECURITY_CHECK"

RWMO_TEST_OBJECTIVE = "RWMO_TEST_OBJECTIVE"


#   **************************************
#   ***  RWMO_A_CHALLENGER_APPROACHES  ***
#   **************************************

class RWMO_ThisTimeItsPersonal(Plot):
    LABEL = RWMO_A_CHALLENGER_APPROACHES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc: gears.base.Character = self.seek_element(nart, "_commander", self.is_good_challenger, must_find=True, lock=True)
        myfac = mynpc.faction
        if not mynpc.job:
            mynpc.job = gears.jobs.ALL_JOBS["Mecha Pilot"]
        if mynpc.renown < self.rank:
            mynpc.job.scale_skills(mynpc, mynpc.renown + random.randint(1,10))

        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        myunit = gears.selector.RandomMechaUnit(self.rank, 120 - mynpc.get_reaction_score(nart.camp.pc, nart.camp),
                                                myfac, myscene.environment, add_commander=False)
        self.add_sub_plot(nart,"MC_GRUDGE_MATCH", elements={"NPC":mynpc})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Deal with {}".format(self.elements["_commander"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True
        self.alert_ready = True

        return True

    def is_good_challenger(self, nart, candidate):
        # We want a challenger who is personally unfavorable to the PC and who has lost to the PC in the past.
        return (
            isinstance(candidate, gears.base.Character) and candidate.combatant and
            candidate not in nart.camp.party and candidate.relationship and candidate.relationship.is_unfavorable() and
            candidate.relationship.get_recent_memory({gears.relationships.MEM_LoseToPC,})
        )


    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.alert_ready:
            self.alert_ready = False
            # Allow the PC to decide whether or not to accept the challenge.
            npc = self.elements["_commander"]
            pbge.alert("The way forward is blocked by {}'s lance.".format(npc))

    def _commander_offers(self, camp):
        mylist = list()
        npc = self.elements["_commander"]

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[CHANGE_MIND_AND_RETREAT]",
                context=ContextTag([context.RETREAT, ]), effect=self._retreat,
            ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, rank=npc.renown,
            difficulty=gears.stats.DIFFICULTY_HARD,
            no_random=False
        )

        return mylist

    def _retreat(self, camp):
        pbge.alert("{}'s lance flees the battlefield.".format(self.elements["_commander"]))
        self.elements["_eteam"].retreat(camp)


class RWMO_TheGambler(Plot):
    LABEL = RWMO_A_CHALLENGER_APPROACHES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene: gears.GearHeadScene = self.elements["LOCALE"]
        myscene.attributes |= {gears.tags.SCENE_SOLO, gears.tags.SCENE_ARENARULES}
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(5, 5, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc: gears.base.Character = self.seek_element(nart, "_commander", self.is_good_challenger, must_find=True, lock=True)
        if not mynpc.job:
            mynpc.job = gears.jobs.ALL_JOBS["Mecha Pilot"]
        if mynpc.renown < self.rank:
            mynpc.job.scale_skills(mynpc, mynpc.renown + random.randint(1,10))
        self.add_sub_plot(nart,"MC_DUEL_DEVELOPMENT",elements={"NPC":mynpc})

        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)

        self.obj = adventureseed.MissionObjective("Defeat challenger {}".format(self.elements["_commander"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True
        self.choice_ready = True

        return True

    def is_good_challenger(self, nart, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate.combatant and
            candidate not in nart.camp.party and (
            (candidate.faction and candidate.faction.get_faction_tag() is gears.factions.ProDuelistAssociation) or
            (gears.personality.Glory in candidate.personality and gears.tags.Adventurer in candidate.get_tags())
            ) and candidate.renown <= self.rank + 15
        )

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.choice_ready:
            self.choice_ready = False
            # Allow the PC to decide whether or not to accept the challenge.
            npc = self.elements["_commander"]
            pbge.alert("You are approached by {}.".format(npc))

            mymenu = game.content.ghcutscene.SimpleMonologueMenu("[I_PROPOSE_DUEL]", npc, camp)

            mymenu.add_item("Accept the challenge", None)
            mymenu.add_item("Reject the challenge", self.cancel_the_adventure)

            choice = mymenu.query()
            if choice:
                choice(camp)

    def cancel_the_adventure(self,camp: gears.GearHeadCampaign):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)


class RWMO_GenericChallenger(Plot):
    LABEL = RWMO_A_CHALLENGER_APPROACHES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc: gears.base.Character = self.seek_element(nart, "_commander", self.is_good_challenger, must_find=True, lock=True)
        myfac = mynpc.faction
        if not mynpc.job:
            mynpc.job = gears.jobs.ALL_JOBS["Mecha Pilot"]
        if mynpc.renown < self.rank:
            mynpc.job.scale_skills(mynpc, mynpc.renown + random.randint(1,10))

        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        self.add_sub_plot(nart,"MC_ENEMY_DEVELOPMENT",elements={"NPC":mynpc})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat challenger {}".format(self.elements["_commander"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True
        self.choice_ready = True

        self.chose_glory = False
        self.bounty_primed = False

        return True

    def is_good_challenger(self, nart, candidate):
        # Similar to the missionbuilder utility function but a few key differences. Looks for an unfavorable NPC
        # regardless of faction, and doesn't care about the NPC's renown.
        return (
            isinstance(candidate, gears.base.Character) and candidate.combatant and
            nart.camp.is_unfavorable_to_pc(candidate) and candidate not in nart.camp.party
        )

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)

        target = self.elements["_commander"].get_root()
        if not target.is_operational():
            if self.chose_glory:
                for sk in gears.stats.COMBATANT_SKILLS:
                    camp.dole_xp(50,sk)
            if self.bounty_primed:
                bounty_amount = gears.selector.calc_threat_points(self.elements["_commander"].renown,200)//5
                pbge.alert("You earn a bounty of ${:,} for defeating {}.".format(bounty_amount, self.elements["_commander"]))
                camp.credits += bounty_amount

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.choice_ready:
            self.choice_ready = False
            # Allow the PC to decide whether or not to accept the challenge.
            npc = self.elements["_commander"]
            pbge.alert("Without warning, you are confronted by {}.".format(npc))

            mymenu = game.content.ghcutscene.SimpleMonologueMenu("[I_PROPOSE_BATTLE]", npc, camp)

            if npc.renown > camp.renown + 10:
                game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu, "{} is out of our league, but just imagine the glory if we win!".format(npc),
                    self._choose_glory, camp, (gears.personality.Glory,)
                )
            elif npc.renown < camp.renown - 20:
                self.peace_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu, "I don't like the idea of demolishing a lesser pilot like {npc}, but if that's what {npc.gender.subject_pronoun} wants...".format(npc=npc),
                    self._choose_peace, camp, (gears.personality.Peace,)
                )

            if gears.tags.Criminal in npc.get_tags():
                self.police_npc = game.content.ghcutscene.AddTagBasedLancemateMenuItem(
                    mymenu,
                    "There's probably a bounty for {npc}; defeat {npc.gender.object_pronoun} and we might earn a big payday.".format(npc=npc),
                    self._choose_bounty, camp, (gears.tags.Police,)
                )

            mymenu.add_item("Accept the challenge", None)
            mymenu.add_item("Reject the challenge", self.cancel_the_adventure)

            choice = mymenu.query()
            if choice:
                choice(camp)

    def _choose_bounty(self, camp):
        self.police_npc.relationship.reaction_mod += random.randint(1,6)
        self.bounty_primed = True

    def _choose_peace(self, camp: gears.GearHeadCampaign):
        self.peace_npc.relationship.reaction_mod += random.randint(1,10)
        npc = self.elements["_commander"]
        if camp.make_skill_roll(gears.stats.Ego, gears.stats.Negotiation, npc.renown):
            ghcutscene.SimpleMonologueDisplay("[CHANGE_MIND_AND_RETREAT]", npc)

            pbge.alert("Your challengers flee the battlefield.")
            self.elements["_eteam"].retreat(camp)

            camp.check_trigger("ENDCOMBAT")

    def _choose_glory(self, camp):
        self.chose_glory = True

    def cancel_the_adventure(self,camp: gears.GearHeadCampaign):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.end_adventure(camp)


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
#
# Note: This doesn't need to be a road map adventure! As long as you pass an ADVENTURE_GOAL element to the mission,
#   you can call it from any mission and avoiding combat will take the player to the adventure goal.
#

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
                mymenu = pbge.rpgmenu.AlertMenu("You detect hostile mecha on the road ahead. They are still far enough away that you can avoid them if you want to.")
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
                mymenu = pbge.rpgmenu.AlertMenu("You encounter a group of hostile mecha, but manage to remain unseen.")
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
                mymenu = pbge.rpgmenu.AlertMenu("You find tracks belonging to enemy mecha. It would be a simple matter to find an alternate route around them.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[THERE_ARE_ENEMY_TRACKS] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def cancel_the_adventure(self,camp):
        self.adv.cancel_adventure(camp)
        camp.go(self.elements["ADVENTURE_GOAL"])

#   *****************************
#   ***  RWMO_SECURITY_CHECK  ***
#   *****************************
#
# The "enemy faction" isn't necessarily going to attack; instead they're just doing a patrol to keep enemies out.
#

class RWMO_BasicSecurityCheck(Plot):
    LABEL = RWMO_SECURITY_CHECK
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True, backup_seek_func=self.adv.is_good_backup_enemy)
        self.regular_checkpoint = True
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
            if nart.camp.is_unfavorable_to_pc(myfac):
                self.add_sub_plot(nart,"MC_ENEMY_DEVELOPMENT",elements={"NPC":mynpc})
                self.regular_checkpoint = False
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander)
            if nart.camp.is_unfavorable_to_pc(myfac):
                self.add_sub_plot(nart,"MC_NDBCONVERSATION",elements={"NPC":myunit.commander.get_pilot()})
                self.regular_checkpoint = False

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Pass {} Checkpoint".format(myfac),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)

    def _commander_offers(self, camp):
        mylist = list()
        npc = self.elements["_commander"]

        if self.regular_checkpoint:
            mylist.append(Offer(
                "[HALT] Please state your business in {}.".format(self.elements["DEST_SCENE"]),
                ContextTag((context.ATTACK,))
            ))

            mylist.append(Offer(
                "[UNDERSTOOD] You're clear to pass.".format(self.elements["DEST_SCENE"]),
                ContextTag((context.COMBAT_CUSTOM,)), effect=self.cancel_the_adventure,
                data={"reply": "[I_DONT_WANT_TROUBLE]"}
            ))

            mylist.append(Offer(
                "[CHALLENGE]",
                ContextTag((context.COMBAT_CUSTOM,)),
                data={"reply": "[I_DECLARE_WAR]"}
            ))

        return mylist

    def cancel_the_adventure(self, camp):
        self.adv.cancel_adventure(camp)
        camp.go(self.elements["ADVENTURE_GOAL"])

