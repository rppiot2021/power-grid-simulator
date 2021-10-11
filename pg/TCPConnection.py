import selectors
import struct
import time

from TCPBuffer import BufferType


class TCPConnection:
    def __init__(self, selector, sock, address, buffer):
        self.selector = selector
        self.sock = sock
        self.address = address

        self.buffer = buffer

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

    def remote_close(self):
        self.write(end=True)

    def _recv_raw_msg(self):
        """In charge of receiving messages from the connection.
        Function will use first 4 bytes and interpret it as
        message length. Message is located in bytes that follow.

        Returns:
            bytes: raw input stream from TCP connection
        """
        try:
            raw_message_length = self.sock.recv(4)  # --> b'\x00\x08\xf8\x93'
        except:
            # print("no header visible")
            return None
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

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:

            close = self.read()
            try:
                print("r")
                self._set_selector_events_mask("rw")
            except:
                pass

        if mask & selectors.EVENT_WRITE:
            print("w")
            close = self.write()
            try:
                self._set_selector_events_mask("r")
            except:
                pass

        return close


    def process_message(self):
        new_message = self.buffer._fmt[BufferType.RECV]
        print("RECEIVED MESSAGE", new_message)

        if new_message is not None:
            if "client_sent" in new_message:
                if new_message['client_sent'] == "CLOSE":
                    self.close()
                    self.buffer.clear(BufferType.SEND)
                    self.buffer.clear(BufferType.RECV)
                    return True
        if new_message != {}:
            self.buffer.push_and_clear()

        return False

    def read(self):
        print("read started")
        for i in range(5):
            try:
                self.buffer._raw[BufferType.RECV] = self._recv_raw_msg()
                if self.buffer._raw[BufferType.RECV] is not None:
                    break
                time.sleep(1)
            except KeyboardInterrupt:
                break

        print("recived", self.buffer._raw[BufferType.RECV])
        self.buffer.from_bytes()

        close = self.process_message()

        return close

    def write(self, payload=None,end=False):

        self.buffer.create_response(overwrite=True,
                                    custom_message=payload,
                                    end=end)

        print("buffer send fmt", )
        self.buffer.to_bytes()
        print("created_message", self.buffer._fmt[BufferType.SEND])

        self.sock.sendall(self.buffer._raw[BufferType.SEND])

        print("SENT", self.buffer._raw[BufferType.SEND])
        self.buffer.clear(BufferType.SEND)

    def close(self):
        print("closing connection to", self.address, "\n")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.address}: {repr(e)}",
            )

        try:
            self.sock.close()
        except AttributeError:
            print("sock is none")
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.address}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
