from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,GHNarrativeRequest,PLOT_LIST,mechtarot
from . import tarot_cards


#   **************************
#   ***   MECHA_WORKSHOP   ***
#   **************************

class SmallMechaFactory(Plot):
    LABEL = "MECHA_WORKSHOP"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        npc_name,garage_name = self.generate_npc_and_building_name()

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(50, 50, garage_name, player_team=team1, civilian_team=team2,
                                       attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_GARAGE, gears.tags.SCENE_SHOP),
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, gharchitecture.FactoryBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident="METROSCENE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(10,10,anchor=pbge.randmaps.anchors.south,),
                                    dident="LOCALE")

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        self.rank, name=npc_name, local_tags=self.elements["METROSCENE"].attributes,
                                        job=gears.jobs.ALL_JOBS["Mechanic"]
                                    ))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=self.elements["METROSCENE"].faction,
                                  ware_types=services.MECHA_PARTS_STORE, rank=self.rank)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("[HELLO]",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "custom built mecha parts"}
                            ))

        return mylist

    NAME_PATTERNS = ("{npc} Mecha Works", "{town} Mecha Works")
    def generate_npc_and_building_name(self):
        npc_name = gears.selector.EARTH_NAMES.gen_word()
        building_name = random.choice(self.NAME_PATTERNS).format(npc=npc_name,town=str(self.elements["METROSCENE"]))
        return npc_name,building_name


#   ***************************
#   ***   MEKWORK_PROBLEM   ***
#   ***************************


#   ***************************
#   ***   MEKWORK_FEATURE   ***
#   ***************************


#   ************************
#   ***   MEKWORK_MISC   ***
#   ************************



