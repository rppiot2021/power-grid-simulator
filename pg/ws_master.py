import asyncio
import websockets

from hat.aio import run_asyncio
import nest_asyncio


class Server:

    def __init__(self):
        self.debug_counter = 0

    async def echo(self, websocket, path):
        async for message in websocket:

            print("received;", message)
            await websocket.send(str("echo:" + str(self.debug_counter) + str(message)))
            self.debug_counter += 1


async def init_server():
    server = Server()

    print("connect on ws://localhost:8765")

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(server.echo, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()

    return server


async def async_main():
    await init_server()


def main():
    nest_asyncio.apply()
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
