import asyncio

from App import Controller

if __name__ == "__main__":
    class R(object):
        def update(self, speed):
            print(speed)


    Controller(R(), "ws://127.0.0.1:8080")

    asyncio.get_event_loop().run_forever()
