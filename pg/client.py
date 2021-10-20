from abc import ABCMeta, abstractmethod


class Client(object):
    __metaclass__ = ABCMeta

    def __init__(self, domain_name="127.0.0.1", port=5000):
        print("Client init")
        self.domain_name = domain_name
        self.port = port

    @abstractmethod
    async def send(self, payload):
        raise NotImplementedError

    @abstractmethod
    async def receive(self):
        raise NotImplementedError

    @abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError
