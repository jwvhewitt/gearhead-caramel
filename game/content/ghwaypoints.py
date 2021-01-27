
# A Waypoint is a special effect waiting on a tile. It is normally invisible,
# but can affect the terrain of the tile it is placed in. Walking onto the tile
# or bumping it will activate its effect.

import pbge
from . import ghterrain
from game.content.ghterrain import DZDTownTerrain, DZDWCommTowerTerrain, DZDCommTowerTerrain
from pbge.scenes.waypoints import Waypoint
from game import geareditor, fieldhq
from game import cyberdoc
import gears
import random


class VendingMachine( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.VendingMachineTerrain )
    desc = "You stand before a vending machine."


class Exit( Waypoint ):
    name = "Exit"
    TILE = pbge.scenes.Tile( None, ghterrain.ExitTerrain, None )
    def __init__( self, dest_scene=None, dest_entrance=None, **kwargs ):
        self.dest_scene = dest_scene
        self.dest_entrance = dest_entrance
        super(Exit,self).__init__(**kwargs)

    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        if self.dest_scene and self.dest_entrance:
            camp.destination = self.dest_scene
            camp.entrance = self.dest_entrance
        else:
            pbge.alert("This door doesn't seem to go anywhere.")

    def combat_use(self, camp, pc):
        rpm = self.MENU_CLASS(camp, self)
        rpm.desc = "Do you want to retreat?"
        rpm.add_item("Leave combat.", True)
        rpm.add_item("Keep fighting.", False)
        fx = rpm.query()
        if fx:
            camp.scene.contents.remove(pc)

    def combat_bump(self, camp, pc):
        # Send a BUMP trigger.
        camp.check_trigger("BUMP",self)
        # If plot_locked, check plots for possible actions.
        # Otherwise, use the normal unlocked_use.
        if self.plot_locked:
            rpm = self.MENU_CLASS( camp, self )
            camp.expand_puzzle_menu( self, rpm )
            fx = rpm.query()
            if fx:
                fx( camp )
        else:
            self.combat_use( camp, pc )


class Crate( Waypoint ):
    name = "Crate"
    TILE = pbge.scenes.Tile(None,None,ghterrain.OldCrateTerrain)
    desc = "You see a large plastic crate."
    DEFAULT_TREASURE_TYPE = (gears.tags.ST_TREASURE,)
    def __init__( self, treasure_rank=0, treasure_amount=100, treasure_type=DEFAULT_TREASURE_TYPE, **kwargs ):
        self.contents = pbge.container.ContainerList()
        if treasure_rank > 0:
            mytreasure = gears.selector.get_random_loot(treasure_rank, treasure_amount, treasure_type)
            self.contents += mytreasure
        super().__init__(**kwargs)

    def unlocked_use( self, camp: gears.GearHeadCampaign ):
        # Perform this waypoint's special action.
        fieldhq.backpack.ItemExchangeWidget.create_and_invoke(camp, camp.first_active_pc(), self.contents)


class DZDTown( Exit ):
    name = 'Town'
    TILE = pbge.scenes.Tile( None, DZDTownTerrain, None )
    desc = "You stand before a deadzone community."


class DZDWCommTower( Exit ):
    name = 'Comm Tower'
    TILE = pbge.scenes.Tile( None, DZDWCommTowerTerrain, None )
    desc = "You stand before a communications tower."


class DZDCommTower( Exit ):
    name = 'Comm Tower'
    TILE = pbge.scenes.Tile( None, DZDCommTowerTerrain, None )
    desc = "You stand before a communications tower."

class Victim(Waypoint):
    name = 'Victim'
    TILE = pbge.scenes.Tile(None,None,ghterrain.VictimTerrain)
    desc = "This person has seen better days."

class OldCrate(Crate):
    name = 'Crate'
    TILE = pbge.scenes.Tile(None,None,ghterrain.OldCrateTerrain)
    desc = "You see a large plastic crate."


class RetroComputer(Waypoint):
    name = 'Computer Terminal'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.RetroComputerTerrain)
    desc = "An obsolete but still functioning computer terminal."

class UlsaniteFilingCabinet(Waypoint):
    name = 'Filing Cabinet'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.UlsaniteFilingCabinetTerrain)
    desc = "A filing cabinet."

class ScrapIronDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.ScrapIronDoorTerrain)
    desc = "A door."

class GlassDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.GlassDoorTerrain)
    desc = "A door."

class ScreenDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.ScreenDoorTerrain)
    desc = "A door."

class WoodenDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.WoodenDoorTerrain)
    desc = "A door."

