from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility, ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder, rwme_objectives
from gears import champions

DDBAMO_DUEL_LANCEMATE = "DDBAMO_DuelLancemate"  # Custom Element: LMNPC
DDBAMO_CHAMPION_1V1 = "DDBAMO_Champion1v1"
DDBAMO_ENCOUNTER_ZOMBOTS = "DDBAMO_EncounterZombots"
DDBAMO_INVESTIGATE_METEOR = "DDBAMO_InvestigateMeteor"
DDBAMO_INVESTIGATE_REFUGEE_CAMP = "DDBAMO_INVESTIGATE_REFUGEE_CAMP"
DDBAMO_KERBEROS = "DDBAMO_KERBEROS"
DDBAMO_MAYBE_AVOID_FIGHT = rwme_objectives.RWMO_MAYBE_AVOID_FIGHT
DDBAMO_MEET_CETUS = "DDBAMO_CETUS1"
DDBAMO_FIGHT_CETUS = "DDBAMO_CETUS2"

DDBAMO_ONAWA_MISSION = "DDBAMO_ONAWA_MISSION"


class GodsBlood(pbge.scenes.waypoints.Waypoint):
    name = "Mystery Ooze"
    TILE = pbge.scenes.Tile(ghterrain.ToxicSludge, None, None)

    def combat_bump(self, camp, pc):
        # Send a BUMP trigger.
        camp.check_trigger("BUMP", self)


class DDBAMO_BloodFromASynth(Plot):
    LABEL = DDBAMO_ONAWA_MISSION
    active = True
    scope = "LOCALE"

    ENEMY_FACTIONS = (gears.factions.AegisOverlord, gears.factions.BladesOfCrihna)

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom: pbge.randmaps.rooms.Room = self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(10, 10),
                                                                 dident="LOCALE")
        myfac = self.register_element("enemy_faction", random.choice(self.ENEMY_FACTIONS))
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.register_element("_commander", nart.camp.cast_a_combatant(myfac, self.rank + 20, myplot=self),
                                      lock=True)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, myfac, myscene.environment, add_commander=False)
        team2.contents += myunit.mecha_list

        mywaypoint = self.register_element("OOZE", GodsBlood(desc="You stand before a pool of mysterious ooze."),
                                           dident="ROOM")

        self.obj = adventureseed.MissionObjective("Investigate the battlefield",
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False
        self.sample_collected = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            pbge.alert(
                "As you approach the battle site, you are confronted by a hostile mecha team who are also investigating the situation.")
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.combat_entered = True

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[WHATAREYOUDOINGHERE] This area and everything in it has been claimed by {enemy_faction}.".format(
                **self.elements),
            context=ContextTag([context.ATTACK, ])))
        mylist.append(Offer("[WITHDRAW]", effect=self._player_retreat, context=ContextTag([context.WITHDRAW, ])))
        mylist.append(Offer("[CHALLENGE]", context=ContextTag([context.CHALLENGE, ])))
        ghdialogue.SkillBasedPartyReply(
            Offer(
                "Wait, this is just regular radioactive waste?! Forget you saw us here! Alright, team, move out... this is another dead end.",
                context=ContextTag([context.COMBAT_CUSTOM]),
                data={
                    "reply": "You came all the way to Earth to fight over a puddle of radioactive waste? You can get all you want in the deadzone."},
                effect=self._enemies_retreat
            ), camp, mylist, gears.stats.Charm, gears.stats.Biotechnology, rank=self.rank,
            difficulty=gears.stats.DIFFICULTY_HARD
        )
        return mylist

    def _player_retreat(self, camp: gears.GearHeadCampaign):
        camp.scene.player_team.retreat(camp)

    def _enemies_retreat(self, camp):
        myteam = self.elements["_eteam"]
        myteam.retreat(camp)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1 or self.sample_collected:
            self.obj.win(camp)
            if not self.combat_finished:
                pbge.alert(
                    "You have secured the battle zone. There is a pool of unknown fluid that might provide some clues about the mysterious flying object.")
                self.combat_finished = True
        else:
            self.obj.failed = True


    def OOZE_BUMP(self, camp):
        if not self.sample_collected:
            self.sample_collected = True
            pbge.alert("You collect a sample of the mysterious ooze.")
            self.obj.win(camp)
        else:
            pbge.alert("You don't need more of this stuff, whatever it is.")


