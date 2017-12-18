from pbge.plots import Plot, Chapter
import waypoints
import ghterrain
import gears
import pbge
from .. import teams

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
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Mauna",player_team=team1,scale=gears.scale.HumanScale)

        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.WinterMochaSnowdrift)
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

        myscenegen.contents.append(myroom)

        myroom2 = pbge.randmaps.rooms.FuzzyRoom(10,10)
        myroom2.contents.append( waypoints.WinterMochaToolbox() )
        myroom2.contents.append( ghterrain.WinterMochaDomeTerrain )
        myroom2.contents.append( ghterrain.WinterMochaBrokenShovel )
        myroom2.contents.append( ghterrain.WinterMochaGeothermalGeneratorTerrain )

        myscenegen.contents.append(myroom2)


        return True

