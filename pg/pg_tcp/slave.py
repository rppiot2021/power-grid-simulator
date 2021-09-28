import socket
import selectors


class Client:

    def __init__(self, host="127.0.0.1", port=65432):
        
        sel = selectors.DefaultSelector()

        address = (host, port)
        print("starting connection to", address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(address)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = self.Message(sel, sock, address)
        sel.register(sock, events, data=message)

        try:
            while True:
                events = sel.select(timeout=1)

                for key, mask in events:
                    message = key.data
                    message.process_events(mask)

                if not sel.get_map():
                    break

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()

    class Message:
        def __init__(self, selector, sock, address):
            self.selector = selector
            self.sock = sock
            self.address = address
            self._receive_buffer = b""
            self._send_buffer = b""
            self._request_queued = False
            self.counter = 0

            print("new message instanced")

        def process_events(self, mask):
            if mask & selectors.EVENT_READ:
                data = self.sock.recv(4096)
                self._receive_buffer += data
                print("received", self._receive_buffer)
                self.close()

            if mask & selectors.EVENT_WRITE:
                if not self._request_queued:
                    self._send_buffer += b"message 6"
                    self.counter += 1

                    self._request_queued = True

                print("sending", repr(self._send_buffer), "to", self.address)
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]

                if self._request_queued:
                    if not self._send_buffer:
                        events = selectors.EVENT_READ
                        self.selector.modify(self.sock, events, data=self)

        def close(self):
            print("closing connection to", self.address)

            self.selector.unregister(self.sock)

            self.sock.close()
            self.sock = None


def main():

    Client()


if __name__ == '__main__':
    main()
