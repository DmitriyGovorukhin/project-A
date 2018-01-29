import argparse
import json
import queue
import subprocess

import websockets

from core.Robot import *


class Video(object):
    def __init__(self, device, host):
        self.cmd = "ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -i " + device + \
                   " -f mpegts -r 30 -codec:v mpeg1video -s 1280x720 -b:v 100000k -bf 0 http://" + host

        self.q = queue.Queue()
        self.p = None
        thread = Thread(target=self.run, name='Video')
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            next_command = self.q.get()

            if next_command == "video_start" and self.p is None:
                print("video_start")

                self.p = subprocess.Popen("exec " + self.cmd, shell=True)
            elif next_command == "video_stop" and self.p is not None:
                print("video_stop")

                self.p.kill()

                self.p = None

    def start_video(self):
        self.q.put("video_start")

    def stop_video(self):
        self.q.put("video_stop")


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
    def __init__(self, robot, video_dic, host):
        self.robot = robot
        self.video = video_dic

        async def listener():
            async with websockets.connect("ws://" + host + ":8090") as ws:
                init_msg = json.dumps({"from": "robot"})

                await ws.send(init_msg)

                while True:
                    msg = await ws.recv()

                    print("> {}".format(msg))

                    data = json.loads(msg)

                    if "cmd" in data:
                        if data["cmd"] == "axis":
                            res = {"from": "robot"}

                            res.update(self.on_receive(data))

                            print("< {}".format(res))

                            await ws.send(json.dumps(res))
                        elif data["cmd"] == "video_start":
                            self.video["2"].start_video()

                        elif data["cmd"] == "video_stop":
                            self.video["2"].stop_video()

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

        speed = {"A": a_speed, "B": b_speed}

        #if self is not None:
         #   self.robot.update(speed)

        return speed


if __name__ == "__main__":
    args = args()

    host = args.remote

    # comPort = "/dev/ttyACM0"

    # r = Robot(comPort)

    video = {"1": Video("/dev/video1", host + ":8091"),
             "2": Video("/dev/video0", host + ":8092")}

    Controller(None, video, args.remote)
