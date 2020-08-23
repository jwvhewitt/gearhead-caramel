# Character development plots for lancemates.
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
from gears import relationships
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,ghcutscene, dungeonmaker
from . import missionbuilder,dd_customobjectives

class LMPlot(Plot):
    # Contains convenience methods for lancemates.
    def npc_is_ready_for_lancedev(self, camp, npc):
        return (isinstance(npc, gears.base.Character) and npc in camp.party and npc.relationship
                and npc.relationship.can_do_development())

    def t_START(self,camp):
        npc = self.elements["NPC"]
        if npc.is_destroyed() or npc not in camp.party:
            self.end_plot(camp)

    def proper_end_plot(self,camp,improve_react=True):
        self.elements["NPC"].relationship.development_plots += 1
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1,10)
        self.end_plot(camp)

    def proper_non_end(self,camp,improve_react=True):
        # This plot is not ending, but it's entering a sort of torpor phase where we don't want it interfering
        # with other DZD_LANCEDEV plots. For instance: if a plot adds a permanent new location to the world, you
        # might not want to end the plot but you will want to unlock the NPC and whatever else.
        self.elements["NPC"].relationship.development_plots += 1
        self.LABEL = None
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1,10)
        if "NPC" in self.locked_elements:
            self.locked_elements.remove("NPC")


class LMMissionPlot(LMPlot):
    mission_active = False
    mission_seed = None
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_BUILDINGS)
    CASH_REWARD = 150
    EXPERIENCE_REWARD = 150

    def prep_mission(self, camp: gears.GearHeadCampaign):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "{NPC}'s Mission".format(**self.elements),
            (self.elements["METROSCENE"],self.elements["MISSION_GATE"]),
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            rank=camp.renown, objectives=self.MISSION_OBJECTIVES,
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission
        )

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_active and self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def win_mission(self, camp):
        self.proper_end_plot(camp)

    def lose_mission(self, camp):
        self.proper_end_plot(camp)


#   **********************
#   ***  DZD_LANCEDEV  ***
#   **********************
#  Required elements: METRO, METROSCENE, MISSION_GATE

