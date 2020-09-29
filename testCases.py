import unittest
import kruptosaurus
import henosisaurus

class HashTests(unittest.TestCase):

    def test_hash(self):
        rgb_int = [24, 66, 204]
        result = kruptosaurus.hash_pixel(rgb_int)
        self.assertEqual(result, 1859)
        
    def test_hash_zeroes(self):
        rgb_int = [0, 0, 0]
        result = kruptosaurus.hash_pixel(rgb_int)
        self.assertEqual(result, 356)

class CheckNumBytesTests(unittest.TestCase):

    def test_check_num_bytes_1(self):
        char = 'a'
        result = henosisaurus.check_num_bytes(char)
        self.assertEqual(1, result)

    def test_check_num_bytes_2(self):
        char = 'Շ'
        result = henosisaurus.check_num_bytes(char)
        self.assertEqual(2, result)

    def test_check_num_bytes_3(self):
        char = 'ࠀ'
        result = henosisaurus.check_num_bytes(char)
        self.assertEqual(3, result)

    def test_check_num_bytes_4(self):
        char = '𞋇'
        result = henosisaurus.check_num_bytes(char)
        self.assertEqual(4, result)

def hash_suite():
    suite = unittest.TestSuite()
    suite.addTest(HashTests('test_hash'))
    suite.addTest(HashTests('test_hash_zeroes'))
    return suite

def check_num_bytes_suite():
    suite = unittest.TestSuite()
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_1'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_2'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_3'))
    suite.addTest(CheckNumBytesTests('test_check_num_bytes_4'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(hash_suite())
    runner.run(check_num_bytes_suite())