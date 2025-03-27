# Utility plots for Raid on Pirate's Point, since I am still working on the scenario editor.

import random
from typing import override
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState, Adventure
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, worldmapwar, wmw_occupation
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections

ROPPCD_DEFECTION = "ROPPCD_DEFECTION"
ROPPCD_AIDED_DISSIDENTS = "ROPPCD_AIDED_DISSIDENTS"
# War status passed to the resolution plot.
E_WAR_STATUS = "E_WAR_STATUS"


ROPPCD_HERO_POINTS = "hero_points"
ROPPCD_FOUND_CARGO = "found_cargo"
ROPPCD_SPENT_CARGO = "spent_cargo"
ROPPCD_AEGIS_INFILTRATOR = "ROPPCD_AEGIS_INFILTRATOR"


class ROPP_WarStarter(Plot):
    LABEL = "ROPP_WAR_STARTER"
    scope = True
    active = True

    def custom_init(self, nart):
        self.elements[worldmapwar.WORLD_MAP_IDENTIFIER] = "WORLDMAP_6"
        world_map = nart.camp.campdata["WORLDMAP_6"]
        for node in world_map.nodes:
            node.visible = True

        war_teams = dict()
        war_teams[gears.factions.TheSolarNavy] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'],
            color=1, unpopular=False, occtype=wmw_occupation.WMWO_MARTIAL_LAW
        )

        war_teams[gears.factions.TreasureHunters] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'],
            color=2, unpopular=False, occtype=wmw_occupation.WMWO_DEFENDER
        )

        war_teams[gears.factions.AegisOverlord] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000005'],
            color=3, unpopular=True, loyalty=50, occtype=wmw_occupation.WMWO_IRON_FIST
        )

        nart.camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.AegisOverlord)
        nart.camp.set_faction_enemies(gears.factions.TreasureHunters, gears.factions.TheSolarNavy)
        nart.camp.set_faction_enemies(gears.factions.AegisOverlord, gears.factions.TheSolarNavy)

        self.elements[worldmapwar.WORLD_MAP_TEAMS] = war_teams
        sp = self.add_sub_plot(nart, "WORLD_MAP_WAR", ident="ROPPWAR")
        self.world_map_war = self.register_element("WORLD_MAP_WAR", sp.world_map_war)
        nart.camp.campdata["WORLD_MAP_WAR"] = self.world_map_war
        nart.camp.campdata[ROPPCD_DEFECTION] = 0

        if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
            self.register_element("_ROOM", pbge.randmaps.rooms.FuzzyRoom(5,5), dident="LOCALE")
            self.register_element("COMPY", ghwaypoints.OldTerminal(
                plot_locked=True, anchor=pbge.randmaps.anchors.middle, name="War Simulator",
                desc="This is a computer terminal to test the world map war system. Yay!"
            ), dident="_ROOM")

        # Locate the major NPCs.
        self.seek_element(nart, "NPC_CHARLA", self._seek_charla, lock=True)
        self.seek_element(nart, "NPC_BRITAINE", self._seek_britaine, lock=True)
        self.seek_element(nart, "NPC_PINSENT", self._seek_pinsent, lock=True)
        self.seek_element(nart, "NPC_BOGO", self._seek_bogo, lock=True)
        self.seek_element(nart, "NPC_AEGIS", self._seek_aegis, lock=True)

        # Add the joiner plots
        self.add_sub_plot(nart, "ROPP_SOLAR_NAVY_JOINER")
        self.add_sub_plot(nart, "ROPP_TREASURE_HUNTERS_JOINER")
        self.add_sub_plot(nart, "ROPP_AEGIS_JOINER")

        # Add other plots which may require the major NPCs.
        self.add_sub_plot(nart, "ROPP_AEGIS_INFILTRATOR")

        return True

    def __setstate__(self, state):
        # For v0.947 and earlier: set occtype for the war teams.
        self.__dict__.update(state)
        wardict = self.elements[worldmapwar.WORLD_MAP_TEAMS]
        wardict[gears.factions.TheSolarNavy].occtype = wmw_occupation.WMWO_MARTIAL_LAW
        wardict[gears.factions.TheSolarNavy].unpopular = False
        wardict[gears.factions.AegisOverlord].occtype = wmw_occupation.WMWO_IRON_FIST

    def WORLD_MAP_WAR_PEACE(self, camp):
        pstate = PlotState(adv=Adventure("Resolution"), elements={E_WAR_STATUS: worldmapwar.WorldMapWar.WAR_WON, "WINNER": gears.factions.TreasureHunters}).based_on(self)
        _ = content.load_dynamic_plot(camp, "ROPP_RESOLUTION", pstate)

    def ROPPWAR_WIN(self, camp: gears.GearHeadCampaign):
        pstate = PlotState(adv=Adventure("Resolution"), elements={E_WAR_STATUS: worldmapwar.WorldMapWar.WAR_WON}).based_on(self)
        _ = content.load_dynamic_plot(camp, "ROPP_RESOLUTION", pstate)

    def ROPPWAR_LOSE(self, camp: gears.GearHeadCampaign):
        pstate = PlotState(adv=Adventure("Resolution"), elements={E_WAR_STATUS: worldmapwar.WorldMapWar.WAR_LOST}).based_on(self)
        _ = content.load_dynamic_plot(camp, "ROPP_RESOLUTION", pstate)

    def _seek_charla(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Admiral Charla"

    def _seek_britaine(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Britaine"

    def _seek_pinsent(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "General Pinsent"

    def _seek_bogo(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Jjang Bogo"

    def _seek_aegis(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.job and candidate.job.name == "Diplomat" and
                candidate.faction is gears.factions.AegisOverlord)

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.add_item("Start the next round", self.start_war_round)
        thingmenu.add_item("ZZWin the war", self.ROPPWAR_WIN)
        thingmenu.add_item("ZZLose the war", self.ROPPWAR_LOSE)

    def start_war_round(self, camp):
        myround = worldmapwar.WorldMapWarRound(self.world_map_war, camp)
        while myround.keep_going():
            result = myround.perform_turn()


class AegisInfiltratorPlot(Plot):
    LABEL = "ROPP_AEGIS_INFILTRATOR"
    scope = True
    active = True

    def custom_init(self, nart):
        self.have_informed_guild = False
        self.have_informed_navy = False
        self.have_activated_peace_offer = False
        self.have_activated_alliance_offer = False
        self.have_accepted_peace = False
        self.set_initial_memo = False
        return True

    def t_UPDATE(self, camp):
        if camp.campdata.get(ROPPCD_AEGIS_INFILTRATOR) and not self.memo and not self.set_initial_memo:
            self.memo = "You have learned that {} of the Treasure Hunter's Guild is secretly working for Aegis Overlord.".format(camp.campdata.get(ROPPCD_AEGIS_INFILTRATOR))
            self.set_initial_memo = True
        if self.elements["WORLD_MAP_WAR"].get_war_status(camp):
            self.end_plot(camp, True)

    def NPC_PINSENT_offers(self, camp):
        mylist = list()

        if self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.AegisOverlord) and not self.have_activated_alliance_offer:
            if camp.are_faction_enemies(gears.factions.AegisOverlord, gears.factions.TreasureHunters):
                mylist.append(Offer(
                    "So now both of us face a common enemy... If Jjang Bogo could be persuaded to form a temporary alliance with the Solar Navy, we could make short work of Aegis.",
                    ContextTag([context.CUSTOM]),
                    data={"reply": "Aegis Overlord and the Treasure Hunters are no longer aligned."},
                    effect=self._activate_alliance_offer
                ))

                mylist.append(Offer(
                    "So now both of us face a common enemy... If Jjang Bogo could be persuaded to form a temporary alliance with the Solar Navy, we could make short work of Aegis.",
                    ContextTag([context.UNFAVORABLE_CUSTOM]),
                    data={"reply": "Aegis Overlord has broken their alliance with the Treasure Hunters."},
                    effect=self._activate_alliance_offer
                ))

        return mylist

    def NPC_BRITAINE_offers(self, camp):
        mylist = list()
        ainpc = camp.campdata.get(ROPPCD_AEGIS_INFILTRATOR, None)
        if ainpc:
            mylist.append(Offer(
                "[THAT_IS_FUNNY] So Aegis pulled one over on the fox-king of the dust sea? What I'd give to see Jjang Bogo's face when he finds out...",
                ContextTag([context.CUSTOM]),
                data={"reply": "Aegis spy {} has infiltrated the Treasure Hunters Guild.".format(ainpc)}
            ))

        return mylist

    def NPC_CHARLA_offers(self, camp):
        mylist = list()
        if not self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.AegisOverlord) and not self.have_activated_peace_offer:
            if camp.are_faction_allies(gears.factions.AegisOverlord, gears.factions.TreasureHunters):
                mylist.append(Offer(
                    "That may be so, but as long as they maintain an alliance with the Treasure Hunter's Guild we must continue to fight.",
                    ContextTag([context.CUSTOM]),
                    data={"reply": "Aegis Overlord has been defeated."}
                ))
                mylist.append(Offer(
                    "That may be so, but as long as the Treasure Hunter's Guild counts them as allies we will continue to fight.",
                    ContextTag([context.UNFAVORABLE_CUSTOM]),
                    data={"reply": "Aegis Overlord has been defeated."}
                ))
            else:
                mylist.append(Offer(
                    "Since the alliance between Aegis and the Treasure Hunters Guild has been broken, our objectives have been satisfied. If Jjang Bogo were willing to sign a peace agreement this war could be over soon.",
                    ContextTag([context.CUSTOM]),
                    data={"reply": "Aegis Overlord has been defeated."},
                    effect=self._activate_peace_offer
                ))

                mylist.append(Offer(
                    "Since the alliance between Aegis and the Treasure Hunters Guild has been broken, our objectives have been satisfied. If Jjang Bogo were willing to sign a peace agreement this war could be over soon.",
                    ContextTag([context.UNFAVORABLE_CUSTOM]),
                    data={"reply": "Aegis Overlord has been defeated."},
                    effect=self._activate_peace_offer
                ))

        return mylist

    def _activate_peace_offer(self, camp):
        self.have_activated_peace_offer = True
        self._update_memo()

    def _activate_alliance_offer(self, camp):
        self.have_activated_alliance_offer = True
        self._update_memo()

    def _update_memo(self):
        if self.have_activated_peace_offer and self.have_activated_alliance_offer:
            self.memo = "With Aegis both defeated and no longer aligned with the Treasure Hunter's Guild, now would be a good time to broker a peace deal."
        elif self.have_activated_alliance_offer:
            self.memo = "Now that the Treasure Hunter's Guild is fighting Aegis Overlord, it may be possible to broker a truce with the Solar Navy to drive Aegis out of Pirate's Point for good."
        elif self.have_activated_peace_offer:
            self.memo = "Now that Aegis Overlord has been driven from Pirate's Point, Admiral Charla has expressed willingness to accept peace with the Treasure Hunters Guild."

    def NPC_BOGO_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        ainpc = camp.campdata.get(ROPPCD_AEGIS_INFILTRATOR, None)
        if ainpc:
            if camp.are_faction_allies(gears.factions.TreasureHunters, gears.factions.AegisOverlord) and not self.have_informed_guild:
                mylist.append(Offer(
                    "[THAT_IS_A_SERIOUS_ALLEGATION] I will attend to this personally, and if what you say is true, the Guild's relationship with Aegis is over.",
                    context=ContextTag([context.CUSTOM,]),
                    data={"reply": "{} is a spy for Aegis; the Guild's inner circle has been compromised.".format(ainpc)},
                    effect=self._inform_guild, 
                ))

                mylist.append(Offer(
                    "[THAT_IS_A_SERIOUS_ALLEGATION] I will attend to this personally, and if what you say is true, the Guild's relationship with Aegis is over.",
                    context=ContextTag([context.UNFAVORABLE_CUSTOM,]),
                    data={"reply": "Aegis has compromized your guild; {} is the name of their agent.".format(ainpc)},
                    effect=self._inform_guild, 
                ))

        if not self.have_accepted_peace:
            if self.have_activated_peace_offer:
                mylist.append(Offer(
                    "[LET_ME_GET_THIS_STRAIGHT] The Solar Navy will cease all hostilities and withdraw from Pirate's Point? The Treasure Hunter's Guild will remain in control of the city?",
                    context=ContextTag([context.CUSTOM,]),
                    data={"reply": "I come to you with a peace offer from the Solar Navy."}, 
                    subject=self, subject_start=True
                ))

                mylist.append(Offer(
                    "Your offer is accepted. Let's call the troops and tell them they can stop shooting now.",
                    context=ContextTag([context.CUSTOMREPLY,]),
                    data={"reply": "Yes, that's correct. The war is over."}, 
                    subject=self, effect=self._accept_peace, dead_end=True
                ))

                mylist.append(Offer(
                    "Don't wait too long. [GOODBYE]",
                    context=ContextTag([context.CUSTOMREPLY,]),
                    data={"reply": "[I_WILL_COME_BACK_LATER]"}, 
                    subject=self, dead_end=True
                ))

                mylist.append(Offer(
                    "[LET_ME_GET_THIS_STRAIGHT] The Solar Navy will cease all hostilities and withdraw from Pirate's Point? The Treasure Hunter's Guild will remain in control of the city?",
                    context=ContextTag([context.UNFAVORABLE_CUSTOM,]),
                    data={"reply": "I come to you with a peace offer from the Solar Navy."}, 
                    subject=self, subject_start=True
                ))

 
            elif self.have_activated_alliance_offer:
                if self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.AegisOverlord):
                    if self.have_informed_guild or self.elements["WORLD_MAP_WAR"].player_team is gears.factions.TreasureHunters:
                        mylist.append(Offer(
                            "[LET_ME_GET_THIS_STRAIGHT] The Solar Navy and the Treasure Hunter's Guild will fight side by side to rid Pirate's Point of Aegis Overlord. It may be a challenge convincing our troops to go along, as there is a lot of mistrust on both sides.",
                            context=ContextTag([context.CUSTOM,]),
                            data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                            subject=self, subject_start=True
                        ))

                        mylist.append(Offer(
                            "[LET_ME_GET_THIS_STRAIGHT] The Solar Navy and the Treasure Hunter's Guild will fight side by side to rid Pirate's Point of Aegis Overlord. It may be a challenge convincing our troops to go along, as there is a lot of mistrust on both sides.",
                            context=ContextTag([context.UNFAVORABLE_CUSTOM,]),
                            data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                            subject=self, subject_start=True
                        ))

                        mylist.append(Offer(
                            "I think you're right. For now, the Treasure Hunter's Guild and the Solar Navy will work side by side... to kick treacherous Lunar arse.",
                            context=ContextTag([context.CUSTOMREPLY,]),
                            data={"reply": "True, but I think it's worth trying."}, 
                            subject=self, effect=self._accept_alliance, dead_end=True
                        ))

                        mylist.append(Offer(
                            "Don't wait too long. [GOODBYE]",
                            context=ContextTag([context.CUSTOMREPLY,]),
                            data={"reply": "[I_WILL_COME_BACK_LATER]"}, 
                            subject=self, dead_end=True
                        ))
                    else:
                        mylist.append(Offer(
                            "What reason do I have to trust this alliance? I have already been betrayed by one ally, and we're now fighting a war on two fronts. I'll need a demonstration of your goodwill before I'm willing to take this seriously.",
                            context=ContextTag([context.CUSTOM,]),
                            data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                            dead_end=True
                        ))

                        mylist.append(Offer(
                            "What reason do I have to trust this alliance? I have already been betrayed by one ally, and we're now fighting a war on two fronts. I'll need a demonstration of your goodwill before I'm willing to take this seriously.",
                            context=ContextTag([context.UNFAVORABLE_CUSTOM,]),
                            data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                            dead_end=True
                        ))

                else:
                    mylist.append(Offer(
                        "Here are my terms. The Solar Navy will cease their aggression immediately. After helping us clean up the stragglers from Aegis, they will withdraw from Pirate's Point and leave the Treasure Hunter's Guild in peace. Can you guarantee this?",
                        context=ContextTag([context.CUSTOM,]),
                        data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                        subject=self, subject_start=True
                    ))

                    mylist.append(Offer(
                        "In that case, I welcome this new friendship with the Terran Federation. Let's put an end to all this unpleasantness.",
                        context=ContextTag([context.CUSTOMREPLY,]),
                        data={"reply": "Yes, that's correct. The war is over."}, 
                        subject=self, effect=self._accept_peace, dead_end=True
                    ))

                    mylist.append(Offer(
                        "Be quick about it. [GOODBYE]",
                        context=ContextTag([context.CUSTOMREPLY,]),
                        data={"reply": "[I_WILL_COME_BACK_LATER]"}, 
                        subject=self, dead_end=True
                    ))

                    mylist.append(Offer(
                        "Here are my terms. The Solar Navy will cease their aggression immediately. After helping us clean up the stragglers from Aegis, they will withdraw from Pirate's Point and leave the Treasure Hunter's Guild in peace. Can you guarantee this?",
                        context=ContextTag([context.UNFAVORABLE_CUSTOM,]),
                        data={"reply": "I come to you with an alliance offer from the Solar Navy."}, 
                        subject=self, subject_start=True
                    ))

        return mylist

    def _accept_peace(self, camp: gears.GearHeadCampaign):
        self.have_accepted_peace = True
        camp.check_trigger("PEACE", self.elements["WORLD_MAP_WAR"])
        self.memo = None

    def _accept_alliance(self, camp):
        camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.TheSolarNavy)
        camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.TerranDefenseForce)
        camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.Guardians)
        camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.TerranFederation)
        self.have_accepted_peace = True

        if not self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.AegisOverlord):
            camp.check_trigger("PEACE", self.elements["WORLD_MAP_WAR"])
        self.memo = None

    def _inform_guild(self, camp: gears.GearHeadCampaign):
        self.have_informed_guild = True
        camp.set_faction_enemies(gears.factions.TreasureHunters, gears.factions.AegisOverlord)
        _ = pbge.BasicNotification("The Treasure Hunters Guild and Aegis Overlord are now enemies.", count=150)
        mynpc = camp.campdata.get(ROPPCD_AEGIS_INFILTRATOR, None)
        myrelationship = camp.get_relationship(mynpc)
        myrelationship.attitude = random.choice((gears.relationships.A_RESENT, gears.relationships.A_EQUAL, gears.relationships.A_DISTANT))
        myrelationship.role = gears.relationships.R_ADVERSARY
        myrelationship.history.append(gears.relationships.Memory(
            "you told Jjang Bogo that I was working for Aegis",
            "I got you thrown out of the Treasure Hunters Guild for spying",
            -10, (gears.relationships.MEM_Clash, gears.relationships.MEM_Ideological)
        ))
        camp.egg.dramatis_personae.add(mynpc)
        camp.freeze(mynpc)


