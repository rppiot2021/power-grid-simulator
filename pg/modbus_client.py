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
    def hex_parts_as_int_to_ip(parts):
        ip = ""
        for part in parts:
            first = int(('0x%04x' % part)[:4], 0)
            second = int("0x" + ('0x%04x' % part)[4:], 0)
            ip = ip + f'{first}.{second}.'

        return ip[:-1]

    @staticmethod
    def ip_to_hex_parts_as_int(ip):
        parts = ip.split(".")
        parts = ['0x%02x' % int(i) for i in parts]
        containers = []
        for f, s in zip(parts[0::2], parts[1::2]):
            containers.append(int(f + s[2:], 16))
        return containers

    async def connect(self, ip, slave):
        async with self.tcm_master_connection(ip, 5021) as client:
            print("Successful connection ->", client)
            print()

            payload = "The quick brown fox jumps over the lazy dog"
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

            print("pl int:", r_response)

            pl_hex_split = [('0x%03x' % int(i))[2:] for i in r_response]
            print("hex sp:", pl_hex_split)

            payload_hex = "".join(pl_hex_split)

            payload_hex = payload_hex[:-3] + payload_hex[-3:].strip("0")

            print("pl hex:", payload_hex)

            # tmp = codecs.decode(payload_hex, "hex").decode("utf-8")
            tmp = bytes.fromhex(payload_hex).decode('utf-8')

            print("output:", tmp)


@click.command()
@click.option('--slave-address',
              help='Trafo-stick data to send.',
              default='1.0.0.1')
@click.option('--ip',
              help='Connection ip.',
              default='127.0.0.1')
def main(slave_address, ip):
    click.echo(f"Slave @ {slave_address}!")
    click.echo(f"Ip @ {ip}!")

    modbus_client = ModbusClient()

    result = hat.aio.run_asyncio(modbus_client.connect(ip, slave_address))
    return result


if __name__ == '__main__':
    main()
