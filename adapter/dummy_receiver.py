import sys
import os
sys.path.insert(0, os.getcwd() + '/../')
sys.path.insert(0, os.getcwd() + '/../protocols')


from hat.aio import run_asyncio

from protocols.ws.ws_client import WSClient

async def async_main():
    client = WSClient()

    print(client.receive())

    client.connection.close()


def main():
    run_asyncio(async_main())



if __name__ == '__main__':
    main()
