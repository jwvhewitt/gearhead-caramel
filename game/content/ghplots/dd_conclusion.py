from pbge.plots import Plot, PlotState, Adventure
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from game.content import backstory, plotutility, ghterrain, ghwaypoints, gharchitecture, ghrooms, ghcutscene
import random
from gears import relationships
from game import content
from . import dd_main, missionbuilder, dd_customobjectives
from .dd_main import DZDRoadMapExit
from pbge.memos import Memo
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery


DZDCVAR_NUM_ALLIANCES = "DZDCVAR_NUM_ALLIANCES"
DZDCVAR_CETUS_TOWN = "DZDCVAR_CETUS_TOWN"
DZDCVAR_YES_TO_TDF = "DZDCVAR_YES_TO_TDF"

class DZD_Conclusion(Plot):
    # This plot is the conclusion controller; it loads and activates the individual bits of the conclusion
    # as necessary.
    LABEL = "DZD_CONCLUSION"
    active = True
    scope = True

    def custom_init( self, nart ):
        # Add the doomed village subplot, just because we want to know the village name
        sp = self.add_sub_plot(nart, "DZDC_DOOMED_VILLAGE", ident="VILLAGE")
        self.elements["DOOMED_VILLAGE"] = sp.elements["LOCALE"]

        # Add the victory party subplot
        self.add_sub_plot(nart, "DZDC_VICTORY_PARTY", ident="PARTY")

        # Determine Cetus's path to Wujung. Gonna do that now just because.
        mymap = self.elements["DZ_ROADMAP"]
        candidates = [n for n in mymap.nodes if n.sub_plot_label == "DZD_ROADSTOP"]
        candidates.sort(key=lambda n: n.pos[0])
        self.cetus_path = [candidates[random.randint(0,1)], candidates[random.randint(2,3)], candidates[random.randint(4,5)]]

        # Also: Create the Voice of Iijima contact NPC.
        npc = nart.camp.get_major_npc("General Pinsent")
        if not npc:
            npc = gears.selector.random_character(
                rank=55, job = gears.jobs.ALL_JOBS["Commander"],
                faction=gears.factions.TerranDefenseForce
            )
        self.register_element("TDF_CONTACT", npc)

        return True

    def PARTY_WIN(self, camp: gears.GearHeadCampaign):
        # We get the PARTY_WIN trigger when the PC is informed about the happenings in THAT_TOWN.
        self.subplots["VILLAGE"].activate(camp)

    def VILLAGE_WIN(self, camp: gears.GearHeadCampaign):
        # Cetus has been met, and possibly even defeated once. Start the final part of the conclusion.
        pstate = PlotState(adv=Adventure("Conclusion")).based_on(self)
        content.load_dynamic_plot(camp, "DZDC_NEW_DEADZONE_ORDER", pstate)
        self._load_next_fight(camp)

    def _load_next_fight(self, camp):
        # Load the next fight against Cetus. In case you run out of villages, load the BAD END.
        if self.cetus_path:
            mytown = self.cetus_path.pop(0)
            camp.campdata[DZDCVAR_CETUS_TOWN] = mytown.destination
            pstate = PlotState(
                adv=Adventure("CetusFight"),
                elements={"METROSCENE": mytown.destination, "METRO": mytown.destination.metrodat,
                          "MISSION_GATE": mytown.entrance},
            ).based_on(self)
            sp = content.load_dynamic_plot(camp, "DZDC_FIGHT_CETUS", pstate)
            self.subplots["FIGHTCETUS"] = sp

        else:
            pstate = PlotState(adv=Adventure("Resolution")).based_on(self)
            content.load_dynamic_plot(camp, "DZDCEND_BAD", pstate)
            self.end_plot(camp, True)

    def FIGHTCETUS_WIN(self, camp):
        pstate = PlotState(adv=Adventure("Resolution")).based_on(self)
        if camp.campdata[DZDCVAR_NUM_ALLIANCES] >= 3:
            content.load_dynamic_plot(camp, "DZDCEND_DZALLIANCE", pstate)
        else:
            content.load_dynamic_plot(camp, "DZDCEND_TDFMISSILES", pstate)
        self.end_plot(camp, True)

    def FIGHTCETUS_LOSE(self, camp):
        self._load_next_fight(camp)


