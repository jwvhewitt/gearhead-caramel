import gears
import container
import calibre
import damage

part = gears.BeamWeapon(name="Intercept Laser",reach=2,damage=1,accuracy=2,penetration=1)
print( isinstance( part, gears.Weapon ) )

my_mecha = gears.Mecha( desig="CHR-3L", name="Chimentero", sub_com = (
        gears.Storage(name="Right Thruster", size=5, sub_com = (
            gears.Armor(size=6),
            gears.HoverJets(size=11),
            gears.Mount(name="Right Thruster Mount", inv_com=(
               gears.BeamWeapon(name="Heavy Pulse Cannon",reach=6,damage=3,accuracy=4,penetration=0),
            )),
            gears.Launcher( size=2, sub_com = (
                gears.Missile( name="Swarm Missiles", reach=6,damage=1,accuracy=1,penetration=1,quantity=10 ),
            )),
        )),
        gears.Storage(name="Left Thruster", size=5, sub_com = (
            gears.Armor(size=6),
            gears.HoverJets(size=11),
            gears.Mount(name="Right Thruster Mount", inv_com=(
               gears.BeamWeapon(name="Heavy Pulse Cannon",reach=6,damage=3,accuracy=4,penetration=0),
            )),
            gears.Launcher( size=2, sub_com = (
                gears.Missile( name="Swarm Missiles", reach=6,damage=1,accuracy=1,penetration=1,quantity=10 ),
            )),
        )),
        gears.Torso(size=7, sub_com = (
            gears.Armor(size=7),
            gears.Engine(size=1000,sub_com = (
                gears.Armor(size=2),
            )),
            gears.Gyroscope(sub_com = (
                gears.Armor(size=2),
            )),
            gears.Cockpit( sub_com = (
                gears.Armor(size=2),
            )),
            gears.BeamWeapon(name="Plasma Core Gun",reach=7,damage=3,accuracy=0,penetration=4),
            gears.Mount(name="Lower Weapon Mount", inv_com=(
                gears.Launcher( size=12, sub_com = (
                    gears.Missile( name="Swarm Missiles", reach=6,damage=1,accuracy=1,penetration=1,quantity=60 ),
                )),
            )),
            gears.Mount(name="Top Weapon Mount", inv_com=(
                gears.Launcher( size=12, sub_com = (
                    gears.Missile( name="Swarm Missiles", reach=6,damage=1,accuracy=1,penetration=1,quantity=60 ),
                )),
            )),
        )),
        gears.Arm(name="Right Arm",size=5, sub_com = (
            gears.Armor(size=7),
            gears.Hand(name="Right Hand"),
            gears.Mount(name="Right Arm Mount", inv_com=(
                gears.BallisticWeapon(name="Monster Assault Cannon",reach=5,damage=5,accuracy=1,penetration=1,sub_com=(
                    gears.Ammo( calibre=calibre.Shells_150mm, quantity=15 ),
                )),
            )),
        )),
        gears.Arm(name="Left Arm",size=5, sub_com = (
            gears.Armor(size=7),
            gears.Hand(name="Left Hand"),
            gears.Mount(name="Left Arm Mount", inv_com=(
                gears.BallisticWeapon(name="Monster Assault Cannon",reach=5,damage=5,accuracy=1,penetration=1,sub_com=(
                    gears.Ammo( calibre=calibre.Shells_150mm, quantity=15 ),
                )),
            )),
        )),
        gears.Leg(name="Right Leg",size=8, sub_com = (
            gears.Armor(size=7),
            gears.HoverJets(size=4),
        )),
        gears.Leg(name="Left Leg",size=8, sub_com = (
            gears.Armor(size=7),
            gears.HoverJets(size=4),
        )),
    )
 )

print "Shaka Cannon..."
damage.combat_test( my_mecha, damage.ShakaCannon )
print "Railgun..."
damage.combat_test( my_mecha, damage.Railgun )
print "Guided Missile..."
damage.combat_test( my_mecha, damage.Smartgun )
print "Glass Cow..."
damage.combat_test( my_mecha, damage.GlassCow )



