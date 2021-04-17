import json
from enum import Enum
from json import JSONDecodeError

from connection.exceptions import HeaderReadingError


class ContentType(Enum):
    TEXT = 1
    FILE = 2
    SET_ENCRYPTION = 3


class Header:
    VERSION = 1
    HEADER_LENGTH = 100
    REQUIRED_FIELDS = ['version', 'content-type', 'size']

    @staticmethod
    def build_header(content_type, size):
        values = {
            'version': Header.VERSION,
            'content-type': content_type.value,
            'size': size
        }
        header = json.dumps(values).encode()

        # Fill header with spaces, so it has a correct length
        header += b' ' * (Header.HEADER_LENGTH - len(header))
        return header

    @staticmethod
    def load_header(header):
        try:
            header = json.loads(header)
        except JSONDecodeError:
            raise HeaderReadingError(header, 'Error when parsing received header.')
        if header.get('version') != Header.VERSION:
            raise HeaderReadingError(header, 'Version of the received header is different than this parser version.')
        if not all(key in header for key in Header.REQUIRED_FIELDS):
            raise HeaderReadingError(header, 'Not all required values are in received header.')
        if header['content-type'] == ContentType.FILE.value and not 'file-info-size' not in header:
            raise HeaderReadingError(header, "No 'info-size' in header.")
        return header