class VictoryParty(Plot):
    # Following the player's success in opening the road, there will be a victory party.
    # This party will be interrupted by the attack on DoomedTown.
    LABEL = "DZDC_VICTORY_PARTY"
    active = True
    scope = True

    COMMENTS = (
        "Thanks for helping us get the power back on!",
        "Let me buy you a drink... I'm sure everyone else here tonight will want to do the same!",
        "Now that the roads are clear, maybe I'll go visit the green zone.",
        "It's going to be another little while of unstable power, but after that I can start doing my podcast again.",
        "You're so brave! I wanted to be a cavalier too, until I took an arrow to the knee.",
        "Praise Atan! You're the one we're having this party for tonight.",
        "Would you like to dance? Well, if you decide to dance, remember that I asked you first.",
        "I wanted to thank you for all that you've done for our town."
    )

    def custom_init( self, nart ):
        dest = self.elements["TAVERN"]
        self.party_npcs = list()
        self.talked_to_npcs = list()
        for t in range(8):
            npc = self.seek_element(nart, "NPC_{}".format(t), self._is_good_npc, scope=self.elements["METROSCENE"],
                                    must_find=False, lock=True)
            if npc:
                plotutility.CharacterMover(nart.camp, self, npc, dest, dest.civilian_team)
                self.party_npcs.append(npc)
            else:
                break

        self.started_party = False
        self.countdown = 2
        self.party_lines = random.sample(self.COMMENTS, 7)
        self.memo = Memo("There's a party to celebrate the clearing of the highway at {TAVERN} in {METROSCENE}.".format(**self.elements),
                         location=self.elements["TAVERN"])

        return True

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc in self.party_npcs:
            if self.countdown > 0 and self.party_lines:
                goffs.append(Offer(
                    "[HELLO] {}".format(self.party_lines.pop()),
                    ContextTag((context.HELLO,)), effect=self._say_party_line
                ))
            else:
                goffs.append(Offer(
                    "[HELLO] You know, you're the one who really did the hard work to help get our power back. I say you should give a speech!",
                    ContextTag((context.HELLO,)), effect=self._give_speech, dead_end=True
                ))
        return goffs

    def _say_party_line(self, camp):
        self.countdown -= 1

    def _give_speech(self, camp):
        pbge.alert("At this suggestion, everyone in the bar turns to you and applauds. It seems you won't be getting out of here tonight without saying a few words.")

        mymenu= pbge.rpgmenu.AlertMenu("How do you want to begin your speech?")
        mymenu.add_item("Start on a joke.", "[DZDC_VICTORY_PARTY:TRY_FUNNY]")
        mymenu.add_item("Introduce yourself.", "[DZDC_VICTORY_PARTY:TRY_INTRODUCTION]")

        answer = mymenu.query()
        if answer:
            ghcutscene.SimpleMonologueDisplay(answer, camp.pc)(camp,False)
        else:
            ghcutscene.SimpleMonologueDisplay("...", camp.pc)(camp,False)
            pbge.alert("The rest of the party watches you with anticipation.")

        mymenu= pbge.rpgmenu.AlertMenu("What will you say next?")
        mymenu.add_item("Tell then about securing the highway.", "[DZDC_VICTORY_PARTY:TELL_HIGHWAY]")
        mymenu.add_item("Tell them about the adventures you've had.", "[DZDC_VICTORY_PARTY:TELL_ADVENTURES]")

        answer = mymenu.query()
        if answer:
            ghcutscene.SimpleMonologueDisplay(answer, camp.pc)(camp,False)
        else:
            ghcutscene.SimpleMonologueDisplay("um...", camp.pc)(camp,False)
            pbge.alert("Everybody stares at you expectantly.")

        mymenu= pbge.rpgmenu.AlertMenu("How will you conclude?")
        mymenu.add_item("Make a toast to {}.".format(self.elements["METROSCENE"]), "[DZDC_VICTORY_PARTY:TOAST_TOWN]")
        mymenu.add_item("Thank {} for {} help.".format(self.elements["DZ_CONTACT"],self.elements["DZ_CONTACT"].gender.possessive_determiner), "[DZDC_VICTORY_PARTY:TOAST_SHERIFF]")

        answer = mymenu.query()
        if answer:
            ghcutscene.SimpleMonologueDisplay(answer, camp.pc)(camp,False)
            pbge.alert("The people in the bar give you a round of thunderous applause.")
        else:
            ghcutscene.SimpleMonologueDisplay("...and that's all I have to say about that.", camp.pc)(camp,False)
            pbge.alert("The people in the bar nod in polite silence and then get back to whatever they were doing before.")

        pbge.alert("As you finish your speech, {} rushes over and pulls you aside.".format(self.elements["DZ_CONTACT"]))
        self._end_the_party(camp)

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is camp.pc:
            mygram = {
                "[DZDC_VICTORY_PARTY_SHERIFF]": [str(self.elements["DZ_CONTACT"])],
                "[DZDC_VICTORY_PARTY_TOWN]": [str(self.elements["METROSCENE"])],
                "[DZDC_VICTORY_PARTY:TRY_FUNNY]": [
                    "Did you heard about the kaiju that threw up? It's all over town! Moving right along...",
                    "Why did the robot cross the road? Because it was programmed by a chicken! I've got a million jokes like that... Some of them are even funny!",
                    "My cousin's bread factory was burnt to the ground by raiders... Now his business is toast. That was just a joke, by the way; you don't have to look sad.",
                    "Two morlocks are eating a clown. One says to the other 'Does this taste funny to you?'... Actually that didn't happen. Morlocks can't talk.",
                    "Why was the mecha itchy? Because it had roboticks! Get it? Seriously, though, I'm glad to be here... How are you folks doing?",
                    "What do you call a fish with no eye? Fssshh. Now that I think about it, this joke is only funny if you see it written down. Let's just skip to the next part.",
                    "How can you tell when there's an ace pilot in the room? Don't worry, [subject_pronoun]'ll tell you.",
                    "Sometimes I tuck my knees into my chest and lean forward. That's just how I roll.",
                    "There are three types of people in the world. Those of us who are good at math, and those of us who aren't. Ha ha, thanks for coming here tonight.",
                    "I was going to start tonight with a joke, but then I remembered that I don't know any jokes.",
                ],
                "[DZDC_VICTORY_PARTY:TRY_INTRODUCTION]": [
                    "Hello, I'm [speaker]. You may remember me from the constant bandit attacks your town has had lately. I mean, I'be been fighting on your side, I'm not one of the bandits...",
                    "Hi, I'm [speaker]; I'm a cavalier. I've been working hard to get a repair crew for your powerplant."
                ],
                "[DZDC_VICTORY_PARTY:TELL_HIGHWAY]": [
                    "Finding someone to repair your powerplant was harder than it sounds, because nobody I spoke to was willing to come out this far unless the highway was secure. So, I cleared the highway all the way from here to Wujung.",
                    "The company in Wujung didn't want to come this far into the deadzone, so I had to secure the highway all this distance. It was a big job but I did it. RegEx Construction will be arriving to begin work soon!"
                ],
                "[DZDC_VICTORY_PARTY:TELL_ADVENTURES]": [
                    "It's been an exciting week, let me tell you. To get the repair crew I've had to fight bandits, Aegis, a variety of monsters... Happy to say that I triumphed, and RegEx Construction will be arriving to fix your powerplant soon!",
                    "There I was, crossing the deadzone from here to Wujung, taking on all comers... Bandits tried to stop me. Ironwind Fortress sent a division to catch me. I was attacked by space pirates and weird nameless things. But I never once stopped, knowing that all of you were waiting for my help."
                ],
                "[DZDC_VICTORY_PARTY:TOAST_TOWN]": [
                    "Let's raise a glass to [DZDC_VICTORY_PARTY_TOWN]; long may your town prosper!",
                    "I propose a toast to [DZDC_VICTORY_PARTY_TOWN]. May your new powerplant be the beginning of many wonderful things!"
                ],
                "[DZDC_VICTORY_PARTY:TOAST_SHERIFF]": [
                    "Before I stop talking, I absolutely must thank [DZDC_VICTORY_PARTY_SHERIFF], whose hard work has kept [DZDC_VICTORY_PARTY_TOWN] safe while I was away. To [DZDC_VICTORY_PARTY_SHERIFF]!",
                    "Finally, I need to thank [DZDC_VICTORY_PARTY_SHERIFF] for protecting [DZDC_VICTORY_PARTY_TOWN] all this time, and without whose efforts we wouldn't be having a party tonight because there'd be no town left to have the party in!"
                ],
            }

        return mygram

    def TAVERN_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.started_party:
            pbge.alert("As you enter {TAVERN}, the party is already going full swing. Might as well mingle and chat for a bit.".format(**self.elements))
            self.started_party = True

    def METROSCENE_ENTER(self, camp):
        if self.started_party:
            pbge.alert(
                "As you leave {}, {} rushes over and pulls you aside.".format(self.elements["TAVERN"], self.elements["DZ_CONTACT"]))
            self._end_the_party(camp)

    def _end_the_party(self, camp):
        ghcutscene.SimpleMonologueDisplay(
            "[THIS_IS_AN_EMERGENCY] I just got a distress call from {DOOMED_VILLAGE}- right before the comm signal cut out entirely. Could you go there and make sure everything is alright?".format(**self.elements),
            self.elements["DZ_CONTACT"]
        )(camp, True)
        camp.check_trigger("WIN", self)
        self.end_plot(camp)

    def _is_good_npc(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.scene is not self.elements["TAVERN"] and
                candidate not in nart.camp.party)



