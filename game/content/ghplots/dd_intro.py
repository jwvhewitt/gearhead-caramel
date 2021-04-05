import game.content.plotutility
from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,backstory
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from . import missionbuilder


class DZDIntro_GetInTheMekShimli(Plot):
    # Start of the DZD Intro. Meet the sheriff of the dead zone town you're protecting. Go into battle.
    LABEL = "DZD_INTRO"
    active = True
    scope = True
    MISSION_LABEL = "DZD_INTRO_MISSION"
    MISSION_ELEMENTS = {}
    DEBRIEFING_ELEMENTS = {
        "DEBRIEFING_HELLO": "Defending {DZ_TOWN_NAME} by ourselves isn't working; there's too much ground to cover and not enough of us to do it. Plus, now we have to deal with a ransacked powerplant. Who knows if it can even be fixed?",
        "DEBRIEFING_MISSION": "I'd like for you to head to Wujung. Hire some lancemates. Find someone who can help us with our energy problems. Then come back here and we'll see if we can put a permanent stop to those raiders."
    }
    @classmethod
    def matches( self, pstate: pbge.plots.PlotState ):
        """Returns True if this plot matches the current plot state."""
        return not pstate.adv.world.pc.has_badge("Criminal")

    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        self.elements["DZ_TOWN_NAME"] = self.generate_town_name()

        myscene = gears.GearHeadScene(
            15,15,"{} Mecha Hangar".format(self.elements["DZ_TOWN_NAME"]),player_team=team1,
            scale=gears.scale.HumanScale,civilian_team=team2,attributes=(gears.personality.DeadZone,),is_metro=True,
            exploration_music='A wintertale.ogg', combat_music='Chronos.ogg'
        )
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.IndustrialBuilding(floor_terrain=ghterrain.GrateFloor))
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        # Start a new adventure for this plot and its children- the intro will be disposed of when it's finished.
        self.adv = pbge.plots.Adventure(world=myscene)

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.ClosedRoom(10,7),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")
        mychute = self.register_element("CHUTE",ghwaypoints.BoardingChute(plot_locked=True),dident="_EROOM")
        myroom.contents.append(ghwaypoints.ClosedBoardingChute())
        myroom.contents.append(ghwaypoints.VentFan())

        npc = self.register_element("SHERIFF",
                            gears.selector.random_character(45, local_tags=self.elements["LOCALE"].attributes,
                                                            job=gears.jobs.ALL_JOBS["Sheriff"]))
        npc.place(myscene, team=team2)

        self.register_element("MISSION_RETURN", (myscene,myent))

        # Request the intro mission and debriefing.
        self.add_sub_plot(nart, self.MISSION_LABEL, ident="MISSION", elements=self.MISSION_ELEMENTS)
        self.add_sub_plot(nart,"DZD_MISSION_DEBRIEFING", ident="DEBRIEFING", elements=self.DEBRIEFING_ELEMENTS)

        # Add an egg lancemate, if possible.
        self.add_sub_plot(nart, "ADD_INSTANT_EGG_LANCEMATE", necessary=False)

        # Attempt to load the test mission.
        mytest = self.add_sub_plot(nart,"DZRE_TEST",spstate=pbge.plots.PlotState(rank=1,elements={"METRO":myscene.metrodat,"MISSION_GATE":mychute,"FACTION":game.content.plotutility.RandomBanditCircle(nart.camp),"DZREPR_MISSION_WINS":0}).based_on(self),necessary=False)

        if mytest:
            print("Loaded test!")
            mytest.mission_active = True

        self.started_the_intro = False
        self._tutorial_on = False

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","{} Village","New {}", "{}'s End", "{}", "Mount {}",
                          "{} Hamlet", "Castle {}", "Nova {}", "{} Ruins", "Old {}", "{} Haven", "{} Spire")
    def generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            # Make sure the PC has a mecha.
            mek = camp.get_pc_mecha(camp.pc)
            if not mek:
                mek = gears.selector.MechaShoppingList.generate_single_mecha(camp.pc.renown,None,env=gears.tags.GroundEnv)
                camp.assign_pilot_to_mecha(camp.pc,mek)
                camp.party.append(mek)

            pbge.alert("You have spent the past few weeks in the deadzone community {}, helping the sheriff {} defend the town against raiders. Things have not been going well.".format(self.elements["DZ_TOWN_NAME"], self.elements["SHERIFF"]))

            npc = self.elements["SHERIFF"]
            npc.relationship = gears.relationships.Relationship(random.randint(1,20))
            while npc.get_reaction_score(camp.pc,camp) < 20:
                npc.relationship.reaction_mod += random.randint(1,50)
            self._did_first_reply = False
            ghdialogue.start_conversation(camp,camp.pc,npc)

            self.started_the_intro = True

    def _choose_friendly_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.role = gears.relationships.R_COLLEAGUE
        npc.relationship.attitude = gears.relationships.A_FRIENDLY
        missionbuilder.NewMissionNotification("Protect the Powerplant")

    def _choose_professional_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.role = gears.relationships.R_COLLEAGUE
        npc.relationship.attitude = gears.relationships.A_THANKFUL
        missionbuilder.NewMissionNotification("Protect the Powerplant")

    def _choose_flirty_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.role = gears.relationships.R_CRUSH
        npc.relationship.attitude = gears.relationships.A_FRIENDLY
        missionbuilder.NewMissionNotification("Protect the Powerplant")

    def _activate_tutorial(self,camp):
        self._tutorial_on = True

    def _deactivate_tutorial(self,camp):
        self._tutorial_on = False

    def SHERIFF_offers(self,camp):
        mylist = list()

        if camp.scene is self.elements["LOCALE"]:
            yes_tutorial = Offer(
                "Alright. When we get to the field, I'll give you a brief tutorial. You can get in your mecha by using the boarding chute over there.",
                dead_end=True, effect=self._activate_tutorial,
            )
            no_tutorial = Offer(
                "Understood. You can get in your mecha by using the boarding chute over there.",
                dead_end=True, effect=self._deactivate_tutorial,
            )

            if not self._did_first_reply:
                myhello = Offer(
                        "We just got an alarm from the power station- it's under attack. Are you ready to suit up and roll out?",
                        context=ContextTag([context.HELLO]), dead_end=True,
                )
                myfriend = Offer(
                    "[GOOD] You've been a true friend to {}, and to me personally. One more question: Do you want me to walk you through the new mecha control upgrade?".format(self.elements["DZ_TOWN_NAME"]),
                    dead_end=True, effect=self._choose_friendly_reply
                )
                mypro = Offer(
                    "I would have had a hard time defending {} without a pilot like you on our side. One question before we go: Do you want me to walk you through the new mecha control upgrade?".format(self.elements["DZ_TOWN_NAME"]),
                    dead_end=True, effect=self._choose_professional_reply
                )
                myflirt = Offer(
                    "And I'd love to take you up on that, but first we need to save {}. One question before we go: Do you want me to walk you through the new mecha control upgrade?".format(self.elements["DZ_TOWN_NAME"]),
                    dead_end=True, effect=self._choose_flirty_reply
                )

                myhello.replies.append(
                    Reply(
                        msg="[IWOULDLOVETO]",destination=myfriend,
                    )
                )
                myhello.replies.append(
                    Reply(
                        msg="[LETS_START_MECHA_MISSION]",destination=mypro,
                    )
                )
                myhello.replies.append(
                    Reply(
                        msg="[THATSUCKS] I was hoping to ask you out today.",destination=myflirt,
                    )
                )
                for rep in myhello.replies:
                    off2 = rep.destination
                    off2.replies.append(
                        Reply(
                            msg="[YESPLEASE]", destination=yes_tutorial
                        )
                    )
                    off2.replies.append(
                        Reply(
                            msg="[NOTHANKYOU]", destination=no_tutorial
                        )
                    )

                mylist.append(myhello)
            else:
                myhello = Offer(
                        "Time to go defend the power station. Do you want me to walk you through the new mecha control upgrade when we get there?",
                        context=ContextTag([context.HELLO]), dead_end=True,
                )
                myhello.replies.append(
                    Reply(
                        msg="[YESPLEASE]", destination=yes_tutorial
                    )
                )
                myhello.replies.append(
                    Reply(
                        msg="[NOTHANKYOU]", destination=no_tutorial
                    )
                )
                mylist.append(myhello)

        return mylist

    def _start_mission(self, camp):
        game.content.plotutility.AutoJoiner(self.elements["SHERIFF"])(camp)
        self.subplots["MISSION"].start_mission(camp,self._tutorial_on)

    def MISSION_END(self, camp):
        self.active = False
        self.subplots["DEBRIEFING"].activate(camp)

    def CHUTE_menu(self, camp, thingmenu):
        thingmenu.desc = "This boarding chute leads to\n your {}.".format(camp.get_pc_mecha(camp.pc).get_full_name())
        thingmenu.add_item("Board mecha",self._start_mission)
        if pbge.util.config.getboolean( "GENERAL", "dev_mode_on"):
            thingmenu.add_item("Don't panic and go to Wujung",self._skip_first_mission)

    def _skip_first_mission(self,camp):
        self.adv.end_adventure(camp)


