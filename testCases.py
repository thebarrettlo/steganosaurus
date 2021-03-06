import unittest
from steganosaurus import SteganoImage
from kruptosaurus import hash_pixel
from henosisaurus import check_num_bytes, encode_to_cluster, find_next_open
import numpy as np

ONE_BYTE_CHAR = 'a'  # Unicode U+0061
TWO_BYTE_CHAR = 'Շ'  # Unicode U+0547
THREE_BYTE_CHAR = 'ࠀ'  # Unicode U+0800
FOUR_BYTE_CHAR = '𞋇'  # Unicode U+1E2C7

class HashTests(unittest.TestCase):

    def test_hash(self):
        rgb_int = [24, 66, 204]
        result = hash_pixel(rgb_int)
        self.assertEqual(result, 1859)
        
    def test_hash_zeroes(self):
        rgb_int = [0, 0, 0]
        result = hash_pixel(rgb_int)
        self.assertEqual(result, 356)

class CheckNumBytesTests(unittest.TestCase):

    def test_check_num_bytes_01(self):
        char = ONE_BYTE_CHAR
        result = check_num_bytes(char)
        self.assertEqual(1, result)

    def test_check_num_bytes_02(self):
        char = TWO_BYTE_CHAR
        result = check_num_bytes(char)
        self.assertEqual(2, result)

    def test_check_num_bytes_03(self):
        char = THREE_BYTE_CHAR
        result = check_num_bytes(char)
        self.assertEqual(3, result)

    def test_check_num_bytes_04(self):
        char = FOUR_BYTE_CHAR
        result = check_num_bytes(char)
        self.assertEqual(4, result)


class EncodeClusterTests(unittest.TestCase):

    def setUp(self):
        self.pixelmap = np.zeros((2, 3, 3), dtype=int)

    def test_encode_cluster_01(self):
        char = ONE_BYTE_CHAR
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 0, 0, 0, 0, 0]
        encode_to_cluster(char, 0, 1, self.pixelmap)
        result = [channel for y in range (0, 2) for x in range(0, 3) for channel in self.pixelmap[y, x]]
        self.assertEqual(expected, result)

    def test_encode_cluster_02(self):
        char = TWO_BYTE_CHAR
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 1, 2, 0, 1, 3, 0]
        encode_to_cluster(char, 0, 1, self.pixelmap)
        result = [channel for y in range (0, 2) for x in range(0, 3) for channel in self.pixelmap[y, x]]
        self.assertEqual(expected, result)

    def test_encode_cluster_03(self):
        char = THREE_BYTE_CHAR
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 0, 0, 2, 2, 0, 0, 2]
        encode_to_cluster(char, 0, 1, self.pixelmap)
        result = [channel for y in range (0, 2) for x in range(0, 3) for channel in self.pixelmap[y, x]]
        self.assertEqual(expected, result)

    def test_encode_cluster_04(self):
        char = FOUR_BYTE_CHAR
        expected = [0, 2, 3, 2, 0, 1, 3, 0, 0, 3, 3, 0, 0, 2, 1, 3, 2, 2]
        encode_to_cluster(char, 0, 1, self.pixelmap)
        result = [channel for y in range (0, 2) for x in range(0, 3) for channel in self.pixelmap[y, x]]
        self.assertEqual(expected, result)


class FindOpenSpaceTests(unittest.TestCase):

    def setUp(self):
        self.img = SteganoImage('./16x16_dot.jpg')

    def test_middle_empty(self):
        result = find_next_open(8, 8, self.img)
        self.assertEqual((8, 14), result)

    def test_origin_empty(self):
        result = find_next_open(0, 0, self.img)
        self.assertEqual((12, 10), result)
        
    def test_origin_full(self):
        for x in range(0, 15, 3):
            for y in range(0, 15, 2):
                self.img.occupied.add((x, y))
        with self.assertRaises(IndexError):
            find_next_open(0, 0, self.img)

    def tearDown(self):
        self.img.close_fp()

def hash_suite():
    suite = unittest.TestSuite()
    suite.addTest(HashTests('test_hash'))
    suite.addTest(HashTests('test_hash_zeroes'))
    return suite

def check_num_bytes_suite():
    suite = unittest.TestSuite()
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_01'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_02'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_03'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_04'))
    return suite

def encode_to_cluster_suite():
    suite = unittest.TestSuite()
    suite.addTest(EncodeClusterTests('test_encode_cluster_01'))
    suite.addTest(EncodeClusterTests('test_encode_cluster_02'))
    suite.addTest(EncodeClusterTests('test_encode_cluster_03'))
    suite.addTest(EncodeClusterTests('test_encode_cluster_04'))
    return suite

def find_next_open_suite():
    suite = unittest.TestSuite()
    suite.addTest(FindOpenSpaceTests('test_middle_empty'))
    suite.addTest(FindOpenSpaceTests('test_origin_empty'))
    suite.addTest(FindOpenSpaceTests('test_origin_full'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(hash_suite())   # 2
    runner.run(check_num_bytes_suite())   # 4
    runner.run(encode_to_cluster_suite())   # 4
    runner.run(find_next_open_suite())   # 3
