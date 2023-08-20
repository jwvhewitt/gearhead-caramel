from pbge.plots import Plot, Rumor, PlotState
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue, content
from game.ghdialogue import context, OneShotInfoBlast
import gears
import pbge
from .dd_main import DZDRoadMapExit, RoadNode
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, backstory, GHNarrativeRequest, PLOT_LIST, ghchallenges
from gears import personality
from . import ghquests, missionbuilder, dd_main, dd_customobjectives
from pbge import quests, memos


class OnawaMystery(Plot):
    LABEL = "DZD_ONAWA_MYSTERY"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "there's a recon pilot from the Terran Defense Force at {NPC_SCENE}",
        offer_msg = "Her name is Onawa. She's been patrolling the dead zone, looking for something or another. Maybe you can get a mission from her? I don't know.",
        offer_subject="a recon pilot from the Terran Defen", offer_subject_data="this recon pilot",
        memo="Onawa, a recon pilot for the Terran Defense Force, is currently at {NPC_SCENE}.",
        prohibited_npcs=("NPC")
    )

    def custom_init(self, nart):
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_okay_scene)
        npc = self.register_element("NPC", nart.camp.get_major_npc("Onawa GH1"), dident="NPC_SCENE")
        if not npc:
            return False
        self._spoke_before = False
        self._got_mission = False
        self._got_mission_intro = False
        self.needed_wins = random.choice((1,2,2,2,3,3))

        print(self.elements["METROSCENE"])

        self.infoblasts = (
            OneShotInfoBlast(
                "Snake Lake",
                "I was presenting arguments in favor of Constitutional Amendment 79-MS, which granted full citizenship rights to all sentient beings no matter if they are organic, mechanical, or biomechanical. The news media called this 'The Omega Law' but it is not a law it is a constitutional amendment."
            ),
        )

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_MEETING in candidate.attributes)

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def NPC_offers(self, camp):
        mylist = list()

        if not self._spoke_before:
            if camp.pc.has_badge("Typhon Slayer"):
                mylist.append(Offer(
                    "[HELLO] I never expected to see someone like you out here in the middle of nowhere.",
                    context=ContextTag([context.HELLO,]), effect=self._speak_first_time
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] This is a dangerous place; watch your back when you're traveling the highway.",
                    context=ContextTag([context.HELLO,]), effect=self._speak_first_time
                ))

        if not self._got_mission:
            if not self._got_mission_intro:
                mylist.append(Offer(
                    "[THATS_RIGHT] There is something operating in the deadzone. It's been attacking caravans, mecha, isolated settlements. No survivors. Aside from the wreckage left behind, none of the usual signs of combat. And whatever it is, our sensors can't pick it up.",
                    context=ContextTag([context.CUSTOM]), subject=self, subject_start=True,
                    effect=self._get_mission_intro,
                    data={"reply": "Word is that you're out here searching for something."},
                ))
            else:
                mylist.append(Offer(
                    "It's fast. It's invisible to long range sensors. It can destroy a gamma-class mecha squad before they have a chance to defend themselves. Its attack patterns don't correspond to any of our known enemies. Maybe you could help me- if I had a second team gathering evidence, maybe we could convince the Defense Force brass to take this seriously.",
                    context=ContextTag([context.MISSION]),
                    subject=self, subject_start=True
                ))

            mylist.append(Offer(
                "I may just be paranoid because of the Typhon incident last year, but there have been eyewitness accounts of a strange floating object near some of the attack sites. Could be another biomonster. Could be something else. The Defense Force thinks people going missing in the deadzone is just a normal thing. I can't accept that. So I'm here investigating on my own.",
                context=ContextTag([context.CUSTOMREPLY]), subject="There is something operating in the deadzone. It's been attacking caravans,",
                data={"reply": "I can't help but notice you said \"something\" instead of \"someone\"."},
                replies=[pbge.dialogue.Reply(
                    "Tell me more.", destination=pbge.dialogue.Cue(ContextTag([context.MISSION]))
                )], dead_end=True
            ))

            mylist.append(Offer(
                "[GOOD] A convoy has disappeared near {}; it sounds like it might be related to the other cases I've been investigating. If you could go there and see what you can find out, that would be a big help.".format(self.elements["TOWNS"][-1]),
                context=ContextTag([context.ACCEPT]),
                subject=self, effect=self._start_mission
            ))

            mylist.append(Offer(
                "Understood. [GOODBYE]",
                context=ContextTag([context.DENY]), dead_end=True, subject=self
            ))

        for ib in self.infoblasts:
            if ib.active:
                mylist.append(ib.build_offer())

        return mylist

    def _speak_first_time(self, camp):
        self._spoke_before = True

    def _start_mission(self, camp):
        self._got_mission = True
        self.start_next_mission_part(camp)

    def _get_mission_intro(self, camp):
        self._got_mission_intro = True

    def start_next_mission_part(self, camp):
        next_town: dd_main.RoadNode = self.elements["TOWNS"].pop()
        content.load_dynamic_plot(camp, "DZD_ONAWA_SEARCH_MISSION", PlotState().based_on(self, update_elements={"METROSCENE": next_town.destination, "METRO": next_town.destination.metrodat, "ON_WIN": self.win_search_plot}))

    def win_search_plot(self, camp):
        self.needed_wins -= 1
        if self.needed_wins > 0:
            self.start_next_mission_part(camp)
        else:
            next_town: dd_main.RoadNode = self.elements["TOWNS"].pop()
            content.load_dynamic_plot(camp, "DZD_ONAWA_SEARCH_CONCLUSION", PlotState().based_on(self, update_elements={
                "METROSCENE": next_town.destination, "METRO": next_town.destination.metrodat, "ON_WIN": self.win_search_conclusion,
                "ONAWA": self.elements["NPC"], "MISSION_GATE": next_town.entrance
            }))

    def win_search_conclusion(self, camp):
        self.end_plot(camp, True)


