import select
import socket
import time

from aes_cipher import AESCipher
from connection.client_stream import ClientStream


class HostStream(ClientStream):
    def _create_connection(self):
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)
        self.connection, info = self.socket.accept()
        while not (data := self._read_data(self.UUID_LENGTH)):
            self._receive_data()
        self._session_key = self._key_manager.decrypt(data)
        self._aes = AESCipher(self._session_key[:16])
        return
