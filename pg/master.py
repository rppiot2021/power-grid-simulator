import asyncio
import websockets

# from data_manager import init_data_manager
from hat.aio import run_asyncio
import json
import nest_asyncio


class Server:

    def __init__(self):
        self.debug_counter = 0

    async def echo(self, websocket, path):
        async for message in websocket:

            # if message == "init_data":
            #     data = await self.data_manager.get_init_data()
            #
            #     json_data = json.dumps({
            #         str(k): str(v) for k, v in data.items()
            #     })
            #
            #     await websocket.send(str(json_data))
            #
            # elif message == "curr_data":
            #     data = await self.data_manager.get_curr_data()
            #
            #     json_data = json.dumps({
            #         str(k): str(v) for k, v in data.items()
            #     })
            #
            #     await websocket.send(str(json_data))
            #
            # elif message.startswith("update"):
            #     """
            #     update;asdu;io;value
            #     """
            #
            #     raw_d = message.split(";")
            #     asdu = raw_d[1]
            #     io = raw_d[2]
            #     value = raw_d[3]
            #
            #     await self.data_manager.send_data(value, asdu, io)
            #
            # else:
            #     print("other msg", message)
            #     await websocket.send(str("other message data, echo:" +
            #                              str(message)))

            print("received;", message)
            await websocket.send(str("echo:" + str(self.debug_counter) + str(message)))
            self.debug_counter += 1
    # async def init_data_manager(self):
    #     self.data_manager = await init_data_manager()


async def init_server():
    server = Server()
    # await server.init_data_manager()
    # print("data manager configured")

    print("connect on ws://localhost:8765")

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(server.echo, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()

    return server


async def async_main():
    await init_server()


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    nest_asyncio.apply()

    main()