import pbge
from gears import info
import pygame
from .. import invoker


class UsableWidget(invoker.InvocationsWidget):
    IMAGE_NAME = 'sys_invokerinterface_usables.png'


class UsablesUI(invoker.InvocationUI):
    LIBRARY_WIDGET = UsableWidget
    def __init__(self,camp,attacker,**kwargs):
        super().__init__(camp,attacker,attacker.get_usable_library,**kwargs)