class SolarNavyJoinerPlot(Plot):
    LABEL = "ROPP_SOLAR_NAVY_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "Admiral Charla is recruiting cavaliers for the Pirate Point operation",
        offer_msg="The Solar Navy's goal is to remove the Aegis Consulate from Pirate's Point. Should be a lot of good missions in it for you. If you want the job, you can speak to her at the Field HQ.",
        offer_subject="Admiral Charla is recruiting cavaliers",
        offer_subject_data="the Pirate Point operation",
        memo="Admiral Charla is recruiting cavaliers for the Pirate Point operation. You should speak to her if you want to aid the Solar Navy.",
        prohibited_npcs=("NPC_CHARLA",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000018']

        self.signing_bonus = gears.selector.calc_mission_reward(self.rank+10, 500)
        self.got_starter_kit = False
        self.did_cutscene = False
        return True

    def NPC_SCENE_ENTER(self, camp):
        if self.elements["WORLD_MAP_WAR"].player_team:
            self.did_cutscene = True
        elif not self.did_cutscene:
            charla = self.elements["NPC_CHARLA"]
            pinsent = self.elements["NPC_PINSENT"]
            britaine = self.elements["NPC_BRITAINE"]
            pbge.alert("You enter the mobile HQ as the leaders of the three divisions of Terran service- the Solar Navy, the Defense Force, and the Guardians- debate the objectives of this operation.")
            ghcutscene.SimpleMonologueDisplay("Following the Typhon incident, we cannot afford to let Aegis Overlord maintain any presence on Earth. Their consulate in Pirate's Point must be destroyed.", charla)(camp)
            ghcutscene.SimpleMonologueDisplay("As an added bonus, we can get rid of the pirates who've been infesting this area. Two birds with one stone if you ask me.", britaine)(camp, False)
            ghcutscene.SimpleMonologueDisplay("I agree with you that Aegis needs to go, but invading a soverign city-state is going to cause more problems long-term. If you strike carelessly at every percieved threat, all you end up doing is making more enemies.", pinsent)(camp, False)
            ghcutscene.SimpleMonologueDisplay("You are thinking like a turtle, Pinsent, whereas I think like a hawk. The enemy must be defeated now before they become a threat again. Your defensive strategy didn't save us from Typhon, did it?", charla)(camp, False)
            ghcutscene.SimpleMonologueDisplay("No, and I live with the consequences of that every day... You are the one in charge of this operation and I will follow your lead. But I will not be silent when I think you're making a mistake.", pinsent)(camp, False)
            ghcutscene.SimpleMonologueDisplay("Ha-haw! Personally, I can't wait to get into battle!", britaine)(camp, False)
            pbge.alert("The three leaders stop talking when they notice that you have entered the vehicle.")
            self.did_cutscene = True

    def NPC_PINSENT_offers(self, camp):
        mylist = list()
        if self.elements["WORLD_MAP_WAR"].player_team is gears.factions.TheSolarNavy:
            mylist.append(
                Offer(
                    "We are here to get rid of the Aegis Consulate, but the rulers of Pirate's Point aren't going to be happy about us barging in, so we'll probably have to fight them as well.",
                    context=ContextTag(["INFO"]),
                    data={'subject': 'fighting the war'},
                    subject='',
                    no_repeats=True,))

            mylist.append(
                Offer(
                    "Your job will be to capture territories one at a time. You can only attack from a territory we already control. Once a faction's home base has been captured, that faction will be eliminated. The Aegis Consulate is due south from here, along the coastline.",
                    context=ContextTag(["CUSTOM"]),
                    data={'reply': 'So how do we proceed?'},
                    subject='get rid of the Aegis Consulate',
                    subject_start=False,
                    no_repeats=True,))

            mylist.append(
                Offer(
                    "That thing I said about capturing a home base? It also applies to us. During the operation, you have to make sure that enemy troops don't get too close to the Solar Navy camp. If this base is captured, we'll have no choice but to abort the operation.",
                    context=ContextTag(["CUSTOMREPLY"]),
                    data={'reply': 'Is there anything else I need to know?'},
                    subject='The Aegis Consulate is due south from here',
                    subject_start=False,
                    no_repeats=True,
                    dead_end=True))
        else:
            mylist.append(Offer(
                "Admiral Charla is in command of this operation; you should direct all inquiries to her.",
                context=ContextTag([context.HELLO])
            ))

        return mylist


    def NPC_CHARLA_offers(self, camp):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team:
            mylist.append(Offer(
                "[THATS_GOOD] Here is a signing bonus of ${:,}; you can use it to get some equipment from the supply depot. General Pinsent can fill you in on how the ground operations are proceeding.".format(self.signing_bonus),
                ContextTag([context.CUSTOM]), effect=self._join_team,
                data={"reply": "I want to help the Solar Navy."}
            ))

            mylist.append(Offer(
                "All cavaliers ready to defend the Earth are welcome on our team. Here is a signing bonus of ${:,}; you can use it to get some equipment from the supply depot. General Pinsent can fill you in on how the ground operations are proceeding.".format(self.signing_bonus),
                ContextTag([context.UNFAVORABLE_CUSTOM]), effect=self._unfav_join_team,
                data={"reply": "I want to help the Solar Navy."}
            ))
        elif self.elements["WORLD_MAP_WAR"].player_team is not gears.factions.TheSolarNavy and camp.campdata[ROPPCD_DEFECTION] == 0 and self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.TheSolarNavy):
            mylist.append(Offer(
                "[ARE_YOU_SURE_YOU_WANT_TO] Once you switch alleigance to the Solar Navy, you will not be able to change sides again.",
                ContextTag([context.UNFAVORABLE_CUSTOM]), 
                data={"reply": "I want to defect to the Solar Navy."}, subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[ARE_YOU_SURE_YOU_WANT_TO] Once you switch alleigance to the Solar Navy, you will not be able to change sides again.",
                ContextTag([context.CUSTOM]), 
                data={"reply": "I want to defect to the Solar Navy."}, subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "Very well... welcome to the Solar Navy.",
                ContextTag([context.CUSTOMREPLY]), effect=self._defect_to_team,
                data={"reply": "Yes, I have made my decision."}, subject=self,
            ))

            mylist.append(Offer(
                "A wise choice. [GOODBYE]",
                ContextTag([context.CUSTOMREPLY]),
                data={"reply": "I need to think about this some more."}, subject=self,
            ))

        return mylist

    def _defect_to_team(self, camp):
        original_team = self.elements["WORLD_MAP_WAR"].player_team
        if original_team and camp.are_faction_enemies(original_team, gears.factions.TheSolarNavy):
            camp.pc.add_badge(gears.meritbadges.BADGE_TURNCOAT)
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TheSolarNavy)
        camp.egg.faction_scores[gears.factions.TheSolarNavy] = max(0, camp.egg.faction_scores[gears.factions.TheSolarNavy])
        self.RUMOR = None
        self.memo = None
        camp.campdata[ROPPCD_DEFECTION] = 1
        
    def _unfav_join_team(self, camp):
        camp.campdata[ROPPCD_DEFECTION] = 1
        camp.egg.faction_scores[gears.factions.TheSolarNavy] = max(0, camp.egg.faction_scores[gears.factions.TheSolarNavy])
        self._join_team(camp)

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TheSolarNavy)
        self.RUMOR = None
        self.memo = None
        plotutility.CashRewardWithNotification(camp, self.signing_bonus)