class DoomedTown(Plot):
    # Visit the town that has been destroyed by Cetus. Maybe fight some scavengers.
    # Learn about what happened. Find the angel egg. Fight Cetus when you return to Distant Town.
    LABEL = "DZDC_DOOMED_VILLAGE"
    active = False
    scope = True

    def custom_init( self, nart ):
        town_name = self._generate_town_name()
        town_fac = self.register_element( "METRO_FACTION",
            gears.factions.Circle(nart.camp,parent_faction=gears.factions.DeadzoneFederation,name="the {} Council".format(town_name))
        )
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,), faction=town_fac)

        myscene = gears.GearHeadScene(50, 50, town_name, player_team=team1, civilian_team=team2,
                                      scale=gears.scale.MechaScale, is_metro=True,
                                      faction=town_fac,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.City))
        myscene.exploration_music = 'A wintertale.ogg'
        myscene.combat_music = 'Komiku_-_09_-_Run__That_boss_was_a_bearing_wall_.ogg'

        myscene.contents.append(ghrooms.MSRuinsRoom(5,5))
        myscene.contents.append(ghrooms.WreckageRoom(5,5))

        my_egg = self.register_element("ANGELEGG",
            ghwaypoints.AngelEgg(name="?Angel Egg?", plot_locked=True, desc="You stand before a strange crystal egg. Cloudy shapes move on the inside.")
        )
        myroom = pbge.randmaps.rooms.FuzzyRoom(5,5)
        myscene.contents.append(myroom)
        myroom.contents.append(my_egg)

        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.MechaScaleSemiDeadzoneRuins())

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        self.register_element("METRO", myscene.metrodat)

        # Connect this town to the previous town.
        mymap = self.elements["DZ_ROADMAP"]
        connect_to = self.elements["DZ_NODE"]
        self.final_node = dd_main.RoadNode(None, None, visible=False, frame=dd_main.RoadNode.FRAME_DANGER)
        mymap.add_node(self.final_node,random.randint(1,2),random.randint(3,6))
        self.final_edge = dd_main.RoadEdge(discoverable=False,style=1)
        mymap.connect_nodes(connect_to, self.final_node, self.final_edge)
        self.final_edge.eplot = self

        myroom2 = self.register_element("_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.east),
                                        dident="LOCALE")
        towngate = self.register_element("ENTRANCE", DZDRoadMapExit(roadmap=self.elements["DZ_ROADMAP"],
                                                                    node=self.final_node,name="The Highway",
                                                                    desc="You stand before the road leading back to {METROSCENE}.".format(**self.elements),
                                                                    anchor=pbge.randmaps.anchors.east,
                                                                    plot_locked=True), dident="_ROOM2")

        self.final_node.destination = myscene
        self.final_node.entrance = towngate

        # Gonna register the entrance under another name for the subplots.
        self.register_element("MISSION_GATE", towngate)

        # Add an encounter to the map.
        #self.add_sub_plot(nart, "DZDC_DoomVil_ENCOUNTER")

        self.memo = Memo("{LOCALE} sent a distress call moments before the communication signal was lost. You should go there and find out what happened.".format(**self.elements),
                         location=self.elements["METROSCENE"])

        self.did_intro = False
        self.found_egg = False
        self.did_fight = False

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","Mount {}", "{}", "{} Haven",
                          "Castle {}", "{} Village", "{} Spire")

    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def LOCALE_ENTER(self, camp):
        if not self.did_intro:
            pbge.alert("All is quiet as you enter {LOCALE}. Smoke rises from the recently created ruins. There are few signs of combat, and no sign of survivors.".format(**self.elements))
            self.did_intro = True

    def activate( self, camp ):
        super().activate(camp)
        self.final_edge.visible = True
        self.final_node.visible = True

    def ANGELEGG_BUMP(self, camp: gears.GearHeadCampaign):
        if not self.found_egg:
            pbge.alert("You find a large crystal dome that seems to have been uncovered by a construction project. Movement is visible on the inside. A thick violet fluid leaks from a crack near the bottom.")
            if len(camp.get_active_lancemates()) >= 2:
                mypcs = random.sample(camp.get_active_lancemates(), 2)
                ghcutscene.SimpleMonologueDisplay(
                    "[WE_ARE_IN_DANGER] Do any of you know what this thing is? It looks like an egg... a giant one.".format(
                        **self.elements),
                    mypcs[0]
                )(camp, False)
                ghcutscene.SimpleMonologueDisplay(
                    "[I_DONT_KNOW] Whatever it is, I'm guessing it's not a coincidence that the entire town just got destroyed.".format(
                        **self.elements),
                    mypcs[1]
                )(camp, False)
            BiotechDiscovery(
                camp, "We discovered a mecha-sized egg in {}; it may be connected to Cetus.".format(self.elements["LOCALE"]),
                "Cetus, you say? Oh, this is bad... this is really really bad. We'll send a team to secure the contamination zone immediately. Here is {cash} for your discovery.",
                max(camp.pc.renown+15, 65), on_sale_fun=self._inform_biocorp
            )
            self.memo = None
            self.found_egg = True

    def _inform_biocorp(self, camp: gears):
        camp.campdata["INFORM_BIOCORP_ANGEL_EGG"] = self.elements["LOCALE"]

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.found_egg and not self.did_fight:
            start_node = self.final_edge.get_link(dest_node)
            if start_node.pos[0] < dest_node.pos[0]:
                myanchor = pbge.randmaps.anchors.west
            else:
                myanchor = pbge.randmaps.anchors.east
            myadv = missionbuilder.BuildAMissionSeed(
                camp, "Cetus Attacks", start_node.destination, start_node.entrance,
                rank=self.rank,
                objectives = (dd_customobjectives.DDBAMO_MEET_CETUS,),
                adv_type = "BAM_ROAD_MISSION",
                custom_elements={"ADVENTURE_GOAL": dest_node.entrance,"DEST_SCENE": dest_node.destination,
                                 "ENTRANCE_ANCHOR": myanchor},
                scenegen= gharchitecture.DeadZoneHighwaySceneGen,
                architecture=gharchitecture.MechaScaleDeadzone(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
                cash_reward=100, on_loss=self._end_this_bit, on_win=self._end_this_bit
            )
            return myadv

    def _end_this_bit(self, camp):
        camp.check_trigger("WIN", self)
        self.did_fight = True

    def DZ_CONTACT_offers(self, camp):
        mylist = list()
        if not self.did_fight:
            mylist.append(Offer(
                "Go to {LOCALE} and find out what's wrong. Be careful, [audience]... there's no telling what you'll find.".format(**self.elements),
                context=ContextTag([context.HELLO]), allow_generics=False
            ))
        return mylist


class DZD_ChangeTheWorld(Plot):
    # After the big Cetus reveal, we're gonna change some things in the world.
    # Distant Town:
    # - Survivors from DoomedVillage show up and can give some info
    # - Sheriff can give info about TDF, will offer to join party (giving +1 Lancemate slot)
    # - TDF pilot has arrived in town, can explain the plan to PC
    # Worldwide:
    # - BioCorp employees can explain what happened to Cetus in GH1
    # - Apply an alliance plot to every deadzone town
    LABEL = "DZDC_NEW_DEADZONE_ORDER"
    active = True
    scope = True

    def custom_init( self, nart ):
        self.register_element("REFUGEE1", gears.selector.random_character(local_tags=(gears.personality.DeadZone,)), dident="METROSCENE")
        self.register_element("REFUGEE2", gears.selector.random_character(local_tags=(gears.personality.DeadZone,)), dident="METROSCENE")
        self.register_element("REFUGEE3", gears.selector.random_character(
            rank=random.randint(25,50),
            local_tags=(gears.personality.DeadZone,), job=gears.jobs.ALL_JOBS["Construction Worker"], combatant=True
        ), dident="METROSCENE")

        # Add the TDF scout to the town hall.
        self.seek_element(nart, "TOWN_HALL", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_good_scene)
        npc = gears.selector.random_character(
            rank=42, job = gears.jobs.ALL_JOBS["Recon Pilot"],
            faction=gears.factions.TerranDefenseForce
        )
        self.register_element("SCOUT", npc, dident="TOWN_HALL")

        # Record the number of alliances.
        nart.camp.campdata[DZDCVAR_NUM_ALLIANCES] = 0

        # Apply the alliance plots.
        mymap = self.elements["DZ_ROADMAP"]
        for n in mymap.nodes:
            if n.sub_plot_label == "DZD_ROADSTOP":
                self.add_sub_plot(nart, "DZDC_ALLIANCE", elements={"METROSCENE": n.destination, "METRO": n.destination.metrodat, "MISSION_GATE": n.entrance})

        self.did_intro = False

        return True

    def METROSCENE_ENTER(self, camp):
        if not self.did_intro:
            pbge.alert("On the way into {METROSCENE} you see a caravan of survivors who escaped from {DOOMED_VILLAGE}.".format(**self.elements))
            self.did_intro = True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.SCENE_GOVERNMENT in candidate.attributes

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def REFUGEE1_offers(self, camp):
        mylist = list()
        mylist.append(
            Offer(
                "We lost everything. One minute we were just sitting at home, the next there was a war happening right outside our window.",
                context=(context.HELLO,),
            )
        )
        return mylist

    def REFUGEE2_offers(self, camp):
        mylist = list()
        mylist.append(
            Offer(
                "I got separated from my family during the evacuation... I hope they made it out of {DOOMED_VILLAGE}.".format(**self.elements),
                context=(context.HELLO,),
            )
        )
        return mylist

    def REFUGEE3_offers(self, camp):
        mylist = list()
        mylist.append(
            Offer(
                "I was there when they discovered the egg... We thought it was part of a PreZero ruin, but then someone cracked the surface and it started screaming...".format(**self.elements),
                context=(context.HELLO,),
            )
        )
        return mylist

    def DZ_CONTACT_offers(self,camp):
        mylist = list()
        if gears.relationships.RT_LANCEMATE not in self.elements["DZ_CONTACT"].relationship.tags:
            mylist.append(
                Offer(
                    "[THANK_GOODNESS_YOU_ARE_ALIVE] I couldn't contact your radio, something's blocking the signal. We heard that {DOOMED_VILLAGE} has been destroyed.".format(**self.elements),
                    context=(context.HELLO,),
                )
            )
            if camp.pc.has_badge("Cetus Slayer"):
                mylist.append(
                    Offer(
                        "[SWEAR] There's a scout from the Terran Defense Force at {TOWN_HALL}, and I heard they mobilized one of their battlemovers. Come with me and see what we can find out.".format(**self.elements),
                        context=(context.CUSTOM,), data={"reply":"It's a biomonster named Cetus. I already killed it once, but apparently that didn't stick."},
                    )
                )
            else:
                mylist.append(
                    Offer(
                        "There's a scout from the Terran Defense Force at {TOWN_HALL}, and I heard they mobilized one of their battlemovers. Come with me and see what we can find out.".format(**self.elements),
                        context=(context.CUSTOM,), data={"reply":"It's a biomonster. Makes Kerberos look like a puppy."},
                    )
                )

            mylist.append(
                Offer(
                    "Great, let's go.".format(**self.elements),
                    context=(context.CUSTOMREPLY,), data={"reply":"[LETSGO]"}, effect=self._join_lance
                )
            )


        return mylist

    def _join_lance(self, camp: gears.GearHeadCampaign):
        npc = self.elements["DZ_CONTACT"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = plotutility.AutoJoiner(npc)
        effect(camp)
        camp.num_lancemates += 1

    def SCOUT_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] The battlecarrier Voice of Iijima has followed Cetus to {}.".format(camp.campdata[DZDCVAR_CETUS_TOWN]),
                context=(context.HELLO,),
            )
        )

        mylist.append(
            Offer(
                "Go to {} and make contact with {}; {} will know what to do.".format(camp.campdata[DZDCVAR_CETUS_TOWN], self.elements["TDF_CONTACT"], self.elements["TDF_CONTACT"].gender.subject_pronoun),
                context=(context.CUSTOM,), data={"reply": "What can we do to help?"}
            )
        )

        return mylist

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc.faction and npc.faction.get_faction_tag() is gears.factions.BioCorp:
            pass
        return goffs


