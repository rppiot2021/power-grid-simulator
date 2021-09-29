class Server:
    # netstat -tlpn | sort -t: -k2 -n
    # kill -9 {pid_id}

    def __init__(self, domain_name, port):
        self.domain_name = domain_name
        self.port = port
