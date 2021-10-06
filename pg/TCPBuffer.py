import io
import json
import struct
from enum import IntEnum


class BufferType(IntEnum):
    SEND = 0
    RECV = 1


class Buffer:
    def __init__(self, ):
        self._raw = [b"", b""]
        self._fmt = [{}, {}]
        self._history = []

    def from_bytes(self, data=None):

        if data is None:
            if self._raw[BufferType.RECV] == b'':
                raise ValueError
            data = self._raw[BufferType.RECV]

        wrapper = io.TextIOWrapper(io.BytesIO(data),
                                   encoding="utf-8", newline="")
        print(data)
        formatted = json.load(wrapper)
        wrapper.close()

        self._fmt[BufferType.RECV] = formatted
        return formatted

    def to_bytes(self, data=None):

        if data is None:
            data = self._fmt[BufferType.SEND]

        content_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        n = struct.pack(">I", len(content_bytes))

        self._raw[BufferType.SEND] = n + content_bytes
        return self._raw[BufferType.SEND]

    def create_response(self, overwrite=False):
        try:
            response = {
                "content": "First 10 bytes of request: " +
                           str(self._fmt[BufferType.RECV]['client_sent'])[:10]
            }
        except KeyError:
            response = {
                "content": "Last request was empty."
            }

        if overwrite:
            self._fmt[BufferType.SEND] = response
        return response

    def clear(self, buffer_type):
        self._fmt[buffer_type] = {}
        self._raw[buffer_type] = b''

    def read_next(self):
        return self._history.pop()

    def push_and_clear(self):
        self._history.append(self._fmt[BufferType.RECV])
        self.clear(BufferType.RECV)
