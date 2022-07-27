# Contains calibre definitions for ammunition.
# Calibre has one major attribute- "bang"- which determines its mass, volume,
# and the number of bullets that must be expended by a given weapon.

from pbge import Singleton
from . import scale

RISK_INERT = -1
RISK_NORMAL = 0
RISK_VOLATILE = 1

class BaseCalibre( Singleton ):
    bang = 1
    scale = None
    risk = RISK_NORMAL


class Shells_20mm( BaseCalibre ):
    bang = 1
    scale = scale.MechaScale

class Shells_25mm( BaseCalibre ):
    bang = 2
    scale = scale.MechaScale


class Shells_30mm( BaseCalibre ):
    bang = 3
    scale = scale.MechaScale


class Shells_45mm( BaseCalibre ):
    bang = 4
    scale = scale.MechaScale


class Shells_60mm( BaseCalibre ):
    bang = 5
    scale = scale.MechaScale


class Shells_80mm( BaseCalibre ):
    bang = 6
    scale = scale.MechaScale


class Shells_100mm( BaseCalibre ):
    bang = 7
    scale = scale.MechaScale


class Shells_120mm( BaseCalibre ):
    bang = 8
    scale = scale.MechaScale


class Shells_150mm( BaseCalibre ):
    """The ammunition used by the BuruBuru's Shaka Cannon."""
    bang = 9
    scale = scale.MechaScale


class Caseless_45mm( BaseCalibre ):
    bang = 4
    scale = scale.MechaScale


class Caseless_165mm( BaseCalibre ):
    bang = 12
    scale = scale.MechaScale

class Ferrous_10mm( BaseCalibre ):
    bang = 1
    scale = scale.MechaScale
    risk = RISK_INERT

class Ferrous_25mm( BaseCalibre ):
    bang = 5
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_50mm( BaseCalibre ):
    bang = 7
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_70mm( BaseCalibre ):
    bang = 9
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_90mm( BaseCalibre ):
    bang = 12
    scale = scale.MechaScale
    risk = RISK_INERT


class Ferrous_120mm( BaseCalibre ):
    bang = 15
    scale = scale.MechaScale
    risk = RISK_INERT


class SelfPropelled_130mm( BaseCalibre ):
    bang = 12
    scale = scale.MechaScale
    risk = RISK_VOLATILE

class SelfPropelled_160mm( BaseCalibre ):
    bang = 15
    scale = scale.MechaScale
    risk = RISK_VOLATILE


class Ferrous_Frag( BaseCalibre ):
    bang = 8
    scale = scale.MechaScale
    risk = RISK_INERT


class Rifle_5mm(BaseCalibre):
    bang = 6
    scale = scale.HumanScale

class Rifle_6mm(BaseCalibre):
    bang = 9
    scale = scale.HumanScale


class Pistol_6mm(BaseCalibre):
    bang = 4
    scale = scale.HumanScale

class Cartridge_16mm(BaseCalibre):
    bang = 8
    scale = scale.HumanScale



