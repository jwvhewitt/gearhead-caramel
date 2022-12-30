from pbge.plots import Plot, Rumor
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context, OneShotInfoBlast
import gears
import pbge
from .dd_main import DZDRoadMapExit, RoadNode
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, backstory, GHNarrativeRequest, PLOT_LIST
from gears import personality


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
                "Yet as cavaliers we must always try to make things better. I know my actions that time were mathematically justified. It was the cold equation that Typhon must die so many others could live. Still, I mourn for the creature that was never given a chance to really exist.",
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
