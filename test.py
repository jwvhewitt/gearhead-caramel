import engine
import os
import scenes

gamedir = os.path.dirname(__file__)

engine.init('GearHead Caramel','dmeternal',gamedir)

mymenu = engine.rpgmenu.Menu(-150,-150,300,300)
mymenu.add_item('One',1)
mymenu.add_item('Two',1)
mymenu.add_item('Three',1)
mymenu.query()


