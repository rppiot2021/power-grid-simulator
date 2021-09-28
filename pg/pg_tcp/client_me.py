import socket


class Client:

    def __init__(self, host, port, buffer_size=1024):
        self.host = host
        self.port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

        data = self.s.recv(buffer_size)

        s.close()
        print("received data:", data)

    def send(self, payload):
        MESSAGE = "Hello, World!"
        self.s.send(str.encode(MESSAGE))

    def receive(self):


def main():
    client = Client('127.0.0.1', 5005)

if __name__ == '__main__':
    main()
