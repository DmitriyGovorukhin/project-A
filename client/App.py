import json
import argparse
import websockets
import subprocess
import os
import signal

from Robot import *

cmd = "ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -i /dev/video0 -f mpegts -r 30 -codec:v mpeg1video -s 1280x720 -b:v 100000k -bf 0 http://localhost:8092"


def remap(x, y):
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


def args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--remote")

    return parser.parse_args()


class Controller(object):
    def __init__(self, robot, host):
        self.robot = robot

        self.p = None

        async def listener():
            async with websockets.connect(host) as ws:
                init_msg = json.dumps({"client": "robot"})

                await ws.send(init_msg)

                while True:
                    msg = await ws.recv()

                    print("> {}".format(msg))

                    data = json.loads(msg)

                    if data["cmd"] == "axis":
                        res = self.on_receive(data)

                        res["client"] = "robot"

                        print("< {}".format(res))

                        await ws.send(json.dumps(res))
                    elif data["cmd"] == "video_start":
                        print("video_start")

                        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

                    elif data["cmd"] == "video_stop":
                        print("video_stop")

                        try:
                            os.killpg(self.p.pid, signal.SIGINT)
                        except ProcessLookupError:
                            print("exp!!")

        asyncio.get_event_loop().run_until_complete(listener())

    def on_receive(self, data):
        x = int(float(data['x']) * 255)
        y = int(float(data['y']) * 255)

        t = remap(x, y)

        a_speed = 0
        b_speed = 0

        if t[0] > 100 or t[0] < -100:
            a_speed = t[0]

        if t[1] > 100 or t[1] < -100:
            b_speed = t[1]

        # print("x:" + str(x) + " y:" + str(y) + " A: " + str(a_speed) + " B:" + str(b_speed))

        speed = {"A": a_speed, "B": b_speed}

        # self.robot.update(speed)

        return speed


if __name__ == "__main__":
    args = args()

    print(args.remote)

    # comPort = "/dev/ttyACM0"

    # r = Robot(comPort)

    Controller(None, args.remote)
