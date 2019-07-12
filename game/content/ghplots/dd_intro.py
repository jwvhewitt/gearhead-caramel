from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context


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

        myscene = gears.GearHeadScene(15,15,"{} Mecha Hangar".format(self.elements["DZ_TOWN_NAME"]),player_team=team1,scale=gears.scale.HumanScale,civilian_team=team2,attributes=(gears.personality.DeadZone,))
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.IndustrialBuilding(floor_terrain=ghterrain.GrateFloor))
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        # Start a new adventure for this plot and its children- the intro will be disposed of when it's finished.
        self.adv = pbge.plots.Adventure(world=myscene)

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.ClosedRoom(10,7),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")
        self.register_element("_CHUTE",ghwaypoints.BoardingChute(plot_locked=True),dident="_EROOM")
        myroom.contents.append(ghwaypoints.ClosedBoardingChute())
        myroom.contents.append(ghwaypoints.VentFan())


        npc = self.register_element("SHERIFF",
                            gears.selector.random_character(55, local_tags=self.elements["LOCALE"].attributes,
                                                            job=gears.jobs.ALL_JOBS["Sheriff"]))
        npc.place(myscene, team=team2)

        self.mission_entrance = (myscene,myent)
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
                dead_end=True, effect=self._activate_tutorial,
            )

            if not self._did_first_reply:
                myhello = Offer(
                        "We just got an alarm from the power station- it's under attack. Are you ready to suit up and roll out?",
                        context=ContextTag([context.HELLO]), dead_end=True,
                )
                myfriend = Offer(
                    "[GOOD] You've been a big help to {}, and to me. One more question: Do you want me to walk you through the new mecha control upgrade?".format(self.elements["DZ_TOWN_NAME"]),
                    dead_end=True, effect=self._choose_friendly_reply
                )
                mypro = Offer(
                    "I would have had a hard time defending {} without your assistance. One question before we go: Do you want me to walk you through the new mecha control upgrade?".format(self.elements["DZ_TOWN_NAME"]),
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
        pass

    def _CHUTE_menu(self, camp, thingmenu):
        thingmenu.desc = "This boarding chute leads to\n your {}.".format(camp.get_pc_mecha(camp.pc).get_full_name())
        thingmenu.add_item("Board mecha",self._start_mission)


class DZDIntroMission( Plot ):
    # Set up the decoy story for Dead Zone Drifter.
    LABEL = "DZD_INTRO_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")



        self.mission_entrance = (myscene,myent)
        self.started_the_intro = False

        return True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            pass
            self.started_the_intro = True

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.end_the_mission(camp)

    def end_the_mission(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        self.adv.end_adventure(camp)