class DZDIntro_NotSoSmoothCriminal(DZDIntro_GetInTheMekShimli):
    # Alternate intro for Criminal reputation.
    LABEL = "DZD_INTRO"
    active = True
    scope = True

    MISSION_LABEL = "DZD_KETTEL_MISSION"

    MISSION_ELEMENTS = {"ENEMY_FACTION": gears.factions.KettelIndustries}
    DEBRIEFING_ELEMENTS = {
        "DEBRIEFING_HELLO": "I know this isn't entirely your fault; those corporations would never dare strike a greenzone town the way they treat us. Still, I want you to know, I blame you for the destruction of the powerplant.",
        "DEBRIEFING_MISSION": "Head to Wujung and find someone who can build us a new generator. If you can fix this mess I'll consider all the issues between us settled."
    }


    @classmethod
    def matches( self, pstate: pbge.plots.PlotState ):
        """Returns True if this plot matches the current plot state."""
        return pstate.adv.world.pc.has_badge("Criminal")

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            # Make sure the PC has a mecha.
            mek = camp.get_pc_mecha(camp.pc)
            if not mek:
                mek = gears.selector.MechaShoppingList.generate_single_mecha(camp.pc.renown,gears.factions.BoneDevils,env=gears.tags.GroundEnv)
                camp.assign_pilot_to_mecha(camp.pc,mek)
                camp.party.append(mek)

            pbge.alert("You have spent the past few weeks raiding corporate convoys near the deadzone community {DZ_TOWN_NAME}. The local sheriff, {SHERIFF}, doesn't seem too happy about your exploits but at least {SHERIFF.gender.subject_pronoun} has left you alone... until now.".format(**self.elements))

            npc = self.elements["SHERIFF"]
            npc.relationship = gears.relationships.Relationship(random.randint(1,20))
            npc.relationship.history.append(gears.relationships.Memory("you caused Kettel Industries to bomb our power plant",
                                                                       "I tried to protect your power plant from Kettel Industries",
                                                                       -10, (gears.relationships.MEM_Ideological,)))
            self._did_first_reply = False
            ghdialogue.start_conversation(camp,camp.pc,npc)

            self.started_the_intro = True

    def SHERIFF_offers(self,camp):
        mylist = list()

        if camp.scene is self.elements["LOCALE"]:

            mylist.append(Offer(
                "Alright. When we get to the field, I'll give you a brief tutorial. You can get in your mecha by using the boarding chute over there.",
                dead_end=True, effect=self._activate_tutorial,
                context=ContextTag([context.CUSTOMGOODBYE]), subject="TUTORIAL",
                data={"reply": "[YESPLEASE]"}
            ))
            mylist.append(Offer(
                "Understood. You can get in your mecha by using the boarding chute over there.",
                dead_end=True, effect=self._deactivate_tutorial,
                context=ContextTag([context.CUSTOMGOODBYE]), subject="TUTORIAL",
                data={"reply": "[NOTHANKYOU]"}
            ))

            if not self._did_first_reply:
                mylist.append(Offer(
                        "[LISTEN_UP] I know what you've been up to, and it's none of my business so long as you keep that crap outside of town. But the last corp you attacked traced you to {DZ_TOWN_NAME}. That puts all of us in danger.".format(**self.elements),
                        context=ContextTag([context.HELLO]), allow_generics=False, effect=self._ring_the_alarm
                ))

                mylist.append(Offer(
                        "I don't think those corporate goons will see things in the same way. Tell you what- you're going to come with me and make sure they don't blow up anything important. After that we can talk about how we're going to solve this mess.".format(**self.elements),
                        context=ContextTag([context.CUSTOM]), effect=self._choose_robinhood_reply,
                        data={"reply": "I'm just stealing from the rich and giving to the poor. It's all fair play."}
                ))

                mylist.append(Offer(
                        "The fact that we're now under attack by corporate goons says that they did track you back to here. Tell you what- you're going to come with me and make sure they don't blow up anything important. After that we can talk about how we're going to solve this mess.".format(**self.elements),
                        context=ContextTag([context.CUSTOM]), effect=self._choose_skillful_reply,
                        data={"reply": "Impossible. There's no way anyone could track me back to here."}
                ))

                mylist.append(Offer(
                        "Before we head out, I have a question: Would you like me to talk you through the new mecha control scheme?".format(**self.elements),
                        context=ContextTag([context.CUSTOMREPLY]), subject="TUTORIAL", subject_start=True,
                        data={"reply": "That's a fair cop."}
                ))



            else:
                mylist.append(Offer(
                        "Time to go defend the power station. Do you want me to walk you through the new mecha control upgrade when we get there?",
                        context=ContextTag([context.HELLO]), allow_generics=False,
                ))
                mylist.append(Offer(
                    "Alright. When we get to the field, I'll give you a brief tutorial. You can get in your mecha by using the boarding chute over there.",
                    dead_end=True, effect=self._activate_tutorial,
                    context=ContextTag([context.CUSTOM]),
                    data={"reply": "[YESPLEASE]"}
                ))
                mylist.append(Offer(
                    "Understood. You can get in your mecha by using the boarding chute over there.",
                    dead_end=True, effect=self._deactivate_tutorial,
                    context=ContextTag([context.CUSTOM]),
                    data={"reply": "[NOTHANKYOU]"}
                ))

        return mylist

    def _ring_the_alarm(self, camp):
        pbge.alert("Suddenly, the town defense siren goes off. The security monitor shows hostile mecha approaching the powerplant. They appear to belong to Kettel Industries, one of the corporations you robbed...")

    def _choose_robinhood_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.expectation = gears.relationships.E_PROFESSIONAL
        npc.relationship.attitude = gears.relationships.A_FRIENDLY
        missionbuilder.NewMissionNotification("Protect the Powerplant")

    def _choose_skillful_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.expectation = gears.relationships.E_PROFESSIONAL
        npc.relationship.attitude = gears.relationships.A_SENIOR
        missionbuilder.NewMissionNotification("Protect the Powerplant")


