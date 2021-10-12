"""
utils for address translations
"""
import os
import sys
import time

sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../pg')

from hat.aio import run_asyncio
from hat.drivers import iec104
import asyncio
from abc import ABC, abstractmethod
from pg.ws_client import WSClient
from pg.tcp_client2 import TCPClient
from pg.TCPBuffer import MessageType


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
        self.client.send(value)


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


from pg.server import Server


class Adapter(Server):

    """
    notify_small
        if True; return everything when get_curr_data is passed without
        checking if new values are same as old

        sometimes value is passed as new value because there are not
        enough decimal places to check

        you can choose to ignore those values


    get_curr_state and get_curr_data can not work in tandem

    state_or_data
        True:
            get_curr_state works

        False:
            get_curr_data works

    """

    def __init__(self, host_name, port, state_or_data=True, notify_small=False):
        super().__init__(host_name, port)

        self.protocol = IEC104Protocol()
        self.data = {}

        self.notify_small = notify_small

        self.is_init_called = False
        self.state_or_data = state_or_data

    async def _run(self):
        """
        driver for state memory

        :return:
        """

        t = await self.protocol.get_init_data()
        # self.data = dict(self.data, **{var_name: e.payload.data})
        # self.data = dict(self.data, t)
        self.data.update(t)

        print(self.data)

        while True:
            t = await self.protocol.get_curr_data()

            old = {k: v for k, v in self.data.items()}

            self.data.update(t)

            diff = set(old.items()) ^ set(self.data.items())
            print("diff", diff)

            # print(self.data)

    async def get_curr_state(self):
        """
        return current state of system
        include all values that were ever received

        :return:
        """

        return self.data

    async def get_init_data(self):
        """
        return only initial data of system

        :return:
        """

        if self.is_init_called:
            raise Exception("init already called")
        self.is_init_called = True

        t = await self.protocol.get_init_data()
        print(len(t))
        self.data.update(t)
        return await self.protocol.get_init_data()

    async def get_curr_data(self):
        """
        catch one new state of system


        :return:
        """


        if not self.is_init_called:
            raise Exception("init was not called")

        while True:

            t = await self.protocol.get_curr_data()

            if not self.notify_small:

                for k, v in t.items():
                    if k in self.data:

                        if self.data[k] != v:
                            self.data.update(t)
                            return t

                    else:
                        self.data.update(t)
                        return t

            else:
                self.data.update(t)
                return t


class AdapterAll(Server):

    def __init__(self, host_name, port, _):
        super().__init__(host_name, port)

        self.protocol = IEC104Protocol()
        self.data = {}

    async def _run(self):
        t = await self.protocol.get_init_data()
        # self.data = dict(self.data, **{var_name: e.payload.data})
        # self.data = dict(self.data, t)
        self.data.update(t)

        print(self.data)

        while True:
            t = await self.protocol.get_curr_data()

            old = {k: v for k, v in self.data.items()}

            self.data.update(t)

            diff = set(old.items()) ^ set(self.data.items())
            print("diff", diff)

            # print(self.data)

    async def get_init_data(self):

        t = await self.protocol.get_init_data()
        print(len(t))
        return await self.protocol.get_init_data()

    async def get_curr_data(self):
        return self.data


async def async_main():
    # protocol = TCPProtocol()
    # protocol.client.start_connection()
    #
    # await protocol.send_data("1.")
    # await protocol.send_data("2.")
    # await protocol.send_data("3.")
    # await protocol.send_data("4.")
    # time.sleep(2)
    #
    # print(f"     {await protocol.get_curr_data()}")
    # print(f"     {await protocol.get_curr_data()}")
    # print(f"     {await protocol.get_curr_data()}")
    # print(f"     {await protocol.get_curr_data()}")
    #
    # protocol.close()

    t = AdapterAll("123.4.5.6", 23, False)
    await t.protocol.connect()

    print(await t.get_init_data())

    # while True:
    #     old = {k: v for k, v in t.data.items()}
    #     print(await t.get_curr_data())
    #     diff = set(old.items()) ^ set(t.data.items())
    #     print("diff", diff)


    await t._run()
    return

    # protocol = WSProtocol()
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


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
