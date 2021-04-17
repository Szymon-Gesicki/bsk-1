import select
import socket
import time
from Stream.ClientStream import ClientStream


class HostStream(ClientStream):
    def __init__(self, client='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), port))
        self.socket.listen(5)
        self.connection, info = self.socket.accept()
        self._data = ''
