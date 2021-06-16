import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    AVAILABLE_MODES = {AES.MODE_CBC: 'CBC', AES.MODE_CFB: 'CFB', AES.MODE_OFB: 'OFB'}

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key

    def encrypt(self, raw, mode):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, mode, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc, mode):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, mode, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def mode_from_value(value):
        return list(AESCipher.AVAILABLE_MODES.keys())[list(AESCipher.AVAILABLE_MODES.values()).index(value)]

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
