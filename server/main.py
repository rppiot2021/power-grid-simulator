import sys
import os

sys.path.insert(0, os.getcwd() + '/')
sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../adapter')

from hat.aio import run_asyncio

from protocols.modbus.modbus_server import ModbusServer


async def async_main():
    modbus_server = init_modbus_server()
    print(modbus_server)


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
