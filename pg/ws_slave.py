import asyncio
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


class WSClient(Client):

    def __init__(self, domain_name, port):
        super().__init__(domain_name, port)

        self.msg_que = []

    def _get_uri(self):
        return "ws://" + str(self.domain_name) + ":" + str(self.port)

    async def send(self, payload):
        async with websockets.connect(self._get_uri()) as websocket:
            await websocket.send(str(payload))

            tmp = await websocket.recv()


    async def receive(self):
        async with websockets.connect(self._get_uri()) as websocket:
            return await websocket.recv()


async def async_main():

    client = WSClient(port=8765)

    await client.send("hello, Привет")

    tmp = await client.receive()
    print("received", tmp)


def main():

    run_asyncio(async_main())


if __name__ == '__main__':
    main()
