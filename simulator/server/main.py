import sys
import os

from hat.aio import run_asyncio
from simulator.protocols.modbus.modbus_server import init_modbus_server


sys.path.insert(0, os.getcwd() + '/')
sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../adapter')


async def async_main():
    modbus_server = init_modbus_server()
    print(modbus_server)


def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
