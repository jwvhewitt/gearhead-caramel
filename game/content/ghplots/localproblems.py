#
# Some plots involving problems that affect the local metro scene. These problems generally decrease the Quality of
# Life indicators from the Metrodata object.
#

import random

from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from . import dd_customobjectives
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building


#   ***********************
#   ***  LOCAL_PROBLEM  ***
#   ***********************
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE
#

class SregorThrunet(Plot):
    LABEL = "TEST_LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(prosperity=-3)
    active = True

    RUMOR = Rumor(
        "thanks to {NPC}, the Thrunet has been really unstable lately",
        offer_msg="{NPC} is the {NPC.job} responsible for keeping our local data node running. But these days I can't even get the latest matches from Warhammer Arena. Could you go have a talk with {NPC.gender.object_pronoun} at {NPC_SCENE}?",
        memo="The Thrunet service in {METROSCENE} is unreliable; people blame {NPC}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate):
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or \
               cls.LABEL == "TEST_LOCAL_PROBLEM"

    JOBS = ("Mechanic", "Buttonpusher", "Tekno", "Hacker", "Buttonpusher", "Tekno")

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("NPC", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.ScrapIronBuilding,
            waypoints={"DOOR": ghwaypoints.WoodenDoor(name=self.shopname)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM,
                  pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2,
            attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_RUINS),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(
            intscene, gharchitecture.ScrapIronWorkshop(decorate=gharchitecture.FactoryDecor())
        )
        self.register_scene(nart, intscene, intscenegen, ident="NPC_SCENE", dident="METROSCENE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                              decorate=gharchitecture.FactoryDecor()),
                                      dident="NPC_SCENE")
        foyer.contents.append(team2)

        mycon = plotutility.TownBuildingConnection(
            nart, self, self.elements["METROSCENE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.MECHA_PARTS_STORE,
                                  rank=self.rank + random.randint(0, 15))

        foyer.contents.append(ghwaypoints.MechEngTerminal())

        self.thrunet_broken = True
        self.npc_impressed = False

        my_dungeon = dungeonmaker.DungeonMaker(
            nart, self, intscene, "{METROSCENE} Undercity".format(**self.elements),
            gharchitecture.StoneBuilding(decorate=gharchitecture.TechDungeonDecor()),
            self.rank, monster_tags=("ROBOT", "FACTORY", "RUINS", "MUTANT", "EARTH"),
            decor=None
        )

        droom = self.register_element('DUNGEON_ROOM', pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.DefiledFactoryDecor()),
                                      dident="NPC_SCENE")

        mycon2 = plotutility.StairsDownToStairsUpConnector(
            nart, self, intscene, my_dungeon.entry_level, room1=droom
        )

        roboroom = self.register_element('ROBOT_ROOM', pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.UlsaniteOfficeDecor()),
                                      dident="NPC_SCENE")
        roboteam = self.register_element("ROBOTEAM", teams.Team("RobotTeam"), dident="ROBOT_ROOM")
        roboforce = gears.selector.RandomMonsterUnit(self.rank+30, 50, gears.tags.GroundEnv, ("ROBOT",),
                                                     gears.scale.HumanScale)
        roboteam.contents += roboforce.contents

        return True

    TITLE_PATTERNS = (
        "{METROSCENE} Computing", "{METROSCENE} Electronics", "{NPC}'s Telecom", "{NPC}'s Lostech",
        "{adjective} Thrunet", "{METROSCENE} Data Center", "{adjective} Salvage",
        "{NPC}'s Data Mine", "{adjective} Bits", "Comm Center {METROSCENE}", "{adjective} Data Mine",
        "{NPC}'s {adjective} Computers",
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]),
            **self.elements)

    def NPC_offers(self, camp):
        mylist = list()

        if self.thrunet_broken:
            mylist.append(Offer("[HELLO] What do you want?! The Thrunet node for {METROSCENE} is down and everyone thinks I know how to fix it.".format(**self.elements),
                                context=ContextTag([context.HELLO]),
                                ))

            if not self.npc_impressed:
                mylist.append(Offer(
                    "[LISTEN_UP] I work with broken machines every day, I can strip every piece of usable gear out of a salvaged wreck. Everyone comes to the dead zone hoping to find lostech and strike it rich, but do you know what the biggest and most important piece of lostech is?",
                    context=ContextTag([context.CUSTOM]), subject=self, subject_start=True,
                    data={"reply": "I would like to talk about the Thrunet, actually."}
                ))

                mylist.append(Offer(
                    "It's the Thrunet. Sure, we still know how computers work, but about half the data traffic on Earth goes through PreZero nodes that we don't even know where they are. Or what they're doing, for that matter. And the data node deep under this building has decided to go bonky-wook.",
                    context=ContextTag([context.CUSTOMREPLY]), subject=self,
                    data={"reply": "[I_DONT_KNOW]"}
                ))

                ghdialogue.SkillBasedPartyReply(Offer(
                    "You know your stuff. Yeah, we don't even know where half the Thrunet nodes on Earth are- they date to PreZero times, and we lose more every year. We're building new ones but not fast enough. The node deep under this building has conked out, and I was hoping I could fix it from up here, but that doesn't seem likely.",
                    context=ContextTag([context.CUSTOMREPLY]), subject=self, effect=self._impress_npc,
                    data={"reply": "It's the Thrunet. Or the shadow Thrunet, at least."}
                ), camp, mylist, gears.stats.Knowledge, gears.stats.Computers, self.rank, gears.stats.DIFFICULTY_HARD)

            mylist.append(Offer(
                "This place is the top floor of what I guess was a PreZero office tower. The main server is right at the bottom. Unfortunately, the further down you go, the more dangerous it gets. You're a cavalier- why don't you go down and see if you can fix things?",
                context=ContextTag([context.INFO]), subject="deep under this building",
                data={"subject": "the place under this building"}, no_repeats=True, dead_end=True
            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "salvage"},
                            ))

        return mylist

    def _impress_npc(self, camp):
        if not self.npc_impressed:
            npc: gears.base.Character = self.elements["NPC"]
            npc.relationship.reaction_mod += 20
            self.npc_impressed = True


