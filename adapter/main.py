"""
utils for address translations
"""

from hat.aio import run_asyncio
from hat.drivers import iec104
from collections import defaultdict
from hat.drivers import iec104
import asyncio

ADDRESSES = []


class Address:

    @staticmethod
    def get_formatted_name(asdu_address, io_address):
        return str(asdu_address) + ";" + str(io_address)

    def __init__(self, asdu_address, io_address):
        self.asdu_address = asdu_address
        self.io_address = io_address

    def __str__(self):
        return f"{self.asdu_address=} {self.io_address=}"

    def formatted_name(self):
        return Address.get_formatted_name(self.asdu_address, self.io_address)


async def init_data_manager():
    data_manager = DataManager(
        domain_name="127.0.0.1",
        port=19999,
        reconnect_delay=3,
        send_retry_count=3
        )

    data_manager.connection = await data_manager._connect()

    return data_manager


class DataManager:

    def __init__(self, domain_name, port, reconnect_delay, send_retry_count):
        """
        @reconnect_delay delay for this much seconds before retrying to connect
        @send_retry_count try to send this much times command to simulation
        """

        self.domain_name = domain_name
        self.port = port
        self.reconnect_delay = reconnect_delay
        self.send_retry_count = send_retry_count

    async def get_init_data(self):
        raw_data = await self.connection.interrogate(asdu_address=65535)

        return {(i.asdu_address, i.io_address): i.value for i in raw_data}

    async def get_curr_data(self):
        raw_data = await self.connection.receive()

        return {(i.asdu_address, i.io_address): i.value for i in raw_data}

    async def _connect(self):
        address = iec104.Address(self.domain_name, self.port)

        while True:

            try:
                connection = await iec104.connect(address)
                return connection

            except ConnectionRefusedError:
                for i in range(self.reconnect_delay):
                    print("trying to reconnect in", self.reconnect_delay - i)
                    await asyncio.sleep(1)

                print("reconnecting\n")

    async def send_data(self, value, asdu, io):

        print(asdu, io, value, type(value))

        try:
            asdu = int(asdu)
            io = int(io)
            # todo fix this in other part
            val = iec104.common.SingleValue(1 if value == "closed" else 0)
        except ValueError:
            return

        command = iec104.Command(
            value=val,
            asdu_address=asdu,
            io_address=io,
            action=iec104.Action.EXECUTE,
            time=None,
            qualifier=1
        )

        print("command", command)

        result = await self.connection.send_command(command)

        for _ in range(self.send_retry_count):
            if result:
                return

            result = await connection.send_command(command)

        raise Exception("can not send command")


async def async_main():

    data_manager = await init_data_manager()

    t = await data_manager.get_init_data()
    print("init data")
    [print(i) for i in t.items()]

    t = await data_manager.get_curr_data()
    print("curr data")
    [print(i) for i in t.items()]

    # todo handle other cases
    await data_manager.send_data("closed", 30, 0)
    print("data sent")

    while True:
        t = await data_manager.get_curr_data()
        print("curr data")
        [print(i) for i in t.items()]


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()


