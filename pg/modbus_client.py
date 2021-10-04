from contextlib import asynccontextmanager
import click
import hat
import hat.drivers.modbus as mod
import hat.drivers.tcp
from hat.drivers.modbus.common import DataType
from client import Client

import random
import string


class ModbusClient(Client):

    def receive(self):
        return self.register_data

    async def _run(self):

        client = await mod.create_tcp_master(
                mod.ModbusType.TCP,
                hat.drivers.tcp.Address(self.domain_name, self.port))

        while True:
            is_sth_changed = False

            for j in range(2):

                for i in range(9):
                    address = i * 1000

                    r_header = await client.read(
                        1,
                        DataType.HOLDING_REGISTER,
                        address,
                        self.header_len
                    )

                    expected_len = r_header[0]

                    r_body = await client.read(
                        1,
                        DataType.HOLDING_REGISTER,
                        address + self.header_len,
                        expected_len
                    )

                    print("read; address:", address, r_header, r_body)

                    msg = self.split_int_to_str(r_body)

                    print("plaintext:", msg)

                    if address not in self.register_data or \
                            not self.register_data[address] == msg:

                        is_sth_changed = True
                        self.control_dict[address].append(msg)
                        self.register_data[address] = msg

                    else:
                        print("already read this, not updating")

            if not is_sth_changed:
                print("nothing changed in two iters, closing")
                break

        client.close()

    @asynccontextmanager
    async def tcm_master_connection(self):
        client = None
        try:
            client = await mod.create_tcp_master(
                mod.ModbusType.TCP,
                hat.drivers.tcp.Address(self.domain_name, self.port))

            yield client
        finally:
            if client:
                client.close()

    def str_to_split_int(self, payload):
        # print("input :", payload)

        # todo test whole sys with diff vals

        payload_hex = payload.encode("utf-8").hex()
        # print("hex   :", payload_hex)

        three_div_count = len(payload_hex) % self.fragment_len

        if not three_div_count == 0:

            to_add = self.fragment_len - three_div_count

            payload_hex = to_add * "0" + payload_hex

        n = self.fragment_len
        pl_hex_split = [payload_hex[i:i + n] for i in
                        range(0, len(payload_hex), n)]

        # print("hex sp:", pl_hex_split)

        pl_int_split = [int("0x" + i, 16) for i in pl_hex_split]

        # print("pl int:", pl_int_split)

        return pl_int_split

    def split_int_to_str(self, payload):
        # print("pl int:", payload)

        # fixme what is 2
        pl_hex_split = [('0x%03x' % int(i))[2:] for i in payload]
        # print("hex sp:", pl_hex_split)

        payload_hex = "".join(pl_hex_split)
        # print("tmp   :", payload_hex)

        payload_hex = payload_hex[:self.fragment_len].lstrip("0") + payload_hex[self.fragment_len:]

        # print("pl hex:", payload_hex)

        try:
            output = bytes.fromhex(payload_hex).decode('utf-8')
        except:
            print("err on", payload_hex)
            raise ValueError("err")

        return output

    async def send(self, payload):
        async with self.tcm_master_connection() as client:
            # print("Successful connection ->", client)
            # print()

            address = payload[0]
            payload = payload[1]

            print("\twriting; adr:", address, ", payload:", payload)

            pl_int_split = self.str_to_split_int(payload)

            '''
                header
                    message len
            '''

            header = [
                len(pl_int_split),
                # injected_zero_count
            ]

            msg = header + pl_int_split

            w_response = await client.write(
                1,
                DataType.HOLDING_REGISTER,
                # 40000,
                address,
                msg
            )

            # print("\t", msg)

            if w_response:
                print("Write error", w_response.name)
                return


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


async def async_main(domain_name, port):

    modbus_client = ModbusClient()

    modbus_client.register_data = {}
    modbus_client.domain_name = domain_name
    modbus_client.max_msg_len = 100
    # how many things are in it
    modbus_client.header_len = 1
    modbus_client.fragment_len = 3
    modbus_client.port = int(port)

    from collections import defaultdict
    modbus_client.control_dict = defaultdict(list)

    modbus_client._group = hat.aio.Group()
    modbus_client._group.spawn(modbus_client._run)


    dummy_data = {
        0: "tmp val 1",
        1000: "tmp val 2",
        2000: "fnfofsonifni",
        3000: "tmpffff val 2",
        4000: "xjfnwagxoeplewhawikscfoqlvvclombqwfklumoywsxlawdrjasosxozibbxhjlp",
        5000: "pwzwggoyuugtftmoksogwhkkduzcwccludztazxhyfautrfgrjjokfv",
        6000: "fqvnbusfjhzgkhpqankvuehugpyeveutimdpqqsvwzhvbcrtlmgolxudixeehlzqsmeunuxfwhgnxpbhkkvrocbbnjvhvmycxcykwalgptecjemjdrrjcyqzlqxvxjaqxbjlvywziujduzagoacuznnxelzwpzzwcrsxgkmomkevinciahyazjvxatzre",
        7000: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }

    for adr, msg in dummy_data.items():
        await modbus_client.send((adr, msg))


    dummy_data = {
        0: "tmp val 1",
        1000: "kogkdbloynafmrzmhnpfjsktklnqhqxajroplzknitnafxoscefdarfnrellivzhgeqjmpspklnpslkdneplxaeshfqslzovgotvpghuqiyzwaqjhekcdavklhegxog",
        2000: "kfkvetettgydnuzpkorhxeulrpruzocwpkilhcbdlsxnyhztlwgbkvvsvhtwget",
        3000: "lw",
        4000: "beiqeshxhgkxwbfapcaeucbpevdsddysaejocsegpawunsedyauicpmukgxqzrvqiolbhjxfzwvkkv",
        5000: "zsczvqqkgewnjgexwepqeyvdfdiiqaoptepqiwhityvkysmynsgbqppdxnffdaadcriqaozqogwjtlxlyngxuhly",
        6000: "pecemykhwrekjmfnjpfbsaukyagofjepbtzopldarypnojgjfgzxilllbguotfodhycembqixsejksybugnrqyxfulxhxmowcjzbtodywrvzsveobgrkzwx",
        7000: "pfgwizsetdqubcierrjlwgajgvtkrcocjretuaouel",
    }

    for adr, msg in dummy_data.items():
        await modbus_client.send((adr, msg))

    for j in range(4):
        for i in range(9):
            await modbus_client.send((i * 1000, get_random_string(random.randint(0, 150))))

    print("\nreceive queue")
    [print(i) for i in modbus_client.control_dict.items()]

    print("\ntrue data")
    [print(i) for i in modbus_client.register_data.items()]

    await modbus_client._group.wait_closed()


@click.command()
@click.option('--domain-name',default='127.0.0.1')
@click.option("--port", default="5021")
def main(domain_name, port):

    hat.aio.run_asyncio(async_main(domain_name, port))


if __name__ == '__main__':
    main()
