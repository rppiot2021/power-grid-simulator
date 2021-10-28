import sys
import os
import time
import asyncio
from abc import ABC, abstractmethod
from hat.drivers import iec104

sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../protocols')
from protocols.tcp.tcp_client2 import TCPClient
from protocols.ws.ws_client import WSClient
from protocols.tcp.TCPBuffer import MessageType


class Strategy(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def get_init_data(self):
        pass

    @abstractmethod
    async def get_curr_data(self):
        pass

    @abstractmethod
    async def send_data(self, value, asdu, io):
        pass


class IEC104Protocol(Strategy):

    def __init__(self, domain_name="127.0.0.1",
                 port=19999,
                 reconnect_delay=3,
                 send_retry_count=3):
        self.connection = None
        self.domain_name = domain_name
        self.port = port
        self.reconnect_delay = reconnect_delay
        self.send_retry_count = send_retry_count

    async def connect(self):
        address = iec104.Address(self.domain_name, self.port)

        while True:

            try:
                self.connection = await iec104.connect(address)
                return self.connection

            except ConnectionRefusedError:
                for i in range(self.reconnect_delay):
                    print("trying to reconnect in", self.reconnect_delay - i)
                    await asyncio.sleep(1)

                print("reconnecting\n")

    async def get_init_data(self):
        async def get_init_data_payload():
            raw_data = await self.connection.interrogate(asdu_address=65535)
            return {(i.asdu_address, i.io_address): i.value for i in raw_data}

        return await self._connection_wrapper(
            get_init_data_payload
        )

    async def get_curr_data(self):
        async def get_curr_data_payload():
            raw_data = await self.connection.receive()
            return {(i.asdu_address, i.io_address): i.value for i in
                    raw_data}

        return await self._connection_wrapper(
            get_curr_data_payload
        )

    async def _connection_wrapper(self, payload):
        while True:
            try:
                return await payload()
            except ConnectionError:
                print("Connection error")
                self.connection = await self.connect()

    async def send_data(self, value, asdu, io):

        print(asdu, io, value, type(value))

        try:
            asdu = int(asdu)
            io = int(io)

            if isinstance(value, str):

                if value == "close":
                    value = iec104.common.SingleValue(1)

                elif value == "open":
                    value = iec104.common.SingleValue(0)

                else:
                    raise ValueError

            # else use current value, assumption: it is a number

        except ValueError:
            return

        command = iec104.Command(
            value=value,
            asdu_address=asdu,
            io_address=io,
            action=iec104.Action.EXECUTE,
            time=None,
            qualifier=1
        )

        print("command", command)

        for _ in range(self.send_retry_count):
            try:
                await self.connection.send_command(command)
                return
            except ConnectionError:
                print("Connection error")
                self.connection = await self.connect()

        raise Exception("can not send command")


class WSProtocol(Strategy):

    def __init__(self):
        self.client = WSClient()

    async def connect(self):
        pass

    async def get_init_data(self):
        return self.get_curr_data()

    async def get_curr_data(self):
        return self.client.receive()

    async def send_data(self, value, asdu=0, io=0):
        await self.client.send(value)


class TCPProtocol(Strategy):
    def __init__(self):

        self.client = TCPClient("127.0.0.1", 4567)

    async def get_init_data(self):
        return self.get_curr_data()

    async def get_curr_data(self):
        try:
            # return self.client.buffer.read_next()
            return self.client.receive()
        except IndexError:
            self.close()

    async def send_data(self, value, asdu=0, io=0,
                        data_type=MessageType.CONTENT):
        self.client.send(value, data_type)

    async def connect(self):
        self.client.start_connection(dont_close=True)

    def close(self):
        self.client.close_connection()


async def async_main():
    protocol = TCPProtocol()
    protocol.client.start_connection()

    await protocol.send_data("1.")
    await protocol.send_data("2.")
    await protocol.send_data("3.")
    await protocol.send_data("4.")
    time.sleep(2)

    print(f"     {await protocol.get_curr_data()}")
    print(f"     {await protocol.get_curr_data()}")
    print(f"     {await protocol.get_curr_data()}")
    print(f"     {await protocol.get_curr_data()}")

    protocol.close()

    protocol = IEC104Protocol()
    await protocol.connect()

    t = await protocol.get_init_data()
    print("init data")
    [print(i) for i in t.items()]

    t = await protocol.get_curr_data()
    print("curr data")
    [print(i) for i in t.items()]

    await protocol.send_data("closed", 30, 0)
    print("data sent")

    while True:
        t = await protocol.get_curr_data()
        print("curr data")
        [print(i) for i in t.items()]

