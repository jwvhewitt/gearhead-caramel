import gears
from pbge.plots import Plot, Adventure, PlotState
from game.content.plotutility import LMSkillsSelfIntro
import pbge
from pbge.dialogue import Offer, ContextTag
from game import teams, ghdialogue
from game.ghdialogue import context
import pygame
import random
from game.content.plotutility import AdventureModuleData
from game.content import gharchitecture, ghterrain, ghrooms, ghwaypoints, ghcutscene, plotutility

WIN_FIGHT_ONE = "WIN_FIGHT_ONE"
WIN_FINAL_BATTLE = "WIN_FINAL_BATTLE"


class BearBastardMechaCampStub(Plot):
    LABEL = "SCENARIO_BEARBASTARDSMECHACAMP"
    active = True
    scope = True
    # Creates a Bear Bastard's Mecha Camp adventure.

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Bear Bastard's Mecha Camp",
        "Learn everything you need to know about being a mecha pilot from a notorious bandit hoping to cash in on his involvement in the Typhon Incident. Fun and educational!",
        (157, 9, 9), "VHS_BearBastardsMechaCamp.png", convoborder="sys_convoborder_bbmc.png"
    )

    def custom_init(self, nart):
        """Load the features."""
        self.ADVENTURE_MODULE_DATA.apply(nart.camp)

        myplot = self.add_first_locale_sub_plot(nart, locale_type="BBMC_SceneOne", ident="SCENE_ONE")
        self.elements["BEARBASTARD"] = myplot.elements["NPC"]
        the_park = myplot.elements["LOCALE"]
        park_exit = myplot.elements["ENTRANCE"]
        park_statue = myplot.elements["STATUE"]

        # Create the other three campers now, so they can get passed around to the other plots as needed.
        campers = [
            gears.selector.random_character(rank=15, current_year=157, combatant=True,
                                            local_tags=[gears.personality.GreenZone, ],
                                            gender=gears.genderobj.Gender.get_default_male()),
            gears.selector.random_character(rank=15, current_year=157, combatant=True,
                                            local_tags=[gears.personality.GreenZone, ],
                                            gender=gears.genderobj.Gender.get_default_female()),
            gears.selector.random_character(rank=15, current_year=157, combatant=True,
                                            local_tags=[gears.personality.GreenZone, ],
                                            gender=gears.genderobj.Gender.get_default_nonbinary())
        ]
        random.shuffle(campers)
        for c in campers:
            c.mecha_pref = "CBG-87 Ice Wind"
            c.experience[c.TOTAL_XP] += 500

        # We will name the campers ACAM, BCAM, and CCAM, as is the tradition.
        self.elements["ACAM"] = campers[0]
        self.elements["BCAM"] = campers[1]
        self.elements["CCAM"] = campers[2]

        # Add the cabin before Scene Two, since this will be the "home base" of the campers.
        self.add_sub_plot(nart, "BBMC_SceneThree", ident="SCENE_THREE")

        self.add_sub_plot(nart, "BBMC_SceneTwo", ident="SCENE_TWO")

        self.add_sub_plot(nart, "BBMC_FinalBattle", ident="FINAL_BATTLE")

        self.add_sub_plot(nart, "BBMC_Graduation", ident="GRADUATION",
                          elements={"LOCALE": the_park, "ENTRANCE": park_exit, "STATUE": park_statue})

        return True

    def SCENE_ONE_WIN(self, camp):
        self.subplots["SCENE_TWO"].start_first_battle(camp)

    def t_GOTOCABIN(self, camp: gears.GearHeadCampaign):
        camp.go(self.subplots["SCENE_THREE"].elements["ENTRANCE"])

    def SCENE_TWO_WIN(self, camp):
        camp.go(self.subplots["SCENE_THREE"].elements["ENTRANCE"])

    def SCENE_THREE_WIN(self, camp):
        self.subplots["FINAL_BATTLE"].start_final_battle(camp)

    def FINAL_BATTLE_WIN(self, camp):
        self.subplots["GRADUATION"].activate(camp)
        self.subplots["GRADUATION"].go_to_graduation(camp)


class Graduation(Plot):
    LABEL = "BBMC_Graduation"
    active = False
    scope = "LOCALE"

    def custom_init(self, nart):
        # Not much to do here, since the park has already been created...
        self.elements["ENTRANCE"].plot_locked = True
        self.gave_speech = False
        return True

    def go_to_graduation(self, camp):
        self.elements["LOCALE"].place_gears_near_spot(*self.elements["STATUE"].pos,
                                                      self.elements["LOCALE"].civilian_team,
                                                      self.elements["BEARBASTARD"], self.elements["ACAM"],
                                                      self.elements["BCAM"], self.elements["CCAM"])
        camp.go(self.elements["STATUE"])

    def LOCALE_ENTER(self, camp):
        if not self.gave_speech:
            if camp.campdata.get(WIN_FINAL_BATTLE):
                ghcutscene.SimpleMonologueDisplay(
                    "Congratulations! You've all passed Bear Bastard's Mecha Camp... a little bit better than I would have liked, but they say it's a really great teacher who gets his arse kicked by his students.",
                    self.elements["BEARBASTARD"]
                )(camp)
            else:
                ghcutscene.SimpleMonologueDisplay(
                    "Congratulations! You've all survived Bear Bastard's Mecha Camp... now the lot of you can rightfully call yourselves cavaliers, and you'll even have a little card you can stick in your wallet to prove it.",
                    self.elements["BEARBASTARD"]
                )(camp)
            ghcutscene.SimpleMonologueDisplay(
                "That's it. You can all go home now. They're holding a wedding or something here at two. I've got to move all my crap back into storage or the groundskeeper's gonna be pissed again.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            self.gave_speech = True

    def ENTRANCE_menu(self, camp, thingmenu):
        thingmenu.desc = "Are you ready to leave the camp?"
        thingmenu.add_item("It's time to go.", self._end_adventure)
        thingmenu.add_item("Stay here for a bit longer.", None)

    def _end_adventure(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You're still not sure that you got your money's worth, but one thing is certain: you'll never forget Bear Bastard's Mecha Camp.")
        camp.eject()

    def BEARBASTARD_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "Sorry about trying to turn everyone against you in that final battle, but what that really means is you're my best student. I'm sure I'll be seeing you around... unless you see me first.",
            ContextTag([context.HELLO]), allow_generics=False
        ))
        return mylist

    def ACAM_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["ACAM"]
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            mylist.append(Offer(
                "See you later, [audience]. Hopefully we'll meet again. Actually I'm quite sure of it.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "That was quite the experience, wasn't it? [GOODBYE]",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        mylist.append(Offer(
            "[GOODBYE] The next time we meet, it will be in combat.",
            ContextTag([context.UNFAVORABLE_HELLO]), allow_generics=False
        ))
        return mylist

    def BCAM_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["BCAM"]
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            mylist.append(Offer(
                "I'm quite sure we're going to meet again, [audience]. Maybe we'll have an adventure together sometime.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "I guess this is the last time we're ever going to see each other... [GOODBYE]",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        mylist.append(Offer(
            "[GOODBYE] The next time we meet, I will [threat].",
            ContextTag([context.UNFAVORABLE_HELLO]), allow_generics=False
        ))
        return mylist

    def CCAM_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["CCAM"]
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            mylist.append(Offer(
                "It was an honor to fight at your side, [audience]. Hopefully we'll get the chance to do it again soon.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "You know, I didn't expect this to be quite so awkward... [GOODBYE]",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        mylist.append(Offer(
            "[GOODBYE] They say you never forget the people you trained with... and I promise, I will not forget you.",
            ContextTag([context.UNFAVORABLE_HELLO]), allow_generics=False
        ))
        return mylist