class DDBAMO_PracticeDuel(Plot):
    LABEL = DDBAMO_DUEL_LANCEMATE
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]

        self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(15, 15, anchor=pbge.randmaps.anchors.middle),
                              dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.elements["LMNPC"]
        self.locked_elements.add("LMNPC")
        self.party_member = mynpc in nart.camp.party
        if self.party_member:
            plotutility.AutoLeaver(mynpc)(nart.camp)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2, allow_death=False)

        self.obj = adventureseed.MissionObjective("Defeat {}".format(mynpc), missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["LMNPC"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def LMNPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
        else:
            self.obj.failed = True
        if self.party_member:
            plotutility.AutoJoiner(self.elements["LMNPC"])(camp)
        # for pc in camp.party:
        #    pc.restore_all()


class DDBAMO_ChampionDuel(Plot):
    LABEL = DDBAMO_CHAMPION_1V1
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myscene.attributes.add(gears.tags.SCENE_SOLO)

        self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        fac = self.elements["ENEMY_FACTION"]

        npc = self.seek_element(nart, "_champion", self.adv.is_good_enemy_npc, must_find=False, lock=True)
        if npc:
            plotutility.CharacterMover(nart.camp, self, npc, myscene, team2)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": npc})
        else:
            mek = gears.selector.generate_ace(self.rank, fac, myscene.environment)
            npc = mek.get_pilot()
            self.register_element("_champion", npc)
            team2.contents.append(mek)
            champions.upgrade_to_champion(mek)
            self.add_sub_plot(nart, "MC_DUEL_DEVELOPMENT", elements={"NPC": npc})

        self.obj = adventureseed.MissionObjective("Defeat the {}'s champion {}".format(fac, npc),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.intro_ready = False
            npc = self.elements["_champion"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class DDBAMO_EncounterZombots(Plot):
    LABEL = DDBAMO_ENCOUNTER_ZOMBOTS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        self.intro_ready = True
        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if self.intro_ready and not camp.campdata.get(DDBAMO_ENCOUNTER_ZOMBOTS, False):
            self.intro_ready = False
            camp.campdata[DDBAMO_ENCOUNTER_ZOMBOTS] = True
            pbge.alert(
                "The road ahead is blocked by hostile mecha. Ominously, your sensors cannot detect any energy readings from them, though they are clearly moving.")


class DDBAMO_HelpFromTheStars(Plot):
    LABEL = DDBAMO_INVESTIGATE_METEOR
    active = True
    scope = "LOCALE"
    UNIQUE = True

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.register_element("NPC", gears.selector.random_character(rank=self.rank + 10,
                                                                             job=gears.jobs.ALL_JOBS["Knight"],
                                                                             faction=gears.factions.TheSilverKnights,
                                                                             combatant=True))
        mek = plotutility.AutoJoiner.get_mecha_for_character(mynpc, True)
        mek.load_pilot(mynpc)
        self.register_element("SURVIVOR", mek, dident="_ateam")

        self.obj = adventureseed.MissionObjective("Investigate the meteor", missionbuilder.MAIN_OBJECTIVE_VALUE * 2,
                                                  can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_left = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["NPC"]
            pbge.alert(
                "As you approach the supposed crash site, the true nature of the falling star becomes clear: it's a lone mecha, having descended to Earth with an atmospheric drop chute. And from the look of things {}'s going to need your help.".format(
                    npc.gender.subject_pronoun))
            self.eteam_activated = True
            if not self.pilot_left:
                ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.HELLO_STARTER)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def NPC_offers(self, camp):
        mylist = list()
        if self.eteam_defeated:
            mylist.append(
                Offer("[THANKS_FOR_MECHA_COMBAT_HELP] It would be a pleasure to fight at your side again someday.",
                      dead_end=True, context=ContextTag([ghdialogue.context.HELLO, ]),
                      effect=self.pilot_leaves_combat))
        else:
            myoffer = Offer(
                "[HELP_ME_VS_MECHA_COMBAT] I've been tracking weapons smugglers in the L5 region, and have traced their wares to {}.".format(
                    self.elements["ENEMY_FACTION"]),
                dead_end=True, context=ContextTag([ghdialogue.context.HELLO, ]))
            mylist.append(myoffer)
        return mylist

    def pilot_leaves_combat(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.reaction_mod += 10
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        mek = self.elements["SURVIVOR"]
        camp.scene.contents.remove(mek)
        mek.free_pilots()
        npc.place(self.elements["METROSCENE"])

        self.pilot_left = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_left:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                npc = self.elements["NPC"]
                ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.HELLO_STARTER)


class DDBAMO_ChampionsFromTheStars(Plot):
    LABEL = DDBAMO_INVESTIGATE_METEOR
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(10, 10), dident="LOCALE")
        myfac = self.elements.get("ENEMY_FACTION")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        for i in range(4):
            mek = gears.selector.generate_ace(self.rank, myfac, myscene.environment)
            champions.upgrade_to_champion(mek)
            team2.contents.append(mek)

            if i == 0:
                self.register_element("_commander", mek.get_pilot())

        self.obj = adventureseed.MissionObjective("Investigate the meteor", missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            pbge.alert(
                "As you approach the supposed crash site, it becomes clear what the meteor actually was: it's a cargo pod containing a few souped-up mecha. And the recipients of the delivery have already claimed it...")
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.combat_entered = True

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[WHATAREYOUDOINGHERE] These mecha are ours."
                            , context=ContextTag([context.ATTACK])
                            ))
        mylist.append(Offer("[CHALLENGE]"
                            , context=ContextTag([context.CHALLENGE])
                            ))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
            if not self.combat_finished:
                pbge.alert("You stopped the delivery of modified mecha.")
                self.combat_finished = True


class DDBAMO_CargoFromTheStars(Plot):
    LABEL = DDBAMO_INVESTIGATE_METEOR
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(10, 10), dident="LOCALE")
        myfac = self.elements.get("ENEMY_FACTION")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.seek_element(nart, "_commander", self._npc_is_good, must_find=False, lock=True)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander)

        team2.contents += myunit.mecha_list

        team3 = self.register_element("_cargoteam", teams.Team(), dident="ROOM")
        team3.contents += game.content.plotutility.CargoContainer.generate_cargo_fleet(self.rank)
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_containers = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Investigate the meteor", missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and candidate.faction == \
            self.elements["ENEMY_FACTION"] and candidate not in nart.camp.party

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            pbge.alert(
                "As you approach the supposed crash site, it becomes clear what the meteor actually was: a cargo pod dropped from low orbit. It also becomes clear who the cargo belongs to...")
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.combat_entered = True

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[WHATAREYOUDOINGHERE] This cargo is ours.",
                            context=ContextTag([context.ATTACK, ])))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        cargoteam = self.elements["_cargoteam"]
        if len(cargoteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     cargoteam.get_members_in_play(camp)])) // self.starting_number_of_containers)
            if not self.combat_finished:
                pbge.alert("You have captured the cargo.")
                self.combat_finished = True


