import pbge
import gears
import glob


class Eggzaminer(object):
    LEFT_COLUMN = pbge.frects.Frect(-300, -250,220,500)
    RIGHT_COLUMN = pbge.frects.Frect(0,-200,300,400)
    def __init__(self, tsrd):
        self.tsrd = tsrd
        self()

    def examine_egg(self, choice):
        pass

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
