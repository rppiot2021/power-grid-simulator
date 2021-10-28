import hat.drivers.modbus as mod
import hat.drivers.tcp
from hat.aio import run_asyncio

from protocols.util.server import Server


class ModbusServer(Server):

    async def write(
            self,
            slave,
            device_id,
            data_type,
            start_address,
            values
    ):
        print("write ", slave, device_id, data_type)

        for idx, val in enumerate(values):
            self.container[start_address + idx] = val

        # return

    async def write_mask(self):
        print("write mask")
        breakpoint()

    async def read(
            self,
            slave,
            device_id,
            data_type,
            start_address,
            quantity=0
    ):
        print("read ", slave, device_id, data_type)
        # print(self.container[start_address:(int(start_address)+quantity)])
        return self.container[start_address:(int(start_address) + quantity)]

    async def slave_cb(self, slave):
        # print("Slave callback ", slave)
        pass


async def init_modbus_server():
    server = ModbusServer("127.0.0.1", 5021)

    server.container = [0] * (2 ** 16)

    server.address = hat.drivers.tcp.Address(server.host_name, server.port)

    s = await mod.create_tcp_server(
        mod.ModbusType.TCP,
        server.address,
        server.slave_cb,
        server.read,
        server.write,
        server.write_mask
    )

    print("Slave created -> ", s)
    await s.wait_closing()


def main():
    run_asyncio(init_modbus_server())


if __name__ == '__main__':
    main()