class DZDWConcreteBuilding( Exit ):
    name = 'Concrete Building'
    TILE = pbge.scenes.Tile( None, ghterrain.DZDWConcreteBuilding, None )
    desc = "You stand before a concrete building."


class DZDConcreteBuilding( Exit ):
    name = 'Concrete Building'
    TILE = pbge.scenes.Tile( None, ghterrain.DZDConcreteBuilding, None )
    desc = "You stand before a concrete building."

class MetalDoor( Waypoint ):
    name = "Door"
    TILE = pbge.scenes.Tile( None, ghterrain.MetalDoorClosed, None )
    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        if camp.scene.get_wall(*self.pos) is ghterrain.MetalDoorClosed:
            camp.scene.set_wall(self.pos[0],self.pos[1],ghterrain.MetalDoorOpen)
        elif camp.scene.get_wall(*self.pos) is ghterrain.MetalDoorOpen and not camp.scene.get_actors(self.pos):
            camp.scene.set_wall(self.pos[0],self.pos[1],ghterrain.MetalDoorClosed)

class AlliedArmorSignWP(Waypoint):
    name = "Allied Armor"
    TILE = pbge.scenes.Tile(None,None,ghterrain.AlliedArmorSign)
    ATTACH_TO_WALL = True

class StatueM(Waypoint):
    name = "Statue"
    TILE = pbge.scenes.Tile(None,None,ghterrain.StatueMTerrain)
    ATTACH_TO_WALL = True

class StatueF(Waypoint):
    name = "Statue"
    TILE = pbge.scenes.Tile(None,None,ghterrain.StatueFTerrain)
    ATTACH_TO_WALL = True

class GoldPlaque(Waypoint):
    name = "Plaque"
    TILE = pbge.scenes.Tile(None,None,ghterrain.GoldPlaqueTerrain)
    ATTACH_TO_WALL = True

class MechEngTerminal(Waypoint):
    name = "Mecha Engineering Terminal"
    TILE = pbge.scenes.Tile(None,None,ghterrain.MechEngTerminalTerrain)
    ATTACH_TO_WALL = True
    MENU_TITLE = pbge.frects.Frect(-100,-150,200,16)

    def _predraw(self):
        pbge.my_state.view()
        mydest = self.MENU_TITLE.get_rect()
        pbge.default_border.render(mydest)
        pbge.draw_text(pbge.MEDIUMFONT,"Choose mecha to edit",mydest,color=pbge.INFO_HILIGHT,justify=0)

    def _get_meng_name(self,mek):
        if hasattr(mek,"pilot") and mek.pilot:
            return "{} [{}]".format(mek.get_full_name(),str(mek.pilot))
        else:
            return mek.get_full_name()

    def unlocked_use( self, camp ):
        mek = True
        while mek:
            mymenu = pbge.rpgmenu.Menu(-175,-100,350,250,predraw=self._predraw,font=pbge.BIGFONT)
            for mek in camp.party:
                if isinstance(mek,gears.base.Mecha) and not hasattr(mek,"owner"):
                    mymenu.add_item(self._get_meng_name(mek),mek)
            mymenu.sort()
            mymenu.add_item("[EXIT]",None)
            mek = mymenu.query()
            if mek:
                myui = geareditor.GearEditor(mek,camp.party,mode=geareditor.MODE_RESTRICTED)
                myui.activate_and_run()

class CyberdocTerminal( Waypoint ):
    name = "Cyberdoc Terminal"
    TILE = pbge.scenes.Tile(None,None,ghterrain.CyberdocTerminalTerrain)
    ATTACH_TO_WALL = True
    MENU_TITLE = pbge.frects.Frect(-100,-150,200,16)

    def __init__(self, shop = None, **keywords):
        super().__init__(**keywords)
        self.shop = shop

    def _predraw(self):
        pbge.my_state.view()
        mydest = self.MENU_TITLE.get_rect()
        pbge.default_border.render(mydest)
        pbge.draw_text(pbge.MEDIUMFONT,"Choose character",mydest,color=pbge.INFO_HILIGHT,justify=0)

    def unlocked_use(self, camp):
        if not hasattr(self, 'shop'):
            self.shop = None
        char = True
        while char:
            mymenu = pbge.rpgmenu.Menu(-175,-100,350,250,predraw=self._predraw,font=pbge.BIGFONT)
            for char in camp.party:
                if isinstance(char, gears.base.Character):
                    mymenu.add_item(char.name, char)
            mymenu.sort()
            mymenu.add_item("[EXIT]", None)
            char = mymenu.query()
            if char:
                ui = cyberdoc.UI(char, camp, self.shop, camp.party, camp.year)
                ui.activate_and_run()


