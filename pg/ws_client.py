from hat.aio import run_asyncio
from websocket import create_connection

from client import Client


class WSClient(Client):

    def __init__(self, domain_name="127.0.0.1", port=8765):
        super().__init__(domain_name, port)

        # open socket
        self.connection = create_connection(self._get_uri())

    def _get_uri(self):
        return "ws://" + str(self.domain_name) + ":" + str(self.port)

    async def send(self, payload):
        self.connection.send(payload)

    def receive(self):
        # receive from socket
        return self.connection.recv()

async def async_main():
    client = WSClient()

    await    client.send("1")

    print(client.receive())
    await    client.send("2")
    print(client.receive())
    # print(client.receive())
    # print(client.receive())
    # print(client.receive())
    await client.send("3")
    await client.send("4")
    print(client.receive())
    print(client.receive())
    # print(client.receive())
    await client.send("5")
    await client.send("6")
    print(client.receive())

    client.connection.close()


def main():
    run_asyncio(async_main())



if __name__ == '__main__':
    main()
