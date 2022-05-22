import unittest
from encryption_and_decryption import Want_to_crypt
from cryptography.fernet import Fernet
import os
from io import StringIO

tester = Want_to_crypt('sample.mp3')

class Test_encryption_and_decryption(unittest.TestCase):
    def test_new_name(self):
        self.assertAlmostEqual(tester.new_name(1),'sample_encrypted.mp3')
        self.assertAlmostEqual(tester.new_name(2),'sample_decrypted.mp3')
        
    def test_new_name_values(self):
        self.assertRaises(ValueError, tester.new_name, 3)
        
    def test_encryption(self):
        pass
