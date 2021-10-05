import json
import io
import struct
import sys
import socket
import selectors
import traceback
from client import Client
import time


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self.response = None

    def __str__(self):
        return str(self._recv_buffer) + ";" + str(self._send_buffer)

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def __recv_raw_msg(self):
        """In charge of receiving messages from the connection.
        Function will use first 4 bytes and interpret it as
        message length. Message is located in bytes that follow.

        Returns:
            bytes: raw input stream from TCP connection
        """

        raw_message_length = self.sock.recv(4)  # --> b'\x00\x08\xf8\x93'

        if not raw_message_length:
            return None

        # unpack integer holding the size of message
        n = struct.unpack(">I", raw_message_length)[0]  # --> 587923

        full_msg = b""
        while len(full_msg) < n:
            packet = self.sock.recv(
                n - len(full_msg)
            )  # <--make sure u don't receive more bytes than message length
            if not packet:
                break
            full_msg = full_msg + packet

        return full_msg

    def _from_bytes(self, data):
        """Receives raw data from TCP connection,and
        transforms it into a dictionary object

        Args:
            data (bytes): bytes literal,input from TCP

        Returns:
            dict: dictionary representation of the input
        """

        tiow = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", newline="")
        self.response = json.load(tiow)
        tiow.close()

        return self.response

    @staticmethod
    def _to_bytes(data):
        """Transforms data into format compatible
        for TCP transmission.

        Args:
            data (dict): dictionary object that you want to

        Returns:
            bytes: representation of the object in bytes format
        """
        content_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        n = struct.pack(">I", len(content_bytes))

        return n + content_bytes

    def read(self):
        print("read::started")
        # self._read()
        msg = self.__recv_raw_msg()
        print(msg)
        self.response = self._from_bytes(msg)
        print("read::done")

    def write(self):
        print("write::started")
        req = {"client_sent": str(self.request)}

        self._send_buffer = self._to_bytes(req)
        print("TO_SEND", req)
        print("TO_SEND", self._send_buffer)

        self.sock.sendall(self._send_buffer)
        print("write::done")

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            print("process_ev::READ")
            self.read()

            # print("got", self.response)
        if mask & selectors.EVENT_WRITE:
            print("process_ev::WRITE")
            self.write()

            try:
                self._set_selector_events_mask("r")
            except:
                pass

        return self.response

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None


class TCPClient(Client):

    def __init__(self, domain_name, host):
        super(TCPClient, self).__init__(domain_name, host)

        self.rec_list = []

    def send(self, payload):

        return self.driver(payload)


    def receive(self):

        return self.rec_list

    @staticmethod
    def create_request(msg_payload):
        return msg_payload

    def close_connection(self):
        pass


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


    def register_message(self, sel, request):
        message = Message(sel, self.sock, self.address, request)
        sel.register(self.sock, self.events, data=message)

    def driver(self, payload):
        print("driver start")
        if not self.sel:
            print("connection not started")
            return

        request = self.create_request(msg_payload=payload)
        self.register_message(self.sel, request)

        try:

            while True:
                events = self.sel .select(timeout=1)
                for key, mask in events:
                    p = yield payload
                    print(p,payload)
                    request = self.create_request(msg_payload=p)
                    message = key.data
                    try:
                        result = message.process_events(mask)

                        if result:
                            self.rec_list.append(result)

                    except:
                        message.close()


                if not self.sel .get_map():
                    break


        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel .close()


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
