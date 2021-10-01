import asyncio
import codecs
from contextlib import asynccontextmanager

import click
import hat
import hat.drivers.modbus as mod
import hat.drivers.tcp
from hat.drivers.modbus.common import DataType

from client import Client


# import traceback
# import urllib
# from urllib.parse import urlparse


class ModbusClient(Client):

    def send(self, payload):
        return

    def receive(self):
        return

    async def _run(self):
        print("run")

        async with self.tcm_master_connection("1.0.0.1", 5021) as client:
            print("getting response")

            r_response = await client.read(
                1,
                DataType.HOLDING_REGISTER,
                40000,
                len(pl_int_split)
            )

            print("response", r_response)

    @asynccontextmanager
    async def tcm_master_connection(self, ip, port):
        client = None
        try:
            client = await mod.create_tcp_master(
                mod.ModbusType.TCP,
                hat.drivers.tcp.Address(ip, 5021))

            yield client
        finally:
            if client:
                client.close()

    @staticmethod
    def str_to_split_int(payload):
        print("input :", payload)

        payload_hex = payload.encode("utf-8").hex()
        print("hex   :", payload_hex)

        n = 3
        pl_hex_split = [payload_hex[i:i + n] for i in
                        range(0, len(payload_hex), n)]

        print("hex sp:", pl_hex_split)

        pl_hex_split[-1] = pl_hex_split[-1].zfill(3)

        pl_int_split = [int("0x" + i, 16) for i in pl_hex_split]
        print("pl int:", pl_int_split)

        return pl_int_split

    @staticmethod
    def split_int_to_str(payload):
        print("pl int:", payload)

        pl_hex_split = [('0x%03x' % int(i))[2:] for i in payload]
        print("hex sp:", pl_hex_split)

        payload_hex = "".join(pl_hex_split)

        payload_hex = payload_hex[:-3] + payload_hex[-3:].strip("0")

        print("pl hex:", payload_hex)

        output = bytes.fromhex(payload_hex).decode('utf-8')

        return output

    async def connect(self, ip, slave):
        async with self.tcm_master_connection(ip, 5021) as client:
            print("Successful connection ->", client)
            print()

            payload = "The quick brown fox jumps over the lazy dog"
            pl_int_split = self.str_to_split_int(payload)

            w_response = await client.write(
                1,
                DataType.HOLDING_REGISTER,
                40000,
                pl_int_split
            )

            if w_response:
                print("Write error", w_response.name)
                return

            print(80 * "-")

            r_response = await client.read(
                1,
                DataType.HOLDING_REGISTER,
                40000,
                len(pl_int_split)
            )

            output = self.split_int_to_str(r_response)
            print("output:", output)


        # await asyncio.sleep(5)


async def async_main():

    modbus_client = ModbusClient()

    modbus_client._group = hat.aio.Group()
    modbus_client._group.spawn(modbus_client._run)

    # result = hat.aio.run_asyncio(modbus_client.connect(domain_name, slave_address))
    # return result

@click.command()
@click.option('--slave-address', default='1.0.0.1')
@click.option('--domain-name',default='127.0.0.1')
@click.option("--port", default="5021")
def main(slave_address, domain_name, port):

    hat.aio.run_asyncio(async_main())

if __name__ == '__main__':
    main()
