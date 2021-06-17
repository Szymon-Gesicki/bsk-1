import select
import socket
import uuid
from enum import Enum

from Crypto.Cipher import AES

from aes_cipher import AESCipher
from connection.file import File, FileToReceive, FileToSend
from connection.header import Header, ContentType, FileState
from key_manager.key_manager import KeyManager


class NotificationType(Enum):
    MESSAGE = 1
    RECEIVING_FILE = 2
    SENDING_FILE = 3
    ENCRYPTION_MODE_CHANGE = 4


class ClientStream:
    BUFFER_SIZE = 8192
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

# --- Receiving data ---

    def _is_readable(self):
        readable, _, _ = select.select([self.connection], [], [], 0)
        return True if readable else False

    def _receive_data(self):
        while self._is_readable():
            self._data += self.connection.recv(self.BUFFER_SIZE)
            return True
        return False

    def _read_data(self, length):
        if length > len(self._data):
            return None
        data = self._data[:length]
        self._data = self._data[length:]
        if self._aes:
            data = self._aes.decrypt(data, self._encryption_mode).encode()
        return data

    def _get_header(self):
        data = self._read_data(Header.ENCODED_HEADER_LENGTH)
        if not data:
            return None
        header = Header.from_string(data.decode())
        return header

    def _parse_data(self):
        if self._file_to_receive and self._file_to_receive.finished:
            self._file_to_receive.close()
            self._file_to_receive = None

        if header := self._get_header():
            while not (content := self._read_data(header.content_size)):
                self._receive_data()
            if header.content_type == ContentType.TEXT.value:
                content = content.decode()
                self._new_notification(NotificationType.MESSAGE, content)
            elif header.content_type == ContentType.SET_ENCRYPTION.value:
                encryption_mode = int(content)
                self._encryption_mode = encryption_mode
                self._new_notification(NotificationType.ENCRYPTION_MODE_CHANGE, encryption_mode)
            elif header.content_type == ContentType.FILE.value:
                if not self._file_to_receive:
                    self._file_to_receive = FileToReceive(header)
                self._file_to_receive.write_chunk(content)
                if header.file_state == FileState.SENDING_FINISHED.value:
                    self._file_to_receive.finished = True

# --- Sending data ---

    def _send_data(self, header, content):
        # Encrypt header and content
        content = self._aes.encrypt(content, self._encryption_mode)
        header.content_size = len(content)
        header = self._aes.encrypt(str(header), self._encryption_mode)
        # Send encrypted data
        to_send = header + content
        self._send_raw_data(to_send)

    def _send_raw_data(self, raw):
        raw_length = len(raw)
        total_sent = 0
        while total_sent < raw_length:
            sent = self.connection.send(raw[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection has broken.")
            total_sent = total_sent + sent

    def _send_next_file_chunk(self):
        if self._file_to_send.finished:
            self._file_to_send.close()
            self._file_to_send = None
        else:
            # Send the next chunk
            chunk = self._file_to_send.read_chunk()
            file_state = FileState.SENDING_FINISHED if self._file_to_send.finished else FileState.SENDING_IN_PROGRESS
            header = Header(ContentType.FILE, self._file_to_send.size, self._file_to_send.name, file_state)
            self._send_data(header, chunk)

# --- Managing notifications (events) passed to window manager ---

    def _new_notification(self, message_type, content=None):
        """ Creates new notification to be send to window manager """
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

    def _update(self):
        self._receive_data()
        self._parse_data()
        if self._file_to_send:
            self._send_next_file_chunk()

# --- Public functions ---

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
        except OSError as e:
            return False
        self._session_key = str(uuid.uuid1())
        encoded_message = self._session_key.encode()
        encrypted_message = self._key_manager.encrypt(encoded_message)
        try:
            self._send_raw_data(encrypted_message)
        except OSError:
            return False
        self._aes = AESCipher(encoded_message[:16])
        return True

    def send_message(self, message):
        header = Header(ContentType.TEXT)
        self._send_data(header, message)
        return True

    def send_file(self, path):
        if self._file_to_send:
            return False

        self._file_to_send = FileToSend(path)
        return True

    def set_encryption_mode(self, encryption_mode):
        header = Header(ContentType.SET_ENCRYPTION)
        message = str(encryption_mode)
        self._send_data(header, message)
        self._encryption_mode = encryption_mode
        return True

    def get_new_notifications(self):
        self._update()
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