class DZDPostMissionScene(Plot):
    LABEL = "DZD_MISSION_DEBRIEFING"
    active = False
    scope = True

    def custom_init( self, nart ):
        self.did_intro = False
        return True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.did_intro:
            game.content.plotutility.AutoLeaver(self.elements["SHERIFF"])(camp)

            npc = self.elements["SHERIFF"]
            ghdialogue.start_conversation(camp,camp.pc,npc)

            self.did_intro = True

    def _announce_mission(self,camp):
        missionbuilder.NewMissionNotification("Go to Wujung")

    def SHERIFF_offers(self,camp):
        mylist = list()
        myhello = Offer(
            self.elements["DEBRIEFING_HELLO"].format(**self.elements),
            context=ContextTag([context.HELLO]), allow_generics=False
        )

        mylist.append( Offer(
            self.elements["DEBRIEFING_MISSION"].format(**self.elements),
            context=ContextTag([context.SOLUTION]), subject_start=True, subject=self, effect=self._announce_mission
        ))

        mylist.append( Offer(
            "When you get to Wujung you should talk to Osmund Eumann at the Bronze Horse Inn. He'll be able to help you.",
            context=ContextTag([context.ACCEPT]), subject=self
        ))

        mylist.append(myhello)
        return mylist

    def CHUTE_menu(self, camp, thingmenu):
        thingmenu.desc = "This boarding chute leads to\n your {}.".format(camp.get_pc_mecha(camp.pc).get_full_name())
        thingmenu.add_item("Board mecha and go to Wujung",self._finish_mission)

    def _finish_mission(self, camp):
        camp.check_trigger("INTRO_END")
        self.adv.end_adventure(camp)


