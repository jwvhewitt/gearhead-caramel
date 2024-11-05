# Contains calibre definitions for ammunition.
# Calibre has one major attribute- "bang"- which determines its mass, volume,
# and the number of bullets that must be expended by a given weapon.

from pbge import Singleton
from . import scale, attackattributes

RISK_INERT = -1
RISK_NORMAL = 0
RISK_VOLATILE = 1


class AmmoModifier:
    def __init__(self, name, atts):
        self.name = name
        self.atts = atts


class BaseCalibre(Singleton):
    bang = 1
    scale = None
    risk = RISK_NORMAL
    modifiers = ()


class Shells_20mm(BaseCalibre):
    name = "20mm Shell"
    bang = 1
    scale = scale.MechaScale


class Shells_25mm(BaseCalibre):
    name = "25mm Shell"
    bang = 2
    scale = scale.MechaScale


class Shells_30mm(BaseCalibre):
    name = "30mm Shell"
    bang = 3
    scale = scale.MechaScale


class Shells_45mm(BaseCalibre):
    name = "45mm Shell"
    bang = 4
    scale = scale.MechaScale


class Shells_60mm(BaseCalibre):
    name = "60mm Shell"
    bang = 5
    scale = scale.MechaScale


class Shells_80mm(BaseCalibre):
    name = "80mm Shell"
    bang = 6
    scale = scale.MechaScale


class Shells_100mm(BaseCalibre):
    name = "100mm Shell"
    bang = 7
    scale = scale.MechaScale


class Shells_120mm(BaseCalibre):
    name = "120mm Shell"
    bang = 8
    scale = scale.MechaScale


class Shells_150mm(BaseCalibre):
    name = "150mm Shell"
    """The ammunition used by the BuruBuru's Shaka Cannon."""
    bang = 9
    scale = scale.MechaScale


class Caseless_45mm(BaseCalibre):
    name = "45mm Caseless"
    bang = 4
    scale = scale.MechaScale


class Caseless_165mm(BaseCalibre):
    name = "165mm Caseless"
    bang = 12
    scale = scale.MechaScale


class Ferrous_10mm(BaseCalibre):
    name = "10mm Ferrous"
    bang = 1
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_25mm(BaseCalibre):
    name = "25mm Ferrous"
    bang = 5
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_50mm(BaseCalibre):
    name = "50mm Ferrous"
    bang = 7
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_70mm(BaseCalibre):
    name = "70mm Ferrous"
    bang = 9
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_90mm(BaseCalibre):
    name = "90mm Ferrous"
    bang = 12
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_120mm(BaseCalibre):
    name = "120mm Ferrous"
    bang = 15
    scale = scale.MechaScale
    risk = RISK_INERT


class SelfPropelled_130mm(BaseCalibre):
    name = "130mm Self Propelled"
    bang = 12
    scale = scale.MechaScale
    risk = RISK_VOLATILE


class SelfPropelled_70cm(BaseCalibre):
    name = "70cm Self Propelled"
    bang = 16
    scale = scale.MechaScale
    risk = RISK_VOLATILE


class SelfPropelled_160mm(BaseCalibre):
    name = "160mm Self Propelled"
    bang = 15
    scale = scale.MechaScale
    risk = RISK_VOLATILE


class Ferrous_Frag(BaseCalibre):
    name = "Ferrous Frag"
    bang = 8
    scale = scale.MechaScale
    risk = RISK_INERT


#   ******************************
#   ***  HUMAN SCALE CALIBRES  ***
#   ******************************

class Rifle_5mm(BaseCalibre):
    name = "5mm Rifle"
    bang = 6
    scale = scale.HumanScale
    modifiers = (
        AmmoModifier("Flechette", (attackattributes.Scatter,)),
    )


class Rifle_6mm(BaseCalibre):
    name = "6mm Rifle"
    bang = 9
    scale = scale.HumanScale
    modifiers = (
        AmmoModifier("Flechette", (attackattributes.Scatter,)),
    )


class Rifle_20mm(BaseCalibre):
    name = "20mm Rifle"
    bang = 20
    scale = scale.HumanScale


class Snub_7mm(BaseCalibre):
    name = "7mm Snub"
    bang = 10
    scale = scale.HumanScale
    risk = RISK_INERT


class Snub_10mm(BaseCalibre):
    name = "10mm Snub"
    bang = 16
    scale = scale.HumanScale
    risk = RISK_INERT


class Pistol_4mm(BaseCalibre):
    name = "4mm Pistol"
    bang = 4
    scale = scale.HumanScale


class Pistol_6mm(BaseCalibre):
    name = "6mm Pistol"
    bang = 6
    scale = scale.HumanScale
    modifiers = (
        AmmoModifier("Flechette", (attackattributes.Scatter,)),
    )


class Pistol_12mm(BaseCalibre):
    name = "12mm Pistol"
    bang = 12
    scale = scale.HumanScale


class Cartridge_16mm(BaseCalibre):
    name = "16mm Cartridge"
    bang = 8
    scale = scale.HumanScale


class Cannister_25mm(BaseCalibre):
    name = "25mm Cannister"
    bang = 12
    scale = scale.HumanScale


Shell_25mm = Cannister_25mm