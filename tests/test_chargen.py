import unittest
import gears
import game
import pbge

print("Testing...")

gamedir = "/home/joseph/Documents/Programming/gearhead-caramel"
pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png')

gears.init_gears()
game.init_game()


class TestLifepath(unittest.TestCase):
    def test_event_usage(self):
        for t in range(10000):
            _=game.chargen.lifepath.Lifepath.random_lifepath()
        for a in game.chargen.lifepath.ALL_LP_EVENTS:
            self.assertIn(a, game.chargen.lifepath.LP_EVENT_USAGE, "{} not used".format(a))


if __name__ == "__main_":
    unittest.main()
