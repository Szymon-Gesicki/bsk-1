import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    AVAILABLE_MODES = {AES.MODE_CBC: 'CBC', AES.MODE_CFB: 'CFB', AES.MODE_OFB: 'OFB'}

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key

    def encrypt(self, raw, mode):
        # raw = raw.encode('utf8')  # encode to bytes here
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, mode, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc, mode):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, mode, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        # pad with bytes instead of str
        return s + (self.bs - len(s) % self.bs) * \
               chr(self.bs - len(s) % self.bs).encode('utf8')

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
    
    @staticmethod
    def mode_from_value(value):
        return list(AESCipher.AVAILABLE_MODES.keys())[list(AESCipher.AVAILABLE_MODES.values()).index(value)]
