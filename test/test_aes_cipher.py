from unittest import TestCase
from aes_cipher import AESCipher


class TestAESCipher(TestCase):

    def test_encryption(self):
        key = '76ed0f0b-cef1-11'
        text_to_encryption = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "

        aes = AESCipher(key)

        for mode in AESCipher.AVAILABLE_MODES.keys():
            value_encrypt = aes.encrypt(text_to_encryption, mode)
            value_decrypt = aes.decrypt(value_encrypt, mode)
            assert value_decrypt == text_to_encryption
