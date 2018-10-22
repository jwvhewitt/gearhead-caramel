from pbge import Singleton
import color


class AegisOverlord(Singleton):
    name = "Aegis Overlord Luna"
    mecha_colors = (color.LunarGrey, color.AegisCrimson, color.LemonYellow, color.CeramicColor, color.LunarGrey)


class BladesOfCrihna(Singleton):
    name = "the Blades of Crihna"
    mecha_colors = (color.HeavyPurple, color.SeaGreen, color.PirateSunrise, color.Black, color.StarViolet)


class BoneDevils(Singleton):
    name = "the Bone Devil Gang"
    mecha_colors = (color.Black, color.Cream, color.BrightRed, color.Avocado, color.Terracotta)


class TerranDefenseForce(Singleton):
    name = "the Terran Defense Force"
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)


class Circle(object):
    def __init__(self, parent_faction=None, mecha_colors=None, name=""):
        self.name = name
        self.parent_faction = parent_faction
        if parent_faction and not mecha_colors:
            mecha_colors = parent_faction.mecha_colors
        self.mecha_colors = mecha_colors or color.random_mecha_colors()

    def __str__(self):
        return self.name
