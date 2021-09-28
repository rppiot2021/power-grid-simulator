import socket
import selectors


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self.counter = 0

        print("new message instanced")

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            data = self.sock.recv(4096)
            self._recv_buffer += data
            print("curr recc", self._recv_buffer)
            self.close()

        if mask & selectors.EVENT_WRITE:
            if not self._request_queued:
                self._send_buffer += b"message 6"
                self.counter += 1

                self._request_queued = True

            print("sending", repr(self._send_buffer), "to", self.addr)
            sent = self.sock.send(self._send_buffer)
            self._send_buffer = self._send_buffer[sent:]

            if self._request_queued:
                if not self._send_buffer:
                    events = selectors.EVENT_READ
                    self.selector.modify(self.sock, events, data=self)

    def close(self):
        print("closing connection to", self.addr)

        self.selector.unregister(self.sock)

        self.sock.close()
        self.sock = None


def create_request(value):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(value=value),
    )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


def main():
    global sel
    sel = selectors.DefaultSelector()

    host = "127.0.0.1"
    port = 65432
    value = "needle"

    request = create_request(value)
    start_connection(host, port, request)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:

                print("key", key, "mask", mask)
                message = key.data
                try:
                    message.process_events(mask)
                except:

                    message.close()
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == '__main__':
    main()
