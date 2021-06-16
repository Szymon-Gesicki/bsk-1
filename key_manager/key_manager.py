import hashlib

import rsa


def _hash_password(password):
    return hashlib.sha256(password).hexdigest()


def _retrieve_private_key(hashed_password):
    with open("key_manager/private_key/rsa.private", "rb") as f:
        key_data = f.read()
        private = rsa.PrivateKey.load_pkcs1(key_data)
    return private


def _retrieve_public_key(hashed_password):
    with open("key_manager/public_key/rsa.public", "rb") as f:
        key_data = f.read()
        public = rsa.PublicKey.load_pkcs1_openssl_pem(key_data)
    return public


class KeyManager:
    def __init__(self, password=''):
        hashed_password = _hash_password(password)
        self._public_key = _retrieve_public_key(hashed_password)
        self._private_key = _retrieve_private_key(hashed_password)

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key
