import sys
import os

import io
import json
import struct
from enum import IntEnum

sys.path.insert(0, os.getcwd() + '/../')


class BufferType(IntEnum):
    SEND = 0
    RECV = 1


class MessageType(IntEnum):
    CONTENT = 0
    COMMAND = 1


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

        if data is None:
            data = b'{"content": "Receive buffer is empty."}'
            return

        wrapper = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8",
                                   newline="")

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

    def create_response(self,
                        data_type=MessageType.CONTENT,
                        custom_message=None
                        ):
        """
        Generates response message. By default,response is generated from
        last element in history, DO NOT READ buffer to generate response,
        it works the other way ( create_response FILLS buffer).
        :param data_type:
        :param me:
        :param custom_message:
        :param end:
        :return:
        """

        if data_type == MessageType.COMMAND:
            self._fmt[BufferType.SEND] = {data_type: custom_message}
            return self._fmt[BufferType.SEND]

        else:
            try:
                response = self.read_next()
            except IndexError:
                # history is empty -> generate generic message

                response = self._fmt[BufferType.RECV]

                if data_type in response:
                    response = {data_type: response[data_type]}

                else:
                    response = {data_type: ""}
                if custom_message:
                    response[data_type] = custom_message

            self._fmt[BufferType.SEND] = response
            return response

    def clear(self, buffer_type):
        self._fmt[buffer_type] = {}
        self._raw[buffer_type] = b''

    def read_next(self):
        last_val = self._history.pop()
        return {MessageType.CONTENT: last_val}

    def push_and_clear(self):
        for k, v in self._fmt[BufferType.RECV].items():
            if k == MessageType.CONTENT:
                self._history.append(v)
        self.clear(BufferType.RECV)

    def return_history(self):
        return self._history
