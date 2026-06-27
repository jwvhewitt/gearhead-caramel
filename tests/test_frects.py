import unittest
import pbge

class TestPyRect(unittest.TestCase):
    def test_copy(self):
        myrect = pbge.frects.PyRect(0,0,100,50)
        self.assertIsNot(myrect, myrect.copy())

    def test_inflate(self):
        myrect = pbge.frects.PyRect(0,0,100,50)
        irect = myrect.inflate(4, 6)
        self.assertEqual(myrect.w+4, irect.w)
        self.assertEqual(myrect.h+6, irect.h)

if __name__ == "__main_":
    unittest.main()
