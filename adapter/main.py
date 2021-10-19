import sys
import os

sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../pg')
from hat.aio import run_asyncio
from pg.tcp_client2 import TCPClient
import signal
from adapter import get_adapter

# from pg.server import Server
# from pg.ws_server import WSServer
# from pg.client import Client
# import websockets


"""
utils for address translations
"""


# todo later
# class Address:
#
#     @staticmethod
#     def get_formatted_name(asdu_address, io_address):
#         return str(asdu_address) + ";" + str(io_address)
#
#     def __init__(self, asdu_address, io_address):
#         self.asdu_address = asdu_address
#         self.io_address = io_address
#
#     def __str__(self):
#         return f"{self.asdu_address=} {self.io_address=}"
#
#     def formatted_name(self):
#         return Address.get_formatted_name(self.asdu_address, self.io_address)


# async def init_server():
#     server = WSServer("localhost", 8765)
#
#     signal.signal(signal.SIGINT, signal.SIG_DFL)
#
#     print("connect on ws://" + server.host_name + ":" + str(server.port))
#
#     asyncio.get_event_loop().run_until_complete(
#         websockets.serve(server.echo, server.host_name, server.port))
#     asyncio.get_event_loop().run_forever()
#
#     return server


async def async_main():
    # todo .sh that starts this, simulator and designated server

    # todo try with localhost instead of address

    adapter = get_adapter(TCPClient,
                          "127.0.0.1",
                          4567,
                          state_or_data=False,
                          notify_small=False)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    adapter.debug_counter = 1

    await adapter.connect()

    print(await adapter.get_init_data())

    # todo sanitize
    # print("connect using:", adapter.server_type)

    # print("connect on ws://" + adapter.host_name + ":" + str(adapter.port))
    # asyncio.get_event_loop().run_until_complete(
    #     websockets.serve(
    #       adapter._server_driver,
    #       adapter.host_name, adapter.port))
    # asyncio.get_event_loop().run_forever()

    # while True:
    #     old = {k: v for k, v in adapter.data.items()}
    #     print(await adapter.get_curr_data())
    #     diff = set(old.items()) ^ set(adapter.data.items())
    #     print("diff", diff)

    # await t._run()

    # return


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
