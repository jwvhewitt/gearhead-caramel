import random

import game.content
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, PlotState
from . import dd_customobjectives
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


#   *******************************
#   ***  DZRE_BLACKMARKETBLUES  ***
#   *******************************

class BlackMarketBluesMain(Plot):
    # There are bandits raiding the highway. They're operating out of a black market near METROSCENE.
    # The player first needs to find the black market, and then will have a number of choices for how to
    # deal with the problem.
    LABEL = "DZRE_BLACKMARKETBLUES"
    UNIQUE = True
    active = True
    scope = "METRO"

    QOL = gears.QualityOfLife(prosperity=1, stability=-1)

    BMES_ENTERED = 1
    BMES_ATTACKED = 2

    def custom_init( self, nart ):
        self.add_sub_plot(
            nart, "SEEK_ENEMY_BASE", ident="MISSION",
            elements={"ENEMY_FACTION": self.elements["FACTION"], "ENEMY_BASE_NAME": "the Raider Base"}
        )
        self.black_market_found = False
        self.black_market_announced = False

        bmsp = self.add_sub_plot(
            nart, "HIVE_OF_SCUM", elements={
            "LOCALE_NAME": "{METROSCENE} Black Market".format(**self.elements),
            "LOCALE_FACTION": gears.factions.TreasureHunters, "ENTRANCE": self.elements["MISSION_GATE"]}
        )
        self.register_element("BLACK_MARKET", bmsp.elements["LOCALE"])
        self.black_market_entrance = bmsp.elements["EXIT"]
        self.black_market_entry_status = 0

        # Generate the boss of the black market.
        self.register_element("NPC", gears.selector.random_character(
            self.rank+25, local_tags=self.elements["METROSCENE"].attributes,
            camp=nart.camp, faction=gears.factions.TreasureHunters, combatant=True
        ))

        # Place a thieves guild in the black market.
        tgsp = self.add_sub_plot(
            nart, "THIEVES_GUILD", elements={
            "LOCALE": self.elements["BLACK_MARKET"],
            "FACTION": gears.factions.TreasureHunters, "ENTRANCE": None}
        )
        self.elements["GUILD"] = tgsp.elements["INTERIOR"]
        exterior = self.register_element("_exterior", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=str(tgsp.elements["INTERIOR"]))},
            door_sign=(ghterrain.CrossedSwordsTerrainEast, ghterrain.CrossedSwordsTerrainSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]
        ), dident="BLACK_MARKET")
        plotutility.TownBuildingConnection(
            nart, self, self.elements["BLACK_MARKET"], tgsp.elements["INTERIOR"],
            room2=tgsp.elements["_introom"], door2=tgsp.elements["EXIT"], move_door2=False,
            door1=exterior.waypoints["DOOR"], move_door1=False)

        # Add the rules sign.
        myroom = self.register_element("_skullroom", pbge.randmaps.rooms.OpenRoom(5,5), dident="BLACK_MARKET")
        self.register_element("SKULL_SIGN",ghwaypoints.SkullTownSign(
            name="Skull Sign", anchor=pbge.randmaps.anchors.middle,
            desc="Rules of {BLACK_MARKET} as decreed and enforced by {NPC} of {GUILD}:\n-No fighting within the market.\n-No mecha combat within the market.\n-No attacking a rival gang's safehouse.\n-No raiding within 100km of {METROSCENE}.\n-Biomonsters to be leashed at all times.\n-Bounty hunters to be shot on sight.".format(**self.elements),
            plot_locked=True
        ), dident="_skullroom")


        # Place the NPC in the thieves guild.
        self.add_sub_plot(
            nart, "VIP_SCREENING", elements={"LOCALE": tgsp.elements["INTERIOR"]}
        )

        self.bandit_base_found = False
        self.permission_granted = False
        self.bandit_base_destroyed = False

        return True

    def MISSION_WIN(self, camp):
        if not self.black_market_found:
            self.black_market_found = True

    def METROSCENE_ENTER(self, camp):
        if self.black_market_found and not self.black_market_announced:
            missionbuilder.NewLocationNotification("Black Market", self.elements["MISSION_GATE"])
            self.black_market_announced = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.black_market_found:
            thingmenu.add_item("Go to the Black Market.", self._go_to_market)
        if self.bandit_base_found and not self.bandit_base_destroyed:
            thingmenu.add_item("Attack the {} base.".format(self.elements["FACTION"]), self._attack_the_enemy_base)

    def SKULL_SIGN_menu(self, camp, thingmenu):
        thingmenu.add_item("[CONTINUE]", self._read_the_sign)

    def _read_the_sign(self, camp: gears.GearHeadCampaign):
        mybh = [bh for bh in camp.get_active_party() if bh.job and bh.job.name == "Bounty Hunter"]
        if mybh:
            npc = random.choice(mybh)
            ghcutscene.SimpleMonologueDisplay("[I_DONT_FEEL_WELCOME]", npc)(camp)

    def _go_to_market(self, camp):
        if self.black_market_entry_status == self.BMES_ENTERED:
            camp.go(self.black_market_entrance)
        elif self.black_market_entry_status == self.BMES_ATTACKED:
            self._attack_the_black_market(camp)
        else:
            self._attempt_entry_to_black_market(camp)

    def _attack_the_black_market(self, camp):
        self.black_market_entry_status = self.BMES_ATTACKED
        my_mission = missionbuilder.BuildAMissionSeed(
            camp, "Destroy the Black Market", self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements["FACTION"], rank=self.rank+10,
            objectives=(missionbuilder.BAMO_STORM_THE_CASTLE, missionbuilder.BAMO_SURVIVE_THE_AMBUSH),
            cash_reward=500, on_win=self._destroy_black_market
        )
        my_mission(camp)

    def _attack_the_enemy_base(self, camp):
        my_mission = missionbuilder.BuildAMissionSeed(
            camp, "Destroy the {} Base".format(self.elements["FACTION"]), self.elements["METROSCENE"],
            self.elements["MISSION_GATE"],
            enemy_faction=self.elements["FACTION"], rank=self.rank+10,
            objectives=(missionbuilder.BAMO_STORM_THE_CASTLE, ),
            cash_reward=500, on_win=self._destroy_enemy_base
        )
        my_mission(camp)

    def _enter_the_black_market(self, camp):
        self.black_market_entry_status = self.BMES_ENTERED
        camp.go(self.black_market_entrance)

    GUARD_FACTIONS = (gears.factions.BoneDevils, gears.factions.TreasureHunters, gears.factions.BladesOfCrihna)
    def _attempt_entry_to_black_market(self, camp):
        my_mission = missionbuilder.BuildAMissionSeed(
            camp, "Enter the Black Market", self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=random.choice(self.GUARD_FACTIONS), rank=self.rank+5,
            objectives=("DZDBMBMission_AttemptEntry", rwme_objectives.RWMO_MAYBE_AVOID_FIGHT,),
            custom_elements={"ADVENTURE_GOAL": self.black_market_entrance, "BLACK_MARKET": self.elements["BLACK_MARKET"]},
            auto_exit=True, cash_reward=0, on_win=self._win_entry_fight, make_enemies=False
        )
        my_mission(camp)

    def _win_entry_fight(self, camp):
        mymenu = pbge.rpgmenu.AlertMenu("How do you want to deal with the {}?".format(self.elements["BLACK_MARKET"]))
        mymenu.add_item("Attack and destroy it.", self._attack_the_black_market)
        mymenu.add_item("Enter on foot", self._enter_the_black_market)
        mymenu.can_cancel = False
        a = mymenu.query()
        if a:
            a(camp)

    def _destroy_black_market(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self._npc_becomes_enemy(camp)
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.history.append(gears.relationships.Memory(
            "you destroyed {}".format(self.elements["BLACK_MARKET"]),
            "I destroyed {}".format(self.elements["BLACK_MARKET"]),
            -20, (gears.relationships.MEM_Clash, gears.relationships.MEM_LoseToPC)
        ))
        self.elements["BLACK_MARKET"].remove_all_npcs(camp)
        self.end_plot(camp)

    def _destroy_enemy_base(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.bandit_base_destroyed = True
        if not self.permission_granted:
            self._npc_becomes_enemy(camp)
            npc: gears.base.Character = self.elements["NPC"]
            npc.relationship.history.append(gears.relationships.Memory(
                "you attacked the {} base without my permission".format(self.elements["FACTION"]),
                "I broke the rules of {}".format(self.elements["BLACK_MARKET"]),
                -5, (gears.relationships.MEM_Ideological,)
            ))

    def _npc_becomes_enemy(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc.is_not_destroyed():
            camp.freeze(npc)
            if not npc.relationship:
                npc.relationship = camp.get_relationship(npc)
            npc.relationship.attitude = gears.relationships.A_RESENT
            npc.relationship.role = gears.relationships.R_ADVERSARY
            npc.relationship.expectation = gears.relationships.E_REVENGE
            if npc not in camp.egg.dramatis_personae:
                camp.egg.dramatis_personae.append(npc)
            camp.set_faction_as_pc_enemy(gears.factions.TreasureHunters)

    def BLACK_MARKET_ENTER(self, camp):
        self.black_market_entry_status = self.BMES_ENTERED

    def NPC_offers(self, camp):
        mylist = list()
        if not self.permission_granted:
            mylist.append(Offer(
                "[THIS_CANNOT_BE_ALLOWED] You have my permission to utterly destroy their base.",
                ContextTag([context.REVEAL,]), effect=self._get_permission,
                data={"reveal": "{FACTION} has been raiding the highway near {METROSCENE}".format(**self.elements)}
            ))
        return mylist

    def _get_permission(self, camp):
        self.permission_granted = True
        self._reveal_bandit_base(camp)

    def _reveal_bandit_base(self, camp):
        self.bandit_base_found = True
        missionbuilder.NewMissionNotification("Attack {} Base".format(self.elements["FACTION"]),
                                              self.elements["MISSION_GATE"])


class BMB_AttemptEntry(Plot):
    LABEL = "DZDBMBMission_AttemptEntry"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True, backup_seek_func=self.adv.is_good_backup_enemy)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander)

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Get past the guards".format(self.elements["_commander"]),
                                                  missionbuilder.MAIN_OBJECTIVE_VALUE)
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

        mylist.append(Offer(
            "[HALT] State your business in the {METROSCENE} Black Market.".format(**self.elements),
            context=ContextTag([context.ATTACK,])
        ))

        mylist.append(Offer(
            "[WITHDRAW]",
            context=ContextTag([context.WITHDRAW,]), effect=self._withdraw
        ))

        mylist.append(Offer(
            "[CHALLENGE]",
            context=ContextTag([context.COMBAT_CUSTOM,]),
            data={"reply": "[LETSFIGHT]"}
        ))

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[CHANGE_MIND_AND_RETREAT]",
                context=ContextTag([context.RETREAT, ]), effect=self._retreat,
            ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, rank=npc.renown,
            difficulty=gears.stats.DIFFICULTY_HARD,
            no_random=False
        )

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "In that case, you're free to pass.",
                context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._permission,
                data={"reply": "We have important business with the Thieves Guild."}
            ), camp, mylist, gears.stats.Charm, gears.stats.Stealth, rank=npc.renown,
            no_random=False
        )

        ghdialogue.TagBasedPartyReply(
            Offer(
                "Sounds legit. You're free to pass.",
                context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._permission,
                data={"reply": "You know: smuggling, larceny, all the basics."}
            ), camp, mylist, (gears.tags.Criminal,)
        )

        return mylist

    def _retreat(self, camp):
        pbge.alert("{}'s lance flees the battlefield.".format(self.elements["_commander"]))
        self.elements["_eteam"].retreat(camp)

    def _withdraw(self, camp):
        self.elements["LOCALE"].player_team.retreat(camp)

    def _permission(self, camp):
        self.adv.cancel_adventure(camp)
        camp.go(self.elements["ADVENTURE_GOAL"])


