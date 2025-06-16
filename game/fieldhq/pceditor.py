import pbge
import gears
from pbge import widgets
from game import chargen
import pygame

class PCEditorWidget(widgets.Widget):
    def __init__(self, camp: gears.GearHeadCampaign, pc: gears.base.Character):
        super().__init__(0,0,0,0)

        self.camp = camp
        self.pc = pc
        self.portrait_view = gears.portraits.PortraitView(pc.get_portrait(), x_offset=-300)

        right_column = widgets.ColumnWidget(50,-200,250,400,padding=32,center_interior=True)
        self.children.append(right_column)

        name_column = widgets.ColumnWidget(0, 0, right_column.w, 64, draw_border=True, center_interior=True)
        name_column.add_interior(widgets.LabelWidget(0,0,100,0,"name",justify=0))
        self.name_widget = widgets.TextEntryWidget(0,0,right_column.w-20,32,pc.name,font=pbge.BIGFONT,justify=0)
        name_column.add_interior(self.name_widget)
        right_column.add_interior(name_column)

        right_column.add_interior(widgets.LabelWidget(
            0, 0, right_column.w, 0, "Edit Portrait", font=pbge.BIGFONT, justify=0, draw_border=True,
            on_click=self._edit_portrait
        ))

        right_column.add_interior(widgets.LabelWidget(
            0, 0, right_column.w, 0, "Edit Gender", font=pbge.BIGFONT, justify=0, draw_border=True,
            on_click=self._edit_gender, text_fun=self._gender_fun
        ))

        right_column.add_interior(widgets.LabelWidget(
            0, 0, 200, 0, "Done", font=pbge.BIGFONT, justify=0, draw_border=True,
            on_click=self._done
        ))

        self.finished = False

    def _edit_gender(self, *args):
        self.active = False
        chargen.GenderCustomizationWidget.create_and_invoke(self.pc)
        self.active = True

    def _gender_fun(self, *args):
        return "Edit Gender: {}".format(self.pc.gender.adjective.capitalize())

    def _edit_portrait(self, *args):
        self.active = False
        chargen.PortraitEditorW.create_and_invoke_with_pc(self.pc)
        self.portrait_view.portrait = self.pc.get_portrait(force_rebuild=True)
        if pbge.my_state.view and hasattr(pbge.my_state.view, "regenerate_avatars"):
            pbge.my_state.view.regenerate_avatars([self.pc])
        self.active = True

    def _done(self, wid, ev):
        self._apply_changes()
        self.finished = True

    def _apply_changes(self):
        nuname = self.name_widget.text
        if nuname and nuname != self.pc.name:
            # We need to save under the new name before deleting the old save file so that in the event of a crash,
            # power outage, etc, the save file is not lost.
            oldname = self.camp.name
            self.pc.name = nuname
            self.camp.name = nuname
            self.camp.save()
            self.camp.delete_save_file(oldname)

        self.camp.save()

    def _render(self, delta):
        #if draw_background and not self.active:
        #    pbge.my_state.view()
        self.portrait_view.render()

    @classmethod
    def create_and_invoke(cls, camp, pc):
        # Run the UI.
        myui = cls(camp, pc)
        pbge.my_state.widgets.append(myui)

        keepgoing = True
        while keepgoing and not myui.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    myui._apply_changes()
                    keepgoing = False

        pbge.my_state.widgets.remove(myui)


