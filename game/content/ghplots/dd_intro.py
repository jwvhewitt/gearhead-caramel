from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay


class DZDIntro_GetInTheMekShimli(Plot):
    # Start of the DZD Intro. Meet the sheriff of the dead zone town you're protecting. Go into battle.
    LABEL = "DZD_INTRO"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        self.elements["DZ_TOWN_NAME"] = self.generate_town_name()

        myscene = gears.GearHeadScene(15,15,"{} Mecha Hangar".format(self.elements["DZ_TOWN_NAME"]),player_team=team1,scale=gears.scale.HumanScale,civilian_team=team2,attributes=(gears.personality.DeadZone,),is_metro=True)
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
                            gears.selector.random_character(55, local_tags=self.elements["LOCALE"].attributes,
                                                            job=gears.jobs.ALL_JOBS["Sheriff"]))
        npc.place(myscene, team=team2)

        self.register_element("MISSION_RETURN", (myscene,myent))

        # Request the intro mission and debriefing.
        self.add_sub_plot(nart,"DZD_INTRO_MISSION",ident="MISSION")
        self.add_sub_plot(nart,"DZD_MISSION_DEBRIEFING",ident="DEBRIEFING")

        # Attempt to load the test mission.
        mytest = self.add_sub_plot(nart,"DZRE_TEST",spstate=pbge.plots.PlotState(rank=1,elements={"METRO":myscene.metrodat,"MISSION_GATE":mychute,"FACTION":game.content.plotutility.RandomBanditCircle()}).based_on(self),necessary=False)
        if mytest:
            print "Loaded test!"
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

    def _choose_professional_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.role = gears.relationships.R_COLLEAGUE
        npc.relationship.attitude = gears.relationships.A_THANKFUL

    def _choose_flirty_reply(self,camp):
        self._did_first_reply = True
        npc = self.elements["SHERIFF"]
        npc.relationship.role = gears.relationships.R_CRUSH
        npc.relationship.attitude = gears.relationships.A_FRIENDLY

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
        ghdialogue.AutoJoiner(self.elements["SHERIFF"])(camp)
        self.subplots["MISSION"].start_mission(camp,self._tutorial_on)

    def MISSION_END(self, camp):
        self.active = False
        self.subplots["DEBRIEFING"].activate(camp)

    def CHUTE_menu(self, camp, thingmenu):
        thingmenu.desc = "This boarding chute leads to\n your {}.".format(camp.get_pc_mecha(camp.pc).get_full_name())
        thingmenu.add_item("Board mecha",self._start_mission)


class DZDPostMissionScene(Plot):
    LABEL = "DZD_MISSION_DEBRIEFING"
    active = False
    scope = True

    def custom_init( self, nart ):
        self.did_intro = False
        return True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.did_intro:
            ghdialogue.AutoLeaver(self.elements["SHERIFF"])(camp)

            npc = self.elements["SHERIFF"]
            ghdialogue.start_conversation(camp,camp.pc,npc)

            self.did_intro = True

    def SHERIFF_offers(self,camp):
        mylist = list()
        myhello = Offer(
            "Defending {} by ourselves isn't working; there's too much ground to cover and not enough of us to do it. Plus, now we have to deal with a ransacked powerplant. Who knows if it can even be fixed?".format(self.elements["DZ_TOWN_NAME"]),
            context=ContextTag([context.HELLO]),
        )

        mylist.append( Offer(
            "I'd like for you to head to Wujung. Hire some lancemates. Find someone who can help us with our energy problems. Then come back here and we'll see if we can put a permanent stop to those raiders.",
            context=ContextTag([context.SOLUTION]), subject_start=True, subject=self
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
        camp.check_trigger("END",self)
        self.adv.end_adventure(camp)

class DZDIntroMission( Plot ):
    # Set up the decoy story for Dead Zone Drifter.
    LABEL = "DZD_INTRO_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(40,40,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        player_a,enemy_a = random.choice(pbge.randmaps.anchors.OPPOSING_PAIRS)

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=player_a),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        enemy_room = self.register_element("ENEMY_ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,anchor=enemy_a),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ENEMY_ROOM")
        myunit = gears.selector.RandomMechaUnit(level=10,strength=50,fac=None,env=myscene.environment)
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
            if len(myteam.get_active_members(camp)) < 1:
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