class DDLD_CareerChange(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene)
        self.new_job = self._get_new_job(npc)
        return True

    def _get_new_job(self, npc):
        candidates = list()
        if gears.personality.Peace in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Medic in job.tags and job.name != npc.job.name]
        if gears.personality.Glory in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Media in job.tags and job.name != npc.job.name]
        if gears.personality.Fellowship in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Craftsperson in job.tags and job.name != npc.job.name]
        if gears.personality.Duty in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Military in job.tags and job.name != npc.job.name]
        if gears.personality.Justice in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Academic in job.tags and job.name != npc.job.name]
        if not candidates:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if gears.tags.Adventurer in job.tags and job.name != npc.job.name]
        return random.choice(candidates)

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.job and
                candidate.relationship.expectation == gears.relationships.E_IMPROVER and
                candidate.relationship.attitude == gears.relationships.A_FRIENDLY
            )

    def METROSCENE_ENTER(self,camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("As you enter {METROSCENE}, {NPC}'s phone beeps loudly; {NPC.gender.subject_pronoun} checks the screen and then gives a shout of joy.".format(**self.elements))

        self.started_convo = True

        npc.relationship.attitude = relationships.A_THANKFUL
        ghcutscene.SimpleMonologueDisplay(
            "I passed the test! I told you all that I was going to make a change, and now I have. From this point forward I'm an official certified {}!".format(self.new_job),
            npc.get_root())(camp)

        candidates = [npc2 for npc2 in camp.get_lancemates() if npc2 is not npc]
        if candidates:
            npc2 = random.choice(candidates)
            ghcutscene.SimpleMonologueDisplay(
                "Congratulations, {}!".format(npc),
                npc2.get_root())(camp,False)

        npc.job = self.new_job
        for sk in self.new_job.skills:
            npc.statline[sk] += 1

        for sk,bonus in self.new_job.skill_modifiers.items():
            if bonus > 0:
                npc.statline[sk] += bonus
            elif sk not in npc.statline:
                npc.statline[sk] += 1

        ghcutscene.SimpleMonologueDisplay(
            "Thanks! I wouldn't have been able to do this without your support.",
            npc.get_root())(camp, False)

        self.proper_end_plot(camp)


class DDLD_BeFriendsDoCrimes(LMMissionPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 200
    ENEMY_FACTIONS = (gears.factions.KettelIndustries, gears.factions.RegExCorporation, gears.factions.BioCorp,)
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_THE_MINE)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = random.choice(self.ENEMY_FACTIONS)
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.expectation is None and gears.tags.Criminal in candidate.get_tags()
                and candidate.relationship.role == gears.relationships.R_FRIEND
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} pulls you aside for a private chat.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "There's a processing facility belonging to {} just outside of town, and today they'll be moving some valuable cargo. If we strike fast we can rob them blind.".format(self.elements["ENEMY_FACTION"].name),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] We don't need to tell anyone else what kind of mission this is... They wouldn't understand.",
                (context.CUSTOM,),subject=self,data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "Yeah, I know... old habits die hard, I guess. Let's just keep this conversation between you and me. I'll try to stay on the up and up from here on out.",
                (context.CUSTOM,),subject=self,data={"reply": "No; we're cavaliers, not bandits."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you convinced me to give up on crime", "I helped you to reform", 5,
            (gears.relationships.MEM_Ideological,)
        ))
        self.elements["NPC"].statline[gears.stats.Ego] += 2
        self.proper_end_plot(camp,False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "I'll keep looking out for more opportunities like this.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Scouting] += 2

        self.proper_end_plot(camp)



class DDLD_PureBiznessRelationship(LMMissionPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 200
    ENEMY_FACTIONS = (gears.factions.AegisOverlord, gears.factions.ClanIronwind, gears.factions.KettelIndustries,
                      gears.factions.RegExCorporation, gears.factions.BioCorp, gears.factions.BoneDevils,
                      gears.factions.BladesOfCrihna, gears.factions.AegisOverlord, gears.factions.ClanIronwind)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = random.choice(self.ENEMY_FACTIONS)
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.expectation is None
                    and candidate.relationship.role in (gears.relationships.R_ACQUAINTANCE, None)
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("{NPC}'s phone rings. After a short conversation, {NPC.gender.subject_pronoun} turns to you.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just got a hot tip from [foaf]; there's a mission available right now to fight {} for double standard pay. We could really use that money.".format(self.elements["ENEMY_FACTION"].name),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] I'm receiving the data on my phone now... we can get started any time you want.",
                (context.CUSTOM,),subject=self,data={"reply":"[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "[YOU_ARE_THE_BOSS]",
                (context.CUSTOM,),subject=self,data={"reply":"[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you rejected the mission I suggested", "I didn't accept the mission you suggested", -10,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp,False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "Maybe in the future, I could arrange even more missions like this for us. I should practice that.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Negotiation] += 2

        self.proper_end_plot(camp)


class DDLD_SharingMyInfo(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.rank = npc.renown
        self.started_conversation = False
        self.got_info = False

        # Add the ruin dungeon
        self.dungeon_name = "{} Ruin".format(gears.selector.EARTH_NAMES.gen_word())
        self.dungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], self.dungeon_name,
            gharchitecture.FortressBuilding(),
            self.rank,
            monster_tags=("ROBOT", "SYNTH", "MUTANT", "RUINS"),
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS,)
        )
        d_entrance = pbge.randmaps.rooms.ClosedRoom(7, 7, anchor=pbge.randmaps.anchors.middle)
        self.dungeon.entry_level.contents.append(d_entrance)
        self.dungeon_entrance = ghwaypoints.Exit(
            dest_scene=self.elements["METROSCENE"], dest_entrance=self.elements["MISSION_GATE"],
            anchor=pbge.randmaps.anchors.middle,
        )
        d_entrance.contents.append(self.dungeon_entrance)

        # Add the goal room
        final_room = self.register_element(
            "FINAL_ROOM", pbge.randmaps.rooms.ClosedRoom(9, 9, ),
        )
        self.dungeon.goal_level.contents.append(final_room)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 12).based_on(self),
            elements={
                "ROOM": final_room, "LOCALE": self.dungeon.goal_level,
                "TYPE_TAGS": ("ROBOT", "SYNTH", "MUTANT", "RUINS")
            }
        )
        mycrate = ghwaypoints.Crate(treasure_rank=self.rank+20, treasure_amount=250)
        final_room.contents.append(mycrate)
        myitem = self.register_element(
            "MACGUFFIN", gears.base.Treasure(value=1000000, weight=45, name="Proto-Sculpture",
            desc="A mysterious statue crafted by the original inhabitants of {}.".format(self.dungeon_name))
        )
        mycrate.contents.append(myitem)

        self.got_macguffin = False

        return True

    def GET_MACGUFFIN(self, camp):
        if not self.got_macguffin:
            self.got_macguffin = True
            npc: gears.base.Character = self.elements["NPC"]
            if npc in camp.party:
                ghcutscene.SimpleMonologueDisplay("Oh wow, do you realize what that is? Neither do I but I bet it's worth a fortune!", npc)(camp)
                npc.statline[gears.stats.Knowledge] += 2

    def _is_good_npc(self,nart,candidate):
        if self.npc_is_ready_for_lancedev(nart.camp,candidate):
            return (
                candidate.relationship.attitude == gears.relationships.A_FRIENDLY and
                candidate.relationship.role in (gears.relationships.R_ACQUAINTANCE,None,gears.relationships.R_COLLEAGUE)
                and {gears.tags.Adventurer,gears.tags.Criminal}.intersection(candidate.get_tags())
            )

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.got_info:
            thingmenu.add_item("Go to {}".format(self.dungeon_name), self.go_to_dungeon)

    def go_to_dungeon(self, camp):
        camp.destination, camp.entrance = self.dungeon.entry_level,self.dungeon_entrance

    def t_START(self,camp):
        if not self.got_info:
            super().t_START(camp)

    def METROSCENE_ENTER(self,camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, you notice {} gazing out toward the horizon.".format(camp.scene,npc))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_conversation = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.got_info:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "There's a synth-infested ruin near {METROSCENE} that's supposed to be filled with PreZero artifacts. I've always wanted to go there and try my luck. In fact, I'd love to go there with you.".format(**self.elements),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True
            ))
            if self.rank > camp.renown + 5:
                mylist.append(Offer(
                    "Well, I'm not sure you're ready for that yet, [audience]. It's a dangerous place and I don't want to be the one responsible for getting you killed. But maybe later, we can come back and go treasure hunting.",
                    (context.CUSTOM,),subject=self,data={"reply":"I'd like that too, [audience]."},
                    effect=self._accept_offer
                ))
            else:
                mylist.append(Offer(
                    "[GOOD] I've always wanted a buddy to explore dungeons with. This is going to be fun!",
                    (context.CUSTOM,), subject=self, data={"reply": "I'd like that too, [audience]."},
                    effect=self._accept_offer
                ))
            if npc.get_reaction_score(camp.pc, camp) > 25:
                if self.rank > camp.renown + 5:
                    mylist.append(Offer(
                        "What?! No... Well, maybe. I mean, it's a really dangerous place, it's not a good spot for... You're going to need some training before we can go there.",
                        (context.CUSTOM,), subject=self, data={"reply": "You mean, like, on a date?"},
                        effect=self._flirty_offer
                    ))
                else:
                    mylist.append(Offer(
                        "What?! Yes... I mean no. A dungeon is no place for a first date. But I mean, if you wanted to, maybe we could go to a restaurant or something after we finish looting the place...?",
                        (context.CUSTOM,), subject=self, data={"reply": "You mean, like, on a date?"},
                        effect=self._flirty_offer
                    ))

            mylist.append(Offer(
                "That's too bad. I've always wanted to have an adventure buddy to explore dungeons with, but I guess that's not your style. I'm still glad to be your lancemate.",
                (context.CUSTOM,),subject=self,data={"reply":"No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.got_info = True
        self.elements["NPC"].relationship.role = gears.relationships.R_FRIEND
        self.memo = "{NPC} told you about a ruin outside {METROSCENE} where you can find valuable PreZero artifacts.".format(**self.elements)
        self.proper_non_end(camp)

    def _flirty_offer(self, camp):
        self.got_info = True
        self.elements["NPC"].relationship.role = gears.relationships.R_CRUSH
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you asked me out", "I kind of asked you out", 10, (gears.relationships.MEM_Romantic,)
        ))
        self.memo = "{NPC} told you about a ruin outside {METROSCENE} where you can find valuable PreZero artifacts.".format(**self.elements)
        self.proper_non_end(camp)

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.role = gears.relationships.R_FRIEND
        self.end_plot(camp, True)


class DDLD_SortingDuel(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    def custom_init( self, nart ):
        npc = self.seek_element(nart,"NPC",self._is_good_npc,scope=nart.camp.scene,lock=True)
        self.started_conversation = False
        self.accepted_duel = False
        self.duel = missionbuilder.BuildAMissionSeed(
            nart.camp, "{}'s Duel".format(npc), (self.elements["METROSCENE"],self.elements["MISSION_GATE"]),
            rank = npc.renown, objectives = [dd_customobjectives.DDBAMO_DUEL_LANCEMATE],solo_mission=True,
            custom_elements={"LMNPC":npc},experience_reward=200,salvage_reward=False
        )
        return True

    def _is_good_npc(self,nart,candidate):
        if self.npc_is_ready_for_lancedev(nart.camp,candidate):
            return candidate.relationship.expectation == gears.relationships.E_PROFESSIONAL and not candidate.relationship.attitude

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.accepted_duel:
            thingmenu.add_item("Travel into the deadzone to have a practice match with {}".format(self.elements["NPC"]), self.duel)

    def t_START(self,camp):
        npc = self.elements["NPC"]
        if not self.accepted_duel:
            super().t_START(camp)
        elif npc.is_destroyed():
            self.end_plot(camp)
        if self.duel.is_completed():
            if self.duel.is_won():
                npc.relationship.attitude = gears.relationships.A_JUNIOR
                ghcutscene.SimpleMonologueDisplay("Your skills are incredible. It seems I have a lot to learn from you.",npc)(camp)
            else:
                npc.relationship.attitude = gears.relationships.A_SENIOR
                ghcutscene.SimpleMonologueDisplay("You show great potential, but you aren't quite there yet. Maybe someday we can have a rematch.", npc)(camp)
            self.proper_end_plot(camp)

    def t_UPDATE(self,camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, you notice {} giving you a quizzical look.".format(camp.scene,npc))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self,camp):
        mylist = list()
        if not self.accepted_duel:
            mylist.append(Offer(
                "We've been traveling together for a while, but I still haven't figured out how you rank. [CAN_I_ASK_A_QUESTION]",
                (context.HELLO,context.QUERY),
            ))
            mylist.append(Offer(
                "I'm curious about how your combat skills compare to mine. How would you like to go out into the dead zone, find a nice uninhabited place, and have a friendly little practice duel?",
                (context.QUERY,),subject=self,subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] Whenever you're ready, we can head out of town and find an appropriate place.",
                (context.ANSWER,),subject=self,data={"reply":"[ACCEPT_CHALLENGE]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "That's very disappointing. I never imagined you to be a coward, but as I said earlier I don't quite have you figured out yet...",
                (context.ANSWER,),subject=self,data={"reply":"No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.accepted_duel = True

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_RESENT
        self.proper_end_plot(camp,False)


class DDLD_JuniorQuestions(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    def custom_init( self, nart ):
        npc = self.seek_element(nart,"NPC",self._is_good_npc,scope=nart.camp.scene,lock=True)
        self.started_conversation = False
        return True

    def _is_good_npc(self,nart,candidate):
        if self.npc_is_ready_for_lancedev(nart.camp,candidate):
            return not candidate.relationship.expectation and candidate.renown < 20 and candidate.relationship.attitude in (relationships.A_JUNIOR,None)

    def t_UPDATE(self,camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, {} pulls you aside for a conversation.".format(camp.scene,npc))
            npc.relationship.attitude = relationships.A_JUNIOR
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]",
            (context.HELLO,context.QUERY),
        ))
        mylist.append(Offer(
            "I'm pretty new at this cavalier business, and I don't have nearly as much sense for it as you do. What do I need to do to become a real cavalier?",
            (context.QUERY,),subject=self,subject_start=True
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] Yes, I see now that the purpose of a cavalier is to earn the fanciest toys available. I won't forget your advice!",
            (context.ANSWER,),subject=self,data={"reply":"Just keep finding missions and keep getting paid. Then buy a bigger robot."},
            effect=self._merc_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] To be a cavalier is a journey, not a destination. I promise that I will keep doing my best!",
            (context.ANSWER,),subject=self,data={"reply":"Keep practicing, keep striving, and each day you move closer to the best pilot you can be."},
            effect=self._pro_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] With gigantic megaweapons come gigantic responsibilities... I see that now. I promise I won't let you down!",
            (context.ANSWER,),subject=self,data={"reply":"We do this so that we can help people. If you make life better for one person, you've succeeded."},
            effect=self._help_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] In order to fight for great justice, I must first conquer my own inner demons. I promise not to forget your ephemeral wisdom!",
            (context.ANSWER,),subject=self,data={"reply":"There are a lot of bad things in this world; just make sure you don't become one of them."},
            effect=self._just_answer
        ))
        mylist.append(Offer(
            "Thanks, I guess? I was hoping that you'd be able to give me some great insight, but it seems we're all working this out for ourselves. At least I feel a bit more confident now.",
            (context.ANSWER,),subject=self,data={"reply":"[I_DONT_KNOW] And besides, you've proven yourself as a lancemate already."},
            effect=self._fel_answer
        ))
        return mylist

    def _merc_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        if gears.personality.Glory in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Vitality] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Glory)
        self.proper_end_plot(camp)

    def _pro_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_PROFESSIONAL
        if gears.personality.Duty in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Concentration] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Duty)
        self.proper_end_plot(camp)

    def _help_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_GREATERGOOD
        if gears.personality.Peace in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Athletics] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Peace)
        self.proper_end_plot(camp)

    def _just_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER
        if gears.personality.Justice in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.MechaPiloting] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Justice)
        self.proper_end_plot(camp)

    def _fel_answer(self,camp):
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY
        if gears.personality.Fellowship in self.elements["NPC"].personality:
            self.elements["NPC"].dole_experience(200,camp.pc.TOTAL_XP)
            camp.pc.dole_experience(200,camp.pc.TOTAL_XP)
        else:
            self.elements["NPC"].personality.add(gears.personality.Fellowship)
        self.proper_end_plot(camp)

