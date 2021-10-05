import socket
import selectors
import time
import traceback
from server import Server
from TCPConnection import TCPConnection
from TCPBuffer import BufferType, Buffer

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
                                f"{message.address}:\n{traceback.format_exc()}",
                            )
                            message.close()
                time.sleep(2)

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