class FinalBattle(Plot):
    LABEL = "BBMC_FinalBattle"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")

        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(
            40, 40, "Last Hope Quarry", player_team=team1, scale=gears.scale.MechaScale,
            combat_music="Jethro on the Run.ogg", exploration_music="A Surprising Encounter.ogg",
            environment=gears.tags.GroundEnv
        )
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        a1, a2 = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        self.register_element("ROOM1", pbge.randmaps.rooms.OpenRoom(anchor=a1), dident="LOCALE")
        self.register_element("ROOM3", ghrooms.MSRuinsRoom(15, 15, anchor=a2), dident="LOCALE")

        team2 = self.register_element("TEAM2", teams.Team(name="Enemy Team", enemies=[team1]), dident="ROOM3")

        self.register_element("ENTRANCE1", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle),
                              dident="ROOM1")

        self.movers = list()
        self.temp_mecha = list()

        self.intro_ready = True
        self.step_counter = 0
        self.combat_intro_ready = True
        self.end_combat_ready = True

        return True

    def move_npc(self, camp, npcid):
        mymover = plotutility.CharacterMover(
            camp, self, self.elements[npcid], self.elements["LOCALE"], self.elements["TEAM2"], upgrade_mek=False,
            suppress_warnings=True
        )
        self.movers.append(mymover)

    def start_final_battle(self, camp: gears.GearHeadCampaign):
        # Give the PC the practice mecha
        self.practice_mek = gears.selector.get_design_by_full_name("CBG-87b Command Ice Wind")
        self.original_pc_mek = camp.get_pc_mecha(camp.pc)
        camp.party.append(self.practice_mek)
        camp.assign_pilot_to_mecha(camp.pc, self.practice_mek)
        if self.original_pc_mek:
            self.practice_mek.colors = self.original_pc_mek.colors
        self.move_npc(camp, "ACAM")
        self.move_npc(camp, "BCAM")
        self.move_npc(camp, "CCAM")
        self.move_npc(camp, "BEARBASTARD")

        camp.go(self.elements["ENTRANCE1"])

    def LOCALE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert("In the morning, everyone heads back to Last Hope Quarry for one final combat practice.")
            self.intro_ready = False

    def _switch_teams(self, camp, npc):
        camp.scene.local_teams[npc.get_root()] = camp.scene.player_team
        camp.party.append(npc)
        camp.party.append(npc.get_root())
        self.temp_mecha.append(npc.get_root())

    def TEAM2_ACTIVATETEAM(self, camp: gears.GearHeadCampaign):
        if self.combat_intro_ready:
            ghcutscene.SimpleMonologueDisplay(
                "Alright, we've got one last fight practice: everybody against everybody else. In any battle royale like this, the best strategy is to gang up against the strongest fighter... so that's why we're all gonna take out {} first!".format(
                    camp.pc),
                self.elements["BEARBASTARD"].get_root()
            )(camp)
            ACam: gears.base.Character = self.elements["ACAM"]
            BCam: gears.base.Character = self.elements["BCAM"]
            CCam: gears.base.Character = self.elements["CCAM"]
            num_defectors = 0
            if ACam.relationship and gears.relationships.RT_LANCEMATE in ACam.relationship.tags:
                ghcutscene.SimpleMonologueDisplay(
                    "No way. You're the only person not piloting one of these dispose-a-meks. I'm siding with {}!".format(
                        camp.pc),
                    ACam.get_root()
                )(camp, False)
                self._switch_teams(camp, ACam)
                num_defectors += 1

            if BCam.relationship and gears.relationships.RT_LANCEMATE in BCam.relationship.tags:
                ghcutscene.SimpleMonologueDisplay(
                    "Nice try, Bear Bastard, but you've clearly got the better mek. I'm joining {}!".format(camp.pc),
                    BCam.get_root()
                )(camp, False)
                self._switch_teams(camp, BCam)
                num_defectors += 1

            if CCam.relationship and gears.relationships.RT_LANCEMATE in CCam.relationship.tags:
                ghcutscene.SimpleMonologueDisplay(
                    "I still haven't forgiven you over the exploding present, Bear Bastard. I'm team {} from now on!".format(
                        camp.pc),
                    CCam.get_root()
                )(camp, False)
                self._switch_teams(camp, CCam)
                num_defectors += 1

            if num_defectors < 1:
                defector = random.choice([ACam, BCam, CCam])
                defector.relationship = camp.get_relationship(defector)
                defector.relationship.tags.add(gears.relationships.RT_LANCEMATE)
                ghcutscene.SimpleMonologueDisplay(
                    "That's not fair at all. I'm going to join {}!".format(camp.pc),
                    defector.get_root()
                )(camp, False)
                self._switch_teams(camp, defector)
                camp.egg.dramatis_personae.add(defector)

            camp.scene.update_party_position(camp)

            self.combat_intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        if self.end_combat_ready:
            myteam = self.elements["TEAM2"]

            if len(myteam.get_members_in_play(camp)) < 1:
                ghcutscene.SimpleMonologueDisplay(
                    "Alright, you win! You win! Let's head back to the park so I can put this defeat behind me.",
                    self.elements["BEARBASTARD"]
                )(camp)
                camp.campdata[WIN_FINAL_BATTLE] = True
            else:
                ghcutscene.SimpleMonologueDisplay(
                    "And there's your final lesson as a cavalier- sometimes losing is part of the game. But at least it wasn't your mek, right? Let's go back to the park for the closing ceremony.",
                    self.elements["BEARBASTARD"]
                )(camp)
                camp.campdata[WIN_FINAL_BATTLE] = False

            for m in self.movers:
                m(camp)
            if self.elements["ACAM"] in camp.party:
                camp.party.remove(self.elements["ACAM"])
            if self.elements["BCAM"] in camp.party:
                camp.party.remove(self.elements["BCAM"])
            if self.elements["CCAM"] in camp.party:
                camp.party.remove(self.elements["CCAM"])
            camp.assign_pilot_to_mecha(camp.pc, self.original_pc_mek)
            camp.party.remove(self.practice_mek)
            for mek in self.temp_mecha:
                if mek in camp.party:
                    camp.party.remove(mek)
            camp.pc.restore_all()
            camp.dole_xp(300)

            camp.check_trigger("WIN", self)
        self.end_combat_ready = False


