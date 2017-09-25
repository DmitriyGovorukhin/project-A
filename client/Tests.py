from Robot import *

import unittest


class TestTransform(unittest.TestCase):
    def test_stop(self):
        state = {
            "right_analog_x": 0,
            "right_analog_y": 0,
        }

        res1 = map(state)

        self.assertEqual(res1, (0, 0))

    def test_full_forward(self):
        state = {
            "right_analog_x": 0,
            "right_analog_y": 255,
        }

        res1 = map(state)

        self.assertEqual(res1, (255, 255))

        state = {
            "right_analog_x": 0,
            "right_analog_y": 127,
        }

        res1 = map(state)

        self.assertEqual(res1, (127, 127))

    def test_full_backward(self):
        state = {
            "right_analog_x": 0,
            "right_analog_y": -255,
        }

        res1 = map(state)

        self.assertEqual(res1, (-255, -255))

        state = {
            "right_analog_x": 0,
            "right_analog_y": -127,
        }

        res1 = map(state)

        self.assertEqual(res1, (-127, -127))

    def test_turn_left(self):
        state = {
            "right_analog_x": -255,
            "right_analog_y": 0,
        }

        res1 = map(state)

        self.assertEqual(res1, (0, 255))

        state = {
            "right_analog_x": -255,
            "right_analog_y": 255,
        }

        res1 = map(state)

        self.assertEqual(res1, (0, 255))

    def test_turn_right(self):
        state = {
            "right_analog_x": 255,
            "right_analog_y": 255,
        }

        res1 = map(state)

        self.assertEqual(res1, (255, 0))

        state = {
            "right_analog_x": 255,
            "right_analog_y": 0,
        }

        res1 = map(state)

        self.assertEqual(res1, (255, 0))


if __name__ == "__main__":
    unittest.main()
