import json
import os
from json import JSONDecodeError

from connection.exceptions import FileInfoReadingError


class File:
    VERSION = 1
    REQUIRED_FIELDS = ['version', 'file-name', 'size']
    DOWNLOAD_PATH = 'tmp'
    CHUNK_INFO_SIZE = 2
    CHUNK_SIZE = 1022

    def __init__(self, path):
        self._path = path
        self._file = None
        self._size = 0
        self._file_name = 0
        self._processed_size = 0
        self._finished = False

    def __del__(self):
        self._close()

    @property
    def details(self):
        details = {
            'version': File.VERSION,
            'file-name': self._file_name,
            'size': self._size,
        }
        return json.dumps(details).encode()

    @property
    def size(self):
        return self._size

    @property
    def processed_size(self):
        return self._processed_size

    @property
    def path(self):
        return self._path

    @property
    def finished(self):
        return self._finished

    def _close(self):
        self._file.close()


class FileToReceive(File):
    def __init__(self, file_info):
        super().__init__(File.DOWNLOAD_PATH)
        self._load_from_str(file_info)

    def _load_from_str(self, data):
        try:
            values = json.loads(data)
        except JSONDecodeError:
            raise FileInfoReadingError(data, 'Error when parsing received file-info.')
        if values.get('version') != File.VERSION:
            raise FileInfoReadingError(values,
                                       'Version of the received file-info is different than this parser version.')
        if not all(key in values for key in File.REQUIRED_FIELDS):
            raise FileInfoReadingError(data, 'Not all required values are in received file-info.')

        self._file_name = values['file-name']
        self._size = values['size']
        self._file = open(self._path, 'wb')

    def write_chunk(self, chunk):
        self._file.write(chunk)
        self._processed_size += len(chunk)
        if len(chunk) != File.CHUNK_SIZE:
            self._close()
            self._finished = True  # if the whole file has been saved


class FileToSend(File):
    def __init__(self, path):
        super().__init__(path)
        self._load_from_file(path)

    def _load_from_file(self, path):
        self._size = os.path.getsize(path)
        self._file_name = os.path.basename(path)
        self._file = open(path, 'rb')

    def read_chunk(self):
        amount_of_bytes = (0).to_bytes(2, byteorder='big')
        if data := self._file.read(File.CHUNK_SIZE):
            amount_of_bytes = (len(data)).to_bytes(2, byteorder='big')

        self._processed_size += len(data)

        if not data or len(data) < File.CHUNK_SIZE:
            self._finished = True  # if the whole file has been read
        return amount_of_bytes + data
