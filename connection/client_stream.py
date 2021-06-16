import select
import socket
import uuid
from enum import Enum

from Crypto.Cipher import AES

from aes_cipher import AESCipher
from connection.file import File, FileToReceive, FileToSend
from connection.header import Header, ContentType
from key_manager.key_manager import KeyManager


class NotificationType(Enum):
    MESSAGE = 1
    RECEIVING_FILE = 2
    SENDING_FILE = 3
    ENCRYPTION_MODE_CHANGE = 4


class ClientStream:
    BUFFER_SIZE = 8192
    HEADER_LENGTH = 100
    UUID_LENGTH = 128

    def __init__(self, host='192.168.1.192', port=12345, encryption_mode=AES.MODE_CBC, password=''):
        self.host = host
        self.port = port
        self._encryption_mode = encryption_mode
        self._key_manager = KeyManager(password)
        self._session_key = None
        self._aes = None
        self._data = b''  # received and not processed data
        self._new_notifications = []
        self._file_to_send = None
        self._file_to_receive = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initialize socket connection
        self._create_connection()

    def _create_connection(self):
        self.connection = self.socket

    def _is_readable(self):
        readable, _, _ = select.select([self.connection], [], [], 0)
        return True if readable else False

    def _send_data(self, text):
        if self._aes:
            text = self._aes.encrypt(text, self._encryption_mode)
        text_length = len(text)
        total_sent = 0
        while total_sent < text_length:
            sent = self.connection.send(text[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection has broken.")
            total_sent = total_sent + sent

    def _receive_data(self):
        while self._is_readable():
            self._data += self.connection.recv(self.BUFFER_SIZE)
            return True
        return False

    def _read_data(self, length):
        self._receive_data()
        if length > len(self._data):
            return None
        data = self._data[:length]
        self._data = self._data[length:]
        if self._aes:
            data = self._aes.decrypt(data, self._encryption_mode)
        return data

    def _get_header(self):
        data = self._read_data(Header.HEADER_LENGTH)
        if not data:
            return None
        header = Header.load_header(data.decode())
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
        elif message_type == NotificationType.ENCRYPTION_MODE_CHANGE:
            self._new_notifications.append({
                'type': message_type,
                'mode': int(content),
            })

    def _parse_data(self):
        if self._file_to_send:
            if self._file_to_send.finished:
                self._file_to_send.close()
                self._file_to_send = None
            else:
                # Send the next chunk
                self._send_data(self._file_to_send.read_chunk())

        if self._file_to_receive:
            if self._file_to_receive.finished:
                self._file_to_receive.close()
                self._file_to_receive = None
            else:
                # Read the next chunk
                chunk_info = self._read_data(File.CHUNK_INFO_SIZE)
                if not chunk_info:
                    return
                amount_of_bytes = int.from_bytes(chunk_info, 'big')
                while not (chunk := self._read_data(amount_of_bytes)):
                    pass
                self._file_to_receive.write_chunk(chunk)
                return

        while header := self._get_header():
            content = self._read_data(header['size']).decode()
            if header['content-type'] == ContentType.TEXT.value:
                self._new_notification(NotificationType.MESSAGE, content)
            elif header['content-type'] == ContentType.SET_ENCRYPTION.value:
                encryption_mode = int(content)
                self._encryption_mode = encryption_mode
                self._new_notification(NotificationType.ENCRYPTION_MODE_CHANGE, encryption_mode)
            elif header['content-type'] == ContentType.FILE.value:
                self._file_to_receive = FileToReceive(content)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
        except OSError as e:
            return False
        self._session_key = str(uuid.uuid1())
        encoded_message = self._session_key.encode()
        encrypted_message = self._key_manager.encrypt(encoded_message)
        try:
            self._send_data(encrypted_message)
        except OSError:
            return False
        self._aes = AESCipher(self._session_key)
        return True

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
        file_info = self._file_to_send.details
        header = Header.build_header(ContentType.FILE, len(file_info))
        self._send_data(header + file_info)
        return True

    def set_encryption_mode(self, encryption_mode):
        encoded_message = str(encryption_mode).encode()
        header = Header.build_header(ContentType.SET_ENCRYPTION, len(str(encryption_mode)))
        try:
            self._send_data(header + encoded_message)
            self._encryption_mode = encryption_mode
            return True
        except OSError:
            return False

    def get_new_notifications(self):
        self._parse_data()
        if self._file_to_receive:
            self._new_notification(NotificationType.RECEIVING_FILE)
        if self._file_to_send:
            self._new_notification(NotificationType.SENDING_FILE)
        new_notifications = self._new_notifications
        self._new_notifications = []
        return new_notifications

    def close(self):
        self.socket.close()
        del self._file_to_receive
        del self._file_to_send