ONAWA_MISSION_MEMO = "Onawa sent you to investigate a mysterious flying object; so far the trail has lead to {METROSCENE}."


class OnawaSearchConclusion(Plot):
    LABEL = "DZD_ONAWA_SEARCH_CONCLUSION"
    active = True
    scope = True

    RUMOR_PATTERNS = (
        "{NPC} escaped from an unidentified flying object",
        "{NPC} was attacked by a mysterious flying object",
    )

    def custom_init(self, nart):
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_okay_scene)

        npc = self.register_element("NPC", gears.selector.random_character(
            rank=random.randint(20,60), camp=nart.camp, local_tags=self.elements["METROSCENE"].attributes, combatant=True
        ), dident="NPC_SCENE")

        self.memo = memos.Memo(ONAWA_MISSION_MEMO.format(**self.elements), self.elements["METROSCENE"])
        rpat = random.choice(self.RUMOR_PATTERNS).format(**self.elements)
        self.RUMOR = Rumor(
            rpat,
            offer_msg="The best person to ask would be {NPC} at {NPC_SCENE}.",
            offer_subject=rpat,
            offer_subject_data="{NPC} and the flying object",
            memo="You learned that {NPC} was attacked by a mysterious flying object. This could be related to the hostile entity that Onawa is searching for.",
            npc_is_prohibited_fun=self._is_not_in_metroscene
        )

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        # Create the mission seed.
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            nart.camp, "Investigate {NPC}'s Battle".format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=npc.faction,
            rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_ONAWA_MISSION,),
            one_chance=True,
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self.win_challenge, on_loss=self.lose_challenge
        )

        self.got_mission = False
        self.finished_mission = False
        self.actually_won = False

        return True

    def win_challenge(self, camp):
        self.elements["ON_WIN"](camp)
        self.finished_mission = True
        self.actually_won = True

    def lose_challenge(self, camp):
        self.elements["ON_WIN"](camp)
        self.finished_mission = True
        self.actually_won = False

    def _is_best_scene(self, nart, candidate):
        return (
            isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
            and (gears.tags.SCENE_HOSPITAL in candidate.attributes or gears.tags.SCENE_GARAGE in candidate.attributes)
        )

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    @staticmethod
    def _is_not_in_metroscene(self, camp, npc):
        return not (camp.scene.get_metro_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"])

    def NPC_offers(self, camp):
        mylist = list()

        if not self.got_mission:
            mylist.append(Offer(
                "[HELLO] I suppose you're here to ask about the weird aerofighter that nearly killed me, huh?",
                context=ContextTag([context.HELLO])
            ))

            mylist.append(Offer(
                "It moved faster than I could follow. First thing I remember is an explosion that took out my left arm, then I saw it. A white star-shaped thing zig-zagging through the air. I think I managed to land one shot on it but by that time I was just trying to get away.".format(**self.elements),
                context=ContextTag([context.CUSTOM]), effect=self.get_mission, dead_end=True,
                data={"reply": "That's right. What can you tell me about it?"}
            ))

        return mylist

    def get_mission(self, camp):
        self.got_mission = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.got_mission and not self.finished_mission:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


class OnawaSearchMission(Plot):
    LABEL = "DZD_ONAWA_SEARCH_MISSION"
    active = True
    scope = True

    RUMOR_PATTERNS = (
        "{NPC} saw an unidentified flying object recently",
        "there was a weird glowing thing that few over {METROSCENE}; {NPC} saw it",
        "{NPC} says {NPC.gender.subject_pronoun} saw a mysterious object in the sky",
        "{NPC} claims to have seen an unidentified flying object",
        "{NPC} thinks an alien spaceship flew past {METROSCENE}"
        "{NPC} saw a bright light in the sky",
        "{NPC} saw a weird airplane near that place where the trucker disappeared"
    )

    EVENT_PATTERNS = (
        "I was replying to a distress call, but by the time I got there the convoy had been ripped to shreds.",
        "On the way into {METROSCENE} I saw flashing lights in the distance; went to check it out, and found carnage.",
        "While exploring I came across an Aegis scout team... the mecha were intact, but all the pilots were dead. I left that place as fast as I could.",
        "I was searching for the missing convoy, and kind of wish I had never found them. The mecha had disintegrated into pools of toxic slag.",
        "The defense force sent me to aid one of their patrols. By the time I reached the battlefield, I found their mecha frozen in place- the pilots were dead, with no apparent damage to the machines.",
    )

    DESTINATION_PATTERNS = (
        "I saw a light in the sky flying away, heading towards {NEXT_SCENE}.",
        "I briefly saw a five pointed object in the sky moving in the direction of {NEXT_SCENE}.",
        "I saw some kind of aerofighter speeding away towards {NEXT_SCENE}, but my sensors couldn't get a lock on it.",
        "I saw a dark shadow in the sky, and thought I was dead. But then it sped off towards {NEXT_SCENE}.",
        "I've seen plenty of mecha... the thing I saw flying above that place? It wasn't a mecha. It flew towards {NEXT_SCENE}."
    )

    def custom_init(self, nart):
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_okay_scene)

        npc = self.register_element("NPC", gears.selector.random_character(
            rank=random.randint(20,60), camp=nart.camp, local_tags=self.elements["METROSCENE"].attributes, combatant=True
        ), dident="NPC_SCENE")

        self.elements["NEXT_SCENE"] = self.elements["TOWNS"][-1]

        self.memo = memos.Memo(ONAWA_MISSION_MEMO.format(**self.elements), self.elements["METROSCENE"])
        rpat = random.choice(self.RUMOR_PATTERNS).format(**self.elements)
        self.RUMOR = Rumor(
            rpat,
            offer_msg="[I_DONT_KNOW_MUCH] You should speak to {NPC} at {NPC_SCENE} for more information.",
            offer_subject=rpat,
            offer_subject_data="{NPC} and the flying object",
            memo="You learned that {NPC} saw a mysterious flying object. This could be related to the hostile entity that Onawa is searching for.",
            npc_is_prohibited_fun=self._is_not_in_metroscene, prohibited_npcs=("NPC",)
        )

        return True

    def win_challenge(self, camp):
        if self.active:
            self.elements["ON_WIN"](camp)
            self.end_plot(camp, True)

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_MEETING in candidate.attributes)

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    @staticmethod
    def _is_not_in_metroscene(self, camp, npc):
        return not (camp.scene.get_metro_scene() is self.elements["METROSCENE"])

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[CRYPTIC_GREETING] [I_SAW_SOMETHING_YOU_WOULDNT_BELIEVE]",
            context=ContextTag([context.HELLO])
        ))

        mylist.append(Offer(
            (random.choice(self.EVENT_PATTERNS)+" "+random.choice(self.DESTINATION_PATTERNS)).format(**self.elements),
            context=ContextTag([context.INFO]), effect=self.win_challenge, dead_end=True,
            data={"subject": "the mysterious flying object"}
        ))

        return mylist


