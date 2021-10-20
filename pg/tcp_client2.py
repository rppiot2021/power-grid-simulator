import selectors
import socket
from abc import ABC

from TCPBuffer import Buffer, MessageType
from TCPConnection import TCPConnection
from client import Client


class TCPClient(Client):

    def __init__(self, domain_name, host):
        print("TCPClient init")
        super(TCPClient, self).__init__(domain_name, host)

        self.buffer = Buffer()
        self.rec_list = []

    async def connect(self):
        self.start_connection()

    async def close(self):
        self.close_connection()
        # self.close()

    def send(self, payload, data_type=MessageType.CONTENT):
        self.tcp.write(payload, data_type=data_type)

    def receive(self):

        if not self.sel:
            print("connection not started")
            return
        try:
            self.tcp.read()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

        if len(self.buffer.return_history()) == 0:
            return {}
        return self.buffer.return_history().pop()

    def create_request(self, msg_payload):
        return self.buffer.create_response()

    def close_connection(self):
        self.tcp.remote_close()

    def connect_socket(self, address):
        """Define new Socket object, connect to it with address and port"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(address)
        return sock

    def start_connection(self):
        self.sel = selectors.DefaultSelector()

        self.address = (self.domain_name, self.port)
        print("starting connection to", self.address)

        self.sock = self.connect_socket(self.address)
        self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.tcp = TCPConnection(self.sel, self.sock, self.address,
                                 self.buffer)

    def register_message(self, sel):
        sel.register(self.sock, self.events, data=self.tcp)

    def driver(self):
        # todo continuous read
        print("driver start")
        if not self.sel:
            print("connection not started")
            return

        # request = self.create_request(msg_payload=payload)
        # self.register_message(self.sel, request)

        try:
            self.tcp.read()
            # print("events start ")
            # events = self.sel.select(timeout=1)
            # # selectors don't work outside loop
            # print("events end ")
            #
            # print("events", events)
            # for key, mask in events:
            #     print("key", key, mask)
            #     # request = self.create_request(msg_payload=payload)
            #     message = key.data
            #
            #     result = message.process_events(mask)
            #
            #     if result:
            #         breakpoint()
            #         self.rec_list.append(result)
            #
            #         # message.close()
            #
            # if not self.sel.get_map():
            #     return

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

#
# def main():
#     tcp_client = TCPClient("127.0.0.1", 4567)
#     tcp_client.send("tmp 1234567890")
#     tcp_client.send("aaaaa bbbb ccc dd e")
#
#     # print(tcp_client.receive())
#
#
# if __name__ == '__main__':
#     main()
