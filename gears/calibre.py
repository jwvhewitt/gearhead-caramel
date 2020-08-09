# Contains calibre definitions for ammunition.
# Calibre has one major attribute- "bang"- which determines its mass, volume,
# and the number of bullets that must be expended by a given weapon.

from pbge import Singleton
from . import scale

class BaseCalibre( Singleton ):
    bang = 1
    scale = None

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

class Ferrous_25mm( BaseCalibre ):
    bang = 5
    scale = scale.MechaScale

class Ferrous_50mm( BaseCalibre ):
    bang = 7
    scale = scale.MechaScale

class Ferrous_70mm( BaseCalibre ):
    bang = 9
    scale = scale.MechaScale

class Ferrous_90mm( BaseCalibre ):
    bang = 12
    scale = scale.MechaScale

class Ferrous_120mm( BaseCalibre ):
    bang = 15
    scale = scale.MechaScale

class SelfPropelled_130mm( BaseCalibre ):
    bang = 12
    scale = scale.MechaScale

class Ferrous_Frag( BaseCalibre ):
    bang = 8
    scale = scale.MechaScale

class Rifle_5mm(BaseCalibre):
    bang = 6
    scale = scale.HumanScale

class Pistol_6mm(BaseCalibre):
    bang = 4
    scale = scale.HumanScale
