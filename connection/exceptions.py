class ReadingError(Exception):
    pass


class HeaderReadingError(Exception):
    def __init__(self, header, message):
        self.header = header
        self.message = message


class FileInfoReadingError(Exception):
    def __init__(self, file_info, message):
        self.file_info = file_info
        self.message = message
