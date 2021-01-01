import pbge
import gears
import glob
import copy
import pickle


class Eggzaminer(object):
    LEFT_COLUMN = pbge.frects.Frect(-320, -200,300,450)
    RIGHT_COLUMN = pbge.frects.Frect(20,-200,300,400)
    def __init__(self, tsrd):
        self.tsrd = tsrd
        self.info_cache = dict()
        self()

    def geardesc(self, menu_item):
        item = menu_item.value
        if item and isinstance(item, gears.base.BaseGear):
            myrect = self.LEFT_COLUMN.get_rect()
            if item not in self.info_cache:
                self.info_cache[item] = gears.info.get_longform_display(item, width=self.LEFT_COLUMN.w, font=pbge.MEDIUMFONT)
            self.info_cache[item].render(myrect.x, myrect.y)

    def examine_egg(self, fname):
        with open(fname, "rb") as f:
            egg = copy.deepcopy(pickle.load(f))

        mymenu = pbge.rpgmenu.Menu(self.RIGHT_COLUMN.dx,
                                   self.RIGHT_COLUMN.dy,
                                   self.RIGHT_COLUMN.w, self.RIGHT_COLUMN.h,
                                   predraw=self.tsrd, font=pbge.my_state.huge_font
                                   )
        mymenu.add_item(str(egg.pc), egg.pc)
        mymenu.add_item('Mek: '+str(egg.mecha), egg.mecha)
        for i in egg.dramatis_personae:
            mymenu.add_item('DPers: ' + str(i), i)
        for i in egg.stuff:
            mymenu.add_item('Stuff: ' + str(i), i)
        for i in egg.major_npc_records.keys():
            mymenu.add_item('MNPC: ' + str(i), i)

        mymenu.descobj = self.geardesc

        choice = "Blah"
        while choice:
            choice = mymenu.query()


    def __call__(self):
        # Top level menu: select an egg to examine.
        myfiles = glob.glob(pbge.util.user_dir("egg_*.sav"))
        mymenu = pbge.rpgmenu.Menu(self.RIGHT_COLUMN.dx,
                                   self.RIGHT_COLUMN.dy,
                                   self.RIGHT_COLUMN.w, self.RIGHT_COLUMN.h,
                                   predraw=self.tsrd, font=pbge.my_state.huge_font
                                   )
        for fname in myfiles:
            mymenu.add_item(fname,fname)
        mymenu.sort()
        mymenu.add_item("[Exit]", None)

        choice = "Blah"
        while choice:
            choice = mymenu.query()
            if choice:
                self.examine_egg(choice)