class ClassicMurderMystery(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(stability=-3)
    active = True

    WEAPON_CARDS = (
        {"name": "Pistol", "to_verb": "to shoot {}", "verbed": "shot {}",
         "did_not_verb": "didn't shoot {}", "data": {"image_name": "mystery_verbs.png", "frame": 2}},
        {"name": "Axe", "to_verb": "to axe {}", "verbed": "hit {} with an axe",
         "did_not_verb": "didn't have an axe", "data": {"image_name": "mystery_verbs.png", "frame": 1}},
        {"name": "Poison", "to_verb": "to poison {}", "verbed": "poisoned {}",
         "did_not_verb": "didn't poison {}", "data": {"image_name": "mystery_verbs.png", "frame": 5}},
        {"name": "Hydrospanner", "to_verb": "to bludgeon {}",
         "verbed": "bludgeoned {} with a hydrospanner",
         "did_not_verb": "didn't own a hydrospanner", "data": {"image_name": "mystery_verbs.png", "frame": 3}},
        {"name": "Workbot", "to_verb": "to send a workbot to kill {}",
         "verbed": "sent a workbot to kill {}",
         "did_not_verb": "didn't use a workbot", "data": {"image_name": "mystery_verbs.png", "frame": 4}},
    )

    MOTIVE_CARDS = (
        {"name": "Revenge", "to_verb": "to get revenge on {}", "verbed": "got revenge on {}",
         "did_not_verb": "didn't get revenge on {}", "data": {"image_name": "mystery_verbs.png", "frame": 2,
                                                              "excuse": "{VICTIM} was rude to me in middle school..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Money", "to_verb": "to get {}'s money", "verbed": "took {}'s money'",
         "did_not_verb": "didn't take {}'s money", "data": {"image_name": "mystery_verbs.png", "frame": 1,
                                                            "excuse": "{VICTIM} had tons of money, and I can share it..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Hatred", "to_verb": "to be rid of {}", "verbed": "hated {}",
         "did_not_verb": "didn't hate {}", "data": {"image_name": "mystery_verbs.png", "frame": 5,
                                                    "excuse": "All I'll say is that {VICTIM} deserved it..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Secret", "to_verb": "to protect their secrets",
         "verbed": "was being blackmailed by {}",
         "did_not_verb": "didn't have any secrets", "data": {"image_name": "mystery_verbs.png", "frame": 3,
                                                             "excuse": "{VICTIM} had some dirty info on me..."}},
        {"name": "Jealousy", "to_verb": "to protect their status",
         "verbed": "was jealous of {}",
         "did_not_verb": "wasn't jealous of {}", "data": {"image_name": "mystery_verbs.png", "frame": 4,
                                                          "excuse": "Why should {VICTIM} be more successful than me?!"}},
    )


    def custom_init(self, nart):
        # Start by creating the mystery!
        metroscene = self.elements["METROSCENE"]

        victim_name = self.register_element("VICTIM", gears.selector.GENERIC_NAMES.gen_word())

        suspect_cards = list()
        for t in range(5):
            myplot = self.add_sub_plot(nart, "ADD_BORING_NPC")
            npc = myplot.elements["NPC"]
            suspect_cards.append(ghchallenges.NPCSusCard(npc))

        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        weapon_cards = list()
        weapon_source = random.sample(self.WEAPON_CARDS, 5)
        for wcd in weapon_source:
            for k,v in wcd.items():
                if isinstance(v, str):
                    wcd[k] = v.format(victim_name)
            weapon_cards.append(pbge.okapipuzzle.VerbSusCard(**wcd))
        weapon_susdeck = pbge.okapipuzzle.SusDeck("Weapon", weapon_cards)

        motive_cards = list()
        motive_source = random.sample(self.MOTIVE_CARDS, 5)
        for mcd in motive_source:
            for k,v in mcd.items():
                if isinstance(v, str):
                    mcd[k] = v.format(victim_name)
            motive_cards.append(pbge.okapipuzzle.VerbSusCard(**mcd))
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "{}'s Murder".format(victim_name),
            (suspect_susdeck, weapon_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}."
        ))

        # Store the culprit.
        self.elements["CULPRIT"] = mymystery.solution[0].gameob

        # Now, we subcontract the actual mystery challenge out to a utility plot.
        self.add_sub_plot(nart, "MURDER_MYSTERY_CHALLENGE", ident="MCHALLENGE")

        self.mystery_solved = False
        self.mchallenge_won = False
        return True

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text}".format(**self.elements), location=self.elements["CULPRIT"].scene
        )

    def MCHALLENGE_WIN(self, camp: gears.GearHeadCampaign):
        camp.freeze(self.elements["CULPRIT"])
        self.end_plot(camp, True)

    def CULPRIT_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        bribe = gears.selector.calc_mission_reward(self.rank, 500)
        if self.mystery_solved:
            mylist.append(Offer(
                "Don't go to the authorities yet. {} I'll offer ${:,} for you to let me go.".format(mystery.solution[2].data["excuse"].format(**self.elements), bribe),
                ContextTag([context.CUSTOM]), data={"reply": "I know you {}.".format(mystery.solution[1].verbed)},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[I_WOULD_HAVE_GOTTEN_AWAY]",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "No deal. You will pay for your crime."},
                subject=self, effect=self._catch_culprit, dead_end=True
            ))

            mylist.append(Offer(
                "[PLEASURE_DOING_BUSINESS]",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "That sounds like a good deal."},
                subject=self, effect=self._release_culprit, dead_end=True
            ))

            mylist.append(Offer(
                "Let me know when you've come to a decision.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "I'll think about it."},
                subject=self, dead_end=True
            ))

        return mylist

    def _catch_culprit(self, camp):
        camp.dole_xp(100)
        reward = gears.selector.calc_mission_reward(self.rank, 150)
        camp.credits += reward
        camp.freeze(self.elements["CULPRIT"])
        pbge.alert(
            "For catching {}, you earn ${:,}.".format(self.elements["CULPRIT"], reward))
        self.end_plot(camp, True)

    def _release_culprit(self, camp: gears.GearHeadCampaign):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 500)
        content.load_dynamic_plot(camp, "CONSEQUENCE_INJUSTICE", PlotState().based_on(self))
        self.end_plot(camp, True)


