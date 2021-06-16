import hashlib

import rsa
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA

from aes_cipher import AESCipher


def _hash_password(password):
    return hashlib.sha1(password.encode()).digest()


def _retrieve_private_key(aes):
    with open("key_manager/private_key/rsa.private", "rb") as f:
        key_data = f.read()
    key_data = aes.decrypt(key_data, AES.MODE_CBC)
    private = rsa.PrivateKey.load_pkcs1(key_data)
    return private


def _retrieve_public_key(aes):
    with open("key_manager/public_key/rsa.public", "rb") as f:
        key_data = f.read()
    key_data = aes.decrypt(key_data, AES.MODE_CBC)
    public = rsa.PublicKey.load_pkcs1_openssl_pem(key_data)
    return public


class KeyManager:
    def __init__(self, password=''):
        hashed_password = _hash_password(password)
        aes = AESCipher(hashed_password[:16])
        self._public_key = _retrieve_public_key(aes)
        self._private_key = _retrieve_private_key(aes)
        return

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def encrypt(self, bytes):
        encrypted = rsa.encrypt(bytes, self._public_key)
        return encrypted

    def decrypt(self, bytes):
        decrypted = rsa.decrypt(bytes, self._private_key)
        return decrypted
