import json
import io
import struct
import sys
import socket
import selectors
import traceback
from server import Server
import time
from enum import Enum


class Buffer:
    class BType(Enum):
        SEND = 1
        RECV = 2

    def __init__(self, ):
        self._raw_recv = b""
        self._raw_send = b""
        self._recv = {}
        self._send = {}

    def _from_bytes(self, data):

        if data is None:
            return

        tiow = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", newline="")
        self.response = json.load(tiow)
        tiow.close()

        return self.response


class OldMessage:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

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

    def _recv_raw_msg(self):
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

    def _read(self):
        self._recv_buffer = self._recv_raw_msg()

    def _write(self):
        if self._send_buffer:
            sent = self.sock.sendall(self._send_buffer)
            print("SENT", self._send_buffer)
            self._send_buffer = None

    def _from_bytes(self, data):
        """Receives raw data from TCP connection,and
        transforms it into a dictionary object

        Args:
            data (bytes): bytes literal,input from TCP

        Returns:
            dict: dictionary representation of the input
        """
        if data is None:
            return

        tiow = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", newline="")
        self.response = json.load(tiow)
        tiow.close()

        return self.response

    def _to_bytes(self, data):
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

    def _create_response(self):
        if self._recv_buffer is not None:
            response = {
                "content": "First 10 bytes of request: " +
                           str(self._recv_buffer['client_sent'])[:10]
            }
            return response
        return {"content": "No bytes sent"}

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:

            self.read()
            try:
                self._set_selector_events_mask("w")
            except:
                pass

        if mask & selectors.EVENT_WRITE:

            self.write()
            try:
                self._set_selector_events_mask("r")
            except:
                pass

    def process_message(self,msg):
        print("RECEIVED MESSAGE", msg)

        if msg is not None:
            if msg['client_sent'] == "CLOSE":
                self.close()



    def read(self):
        msg = self._recv_raw_msg()
        msg = self._from_bytes(msg)

        self._recv_buffer = msg

        self.process_message(msg)



    def write(self):
        response = self._create_response()

        self._send_buffer = self._to_bytes(response)
        print("created_message", self._send_buffer)

        self._write()


    def close(self):
        print("closing connection to", self.addr, "\n")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except AttributeError:
            print("sock is none")
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None


class TCPServer(Server):

    def __init__(self, domain_name, port):
        super(TCPServer, self).__init__(domain_name, port)
        self.conn =None

        self.sel = selectors.DefaultSelector()
        address = (self.host_name, self.port)
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind(address)
        lsock.listen()
        print("listening on", address)
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:

                events = self.sel.select(timeout=1)

                for key, mask in events:

                    if key.data is None:

                        self.accept_wrapper(key.fileobj)
                    else:

                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()




        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        if not self.conn:
            self.conn, addr = sock.accept()  # Should be ready to read
            print("accepted connection from", addr)
            self.conn.setblocking(False)
            message = OldMessage(self.sel, self.conn, addr)
            self.sel.register(self.conn, selectors.EVENT_READ, data=message)


def main():
    TCPServer("127.0.0.1", 4567)


if __name__ == '__main__':
    main()
