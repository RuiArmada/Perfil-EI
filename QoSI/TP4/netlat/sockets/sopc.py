import socket

from utilities import Timestamp
from sockets import Definitions

class Sopc:
    def __init__(self, port, type_):
        self.port = port
        self.type_ = type_
        if type_ == Definitions.TCP:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif type_ == Definitions.UDP:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise ValueError("Invalid socket type")
        self.s.bind(("0.0.0.0",port))

    def recv(self, rec_bytes = 4096) -> (bytes, ((str,int),(str,int)), Timestamp):
        (data, addr) = (None, None)
        if self.type_ == Definitions.TCP:
            self.s.listen(5)
            conn, addr = self.s.accept()
            data = conn.recv(rec_bytes)
            conn.close()

        elif self.type_ == Definitions.UDP:
            data, addr = self.s.recvfrom(rec_bytes)

        timestamp = Timestamp()

        dst = (Definitions.C2_SERVER_IP, self.port)
        src = (addr[0], addr[1])

        return (data,(dst,src), timestamp)