class ThePlague(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(health=-3)
    active = True

    RUMOR = Rumor(
        "{METROSCENE} is going through an epidemic of {DISEASE}",
        offer_msg="It's terrible; and to make matters worse, the only reliable cure for {DISEASE} is {THECURE}. {METROSCENE} has just about run out.",
        memo="{METROSCENE} is going through an epidemic of {DISEASE}, and the only cure is {THECURE}.",
        memo_location="METROSCENE",
        offer_subject="{DISEASE}", offer_subject_data="{DISEASE}", offer_effect_name="rumor_fun"
    )

    def custom_init(self, nart):
        self.elements["DISEASE"] = plotutility.random_disease_name()
        self.elements["THECURE"] = plotutility.random_medicine_name()

        self.add_sub_plot(nart, "EPIDEMIC_STARTER", ident="EPIDEMIC")
        self.add_sub_plot(nart, "MAKE_DRUGS_STARTER", ident="MAKE_DRUGS")

        return True

    def rumor_fun(self, camp):
        self.subplots["EPIDEMIC"].activate(camp)
        self.subplots["MAKE_DRUGS"].activate(camp)

    def EPIDEMIC_WIN(self, camp):
        pbge.alert("The epidemic appears to be under control now.")
        self.end_plot(camp, True)

    def MAKE_DRUGS_WIN(self, camp):
        pbge.alert("{METROSCENE} now has enough {THECURE} to bring {DISEASE} under control.".format(**self.elements))
        self.end_plot(camp, True)

    def _get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mygram = dict()

        mygram["[CURRENT_EVENTS]"] = [
            "Stand back... I don't want to catch {DISEASE}.".format(**self.elements),
            "There's been an outbreak of {DISEASE} in {METROSCENE}... If a cure isn't found, then we are doomed.".format(
                        **self.elements),
        ]

        return mygram


class RabbleRouser(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(community=-3)
    active = True

    RUMOR = Rumor(
        "{NPC} has been spreading a baseless conspiracy theory",
        offer_msg="You can speak to {NPC} at {NPC_SCENE} if you want to find out for yourself.",
        memo="{NPC} has been expounding a conspiracy theory and stirring up local resentment against {METROSCENE} leader {LEADER}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        return "METRO" in pstate.elements and isinstance(pstate.elements["METRO"].city_leader, gears.base.Character)

    def custom_init(self, nart):
        # Start by creating and placing the rabble-rouser.
        scene = self.seek_element(
            nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_ok_scene
        )

        metroscene = self.elements["METROSCENE"]
        self.conspiracy = content.backstory.Backstory(
            commands=("CONSPIRACY",), elements={"LOCALE": metroscene}, keywords=metroscene.get_keywords()
        )

        npc = self.register_element(
            "NPC",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Pundit"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="NPC_SCENE")

        # Also save the leader in this plot.
        leader = self.elements["LEADER"] = self.elements["METRO"].city_leader

        # Find a military/police person in this city.
        guard = self.seek_element(
            nart, "GUARD", self._is_best_guard, scope=self.elements["METROSCENE"], must_find=False
        )
        if not guard:
            myplot = self.add_sub_plot(nart, "PLACE_LOCAL_REPRESENTATIVES",
                                       elements={"LOCALE": self.elements["METROSCENE"],
                                                 "FACTION": self.elements["METROSCENE"].faction})
            guard = myplot.elements["NPC"]
            self.elements["GUARD"] = guard

        # Why not add a tycoon and a rival politician as well?
        self.seek_element(
            nart, "_TYCOON_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        tycoon = self.register_element(
            "TYCOON",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Corporate Executive"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_TYCOON_SCENE")

        self.seek_element(
            nart, "_RIVAL_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        rival = self.register_element(
            "RIVAL",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Bureaucrat"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_RIVAL_SCENE")

        # Now, we don't know yet whether the rabble-rouser is in the right to be raising rabble, so we're going to
        # add a mystery to find out.
        suspect_cards = [ghchallenges.NPCSusCard(c) for c in (npc, leader, guard, tycoon, rival)]
        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        action_cards = [
            ghchallenges.VerbSusCardFeaturingNPC("Hire {}".format(npc), "to hire {}".format(npc),
                                                 "hired {}".format(npc), "did not hire {}".format(npc), npc),
            ghchallenges.VerbSusCardFeaturingNPC("Bribery", "to bribe {}".format(guard), "bribed {}".format(guard),
                                                 "did not bribe {}".format(guard), guard),
            pbge.okapipuzzle.VerbSusCard("Spread Lies", "to spread lies", "spread lies", "didn't spread lies",
                                         data={"image_name": "mystery_verbs.png", "frame": 2}),
            pbge.okapipuzzle.VerbSusCard("Embezzled", "to embezzle", "embezzled government funds",
                                         "didn't embezzle anything",
                                         data={"image_name": "mystery_verbs.png", "frame": 2}, gameob=npc),
            pbge.okapipuzzle.VerbSusCard("Sow Chaos", "to sow chaos in {}".format(self.elements["METROSCENE"]),
                                                 "sowed chaos in {}".format(self.elements["METROSCENE"]),
                                                 "did not cause chaos in {}".format(self.elements["METROSCENE"]),
                                                 data={"image_name": "mystery_verbs.png", "frame": 2})
        ]
        action_susdeck = pbge.okapipuzzle.SusDeck("Action", action_cards)

        motive_cards = [
            pbge.okapipuzzle.VerbSusCard(
                "Keep Power", "to maintain power", "maintained control", "didn't try to maintain power",
                data={"image_name": "mystery_motives.png", "frame": 2}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Take Over", "to usurp control of {}".format(self.elements["METROSCENE"]), "usurped control",
                "didn't try to usurp power",
                data={"image_name": "mystery_motives.png", "frame": 2}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Pay Debts", "to pay off gambling debts", "paid off gambling debts", "didn't have gambling debts",
                data={"image_name": "mystery_verbs.png", "frame": 5}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            ghchallenges.VerbSusCardFeaturingNPC(
                "Get Revenge", "to get revenge on {}".format(leader),
                "got revenge", "didn't try to get revenge on {}".format(leader), leader,
                role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Become Rich", "to enrich themself", "enriched themself", "didn't get rich",
                data={"image_name": "mystery_motives.png", "frame": 5}, role=pbge.okapipuzzle.SUS_MOTIVE
            )
        ]
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)

        # We are going to create the solution here because we need to error-check unreasonable cases.
        solution = [random.choice(suspect_cards), random.choice(action_cards), random.choice(motive_cards)]
        if random.randint(1,2) == 1:
            # The guilty party is most likely going to be the leader or the rabblerouser.
            solution[0] = random.choice(suspect_cards[:2])

        while solution[1].gameob is solution[0].gameob:
            solution[1] = random.choice(action_cards)

        if solution[0].gameob is leader:
            if solution[2] is motive_cards[1]:
                solution[2] = motive_cards[0]
            elif solution[2] is motive_cards[3]:
                solution[2] = motive_cards[4]
        elif solution[0].gameob is npc:
            if solution[2] is motive_cards[0]:
                solution[2] = motive_cards[1]

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "Trouble in {}".format(self.elements["METROSCENE"]),
            (suspect_susdeck, action_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}.",
            solution=solution
        ))

        # Now, we subcontract the actual mystery challenge out to a utility plot.
        self.add_sub_plot(nart, "POLITICAL_MYSTERY_CHALLENGE", ident="MCHALLENGE",
                          elements={"VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice)})

        # We're also going to subcontract out NPC's attempt to dethrone LEADER and LEADER's attempt to discredit NPC.
        sp = self.add_sub_plot(
            nart, "DETHRONE_BY_POPULAR_UPRISING", ident="DETHRONE_CHALLENGE",
            elements={"NPC": leader, "VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice),
                      "UPHELD_VIRTUE": random.choice([gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Duty])}
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(npc)

        sp = self.add_sub_plot(
            nart, "DIPLOMACY_TO_DISCREDIT", ident="DISCREDIT_CHALLENGE",
            elements={"NPC": npc, "VIOLATED_VIRTUE": gears.personality.Fellowship,
                      "UPHELD_VIRTUE": random.choice([None, gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Justice, gears.personality.Duty]),

                      }
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(leader)

        # Store the villain of the story as another element. This way, we only need to deal with the stuff once.
        self.elements["CULPRIT"] = solution[0].gameob

        self.mystery_solved = False
        self.solution_public = False

        self.started_dethrone = False
        self.won_dethrone = False

        self.started_discredit = False
        self.won_discredit = False

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_CULTURE in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_best_guard(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.combatant and
                nart.camp.is_not_lancemate(candidate) and candidate is not self.elements["LEADER"] and
                nart.camp.are_faction_allies(candidate, self.elements["METROSCENE"]) and not candidate.mnpcid)

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text}".format(**self.elements), location=self.elements["CULPRIT"].scene
        )

    def t_UPDATE(self, camp):
        # If the city leader changes or dies, just end this plot. Things have changed sufficiently that whatever
        # schemes were going on before are no longer relevant.
        if self.elements["METRO"].city_leader is not self.elements["LEADER"]:
            self.end_plot(camp, True)
        elif not self.elements["LEADER"].is_operational():
            self.end_plot(camp, True)


    def MCHALLENGE_WIN(self, camp):
        self.solution_public = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text} This information is no longer a secret.".format(**self.elements),
            location=self.elements["CULPRIT"].scene
        )

    def DETHRONE_CHALLENGE_WIN(self, camp):
        self.won_dethrone = True

    def DISCREDIT_CHALLENGE_WIN(self, camp):
        self.won_discredit = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] [CRYPTIC_GREETING]",
            ContextTag([context.HELLO, ]),
        ))

        if not self.started_dethrone:
            mylist.append(Offer(
                self.conspiracy.get("text"),
                ContextTag([context.CUSTOM, ]), data={"reply": "I heard that you have some thoughts on current events?"},
                subject=self.conspiracy, subject_start=True
            ))

            mylist.append(Offer(
                "It is clearly {LEADER.job} {LEADER}, the leader of {METROSCENE}. Will you help me convince the populace to remove {NPC.gender.object_pronoun} from power?".format(**self.elements),
                ContextTag([context.CUSTOMREPLY, ]), data={"reply": "And who do you think is responsible for all of that?"},
                subject=self.conspiracy
            ))

            if not self.started_discredit:
                mylist.append(Offer(
                    "[THATS_GOOD] Speak to the people of {METROSCENE}... Make them see the truth!".format(**self.elements),
                    ContextTag([context.CUSTOMGOODBYE, ]), data={"reply": "[IWILLDOMISSION]", "mission": "help spread your message"},
                    subject=self.conspiracy, dead_end=True, effect=self._start_dethrone
                ))

            mylist.append(Offer(
                "In time, even your eyes will be opened to the truth. [GOODBYE]".format(**self.elements),
                ContextTag([context.CUSTOMGOODBYE, ]), data={"reply": "[MISSION:DENY]"},
                subject=self.conspiracy, dead_end=True
            ))

            mylist.append(Offer(
                "[GOODBYE] Be careful out there... {LEADER} is [adjective].".format(**self.elements),
                ContextTag([context.CUSTOMREPLY, ]), data={"reply": "[I_HAVE_HEARD_ENOUGH]"},
                subject=self.conspiracy, dead_end=True
            ))
        elif self.won_dethrone:
            if self.elements["NPC"] is self.elements["CULPRIT"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now I can assume my rightful position as leader of {METROSCENE}!".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), data={"reply": "I have turned the people of {METROSCENE} against {LEADER}.".format(**self.elements)},
                    effect=self._win_dethrone, dead_end=True
                ))
            else:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now {METROSCENE} is free of {LEADER.gender.possessive_determiner} tyranny!".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), data={"reply": "I have turned the people of {METROSCENE} against {LEADER}.".format(**self.elements)},
                    effect=self._win_dethrone, dead_end=True
                ))

        return mylist

    def _start_dethrone(self, camp):
        self.subplots["DETHRONE_CHALLENGE"].activate(camp)
        self.started_dethrone = True

    def _win_dethrone(self, camp: gears.GearHeadCampaign):
        self.elements["METRO"].city_leader = None
        if self.elements["LEADER"] is not self.elements["CULPRIT"]:
            # Oops. Someone else was behind this all along.
            self.culprit_succeeded(camp)
        camp.freeze(self.elements["LEADER"])
        self.end_plot(camp, True)

    def culprit_succeeded(self, camp):
        culprit = self.elements["CULPRIT"]
        if self.elements["NPC"] is culprit:
            self.elements["METRO"].city_leader = self.elements["NPC"]
            cityhall = self.elements["LEADER"].scene
            self.elements["NPC"].place(cityhall)
            content.load_dynamic_plot(camp, "CONSEQUENCE_CULTOFPERSONALITY", PlotState().based_on(self))
            pbge.alert("With {LEADER} out of the picture, {NPC} becomes the new leader of {METROSCENE}.".format(**self.elements))
        elif self.elements["LEADER"] is culprit:
            camp.freeze(self.elements["NPC"])
            content.load_dynamic_plot(camp, "CONSEQUENCE_TOTALCRACKDOWN", PlotState().based_on(self, update_elements={"CRACKDOWN_REASON": "{LEADER} has eliminated all resistance to {LEADER.gender.possessive_determiner} absolute rule".format(**self.elements)}))
            pbge.alert("With all resistance eliminated, {LEADER} becomes the absolute dictator of {METROSCENE}.".format(**self.elements))
        else:
            self.elements["METRO"].city_leader = culprit
            cityhall = self.elements["LEADER"].scene
            camp.freeze(self.elements["LEADER"])
            culprit.place(cityhall)
            content.load_dynamic_plot(camp, "CONSEQUENCE_KLEPTOCRACY", PlotState().based_on(self))
            pbge.alert("While {LEADER} was busy worrying about {NPC}, {CULPRIT} seized control of {METROSCENE}.".format(**self.elements))


    def LEADER_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        leader = self.elements["LEADER"]
        if self._rumor_memo_delivered and not self.started_discredit:
            mylist.append(Offer(
                "It's true. {NPC} is a rabble-rouser who has been trying to set the people of {METROSCENE} against me. If you could help me deliver a more positive message, that would be greatly appreciated.".format(**self.elements),
                ContextTag([context.CUSTOM, ]), data={"reply": "I heard that {NPC} is causing problems for you.".format(**self.elements)},
                subject=leader, subject_start=True
            ))

            mylist.append(Offer(
                "That's too bad. Politics isn't for everyone.".format(**self.elements),
                ContextTag([context.CUSTOMREPLY, ]), data={"reply": "[MISSION:DENY]"},
                subject=leader
            ))

            if not self.started_dethrone:
                mylist.append(Offer(
                    "[THANK_YOU] Just talk with some of the citizens and I'm sure you'll find them receptive to my message.".format(**self.elements),
                    ContextTag([context.CUSTOMREPLY, ]), data={"reply": "[IWILLDOMISSION]", "mission": "help improve your image"},
                    subject=leader, effect = self._start_discredit, dead_end=True
                ))

        if self.won_discredit:
            if leader is self.elements["CULPRIT"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] With all opposition extinguished, I can now rule {METROSCENE} as I please!".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))
            elif self.elements["CULPRIT"] is not self.elements["NPC"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] But I've learned too late that {NPC} wasn't the real threat to {METROSCENE}...".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))
            else:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now {METROSCENE} can once more be united as a true community!".format(**self.elements),
                    ContextTag([context.CUSTOM, ]), data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))


        return mylist

    def _start_discredit(self, camp):
        self.subplots["DISCREDIT_CHALLENGE"].activate(camp)
        self.started_discredit = True

    def _win_discredit(self, camp: gears.GearHeadCampaign):
        if self.elements["NPC"] is not self.elements["CULPRIT"]:
            # Oops. Someone else was behind this all along.
            self.culprit_succeeded(camp)
        camp.freeze(self.elements["NPC"])
        self.end_plot(camp, True)

    def CULPRIT_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        bribe = gears.selector.calc_mission_reward(self.rank, 1000)
        if self.mystery_solved:
            mylist.append(Offer(
                "Wait, we can come to a deal about this... I'll offer you ${:,} to forget you heard anything.".format(bribe),
                ContextTag([context.CUSTOM]), data={"reply": "I know you {}.".format(mystery.solution[1].verbed)},
                subject=self, subject_start=True
            ))
            if self.solution_public:
                mylist.append(Offer(
                    "[I_WOULD_HAVE_GOTTEN_AWAY]",
                    ContextTag([context.CUSTOMREPLY]), data={"reply": "Too late. I've already released the information."},
                    subject=self, effect=self._catch_culprit
                ))
            else:
                mylist.append(Offer(
                    "[I_WOULD_HAVE_GOTTEN_AWAY]",
                    ContextTag([context.CUSTOMREPLY]), data={"reply": "No deal. You're going down."},
                    subject=self, effect=self._catch_culprit, dead_end=True
                ))

                mylist.append(Offer(
                    "[PLEASURE_DOING_BUSINESS]",
                    ContextTag([context.CUSTOMREPLY]), data={"reply": "That sounds like a fair trade."},
                    subject=self, effect=self._release_culprit, dead_end=True
                ))

            mylist.append(Offer(
                "Let me know when you've come to a decision.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "I'll think about it."},
                subject=self, dead_end=True
            ))

        return mylist

    def _get_generic_offers(self, npc, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        reward = gears.selector.calc_mission_reward(self.rank, 165)

        if camp.is_not_lancemate(npc):
            if self.mystery_solved and camp.are_faction_allies(npc, self.elements["METROSCENE"]) and not any([c.gameob is npc for c in mystery.solution]):
                mylist.append(Offer(
                    "[THIS_CANNOT_BE_ALLOWED] Here is a reward of ${:,} for helping to stop this crime.".format(reward),
                    ContextTag([context.CUSTOM]), data={"reply": mystery.solution_text},
                    effect=self._turn_in_culprit, dead_end=True
                ))
        return mylist

    def _get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mygram = dict()

        if npc is not self.elements["LEADER"] and self.elements["NPC"] is not self.elements["CULPRIT"]:
            mygram["[CURRENT_EVENTS]"] = [
                "{LEADER} has not been a great leader for {METROSCENE}.".format(**self.elements),
            ]

        return mygram

    def _turn_in_culprit(self, camp):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 165)
        self._catch_culprit(camp)

    def _catch_culprit(self, camp: gears.GearHeadCampaign):
        camp.dole_xp(200)
        camp.freeze(self.elements["CULPRIT"])
        if self.elements["CULPRIT"] is self.elements["LEADER"]:
            self.elements["METRO"].city_leader = None
        pbge.alert("With {CULPRIT} out of the way, life soon returns to normal in {METROSCENE}.".format(**self.elements))
        self.end_plot(camp, True)

    def _release_culprit(self, camp: gears.GearHeadCampaign):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 1000)
        self.culprit_succeeded(camp)
        self.end_plot(camp, True)
