import select
import socket
import time

from aes_cipher import AESCipher
from connection.client_stream import ClientStream
from connection.header import Header, ContentType


class HostStream(ClientStream):
    def _create_connection(self):
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)
        self.connection, info = self.socket.accept()
        self._send_raw_data(self._key_manager.public_key.exportKey('OpenSSH'))
        while not (data := self._read_data(self.UUID_LENGTH)):
            self._receive_data()
        self._session_key = self._key_manager.decrypt(data)
        self._aes = AESCipher(self._session_key[:16])
        if self._key_manager.hacker:
            self.is_hacker = True
            header = Header(ContentType.WARNING)
            self._send_data(header, "Beware!  A hacker has broken in!".encode('utf8'))
        return
