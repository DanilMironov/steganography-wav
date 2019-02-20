import unittest
import os
from unittest.mock import MagicMock
from lsb_encoder import LSBEncoder


class TestEncoder(unittest.TestCase):
    def test_init(self):
        with open('filename.txt', 'w') as file:
            file.write('blablablablablablablablablablablablablablabla')
        sample = LSBEncoder('filename.txt', 'filename.txt')
        os.remove('filename.txt')
        self.assertIsInstance(sample.main_file, bytearray)
        self.assertIsInstance(sample.inserted_file, bytearray)
        self.assertEqual(sample.index_of_start_of_data, 7)
        self.assertIsInstance(sample.bits_per_sample, int)

    def test_define_filename(self):
        test_str = r'C:\Users\User\Desktop\filename.txt'
        result = LSBEncoder._define_filename(test_str)
        expectation = bytearray(bytes('filename.txt', 'utf-8'))
        self.assertEqual(result, expectation)

    def test_get_bits_per_sample(self):
        expectation = 16
        string = ''
        for i in range(34):
            string += '\x00'
        string += '\x10\x00'
        result = LSBEncoder._get_bits_per_sample(bytearray(bytes(string, 'utf-8')))
        self.assertEqual(result, expectation)

    def test_create_description(self):
        test_pairs = ['00', '10', '11', '11', '01', '00', '10', '01']
        expectation = ['0', '0', '0', '0', '0', '0', '0', '0', '0',
                       '0', '0', '0', '1', '0', '0', '0']
        result = LSBEncoder._create_description(test_pairs, 16)
        self.assertEqual(result, expectation)

    def test_create_new_byte_of_flag(self):
        description = ['0', '0', '0', '0', '0', '0', '0', '0', '0',
                       '0', '0', '0', '1', '0', '0', '0']
        byte = bytearray(b'\x00')
        i = 12
        expectation = 1
        result = LSBEncoder._create_new_byte_of_flag(byte, description, i)
        self.assertEqual(result, expectation)

    def test_create_new_byte_of_data(self):
        byte = bytearray(b'\x00')
        pairs = ['00', '10', '11', '01', '00', '11', '10']
        i = 2
        expectation = 3
        result = LSBEncoder._create_new_byte_of_data(byte, pairs, i)
        self.assertEqual(result, expectation)


if __name__ == '__main__':
    unittest.main()
