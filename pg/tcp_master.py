import socket
import selectors
import traceback


class Server:

    class Message:
        def __init__(self, selector, sock, addr):
            self.selector = selector
            self.sock = sock
            self.addr = addr
            self._recv_buffer = b""
            self._send_buffer = b""

        def process_events(self, mask):

            data = self.sock.recv(4096)
            self._recv_buffer += data

            print("recv buffer", self._recv_buffer)
            print(len(self._recv_buffer))
            # events = selectors.EVENT_WRITE
            # self.selector.modify(self.sock, events, data=self)

            self._send_buffer += b"teddy bear " + data

            print("sending", repr(self._send_buffer), "to", self.addr)
            sent = self.sock.send(self._send_buffer)
            self._send_buffer = self._send_buffer[sent:]
            if sent and not self._send_buffer:
                print("closing connection to", self.addr)
                self.selector.unregister(self.sock)
                self.sock.close()
                self.sock = None

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = self.Message(sel, conn, addr)
        sel.register(conn, selectors.EVENT_READ, data=message)

    def run_server(self):
        global sel

        sel = selectors.DefaultSelector()

        host = "127.0.0.1"
        port = 65432
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()
        print("listening on", (host, port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        print("server is up and running")

        try:
            while True:

                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except:
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()


def main():
    server = Server()
    server.run_server()


if __name__ == '__main__':
    main()


