import abc


class Client(abc.ABC):

    def __init__(self, domain_name="127.0.0.1", port=5000):
        print("Client init")
        self.domain_name = domain_name
        self.port = port

    @abc.abstractmethod
    async def send(self, payload):
        raise NotImplementedError

    @abc.abstractmethod
    async def receive(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self):
        raise NotImplementedError
