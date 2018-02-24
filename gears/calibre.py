# Contains calibre definitions for ammunition.
# Calibre has one major attribute- "bang"- which determines its mass, volume,
# and the number of bullets that must be expended by a given weapon.

from pbge import Singleton

class BaseCalibre( Singleton ):
    bang = 1

class Shells_20mm( BaseCalibre ):
    bang = 1

class Shells_25mm( BaseCalibre ):
    bang = 2

class Shells_30mm( BaseCalibre ):
    bang = 3

class Shells_45mm( BaseCalibre ):
    bang = 4

class Shells_60mm( BaseCalibre ):
    bang = 5

class Shells_80mm( BaseCalibre ):
    bang = 6

class Shells_100mm( BaseCalibre ):
    bang = 7

class Shells_120mm( BaseCalibre ):
    bang = 8

class Shells_150mm( BaseCalibre ):
    """The ammunition used by the BuruBuru's Shaka Cannon."""
    bang = 9

class Ferrous_70mm( BaseCalibre ):
    bang = 9