class OmegaTalksTyphon(Plot):
    LABEL = "DZD_OMEGA1004"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "there's a robot hanging out at {NPC_SCENE}",
        offer_msg = "He seems to be a nice guy... I just never met a robot that's a person before. But once you start talking you forget that he's made of metal.",
        offer_subject="a robot hanging out", offer_subject_data="the robot",
        memo="There's a robot hanging out at {NPC_SCENE}.",
        prohibited_npcs=("NPC")
    )

    QOL = gears.QualityOfLife(community=1)

    def custom_init(self, nart):
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_okay_scene)
        npc = self.register_element("NPC", nart.camp.get_major_npc("Omega 1004"), dident="NPC_SCENE")
        if not npc:
            return False
        self._got_initial_story = False
        self._got_typhon_story = False

        self.infoblasts = (
            OneShotInfoBlast(
                "Snake Lake",
                "I was presenting arguments in favor of Constitutional Amendment 79-MS, which granted full citizenship rights to all sentient beings no matter if they are organic, mechanical, or biomechanical. The news media called this 'The Omega Law' but it is not a law it is a constitutional amendment."
            ),
        )
        self.shop = services.SkillTrainer([gears.stats.Biotechnology, gears.stats.Wildcraft, gears.stats.Science])

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_BUILDING in candidate.attributes)

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def NPC_offers(self, camp):
        mylist = list()
        if not self._got_initial_story:
            if camp.pc.has_badge("Typhon Slayer"):
                mylist.append(Offer(
                    "[THANKS] I replaced all of my rusted out body panels, had some chrome installed, and bought myself a genuine face. It's top quality synthetic polyvinyl chloride.",
                    ContextTag([context.CUSTOM]), data={"reply": "Omega! You're looking good these days."},
                    subject=self, subject_start=True
                ))
            else:
                mylist.append(Offer(
                    "Yes, your information is correct, though I am not certain I feel comfortable with that being my best known achievement. It is a pleasure to meet a fellow cavalier.",
                    ContextTag([context.CUSTOM]), data={"reply": "Aren't you the robot that helped defeat Typhon?"},
                    subject=self, subject_start=True
                ))

            mylist.append(Offer(
                "I am happy to be back at my old task, cataloging neofauna in the trans-Eurasian dead zone. I spent far too much of the past year indoors at the parliament buildings in Snake Lake. I would be happy to discuss my research with you sometime.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "What have you been doing lately?"},
                subject=self, effect=self._do_introduction
            ))
        else:
            mylist.append(Offer(
                "Nothing would make me happier... other than possibly discovering a new type of feral synthoid.",
                ContextTag([context.CUSTOM]), data={"reply": "I would like to discuss your research findings."},
                dead_end=True, effect=self.shop
            ))
            if random.randint(1,2) == 1 and not self._got_typhon_story:
                mylist.append(Offer(
                    "I have been thinking about Typhon again, and how tragic its life was. Imagine being created solely as a weapon. A living, feeling tool of death. And think of Cetus, never truly born, but experimented upon and tortured for centuries. I run the scenarios again and again yet cannot find a happy ending.",
                    ContextTag([context.CUSTOM]), data={"reply": "You look sort of down today... Is anything wrong?"},
                    subject=self.shop, subject_start=True
                ))

            mylist.append(Offer(
                "And that is what bothers me- unlike my human lancemates, it was not fear or will to survive that led me to kill Typhon. It was the cold equation that Typhon must die so many others could live. Even with the benefit of hindsight I see no other solutions.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "You did the only thing you could do."},
                subject=self.shop, effect=self._do_typhon_talk
            ))

            mylist.append(Offer(
                "Yet as cavaliers we must always try to make things better. I know my actions that day were mathematically justified. It was the cold equation that Typhon must die so many others could live. Still, I mourn for the creature that was never given a chance to really exist.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "Life isn't fair. In fact usually it sucks."},
                subject=self.shop, effect=self._do_typhon_talk
            ))

        for ib in self.infoblasts:
            if ib.active:
                mylist.append(ib.build_offer())

        return mylist

    def _do_introduction(self, camp):
        self._got_initial_story = True
        self.RUMOR = False
        self.memo = pbge.memos.Memo("Omega 1004 at {NPC_SCENE} offered to discuss his research with you.".format(**self.elements), location=self.elements["NPC_SCENE"])

    def _do_typhon_talk(self, camp):
        self._got_typhon_story = True


