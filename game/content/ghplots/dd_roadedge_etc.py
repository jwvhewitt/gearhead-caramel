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
        mybh = [bh for bh in camp.get_active_party() if isinstance(bh, gears.base.Character) and bh.job and bh.job.name == "Bounty Hunter"]
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
                camp.egg.dramatis_personae.add(npc)
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
        pc = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Computers, self.rank, difficulty=gears.stats.DIFFICULTY_EASY, no_random=True)
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
        pc = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Computers, self.rank, no_random=True)
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

        self.register_element("_C1FAC", city1.faction)
        self.register_element("_C2FAC", city2.faction)

        self.register_element("C1_WAR", Challenge(
            "Defeat {}".format(city2), ghchallenges.FIGHT_CHALLENGE, (city2.faction,),
            involvement=ghchallenges.InvolvedMetroFactionNPCs(city1),
            data={
                "challenge_objectives": ["defend {} from {}".format(city1, city2),],
                "challenge_fears": ["attack {}".format(city1)],
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
            }, memo=pbge.challenges.ChallengeMemo(
                "{CITY1} is fighting {CITY2}.".format(**self.elements)
            )
        ))

        self.register_element("C2_WAR", Challenge(
            "Defeat {}".format(city1), ghchallenges.FIGHT_CHALLENGE, (city1.faction,),
            involvement=ghchallenges.InvolvedMetroFactionNPCs(city2),
            data={
                "challenge_objectives": ["defend {} from {}".format(city2, city1), ],
                "challenge_fears": ["attack {}".format(city2)],
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
            }, memo=pbge.challenges.ChallengeMemo(
                "{CITY2} is fighting {CITY1}.".format(**self.elements)
            )
        ))

        self.add_sub_plot(nart, "DZRE_WOTH_CASUSBELLI", ident="CASUSBELLI")

        return True

    def C1_WAR_ADVANCE_CHALLENGE(self, camp):
        if self.elements["C1_WAR"].points_earned >= 10:
            pbge.alert("{CITY2} has been defeated; the war with {CITY1} is over.".format(**self.elements))
            self.elements["C1_WAR"].deactivate(camp)
            self.elements["C2_WAR"].deactivate(camp)
            camp.check_trigger("WIN", self)
            self.deactivate(camp)

    def C2_WAR_ADVANCE_CHALLENGE(self, camp):
        if self.elements["C2_WAR"].points_earned >= 10:
            pbge.alert("{CITY1} has been defeated; the war with {CITY2} is over.".format(**self.elements))
            self.elements["C1_WAR"].deactivate(camp)
            self.elements["C2_WAR"].deactivate(camp)
            camp.check_trigger("WIN", self)
            self.deactivate(camp)

    def _C1FAC_DEFEAT(self, camp):
        self.elements["C2_WAR"].advance(camp, 1)

    def _C2FAC_DEFEAT(self, camp):
        self.elements["C1_WAR"].advance(camp, 1)

    def CASUSBELLI_WIN(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.elements["C1_WAR"].deactivate(camp)
        self.elements["C2_WAR"].deactivate(camp)
        self.deactivate(camp)

    FEAR_PATTERNS = (
        "[I_worry_that] {} will {}.",
        "[I_worry_that] {} is going to {}.",
        "[I_worry_that] {} will succeed in their attempt to {}."
    )
    def get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mydict = dict()
        if camp.is_not_lancemate(npc):
            myscene = npc.scene.get_root_scene()
            if myscene is self.elements["CITY1"]:
                mywar = self.elements["C1_WAR"]
                myenemy = mywar.key[0]
                mydict["[CURRENT_EVENTS]"] = list()
                for s in mywar.data["challenge_fears"]:
                    mydict["[CURRENT_EVENTS]"].append(random.choice(self.FEAR_PATTERNS).format(myenemy, s))
                mydict["[News]"] = ["{CITY1} is at war with {CITY2}".format(**self.elements)]
            elif myscene is self.elements["CITY2"]:
                mywar = self.elements["C2_WAR"]
                myenemy = mywar.key[0]
                mydict["[CURRENT_EVENTS]"] = list()
                for s in mywar.data["challenge_fears"]:
                    mydict["[CURRENT_EVENTS]"].append(random.choice(self.FEAR_PATTERNS).format(myenemy, s))
                mydict["[News]"] = ["{CITY2} is at war with {CITY1}".format(**self.elements)]



#   ******************************
#   ***  DZRE_WOTH_CASUSBELLI  ***
#   ******************************
#
#   The cause of the conflict in a WarOnTheHighway plot.
#   If the casus belli is resolved and the war subsequently ended, this plot will set a WIN trigger.
#

class WOTHCB_DoubleTheChallenge(Plot):
    # Each of the towns involved have a separate motive for fighting.
    LABEL = "DZRE_WOTH_CASUSBELLI"
    active = True
    scope = True

    def custom_init(self, nart):
        self.add_sub_plot(
            nart, "DZRE_WOTH_CBMOTIVE", ident="CBMOTIVE1",
            elements={
                "THIS_CITY": self.elements["CITY1"], "THIS_WAR": self.elements["C1_WAR"],
                "THIS_METRO": self.elements["CITY1"].metrodat,
                "THAT_CITY": self.elements["CITY2"], "THAT_WAR": self.elements["C2_WAR"],
                "THAT_METRO": self.elements["CITY2"].metrodat,
            }
        )

        self.add_sub_plot(
            nart, "DZRE_WOTH_CBMOTIVE", ident="CBMOTIVE2",
            elements={
                "THIS_CITY": self.elements["CITY2"], "THIS_WAR": self.elements["C2_WAR"],
                "THIS_METRO": self.elements["CITY2"].metrodat,
                "THAT_CITY": self.elements["CITY1"], "THAT_WAR": self.elements["C1_WAR"],
                "THAT_METRO": self.elements["CITY1"].metrodat,
            }
        )

        self.city1_peace = False
        self.city2_peace = False

        #print(self.elements["CITY1"], self.elements["CITY2"])

        return True

    def C1_WAR_WIN(self, camp: gears.GearHeadCampaign):
        if hasattr(self.subplots["CBMOTIVE1"], "won_the_war"):
            self.subplots["CBMOTIVE1"].won_the_war(camp)
        if hasattr(self.subplots["CBMOTIVE2"], "lost_the_war"):
            self.subplots["CBMOTIVE2"].lost_the_war(camp)

    def C2_WAR_WIN(self, camp: gears.GearHeadCampaign):
        if hasattr(self.subplots["CBMOTIVE2"], "won_the_war"):
            self.subplots["CBMOTIVE2"].won_the_war(camp)
        if hasattr(self.subplots["CBMOTIVE1"], "lost_the_war"):
            self.subplots["CBMOTIVE1"].lost_the_war(camp)

    def CBMOTIVE1_WIN(self, camp: gears.GearHeadCampaign):
        self.city1_peace = True
        if self.city2_peace:
            self.win_peace(camp)

    def CBMOTIVE2_WIN(self, camp: gears.GearHeadCampaign):
        self.city2_peace = True
        if self.city1_peace:
            self.win_peace(camp)

    def win_peace(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        pbge.alert("Thanks to your efforts, {CITY1} and {CITY2} begin peace negotiations. The war is over.".format(**self.elements))
        camp.set_faction_as_pc_ally(self.elements["CITY1"].faction)
        camp.set_faction_as_pc_ally(self.elements["CITY2"].faction)
        camp.set_faction_neutral(self.elements["CITY1"].faction, self.elements["CITY2"].faction)
        if hasattr(self.subplots["CBMOTIVE1"], "peace_happened"):
            self.subplots["CBMOTIVE1"].peace_happened(camp)
        if hasattr(self.subplots["CBMOTIVE2"], "peace_happened"):
            self.subplots["CBMOTIVE2"].peace_happened(camp)
        self.end_plot(camp)


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

        c1war.data["mission_objectives"].append(ghchallenges.DescribedObjective(
            missionbuilder.BAMO_CAPTURE_BUILDINGS,
            "We need to seize control of their strategic resources.",
            "capture your weapon stockpiles", "defend our resources",
            "I captured your weapon stockpiles", "you robbed {} of our resources".format(self.elements["CITY2"]),
            "I failed to liberate your weapon stockpiles",
            "you tried to rob {} and failed".format(self.elements["CITY2"])
        ))
        c1war.data["challenge_fears"].append("devastate {CITY1}".format(**self.elements))
        c1war.data["challenge_fears"].append("cut off all trade to {CITY1}".format(**self.elements))

        c2war.data["mission_objectives"].append(ghchallenges.DescribedObjective(
            missionbuilder.BAMO_DESTROY_ARTILLERY,
            "The enemy's artillery is moving within range of town; your job is to neutralize it.",
            "neutralize your artillery", "attack {}".format(self.elements["CITY2"]),
            "I destroyed your artillery", "you destroyed my artillery",
            "I failed to neutralize your artillery",
            "I shelled {} into submission".format(self.elements["CITY2"])
        ))
        c1war.data["challenge_fears"].append("conquer {CITY2}".format(**self.elements))
        c1war.data["challenge_fears"].append("bomb {CITY2} into submission".format(**self.elements))

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
            ), memo=pbge.challenges.ChallengeMemo(
                "You may be able to get {CITY1} to agree to peace with {CITY2}.".format(**self.elements)
            ), memo_active=True

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
            ), memo=pbge.challenges.ChallengeMemo(
                "You may be able to get {CITY2} to agree to peace with {CITY1}.".format(**self.elements)
            ), memo_active=True
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
            self.elements["C1_DIPLOMACY"].deactivate(camp)

    def C2_DIPLOMACY_ADVANCE_CHALLENGE(self, camp):
        mydip: Challenge = self.elements["C2_DIPLOMACY"]
        otherdip: Challenge = self.elements["C1_DIPLOMACY"]
        if mydip.points_earned >= 10 and otherdip.points_earned >= 10:
            self.win_peace(camp)
        elif mydip.points_earned >= 10:
            pbge.BasicNotification("The citizens of {CITY2} are willing to accept peace.".format(**self.elements))
            self.elements["C2_DIPLOMACY"].deactivate(camp)

    def win_peace(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        self.elements["C1_DIPLOMACY"].deactivate(camp)
        self.elements["C2_DIPLOMACY"].deactivate(camp)
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
        self.elements["C1_DIPLOMACY"].activate(camp)
        self.elements["C2_DIPLOMACY"].activate(camp)
        self.has_activated_negotiations = True

#   ****************************
#   ***  DZRE_WOTH_CBMOTIVE  ***
#   ****************************
#
#   The casus belli for one side in a WarOnTheHighway plot.
#   If this city is ready to negotiate for peace, this plot will set a WIN trigger.
#
#   Elements:
#       THIS_CITY, THIS_WAR: The city and war challenge of the city this motive applies to
#       THAT_CITY, THAT_WAR: The city and war of the other side
#
#   Optional Methods:
#       peace_happened(self, camp): Call this method if peace is achieved.
#       won_the_war(self, camp):    Call this method if this side won the war.
#       lost_the_war(self, camp):   Call this method if this side lost the war.

class WOTHCBM_HomeDespot(Plot):
    # This side of the war is being run by a total despot. If the despot wins the war or reaches a peace deal,
    # that will consolidate their hold on power and is a Bad Thing(tm).
    LABEL = "DZRE_WOTH_CBMOTIVE"
    active = True
    scope = "THIS_METRO"
    UNIQUE = True

    QOL = gears.QualityOfLife(
        0, 0, -1, -1, 1
    )

    RUMOR = pbge.plots.Rumor(
        "as long as {NPC} is busy with {THAT_CITY}, {THIS_CITY} can relax a little",
        offer_msg="[THIS_IS_A_SECRET] {NPC} rules {THIS_CITY} with an iron fist; as long as {NPC.gender.subject_pronoun} is attacking someone else {NPC.gender.subject_pronoun} can't attack us.",
        memo="{NPC}, the despotic leader of {THIS_CITY}, is too busy fighting {THAT_CITY} to oppress {NPC.gender.possessive_determiner} own town.",
        memo_location="SCENE", prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.register_element("NPC", self.elements["THIS_METRO"].city_leader)
        self.war_ongoing = True

        this_war: pbge.challenges.Challenge = self.elements["THIS_WAR"]
        this_war.data["challenge_objectives"].append("crush all resistance in {THAT_CITY}".format(**self.elements))
        this_war.data["enemy_objectives"].append("resist {THAT_CITY}'s leader {NPC}".format(**self.elements))
        this_war.data["mission_objectives"].append(
            ghchallenges.DescribedObjective(
                missionbuilder.BAMO_AID_ALLIED_FORCES,
                "Our glorious army has been dispatched to pacify {THAT_CITY}".format(**self.elements),
                "crush {THAT_CITY}".format(**self.elements), "resist your invasion",
                "I led {THIS_CITY} to victory".format(**self.elements),
                "you invaded {THAT_CITY}".format(**self.elements),
                "you proved stronger than I thought",
                "I protected {THAT_CITY} from {NPC}'s tyranny".format(**self.elements)
            )
        )
        this_war.data["challenge_fears"].append("lose to {THIS_CITY}".format(**self.elements))
        this_war.data["challenge_fears"].append("just make things worse in {THIS_CITY}".format(**self.elements))

        that_war: pbge.challenges.Challenge = self.elements["THAT_WAR"]
        that_war.data["challenge_fears"].append("spread {NPC}'s tyranny to {THAT_CITY}".format(**self.elements))
        that_war.data["challenge_fears"].append("demolish {THAT_CITY}".format(**self.elements))

        # Now for the challenges! There is a mostly normal peace challenge that can be unlocked...
        self.peace_challenge_started = False
        self.register_element("PEACE_CHALLENGE", Challenge(
            "Negotiate peace in {}".format(self.elements["THIS_CITY"]),
            ghchallenges.DIPLOMACY_CHALLENGE, [self.elements["THIS_CITY"].faction, self.elements["THAT_CITY"].faction],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["THIS_CITY"]), active=False,
            data={
                "challenge_subject": "the war with {THAT_CITY}".format(**self.elements),
                "challenge_statements": (
                    "{THAT_CITY} has to be punished for resisting {THIS_CITY}".format(**self.elements),
                    "{THIS_CITY} needs to show {THAT_CITY} our strength".format(**self.elements),
                ),
                "pc_rebuttals": (
                    "constant war will only make {THIS_CITY} weaker".format(**self.elements),
                    "fighting {THAT_CITY} only weakens {THIS_CITY}".format(**self.elements)
                ),
                "npc_agreement": (
                    "{THIS_CITY} should deal with our own problems first".format(**self.elements),
                    "{THAT_CITY} isn't worth fighting over".format(**self.elements)
                ),
                "npc_disagreement": (
                    "the deadzone must bend to {THIS_CITY}'s will".format(**self.elements),
                    "we won't accept the insults of {THAT_CITY}".format(**self.elements)
                ),
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._use_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["THAT_CITY"].faction
                        }
                    ), active=True, uses=99, involvement=this_war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),
                AutoOffer(
                    dict(
                        msg="[OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._use_diplomacy,
                        data={
                            "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                            "enemy_faction": self.elements["THAT_CITY"].faction
                        }
                    ), active=True, uses=99, involvement=this_war.involvement,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                )
            ), memo=pbge.challenges.ChallengeMemo(
                "You may be able to get {THIS_CITY} to agree to peace with {THAT_CITY}.".format(**self.elements)
            ), memo_active=True
        ))

        # There is also a dethrone challenge which might possibly be unlocked.
        self.dethrone_started = False
        self.register_element("DETHRONE_CHALLENGE", Challenge(
            "Dethrone the Despot", ghchallenges.DETHRONE_CHALLENGE, (npc,),
            ghchallenges.InvolvedMetroResidentNPCs(self.elements["THIS_CITY"], exclude=[npc]),
            active=False, data={
                "reasons_to_dethrone": [
                    "{NPC} is is harming {THIS_CITY} as much as {THAT_CITY}".format(**self.elements),
                    "{NPC} is a tyrant".format(**self.elements)
                ],
                "reasons_to_support": [
                    "tyrant or not, {NPC} is our leader".format(**self.elements),
                    "only {NPC} stands bewtween {THIS_CITY} and anarchy".format(**self.elements)
                ],
                "violated_virtue": gears.personality.Justice,
                "upheld_virtue": gears.personality.Duty
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[YOU_COULD_BE_RIGHT] If enough people supported revolution, I would too.",
                        context=ContextTag([context.CUSTOM, ]), effect=self._convince_to_evict,
                        data={
                            "reply": "{NPC} can be overthrown while {NPC.gender.subject_pronoun} is busy with {THAT_CITY}.".format(**self.elements)
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                ),
                AutoOffer(
                    dict(
                        msg="[YOU_COULD_BE_RIGHT] If enough people supported revolution, I would too.",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._convince_to_evict,
                        data={
                            "reply": "{NPC} can be overthrown while {NPC.gender.subject_pronoun} is busy with {THAT_CITY}.".format(**self.elements)
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_LEGENDARY, untrained_ok=True
                    )
                )
            ), memo=pbge.challenges.ChallengeMemo(
                "If {NPC} were removed from power, {THIS_CITY} might agree to peace with {THAT_CITY}.".format(**self.elements)
            ), memo_active=True

        ))
        return True

    def _convince_to_evict(self, camp):
        self.elements["DETHRONE_CHALLENGE"].advance(camp, 1)

    def _use_diplomacy(self, camp):
        self.elements["PEACE_CHALLENGE"].advance(camp, 1)

    def PEACE_CHALLENGE_WIN(self, camp: gears.GearHeadCampaign):
        pbge.BasicNotification("The citizens of {THIS_CITY} are willing to accept peace.".format(**self.elements))
        camp.check_trigger("WIN", self)
        self.elements["PEACE_CHALLENGE"].deactivate(camp)

    def DETHRONE_CHALLENGE_WIN(self, camp: gears.GearHeadCampaign):
        if self.elements["THIS_METRO"].city_leader is self.elements["NPC"] and self.elements["DETHRONE_NPC"].is_operational():
            pbge.BasicNotification("The citizens of {THIS_CITY} depose {NPC}, and {DETHRONE_NPC} becomes the new leader.".format(**self.elements))
            camp.freeze(self.elements["NPC"])
            self.elements["NPC"].faction = None
            self.elements["THIS_METRO"].city_leader = self.elements["DETHRONE_NPC"]
        self.elements["DETHRONE_CHALLENGE"].deactivate(camp)

    def NPC_offers(self, camp):
        mylist = list()
        if not self.war_ongoing:
            return mylist

        if not self.peace_challenge_started:
            mylist.append(Offer(
                "I am a peaceful ruler, and of course I am open to negotiations with {THAT_CITY}, if they could be convinced to give up their violent ways.".format(**self.elements),
                context=ContextTag([context.CUSTOM, ]), effect=self._start_peace_challenge,
                data={
                    "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                    "enemy_faction": str(self.elements["THAT_CITY"])
                }
            ))

            mylist.append(Offer(
                "I am a peaceful ruler, and of course I am open to negotiations with {THAT_CITY}, if they could be convinced to give up their violent ways.".format(**self.elements),
                context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._start_peace_challenge,
                data={
                    "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                    "enemy_faction": str(self.elements["THAT_CITY"])
                }
            ))

        return mylist

    def _get_generic_offers( self, npc, camp ):
        mylist = list()
        if not self.war_ongoing:
            return mylist

        if not self.peace_challenge_started:
            if self.elements["THIS_METRO"].city_leader is not self.elements["NPC"]:
                mylist.append(Offer(
                    "With {NPC} out of the picture, I don't think anyone in {THIS_CITY} would object to peace with {THAT_CITY}.".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), effect=self._start_peace_challenge,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["THAT_CITY"])}
                ))
                mylist.append(Offer(
                    "With {NPC} out of the picture, I don't think anyone in {THIS_CITY} would object to peace with {THAT_CITY}.".format(**self.elements),
                    ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._start_peace_challenge,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["THAT_CITY"])}
                ))
            elif self.elements["THIS_WAR"].is_involved(camp, npc) and npc is not self.elements["NPC"]:
                myoff = Offer(
                    "I hate to admit this, but our leader {NPC} would be willing to make peace with {THAT_CITY} if {NPC.gender.subject_pronoun} thought there was popular support for it.".format(**self.elements),
                    ContextTag([context.CUSTOM,]), effect=self._start_peace_challenge,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["THAT_CITY"])}
                )
                if gears.personality.Fellowship in npc.personality:
                    mylist.append(myoff)

        if self._rumor_memo_delivered and not self.dethrone_started:
            if self.elements["THIS_WAR"].is_involved(camp, npc) and npc is not self.elements["NPC"]:
                ghdialogue.MatchingTagPartyReply(
                    Offer(
                        "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] I will see what I can do to bring {NPC} to justice, but without support it's a hopeless cause.".format(**self.elements),
                        ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "You know {NPC} doesn't deserve to be leader of {THIS_CITY}.".format(**self.elements),
                            "opinion": "{NPC} has become a tyrant".format(**self.elements)
                        }, effect=ghdialogue.NPCInclusiveOfferEffect(npc, self._start_dethrone_challenge)
                    ), camp, mylist, npc, gears.personality.Justice
                )

                ghdialogue.MatchingTagPartyReply(
                    Offer(
                        "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] It will take a rebellion of the common people to remove {NPC.gender.object_pronoun} from power, and for that I am going to need more support.",
                        ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "You know {NPC} has been abusing the people of of {THIS_CITY}.".format(**self.elements),
                            "opinion": "{NPC} treats {THIS_CITY} as {NPC.gender.possessive_determiner} property".format(**self.elements)
                        }, effect=ghdialogue.NPCInclusiveOfferEffect(npc, self._start_dethrone_challenge)
                    ), camp, mylist, npc, gears.personality.Fellowship
                )

        return mylist

    def t_UPDATE(self, camp):
        if self.elements["THIS_METRO"].city_leader is not self.elements["NPC"]:
            self.elements["DETHRONE_CHALLENGE"].deactivate(camp)
            self.dethrone_started = True
            self.RUMOR = None
        elif self.elements["NPC"].is_destroyed():
            self.elements["THIS_METRO"].city_leader = self.elements.get("DETHRONE_NPC")
            self.elements["DETHRONE_CHALLENGE"].deactivate(camp)
            self.dethrone_started = True
            self.RUMOR = None

    def _start_dethrone_challenge(self, camp, npc):
        self.dethrone_started = True
        self.elements["DETHRONE_NPC"] = npc
        mychallenge: Challenge = self.elements["DETHRONE_CHALLENGE"]
        mychallenge.activate(camp)
        mychallenge.involvement.exclude.add(npc)
        mychallenge.memo = pbge.challenges.ChallengeMemo("{DETHRONE_NPC} is attempting to remove {NPC} as ruler of {THIS_CITY}.", challenge=mychallenge)

    def _start_peace_challenge(self, camp: gears.GearHeadCampaign):
        self.elements["PEACE_CHALLENGE"].activate(camp)
        camp.set_faction_as_pc_neutral(self.elements["THIS_CITY"].faction)
        self.peace_challenge_started = True

    def won_the_war(self, camp):
        myscene: gears.GearHeadScene = self.elements["THIS_CITY"]
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.elements["DETHRONE_CHALLENGE"].deactivate(camp)
        self.war_ongoing = False
        if self.elements["THIS_METRO"].city_leader is self.elements["NPC"]:
            game.content.load_dynamic_plot(camp, "CONSEQUENCE_TOTALCRACKDOWN", PlotState(
                rank=self.rank, elements={
                    "METRO": myscene.metrodat, "METROSCENE": myscene,
                    "CRACKDOWN_REASON": "with the war over, {NPC} is cracking down on {NPC.gender.possessive_determiner} internal enemies".format(**self.elements)
                }
            ).based_on(self))
        else:
            self.end_plot(camp)

    def lost_the_war(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.elements["DETHRONE_CHALLENGE"].deactivate(camp)
        self.war_ongoing = False
        if self.elements["THIS_METRO"].city_leader is not self.elements["NPC"]:
            self.end_plot(camp, True)

    def peace_happened(self, camp):
        myscene: gears.GearHeadScene = self.elements["THIS_CITY"]
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.elements["DETHRONE_CHALLENGE"].deactivate(camp)
        self.war_ongoing = False
        if self.elements["THIS_METRO"].city_leader is self.elements["NPC"]:
            game.content.load_dynamic_plot(camp, "CONSEQUENCE_TOTALCRACKDOWN", PlotState(
                rank=self.rank, elements={
                    "METRO": myscene.metrodat, "METROSCENE": myscene,
                    "CRACKDOWN_REASON": "with the war over, {NPC} is cracking down on {NPC.gender.possessive_determiner} internal enemies".format(**self.elements)
                }
            ).based_on(self))
        self.end_plot(camp)


class WOTHCBM_AspiringConqueror(Plot):
    # This town's war effort is being led by a wannabe conqueror. Peace is not possible until either that leader is
    # deposed or intimidated into compliance. Also, if this town wins the war, the other town is going to get occupied.
    LABEL = "DZRE_WOTH_CBMOTIVE"
    active = True
    scope = "THIS_METRO"
    UNIQUE = True

    QOL = gears.QualityOfLife(
        1, 0, -1, -1, 2
    )

    RUMOR = pbge.plots.Rumor(
        "{NPC} will lead us to victory over {THAT_CITY}",
        offer_msg="{NPC} plans to make {THIS_CITY} the most powerful city in the deadzone! Starting with {THAT_CITY}, we will build an empire to surpass Clan Ironwind.",
        memo="{NPC}, the warlord of {THIS_CITY}, has plans to conquer {THAT_CITY}.", memo_location="SCENE",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        this_war: pbge.challenges.Challenge = self.elements["THIS_WAR"]
        this_war.data["challenge_objectives"].append("conquer {THAT_CITY}".format(**self.elements))
        this_war.data["enemy_objectives"].append("protect {THAT_CITY}".format(**self.elements))
        this_war.data["mission_objectives"].append(
            ghchallenges.DescribedObjective(
                missionbuilder.BAMO_CAPTURE_THE_MINE,
                "We need to seize control of {THAT_CITY}'s strategic resources".format(**self.elements),
                "conquer {THAT_CITY}".format(**self.elements), "repel your invasion",
                "I led {THIS_CITY} to victory".format(**self.elements),
                "you invaded {THAT_CITY}".format(**self.elements),
                "you drove me out of {THAT_CITY}".format(**self.elements),
                "I protected {THAT_CITY} from you".format(**self.elements)
            )
        )
        this_war.data["challenge_fears"].append("halt {THIS_CITY}'s expansion".format(**self.elements))
        this_war.data["challenge_fears"].append("defeat {THIS_CITY}'s army of unification".format(**self.elements))

        that_war: pbge.challenges.Challenge = self.elements["THAT_WAR"]
        that_war.data["challenge_fears"].append("subjugate {THAT_CITY}".format(**self.elements))
        that_war.data["challenge_fears"].append("take over {THAT_CITY} completely".format(**self.elements))

        myhq = self.seek_element(nart, "SCENE", self._is_good_hq, scope=self.elements["THIS_CITY"])
        npc: gears.base.Character = self.register_element("NPC", gears.selector.random_character(
            self.rank, current_year=nart.camp.year, camp=nart.camp, combatant=True, job=gears.jobs.ALL_JOBS["Warlord"],
            faction=self.elements["THIS_CITY"].faction
        ), dident="SCENE")
        if gears.personality.Glory not in npc.personality:
            npc.personality.add(gears.personality.Glory)
        if gears.personality.Justice in npc.personality:
            npc.personality.remove(gears.personality.Justice)

        self.elements["THIS_METRO"].city_leader = npc

        self.register_element("PEACE_CHALLENGE", Challenge(
            "Dethrone the Warlord", ghchallenges.DETHRONE_CHALLENGE, (npc,),
            ghchallenges.InvolvedMetroResidentNPCs(self.elements["THIS_CITY"], exclude=[npc]),
            active=False, data={
                "reasons_to_dethrone": [
                    "{NPC} is waging war against {THAT_CITY} for no reason".format(**self.elements),
                    "{NPC} will lead {THIS_CITY} into neverending war".format(**self.elements)
                ],
                "reasons_to_support": [
                    "{NPC} has led {THIS_CITY} to glory".format(**self.elements),
                    "{NPC}'s plan will make {THIS_CITY} prosperous again".format(**self.elements)
                ],
                "violated_virtue": gears.personality.Justice,
                "upheld_virtue": gears.personality.Glory
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[YOU_COULD_BE_RIGHT] [OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._convince_to_evict,
                        data={
                            "reply": "{NPC} must be removed from power.".format(**self.elements),
                            "enemy_faction": self.elements["THAT_CITY"].faction
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_HARD, untrained_ok=True
                    )
                ),
                AutoOffer(
                    dict(
                        msg="[YOU_COULD_BE_RIGHT] [OPEN_TO_PEACE_WITH_ENEMY_FACTION]",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._convince_to_evict,
                        data={
                            "reply": "{NPC} must be removed from power.".format(**self.elements),
                            "enemy_faction": self.elements["THAT_CITY"].faction
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank,
                        difficulty=gears.stats.DIFFICULTY_LEGENDARY, untrained_ok=True
                    )
                )
            ), memo=pbge.challenges.ChallengeMemo(
                "If {NPC} were removed from power, {THIS_CITY} might agree to peace with {THAT_CITY}.".format(**self.elements)
            ), memo_active=True

        ))
        return True

    def _convince_to_evict(self, camp):
        self.elements["PEACE_CHALLENGE"].advance(camp, 1)

    def _is_good_hq(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_GOVERNMENT in candidate.attributes
                and gears.tags.SCENE_PUBLIC in candidate.attributes)

    def PEACE_CHALLENGE_WIN(self, camp: gears.GearHeadCampaign):
        pbge.alert("The citizens of {THIS_CITY} relieve {NPC} from {NPC.gender.possessive_determiner} role as warlord. The path to a peaceful resolution for this conflict is now clear.".format(**self.elements))
        self.elements["NPC"].faction = None
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.elements["THIS_METRO"].city_leader = None
        camp.freeze(self.elements["NPC"])
        camp.check_trigger("WIN", self)
        self.end_plot(camp)

    def won_the_war(self, camp):
        myscene: gears.GearHeadScene = self.elements["THAT_CITY"]
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        game.content.load_dynamic_plot(camp, "CONSEQUENCE_MILOCCUPATION", PlotState(
            rank=self.rank, elements={
                "METRO": myscene.metrodat, "METROSCENE": myscene,
                "OCCUPYING_FACTION": self.elements["THIS_CITY"].faction
            }
        ).based_on(self))
        self.end_plot(camp)

    def lost_the_war(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.end_plot(camp)

    def peace_happened(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.elements["PEACE_CHALLENGE"].active:
            ghdialogue.TagBasedPartyReply(Offer(
                "[WHY_SHOULD_I] My conquest of {THAT_CITY} is just the first step... Soon the entire deadzone will fear the might of {THIS_CITY}!".format(**self.elements),
                context=ContextTag([context.CUSTOM, ]), effect=self._reveal_warlord_intentions,
                data={
                    "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                    "enemy_faction": str(self.elements["THAT_CITY"])
                }
            ), camp, mylist, (gears.personality.Peace,)
            )

            ghdialogue.TagBasedPartyReply(Offer(
                "[WHY_SHOULD_I] My conquest of {THAT_CITY} is just the first step... Soon the entire deadzone will fear the might of {THIS_CITY}!".format(**self.elements),
                context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._reveal_warlord_intentions,
                data={
                    "reply": "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]",
                    "enemy_faction": str(self.elements["THAT_CITY"])
                }
            ), camp, mylist, (gears.personality.Peace,)
            )

        if self.elements["THAT_WAR"].points_earned > 0:
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Yeah, maybe I wasn't cut out for this deadzone conqueror business... I'm willing to talk peace if {THAT_CITY} is as well.".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), effect=self.surrender,
                    data={"reply": "[SURRENDER_TO_FACTION]", "faction": str(self.elements["THAT_CITY"])}
                ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation,
                self.rank + 25 - self.elements["THAT_WAR"].points_earned * 10,
                gears.stats.DIFFICULTY_HARD
            )

            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Yeah, maybe I wasn't cut out for this deadzone conqueror business... I'm willing to talk peace if {THAT_CITY} is as well.".format(**self.elements),
                    ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self.surrender,
                    data={"reply": "[SURRENDER_TO_FACTION]", "faction": str(self.elements["THAT_CITY"])}
                ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation,
                self.rank + 25 - self.elements["THAT_WAR"].points_earned * 10,
                gears.stats.DIFFICULTY_HARD
            )

        return mylist

    def _get_generic_offers( self, npc, camp ):
        mylist = list()

        if (self.elements["THAT_WAR"].points_earned > self.elements["THIS_WAR"].points_earned and
                npc is not self.elements["NPC"] and self.elements["THIS_WAR"].is_involved(camp, npc) and
                not self.elements["PEACE_CHALLENGE"].active):
            mylist.append(Offer(
                "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] It might be better if {NPC.gender.subject_pronoun} were removed from power.".format(**self.elements),
                context=ContextTag([context.CUSTOM, ]), effect=self._reveal_warlord_intentions,
                data={"reply": "You realize that you are going to lose this war, right?",
                      "opinion": "{NPC} has gotten us into an unwinnable situation".format(**self.elements)}
            ))

            mylist.append(Offer(
                "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] It might be better if {NPC.gender.subject_pronoun} were removed from power.".format(**self.elements),
                context=ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self._reveal_warlord_intentions,
                data={"reply": "You realize that you are going to lose this war, right?",
                      "opinion": "{NPC} has gotten us into an unwinnable situation".format(**self.elements)}
            ))

        return mylist

    def _reveal_warlord_intentions(self, camp):
        self.elements["PEACE_CHALLENGE"].activate(camp)

    def surrender(self, camp: gears.GearHeadCampaign):
        # The warlord has wisely chosen to surrender. They can stay in power.
        pbge.BasicNotification("The leadership of {THIS_CITY} is willing to accept peace.".format(**self.elements))
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        camp.check_trigger("WIN", self)
        camp.set_faction_as_pc_neutral(self.elements["THIS_CITY"].faction)
        self.end_plot(camp)


class WOTHCBM_PeacefulPeople(Plot):
    # This town doesn't really want to fight. I mean, really really doesn't want to fight. You're gonna have to
    # complete a challenge just to open the fight path.
    LABEL = "DZRE_WOTH_CBMOTIVE"
    active = True
    scope = "THIS_METRO"
    UNIQUE = True

    QOL = gears.QualityOfLife(
        0, 1, 2, 2, -2
    )

    RUMOR = pbge.plots.Rumor(
        "{THIS_CITY} is under attack by {THAT_CITY} but we can't even defend ourselves",
        offer_subject="{THIS_CITY} is under attack by {THAT_CITY}", offer_subject_data="this town's defenses",
        offer_msg="We are a peaceful people and our militia isn't strong enough to defeat {THAT_CITY}.",
        memo="{THIS_CITY} is being attacked by {THAT_CITY}, but lacks the defenses to resist.",
        memo_location="THIS_CITY"
    )

    def custom_init(self, nart):
        self.agreed_to_peace = False
        self.army_untrained = True
        self.war_is_over = False

        this_war: pbge.challenges.Challenge = self.elements["THIS_WAR"]
        this_war.deactivate(nart.camp)
        this_war.data["challenge_objectives"].append("defend us from {THAT_CITY}".format(**self.elements))
        this_war.data["challenge_objectives"].append("protect {THIS_CITY}".format(**self.elements))
        this_war.data["enemy_objectives"].append("conquer {THIS_CITY}".format(**self.elements))
        this_war.data["mission_objectives"].append(
            ghchallenges.DescribedObjective(
                missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
                "Our militia is having trouble holding back the enemy forces",
                "defend {THIS_CITY}".format(**self.elements), "capture {THIS_CITY}".format(**self.elements),
                "I defended {THIS_CITY} from you".format(**self.elements),
                "you defeated me in {THIS_CITY}".format(**self.elements),
                "you invaded {THIS_CITY}".format(**self.elements),
                "I invaded {THIS_CITY}".format(**self.elements)
            )
        )
        this_war.data["challenge_fears"].append("end our peaceful way of life forever".format(**self.elements))
        this_war.data["challenge_fears"].append("destroy {THIS_CITY} in body and spirit".format(**self.elements))

        that_war: pbge.challenges.Challenge = self.elements["THAT_WAR"]
        that_war.data["challenge_fears"].append("keep resisting our forces".format(**self.elements))
        that_war.data["challenge_fears"].append("refuse to surrender".format(**self.elements))


        self.register_element("PEACE_CHALLENGE", Challenge(
            "Train an Army", ghchallenges.RAISE_ARMY_CHALLENGE, (self.elements["THIS_CITY"],),
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["THIS_CITY"]),
            active=False, points_target=5,
            data={
                "threat": self.elements["THAT_CITY"]
            }, oppoffers=(
                AutoOffer(
                    dict(
                        msg="[I_NEED_MORE_PRACTICE] [LETS_GET_STARTED]",
                        context=ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "Are you prepared to defend {THIS_CITY} from {THAT_CITY}?".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99, npc_effect=self._train_soldier
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "In order to defend itself from {THAT_CITY}, {THIS_CITY} needs to improve its defenses.".format(**self.elements)
            ), memo_active=True
        ))
        return True

    def _train_soldier(self, camp: gears.GearHeadCampaign, npc: gears.base.Character):
        pbge.alert("You begin training {} in the ways of mecha warfare.".format(npc))
        if camp.do_skill_test(gears.stats.Knowledge, gears.stats.MechaPiloting, self.rank, gears.stats.DIFFICULTY_HARD):
            ghcutscene.SimpleMonologueDisplay("[I_LEARNED_SOMETHING] I'm all ready to take on {THAT_CITY}!".format(**self.elements), npc)(camp, False)
            self.elements["PEACE_CHALLENGE"].advance(camp, 1)
        else:
            ghcutscene.SimpleMonologueDisplay("[I_LEARNED_NOTHING] [WE_ARE_DOOMED]", npc)(camp, False)

    def _get_generic_offers( self, npc: gears.base.Character, camp ):
        # To start the peace process going, you need at least one person on either side or a lance member who is
        # interested in peace.
        myoffs = list()
        if self.war_is_over:
            return myoffs

        if self.elements["THIS_WAR"].is_involved(camp, npc):
            if not self.agreed_to_peace:
                myoffs.append(Offer(
                    "{THIS_CITY} would gladly welcome peace with {THAT_CITY}; this continued fighting helps no-one.".format(**self.elements),
                    ContextTag([context.CUSTOM,]), effect=self.win_peace,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["THAT_CITY"])}
                ))

                myoffs.append(Offer(
                    "Of course we want peace! {THAT_CITY} is the one who attacked us... Convince them to stop, and this will all be over.".format(**self.elements),
                    ContextTag([context.UNFAVORABLE_CUSTOM,]), effect=self.win_peace,
                    data={"reply": "[HAVE_YOU_TRIED_PEACE]", "enemy_faction": str(self.elements["THAT_CITY"])}
                ))
            if self.elements["THAT_WAR"].points_earned > 0:
                ghdialogue.SkillBasedPartyReply(
                    Offer(
                        "I fear that you are correct... If it means an end to the conflict, we have no choice but to surrender.".format(**self.elements),
                        ContextTag([context.CUSTOM, ]), effect=self.surrender,
                        data={"reply": "[SURRENDER_TO_FACTION]", "faction": str(self.elements["THAT_CITY"])}
                    ), camp, myoffs, gears.stats.Ego, gears.stats.Negotiation,
                    self.rank - self.elements["THAT_WAR"].points_earned * 10,
                    gears.stats.DIFFICULTY_HARD
                )

                ghdialogue.SkillBasedPartyReply(
                    Offer(
                        "I fear that you are correct... If it means an end to the conflict, we have no choice but to surrender.".format(**self.elements),
                        ContextTag([context.UNFAVORABLE_CUSTOM, ]), effect=self.surrender,
                        data={"reply": "[SURRENDER_TO_FACTION]", "faction": str(self.elements["THAT_CITY"])}
                    ), camp, myoffs, gears.stats.Ego, gears.stats.Negotiation,
                    self.rank - self.elements["THAT_WAR"].points_earned * 10,
                    gears.stats.DIFFICULTY_HARD
                )

            if self.army_untrained and not self.elements["PEACE_CHALLENGE"].active:
                myoffs.append(Offer(
                    "[HELLO] It's only a matter of time before {THAT_CITY} defeats us.".format(**self.elements),
                    ContextTag([context.HELLO,]),
                ))

                myoffs.append(Offer(
                    "Our town militia is small and inexperienced; in order to fight back effectively, we are going to need more pilots and training.",
                    ContextTag([context.CUSTOM,]), effect=self.start_training,
                    data={"reply": "You should fight back against {THAT_CITY}!".format(**self.elements)},
                    subject=str(self.elements["THAT_CITY"]),
                ))

        return myoffs

    def start_training(self, camp):
        self.elements["PEACE_CHALLENGE"].activate(camp)
        self.army_untrained = False

    def PEACE_CHALLENGE_WIN(self, camp):
        pbge.alert("{THIS_CITY} is all ready to defend itself against {THAT_CITY}.".format(**self.elements))
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.elements["THIS_WAR"].activate(camp)

    def win_peace(self, camp: gears.GearHeadCampaign):
        pbge.BasicNotification("The citizens of {THIS_CITY} are willing to accept peace.".format(**self.elements))
        camp.check_trigger("WIN", self)
        self.agreed_to_peace = True

    def surrender(self, camp: gears.GearHeadCampaign):
        self.elements["THAT_WAR"].advance(camp, 25)
        myscene: gears.GearHeadScene = self.elements["THIS_CITY"]
        game.content.load_dynamic_plot(camp, "CONSEQUENCE_MILOCCUPATION", PlotState(
            rank=self.rank, elements={
                "METRO": myscene.metrodat, "METROSCENE": myscene, "OCCUPYING_FACTION": self.elements["THAT_CITY"].faction
            }
        ).based_on(self))
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.end_plot(camp)

    def won_the_war(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.war_is_over = True
        self.memo = None
        self.RUMOR = None

    def lost_the_war(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.end_plot(camp)

    def peace_happened(self, camp):
        self.elements["PEACE_CHALLENGE"].deactivate(camp)
        self.war_is_over = True
        self.memo = None
        self.RUMOR = None

