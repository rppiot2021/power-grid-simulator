from websocket import create_connection
from client import Client

class WSClient(Client):

    def __init__(self, domain_name="127.0.0.1", port=8765):
        super().__init__(domain_name, port)

        # open socket
        self.connection = create_connection(self._get_uri())

    def _get_uri(self):
        return "ws://" + str(self.domain_name) + ":" + str(self.port)

    def send(self, payload):
        self.connection.send(payload)

    def receive(self):
        # receive from socket
        return self.connection.recv()


def main():
    client = WSClient()

    client.send("1")

    print(client.receive())
    client.send("2")
    print(client.receive())
    # print(client.receive())
    # print(client.receive())
    # print(client.receive())
    client.send("3")
    client.send("4")
    print(client.receive())
    print(client.receive())
    # print(client.receive())
    client.send("5")
    client.send("6")
    print(client.receive())

    client.connection.close()


if __name__ == '__main__':
    main()
