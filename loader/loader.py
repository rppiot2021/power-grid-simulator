import sys
import os

sys.path.insert(0, os.getcwd() + '/')
sys.path.insert(0, os.getcwd() + '/../')
# sys.path.insert(0, os.getcwd() + '/../adapter')
sys.path.insert(0, os.getcwd() + '/../adapter')

from hat.aio import run_asyncio
import signal
from adapter import Adapter

from ws.ws_client import WSClient

# from protocols.server import Server
# from protocols.ws_server import WSServer
# from protocols.client import Client
# import websockets

from yaml_parser import get_config

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

    adapter = Adapter(
        state_or_data=False,
        notify_small=False
    )

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    config = get_config()

    adapter.debug_counter = 1

    while True:
        # todo use config file

        ws_config = config["protocol_WebSocket"]

        print("ws_config", ws_config)

        identifier = getattr(sys.modules[__name__], "WSClient")

        print("id", identifier)

        await adapter.forward(

            source_protocol_type=getattr(sys.modules[__name__], ws_config["client_class_name"]),
            source_domain_name=ws_config["domain_name"],
            source_port=int(ws_config["port"]),

            keep_alive_source=True,

            destination_protocol_type=None,
            destination_domain_name=None,
            destination_port=None,
            keep_alive_destination=True,
            forward_without_confirmation=True
        )

        # def __init__(self, domain_name="127.0.0.1", port=8765):

        break

    # await adapter.connect()
    # print(await adapter.tcp_get_curr_data())
    # await adapter.close()
    #
    # await adapter.connect()
    # print(await adapter.tcp_get_curr_data())
    # await adapter.close()

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