#   *************************
#   ***   DZDC_ALLIANCE   ***
#   *************************
#
# Each of these plots provide the PC with an opportunity to form an alliance with a deadzone town.

class DZDCNegotiationAlliance(Plot):
    # Talk to the local authorities to get the militia on your side.
    LABEL = "DZDC_ALLIANCE"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        myscene: gears.GearHeadScene = self.elements["METROSCENE"]
        # Make sure there's a faction representative for the duration of this plot.
        self.elements["FACTION"] = myscene.faction
        self.add_sub_plot(nart, "ENSURE_LOCAL_REPRESENTATION")

        return True

    PLEAS = (
        "I need {METROSCENE}'s help to defeat Cetus.",
        "I need your help to defeat Cetus.",
        "There's a biomonster on the loose, and I can't defeat it without your help.",
        "With the {METROSCENE} milita's help, I may be able to defeat Cetus."
    )

    RETORTS = (
        "The Terran Defense Force has unleashed their big guns; what do you think our militia can do against a threat of that size?",
        "Our town militia would get wiped out in an instant. Let the greenzoners handle this.",
        "The Defense Force has a flying battleship tracking that monster. If they can't stop it, we have no chance.",
        "When whales fight, it's the shrimp that suffer. My priority right now is to keep this town safe.",
        "Our best bet right now is to keep our heads down and hope that neither the monster nor the Defense Force decide to blow this town up.",
        "We barely have enough meks to defend ourselves; we don't have nearly enough firepower to go hunting giant monsters."
    )

    NEGCHARM = (
        "If we're doomed anyhow, it's better to go down fighting!",
        "Alone we might be weak, but together our power is multiplied!",
        "You're not alone; we already have the beginning of a coalition!",
        "All of the cool towns have already joined my club."
    )

    def _get_generic_offers(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc.faction is self.elements["FACTION"]:
            rank = self.rank + 10 - npc.get_reaction_score(camp.pc, camp)//10
            qol: gears.QualityOfLife = self.elements["METRO"].get_quality_of_life()
            if qol.defense > 0:
                # This town has good defenses. Convincing them to help will be easier.
                diff = gears.stats.DIFFICULTY_EASY
            elif qol.defense < 0:
                diff = gears.stats.DIFFICULTY_LEGENDARY
            else:
                diff = gears.stats.DIFFICULTY_AVERAGE

            goffs.append(Offer(
                "[YOUR_PLAN_IS_HOPELESS] {}".format(random.choice(self.RETORTS)),
                context=ContextTag((context.CUSTOM,)), subject=self, subject_start=True,
                data={"reply":random.choice(self.PLEAS).format(**self.elements)}
            ))

            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Alright, when you fight Cetus, you will have the support of {}.".format(self.elements["METROSCENE"]),
                    context=ContextTag((context.CUSTOMREPLY,)), subject=self,
                    data={"reply":self.NEGCHARM[min(camp.campdata.get(DZDCVAR_NUM_ALLIANCES,0),3)]},
                    effect=self._win_plot
                ), camp, goffs, gears.stats.Charm, gears.stats.Negotiation, rank, diff
            )

        return goffs

    def _win_plot(self, camp: gears.GearHeadCampaign):
        camp.campdata[DZDCVAR_NUM_ALLIANCES] += 1
        self.end_plot(camp, True)


