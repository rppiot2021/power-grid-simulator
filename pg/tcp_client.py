import json
import io
import struct
import sys
import socket
import selectors
import traceback
from client import Client


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
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

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_binary_content(self):
        content = self.response
        print(f"got response: {repr(content)}")

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()

            print("got", self.response)
        if mask & selectors.EVENT_WRITE:
            self.write()

        return self.response

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

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

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]

        req = {
            "content_bytes": content,
            "content_type": content_type,
            "content_encoding": content_encoding,
        }

        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            # for reqhdr in (
            #     # "byteorder",
            #     "content-length",
            #     # "content-type",
            #     # "content-encoding",
            # ):
            #     if reqhdr not in self.jsonheader:
            #         raise ValueError(f'Missing required header "{reqhdr}".')

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        # Binary or unknown content-type
        self.response = data
        print(
            f'received  response from',
            self.addr,
        )
        self._process_response_binary_content()
        # Close when response has been processed
        self.close()


class TCPClient(Client):

    def __init__(self, domain_name, host):
        super(TCPClient, self).__init__(domain_name, host)

        self.rec_list = []

    def send(self, payload):

        self.driver(payload)

    def receive(self):

        return self.rec_list

    @staticmethod
    def create_request(msg_payload):
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(msg_payload, encoding="utf-8"),
        )

    def start_connection(self, request, sel):
        addr = (self.domain_name, self.port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = Message(sel, sock, addr, request)
        sel.register(sock, events, data=message)

    def driver(self, payload):
        sel = selectors.DefaultSelector()
        request = self.create_request(msg_payload=payload)
        self.start_connection(request, sel)

        try:
            while True:
                events = sel.select(timeout=1)
                print("get map", sel.get_map())
                print("events", events)
                for key, mask in events:
                    print("key", key)
                    print("mask", mask)

                    message = key.data
                    print("message", message)
                    try:
                        result = message.process_events(mask)
                        print("result", result)

                        if result:
                            self.rec_list.append(result)
                    except:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                    print()

                if not sel.get_map():
                    print("not get map")
                    break

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()


def main():
    tcp_client = TCPClient("127.0.0.1", 4567)
    tcp_client.send("tmp 1234567890")
    tcp_client.send("aaaaa bbbb ccc dd e")

    print(tcp_client.receive())


if __name__ == '__main__':
    main()