class TreasureHuntersJoinerPlot(Plot):
    LABEL = "ROPP_TREASURE_HUNTERS_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "Jjang Bogo is offering big money for pilots to defend Pirate's Point",
        offer_msg="The Solar Navy has finally decided to get rid of our town. If we don't fight back, it'll be game over for Pirate's Point. You can talk to the grandmaster at [NPC_SCENE] to find out more.",
        offer_subject="Jjang Bogo is offering big money",
        offer_subject_data="defending Pirate's Point",
        memo="The grandmaster of the Treasure Hunter's Guild, Jjang Bogo, is offering lots of money for pilots to defend Pirate's Point from the Solar Navy.",
        prohibited_npcs=("NPC_BOGO",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002C']
        self.elements["NPC_MAYOR"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002E']

        self.signing_bonus = gears.selector.calc_mission_reward(self.rank+10, 500)
        self.did_cutscene = False
        return True

    def NPC_BOGO_offers(self, camp):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team:
            mylist.append(Offer(
                "[THATS_GOOD] I give you ${cash:,} to prepare for the upcoming battles. {NPC_MAYOR} can explain what you need to do.".format(cash=self.signing_bonus, **self.elements),
                ContextTag([context.CUSTOM]), effect=self._join_team,
                data={"reply": "I want to help defend Pirate's Point."}
            ))

            mylist.append(Offer(
                "Bwa ha ha! Welcome to the thieves guild, [audience]! Can't be too picky about who's on our side and who isn't at the moment. Here's ${cash:,} to prepare for the upcoming battles; {NPC_MAYOR} can explain what you need to do.".format(cash=self.signing_bonus, **self.elements),
                ContextTag([context.UNFAVORABLE_CUSTOM]), effect=self._unfav_join_team,
                data={"reply": "I want to help defend Pirate's Point."}
            ))
        elif self.elements["WORLD_MAP_WAR"].player_team is not gears.factions.TreasureHunters and camp.campdata[ROPPCD_DEFECTION] == 0 and self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.TreasureHunters):
            mylist.append(Offer(
                "[ARE_YOU_SURE_YOU_WANT_TO] I mean, I have no trouble accepting disloyal self-serving cutthroats into our ranks, but joining our team will leave a mark on your permanent record.",
                ContextTag([context.UNFAVORABLE_CUSTOM]), 
                data={"reply": "I want to join the Treasure Huters Guild."}, subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[ARE_YOU_SURE_YOU_WANT_TO] I mean, I have no trouble accepting disloyal self-serving cutthroats into our ranks, but joining our team will leave a mark on your permanent record.",
                ContextTag([context.CUSTOM]), 
                data={"reply": "I want to join the Treasure Huters Guild."}, subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "Bwa ha ha! Welcome aboard, then. Now get out there and fight for the glory of Pirate's Point!",
                ContextTag([context.CUSTOMREPLY]), effect=self._defect_to_team,
                data={"reply": "Yes, I have made my decision."}, subject=self,
            ))

            mylist.append(Offer(
                "Suit yourself. [GOODBYE]",
                ContextTag([context.CUSTOMREPLY]),
                data={"reply": "Maybe I don't want to change sides."}, subject=self,
            ))

        return mylist

    def NPC_MAYOR_offers(self, camp):
        mylist = list()
        if self.elements["WORLD_MAP_WAR"].player_team is gears.factions.TreasureHunters:
            mylist.append(
                Offer(
                    "We need to move reinforcements into all the districts of the city, and reclaim areas that have been captured by the enemy. You can only direct troops from a district we already control. The battle to claim a district will be more strenuous than a regular mission, so prepare for a long fight.",
                    context=ContextTag(["CUSTOM"]),
                    data={'reply': 'What am I supposed to do about this war?'},
                    subject=self, subject_start=True,
                    no_repeats=True,))

            mylist.append(
                Offer(
                    "When you capture an enemy's home base they will be elminated from the war. This also applies to us, so make sure our opponents don't get close to uptown! The Solar Navy base is near the mountain pass to the northeast. Good luck.",
                    context=ContextTag(["CUSTOMREPLY"]),
                    data={'reply': 'And how do we end this?'},
                    subject=self,
                    subject_start=False,
                    no_repeats=True,
                    dead_end=True))

        return mylist


    def _defect_to_team(self, camp: gears.GearHeadCampaign):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TreasureHunters)
        camp.egg.faction_scores[gears.factions.TreasureHunters] = max(0, camp.egg.faction_scores[gears.factions.TreasureHunters])
        self.RUMOR = None
        self.memo = None
        camp.pc.add_badge(gears.meritbadges.BADGE_CRIMINAL)
        camp.pc.remove_badges_with_tag(gears.tags.Police)
        camp.campdata[ROPPCD_DEFECTION] = 1

    def NPC_SCENE_ENTER(self, camp):
        if self.elements["WORLD_MAP_WAR"].player_team:
            self.did_cutscene = True
        elif not self.did_cutscene:
            bogo = self.elements["NPC_BOGO"]
            mayor = self.elements["NPC_MAYOR"]
            pbge.alert("As you enter the hall, a heated discussion is going on between the rulers of Pirate's Point.")
            ghcutscene.SimpleMonologueDisplay("On this world, the Lunars are outlaws just like the rest of us. We will defend them, and they us, in accordance with the pact.", bogo)(camp)
            ghcutscene.SimpleMonologueDisplay("The Blades of Crihna are not going to be happy about this...", mayor)(camp, False)
            ghcutscene.SimpleMonologueDisplay("I'm not happy about it either, but it is what it is. Aegis cannot be trusted; if there's a way for them to sieze control from us, they will.", bogo)(camp, False)
            ghcutscene.SimpleMonologueDisplay("For now, at least, we need each other. The Guild lacks the power to defeat the Solar Navy in a conventional battle. Aegis has pilots and mecha but they lack the support of the people.", bogo)(camp, False)
            ghcutscene.SimpleMonologueDisplay("So we fight side by side. If the situation changes, we may choose to make different alliances.", bogo)(camp, False)
            self.did_cutscene = True

    def _unfav_join_team(self, camp):
        camp.campdata[ROPPCD_DEFECTION] = 1
        camp.egg.faction_scores[gears.factions.TreasureHunters] = max(0, camp.egg.faction_scores[gears.factions.TreasureHunters])
        self._join_team(camp)

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TreasureHunters)
        self.RUMOR = None
        self.memo = None
        camp.credits += self.signing_bonus
        pbge.BasicNotification("You receive ${:,}.".format(self.signing_bonus))