class MechaPoster(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.MechaPosterTerrain)
    ATTACH_TO_WALL = True

class VentFan(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.VentFanTerrain)
    ATTACH_TO_WALL = True

class BoardingChute(Waypoint):
    name = "Boarding Chute"
    TILE = pbge.scenes.Tile(None,None,ghterrain.GreenBoardingChuteTerrain)
    ATTACH_TO_WALL = True

class ClosedBoardingChute(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.RedBoardingChuteTerrain)
    ATTACH_TO_WALL = True

class SmokingWreckage(Waypoint):
    TILE = pbge.scenes.Tile(None,ghterrain.MSWreckage,ghterrain.Smoke)

class KojedoModel(Waypoint):
    name = "Kojedo Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.KojedoModelTerrain)

class BuruBuruModel(Waypoint):
    name = "Buru Buru Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.BuruBuruModelTerrain)

class GladiusModel(Waypoint):
    name = "Gladius Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.GladiusModelTerrain)

class VadelModel(Waypoint):
    name = "Vadel Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.VadelModelTerrain)

class HarpyModel(Waypoint):
    name = "Harpy Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.HarpyModelTerrain)

class ClaymoreModel(Waypoint):
    name = "Claymore Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.ClaymoreModelTerrain)

class MechaModel(Waypoint):
    name = "Mecha Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.MechaModelTerrain)

class WallMap(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.MapTerrain)
    ATTACH_TO_WALL = True

class EarthMap(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.EarthMapTerrain)
    ATTACH_TO_WALL = True

class Lockers(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.LockersTerrain)
    ATTACH_TO_WALL = True

class ShippingShelves(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.ShippingShelvesTerrain)
    ATTACH_TO_WALL = True

class RegExLogo(Waypoint):
    name = "RegEx Corporation Logo"
    TILE = pbge.scenes.Tile(None,None,ghterrain.RegExLogoTerrain)
    ATTACH_TO_WALL = True

class HamsterCage(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.HamsterCageTerrain)
    ATTACH_TO_WALL = True

class Bookshelf(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.UlsaniteBookshelfTerrain)
    ATTACH_TO_WALL = True

class StoneStairsUp(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.StoneStairsUpTerrain)

class StairsUp(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.StairsUpTerrain)

class StairsDown(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.StairsDownTerrain)

class Trapdoor(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.TrapdoorTerrain)

class TrailSign(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.TrailSignTerrain)

class DZDDefiledFactory(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.DZDDefiledFactoryTerrain)

class RecoveryBed(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.BedTerrain)
    recovery_entrance = True

class UndergroundEntrance(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.UndergroundEntranceTerrain)

class OldMainframe(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.OldMainframeTerrain)


class OldTerminal(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.OldTerminalTerrain)


class Biotank(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.BiotankTerrain)
    SPRITE_OFF = ((0,0),(-14,0),(-6,12),(6,9),(14,0),(6,-12),(-6,-12))

    def fill_tank(self):
        scene = self.scene
        if scene and scene.on_the_map(*self.pos):
            scene.set_decor(self.pos[0], self.pos[1], ghterrain.BiotankTerrain)

    def empty_tank(self):
        scene = self.scene
        if scene and scene.on_the_map(*self.pos):
            scene.set_decor(self.pos[0], self.pos[1], ghterrain.EmptyBiotankTerrain)

    def break_tank(self, process_anim=True):
        # If you're breaking a bunch of tanks at once, set process_anim to False and call handle_anim_sequence yerself.
        scene = self.scene
        if scene and scene.on_the_map(*self.pos):
            mypoints = random.sample(self.SPRITE_OFF,5)
            for t in range(5):
                pbge.my_state.view.anim_list.append(
                    gears.geffects.BigBoom(pos=self.pos, x_off=mypoints[t][0], y_off=mypoints[t][1],
                                           delay=t * 5))
            if process_anim:
                pbge.my_state.view.handle_anim_sequence()
            scene.set_decor(self.pos[0], self.pos[1], ghterrain.BrokenBiotankTerrain)


class EmptyBiotank(Biotank):
    TILE = pbge.scenes.Tile(None, None, ghterrain.EmptyBiotankTerrain)


class BrokenBiotank(Biotank):
    TILE = pbge.scenes.Tile(None, None, ghterrain.BrokenBiotankTerrain)

class OrganicTube(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.OrganicTubeTerrain)

class PZHolo(Waypoint):
    # A PreZero hologram interface
    TILE = pbge.scenes.Tile(None, None, ghterrain.PZHoloTerrain)

class AngelEgg(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.AngelEggTerrain)
