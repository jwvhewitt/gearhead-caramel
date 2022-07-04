from pbge.plots import Plot, PlotState, Adventure
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from .dd_main import DZDRoadMapExit
from game.content import backstory, plotutility, ghterrain, gharchitecture
import random
from game import content




class DZD_TheTownYouStartedIn(Plot):
    LABEL = "DZD_DISTANT_TOWN"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))
        town_fac = self.register_element( "METRO_FACTION",
            gears.factions.Circle(nart.camp,parent_faction=gears.factions.DeadzoneFederation,name="the {} Council".format(self.elements["DZ_TOWN_NAME"]))
        )
        myscene = gears.GearHeadScene(50, 50, self.elements["DZ_TOWN_NAME"], player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=town_fac,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.City, gears.tags.SCENE_PUBLIC,
                                      "DISTANT_TOWN"))
        myscene.exploration_music = 'Good Night.ogg'

        self.register_element("CITY_COLORS", gears.color.random_building_colors())

        for t in range(random.randint(1,3)):
            npc = gears.selector.random_character(50, local_tags=myscene.attributes)
            npc.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, gharchitecture.HumanScaleGreenzone(),
                                                     road_terrain=ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        self.register_element("METRO", myscene.metrodat)

        myroom2 = self.register_element("_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.east),
                                        dident="LOCALE")
        towngate = self.register_element("ENTRANCE", DZDRoadMapExit(roadmap=self.elements["DZ_ROADMAP"],
                                                                    node=self.elements["DZ_NODE"],name="The Highway",
                                                                    desc="The highway stretches far beyond the horizon, all the way back to the green zone.",
                                                                    anchor=pbge.randmaps.anchors.east,
                                                                    plot_locked=True), dident="_ROOM2")
        # Gonna register the entrance under another name for the subplots.
        self.register_element("MISSION_GATE", towngate)
        self.register_element("METROSCENE", myscene)

        mystory = self.register_element("BACKSTORY",backstory.Backstory(commands=("DZTOWN_FOUNDING",),elements={"LOCALE":self.elements["LOCALE"]}))

        team3 = teams.Team(name="Sheriff Team", allies=(team1,team2))
        myroom2.contents.append(team3)

        self.first_quest_done = False

        # Gonna store this town in the campdata, so it can be accessed elsewhere.
        nart.camp.campdata["DISTANT_TOWN"] = myscene
        nart.camp.campdata["DISTANT_TEAM"] = team3

        # Add the services.
        tplot = self.add_sub_plot(nart, "DZRS_ORDER")
        tplot = self.add_sub_plot(nart, "DZRS_GARAGE")
        tplot = self.add_sub_plot(nart, "DZRS_HOSPITAL")
        tplot = self.add_sub_plot(nart, "SHOP_TAVERN", elements={"LOCALE": myscene})

        # Record the tavern scene
        self.elements["TAVERN"] = tplot.elements["INTERIOR"]

        # Add the local tarot.
        #threat_card = nart.add_tarot_card(self, (game.content.ghplots.dd_tarot.MT_THREAT,), )
        #game.content.mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0], steps=3)

        # Add the features
        self.add_sub_plot(nart, "CF_METROSCENE_RECOVERY_HANDLER")
        self.add_sub_plot(nart, "CF_METROSCENE_WME_DEFENSE_HANDLER")
        self.add_sub_plot(nart, "CF_METROSCENE_RANDOM_PLOT_HANDLER", elements={"USE_PLOT_RANK": True})

        return True

    def _finish_first_quest(self,camp):
        pstate = PlotState(adv=Adventure("Conclusion")).based_on(self)
        content.load_dynamic_plot(camp, "DZD_CONCLUSION", pstate)
        self.first_quest_done = True

    def DZ_CONTACT_offers(self,camp):
        mylist = list()

        if not self.first_quest_done:
            mylist.append(
                Offer(
                    "[HELLO] Have you found a solution for our powerplant problem yet?", context=(context.HELLO,),
                )
            )
            if not camp.campdata.get("CONSTRUCTION_ARRANGED"):
                mylist.append(
                    Offer(
                        "You were supposed to go to Wujung, find someone who can fix our powerplant, and bring them back here.",
                        context=(context.CUSTOM,), data={"reply":"[I_FORGOT]"}
                    )
                )
            elif not self.elements["DZ_ROADMAP"].connection_is_made():
                mylist.append(
                    Offer(
                        "Those greenzoners won't move until a secure trade route is opened between here and Wujung.",
                        context=(context.CUSTOM,), data={"reply":"[STILL_WORKING_ON_IT]"}
                    )
                )
            else:
                mylist.append(
                    Offer(
                        "That's great to hear! [THANKS_FOR_HELP] There's going to be a party at {TAVERN} later on to celebrate; why don't you come along?".format(**self.elements),
                        context=(context.CUSTOM,), data={"reply":"The repair crew is on the way."}, effect=self._finish_first_quest
                    )
                )

            if pbge.util.config.getboolean( "GENERAL", "dev_mode_on"):
                mylist.append(
                    Offer(
                        "Good enough. Come to the victory party and we'll see about starting the next bit.",
                        context=(context.CUSTOM,), data={"reply": "For debugging purposes, let's just pretend it's done."},
                        effect=self._finish_first_quest
                    )
                )

        return mylist