class DZDIntroMission( Plot ):
    # Set up the decoy story for Dead Zone Drifter.
    LABEL = "DZD_INTRO_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(
            40,40,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale,
            exploration_music='A wintertale.ogg', combat_music='Chronos.ogg',
        )
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        player_a,enemy_a = random.choice(pbge.randmaps.anchors.OPPOSING_PAIRS)

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=player_a),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        enemy_room = self.register_element("ENEMY_ROOM",game.content.ghrooms.MSRuinsRoom(15,15,anchor=enemy_a),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ENEMY_ROOM")
        myunit = gears.selector.RandomMechaUnit(level=10,strength=50,fac=self.elements.get("ENEMY_FACTION", None),env=myscene.environment)
        team2.contents += myunit.mecha_list
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())
        enemy_room.contents.append(ghterrain.DZDConcreteBuilding)

        self.mission_entrance = (myscene,myent)
        self.started_the_intro = False

        self.tiles_moved = 0
        self.move_tutorial_done = False
        self.threat_tutorial_done = False
        self.combat_tutorial_done = False

        return True

    def start_mission(self,camp,tutorial_on):
        self.tutorial_on = tutorial_on
        camp.destination,camp.entrance=self.elements["LOCALE"],self.elements["ENTRANCE"]

    def t_PCMOVE(self,camp):
        if camp.scene is self.elements["LOCALE"]:
            self.tiles_moved += 1
            if self.tutorial_on and self.tiles_moved > 10 and not self.move_tutorial_done and not self.threat_tutorial_done:
                mycutscene = SimpleMonologueDisplay("Good, you've got the basics of movement mastered. Keep going and let's see if we can find the raiders.",
                                                    self.elements["SHERIFF"])
                mycutscene(camp)
                self.move_tutorial_done = True
            if self.tutorial_on and not self.threat_tutorial_done and game.exploration.current_explo and camp.scene.in_sight.intersection(game.exploration.current_explo.threat_tiles):
                mycutscene = SimpleMonologueDisplay("I've identified the enemy's sensor range using my Target Analysis system; you should see it projected on your map as a red line. This region is called the Threat Area. Combat will begin as soon as we move into it.",
                                                    self.elements["SHERIFF"])
                mycutscene(camp)
                self.threat_tutorial_done = True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            mycutscene = SimpleMonologueDisplay(
                "We're going to have to search this area to find the attacker. Hopefully we aren't too late.",
                self.elements["SHERIFF"])
            mycutscene(camp)
            if self.tutorial_on:
                mycutscene = SimpleMonologueDisplay(
                    "Your mecha is controlled using the M.O.U.S.E. system- don't ask me what that stands for. Just click where you want to go and the navigation computer does the rest. I'll follow along right behind you.",
                    self.elements["SHERIFF"])
                mycutscene(camp)

            self.started_the_intro = True

    def t_STARTCOMBAT(self,camp):
        if camp.scene is self.elements["LOCALE"] and self.tutorial_on and not self.combat_tutorial_done:
            mycutscene = SimpleMonologueDisplay(
                "Combat has started. Each round you get to take two actions; you can move and attack, or attack twice, or anything else you want to do.",
                self.elements["SHERIFF"])
            mycutscene(camp)
            mycutscene.text = "There on the upper left you'll see the icons for the different types of action you can take: movement, attack, skills, and ending your turn. On the upper right is the interface for your currently selected action."
            mycutscene(camp)
            mycutscene.text = "To move, make sure your movement action is selected and just click where you want to go. To attack, you can either click on the attack icon or click on the enemy mecha. You can scroll through weapons and special attacks with the mouse wheel or the arrow keys."
            mycutscene(camp)

            self.combat_tutorial_done = True

    def t_ENDCOMBAT(self,camp):
        if camp.scene is self.elements["LOCALE"]:
            # If the player team gets wiped out, end the mission.
            myteam = self.elements["_eteam"]
            if len(myteam.get_members_in_play(camp)) < 1:
                mycutscene = SimpleMonologueDisplay(
                    "We won! Let's head back to base and discuss our next move...",
                    self.elements["SHERIFF"])
                mycutscene(camp)
                self.end_the_mission(camp)
                camp.check_trigger("WIN",self)
            elif not camp.first_active_pc():
                self.end_the_mission(camp)
                camp.check_trigger("LOSE",self)


    def end_the_mission(self,camp):
        # Restore the party at the end of the mission, then send them back to the hangar.
        camp.totally_restore_party()
        camp.destination, camp.entrance = self.elements["MISSION_RETURN"]
        camp.check_trigger("END", self)


