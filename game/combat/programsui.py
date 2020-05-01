import pbge
from gears import info
import pygame
from .. import invoker



class ProgramWidget(invoker.InvocationsWidget):
    IMAGE_NAME = 'sys_invokerinterface_programs.png'

class ProgramsUI(invoker.InvocationUI):
    LIBRARY_WIDGET = ProgramWidget
    def __init__(self,camp,attacker,**kwargs):
        super().__init__(camp,attacker,attacker.get_program_library,**kwargs)
    def activate( self ):
        super(ProgramsUI,self).activate()
        self.my_widget.maybe_select_shelf_with_this_source(self.camp.fight.cstat[self.pc].last_program_used)
    def launch(self):
        self.camp.fight.cstat[self.pc].last_program_used = self.my_widget.shelf.source
        super(ProgramsUI,self).launch()
