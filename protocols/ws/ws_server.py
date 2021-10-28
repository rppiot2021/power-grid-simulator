import os
import sys

# sys.path.insert(0, os.getcwd() + '/../protocols')
sys.path.insert(0, os.getcwd() + '/../../')

import asyncio
import signal

import nest_asyncio
import websockets
from hat.aio import run_asyncio

from protocols.util.server import Server


class WSServer(Server):

    def __init__(self, domain_name="127.0.0.1", port=8765):
        super().__init__(domain_name, port)

        self.debug_counter = 0

    async def echo(self, websocket, path):
        async for message in websocket:
            print("received:", message)
            await websocket.send(str("echo: " + str(self.debug_counter) + " "
                                     + str(message)))
            self.debug_counter += 1
            print()

    # todo extract this parts because this is not minimal example for ws,
    #   this is concrete implementation
    async def driver(self, websocket, path):

        async for message in websocket:
            print("received:", message)
            print()
            raw_data = message.split(";")
            print("raw data", raw_data)
            sw = raw_data[0]

            if sw == "upload":

                sw = raw_data[1]

                if sw == "get_curr_state":
                    print("get curr state")

                elif sw == "get_init_data":
                    print("get init data")

                elif sw == "get_curr_data":
                    print("get curr data")

                elif sw == "update_data":
                    print("update data")

            elif sw == "download":
                pass

            else:
                await websocket.send(
                    str("echo: " + str(self.debug_counter) + " "
                        + str(message)))
                self.debug_counter += 1

                print("msg", message[:10])
                # raise NotImplementedError


async def init_server():
    server = WSServer("localhost", 8765)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    print("connect on ws://" + server.host_name + ":" + str(server.port))

    # asyncio.get_event_loop().run_until_complete(
    #     websockets.serve(server.echo, server.host_name, server.port))
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(server.driver, server.host_name, server.port))
    asyncio.get_event_loop().run_forever()

    return server


async def async_main():
    await init_server()


def main():
    nest_asyncio.apply()
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
