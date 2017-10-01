import unittest

from core.App import *


class TestTransform(unittest.TestCase):
    def test_stop(self):
        res = remap(0, 0)

        self.assertEqual(res, (0, 0))

    def test_full_forward(self):
        res = remap(0, 255)

        self.assertEqual(res, (255, 255))

        res = remap(0, 127)

        self.assertEqual(res, (127, 127))

    def test_full_backward(self):
        res = remap(0, -255)

        self.assertEqual(res, (-255, -255))

        res = remap(0, -127)

        self.assertEqual(res, (-127, -127))

    def test_turn_left(self):
        res = remap(-255, 0)

        self.assertEqual(res, (0, 255))

        res = remap(-255, 255)

        self.assertEqual(res, (0, 255))

    def test_turn_right(self):
        res = remap(255, 255)

        self.assertEqual(res, (255, 0))

        res = remap(255, 0)

        self.assertEqual(res, (255, 0))


if __name__ == "__main__":
    unittest.main()