#   ******************************
#   ***  DZRE_MECHA_GRAVEYARD  ***
#   ******************************

class MechaGraveyardAdventure(Plot):
    LABEL = "DZRE_MECHA_GRAVEYARD"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.zombots_active = True
        self.got_shutdown = False
        self.safe_shutdown = False
        self.set_collector = False

        # Create the entry mission: PC must defeat the zombots guarding the defiled factory
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35, 35, plotutility.random_deadzone_spot_name(), player_team=team1, scale=gears.scale.MechaScale,
            exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg", exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE")

        mygoal = self.register_element(
            "_goalroom",
            pbge.randmaps.rooms.FuzzyRoom(random.randint(8, 15), random.randint(8, 15),
                                          parent=outside_scene,
                                          anchor=pbge.randmaps.anchors.middle)
        )
        self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"ROOM": mygoal, "TYPE_TAGS": ("ROBOT", "ZOMBOT")},
                          ident="OUTENCOUNTER")

        room1 = self.register_element(
            "ENTRANCE_ROOM",
            pbge.randmaps.rooms.FuzzyRoom(
                5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE"
        )
        myent = self.register_element(
            "ENTRANCE",
            game.content.ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"], anchor=pbge.randmaps.anchors.middle),
            dident="ENTRANCE_ROOM"
        )

        # Local NPC can tell about the entry mission.
        self.add_sub_plot(nart, "REVEAL_LOCATION", ident="LOCATE", elements={
            "INTERESTING_POINT": "The zombie mecha seem to be attracted to the ancient ruined tower there."})
        self.location_unlocked = False

        # Add the defiled factory dungeon
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Defiled Factory", gharchitecture.ScrapIronWorkshop(),
            self.rank,
            monster_tags=("ROBOT", "ZOMBOT", "FACTORY"),
            explo_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            connector=plotutility.StairsUpToStairsDownConnector,
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS, gears.tags.SCENE_FACTORY),
            decor=gharchitecture.DefiledFactoryDecor()
        )
        d_entrance = pbge.randmaps.rooms.ClosedRoom(7, 7, anchor=pbge.randmaps.anchors.south)
        mydungeon.entry_level.contents.append(d_entrance)
        mycon2 = plotutility.TownBuildingConnection(
            nart, self, outside_scene, mydungeon.entry_level,
            room1=mygoal,
            room2=d_entrance,
            door1=ghwaypoints.DZDDefiledFactory(name="Defiled Factory", anchor=pbge.randmaps.anchors.middle),
            door2=ghwaypoints.Exit(anchor=pbge.randmaps.anchors.south)
        )

        # Add the lore rooms
        levels = random.sample(mydungeon.levels, 3)
        while len(levels) < 3:
            levels.append(random.choice(mydungeon.levels))

        lr1 = self.register_element(
            "LORE_ROOM_1", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[0].contents.append(lr1)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr1, "LOCALE": levels[0], "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        lorecompy1 = self.register_element("LORE1", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the primary research terminal."),
                                        dident="LORE_ROOM_1")

        lr2 = self.register_element(
            "LORE_ROOM_2", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[1].contents.append(lr2)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr2, "LOCALE": levels[1], "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        lorecompy2 = self.register_element("LORE2", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the research overview terminal."),
                                        dident="LORE_ROOM_2")

        lr3 = self.register_element(
            "LORE_ROOM_3", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[2].contents.append(lr3)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr3, "LOCALE": levels[2], "TYPE_TAGS": ("ROBOT",)}
        )
        lorecompy3 = self.register_element("LORE3", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the incubation chamber control terminal."),
                                        dident="LORE_ROOM_3")
        biotank_alpha = self.register_element("BIO_A", ghwaypoints.Biotank(plot_locked=True, name="Biotank",),
                                        dident="LORE_ROOM_3")
        biotank_beta = self.register_element("BIO_B", ghwaypoints.EmptyBiotank(plot_locked=True, name="Biotank",),
                                        dident="LORE_ROOM_3")

        self.alpha_full = True
        self.beta_full = False

        # Add the goal room
        final_room = self.register_element(
            "FINAL_ROOM", pbge.randmaps.rooms.ClosedRoom(9, 9, ),
        )
        mydungeon.goal_level.contents.append(final_room)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 12).based_on(self),
            elements={"ROOM": final_room, "LOCALE": mydungeon.goal_level, "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        mycompy = self.register_element("COMPY", ghwaypoints.OldMainframe(plot_locked=True, name="Factory Control",
                                                                          anchor=pbge.randmaps.anchors.middle,
                                                                          desc="You stand before the factory control mainframe."),
                                        dident="FINAL_ROOM")

        #print(self.elements["METROSCENE"])

        return True

    def LOCATE_WIN(self, camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def COMPY_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if self.zombots_active:
            thingmenu.desc = "{} The lights are blinking wildly.".format(thingmenu.desc)
            thingmenu.add_item("Smash the system", self._smash)
            if self.got_shutdown:
                thingmenu.add_item("Activate the FINAL_DEATH command", self._shutdown)

    def _smash(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You smash the computer until the lights stop blinking. Then you smash it a bit more just to be safe. If that doesn't take care of the zombie mecha problem, you're not sure what will.")
        self.zombots_active = False
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)
        BiotechDiscovery(camp, "I found an old zombot-infested biotech laboratory.",
                         "[THATS_INTERESTING] I'll get one of our hazmat recovery teams to check it out. Here is the {cash} you've earned.",
                         self.rank//2)

    def _shutdown(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You activate the emergency shutdown. For the first time in nearly two hundred years, the computer powers off and comes to a rest.")
        self.zombots_active = False
        self.safe_shutdown = True
        if self.beta_full:
            self.set_collector = True
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)
        BiotechDiscovery(camp, "I found a PreZero lab where they were developing self-repair technology",
                         "[THATS_INTERESTING] This could be a very important discovery; I'd say it's easily worth {cash}.", self.rank+15)

    def LORE3_menu(self, camp, thingmenu):
        if self.alpha_full:
            thingmenu.add_item("Drain Alpha Chamber", self._toggle_alpha)
        else:
            thingmenu.add_item("Fill Alpha Chamber", self._toggle_alpha)
        if self.beta_full:
            thingmenu.add_item("Drain Beta Chamber", self._toggle_beta)
        else:
            thingmenu.add_item("Fill Beta Chamber", self._toggle_beta)

    def _toggle_alpha(self, camp):
        if self.alpha_full:
            self.alpha_full = False
            self.elements["BIO_A"].break_tank()
            mymonster: gears.base.Monster = gears.selector.get_design_by_full_name("Skeletron")
            mymonster.roll_stats(20,False)
            mymonster.colors = (gears.color.CardinalRed, gears.color.Ebony, gears.color.ElectricYellow, gears.color.Cyan, gears.color.Malachite)
            mymonster.name = "Subject Alpha"
            mymonster.statline[gears.stats.CloseCombat] += 4
            mymonster.statline[gears.stats.Vitality] += 7
            myteam = teams.Team(enemies=(camp.scene.player_team,))
            camp.scene.place_gears_near_spot(self.elements["BIO_A"].pos[0],self.elements["BIO_A"].pos[1],myteam, mymonster)
        else:
            pbge.alert("ERROR: Alpha Chamber not responding. Please consult manual.")

    def _toggle_beta(self, camp):
        if self.beta_full:
            self.elements["BIO_B"].empty_tank()
        else:
            self.elements["BIO_B"].fill_tank()
        self.beta_full = not self.beta_full

    def BIO_A_menu(self, camp, thingmenu):
        if self.alpha_full:
            thingmenu.desc = "This biotank is filled with a cloudy green liquid. There is something moving gently inside of it."
        else:
            thingmenu.desc = "This biotank has been destroyed."

    def BIO_B_menu(self, camp, thingmenu):
        if self.set_collector:
            if self.beta_full:
                thingmenu.desc = "This biotank is filled with a cloudy green liquid. There is a large, dark shape in the middle of the tank."
            else:
                thingmenu.desc = "This biotank contains a featureless black box. You are pretty sure it wasn't there earlier."
                thingmenu.add_item("Get the box", self._get_box)
        else:
            if self.beta_full:
                thingmenu.desc = "This biotank is filled with a cloudy green liquid."
            else:
                thingmenu.desc = "This biotank is empty."

    def _get_box(self, camp):
        pbge.alert("You retrieve the box from the biotank. It appears to be some kind of mecha component.")
        self.set_collector = False
        myitem = gears.selector.get_design_by_full_name("NC-1 Self Repair System")
        camp.party.append(myitem)

    def LORE2_menu(self, camp, thingmenu):
        thingmenu.add_item("Read the overview for the NC-1 Self Repair Module", self._read_overview)
        thingmenu.add_item("Search for hidden files", self._search_l2)

    def _read_overview(self, camp):
        pbge.alert(
            "The NC-1 Self Repair Module is a revolutionary new technology for conventional battlemovers. It uses bionite agents to effect instantaneous repair of mechanical systems.")
        pbge.alert(
            "Direction is provided by the gestalt intelligence of the bionite network. This allows the system to operate without a central control unit and to make efficient use of available resources.")
        pbge.alert(
            "Join the battleforce of the future, today. Support development of the NC-1 Self Repair Module now and get early backer exclusive rewards.")

    def _search_l2(self, camp: gears.GearHeadCampaign):
        pc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, difficulty=gears.stats.DIFFICULTY_EASY, no_random=True)
        if pc:
            if pc is camp.pc:
                pbge.alert("You easily hack into the ancient computer system.")
            else:
                pbge.alert("{} hacks into the ancient computer system.".format(pc))
            pbge.alert("You discover an additional data file for a secondary project.")
            pbge.alert("Test subject HC-Alpha shows the potential for the NC-1 system to be used not just for battlemovers, but individual soldiers as well. Biotechnology allows perfect fusion of organic and inorganic components.")
            pbge.alert("If the neural degradation problem can be solved, imagine the potential: Immortal soldiers who instantly recover from any damage. The keys to their immortality safely held by illumos who control the power source.")
            pbge.alert("Even if the degradation problem is intractable, there are ways to weaponize this phenomenon. Imagine high-C munitions loaded with NC bionites. Initial casulties could be reanimated to eliminate surviving defenders.")
            pbge.alert("Anyway, it's something to think about when we submit the third round of grant applications.")
            self.got_shutdown = True
        else:
            pbge.alert("This computer uses a PreZero operating system that is far beyond your understanding.")

    def LORE1_menu(self, camp, thingmenu):
        thingmenu.add_item("Read the notes of Dr. Herbert Coombs", self._read_hc)
        thingmenu.add_item("Read the notes of Dr. Millicent Savini", self._read_ms)
        thingmenu.add_item("Search for hidden files", self._search_l1)

    def _read_hc(self, camp):
        pbge.alert(
            "\"Initial tests of the NC-1 bionite have shown promising results. The program is able to repair damage to mechanical systems, including systems it has never before encountered, thanks to the coordination of the cells' gestalt intelligence.\"")
        pbge.alert(
            "\"There are still limitations. The bionite mass has no internal power source, and so depends upon an external broadcast engine. Individual bionites which move beyond control range perish quickly.\"")
        pbge.alert(
            "\"I have introduced a small amount of NC-1 into my leg prosthetic to see if they can repair my constantly slipping ankle joint.\"")

    def _read_ms(self, camp):
        pbge.alert(
            "\"Initial tests for the NC-1 bionite have revealed problems not indicated by the prototypes. Among these issues, the infectious nature of the system must be resolved before testing resumes.\"")
        pbge.alert(
            "\"The gestalt intelligence does not differentiate between its host machinery and external units. This leads to the bionites attempting to colonize any machine they are brought into contact with. A self-repair system that will also repair your enemy's machine is, to put it bluntly, less than optimal.\"")
        pbge.alert(
            "\"So far, the spread of the bionites has been limited by their fragility when moved beyond range of the broadcast power system. Testing cannot resume until it's clear we're not risking another Onyx Jelly fiasco.\"")

    def _search_l1(self, camp: gears.GearHeadCampaign):
        pc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, no_random=True)
        if pc:
            if pc is camp.pc:
                pbge.alert("You easily hack into the ancient computer system.")
            else:
                pbge.alert("{} hacks into the ancient computer system.".format(pc))
            pbge.alert("You discover an additional log file from Dr. Millicent Savini which someone attempted to delete from the database.")
            pbge.alert("\"Attempts to restrain the NC-1 bionite seem to be interpreted by the gestalt intelligence as a form of damage. Thus far, it has outmaneuvered every security protocol we have attempted.\"")
            pbge.alert("\"Herbert's condition is deteriorating as more of his biomass is being replaced by machinery. It is not clear what effect the infection has had on his brain. In any case, I have restrained him in a specimen vat and will be conducting further tests.\"")
            pbge.alert("\"I have installed an emergency shutdown switch into the factory control mainframe. In the event that we lose control of NC-1, the command FINAL_DEATH will cut power to the system. Active bionites will be moved to the containment system.\"")
            self.got_shutdown = True
        else:
            pbge.alert("This computer uses a PreZero operating system that is far beyond your understanding.")

    def go_to_locale(self, camp):
        camp.go(self.elements["ENTRANCE"])


