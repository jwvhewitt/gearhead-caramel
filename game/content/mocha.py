from pbge.plots import Plot, Chapter
import waypoints
import ghterrain
import gears
import pbge
from .. import teams,ghdialogue
from pbge.scenes.movement import Walking, Flying, Vision
from gears.geffects import Skimming, Rolling



# ********************************
# ***   TERRAIN  DEFINITIONS   ***
# ********************************

class WinterMochaSnowdrift( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_wintermocha_snowdrift.png'
    bordername = ''
    blocks = (Walking,Skimming,Rolling)

class WinterMochaHangarTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_hangar.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class WinterMochaHangar(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaHangarTerrain
    TERRAIN_MAP = (
        (0,1),
        (2,3,4),
        (5,6,7,8),
        (9,10,11,12,13,14),
        (15,16,17,18,19,20),
        (21,22,23,24,25,26),
        (None,27,28,29,30,31),
        (None,None,32,33,34,35),
        (None,None,36,37,38,39),
        (None,None,WinterMochaSnowdrift,WinterMochaSnowdrift,WinterMochaSnowdrift)
    )
    WAYPOINT_POS = {
        "DOOR": (3,8)
    }

class WinterMochaFenceTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_fence.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class WinterMochaFence(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaFenceTerrain
    TERRAIN_MAP = (
        (0,),
        (1,),
        (2,),
    )
    WAYPOINT_POS = {
        "DOOR": (0,1)
    }



# *****************
# ***   PLOTS   ***
# *****************

class MochaStub( Plot ):
    LABEL = "SCENARIO_MOCHA"
    # Creates a Winter Mocha adventure.
    # - Play starts in Mauna, near Vikki and Hyolee.
    #   - The good mecha are snowed into the hangar.
    #   - The bad mecha are in the parking lot.
    # - Head out to battle some raiders.
    # - Win or lose, the end.

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        w = nart.camp
        self.register_element( "WORLD", w )
        self.chapter = Chapter( world=w )
        self.add_first_locale_sub_plot( nart, locale_type="MOCHA_MAUNA" )


        return True

class FrozenHotSpringCity( Plot ):
    # Mauna in winter. There was a heavy snowfall last night, and the mecha
    # hangar is blocked.
    LABEL = "MOCHA_MAUNA"
    active = True
    scope = True
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60,60,"Mauna",player_team=team1,scale=gears.scale.HumanScale)

        myfilter = pbge.randmaps.converter.BasicConverter(WinterMochaSnowdrift)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.SmallSnow,myfilter,mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)


        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = pbge.randmaps.rooms.FuzzyRoom(10,10)

        myent = self.register_element( "ENTRANCE", waypoints.WinterMochaBarrel(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append( myent )

        vikki = gears.base.Character(name="Vikki",statline={gears.stats.Reflexes:15,
         gears.stats.Body:10,gears.stats.Speed:13,gears.stats.Perception:13,
         gears.stats.Knowledge:10,gears.stats.Craft:10,gears.stats.Ego:10,
         gears.stats.Charm:12,gears.stats.MechaPiloting:7,gears.stats.MechaGunnery:7,
         gears.stats.MechaFighting:7})
        vikki.imagename = 'cha_wm_vikki.png'
        vikki.portrait = 'por_f_wintervikki.png'
        vikki.colors = (gears.color.ShiningWhite,gears.color.LightSkin,gears.color.NobleGold,gears.color.HunterOrange,gears.color.Olive)
        vikki.mmode = pbge.scenes.movement.Walking
        myroom.contents.append(vikki)
        self.register_element( "VIKKI", vikki )

        myscenegen.contents.append(myroom)

        myroom2 = pbge.randmaps.rooms.FuzzyRoom(15,15)
        myroom3 = WinterMochaHangar(parent=myroom2,waypoints={"DOOR":waypoints.VendingMachine()})
        myscenegen.contents.append(myroom2)

        myroom4 = pbge.randmaps.rooms.FuzzyRoom(6,5,anchor=pbge.randmaps.anchors.northwest,parent=myscenegen)
        myroom5 = WinterMochaFence(parent=myroom4,anchor=pbge.randmaps.anchors.west)


        return True

    def VIKKI_offers(self,camp):
        # Return list of dialogue offers.
        mylist = list()
        mylist.append( pbge.dialogue.Offer('[HELLO]',context=pbge.dialogue.ContextTag((ghdialogue.context.HELLO,))))
        return mylist


