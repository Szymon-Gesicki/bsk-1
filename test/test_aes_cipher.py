from unittest import TestCase
from aes_cipher import AESCipher
from connection.file import FileToSend


class TestAESCipher(TestCase):

    def test_encryption(self):
        path = "/Users/szymongesicki/aidlab-firmware.zip"
        key = b'76ed0f0b-cef1-11'
        file_to_send = FileToSend(path)
        aes = AESCipher(key)

        while not file_to_send.finished:
            for mode in AESCipher.AVAILABLE_MODES.keys():
                chunk = file_to_send.read_chunk()
                value_encrypt = aes.encrypt(chunk, mode)
                value_decrypt = aes.decrypt(value_encrypt, mode)
                assert value_decrypt == chunk

        # key = '76ed0f0b-cef1-11'
        # text_to_encryption = "ąLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"
        #
        # aes = AESCipher(key)
        #
        # for mode in AESCipher.AVAILABLE_MODES.keys():
        #     value_encrypt = aes.encrypt(text_to_encryption, mode)
        #     value_decrypt = aes.decrypt(value_encrypt, mode).decode('utf-8')
        #     assert value_decrypt == text_to_encryption
