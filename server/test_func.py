__author__ = 'PCPC'

import unittest
import func


class MyTestCase(unittest.TestCase):
    def test_allow_file(self):
        ret = func.allowed_file('www.pcap')
        ret1 = func.allowed_file('www.cap')
        ret2 = func.allowed_file('www.pcapng')
        self.assertTrue(ret1)
        self.assertTrue(ret2)
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()
