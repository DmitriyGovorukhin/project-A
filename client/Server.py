import asyncio
import json
import websockets

if __name__ == "__main__":
    async def listener(ws, path):
        input1 = await ws.recv()

        print("> {}".format(input1))

        await ws.send(json.dumps({"x": 1.0, "y": 0.0}))

        input2 = await ws.recv()

        print("> {}".format(input2))


    server = websockets.serve(listener, '127.0.0.1', 8080)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
