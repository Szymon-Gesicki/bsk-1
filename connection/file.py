import os


class File:
    DOWNLOAD_PATH = 'tmp'
    CHUNK_SIZE = 32768

    def __init__(self, path):
        self._path = path
        self._file = None
        self._size = 0
        self._file_name = 0
        self._processed_size = 0
        self._finished = False

    def __del__(self):
        self.close()

    @property
    def size(self):
        return self._size

    @property
    def name(self):
        return self._file_name

    @property
    def processed_size(self):
        return self._processed_size

    @property
    def path(self):
        return self._path

    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, value):
        self._finished = value

    @staticmethod
    def _prepare_path(path):
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

    def close(self):
        self._file.close()


class FileToReceive(File):
    def __init__(self, header):
        super().__init__(File.DOWNLOAD_PATH)
        self._load_from_header(header)

    def _load_from_header(self, header):
        self._file_name = header.file_name
        self._path = os.path.join(self._path, self._file_name)
        self._size = header.file_size
        self._prepare_path(self._path)
        self._file = open(self._path, 'wb')

    def write_chunk(self, chunk):
        self._file.write(chunk)
        self._processed_size += len(chunk)


class FileToSend(File):
    def __init__(self, path):
        super().__init__(path)
        self._load_from_file(path)

    def _load_from_file(self, path):
        self._size = os.path.getsize(path)
        self._file_name = os.path.basename(path)
        self._file = open(path, 'rb')

    def read_chunk(self):
        data = self._file.read(File.CHUNK_SIZE)
        self._processed_size += len(data)

        if not data or len(data) < File.CHUNK_SIZE:
            self._finished = True  # if the whole file has been read
        return data
