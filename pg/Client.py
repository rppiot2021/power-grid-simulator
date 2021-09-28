class Client:

    def __init__(self, domain_name, port):
        self.domain_name = domain_name
        self.port = port

    def send(self):

        raise NotImplementedError

    def receive(self):

        raise NotImplementedError
