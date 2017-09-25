from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3
from threading import *

import time
import asyncio


def map(state):
    x = state['right_analog_x']
    y = state['right_analog_y']

    def compute(a, b):
        MAX = max(a, b)

        if b == 0:
            return MAX, MAX

        if b < MAX:
            return MAX, MAX - b
        else:
            return MAX, 0

    res = compute(abs(y), abs(x))

    if abs(x) < 50:
        if y > 0:
            return res
        else:
            return -res[0], -res[1]

    # Forward
    if y >= 0:
        if x > 0:
            return res
        else:
            return res[1], res[0]
    # Backward
    else:
        if x > 0:
            return -res[0], res[1]
        else:
            return res[1], -res[0]


def normal(v):
    return (v - 128) * 2 + 1


def _map(state):
    x = state['l2_analog']
    y = state['r2_analog']

    return _normal(x), _normal(y)


def _normal(n):
    if n > 50:
        return n
    elif n < -50:
        return n
    else:
        return 0


class Robot(object):
    DIR_A = 12
    BRAKE_A = 9
    PWM_A = 3

    DIR_B = 13
    BRAKE_B = 8
    PWM_B = 11

    MIN = 100
    MAX = 255

    RANGE = MAX - MIN

    include = ["left_analog_x",
               "left_analog_y",
               "right_analog_x",
               "right_analog_y",
               "l2_analog",
               "r2_analog",
               "battery"]

    lock = Lock()

    freq = 0.3

    def __init__(self, port):
        self.port = port
        self.state = {
            "left_analog_x": 0,
            "left_analog_y": 0,
            "right_analog_x": 0,
            "right_analog_y": 0,
            "l2_analog": 0,
            "r2_analog": 0,
            "battery": 0
        }

        self.a = PyMata3(com_port=self.port)

        self.a.set_pin_mode(self.BRAKE_A, Constants.OUTPUT)
        self.a.set_pin_mode(self.DIR_A, Constants.OUTPUT)
        self.a.set_pin_mode(self.PWM_A, Constants.PWM)

        self.a.set_pin_mode(self.BRAKE_B, Constants.OUTPUT)
        self.a.set_pin_mode(self.DIR_B, Constants.OUTPUT)
        self.a.set_pin_mode(self.PWM_B, Constants.PWM)

        thread = Thread(target=self.loop, name='Robot')
        thread.start()

    def loop(self):
        asyncio.set_event_loop(self.a.loop)

        while True:
            time.sleep(self.freq)

            self.lock.acquire()

            state = self.state

            t = map(state)

            self.lock.release()

            a_speed = 0
            b_speed = 0

            if t[0] > 100 or t[0] < -100:
                a_speed = t[0]

            if t[1] > 100 or t[1] < -100:
                b_speed = t[1]

            print("state:" + str(state) + " motors: " + str((a_speed, b_speed)))

            self._set_speed("B", a_speed)
            self._set_speed("A", b_speed)

    def _set_speed(self, motor, speed):
        if "A" == motor:
            d = 0
            if speed < 0:
                d = 1
            self.a.digital_pin_write(self.BRAKE_A, 0)
            self.a.digital_pin_write(self.DIR_A, d)
            self.a.analog_write(self.PWM_A, abs(speed))
        elif "B" == motor:
            d = 0
            if speed < 0:
                d = 1
            self.a.digital_pin_write(self.BRAKE_B, 0)
            self.a.digital_pin_write(self.DIR_B, d)
            self.a.analog_write(self.PWM_B, abs(speed))

    def event_handler(self, event_map):
        self.lock.acquire()

        self.state = {
            "left_analog_x": normal(event_map["left_analog_x"]),
            "left_analog_y": -normal(event_map["left_analog_y"]),
            "right_analog_x": normal(event_map["right_analog_x"]),
            "right_analog_y": -normal(event_map["right_analog_y"]),
            "l2_analog": event_map["l2_analog"],
            "r2_analog": event_map["r2_analog"],
            "battery": event_map["battery"],
        }

        self.lock.release()
