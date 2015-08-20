import gears
import container
import calibre
import materials
import damage

part = gears.BeamWeapon(name="Intercept Laser",reach=2,damage=1,accuracy=2,penetration=1)
print( isinstance( part, gears.Weapon ) )

my_mecha = gears.Mecha( desig="Z45-62", name="Zerosaiko", sub_com = (
        gears.Head(size=4, material=materials.ADVANCED, sub_com = (
            gears.Armor(size=5, material=materials.ADVANCED),
            gears.Sensor(material=materials.ADVANCED),
        )),
        gears.Torso(size=5,material=materials.ADVANCED, sub_com = (
            gears.Armor(size=6,material=materials.ADVANCED),
            gears.Engine(size=1500,material=materials.ADVANCED,sub_com = (
                gears.Armor(size=1,material=materials.ADVANCED),
            )),
            gears.Gyroscope(material=materials.ADVANCED,sub_com = (
                gears.Armor(size=1,material=materials.ADVANCED),
            )),
            gears.Cockpit( material=materials.ADVANCED,sub_com = (
                gears.Armor(size=2,material=materials.ADVANCED),
            )),
            gears.Launcher( size=4,material=materials.ADVANCED, sub_com = (
                gears.Missile( name="Swarm Missiles", reach=6,damage=1,accuracy=1,penetration=1,quantity=20 ),
            )),
            gears.Mount(name="Right Collar Mount",material=materials.ADVANCED),
            gears.Mount(name="Left Collar Mount",material=materials.ADVANCED),
        )),
        gears.Arm(name="Right Arm",size=5,material=materials.ADVANCED, sub_com = (
            gears.Armor(size=5,material=materials.ADVANCED),
            gears.Hand(name="Right Hand",material=materials.ADVANCED, inv_com=(
                gears.BallisticWeapon(name="Mass Driver",material=materials.ADVANCED,reach=5,damage=3,accuracy=2,penetration=2,sub_com=(
                    gears.Ammo( calibre=calibre.Shells_150mm, quantity=15 ),
                )),
            )),
            gears.BeamWeapon(name="Point Cannon",material=materials.ADVANCED,reach=2,damage=1,accuracy=2,penetration=0,integral=True),
        )),
        gears.Arm(name="Left Arm",size=5,material=materials.ADVANCED, sub_com = (
            gears.Armor(size=5,material=materials.ADVANCED),
            gears.Hand(name="Left Hand",material=materials.ADVANCED, inv_com=(
                gears.BeamWeapon(name="Beam Sword",material=materials.ADVANCED,reach=1,damage=4,accuracy=3,penetration=1),
            )),
            gears.BeamWeapon(name="Point Cannon",material=materials.ADVANCED,reach=2,damage=1,accuracy=2,penetration=0,integral=True),
        )),
        gears.Leg(name="Right Leg",size=5,material=materials.ADVANCED, sub_com = (
            gears.Armor(size=5,material=materials.ADVANCED),
            gears.HoverJets(size=5,material=materials.ADVANCED),
        )),
        gears.Leg(name="Left Leg",size=5,material=materials.ADVANCED, sub_com = (
            gears.Armor(size=5,material=materials.ADVANCED),
            gears.HoverJets(size=5,material=materials.ADVANCED),
        )),
    )
 )

print "{} tons".format( my_mecha.mass / 10000.0 )
print "${}".format( my_mecha.cost )


print my_mecha.calc_mobility()

print "Shaka Cannon..."
damage.combat_test( my_mecha, damage.ShakaCannon )
print "Railgun..."
damage.combat_test( my_mecha, damage.Railgun )
print "Guided Missile..."
damage.combat_test( my_mecha, damage.Smartgun )