#   ****************************
#   ***   DZDC_CETUS_FIGHT   ***
#   ****************************
#
# Cetus is at a certain DeadZone town. The TDF battlecarrier "Voice of Iijima" is also there.

class CetusFight(Plot):
    # Each time Cetus moves to a new village, you have one chance to fight it.
    # In order to win the fight you must have at least one "advantage". Otherwise,
    # once it has taken enough damage, Cetus will simply release a death wave and fly away.
    # Also, if you lose the third fight, the TDF has had enough and will use their nukes.
    LABEL = "DZDC_FIGHT_CETUS"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        myscene: gears.GearHeadScene = self.elements["METROSCENE"]

        # Move the TDF_CONTACT to the current town.
        townhall = self.seek_element(nart, "TOWN_HALL", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_good_scene)
        npc = self.elements["TDF_CONTACT"]
        self.place_element(npc, townhall)

        # Create the Cetus encounter.
        self.mission = missionbuilder.BuildAMissionSeed(
            nart.camp, "Cetus Attacks", myscene, self.elements["MISSION_GATE"],
            rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_FIGHT_CETUS,),
            architecture=gharchitecture.MechaScaleSemiDeadzoneRuins(),
            cash_reward=100, on_loss=self._lose_mission, on_win=self._win_mission
        )

        self.memo = Memo(
            "Cetus has been tracked to {METROSCENE}; you can speak to {TDF_CONTACT} there about defeating it.".format(
                **self.elements
            ), location=townhall
        )

        return True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission:
            thingmenu.add_item("Go intercept Cetus.", self.mission)

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.SCENE_GOVERNMENT in candidate.attributes

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _lose_mission(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("LOSE", self)
        self.end_plot(camp)

    def _win_mission(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.end_plot(camp)

    def TDF_CONTACT_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] We are unable to track its exact position, but Cetus appears to be moving towards {METROSCENE}. Our battlecarrier The Voice of Iijima stands ready to fire on the biomonster as soon as we have a clear shot.".format(**self.elements),
                context=(context.HELLO,),
            )
        )
        if not camp.campdata.get(DZDCVAR_YES_TO_TDF):
            mylist.append(
                Offer(
                    "{METROSCENE} is being evacuated as we speak. Mecha scale weapons are clearly not powerful enough to counteract Cetus's regeneration factor. We must stop it now, before it reaches the cities of the green zone. In a worst case scenario we're talking about the difference between hundreds of dead and millions. Are you going to help us or not?".format(**self.elements),
                    context=(context.CUSTOM,), subject=self, subject_start=True,
                    data={"reply":"You can't seriously be going to use your nuclears this close to a town?!"}
                )
            )

            mylist.append(
                Offer(
                    "Cetus appears to have active sensor blocking capability, similar to the experimental Anubis mecha. It's been moving in a series of short, high velocity flights. Every time it jumps we lose it and have to start looking again, but the hope is that after each jump it needs to recharge before jumping again. Will you help us defeat this monster?".format(**self.elements),
                    context=(context.CUSTOM,), subject=self, subject_start=True,
                    data={"reply":"Why can't you track its position?"}
                )
            )

            mylist.append(
                Offer(
                    "As I said, Cetus is approaching {METROSCENE}. If you can get it to expend some of its energy, just enough to prevent it from making a quick rocket jump, then we can hit it with everything we have.".format(**self.elements),
                    context=(context.CUSTOMREPLY,), subject=self,
                    data={"reply":"Alright, I'll help you."}, effect=self._say_yes
                )
            )

            mylist.append(
                Offer(
                    "In that case I suggest you get out of here. This area is going to be dangerous.".format(**self.elements),
                    context=(context.CUSTOMREPLY,), subject=self,
                    data={"reply":"No, there must be another way."}
                )
            )

        return mylist

    def _say_yes(self, camp):
        camp.campdata[DZDCVAR_YES_TO_TDF] = True


