import select
import socket
import time
from connection.client_stream import ClientStream


class HostStream(ClientStream):
    def _create_connection(self):
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)
        self.connection, info = self.socket.accept()
        self._session_key = self._read_data(self.UUID_LENGTH).decode()
        return
