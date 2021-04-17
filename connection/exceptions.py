class HeaderReadingError(Exception):
    def __init__(self, header, message):
        self.header = header
        self.message = message
