# Contains calibre definitions for ammunition.
# Calibre has one major attribute- "bang"- which determines its mass, volume,
# and the number of bullets that must be expended by a given weapon.

from pbge import Singleton

class BaseCalibre( Singleton ):
    bang = 1

class Shells_150mm( BaseCalibre ):
    """The ammunition used by the BuruBuru's Shaka Cannon."""
    bang = 9

