from unittest import TestCase
from aes_cipher import AESCipher
from connection.file import FileToSend
import time


class TestAESCipher(TestCase):

    def test_encryption_file_with_read(self):
        path = "path_to_file"
        key = b'76ed0f0b-cef1-11'
        aes = AESCipher(key)

        for mode in AESCipher.AVAILABLE_MODES.keys():
            file_to_send = FileToSend(path)
            start_time = time.time()

            while not file_to_send.finished:
                chunk = file_to_send.read_chunk()
                value_encrypt = aes.encrypt(chunk, mode)
                value_decrypt = aes.decrypt(value_encrypt, mode)
                assert value_decrypt == chunk

            print("Mode ", str(AESCipher.AVAILABLE_MODES[mode]), "time: ", time.time()-start_time)


    def test_encryption_file_without_read(self):
        path = "path_to_file"
        key = b'76ed0f0b-cef1-11'
        aes = AESCipher(key)
        
        file_to_send = FileToSend(path)
        files_chunks = []
        while not file_to_send.finished:
            chunk = file_to_send.read_chunk()
            files_chunks.append(chunk)

        for mode in AESCipher.AVAILABLE_MODES.keys():

            start_time = time.time()

            for chunk in files_chunks:
                value_encrypt = aes.encrypt(chunk, mode)
                value_decrypt = aes.decrypt(value_encrypt, mode)
                assert value_decrypt == chunk

            print("Mode ", str(AESCipher.AVAILABLE_MODES[mode]), "time: ", time.time()-start_time)


