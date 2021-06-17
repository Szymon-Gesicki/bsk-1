import json
from enum import Enum
from json import JSONDecodeError

from connection.exceptions import HeaderReadingError


class ContentType(Enum):
    TEXT = 1
    FILE = 2
    SET_ENCRYPTION = 3


class FileState(Enum):
    NONE = 0
    SENDING_IN_PROGRESS = 1
    SENDING_FINISHED = 2


class Header:
    VERSION = 2
    HEADER_LENGTH = 256
    ENCODED_HEADER_LENGTH = 384
    REQUIRED_FIELDS = ['version', 'content-type', 'size']

    def __init__(self, content_type, file_size=0, file_name='', file_state=FileState.NONE):
        self._content_size = 0
        self._content_type = content_type
        self._file_size = file_size
        self._file_name = file_name
        self._file_state = file_state

    def __str__(self):
        header_string = json.dumps(self._to_dict())
        # Fill header with spaces, so it has a correct length
        header_string += ' ' * (Header.HEADER_LENGTH - len(header_string))
        return header_string

    def __repr__(self):
        return self.__str__()

    def _to_dict(self):
        values = {
            'version': Header.VERSION,
            'content-type': self._content_type.value,
            'size': self._content_size,
            'file-size': self._file_size,
            'file-name': self._file_name,
            'file-state': self._file_state.value,
        }
        return values

    @property
    def file_name(self):
        return self._file_name

    @property
    def content_type(self):
        return self._content_type

    @property
    def file_state(self):
        return self._file_state

    @property
    def file_size(self):
        return self._file_size

    @property
    def content_size(self):
        return self._content_size

    @content_size.setter
    def content_size(self, value):
        self._content_size = value

    @staticmethod
    def from_string(header):
        try:
            header_dict = json.loads(header)
        except JSONDecodeError:
            raise HeaderReadingError(header, 'Error when parsing received header.')
        created_header = Header(header_dict['content-type'], header_dict['file-size'], header_dict['file-name'],
                                header_dict['file-state'])
        created_header.content_size = header_dict['size']
        return created_header

