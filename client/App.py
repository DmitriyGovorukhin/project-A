from DS4 import *
from Robot import *

import threading


class Fil:
    def __init__(self):
        self.state = {}

    def handler(self, e):
        time.sleep(1)

        print(e)


f = Fil()

if __name__ == "__main__":
    port = "/dev/ttyACM0"

    #r = Robot(port)
    #Controller(r.event_handler)

    f = Fil()
    Controller(f.handler)
