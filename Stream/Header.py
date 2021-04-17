import json
from json import JSONDecodeError

from Stream.Exceptions import HeaderReadingError


class Header:
    HEADER_LENGTH = 100
    VERSION = 1

    @staticmethod
    def build_header(content_type, size):
        values = {
            'version': Header.VERSION,
            'content-type': content_type.value,
            'size': size
        }
        header = json.dumps(values).encode()

        # Fill header with spaces to, so it has a correct length
        header += b' ' * (Header.HEADER_LENGTH - len(header))
        return header

    @staticmethod
    def load_header(header):
        try:
            header = json.loads(header)
        except JSONDecodeError:
            raise HeaderReadingError(header, 'Error when parsing received header.')
        if not all(key in header for key in ['version', 'content-type', 'size']):
            raise HeaderReadingError(header, 'Not all required values are in received header.')
        return header