class RanMagnusMechaFactory(Plot):
    LABEL = "DZD_MAGNUSMECHA"

    active = True
    scope = "METRO"

    QOL = gears.QualityOfLife(defense=1, prosperity=1)

    def custom_init(self, nart):
        # Create a building within the town.
        garage_name = "Magnus Mecha Works"
        building = self.register_element(
            "_EXTERIOR", ghterrain.IndustrialBuilding(
                waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=garage_name)},
                door_sign=(ghterrain.FixitShopSignEast, ghterrain.FixitShopSignSouth),
                tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CONNECTED_ROOM]),
            dident="METROSCENE"
        )

        self.rank = 55
        tplot = self.add_sub_plot(nart, "MECHA_WORKSHOP", elements={"BUILDING_NAME": garage_name})
        self.elements["LOCALE"] = tplot.elements["LOCALE"]

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["METROSCENE"], tplot.elements["LOCALE"],
                                                    room2=tplot.elements["FOYER"],
                                                    room1=building, door1=building.waypoints["DOOR"],
                                                    move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        name="Ran Magnus",
                                        rank=75, local_tags=(gears.personality.GreenZone,),
                                        job=gears.jobs.ALL_JOBS["Mecha Designer"],
                                        birth_year=106, combatant=False, faction=gears.factions.ProDuelistAssociation,
                                        personality=[personality.Passionate, personality.Sociable,
                                                     personality.Fellowship],
                                        mnpcid="RAN_MAGNUS",
                                        gender=gears.genderobj.Gender.get_default_female(),
                                        portrait='card_f_ranmagnus.png',
                                        colors=(gears.color.GriffinGreen, gears.color.DarkSkin, gears.color.Fuschia,
                                                gears.color.PlasmaBlue, gears.color.CardinalRed),
                                    ))
        npc.place(tplot.elements["LOCALE"], team=tplot.elements["CIVILIAN_TEAM"])

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.ProDuelistAssociation,
                                  ware_types=services.MEXTRA_STORE, rank=55)

        self.got_reward = False

        self.magnus_info = (
            OneShotInfoBlast("Osmund",
                             "We used to be lancemates back in the old days. You couldn't ask for a better partner. Then his knees gave out and I discovered that I like building mecha better than I like blasting them."),

            OneShotInfoBlast("mecha",
                             "Kind of a lifelong obsession for me. One of several, to be honest. But, it's the one that gets me paid. I've been designing mecha for thirty years now. Around ten years back I started this company and now I build mecha, too."),

            OneShotInfoBlast("design",
                             "It's important that a mecha know what its job is. There is no such thing as a perfect mecha, just fitness for a particular role. Install that which is useful, uninstall that which is not, and create that which is essentially your own."),

            OneShotInfoBlast("factory",
                             "This is my first factory in Eurasia. We're trying to ramp up production; the possibility of a war with Luna has doubled the demand for our meks. It's way too cold in {} but the local food is delicious so that kind of evens out.".format(
                                 self.elements["METROSCENE"]),
                             subject_text="the factory"),
        )

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        if camp.campdata.get("MINE_MISSION_WON") and not self.got_reward:
            mylist.append(Offer(
                "[HELLO] Osmund told me that you liberated my mine from those bandits; that means you get to buy the good stuff.",
                context=ContextTag([context.HELLO]), effect=self._open_custom_shop
                ))
        else:
            mylist.append(Offer("[HELLO] [_MAGNUS_SPIEL]",
                                context=ContextTag([context.HELLO]),
                                ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "mecha"}
                            ))

        for inf in self.magnus_info:
            if inf.active:
                mylist.append(inf.build_offer())

        return mylist

    def _open_custom_shop(self, camp):
        self.got_reward = True
        self.shop.sell_champion_equipment = True
        self.shop.last_updated = -1
        self.elements["SHOPKEEPER"].relationship.history.append(gears.relationships.Memory(
            "you liberated my mine from some bandits", "I recovered your mine from bandits", 10,
            (gears.relationships.MEM_AidedByPC,)
        ))
        camp.campdata["CD_SPOKE_TO_RAN"] = True

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        mygram["[_MAGNUS_SPIEL]"] = [
            "This factory is where the magic happens.",
            "Next time you're in Wujung tell Osmund to come visit {METROSCENE}.".format(**self.elements),
            "Remember when [MEM_AidedByPC]? Good times.",
            "Obviously pilots are important, but it's the right design that spells the difference between victory and defeat.",
            "This is where the mecha magic happens."
        ]

        return mygram
