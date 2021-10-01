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
        return self._recv_list

    async def _run(self):
        print("run")

        ip = "127.0.0.1"

        print("creating client")

        client = await mod.create_tcp_master(
                mod.ModbusType.TCP,
                hat.drivers.tcp.Address(ip, 5021))

        print("getting response")

        r_response = await client.read(
            1,
            DataType.HOLDING_REGISTER,
            40000,
            # len
            100
        )

        print("repsonse", r_response)

        self._recv_list.append(ModbusClient.split_int_to_str(r_response))

        client.close()

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

        # print(len(payload_hex) % 3)

        three_div_count = len(payload_hex) % 3

        if not three_div_count == 0:
            # print(three_div_count)

            to_add = 3 - three_div_count

            payload_hex = to_add * "0" + payload_hex

        n = 3
        pl_hex_split = [payload_hex[i:i + n] for i in
                        range(0, len(payload_hex), n)]

        # before_filling = len(pl_hex_split[-1])
        #
        # pl_hex_split[-1] = pl_hex_split[-1].zfill(3)
        #
        # after_filling = len(pl_hex_split[-1])

        injected_zero_count = 0
        # injected_zero_count = after_filling - before_filling
        # print("injected", injected_zero_count)
        print("hex sp:", pl_hex_split)

        pl_int_split = [int("0x" + i, 16) for i in pl_hex_split]

        print("pl int:", pl_int_split)

        return pl_int_split, injected_zero_count

    @staticmethod
    def split_int_to_str(payload, injected_zero_count):
        # print("pl int:", payload)

        pl_hex_split = [('0x%03x' % int(i))[2:] for i in payload]
        # print("hex sp:", pl_hex_split)

        payload_hex = "".join(pl_hex_split)

        if not injected_zero_count == 0:
            payload_hex = payload_hex[:-3] + payload_hex[-3:].strip("0")

        # print("pl hex:", payload_hex)

        output = bytes.fromhex(payload_hex).decode('utf-8')

        return output

    async def connect(self, ip, payload):
        async with self.tcm_master_connection(ip, 5021) as client:
            # print("Successful connection ->", client)
            print()
            # print("pyl", payload)

            # payload = "The quick brown fox jumps over the lazy dog"
            pl_int_split, injected_zero_count = self.str_to_split_int(payload)

            '''
                header
                    message len
            '''

            # header = ModbusClient.str_to_split_int(str(len(pl_int_split)))
            #
            # print("header", header)

            header = [
                len(pl_int_split),
                # injected_zero_count
            ]

            header_len = len(header)

            msg = header + pl_int_split

            # print("sending", msg)

            w_response = await client.write(
                1,
                DataType.HOLDING_REGISTER,
                40000,
                msg
            )

            if w_response:
                print("Write error", w_response.name)
                return

            # print(80 * "-")
            # ///////////////////////////////////////////////////////////////////////////////////////////////////

            r_header = await client.read(
                1,
                DataType.HOLDING_REGISTER,
                40000,
                header_len
            )


            # 23466 -> 234 066
            # 234066 -> 234 066


            # print("r header", r_header)

            expected_len = r_header[0]
            # injected_zero_count = r_header[1]

            r_body = await client.read(
                1,
                DataType.HOLDING_REGISTER,
                40000 + header_len,
                expected_len
            )

            # print("r body  ", r_body)

            expected_len = ModbusClient.split_int_to_str(r_body, injected_zero_count=0)

            print("msg", expected_len)


            # r_response = await client.read(
            #     1,
            #     DataType.HOLDING_REGISTER,
            #     40000,
            #     self.max_msg_len
            # )
            #
            # print("rec   :", r_response)
            # print(ModbusClient.split_int_to_str(r_response))
            #
            # print(80 * "-")
            # print(80 * "-")
            # print(80 * "-")
            #
            # response_buffer = []
            #
            # offset = 40000
            #
            # while True:
            #
            #     r_response = await client.read(
            #         1,
            #         DataType.HOLDING_REGISTER,
            #         offset,
            #         1
            #     )
            #
            #     r_response = r_response[0]
            #
            #     if r_response == 0:
            #         break
            #
            #     offset += 1
            #
            #     response_buffer.append(r_response)
            #
            # print(response_buffer)
            #
            # print(ModbusClient.split_int_to_str(response_buffer))
            #
            # # output = self.split_int_to_str(r_response)
            # # print("output:", output)


import random
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)

    return result_str

async def async_main():
    domain_name = "127.0.0.1"
    slave_address = '1.0.0.1'

    modbus_client = ModbusClient()
    modbus_client._recv_list = []

    modbus_client.max_msg_len = 100

    # modbus_client._group = hat.aio.Group()
    # modbus_client._group.spawn(modbus_client._run)

    await modbus_client.connect(domain_name, "tmp val 1")
    await modbus_client.connect(domain_name, "tmp val 2")
    await modbus_client.connect(domain_name, "fnfofsonifni")
    await modbus_client.connect(domain_name, "tmpffff val 2")

    msg = "xjfnwagxoeplewhawikscfoqlvvclombqwfklumoywsxlawdrjasosxozibbxhjlp"
    await modbus_client.connect(domain_name, msg)

    for i in range(100):

        await modbus_client.connect(domain_name, get_random_string(random.randint(0, 100)))


    # await asyncio.sleep(1)
    # await asyncio.sleep(1)
    # await asyncio.sleep(5)
    # await asyncio.sleep(1)
    # await asyncio.sleep(1)
    # await asyncio.sleep(1)

    # result = hat.aio.run_asyncio(modbus_client.connect(domain_name, slave_address))
    # return result

    # print("get", modbus_client.receive())

    print()
    print("responding")

    [print(i) for  i in modbus_client.receive()]

@click.command()
@click.option('--slave-address', default='1.0.0.1')
@click.option('--domain-name',default='127.0.0.1')
@click.option("--port", default="5021")
def main(slave_address, domain_name, port):

    hat.aio.run_asyncio(async_main())

if __name__ == '__main__':
    main()
