from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import game.content.gharchitecture
import pbge
import game.content.plotutility
from game.content import ghwaypoints
import game.content.ghterrain
from .dd_main import DZDRoadMapExit




class DZD_TheTownYouStartedIn(Plot):
    LABEL = "DZD_DISTANT_TOWN"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))
        myscene = gears.GearHeadScene(50, 50, self.elements["DZ_TOWN_NAME"], player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale, is_metro=True,
                                      faction=gears.factions.TerranFederation,
                                      attributes=(
                                      gears.personality.DeadZone, gears.tags.City, gears.tags.SCENE_PUBLIC))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, game.content.gharchitecture.HumanScaleGreenzone(),
                                                     road_terrain=game.content.ghterrain.Flagstone)

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

        team3 = teams.Team(name="Sheriff Team", allies=(team1,team2))
        myroom2.contents.append(team3)

        self.first_quest_done = False

        # Gonna store this town in the campdata, so it can be accessed elsewhere.
        nart.camp.campdata["DISTANT_TOWN"] = myscene
        nart.camp.campdata["DISTANT_TEAM"] = team3

        # Add the services.
        #tplot = self.add_sub_plot(nart, "DZDHB_AlliedArmor")
        #tplot = self.add_sub_plot(nart, "DZDHB_EliteEquipment")
        #tplot = self.add_sub_plot(nart, "DZDHB_BlueFortress")
        #tplot = self.add_sub_plot(nart, "DZDHB_BronzeHorseInn")
        #tplot = self.add_sub_plot(nart, "DZDHB_WujungHospital")
        #tplot = self.add_sub_plot(nart, "DZDHB_LongRoadLogistics")
        # Black Isle Pub
        # Wujung Tires - Conversion supplies
        # Hwang-Sa Mission
        # Reconstruction Site

        # Add the local tarot.
        #threat_card = nart.add_tarot_card(self, (game.content.ghplots.dd_tarot.MT_THREAT,), )
        #game.content.mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0], steps=3)

        return True

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
                pass
        else:
            pass

        return mylist