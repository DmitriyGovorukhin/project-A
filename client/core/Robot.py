from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3
from threading import *

import time
import asyncio


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

    lock = Lock()

    freq = 0.3

    def __init__(self, port):
        self.port = port
        self.speed = {
            "A": 0,
            "B": 0
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

            speed = self.speed

            self.lock.release()

            self._set_speed("A", speed["A"])
            self._set_speed("B", speed["B"])

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

    def update(self, speed):
        self.lock.acquire()

        self.speed = speed

        self.lock.release()
