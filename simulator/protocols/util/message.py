class Message:

    def __init__(self, header, payload):
        self.header = header
        self.payload = payload

    def __str__(self):
        return str(["header:", self.header, "payload", self.payload])


def main():
    message = Message(
        header={"control": "256adf", "len": 3},
        payload="tmp msg"
    )

    print(message)


if __name__ == '__main__':
    main()