class DZDKettelMission( DZDIntroMission ):
    # As above, but with a special gift from Elisha.
    LABEL = "DZD_KETTEL_MISSION"

    def custom_init( self, nart ):
        super().custom_init(nart)
        # Add a generator. Or, since I don't have a generator handy, some fuel tanks.
        myfuel = self.register_element(
            "FUEL_TANKS", gears.selector.get_design_by_full_name("Chemical Tanks"),
            dident="ENEMY_ROOM"
        )

        return True

    def t_ENDCOMBAT(self,camp):
        if camp.scene is self.elements["LOCALE"]:
            # If the player team gets wiped out, end the mission.
            myteam = self.elements["_eteam"]
            if len(myteam.get_members_in_play(camp)) < 1:
                pbge.alert("As combat ends, you receive a comm signal from an unknown transmitter.")
                pbge.alert('"Kettel Industries reserves the right to defend itself from criminal activity. Those who harbor criminals will be considered accomplaices."', font=pbge.ALTTEXTFONT)
                pbge.alert('"Thank you for listening, and please consider Kettel Industries for your upcoming reconstruction work."', font=pbge.ALTTEXTFONT)

                pbge.my_state.view.play_anims(gears.geffects.Missile3(start_pos=self.elements["ENTRANCE"].pos, end_pos=self.elements["FUEL_TANKS"].pos))

                my_invo = pbge.effects.Invocation(
                    fx=gears.geffects.DoDamage(10, 8, anim=gears.geffects.SuperBoom,
                                               scale=gears.scale.MechaScale,
                                               is_brutal=True),
                    area=pbge.scenes.targetarea.SelfCentered(radius=5, delay_from=-1))
                my_invo.invoke(camp, None, [self.elements["FUEL_TANKS"].pos, ], pbge.my_state.view.anim_list)
                pbge.my_state.view.handle_anim_sequence()

                mycutscene = SimpleMonologueDisplay(
                    "I admit, I was not expecting that. Let's head back to base...",
                    self.elements["SHERIFF"])
                mycutscene(camp)

                self.end_the_mission(camp)
                camp.check_trigger("WIN",self)
            elif not camp.first_active_pc():
                self.end_the_mission(camp)
                camp.check_trigger("LOSE",self)