class AegisJoinerPlot(Plot):
    LABEL = "ROPP_AEGIS_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "{NPC_AEGIS} is seeking a skilled pilot to defend the Lunar district from Terran invaders",
        offer_msg="The people of Terra are always fighting, but from what I hear the warlord threatening us now is more powerful than most. You should go to the Aegis Consulate and volunteer for service.",
        offer_subject="defend the Lunar district from Terran invaders",
        offer_subject_data="defending the Lunar district",
        memo="{NPC_AEGIS} is looking for a skilled pilot to defend the Lunar district of Pirate's Point from Terran invaders.",
        prohibited_npcs=("NPC_AEGIS",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000005'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002F']

        self.did_cutscene = False
        self.can_try_to_join = True
        return True

    def NPC_AEGIS_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team and self.can_try_to_join:
            if camp.pc.has_badge(gears.oldghloader.TYPHON_SLAYER.name):
                mylist.append(Offer(
                    "[HAGOODONE] I know exactly who you are, [audience]. You have a lot of nerve showing your face here. Unless you have official diplomatic business, I suggest you leave.",
                    ContextTag([context.CUSTOM]), effect=self._reject_pc,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))
            elif camp.pc.get_tags().intersection(gears.personality.MUTATIONS):
                mylist.append(Offer(
                    "I'm afraid the Aegis Expeditionary Force only accepts human pilots. Maybe the Solar Navy is desperate enough to hire a malformed deviant like you.",
                    ContextTag([context.CUSTOM]), effect=self._reject_pc,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))
            else:
                mylist.append(Offer(
                    "[THATS_GOOD] Aegis Overlord will overcome all opposition! I will give your team a set of advanced Lunar mecha; these should be far superior to anything you can purchase on Earth.",
                    ContextTag([context.CUSTOM]), effect=self._join_team,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))

        elif self.elements["WORLD_MAP_WAR"].player_team is not gears.factions.AegisOverlord and camp.campdata[ROPPCD_DEFECTION] == 0 and self.elements["WORLD_MAP_WAR"].faction_is_active(gears.factions.AegisOverlord):
            mylist.append(Offer(
                "Well Aegis Overlord does not need you. Run back to your pitiful earthbound comrades and await your inevitable death.",
                ContextTag([context.UNFAVORABLE_CUSTOM]), 
                data={"reply": "I want to join Aegis Overlord."}, subject=self, subject_start=True
            ))

        return mylist

    def _reject_pc(self, camp):
        self.can_try_to_join = False

    def NPC_SCENE_ENTER(self, camp):
        if self.elements["WORLD_MAP_WAR"].player_team:
            self.did_cutscene = True
        elif not self.did_cutscene:
            diplomat = self.elements["NPC_AEGIS"]
            pbge.alert("All is silent as you enter the Aegis Consulate. The staff in the front office are hard at work, completing their tasks with tireless efficiency.")
            pbge.alert("One diplomat, obviously a {NPC_AEGIS.gender.noun} of great authority, turns to face you. You feel like {NPC_AEGIS.gender.possessive_determiner} eyes are staring directly into your soul.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "Welcome to the Aegis Consulate. As you can see, we are quite busy at the moment. If you have no business here then I suggest you leave.",
                diplomat)(camp)
            self.did_cutscene = True

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.AegisOverlord)
        self.RUMOR = None
        self.memo = None
        camp.party.append(gears.selector.get_design_by_full_name("CHA-03 Command Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-02b Sniper Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-01 Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-01 Chameleon"))

        pbge.BasicNotification("You receive four Chameleon mecha.")


