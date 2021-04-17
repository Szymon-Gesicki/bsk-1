import select
import socket
import time
from enum import Enum

from Stream.Header import Header

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

    def __init__(self, host='localhost', port=12345):
        # Initialize socket connection
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connection = self.socket

        # Received and not processed data
        self._data = ''

    def _is_readable(self):
        readable, _, _ = select.select([self.connection], [], [], 0)
        return True if readable else False

    def _send_text(self, text):
        text_length = len(text)
        total_sent = 0
        while total_sent < text_length:
            sent = self.connection.send(text[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection has broken.")
            total_sent = total_sent + sent

    def _receive(self):
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

    def _read_messages(self):
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
        self._send_text(header + encoded_message)

    def _is_writable(self):
        _, writable, _ = select.select([], [self.connection], [], 5)
        return True if writable else False

    def get_new_messages(self):
        self._receive()
        messages = self._read_messages()
        return messages

    def close(self):
        self.socket.close()