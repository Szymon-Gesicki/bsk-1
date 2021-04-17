import select
import socket
import time
from enum import Enum

from connection.header import Header

"""
content-type:
1 - text
2 - file
3 - set encryption
"""


class ContentType(Enum):
    TEXT = 1
    FILE = 2
    SET_ENCRYPTION = 3


class ClientStream:
    BUFFER_SIZE = 8192
    HEADER_LENGTH = 100

    def __init__(self, host='192.168.1.192', port=12345):
        # initialize socket connection
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = self.socket
        # received and not processed data
        self._data = ''

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            return True
        except OSError:
            return False

    def _is_readable(self):
        readable, _, _ = select.select([self.connection], [], [], 1)
        return True if readable else False

    def _send_data(self, text):
        text_length = len(text)
        total_sent = 0
        while total_sent < text_length:
            sent = self.connection.send(text[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection has broken.")
            total_sent = total_sent + sent

    def _receive_data(self):
        while self._is_readable():
            self._data += self.connection.recv(self.BUFFER_SIZE).decode()
            return True
        return False

    def _read_data(self, length):
        if length > len(self._data):
            return None
        data = self._data[:length]
        self._data = self._data[length:]
        return data

    def _get_header(self):
        header = self._read_data(Header.HEADER_LENGTH)
        if not header:
            return None
        header = Header.load_header(header)
        return header

    def _parse_data(self):
        messages = []
        header = self._get_header()
        while header:
            content = self._read_data(header['size'])
            if header['content-type'] == ContentType.TEXT.value:
                messages.append(content)
            header = self._get_header()
        return messages

    def send_message(self, message):
        encoded_message = message.encode()
        header = Header.build_header(ContentType.TEXT, len(message))
        try:
            self._send_data(header + encoded_message)
            return True
        except OSError:
            return False

    def get_new_messages(self):
        self._receive_data()
        messages = self._parse_data()
        return messages

    def close(self):
        self.socket.close()