class RoppResolutionExtravaganza(Plot):
    # There are no separate "win" and "lose" endings because that is up to the player to decide.
    # Instead, the consequences of the war are determined by game state regardless of which side the player fought on.
    # Of course, the player has the ability to change things somewhat, depending on their actions...
    LABEL = "ROPP_RESOLUTION"
    scope = True
    active = True

    @override
    def custom_init(self, nart):
        # Create the meeting room.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))

        # Actually, there is a difference between whether the PC won or lost- the music!
        player_faction = self.elements["WORLD_MAP_WAR"].player_team
        self.elements["PLAYER_FACTION"] = player_faction
        if not self.elements.get("WINNER"):
            if self.elements.get(E_WAR_STATUS) == worldmapwar.WorldMapWar.WAR_WON:
                music = "yoitrax - Warrior.ogg"
                self.elements["WINNER"] = player_faction
            else:
                music = "Komiku_-_13_-_Nothing_will_grow_here.ogg"
                self.elements["WINNER"] = self.elements["WORLD_MAP_WAR"].pick_a_winner()
        else:
            music = "Mr Smith - Poor Mans Groove.ogg"

        myscene = gears.GearHeadScene(
            30, 30, "Aegis Consulate", player_team=team1, civilian_team=team2,
            scale=gears.scale.HumanScale,
            exploration_music=music
        )

        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.AegisArchitecture(),)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        _ = self.register_element("_room", pbge.randmaps.rooms.OpenRoom(20,10, decorate=gharchitecture.UlsaniteOfficeDecor()), dident="LOCALE")

        aegis_team = teams.Team(name="Aegis Team", allies=(team1,))
        aroom = self.register_element("_aegis_room", pbge.randmaps.rooms.Room(5,5, anchor=pbge.randmaps.anchors.west), dident="_room")
        aroom.contents.append(aegis_team)
        aegis_team.contents.append(self.elements["NPC_AEGIS"])
        for t in range(2):
            npc = self.seek_element(nart, "ANPC{}".format(t), self._is_aegis_character, must_find=False, lock=True)
            if npc:
                aegis_team.contents.append(npc)

        guild_team = teams.Team(name="Guild Team", allies=(team1, aegis_team))
        broom = self.register_element("_guild_room", pbge.randmaps.rooms.Room(5,5, anchor=pbge.randmaps.anchors.middle), dident="_room")
        broom.contents.append(guild_team)
        guild_team.contents.append(self.elements["NPC_BOGO"])
        for t in range(2):
            npc = self.seek_element(nart, "GNPC{}".format(t), self._is_guild_character, must_find=False, lock=True)
            if npc:
                guild_team.contents.append(npc)

        navy_team = teams.Team(name="Navy Team", allies=(team1, aegis_team, guild_team))
        croom = self.register_element("_navy_room", pbge.randmaps.rooms.Room(5,5, anchor=pbge.randmaps.anchors.east), dident="_room")
        croom.contents.append(navy_team)
        navy_team.contents.append(self.elements["NPC_CHARLA"])
        navy_team.contents.append(self.elements["NPC_BRITAINE"])
        navy_team.contents.append(self.elements["NPC_PINSENT"])

        _ = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(
                name="Exit",
                desc="Are you ready to leave Pirate's Point?",
                anchor=pbge.randmaps.anchors.south,
                plot_locked=True
            ), dident="_room"
        )

        if self.elements["WINNER"] is gears.factions.TheSolarNavy:
            if nart.camp.are_faction_allies(gears.factions.TheSolarNavy, gears.factions.TreasureHunters):
                self.add_sub_plot(nart, "ROPP_RESOLUTION_SOLARGUILD")
            else:
                self.add_sub_plot(nart, "ROPP_RESOLUTION_SOLARNAVY")
        elif self.elements["WINNER"] is gears.factions.TreasureHunters:
            if nart.camp.are_faction_allies(gears.factions.TheSolarNavy, gears.factions.TreasureHunters):
                self.add_sub_plot(nart, "ROPP_RESOLUTION_SOLARGUILD")
            elif nart.camp.are_faction_allies(gears.factions.AegisOverlord, gears.factions.TreasureHunters):
                self.add_sub_plot(nart, "ROPP_RESOLUTION_AEGISHUNTER")
            else:
                self.add_sub_plot(nart, "ROPP_RESOLUTION_TREASUREHUNTER")
        else:
            self.add_sub_plot(nart, "ROPP_RESOLUTION_AEGIS")

        # For the final scene, set all factions as allies so we can have a good chat.
        nart.camp.faction_relations[gears.factions.TheSolarNavy].set_pc_ally()
        nart.camp.faction_relations[gears.factions.TerranDefenseForce].set_pc_ally()
        nart.camp.faction_relations[gears.factions.Guardians].set_pc_ally()
        nart.camp.faction_relations[gears.factions.AegisOverlord].set_pc_ally()
        nart.camp.faction_relations[gears.factions.TreasureHunters].set_pc_ally()
        nart.camp.faction_relations[gears.factions.BoneDevils].set_pc_ally()
        nart.camp.faction_relations[gears.factions.BladesOfCrihna].set_pc_ally()

        self.started_resolution = False

        return True

    def _is_aegis_character(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.faction is gears.factions.AegisOverlord)

    def _is_guild_character(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.faction in {gears.factions.TreasureHunters, gears.factions.BoneDevils, gears.factions.BladesOfCrihna})


    WIN_ALERT = (
        "You are victorious! With the battle over, {WINNER} moves swiftly to consolidate their hold on Pirate's Point.",
        "You have secured victory for {WINNER}! Reports come in from all across Pirate's Point; the war is over."
    )
    LOSE_ALERT = (
        "As the battle ends, you receive orders to fall back. The forces of {PLAYER_FACTION} withdraw from the city as {WINNER} siezes control.",
        "You are contacted by {PLAYER_FACTION} with bad news; their foothold in Pirate's Point has been broken by {WINNER}. You escape the city along with other retreating units.",
    )
    def t_UPDATE(self, camp: gears.GearHeadCampaign):
        if not self.started_resolution:
            if self.elements["PLAYER_FACTION"] is self.elements["WINNER"]:
                _ = pbge.alert(random.choice(self.WIN_ALERT).format(**self.elements))
            else:
                _ = pbge.alert(random.choice(self.LOSE_ALERT).format(**self.elements))

            _ = pbge.alert("A short time later, the leaders of all involved factions meet at the Aegis Consulate to negotiate the new conditions of peace.")
            camp.go(self.elements["ENTRANCE"])
            self.started_resolution = True

    def ENTRANCE_menu(self, camp, thingmenu):
        thingmenu.add_item("End this adventure", self._end_adventure)
        thingmenu.add_item("Stay here a while longer", None)

    def _end_adventure(self, camp):
        pbge.alert("The fate of Pirate's Point has been settled for now, but new conflicts loom on the horizon. When the time comes you must be ready to fight again.")
        camp.eject()


