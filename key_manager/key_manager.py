import hashlib
import os.path

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

from aes_cipher import AESCipher


def _hash_password(password):
    return hashlib.sha1(password.encode()).digest()


def _retrieve_private_key(aes):
    with open(KeyManager.PRIVATE_KEY_PATH, "rb") as f:
        key_data = f.read()
    key_data = aes.decrypt(key_data, AES.MODE_CBC)
    private = RSA.import_key(key_data)
    return private


def _retrieve_public_key(aes):
    with open(KeyManager.PUBLIC_KEY_PATH, "rb") as f:
        key_data = f.read()
    key_data = aes.decrypt(key_data, AES.MODE_CBC)
    public = RSA.import_key(key_data)
    return public


class KeyManager:
    PRIVATE_KEY_PATH = 'key_manager/private_key/private.pem'
    PUBLIC_KEY_PATH = 'key_manager/public_key/public.pem'

    def __init__(self, password=''):
        hashed_password = _hash_password(password)
        aes = AESCipher(hashed_password[:16])
        self._public_key = _retrieve_public_key(aes)
        self._private_key = _retrieve_private_key(aes)

    @staticmethod
    def check_if_keys_exist():
        return os.path.isfile(KeyManager.PRIVATE_KEY_PATH) and os.path.isfile(KeyManager.PUBLIC_KEY_PATH)

    @staticmethod
    def generate_keys(password):
        hashed_password = _hash_password(password)
        aes = AESCipher(hashed_password[:16])

        # Private key
        key = RSA.generate(1024)
        encrypted_key = aes.encrypt(key.exportKey('PEM'), AES.MODE_CBC)
        f = open(KeyManager.PRIVATE_KEY_PATH, "wb")
        f.write(encrypted_key)
        f.close()

        # Public key
        pubkey = key.publickey()
        encrypted_pubkey = aes.encrypt(pubkey.exportKey('OpenSSH'), AES.MODE_CBC)
        f = open(KeyManager.PUBLIC_KEY_PATH, "wb")
        f.write(encrypted_pubkey)
        f.close()

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def encrypt(self, bytes, pubkey=None):
        pubkey = pubkey or self._public_key
        cipher = Cipher_PKCS1_v1_5.new(pubkey)
        cipher_text = cipher.encrypt(bytes)
        return cipher_text

    def decrypt(self, bytes):
        decipher = Cipher_PKCS1_v1_5.new(self._private_key)
        cipher_text = decipher.decrypt(bytes, None)
        return cipher_text
