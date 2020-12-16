from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from game.content import backstory, plotutility, ghterrain, ghwaypoints, gharchitecture, ghrooms
import random
from gears import relationships
from game import content
from . import dd_main
from .dd_main import DZDRoadMapExit


class DZD_Conclusion(Plot):
    # This plot is the conclusion controller; it loads and activates the individual bits of the conclusion
    # as necessary.
    LABEL = "DZD_CONCLUSION"
    active = True
    scope = True

    def custom_init( self, nart ):
        # First off, we're gonna need a name for the town Cetus wrecks, aka THAT_TOWN
        self.elements["THAT_TOWN_NAME"] = gears.selector.DEADZONE_TOWN_NAMES.gen_word()

        # Add the doomed village subplot, just because we want to know the village name
        self.add_sub_plot(nart, "DZDC_DOOMED_VILLAGE", ident="VILLAGE")

        # Add the victory party subplot
        self.add_sub_plot(nart, "DZDC_VICTORY_PARTY", ident="PARTY")


        return True

    def PARTY_WIN(self, camp: gears.GearHeadCampaign):
        # We get the PARTY_WIN trigger when the PC is informed about the happenings in THAT_TOWN.
        self.subplots["VILLAGE"].activate(camp)

class VictoryParty(Plot):
    # Following the player's success in opening the road, there will be a victory party.
    # This party will be interrupted by the attack on DoomedTown.
    LABEL = "DZDC_VICTORY_PARTY"
    active = True
    scope = True

    def custom_init( self, nart ):
        dest = self.elements["TAVERN"]
        self.party_npcs = list()
        for t in range(8):
            npc = self.seek_element(nart, "NPC_{}".format(t), self._is_good_npc, scope=self.elements["METROSCENE"],
                                    must_find=False, lock=True)
            if npc:
                plotutility.CharacterMover(nart.camp, self, npc, dest, dest.civilian_team)
                self.party_npcs.append(npc)
            else:
                break

        self.prep_tavern = False

        return True

    def TAVERN_ENTER(self, camp: gears.GearHeadCampaign):
        self.prep_tavern = True

    def METROSCENE_ENTER(self, camp):
        if self.prep_tavern:
            pbge.alert("Alright, party's over.")
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
        self.add_sub_plot(nart, "DZDC_DoomVil_ENCOUNTER")

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","Mount {}", "{}", "{} Haven",
                          "Castle {}", "{} Village", "{} Spire")

    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def activate( self, camp ):
        super().activate(camp)
        self.final_edge.visible = True
        self.final_node.visible = True

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        pass


class CetusFight(Plot):
    # Each time Cetus moves to a new village, you have one chance to fight it.
    # In order to win the fight you must have at least one "advantage". Otherwise,
    # once it has taken enough damage, Cetus will simply release a death wave and fly away.
    # Also, if you lose the third fight, the TDF has had enough and will use their nukes.
    pass


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