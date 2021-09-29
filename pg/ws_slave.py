import asyncio

import hat
import websockets
from hat.aio import run_asyncio

from client import Client


async def hello(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello world!")
        t = await websocket.recv()
        print(t)
        print()

        await websocket.send("init_data")
        t = await websocket.recv()
        print(t)
        print()

        await websocket.send("curr_data")
        t = await websocket.recv()
        print(t)
        print()

asyncio.get_event_loop().run_until_complete(
    hello('ws://localhost:8765'))


class WSClient():

    # def __init__(self, domain_name, port):
    #     super().__init__(domain_name, port)

        # self.msg_que = []

    def _get_uri(self):
        return "ws://" + str(self.domain_name) + ":" + str(self.port)

    async def _driver(self):
        print("driver created")

        while True:
            # async with websockets.connect(self._get_uri()) as websocket:
                # await websocket.send(str(payload))
            # breakpoint()
            tmp = await self.websocket.recv()

            print("tmp", tmp)
            # self.msg_que.append(tmp)

            # print("que updated", self.msg_que)

    async def send(self, payload):
        print("attempting to send", payload)
        # async with websockets.connect(self._get_uri()) as websocket:
        await self.websocket.send(str(payload))

        print("sent:", payload)

    # async def receive(self):
    #     print()

    # async def receive(self):
    #     pass
    # #     # async with websockets.connect(self._get_uri()) as websocket:
    # #     return await self.websocket.recv()
    # #
    # #
    #

async def async_main():

    # breakpoint()

    client = WSClient()

    client.domain_name="127.0.0.1"
    client.port=8765

    # client.websocket = await websockets.connect(client._get_uri())
    async with websockets.connect(client._get_uri()) as websocket:

        client.websocket = websocket

        client._group = hat.aio.Group()
        client._group.spawn(client._driver)

        await client.send("tmfp")

        await asyncio.sleep(10)

        await client._group.async_close()
        client.websocket = None

    # await client._driver()

    # await client.send("hello, Привет")

    # tmp = await client.receive()
    # print("received", tmp)
    # await client.receive()

def main():

    run_asyncio(async_main())


if __name__ == '__main__':
    main()