class TheCabinInTheDeadzone(Plot):
    LABEL = "BBMC_SceneThree"
    active = True
    scope = True

    def custom_init(self, nart):
        # Create the cabin.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            50, 50, "The Cabin", player_team=team1, civilian_team=team2,
            combat_music="Jethro on the Run.ogg", exploration_music="Good Night.ogg",
            attributes=(gears.tags.SCENE_BUILDING, gears.tags.SCENE_PUBLIC),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(
            intscene, gharchitecture.ResidentialBuilding(wall_terrain=ghterrain.WoodenWall,
                                                         decorate=gharchitecture.ResidentialDecor())
        )
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE")
        foyer = self.register_element(
            'BEDROOM', pbge.randmaps.rooms.ClosedRoom(20, 20, anchor=pbge.randmaps.anchors.south),
            dident="LOCALE"
        )
        foyer.contents.append(team2)
        team2.contents.append(self.elements["ACAM"])
        team2.contents.append(self.elements["BCAM"])
        team2.contents.append(self.elements["CCAM"])

        subroom = pbge.randmaps.rooms.Room(15, 15, anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(subroom)
        anchors = [pbge.randmaps.anchors.northwest, pbge.randmaps.anchors.northeast,
                   pbge.randmaps.anchors.southwest, pbge.randmaps.anchors.southeast]
        random.shuffle(anchors)
        for t in range(3):
            myanc = anchors.pop()
            myroom = pbge.randmaps.rooms.Room(3, 3, anchor=myanc)
            subroom.contents.append(myroom)
            myroom.contents.append(ghwaypoints.RecoveryBed(anchor=pbge.randmaps.anchors.middle))
        pcroom = pbge.randmaps.rooms.Room(3, 3, anchor=anchors[0])
        subroom.contents.append(pcroom)
        mybed = self.register_element("BED", ghwaypoints.RecoveryBed(
            name="Your Bed", desc="This is where you are going to sleep tonight.",
            plot_locked=True, anchor=pbge.randmaps.anchors.middle
        ))
        pcroom.contents.append(mybed)
        # Add a locker to the foot of the PC's bed. Make sure it has a complete minimal set of armor + weapons,
        # plus some extra goodies.
        mylocker = ghwaypoints.AmmoBox(treasure_rank=5, treasure_amount=50, anchor=pbge.randmaps.anchors.south)
        mylocker.contents.append(gears.selector.get_design_by_full_name("Leather Jacket"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Leather Jacket"))
        mylocker.contents[-1].name = "Denim Jacket"
        mylocker.contents.append(gears.selector.get_design_by_full_name("Katana"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Teddy Hat"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Elbow Pad"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Elbow Pad"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Knee Pad"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Knee Pad"))
        mylocker.contents.append(gears.selector.get_design_by_full_name("Hounder Slug Pistol"))
        pcroom.contents.append(mylocker)
        self.elements["LOCKER"] = mylocker

        entrance = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(plot_locked=True,
                                         desc="There's nothing but kilometers of dead zone out there. Better to stay inside for the night.",
                                         anchor=pbge.randmaps.anchors.south),
            dident="BEDROOM"
        )

        intscene.contents.append(pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.StorageRoomDecor()))

        self.intro_ready = True
        self.inv_tutorial_ready = True

        # Load the character plots. ACAM was the opponent in the first fight; they get a talky-talky plot.
        self.add_sub_plot(nart, "ACAM_Plot")
        # BCAM will get a combat plot. There's something in the cabin, and it's not friendly.
        self.add_sub_plot(nart, "BCAM_Plot", ident="BPLOT")
        # CCAM will get an object interaction plot.
        self.add_sub_plot(nart, "CCAM_Plot")

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        camp.pc.restore_all()
        if self.intro_ready:
            camp.scene.place_gears_near_spot(*self.elements["ENTRANCE"].pos, self.elements["LOCALE"].civilian_team,
                                             self.elements["BEARBASTARD"])
            ghcutscene.SimpleMonologueDisplay(
                "That's nearly it for the first time. One thing left to do before going to sleep- over there in front of your bed is a foot locker with all kinds of goodies. Don't worry, no fireworks this time... I'm renting this cabin.",
                self.elements["BEARBASTARD"]
            )(camp)
            ghcutscene.SimpleMonologueDisplay(
                "Head over there, grab whatever equipment you like, and try it on.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            self.memo = "Go to your locker and get equipped."

            camp.home_base = self.elements["ENTRANCE"]

            self.intro_ready = False

    def LOCKER_BUMP(self, camp: gears.GearHeadCampaign):
        if self.inv_tutorial_ready:
            ghcutscene.SimpleMonologueDisplay(
                "Once you pick out your stuff you can see your inventory by pressing \"i\". Or you can get to it through the FieldHQ by pressing \"H\". Or you can do either with the popup menu, right click or shift enter...",
                self.elements["BEARBASTARD"]
            )(camp)
            ghcutscene.SimpleMonologueDisplay(
                "I'm tired. You might wanna check out the FieldHQ as well as your inventory, since you probably have some experience to spend. After that just go to bed since there's nothing else to do around here. We'll have the final lesson in the morning.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            camp.freeze(self.elements["BEARBASTARD"])
            self.memo = "Equip your gear, then go to bed. Tomorrow is the final exam."
            self.inv_tutorial_ready = False

    def BEARBASTARD_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if camp.scene is self.elements["LOCALE"]:
            mylist.append(Offer(
                "Go on, then... Go see what treats you have waiting in the foot locker.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        return mylist

    def BED_menu(self, camp, thingmenu):
        if self.inv_tutorial_ready:
            thingmenu.desc += " You should choose and equip some gear before going to bed. Tomorrow is the final exam, whatever that means."
        else:
            thingmenu.add_item("Go to sleep.", self._go_to_final_scene)
            thingmenu.add_item("Stay up for a bit longer.", None)

    def _go_to_final_scene(self, camp):
        camp.check_trigger("WIN", self)

    def BPLOT_LOSE(self, camp):
        # PC must've gotten taken down in the combat. But since this is the tutorial, we don't want them to die...
        # restore the PC and jump straight to the final combat.
        pbge.alert("Everything goes dark...")
        pbge.alert(
            "You wake up the next morning in your camp bed, a bit sore but still alive. It's time for the final exam.")
        self._go_to_final_scene(camp)


class CCamAirCon(Plot):
    LABEL = "CCAM_Plot"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        compyroom = self.register_element("COMPYROOM", pbge.randmaps.rooms.OpenRoom(5, 5), dident="LOCALE")
        compy = self.register_element("COMPY", ghwaypoints.RetroComputer(name="Cabin Control", plot_locked=True,
                                                                         desc="This computer runs all the utilities in the cabin."),
                                      dident="COMPYROOM")

        self.learned_of_problem = False
        self.solved_problem = False
        self.told_solution = False
        return True

    def CCAM_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if self.told_solution:
            mylist.append(Offer(
                "Tomorrow is the final exam. Knowing Bear Bastard, it's going to be something rough.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "Who turned on the air conditioning?! This is Last Hope, in September. If I wanted to camp out in Norstead I would've gone to Norstead.",
                ContextTag([context.HELLO]), allow_generics=False, effect=self._learn_of_problem
            ))

            mylist.append(Offer(
                "A little chilly? It's bloody freezing is what it is. I tried to find the thermostat but there certainly isn't one in this room.",
                ContextTag([context.CUSTOM]), allow_generics=False,
                data={"reply": "It is a little chilly in here..."}
            ))

            if self.solved_problem:
                mylist.append(Offer(
                    "[THANK_YOU] I can feel my fingers and toes again.",
                    ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                    data={
                        "reply": "I turned off the air conditioning. The cabin should be a reasonable temperature soon."}
                ))

        return mylist

    def _learn_of_problem(self, camp):
        self.learned_of_problem = True

    def _make_friend(self, camp: gears.GearHeadCampaign):
        self.told_solution = True
        self.elements["CCAM"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["CCAM"].relationship.reaction_mod += 10
        camp.egg.dramatis_personae.add(self.elements["CCAM"])

    def COMPY_menu(self, camp, thingmenu):
        if self.learned_of_problem and not self.solved_problem:
            thingmenu.add_item("Turn the air conditioner down to a reasonable temperature.", self._turn_off_aircon)

    def _turn_off_aircon(self, camp):
        self.solved_problem = True


class CCamMonoPuffs(Plot):
    LABEL = "CCAM_Plot"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        self.returned_puffs = False
        mofo_puff = self.register_element(
            "MONOPUFF", gears.base.Treasure(name="Mono Puffs", desc="A shrinkwrapped package of snack cakes.", value=10,
                                            weight=2), dident="LOCALE"
        )
        return True

    def CCAM_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if self.returned_puffs:
            mylist.append(Offer(
                "Now that my blood sugar level is back to normal, I feel much better. See you in the morning, [audience].",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "I brought a pack of Mono Puffs all the way from Ipshil, and now I can't find them! I bet one of the other campers ate them...",
                ContextTag([context.HELLO]), allow_generics=False
            ))

            if camp.party_has_item(self.elements["MONOPUFF"]):
                mylist.append(Offer(
                    "[THANK_YOU] I won't forget that you returned my snacks... When I'm hungry, I'm just not myself.",
                    ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                    data={"reply": "I believe these are your Mono Puffs?"}
                ))

        return mylist

    def _make_friend(self, camp: gears.GearHeadCampaign):
        self.returned_puffs = True
        self.elements["CCAM"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["CCAM"].relationship.reaction_mod += 10
        camp.egg.dramatis_personae.add(self.elements["CCAM"])
        if self.elements["MONOPUFF"] in camp.pc.inv_com:
            camp.pc.inv_com.remove(self.elements["MONOPUFF"])


class BCamMouse(Plot):
    LABEL = "BCAM_Plot"
    active = True
    scope = True

    def custom_init(self, nart):
        # Add the basement.
        team1 = teams.Team(name="Player Team")
        intscene = gears.GearHeadScene(
            50, 50, "The Creepy Basement", player_team=team1,
            combat_music="Jethro on the Run.ogg", exploration_music="Good Night.ogg",
            attributes=(gears.tags.SCENE_BUILDING,), scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(
            intscene, gharchitecture.ResidentialBuilding(wall_terrain=ghterrain.WoodenWall,
                                                         decorate=gharchitecture.RundownFactoryDecor())
        )
        self.register_scene(nart, intscene, intscenegen, ident="BASEMENT")

        room1 = self.register_element("ROOM1", pbge.randmaps.rooms.ClosedRoom(5, 5), dident="LOCALE")
        room2 = self.register_element("ROOM1", pbge.randmaps.rooms.ClosedRoom(5, 5), dident="BASEMENT")

        # Connect the scenes.
        plotutility.TrapdoorToStairsUpConnector(
            nart, self, self.elements["LOCALE"], intscene, room1=room1, room2=room2
        )

        intscene.contents.append(pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.StorageRoomDecor()))
        intscene.contents.append(pbge.randmaps.rooms.ClosedRoom())
        mychest = ghwaypoints.OldCrate()
        mychest.contents.append(gears.selector.get_design_by_full_name("5 Pack Quick Fix Pill"))
        mychest.contents.append(gears.selector.get_design_by_full_name("5 Pack Antidote"))
        intscene.contents[-1].contents.append(mychest)

        mouseroom = self.register_element("MOUSEROOM",
                                          pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.StorageRoomDecor()),
                                          dident="BASEMENT")
        team2 = self.register_element("MTEAM", teams.Team("Mouse Team", enemies=(team1,)), dident="MOUSEROOM")
        team2.contents.append(gears.selector.get_design_by_full_name("Mechanical Mouse"))

        self.dealt_with_mouse = False
        self.did_mouse_intro = False
        self.told_about_mouse = False
        self.got_reward = False
        return True

    def BCAM_offers(self, camp):
        mylist = list()
        if camp.scene is self.elements["LOCALE"]:
            if self.got_reward:
                mylist.append(Offer(
                    "Now that I know this cabin is safe, I can finally get some sleep.",
                    ContextTag([context.HELLO]), allow_generics=False
                ))

            else:
                if self.told_about_mouse:
                    mylist.append(Offer(
                        "How am I supposed to rest knowing there's a robotic rat crawling around inside the walls?!",
                        ContextTag([context.HELLO]), allow_generics=False
                    ))
                else:
                    mylist.append(Offer(
                        "I want to go to bed, but I can hear something crawling around in the walls. I think this cabin is infested with rats or something.",
                        ContextTag([context.HELLO]), allow_generics=False
                    ))
                if self.dealt_with_mouse:
                    mylist.append(Offer(
                        "[THANKS_FOR_HELP] Now I can finally go to bed.",
                        ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                        data={"reply": "Don't worry. The mechanical mouse has been dealt with."}
                    ))

                elif self.did_mouse_intro and not self.told_about_mouse:
                    mylist.append(Offer(
                        "THIS CABIN IS INFESTED WITH ROBOT RATS?! Great! Now I'll never get to sleep.",
                        ContextTag([context.CUSTOM]), allow_generics=False, effect=self._tell_about_mouse,
                        data={"reply": "Yeah, I saw it in the basement. It's a weird robotic mouse."}
                    ))
                else:
                    mylist.append(Offer(
                        "YOU ARE NOT HELPING ME TO RELAX RIGHT NOW!!!",
                        ContextTag([context.CUSTOM]), allow_generics=False,
                        data={
                            "reply": "Don't worry. We're right on the edge of the dead zone, and there are far worse things lurking outside."}
                    ))
                if not self.dealt_with_mouse:
                    mylist.append(Offer(
                        "Yeah, we'll see how that goes...",
                        ContextTag([context.CUSTOM]), allow_generics=False,
                        data={"reply": "Good luck with that."}
                    ))

        return mylist

    def _make_friend(self, camp: gears.GearHeadCampaign):
        self.elements["BCAM"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["BCAM"].relationship.reaction_mod += 10
        camp.egg.dramatis_personae.add(self.elements["BCAM"])
        self.got_reward = True

    def _tell_about_mouse(self, camp):
        self.told_about_mouse = True

    def MTEAM_ACTIVATETEAM(self, camp: gears.GearHeadCampaign):
        if not self.did_mouse_intro:
            if gears.personality.DeadZone in camp.pc.personality:
                pbge.alert(
                    "Without warning, the denizen of this dusty place attacks you! It seems to be a mechanical mouse... this must be some kind of robot monster built in the green zone.")
            elif gears.personality.GreenZone in camp.pc.personality:
                pbge.alert(
                    "Without warning, the denizen of this dusty place attacks you! It's some kind of mechanical mouse... it must have wandered into Last Hope from the PreZero ruins of the dead zone.")
            else:
                pbge.alert(
                    "Without warning, the denizen of this dusty place attacks you! It appears to be some kind of feral robotic hamster... this confirms all the bad things you've ever heard about living on Earth.")
            self.did_mouse_intro = True

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        if camp.scene is self.elements["BASEMENT"]:
            myteam = self.elements["MTEAM"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.dealt_with_mouse = True
            elif not camp.pc.is_operational():
                camp.pc.restore_all()
                camp.check_trigger("LOSE", self)


class ACamGracious(Plot):
    LABEL = "ACAM_Plot"
    active = True
    scope = "LOCALE"

    @classmethod
    def matches(cls, pstate):
        npc: gears.base.Character = pstate.elements["ACAM"]
        return npc.personality.intersection(
            {gears.personality.Cheerful, gears.personality.Easygoing, gears.personality.Fellowship})

    def custom_init(self, nart):
        self.had_convo = False
        return True

    def ACAM_offers(self, camp):
        mylist = list()
        if self.had_convo:
            mylist.append(Offer(
                "I'm going to go to bed soon. Tomorrow's another exciting time!",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        elif camp.campdata.get(WIN_FIGHT_ONE):
            mylist.append(Offer(
                "Congratulations on your win, [audience]. I did my best but you came out on top.",
                ContextTag([context.HELLO]), allow_generics=False
            ))

            mylist.append(Offer(
                "[THANK_YOU] Maybe we'll get a chance to fight on the same team, someday.",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                data={"reply": "Thanks. You fought well."}
            ))

            mylist.append(Offer(
                "[REALLY?] Well, maybe we'll get a chance to face each other in combat again someday.",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_enemy,
                data={"reply": "You better remember it, because I'm the best pilot!"}
            ))

        else:
            mylist.append(Offer(
                "You put up a good fight, [audience]. Well done out there.",
                ContextTag([context.HELLO]), allow_generics=False
            ))

            mylist.append(Offer(
                "[THANK_YOU] Hopefully someday we'll be able to fight on the same team.",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                data={"reply": "Congratulations on defeating me."}
            ))

            mylist.append(Offer(
                "[REALLY?] I look forward to our next battle, then.",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_enemy,
                data={"reply": "You just got lucky; next time I'll [threat]!"}
            ))

        return mylist

    def _make_friend(self, camp: gears.GearHeadCampaign):
        self.had_convo = True
        self.elements["ACAM"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["ACAM"].relationship.reaction_mod += 10
        camp.egg.dramatis_personae.add(self.elements["ACAM"])

    def _make_enemy(self, camp):
        self.had_convo = True
        self.elements["ACAM"].relationship.expectation = gears.relationships.E_RIVAL
        camp.egg.dramatis_personae.add(self.elements["ACAM"])


class ACamResentful(Plot):
    LABEL = "ACAM_Plot"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        self.had_convo = False
        return True

    def ACAM_offers(self, camp):
        mylist = list()
        if self.had_convo:
            mylist.append(Offer(
                "I'm going to go to bed... Today was a rough time.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
        elif camp.campdata.get(WIN_FIGHT_ONE):
            mylist.append(Offer(
                "Don't think you're so great just because you beat me...  You wouldn't even be at this camp if you weren't a nobody like the rest of us.",
                ContextTag([context.HELLO]), allow_generics=False
            ))

            mylist.append(Offer(
                "[YOU_COULD_BE_RIGHT] Sorry for taking things so personal... Maybe next time we can fight on the same team, ok?",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                data={"reply": "Winning and losing is all part of being a cavalier. You put up a good fight out there."}
            ))

            mylist.append(Offer(
                "[SWEAR] Someday we're gonna fight again, and next time I'm gonna [threat]!",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_enemy,
                data={"reply": "You're the only nobody I see in this room."}
            ))

        else:
            mylist.append(Offer(
                "How does it feel to be a loser, [audience]? I kicked your arse out there.",
                ContextTag([context.HELLO]), allow_generics=False
            ))

            mylist.append(Offer(
                "[SWEAR] Why'd you have to be gracious in defeat like that? Now I feel like an arsehole! The next time we meet in battle, I'm going to [threat]!",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_enemy,
                data={"reply": "Yes, and I congratulate you on your victory."}
            ))

            mylist.append(Offer(
                "[REALLY?] Then I guess the next time we're in battle, we better be on the same team. I like your attitude, [audience].",
                ContextTag([context.CUSTOM]), allow_generics=False, effect=self._make_friend,
                data={"reply": "Don't overestimate yourself. Next time I'll [threat]."}
            ))

        return mylist

    def _make_friend(self, camp: gears.GearHeadCampaign):
        self.had_convo = True
        self.elements["ACAM"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["ACAM"].relationship.reaction_mod += 10
        camp.egg.dramatis_personae.add(self.elements["ACAM"])

    def _make_enemy(self, camp):
        self.had_convo = True
        self.elements["ACAM"].relationship.attitude = gears.relationships.A_RESENT
        camp.egg.dramatis_personae.add(self.elements["ACAM"])


class SceneTwo(Plot):
    LABEL = "BBMC_SceneTwo"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")

        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(
            40, 40, "Last Hope Quarry", player_team=team1, scale=gears.scale.MechaScale,
            combat_music="Jethro on the Run.ogg", exploration_music="A Surprising Encounter.ogg",
            environment=gears.tags.GroundEnv
        )
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        a1, a2 = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        self.register_element("ROOM1", pbge.randmaps.rooms.OpenRoom(anchor=a1), dident="LOCALE")
        self.register_element("ROOM2", pbge.randmaps.rooms.OpenRoom(anchor=a2), dident="LOCALE")
        self.register_element("ROOM3", ghrooms.DragonToothRoom(15, 15, anchor=pbge.randmaps.anchors.middle),
                              dident="LOCALE")

        team2 = self.register_element("TEAM2", teams.Team(name="Enemy Team", enemies=[team1]), dident="ROOM2")

        self.register_element("ENTRANCE1", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle),
                              dident="ROOM1")
        self.register_element("ENTRANCE3", pbge.scenes.waypoints.Waypoint(), dident="ROOM3")
        self.intro_ready = True
        self.step_counter = 0
        self.combat_intro_ready = True
        self.end_combat_ready = True

        return True

    def start_first_battle(self, camp: gears.GearHeadCampaign):
        # Give the PC the practice mecha
        self.practice_mek = gears.selector.get_design_by_full_name("CBG-87 Ice Wind")
        self.original_pc_mek = camp.get_pc_mecha(camp.pc)
        camp.party.append(self.practice_mek)
        camp.assign_pilot_to_mecha(camp.pc, self.practice_mek)
        if self.original_pc_mek:
            self.practice_mek.colors = self.original_pc_mek.colors

        self.mymover = plotutility.CharacterMover(
            camp, self, self.elements["ACAM"], self.elements["LOCALE"], self.elements["TEAM2"], upgrade_mek=False,
            suppress_warnings=True
        )

        camp.go(self.elements["ENTRANCE1"])

    def LOCALE_ENTER(self, camp):
        if self.intro_ready:
            ghcutscene.SimpleMonologueDisplay(
                "Alright, so Last Hope doesn't really have a mecha arena... but it does have this quarry! That's why I hold the camp on weekends, so no-one accidentally steps on a bulldozer or nothing. Quarries are a great place for mecha battles.",
                self.elements["BEARBASTARD"]
            )(camp)
            ghcutscene.SimpleMonologueDisplay(
                "Your mecha for this fight will be the Ice Wind. It's a versatile, high tech machine... and I can get five of 'em together in a value pack. You'll start in exploration mode, just like moving around at the park.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            ghcutscene.SimpleMonologueDisplay(
                "By the way, if you haven't read the instruction manual yet, now would be a great time to start. You should be able to find it under your seat. In the event of a crash over water you can also use it as a floatation device. Too much water is dangerous; that's why I never touch the stuff.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            self.intro_ready = False

    def t_PCMOVE(self, camp):
        if self.step_counter >= 0:
            self.step_counter += 1
            if self.step_counter > 9:
                ghcutscene.SimpleMonologueDisplay(
                    "At some point in time, you're gonna see the \"Danger Zone\". It'll look like a flashing red line on the ground. Usually you find 'em on the highway. This line shows an enemy mecha's sensor range; move past the line and combat starts.",
                    self.elements["BEARBASTARD"]
                )(camp)
                self.step_counter = -1

    def TEAM2_ACTIVATETEAM(self, camp: gears.GearHeadCampaign):
        if self.combat_intro_ready:
            npc: gears.base.Character = self.elements["ACAM"]
            ghcutscene.SimpleMonologueDisplay(
                "You are now fighting {}... Combat adds a few more controls to yer screen. On the top left, those are your action categories. Then in the middle, that's your action clock. Over on the top right is your action selector.".format(
                    npc),
                self.elements["BEARBASTARD"]
            )(camp)
            ghcutscene.SimpleMonologueDisplay(
                "There's a whole bunch of different things you can do in combat. Usually you get to do two actions on your turn, as shown by the clock. You can spend half an action on movement and still do something else, as long as that clock section stays white.",
                self.elements["BEARBASTARD"]
            )(camp, False)
            ghcutscene.SimpleMonologueDisplay(
                "To see all your possible actions you can scroll through them with either the middle mouse wheel or the arrow keys on your keyboard. Some actions have multiple options; you can click those or press left and right to move through them.",
                self.elements["BEARBASTARD"]
            )(camp, False)

            if camp.party_has_skill(gears.stats.Repair):
                ghcutscene.SimpleMonologueDisplay(
                    "Remember that you've got the repair skill. If your mek gets damaged- and it will get damaged, these things are practically made of cardboard- you can use that skill on yourself to heal up.",
                    self.elements["BEARBASTARD"]
                )(camp, False)
            if camp.party_has_skill(gears.stats.Stealth):
                ghcutscene.SimpleMonologueDisplay(
                    "You can use yer stealth skill to hide. This will make it much harder for enemies to hit you, and much easier for you to hit them. Doesn't always work but it's worth a shot.",
                    self.elements["BEARBASTARD"]
                )(camp, False)

            if camp.party_has_skill(gears.stats.Science):
                ghcutscene.SimpleMonologueDisplay(
                    "Yer science skill can be used to spot weaknesses in an enemy mecha, making it more likely your shots will go through their armor. Given that these Ice Winds are barely armored at all it's probably not worth using that now..",
                    self.elements["BEARBASTARD"]
                )(camp, False)

            if camp.party_has_skill(gears.stats.Performance) or camp.party_has_skill(gears.stats.Negotiation):
                ghcutscene.SimpleMonologueDisplay(
                    "Performance can be used to inspire your allies. Negotiation can be used to charge up an ally's MP at the cost of your stamina. Since you're fighting alone, neither of these skills will be useful right now.",
                    self.elements["BEARBASTARD"]
                )(camp, False)

            if npc.has_skill(gears.stats.Stealth):
                ghcutscene.SimpleMonologueDisplay(
                    "Watch out because {npc} knows Stealth; {npc.gender.subject_pronoun} can disappear like a ninja at any time. You can use your search skill to find {npc.gender.object_pronoun}, or just hit {npc.gender.object_pronoun} with a damaging shot.".format(
                        npc=npc),
                    self.elements["BEARBASTARD"]
                )(camp, False)

            self.combat_intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        if self.end_combat_ready:
            myteam = self.elements["TEAM2"]

            if len(myteam.get_members_in_play(camp)) < 1:
                ghcutscene.SimpleMonologueDisplay(
                    "Congratulations! You've won the mecha combat. That's just about all the training we have for today... Let's head back to the cabin.",
                    self.elements["BEARBASTARD"]
                )(camp)
                camp.campdata[WIN_FIGHT_ONE] = True
            else:
                ghcutscene.SimpleMonologueDisplay(
                    "Congratulations! You've successfully ejected from a doomed mecha. That's just about all the training we have for today... Let's head back to the cabin.",
                    self.elements["BEARBASTARD"]
                )(camp)
                camp.campdata[WIN_FIGHT_ONE] = False

            self.mymover(camp)
            camp.assign_pilot_to_mecha(camp.pc, self.original_pc_mek)
            camp.party.remove(self.practice_mek)
            camp.pc.restore_all()
            camp.dole_xp(200)

            camp.check_trigger("WIN", self)
        self.end_combat_ready = False


class SceneOne(Plot):
    LABEL = "BBMC_SceneOne"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        myscene = gears.GearHeadScene(
            25, 25, "Last Hope Memorial Park", player_team=team1,
            scale=gears.scale.HumanScale, civilian_team=team2, attributes=(gears.personality.DeadZone,),
            exploration_music='Journey of Hope.ogg', combat_music='Jethro on the Run.ogg'
        )
        myscenegen = pbge.randmaps.PartlyUrbanGenerator(
            myscene, gharchitecture.HumanScaleDeadzone(), road_terrain=ghterrain.Flagstone,
            urban_area=ghrooms.GrassRoom(13, 13, anchor=pbge.randmaps.anchors.middle), road_thickness=3
        )
        statue_room = self.register_element("STATUE_ROOM", pbge.randmaps.rooms.OpenRoom(
            7, 7, (pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM),
            archi=pbge.randmaps.architect.Architecture(floor_terrain=ghterrain.Flagstone),
            anchor=pbge.randmaps.anchors.middle
        ))
        myscene.contents.append(statue_room)
        statue_room.contents.append(team2)

        entry_room = pbge.randmaps.rooms.Room(
            3, 3, (pbge.randmaps.IS_CONNECTED_ROOM,),
            anchor=pbge.randmaps.anchors.south
        )
        myscene.contents.append(entry_room)
        my_exit = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(
                desc="The way out of the park.\nYou've already paid your momey; might as well stay for the mecha camp.",
                plot_locked=True, anchor=pbge.randmaps.anchors.middle
            )
        )
        entry_room.contents.append(my_exit)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE", )

        self.register_element("STATUE", ghwaypoints.ParkStatueMan(
            name="Bear Bastard Statue",
            desc="A magnificent statue of Bear Bastard, looking as heroic as possible given the subject matter. A golden plaque at the bottom of the statue reads \"In honor of Bear Bastard, Saviour of Last Hope, Master of the Impossible\".",
            anchor=pbge.randmaps.anchors.middle
        ), dident="STATUE_ROOM")

        west_shrine_room = self.register_element(
            "_west_shrine_room", pbge.randmaps.rooms.Room(5, 15, anchor=pbge.randmaps.anchors.west), dident="LOCALE"
        )

        east_shrine_room = self.register_element(
            "_east_shrine_room", pbge.randmaps.rooms.Room(5, 15, anchor=pbge.randmaps.anchors.east), dident="LOCALE"
        )

        north_shrine_room = self.register_element(
            "_north_shrine_room", pbge.randmaps.rooms.Room(5, 5, anchor=pbge.randmaps.anchors.north), dident="LOCALE"
        )

        self.register_element(
            "DUTY_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Duty",
                desc="The plaque on this shrine reads:\n\"Let me be honest and true at all times, and never fail to fulfil my responsibilites.\"",
                anchor=pbge.randmaps.anchors.south
            ), dident="_west_shrine_room"
        )

        self.register_element(
            "FELLOWSHIP_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Fellowship",
                desc="The plaque on this shrine reads:\n\"Let me be considerate to all in everything I do, and do wrong by no one.\"",
                anchor=pbge.randmaps.anchors.north
            ), dident="_west_shrine_room"
        )

        self.register_element(
            "GLORY_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Glory",
                desc="The plaque on this shrine reads:\n\"Let me strive every moment to make myself better and better, to the best of my ability, that all may profit by it.\"",
                anchor=pbge.randmaps.anchors.middle
            ), dident="_north_shrine_room"
        )

        self.register_element(
            "JUSTICE_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Justice",
                desc="The plaque on this shrine reads:\n\"Let me think of the right and lend all my assistance to those who need it, with no regard for anything but justice.\"",
                anchor=pbge.randmaps.anchors.north
            ), dident="_east_shrine_room"
        )

        self.register_element(
            "PEACE_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Peace",
                desc="The plaque on this shrine reads:\n\"Let me act always with compassion, and wield my immense power only to protect life.\"",
                anchor=pbge.randmaps.anchors.south
            ), dident="_east_shrine_room"
        )

        self.register_element("PRESENT", gears.base.Treasure(name="Present", value=10))

        npc: gears.base.Character = self.register_element("NPC", nart.camp.get_major_npc("Bear Bastard"))
        npc.place(myscene, team=team2)
        npc.relationship = nart.camp.get_relationship(npc)
        npc.relationship.make_not_unfavorable()

        self.intro_ready = True
        self.impatience_counter = -1
        self.had_first_conversation = False
        self.finished_bump_practice = False
        self.tiles_moved = 0
        self.bumped_objects = set()
        self.had_second_conversation = False
        self.finished_pickup_practice = False
        self.opened_mecha_arena = False

        return True

    def LOCALE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert(
                "You enter Last Hope Memorial Park, eager for the first time of mecha camp. Today is the time you learn how to be a proper cavalier!")
            if camp.pc.has_badge("Typhon Slayer"):
                pbge.alert(
                    "Not that you aren't already a highly accomplished cavalier. But it never hurts to get a refresher every once in a while.")
            ghcutscene.SimpleMonologueDisplay(
                "Listen close, {pc.gender.noun}-cub! I'm Bear Bastard, hero of the Typhon Incident! I'll be running this camp for aspiring cavaliers such as yourself. Why don't you come over here so we can talk?".format(
                    pc=camp.pc),
                self.elements["NPC"]
            )(camp)
            self.intro_ready = False
            self.impatience_counter = 0

    def t_HALFMINUTE(self, camp):
        if self.impatience_counter > -1:
            if not self.had_first_conversation:
                self.impatience_counter += 1
                if self.impatience_counter == 2:
                    ghcutscene.SimpleMonologueDisplay(
                        "Alright, I can see you've got some problems with doing what you're told. That's actually kinda relateable. Just see if you can move over to me and we can start the conversation.",
                        self.elements["NPC"]
                    )(camp)

                elif self.impatience_counter == 3:
                    ghcutscene.SimpleMonologueDisplay(
                        "Okay, you know what? Let's try a visualization exercise. Pretend you've got a keyboard and/or a mouse right there in front of you. Or a joypad if you're into that steamy stuff. Imagine an orange square on the ground.",
                        self.elements["NPC"]
                    )(camp)
                    ghcutscene.SimpleMonologueDisplay(
                        "You can move this orange cursor around with the power of your mind, by which I mean your mouse or numeric keypad or whatever. Move the cursor over to me and left click. Or press enter. That should get the job done.",
                        self.elements["NPC"]
                    )(camp, False)
            elif self.finished_bump_practice and not self.had_second_conversation:
                self.impatience_counter += 1
                if self.impatience_counter % 2 == 0:
                    ghcutscene.SimpleMonologueDisplay(
                        "I'm getting bored over here... finish looking around and come talk to me. It's not that big of a park.",
                        self.elements["NPC"]
                    )(camp)

    def STATUE_BUMP(self, camp):
        if not self.had_first_conversation:
            ghcutscene.SimpleMonologueDisplay(
                "Alright, so you can move. I can see how you'd get us confused, with the both of us being ruggedly handsome and all, but that statue ain't gonna talk back to you. What you need to do is come bump into me.",
                self.elements["NPC"]
            )(camp)
        elif not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["STATUE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def ENTRANCE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["ENTRANCE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def ENTRANCE_menu(self, camp, thingmenu):
        if self.opened_mecha_arena:
            thingmenu.desc = "Having finished training at the park, it's time to go to the mecha arena and learn how to fight."
            thingmenu.add_item("Go to the arena.", self._win_scene_one)
            thingmenu.add_item("Stay here a bit longer.", None)
        elif pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            thingmenu.add_item("Skip straight to the arena.", self._win_scene_one)
            thingmenu.add_item("Skip straight to the cabin.", self._go_to_cabin)
            thingmenu.add_item("Why be in such a hurry?", None)

    def _win_scene_one(self, camp: gears.GearHeadCampaign):
        self.end_plot(camp)
        camp.check_trigger("WIN", self)

    def _go_to_cabin(self, camp: gears.GearHeadCampaign):
        self.end_plot(camp)
        camp.check_trigger("GOTOCABIN")

    def DUTY_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["DUTY_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def FELLOWSHIP_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["FELLOWSHIP_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def GLORY_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["GLORY_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def JUSTICE_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["JUSTICE_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def PEACE_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["PEACE_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def NPC_offers(self, camp):
        mylist = list()
        npc: gears.base.Character = self.elements["NPC"]
        if not self.had_first_conversation:
            if camp.pc.has_badge("Typhon Slayer") or (
                    npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags):
                mylist.append(Offer(
                    "[SWEAR] It's you, [audience]! What the bloody bazookas are you doing here? You're not a beginner mecha pilot.",
                    ContextTag([context.HELLO]), effect=self._have_first_conversation, allow_generics=False
                ))
                mylist.append(Offer(
                    "Yeah, I suppose... the next technology we're going to practice is moving around and bumping into things. Take a look at some of the stuff in this park. Just walk over and bump into it, like you did for me.",
                    ContextTag([context.CUSTOM]),
                    data={"reply": "A cavalier should always keep up with the latest technology."}, allow_generics=False
                ))
                mylist.append(Offer(
                    "No scam, I've gone legit. This is me sharing my years of mecha piloting knowledge to the youngster generation. So the next lesson is moving around and bumping into stuff. Take a look at the things in this park. Just walk over and bump into 'em, like you did for me.",
                    ContextTag([context.CUSTOM]),
                    data={"reply": "I'm checking up on you; see what kind of scam you're pulling this time."},
                    allow_generics=False
                ))

            else:
                mylist.append(Offer(
                    "Good job, you can move around and interact with other people. You're going to be doing a whole lot of that as a cavalier.",
                    ContextTag([context.HELLO]), effect=self._have_first_conversation, allow_generics=False
                ))

                mylist.append(Offer(
                    "You're gonna walk around the park and bump into stuff. You might have noticed there's a bunch of things in the park. Just like starting the conversation with me, you can interact with these things by walking right up to them and seeing what happens.",
                    ContextTag([context.CUSTOM]), data={"reply": "[THANKS_FOR_ADVICE] What's next?"},
                    allow_generics=False
                ))

            mylist.append(Offer(
                "You say that now, but just wait until the next bit! We're going to try moving around and bumping into stuff! That's how you interact with most things in this messed-up world... just walk straight up to a thing and see what happens.",
                ContextTag([context.CUSTOM]),
                data={"reply": "Gee, this lesson has really been worth the money I paid so far."}, allow_generics=False
            ))


        elif not self.finished_bump_practice:
            mylist.append(Offer(
                "Your next job is to walk around for a bit and check out the things in the park. Let's do some visualization: you can do that by moving the cursor over the thing you want to examine, using either your mental mouse or spiritual numeric keypad, and left clicking or pressing enter.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
            mylist.append(Offer(
                "Ooh, now you're getting into advanced territory. Right clicking brings up your Mind Palace Popup Menu! From there you can choose to interact with the object or do a whole bunch of other things.",
                ContextTag([context.CUSTOM]), data={"reply": "What happens if I right click instead?"},
                allow_generics=False
            ))

        elif self.finished_bump_practice and not self.finished_pickup_practice:
            mylist.append(Offer(
                "I've just sent a message to your phone. You can take a look at memos by pressing 'm' or right-clicking to get the popup menu. After this, we move on to the good stuff.",
                ContextTag([context.HELLO]), allow_generics=False, effect=self._have_second_conversation
            ))

        elif self.finished_pickup_practice:
            mylist.append(Offer(
                "That's all you need to know about moving around. Next, I'm gonna teach you how to fight! Head to the park exit and we can go to Last Hope Arena.",
                ContextTag([context.HELLO]), allow_generics=False, effect=self._open_mecha_arena
            ))

        return mylist

    def _open_mecha_arena(self, camp):
        self.opened_mecha_arena = True
        self.memo = "Go to the park exit and enter mecha combat."

    def t_PCMOVE(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice and self.tiles_moved > -1:
            self.tiles_moved += 1
            if self.tiles_moved > 10:
                ghcutscene.SimpleMonologueDisplay(
                    "Wow, look at you, movin' all around the park, just like a pro!",
                    self.elements["NPC"]
                )(camp)
                self.tiles_moved = -1

    def _have_first_conversation(self, camp):
        self.had_first_conversation = True

    def _have_second_conversation(self, camp):
        # Actually isn't this the third conversation? I can't remember anymore. Whatever.
        self.had_second_conversation = True
        self.memo = "I left a present for you somewhere in this park. I'll just say, you can find it between Justice and Peace. Pretty good riddle, huh? To pick it up move to the tile where the box is, then click on that tile again."
        present: gears.base.Treasure = self.elements["PRESENT"]
        present.place(self.elements["LOCALE"], (23, 12))

    def PRESENT_GET(self, camp):
        pbge.alert("Suddenly, the box explodes in your hands!")
        pbge.my_state.view.play_anims(gears.geffects.SuperBoom(pos=camp.pc.pos),
                                      pbge.scenes.animobs.Caption("Surprise!", pos=camp.pc.pos, delay=6))
        present: gears.base.Treasure = self.elements["PRESENT"]
        if present in camp.pc.inv_com:
            camp.pc.inv_com.remove(present)
        ghcutscene.SimpleMonologueDisplay(
            "And let that be a lesson to you- you can't trust everyone you meet. That was just a firecracker but it could've been a plasma grenade or worse. This is what you call the tough love school of teaching. Come back over here; I have one last thing to discuss.",
            self.elements["NPC"]
        )(camp)
        self.memo = "Return to Bear Bastard for one more conversation."
        self.finished_pickup_practice = True

    def _complete_bump_practice(self, camp):
        self.finished_bump_practice = True
        ghcutscene.SimpleMonologueDisplay(
            "Alright, that's enough bumpin' practice for now. You can finish looking around the park, then come back and talk to me again. We've got one more lesson before you're ready to get in a mek.",
            self.elements["NPC"]
        )(camp)
        self.impatience_counter = 0
