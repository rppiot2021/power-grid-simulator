import selectors
import socket
import time

from TCPBuffer import Buffer
from TCPConnection import TCPConnection
from server import Server


class TCPServer(Server):

    def __init__(self, domain_name, port):
        super(TCPServer, self).__init__(domain_name, port)
        self.conn = None

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
        self.buffer = Buffer()

        try:
            while True:
                events = self.sel.select(timeout=0.5)
                for key, mask in events:
                    print((" " * 17) + "BUFFER", self.buffer._fmt,
                          self.buffer._raw)
                    print((" " * 17) + "history", self.buffer.return_history())

                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data

                        try:
                            close = message.process_events(mask)

                            if close:
                                self.conn = None
                                continue
                        except BrokenPipeError:
                            print("broken pipe::client not listening")
                            time.sleep(2)
                        except ConnectionResetError:
                            print("conn reset")
                # time.sleep(2)

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        if not self.conn:
            self.conn, address = sock.accept()  # Should be ready to read
            print("accepted connection from", address)
            self.conn.setblocking(False)
            message = TCPConnection(self.sel, self.conn, address, self.buffer)
            self.sel.register(self.conn, selectors.EVENT_READ, data=message)


def main():
    TCPServer("127.0.0.1", 4567)


if __name__ == '__main__':
    main()
