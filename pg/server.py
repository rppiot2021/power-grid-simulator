class Server:
    # netstat -tlpn | sort -t: -k2 -n
    # kill -9 {pid_id}

    def __init__(self, host_name, port):
        self.host_name = host_name
        self.port = port