#   *************************
#   ***   UTILITY  BITS   ***
#   *************************

class DZDCDoomVilMechaEncounter(Plot):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "DZDC_DoomVil_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM", pbge.randmaps.rooms.OpenRoom(5, 5), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("FACTION", None),
                                                         myscene.environment).mecha_list
        return True

    def t_ENDCOMBAT(self, camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(100)

#   ***********************
#   ***   RESOLUTIONS   ***
#   ***********************

def get_current_qol_total(camp, mymap):
    total_qol = 0
    for n in mymap.nodes:
        if n.destination and hasattr(n.destination, "metrodat") and n.destination.metrodat:
            total_qol += n.destination.metrodat.get_quality_of_life_index()
    return total_qol

DISASTER_MAGNET = gears.meritbadges.UniversalReactionBadge(
    "Disaster Magnet", "Everywhere you go, disaster seems to follow.", -5
)

class BadEnding(Plot):
    LABEL = "DZDCEND_BAD"
    active = True
    scope = True

    def t_START(self, camp: gears.GearHeadCampaign):
        pbge.alert("With time running out, the Terran Defense Force launches an all-out attack using the Voice of Iijima. Saturation bombing is used in an attempt to kill Cetus before it can jet away.")
        pbge.alert("{} is utterly destroyed in the crossfire. Following the battle the Defense Force claims that Cetus has been eliminated, though no remains are ever recovered.".format(camp.campdata[DZDCVAR_CETUS_TOWN]))
        pbge.alert("Relations between the greenzone cities and the towns of the deadzone become more strained than they were before. For better or worse, your role in these events is mostly forgotten.")

        camp.pc.add_badge(DISASTER_MAGNET)

        camp.eject()

class DZAllianceEnding(Plot):
    LABEL = "DZDCEND_DZALLIANCE"
    active = True
    scope = True

    def t_START(self, camp: gears.GearHeadCampaign):
        pbge.alert("The communities of the dead zone celebrate your victory over Cetus. Many of the local leaders enter talks to expand trade and mutual defense pacts between their isolated settlements.")
        pbge.alert("Within the green zone the Terran Defense Force claims this outcome was a result of their deterrence strategy, though some of the commanders resent you for letting Cetus get away.")
        pbge.alert("Cetus does not return to trouble this part of the world again.")
        total_qol = get_current_qol_total(camp, self.elements["DZ_ROADMAP"])
        if total_qol < camp.campdata["INITIAL_QOL"]:
            camp.pc.add_badge(DISASTER_MAGNET)
        else:
            camp.pc.add_badge(gears.meritbadges.TagReactionBadge(
                "DeadZone Hero", "You united the deadzone to fight Cetus.",
                {gears.personality.DeadZone: 10, gears.factions.TerranDefenseForce: -10}
            ))
        camp.eject()


class TDFMissilesEnding(Plot):
    LABEL = "DZDCEND_TDFMISSILES"
    active = True
    scope = True

    def t_START(self, camp: gears.GearHeadCampaign):
        pbge.alert("The bombardment from the Voice of Iijima leaves a crater a kilometer across. No remains of Cetus are ever found, and the biomonster is presumed eliminated.")
        pbge.alert("The meagre farmland around {} is polluted by the fallout. Though the Terran Federation provides food aid to the community, the trust between them has been lost.".format(camp.campdata[DZDCVAR_CETUS_TOWN]))
        pbge.alert("You are welcomed as a hero in the greenzone, though a part of you continues to wonder if this is truly over...")
        total_qol = get_current_qol_total(camp, self.elements["DZ_ROADMAP"])
        if total_qol < camp.campdata["INITIAL_QOL"]:
            camp.pc.add_badge(DISASTER_MAGNET)
        camp.pc.add_badge(gears.meritbadges.TagReactionBadge(
            "GreenZone Hero", "You helped the Terran Defense Force to defeat Cetus before it could reach the green zone.",
            {gears.personality.DeadZone: -10, gears.personality.GreenZone: 10}
        ))
        camp.eject()


