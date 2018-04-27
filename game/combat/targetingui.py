import pbge
from gears import info
import pygame
from .. import invoker



class WeaponMenuDesc( pbge.frects.Frect ):
    def render_desc( self, menu_item ):
        # Just print this weapon's stats in the provided window.
        myrect = self.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text( pbge.SMALLFONT, self.get_desc(menu_item.value.source), self.get_rect(), justify = -1, color=pbge.WHITE )
    def get_desc( self, weapon ):
        # Return the weapon stats as a string.
        if hasattr( weapon, 'get_weapon_desc' ):
            return weapon.get_weapon_desc()
        else:
            return '???'

class AttackWidget(invoker.InvocationsWidget):
    DESC_CLASS = WeaponMenuDesc
    IMAGE_NAME = 'sys_tacticsinterface_attackwidget.png'

class TargetingUI(invoker.InvocationUI):
    LIBRARY_WIDGET = AttackWidget
    def __init__(self,camp,attacker,foo=None,bar=None):
        super(TargetingUI,self).__init__(camp,attacker,attacker.get_attack_library)

