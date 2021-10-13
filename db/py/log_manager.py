class LogManager:

    def __init__(self, is_opened):
        self.is_opened = is_opened

    def check_connection(self):
        if not self.is_opened:
            raise PermissionError("connection closed or not established")

    def __str__(self):
        return self.is_opened