# Things that will change depending on the ending...
# - Who controls Pirate's Point? Fed, THG, Aegis, DZF
# - Aegis status on Earth
# - Treasure Hunters relationship with Federation: Status Quo, Enemies, Allies

EGGDAT_PIRATE_POINT_LEADER = "EGGDAT_PIRATE_POINT_LEADER"
EGGDAT_TREASURE_HUNTER_FED_ALLIANCE = "EGGDAT_TREASURE_HUNTER_FED_ALLIANCE"
ROPP_ENEMIES = "ENEMIES"
ROPP_ALLIES = "ALLIES"
EGGDAT_ROPP_WARNING_ISSUED = "EGGDAT_ROPP_WARNING_ISSUED"

class ROPPSolarNavyVictory(Plot):
    # Federation controls PP, Aegis no victory, Treasure Hunters enemies of Federation
    LABEL = "ROPP_RESOLUTION_SOLARNAVY"
    scope = True
    active = True

    did_intro = False

    @override
    def custom_init(self, nart):
        return True

    def LOCALE_ENTER(self, camp):
        if not self.did_intro:
            pbge.alert("{NPC_CHARLA} stands before the leaders and warriors who now fill this room.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("Pirate's Point is now under the direct control of the Terran Federation. Let it be known that the enemies of Earth will find no refuge on this world.", self.elements["NPC_CHARLA"])(camp, True)
            ghcutscene.SimpleMonologueDisplay("Typical greenzoner arrogance... you think that putting 'Terra' in the name means you speak for the entire planet.", self.elements["NPC_BOGO"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Silence, thief.", self.elements["NPC_BRITAINE"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Not yet, old foe. You have robbed me of my home but may yet discover that the prize you grabbed is a hornet's nest. The guild does not forget, and does not forgive easily.", self.elements["NPC_BOGO"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("As for Aegis, we concede that you have caused Luna a minor setback. But be warned, Admiral, that soon you will face far greater threats from much closer to home.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("I will keep that in mind. Everyone has had their say; this meeting is now ended.", self.elements["NPC_CHARLA"])(camp, False)
            camp.egg.data[EGGDAT_PIRATE_POINT_LEADER] = gears.factions.TerranFederation
            camp.egg.data[EGGDAT_ROPP_WARNING_ISSUED] = True
            camp.egg.data[EGGDAT_TREASURE_HUNTER_FED_ALLIANCE] = ROPP_ENEMIES
            self.did_intro = True

    def NPC_BOGO_offers(self, camp):
        mylist = list()

        if self.elements["PLAYER_FACTION"] is gears.factions.TheSolarNavy:
            pass

        return mylist

    def GNPC0_offers(self, camp):
        mylist = list()

        return mylist

    def GNPC1_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_AEGIS_offers(self, camp):
        mylist = list()

        return mylist

    def ANPC0_offers(self, camp):
        mylist = list()

        return mylist

    def ANPC1_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_CHARLA_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_PINSENT_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_BRITAINE_offers(self, camp):
        mylist = list()

        return mylist


class ROPPSolarGuildVictory(Plot):
    # The Solar Navy/Treasure Hunters Guild alliance won.
    # Guild controls PP, Aegis no victory, Treasure Hunters neutral with Federation
    LABEL = "ROPP_RESOLUTION_SOLARGUILD"
    scope = True
    active = True

    did_intro = False

    @override
    def custom_init(self, nart):
        return True

    def LOCALE_ENTER(self, camp):
        if not self.did_intro:
            if self.elements["WINNER"] is gears.factions.TheSolarNavy:
                pbge.alert("{NPC_CHARLA} stands before the leaders and warriors who now fill this room. At her side, {NPC_BOGO} smiles mischeviously.".format(**self.elements))
                ghcutscene.SimpleMonologueDisplay("Pirate's Point has been liberated from the machinations of Aegis Overlord. Let it be known that the enemies of Earth will find no refuge on this world.", self.elements["NPC_CHARLA"])(camp, True)
                ghcutscene.SimpleMonologueDisplay("You really have no-one to blame but yourself, {NPC_AEGIS}. Or should I say the Overlord Council will have no-one to blame but you?".format(**self.elements), self.elements["NPC_BOGO"])(camp, False)
            else:
                pbge.alert("{NPC_BOGO} enters the room beaming like an arena champion. {NPC_CHARLA} takes her place beside him, as stoic and steely eyed as ever.".format(**self.elements))
                ghcutscene.SimpleMonologueDisplay("The war is over. You, {NPC_AEGIS}, have lost. I want all of your Aegis lackeys out of my city by tomorrow.", self.elements["NPC_BOGO"])(camp, True)
                ghcutscene.SimpleMonologueDisplay("The Terran Federation welcomes our new truce with Pirate's Point. It is in all of our best interests to keep Earth free from Lunar aggression.", self.elements["NPC_CHARLA"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("We will withdraw for now. But be warned, Terrans, that soon you will face far greater threats from much closer to home. When that time comes you will beg Aegis to protect you.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("With all due respect, you can take your empty threats and stuff them, Ambassador.", self.elements["NPC_PINSENT"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("That's enough fighting; is anyone else hungry? Tonight, we feast on Vesuvian honey and {NPC_AEGIS}'s secret liquor stash. Tomorrow will bring what it brings.".format(**self.elements), self.elements["NPC_BOGO"])(camp, False)
            camp.egg.data[EGGDAT_PIRATE_POINT_LEADER] = gears.factions.TreasureHunters
            camp.egg.data[EGGDAT_ROPP_WARNING_ISSUED] = True
            camp.egg.data[EGGDAT_TREASURE_HUNTER_FED_ALLIANCE] = ROPP_ALLIES
            self.did_intro = True


class ROPPTreasureHuntersVictory(Plot):
    # Guild controls PP, Aegis no victory, Relationships remain at status quo
    LABEL = "ROPP_RESOLUTION_TREASUREHUNTER"
    scope = True
    active = True

    did_intro = False

    @override
    def custom_init(self, nart):
        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.did_intro:
            pbge.alert("{NPC_BOGO} strides into the meeting hall as if he owns the place... which, technically, he now does.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("Pirate's Point remains as it has been, as it should be, a den of thieves and cutthroats. I expect both the Solar Navy and Aegis Overlord to withdraw from our city within 24 hours.", self.elements["NPC_BOGO"])(camp, True)
            ghcutscene.SimpleMonologueDisplay("With Aegis gone, the Solar Navy has no further business in this area. We will be out of your way as soon as possible.", self.elements["NPC_CHARLA"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("This was a convenient base of operations, but Terra is vast and Aegis will have no trouble establishing a new outpost.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Am I the only one who's not thrilled about this outcome?! We lost, these pirates are still going to be doing all kinds of illegal drokk down here...", self.elements["NPC_BRITAINE"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Britaine, old foe, you must know by now that you can't defeat us with brute force. For every bandit you catch two more will rise to oppose your suffocating laws.", self.elements["NPC_BOGO"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("But I've had enough of fighting. Tonight, we dine on Vesuvian honey and {NPC_AEGIS}'s secret liquor stash. Tomorrow will bring what it brings.".format(**self.elements), self.elements["NPC_BOGO"])(camp, False)
            camp.egg.data[EGGDAT_PIRATE_POINT_LEADER] = gears.factions.TreasureHunters
            self.did_intro = True

    def NPC_BOGO_offers(self, camp):
        mylist = list()

        return mylist

    def GNPC0_offers(self, camp):
        mylist = list()

        return mylist

    def GNPC1_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_AEGIS_offers(self, camp):
        mylist = list()

        return mylist

    def ANPC0_offers(self, camp):
        mylist = list()

        return mylist

    def ANPC1_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_CHARLA_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_PINSENT_offers(self, camp):
        mylist = list()

        return mylist

    def NPC_BRITAINE_offers(self, camp):
        mylist = list()

        return mylist


class ROPPAegisHuntersVictory(Plot):
    # Aegis controls PP, Aegis minor victory, Relationships remain at status quo
    LABEL = "ROPP_RESOLUTION_AEGISHUNTER"
    scope = True
    active = True

    did_intro = False

    @override
    def custom_init(self, nart):
        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.did_intro:
            _ = pbge.alert("The Aegis meeting hall buzzes with awkward silence. Despite the end of hostilities, all those attending remain on guard.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("I hope you're happy, Charla. For all the lives lost and money wasted your pet war has accomplished exactly nothing.", self.elements["NPC_BOGO"])(camp, True)
            ghcutscene.SimpleMonologueDisplay("...", self.elements["NPC_CHARLA"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("I think you are being too hard on the admiral, old man. Her foolish war has accomplished one thing- it has demonstrated that you are no longer fit to rule Pirate's Point.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("What are you saying?!", self.elements["NPC_BOGO"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("You failed to defend our spaceport from these Terran barbarians. From this point forward, Pirate's Point is under the protection of Aegis Overlord Luna. I advise you all to leave this place while you still can.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("We won't let you do this!".format(**self.elements), self.elements["NPC_PINSENT"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("General, we have already done it. Reinforcements from Luna are arriving as we speak. This city will be our bastion of civilization on the birthworld. If you had the power to stop us you already would have.", self.elements["NPC_AEGIS"])(camp, False)
            _ = pbge.alert("{NPC_AEGIS} sips {NPC_AEGIS.gender.possessive_determiner} drink and smiles. The rest of the hall stands in shocked silence.".format(**self.elements))
            camp.egg.data[EGGDAT_PIRATE_POINT_LEADER] = gears.factions.AegisOverlord
            camp.egg.data[gears.eggs.EGGDAT_AEGIS_VICTORIES_ON_EARTH] = camp.egg.data.get(gears.eggs.EGGDAT_AEGIS_VICTORIES_ON_EARTH, 0) + 1
            self.did_intro = True


class ROPPAegisVictory(Plot):
    # Aegis controls PP, Aegis major victory, Relationships remain at status quo
    LABEL = "ROPP_RESOLUTION_AEGIS"
    scope = True
    active = True

    did_intro = False

    @override
    def custom_init(self, nart):
        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.did_intro:
            _ = pbge.alert("The Aegis meeting hall is decorated as if for a festival, though few of those in attendance are in a festive mood. Ambassador {NPC_AEGIS} enters with the swagger of an aristocrat.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("Pirate's Point has been placed under the protection of Aegis Overlord. We generously offer you 24 hours to withdraw any surviving forces and personnel. After that, you will be hunted and killed as intruders on Lunar territory.", self.elements["NPC_AEGIS"])(camp, True)
            ghcutscene.SimpleMonologueDisplay("I wouldn't be so certain, you arrogant worm. The underworld has controlled this area since the Age of Superpowers. You may yet find that the prize you've won is a hornet's nest.", self.elements["NPC_BOGO"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Already dealt with. Your little club for lawbreakers? It has been thoroughly infiltrated by Aegis Intelligence. Our agents will begin phase two of the cleanup shortly.", self.elements["NPC_AEGIS"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("The Terran Federation will not allow this to stand. The enemies of Earth....", self.elements["NPC_CHARLA"])(camp, False)
            ghcutscene.SimpleMonologueDisplay("Admiral, please. What are you planning to do? Nuke another city? We both know that your hands are tied. Reinforcements from Luna are arriving as we speak.", self.elements["NPC_AEGIS"])(camp, False)
            _ = pbge.alert("The ambassador pauses; a wry grin crosses {NPC_AEGIS.gender.possessive_determiner} face.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("I would advise you all to forget about Pirate's Point. The Aegis Council asks for so little, this one small city. And soon you will have a far greater threat to face. One born of your world, not mine.", self.elements["NPC_AEGIS"])(camp, False)

            camp.egg.data[EGGDAT_PIRATE_POINT_LEADER] = gears.factions.AegisOverlord
            camp.egg.data[EGGDAT_ROPP_WARNING_ISSUED] = True
            camp.egg.data[gears.eggs.EGGDAT_AEGIS_VICTORIES_ON_EARTH] = camp.egg.data.get(gears.eggs.EGGDAT_AEGIS_VICTORIES_ON_EARTH, 0) + 2
            self.did_intro = True
