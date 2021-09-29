import socket
import selectors


class Client:

    def driver(self, host, port, payload=None):

        sel = selectors.DefaultSelector()

        address = (host, port)
        print("starting connection to", address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(address)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = self.Message(sel, sock, address)
        sel.register(sock, events, data=message)

        self.message = message

        if payload:
            message.set_data(payload)

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

    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port

        self.driver(host, port)


    def send(self, payload):
        print("prepare", payload)

        self.driver(self.host, self.port, payload)

        # self.message.set_data(payload)
        #
        # self.message.process_events(mask=0)

    class Message:

        def set_data(self, data):
            self.data_to_send = data

        def __init__(self, selector, sock, address):
            self.selector = selector
            self.sock = sock
            self.address = address
            self._receive_buffer = b""
            self._send_buffer = b""
            self._request_queued = False
            self.counter = 0
            self.data_to_send = "f"

            print("new message instanced")

        def process_events(self, mask):
            if mask & selectors.EVENT_READ:
                data = self.sock.recv(4096)
                self._receive_buffer += data
                print("received", self._receive_buffer)
                self.close()

            if mask & selectors.EVENT_WRITE:
                if not self._request_queued:
                    self._send_buffer += b"tmp _ " \
                                         + str.encode(self.data_to_send)

                    # + (self.counter).to_bytes(2, byteorder="big") \

                    self.counter += 1

                    print("sending", self._send_buffer)
                    # print(type(self._send_buffer))

                    self._request_queued = True

                print("sending", repr(self._send_buffer), "to", self.address)
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]

                if self._request_queued:
                    if not self._send_buffer:
                        events = selectors.EVENT_READ
                        self.selector.modify(self.sock, events, data=self)

                    # self._request_queued = False


        def close(self):
            print("closing connection to", self.address)

            self.selector.unregister(self.sock)

            self.sock.close()
            self.sock = None


def main():

    client = Client()
    client.send("Everest")
    client.send("Aconcagua")
    client.send("McKinley")
    client.send("Kilimanjaro")
    client.send("Elbrus")
    client.send("Vinson")
    client.send("Carstensz Pyramid")


if __name__ == '__main__':
    main()
