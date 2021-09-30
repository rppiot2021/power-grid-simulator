import hat
import click
import ipaddress
import hat.drivers.tcp
import hat.drivers.modbus as mod
from hat.drivers.modbus.common import DataType
from contextlib import asynccontextmanager


# import traceback
# import urllib
# from urllib.parse import urlparse

from client import Client


class ModbusClient(Client):

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

    def hex_parts_as_int_to_ip(self, parts):
        ip = ""
        for part in parts:
            first = int(('0x%04x' % part)[:4],0)
            second = int("0x" + ('0x%04x' % part)[4:],0)
            ip = ip + f'{first}.{second}.'

        return ip[:-1]

    def ip_to_hex_parts_as_int(self, ip):
        parts = ip.split(".")
        parts = ['0x%02x' % int(i) for i in parts]
        containers = []
        for f, s in zip(parts[0::2], parts[1::2]):
            containers.append(int(f+s[2:],16))
        return containers

    async def connect(self, ip, slave):
        async with self.tcm_master_connection(ip, 5021) as client:
            print("Successful connection ->", client)

            parts = self.ip_to_hex_parts_as_int(slave)
            pr = self.print_table()

            pr.print_row("original", slave)
            pr.print_row("parts", str(parts))

            pr.print_space()

            response = await client.write(1,
                                          DataType.HOLDING_REGISTER,
                                          40000,
                                          parts)

            if response is not None:
                print("Write error", response.name)
                return

            response = await client.read(1,
                                         DataType.HOLDING_REGISTER,
                                         40000,
                                         2)
            pr.print_row("Decoded", str(response))
            pr.print_row("Response",self.hex_parts_as_int_to_ip(response))

            pr.end()

    class print_table:
        def __init__(self):
            self.start = False

        def print_row(self, info, data):
            if not self.start:
                print(f'╔{"═" * 10:10}╤{"═" * 15:15}╗')
            self.start = True
            print(f'║{info:10}│{data:>15}║')

        def print_space(self):
            print(f'╟{"─" * 10:10}┼{"─" * 15:15}╢')

        def end(self):
            print(f'╚{"═" * 10:10}╧{"═" * 15:15}╝')
            self.start = False


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

