import codecs

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
            first = int(('0x%04x' % part)[:4],0)
            second = int("0x" + ('0x%04x' % part)[4:],0)
            ip = ip + f'{first}.{second}.'

        return ip[:-1]

    @staticmethod
    def ip_to_hex_parts_as_int( ip):
        parts = ip.split(".")
        parts = ['0x%02x' % int(i) for i in parts]
        containers = []
        for f, s in zip(parts[0::2], parts[1::2]):
            containers.append(int(f+s[2:],16))
        return containers

    async def connect(self, ip, slave):
        async with self.tcm_master_connection(ip, 5021) as client:
            print("Successful connection ->", client)

            # parts = self.ip_to_hex_parts_as_int(slave)
            #
            #
            # print("sending", parts)

            parts = "The quick brown fox jumps over the lazy dog".encode("utf-8").hex()

            # org_p = parts
            # parts = [i for i in ]
            print("hex", parts)
            new_p = []
            b = []
            for i in parts:
                b.append(i)

                if len("".join([i for i in b])) == 3:
                    new_p.append("".join([i for i in b]))

                    b = []

            if b == []:
                pass
            if len(b) == 1:
                new_p.append("00"+"".join(b))
            elif len(b) == 2:
                new_p.append("0" +"".join(b))

            # new_p.append("".join(b))

            print("sep", new_p)
            new_p = [int("0x"+ i, 16) for i in new_p]

            # print("new parts", new_p)

            parts = new_p

            print("parts", parts)
            # print(parts)
            pr = self.TablePrinter()

            # pr.print_row("original", slave)
            # pr.print_row("parts", str(parts))
            #
            # pr.print_space()

            response = await client.write(1,
                                          DataType.HOLDING_REGISTER,
                                          40000,
                                          parts)

            print(80 * "-")

            if response is not None:
                print("Write error", response.name)
                return

            response = await client.read(1,
                                         DataType.HOLDING_REGISTER,
                                         40000,
                                         len(parts))


            # pr.print_row("Decoded", str(response))
            # pr.print_row("Response",self.hex_parts_as_int_to_ip(response))
            #
            # pr.end()

            print("p new",str(response))

            print(parts == response)
            # print("".join([str(i) for  i in response]))

            print(len(response))

            response =[('0x%03x' % int(i))[2:] for i in response]

            print(len(response))
            print("sep", response)

            c = "".join([i for i in response])
            print("hex", c)

            last_three = c[-3:]
            while last_three[0] == "0":
                last_three = last_three[1:]

            print("last", last_three)


            c = c[:-3] + last_three
            print(c)

            # print(c.decode("hex"))
            print(codecs.decode(c, "hex").decode("utf-8"))
            # print(org_p)
            # print(response)

            # print("response,", response)


    class TablePrinter:
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

