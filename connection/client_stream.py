import select
import socket
from enum import Enum

from connection.file import File, FileToReceive, FileToSend
from connection.header import Header, ContentType


class NotificationType(Enum):
    MESSAGE = 1
    RECEIVING_FILE = 2
    SENDING_FILE = 3


class ClientStream:
    BUFFER_SIZE = 8192
    HEADER_LENGTH = 100

    def __init__(self, host='192.168.1.192', port=12345):
        self.host = host
        self.port = port
        self._data = ''  # received and not processed data
        self._new_notifications = []
        self._file_to_send = None
        self._file_to_receive = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initialize socket connection
        self._create_connection()

    def _create_connection(self):
        self.connection = self.socket

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
        data = self._read_data(Header.HEADER_LENGTH)
        if not data:
            return None
        header = Header.load_header(data)
        return header

    def _new_notification(self, message_type, content=None):
        if message_type == NotificationType.MESSAGE:
            self._new_notifications.append({
                'type': message_type,
                'message': content,
            })
        elif message_type == NotificationType.RECEIVING_FILE:
            self._new_notifications.append({
                'type': message_type,
                'processed': self._file_to_receive.processed_size,
                'size': self._file_to_receive.size,
                'path': self._file_to_receive.path,
                'finished': self._file_to_receive.finished,
            })
        elif message_type == NotificationType.SENDING_FILE:
            self._new_notifications.append({
                'type': message_type,
                'processed': self._file_to_send.processed_size,
                'size': self._file_to_send.size,
                'path': self._file_to_send.path,
                'finished': self._file_to_send.finished,
            })

    def _parse_data(self):
        if self._file_to_send and not self._file_to_send.finished:
            # Send the next chunk
            self._send_data(self._file_to_send.read_chunk())

        if self._file_to_receive and not self._file_to_receive.finished:
            # Read the next chunk
            chunk_info = self._read_data(File.CHUNK_INFO_SIZE)
            amount_of_bytes = int.from_bytes(chunk_info, 'big')
            chunk = self._read_data(amount_of_bytes)
            self._file_to_receive.write_chunk(chunk)

            return  # Receiving file, so no headers to read

        while header := self._get_header():
            content = self._read_data(header['size'])
            if header['content-type'] == ContentType.TEXT.value:
                self._new_notification(NotificationType.MESSAGE, content)
            elif header['content-type'] == ContentType.FILE.value:
                self._file_to_receive = FileToReceive(content)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            return True
        except OSError:
            return False

    def send_message(self, message):
        encoded_message = message.encode()
        header = Header.build_header(ContentType.TEXT, len(message))
        try:
            self._send_data(header + encoded_message)
            return True
        except OSError:
            return False

    def send_file(self, path):
        if self._file_to_send:
            return False

        self._file_to_send = FileToSend(path)

    def get_new_notifications(self):
        self._receive_data()
        self._parse_data()
        if self._file_to_receive:
            self._new_notification(NotificationType.RECEIVING_FILE)
        if self._file_to_send:
            self._new_notification(NotificationType.SENDING_FILE)

        return self._new_notifications

    def close(self):
        self.socket.close()
        del self._file_to_receive
        del self._file_to_send