#   ******************************
#   ***  DZRE_WARONTHEHIGHWAY  ***
#   ******************************

class WarOnTheHighwayMain(Plot):
    # Two towns are having a bit of a spat, and that has caused the road to close. Gonna construct this quest using
    # the Narrative Challenge system. So, in theory, this plot should just have to describe the challenge and then
    # let the challenge builder supply the means to the various ends.
    LABEL = "DZRE_WARONTHEHIGHWAY"
    active = True
    scope = True

    def custom_init(self, nart):
        myedge = self.elements["DZ_EDGE"]

        cities = [myedge.start_node.destination, myedge.end_node.destination]
        random.shuffle(cities)

        city1: gears.GearHeadScene = self.register_element("CITY1", cities[0])
        city2: gears.GearHeadScene = self.register_element("CITY2", cities[1])

        nart.camp.set_faction_enemies(city1, city2)

        self.register_element("C1_WAR", Challenge(
            "Defeat {}".format(city2), ghchallenges.FIGHT_CHALLENGE, (city2.faction,),
            involvement=ghchallenges.InvolvedMetroFactionNPCs(city1),
            data={
                "challenge_objectives": ["defend {} from {}".format(city1, city2),],
                "enemy_objectives": ["control the highway between {} and {}".format(city2, city1),],
                "mission_intros": ["The highway to {} has been blocked by enemy forces.".format(city2),],
                "mission_objectives": [
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_RECOVER_CARGO,
                        "Enemy forces have seized a shipment of cargo needed in {}.".format(city1),
                        "recover {}'s goods".format(city1), "cut off all trade to {}".format(city1),
                        "I took back the goods you stole", "you broke our sanctions against {}".format(city1),
                        "you stole supplies needed by {}".format(city1),
                        "I enforced our sanctions against {}".format(city1)
                    ),
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_LOCATE_ENEMY_FORCES,
                        "{} mecha have occupied the highway.".format(city2),
                        "open the highway", "protect {}'s sovereignty".format(city2),
                        "I broke through your highway blockade", "you trespassed into {}".format(city2),
                        "you blocked the highway to {}".format(city1), "you tried to invade {}".format(city2)
                    ),
                ]
            }
        ))

        self.register_element("C2_WAR", Challenge(
            "Defeat {}".format(city1), ghchallenges.FIGHT_CHALLENGE, (city1.faction,),
            involvement=ghchallenges.InvolvedMetroFactionNPCs(city2),
            data={
                "challenge_objectives": ["defend {} from {}".format(city2, city1), ],
                "enemy_objectives": ["control the highway between {} and {}".format(city1, city2), ],
                "mission_intros": ["The highway to {} has been blocked by enemy forces.".format(city1), ],
                "mission_objectives": [
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_RECOVER_CARGO,
                        "Enemy forces have seized a shipment of cargo needed in {}.".format(city2),
                        "recover {}'s goods".format(city2), "cut off all trade to {}".format(city2),
                        "I took back the goods you stole", "you broke our sanctions against {}".format(city2),
                        "you stole supplies needed by {}".format(city2),
                        "I enforced our sanctions against {}".format(city2)
                    ),
                    ghchallenges.DescribedObjective(
                        missionbuilder.BAMO_LOCATE_ENEMY_FORCES,
                        "{} mecha have occupied the highway.".format(city1),
                        "open the highway", "protect {}'s sovereignty".format(city1),
                        "I broke through your highway blockade", "you trespassed into {}".format(city1),
                        "you blocked the highway to {}".format(city2), "you tried to invade {}".format(city1)
                    ),
                ]
            }
        ))

        self.add_sub_plot(nart, "DZRE_WOTH_CASUSBELLI", ident="CASUSBELLI")

        return True

    def C1_WAR_ADVANCE_CHALLENGE(self, camp):
        if self.elements["C1_WAR"].points_earned > 10:
            pbge.alert("{CITY2} has been defeated; the war with {CITY1} is over.".format(**self.elements))
            camp.check_trigger("WIN", self)
            self.deactivate(camp)

    def C2_WAR_ADVANCE_CHALLENGE(self, camp):
        if self.elements["C2_WAR"].points_earned > 10:
            pbge.alert("{CITY1} has been defeated; the war with {CITY2} is over.".format(**self.elements))
            camp.check_trigger("WIN", self)
            self.deactivate(camp)

    def CASUSBELLI_WIN(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.deactivate(camp)


#   ******************************
#   ***  DZRE_WOTH_CASUSBELLI  ***
#   ******************************
#
#   The cause of the conflict in a WarOnTheHighway plot.
#   If the casus belli is resolved and the war subsequently ended, this plot will set a WIN trigger.
#

class WOTHCB_BothSidesSame(Plot):
    # The two towns involved? They have grievances going back over a century. This scenario is symmetrical; it's the
    # test case so I'll be adding some more nuanced conflicts later.
    LABEL = "DZRE_WOTH_CASUSBELLI"
    UNIQUE = True
    active = True
    scope = True

    def custom_init(self, nart):
        c1war = self.elements["C1_WAR"]
        c2war = self.elements["C2_WAR"]

        self.register_element("C1_DIPLOMACY", Challenge(
            "Negotiate peace in {}".format(self.elements["CITY1"]),
            ghchallenges.DIPLOMACY_CHALLENGE, [self.elements["CITY1"].faction, self.elements["CITY2"].faction],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["CITY1"]), active=False,
            data={
                "challenge_subject": "the war with {CITY2}".format(**self.elements),
                "challenge_statements": (
                    "the only way to end this conflict with {CITY2} is to crush their army completely".format(**self.elements),
                    "we won't have peace until {CITY2} is defeated for good".format(**self.elements),
                ),
                "pc_rebuttals": (
                    "if you keep fighting, you'll never have peace",
                    "the people of {CITY2} probably think the same about you".format(**self.elements)
                ),
                "npc_agreement": (
                    "we need to fix our role in this conflict",
                    "peace is only possible if both sides assent"
                ),
                "npc_disagreement": (
                    "you don't know the atrocities they've committed",
                    "if they were interested in peace, they would have surrendered already"
                ),
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.CUSTOM,]), effect=self._use_c1_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["CITY2"].faction
                        }
                    ), active=True, uses=99, involvement=c1war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._use_c1_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["CITY2"].faction
                        }
                    ), active=True, uses=99, involvement=c1war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                )
            )

        ))


        self.register_element("C2_DIPLOMACY", Challenge(
            "Negotiate peace in {}".format(self.elements["CITY2"]),
            ghchallenges.DIPLOMACY_CHALLENGE, [self.elements["CITY2"].faction, self.elements["CITY1"].faction],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["CITY2"]), active=False,
            data={
                "challenge_subject": "the attacks by {CITY1}".format(**self.elements),
                "challenge_statements": (
                    "{CITY1} has to pay for attacking {CITY2}".format(**self.elements),
                    "this war is entirely the fault of {CITY1}".format(**self.elements),
                ),
                "pc_rebuttals": (
                    "the cycle of retribution can only be broken by justice",
                    "more fighting is only going to lead to more retribution"
                ),
                "npc_agreement": (
                    "{CITY2} and {CITY1} both need to own up to our history".format(**self.elements),
                    "reconciliation will be difficult, but maybe it is possible"
                ),
                "npc_disagreement": (
                    "they started it",
                    "there would be no war now if {CITY1} accepted they lost the last one".format(**self.elements)
                ),
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._use_c2_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["CITY1"].faction
                        }
                    ), active=True, uses=99, involvement=c2war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._use_c2_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["CITY1"].faction
                        }
                    ), active=True, uses=99, involvement=c2war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                )
            )
        ))

        self.has_activated_negotiations = False

        return True

    def _use_c1_diplomacy(self, camp):
        self.elements["C1_DIPLOMACY"].advance(camp, 2)

    def _use_c2_diplomacy(self, camp):
        self.elements["C2_DIPLOMACY"].advance(camp, 2)

    def C1_DIPLOMACY_ADVANCE_CHALLENGE(self, camp):
        mydip: Challenge = self.elements["C1_DIPLOMACY"]
        otherdip: Challenge = self.elements["C2_DIPLOMACY"]
        if mydip.points_earned >= 10 and otherdip.points_earned >= 10:
            self.win_peace(camp)
        elif mydip.points_earned >= 10:
            pbge.BasicNotification("The citizens of {CITY1} are willing to accept peace.".format(**self.elements))
            self.elements["C1_DIPLOMACY"].active = False

    def C2_DIPLOMACY_ADVANCE_CHALLENGE(self, camp):
        mydip: Challenge = self.elements["C2_DIPLOMACY"]
        otherdip: Challenge = self.elements["C1_DIPLOMACY"]
        if mydip.points_earned >= 10 and otherdip.points_earned >= 10:
            self.win_peace(camp)
        elif mydip.points_earned >= 10:
            pbge.BasicNotification("The citizens of {CITY2} are willing to accept peace.".format(**self.elements))
            self.elements["C2_DIPLOMACY"].active = False

    def win_peace(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.elements["C1_DIPLOMACY"].active = False
        self.elements["C2_DIPLOMACY"].active = False
        pbge.alert("Thanks to your efforts, {CITY1} and {CITY2} begin peace negotiations. The war is over.".format(**self.elements))
        camp.set_faction_as_pc_ally(self.elements["CITY1"].faction)
        camp.set_faction_as_pc_ally(self.elements["CITY2"].faction)
        camp.set_faction_neutral(self.elements["CITY1"].faction, self.elements["CITY2"].faction)
        self.end_plot(camp)

    def _get_generic_offers( self, npc: gears.base.Character, camp ):
        # To start the peace process going, you need at least one person on either side or a lance member who is
        # interested in peace.
        myoffs = list()

        if not self.has_activated_negotiations:
            if self.elements["C1_WAR"].is_involved(camp, npc):
                myoff = Offer(
                    "Our conflict goes back decades; there is a lot of bad blood on both sides. Still, maybe an outsider like you could find a solution.",
                    ContextTag([context.CUSTOM,]), effect=self._activate_negotiations,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["CITY2"])}
                )
                if gears.personality.Peace in npc.personality:
                    myoffs.append(myoff)
                else:
                    ghdialogue.TagBasedPartyReply(
                        myoff, camp, myoffs, (gears.personality.Peace,)
                    )
            elif self.elements["C2_WAR"].is_involved(camp, npc):
                myoff = Offer(
                    "We've been at war with {} on and off for decades... but this time, they were the ones who attacked us! Maybe someone like you can find a way to end this cycle.".format(self.elements["CITY1"]),
                    ContextTag([context.CUSTOM,]), effect=self._activate_negotiations,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["CITY1"])}
                )
                if gears.personality.Peace in npc.personality:
                    myoffs.append(myoff)
                else:
                    ghdialogue.TagBasedPartyReply(
                        myoff, camp, myoffs, (gears.personality.Peace,)
                    )

        return myoffs

    def _activate_negotiations(self, camp):
        self.elements["C1_DIPLOMACY"].active = True
        self.elements["C2_DIPLOMACY"].active = True
        self.has_activated_negotiations = True
