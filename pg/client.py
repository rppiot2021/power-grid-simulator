
class Client:

    def __init__(self, domain_name="127.0.0.1", port=5000):
        self.domain_name = domain_name
        self.port = port

    async def send(self, payload):

        raise NotImplementedError

    async def receive(self):

        raise NotImplementedError
