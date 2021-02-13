import pbge
from gears import info
import pygame
from .. import invoker



class WeaponMenuDesc( pbge.frects.Frect ):
    def __init__(self, dx, dy, w, h, anchor):
        super(WeaponMenuDesc, self).__init__(dx, dy, w, h, anchor=anchor)
        self.library = dict()

    def __call__( self, menu_item ):
        # Just print this weapon's stats in the provided window.
        if menu_item.value not in self.library:
            self.library[menu_item.value.source] = info.get_shortform_display(menu_item.value.source,width=self.w,font=pbge.SMALLFONT)
        myrect = self.get_rect()
        self.library[menu_item.value.source].render(myrect.x,myrect.y)

class AttackWidget(invoker.InvocationsWidget):
    DESC_CLASS = WeaponMenuDesc
    IMAGE_NAME = 'sys_tacticsinterface_attackwidget.png'
    MENU_POS = (-420,15,200,180)
    DESC_POS = (-200, 15, 180, 180)
    def __init__(self, camp, pc, build_library_function, update_callback, start_source=None, **kwargs):
        super().__init__(camp, pc, build_library_function, update_callback, start_source, **kwargs)
        self.ammo_label = pbge.widgets.LabelWidget(26,37,212,14,text_fun=self._get_ammo_str,color=pbge.WHITE,
                                                   parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT,
                                                   justify=0, on_click=self.pop_invo_menu)
        self.children.append(self.ammo_label)
    def _get_ammo_str(self,wid):
        if self.shelf and self.shelf.source and hasattr(self.shelf.source,"get_ammo_string"):
            return self.shelf.source.get_ammo_string()
        else:
            return ""


class TargetingUI(invoker.InvocationUI):
    LIBRARY_WIDGET = AttackWidget
    def __init__(self,camp,attacker,**kwargs):
        super().__init__(camp,attacker,attacker.get_attack_library,**kwargs)
    def activate( self ):
        super(TargetingUI,self).activate()
        self.my_widget.maybe_select_shelf_with_this_source(self.camp.fight.cstat[self.pc].last_weapon_used)
    def launch(self):
        self.camp.fight.cstat[self.pc].last_weapon_used = self.my_widget.shelf.source
        super(TargetingUI,self).launch()

    def name_current_invo(self):
        # For weapons, always use the attack number.
        return str(self.my_widget.invo)