class BAM_InvestigateRefugeeCamp(Plot):
    LABEL = DDBAMO_INVESTIGATE_REFUGEE_CAMP
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        enemy_room = self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=True)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Investigate refugee camp", adventureseed.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())

        self.intro_ready = True
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.intro_ready = False
            self.obj.win(camp, 100)


class DDBAMO_FightKerberos(Plot):
    LABEL = DDBAMO_KERBEROS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = [gears.selector.get_design_by_full_name("DZD Kerberos") for t in range(4)]
        team2.contents += myunit

        self.obj = adventureseed.MissionObjective("Battle Kerberos", adventureseed.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        return True

    def t_COMBATROUND(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]
        heads = myteam.get_members_in_play(camp)
        num_heads = len(heads)

        # See if a new head is going to pop up.
        if num_heads > 0 and num_heads < 4 and random.randint(1, 2) == 1:
            mymon = gears.selector.get_design_by_full_name("DZD Kerberos")
            camp.scene.deploy_team([mymon, ], myteam)
            pbge.my_state.view.play_anims(gears.geffects.SmokePoof(pos=mymon.pos))
            camp.fight.activate_foe(mymon)
            heads.append(mymon)

        # See if a head will kidnap anyone.
        if not camp.campdata["KERBEROS_DUNGEON_OPEN"]:
            candidates = list()
            for pc in camp.get_active_party():
                draggers = [h for h in heads if camp.scene.distance(pc.pos, h.pos) <= 1]
                if len(draggers) > 1:
                    candidates.append([pc, draggers])
            if candidates:
                pc, draggers = random.choice(candidates)
                pilot = pc.get_pilot()
                is_pc = pilot == camp.pc
                if is_pc:
                    pbge.alert(
                        "Suddenly, the monster's heads wrap around your {} and begin to drag you underground...".format(
                            pc))
                else:
                    pbge.alert(
                        "Suddenly, the monster's heads wrap around {} and begin to drag {} {} underground.".format(
                            pilot, pilot.gender.possessive_determiner, pc))
                pbge.my_state.view.play_anims(gears.geffects.SmokePoof(pos=pc.pos),
                                              *[gears.geffects.SmokePoof(pos=h.pos) for h in draggers])
                for h in draggers:
                    camp.scene.contents.remove(h)

                camp.campdata["KERBEROS_GRAB_FUN"](camp, pc)
                leftovers = [h for h in heads if h not in draggers]
                if leftovers:
                    pbge.my_state.view.play_anims(*[gears.geffects.SmokePoof(pos=h.pos) for h in leftovers])
                    for h in leftovers:
                        camp.scene.contents.remove(h)
                self.adv.cancel_adventure(camp)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class DDBAM_FightCetusFirstTime(Plot):
    LABEL = DDBAMO_MEET_CETUS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        self.cetus: gears.base.Monster = gears.selector.get_design_by_full_name("DZD Cetus")
        self.cetus.never_show_die = True
        team2.contents.append(self.cetus)

        self.obj = adventureseed.MissionObjective("Battle Cetus", adventureseed.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if self.intro_ready:
            if camp.pc.has_badge("Cetus Slayer"):
                pass
            else:
                pass
            self.intro_ready = False

    def t_COMBATLOOP(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]
        if self.cetus.current_health < (self.cetus.max_health // 2) or not self.cetus.is_operational():
            self.cetus.restore_all()
            pbge.alert("The eye of Cetus glows brightly for a moment, and then unleashes a wave of energy.")
            pbge.my_state.view.play_anims(gears.geffects.BiotechnologyAnim(pos=self.cetus.pos))
            my_invo = pbge.effects.Invocation(
                fx=gears.geffects.DoDamage(3, 6, anim=gears.geffects.DeathWaveAnim,
                                           scale=gears.scale.MechaScale,
                                           is_brutal=True),
                area=pbge.scenes.targetarea.SelfCentered(radius=5, delay_from=-1, exclude_middle=True))
            pbge.my_state.view.anim_list.append(gears.geffects.InvokeDeathWaveAnim(pos=self.cetus.pos))
            my_invo.invoke(camp, self.cetus, [self.cetus.pos, ], pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence()
            pbge.alert("Cetus rockets into the air and quickly disappears from sight.")
            pbge.my_state.view.play_anims(gears.geffects.SmokePoof(pos=self.cetus.pos),
                                          pbge.scenes.animobs.BlastOffAnim(model=self.cetus))
            camp.scene.contents.remove(self.cetus)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class DDBAM_FightCetusNextTime(Plot):
    LABEL = DDBAMO_FIGHT_CETUS
    active = True
    scope = "LOCALE"
    ALLIANCES_NEEDED = 3

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        self.cetus: gears.base.Monster = gears.selector.get_design_by_full_name("DZD Cetus")
        self.cetus.never_show_die = True
        team2.contents.append(self.cetus)

        self.obj = adventureseed.MissionObjective("Battle Cetus", adventureseed.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.regen_count = 0

        team3 = self.register_element("_ateam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        self.allied_mecha = gears.selector.RandomMechaUnit(self.rank, 500, gears.factions.DeadzoneFederation,
                                                           myscene.environment).mecha_list

        self.intro_ready = True

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if self.intro_ready:
            if camp.pc.has_badge("Cetus Slayer"):
                pass
            else:
                pass
            self.intro_ready = False

    def t_COMBATLOOP(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]
        if self.cetus.current_health < (self.cetus.max_health // 2) or not self.cetus.is_operational():
            self.regen_count += 1
            self.cetus.restore_all()
            pbge.my_state.view.play_anims(gears.geffects.BiotechnologyAnim(pos=self.cetus.pos))
            my_invo = pbge.effects.Invocation(
                fx=gears.geffects.DoDamage(3, 6, anim=gears.geffects.DeathWaveAnim,
                                           scale=gears.scale.MechaScale,
                                           is_brutal=True),
                area=pbge.scenes.targetarea.SelfCentered(radius=4 - self.regen_count, delay_from=-1,
                                                         exclude_middle=True))
            pbge.my_state.view.anim_list.append(gears.geffects.InvokeDeathWaveAnim(pos=self.cetus.pos))
            my_invo.invoke(camp, self.cetus, [self.cetus.pos, ], pbge.my_state.view.anim_list)
            pbge.my_state.view.handle_anim_sequence()

            if self.regen_count > 1 and not self._has_an_advantage(camp):
                pbge.alert("Once again, Cetus rockets into the air and quickly disappears from sight.")
                pbge.my_state.view.play_anims(gears.geffects.SmokePoof(pos=self.cetus.pos),
                                              pbge.scenes.animobs.BlastOffAnim(model=self.cetus))
                camp.scene.contents.remove(self.cetus)
            elif self.regen_count > 2:
                if camp.campdata["DZDCVAR_NUM_ALLIANCES"] >= self.ALLIANCES_NEEDED:
                    pbge.alert(
                        "As Cetus regenerates again, your allies from across the dead zone arrive at the battlefield.")
                    pc = camp.pc.get_root()
                    camp.scene.deploy_team(self.allied_mecha, self.elements["_ateam"])
                    pbge.my_state.view.play_anims(*[gears.geffects.SmokePoof(pos=h.pos) for h in self.allied_mecha])
                    SimpleMonologueDisplay(
                        "You can't win, Cetus. There are many of us, and only one of you. This is our home. Go back to the deep wasteland and find your own home.",
                        pc)(camp)
                    pbge.alert(
                        "The biomonster appears to consider your words. Its titanic eye scans all of the mecha in attendance.")
                    pbge.alert("Cetus rockets into the sky and flies to the northwest, away from {METROSCENE}.".format(
                        **self.elements))
                    pbge.my_state.view.play_anims(gears.geffects.SmokePoof(pos=self.cetus.pos),
                                                  pbge.scenes.animobs.BlastOffAnim(model=self.cetus))
                    camp.scene.contents.remove(self.cetus)
                    camp.scene.player_team.retreat(camp)
                else:
                    pbge.alert(
                        "This last regeneration seems to have left Cetus dazed. You contact The Voice of Iijima with your current coordinates.")
                    pbge.alert("Your lance makes a hasty withdrawl as hypervelocity missiles streak overhead.")
                    camp.scene.player_team.retreat(camp)
                    my_invo = pbge.effects.Invocation(
                        fx=gears.geffects.DoDamage(20, 8, anim=gears.geffects.SuperBoom,
                                                   scale=gears.scale.MechaScale,
                                                   is_brutal=True),
                        area=pbge.scenes.targetarea.SelfCentered(radius=9, delay_from=-1))
                    my_invo.invoke(camp, self.cetus, [self.cetus.pos, ], pbge.my_state.view.anim_list)
                    pbge.my_state.view.handle_anim_sequence()
                    camp.scene.contents.remove(self.cetus)

    def _has_an_advantage(self, camp):
        # Return True if the PC has obtained one of the advantages that will enable Cetus to be defeated.
        return camp.campdata.get("DZDCVAR_YES_TO_TDF") or camp.campdata[
            "DZDCVAR_NUM_ALLIANCES"] >= self.ALLIANCES_NEEDED

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            if self._has_an_advantage(camp):
                self.obj.win(camp, 100)
            else:
                self.obj.failed = True
