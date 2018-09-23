import logging
import time
import os
import unittest

from quickftp.qftp_helper import Helpers
from quickftp.qftp_client import QuickFtpClient


class TestClient(unittest.TestCase):
    """
    Test the qftp client
    """
    client = None

    def test_connect(self):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__class__.client = QuickFtpClient(os.path.join(current_dir_path, 'conf/client_conf.yml'))
        self.assertTrue(self.__class__.client.is_connected(), 'client not connected')

    def test_files_present(self):
        self.assertTrue(self.__class__.client.is_present('data1'), 'data1 file not present')
        self.assertFalse(self.__class__.client.is_present('data1.md5'), 'data1.md5 file is present')
        self.assertFalse(self.__class__.client.is_present('data1.sha256'),'data1.sha256 file is present')

    def test_timeout(self):
        for i in range(6, 0, -1):
            print('\rWait %d sec' % i, end='')
            time.sleep(1)
        print('')

        self.assertFalse(self.__class__.client.is_connected(), 'client still connected')
        self.__class__.client.get_file('data1')
        self.assertTrue(self.__class__.client.is_connected(), 'client not connected')

    def test_get_file(self):
        self.assertIsNotNone(self.__class__.client.get_file('data1'),'unable to get data1')

    def test_verification(self):
        self.__class__.client.get_file('data2', verify='md5')
        self.__class__.client.get_file('data2', verify='sha256')
        exception_raised = False
        try:
            self.__class__.client.get_file('data2', verify='zzz')
        except Exception as e:
            exception_raised = True
            print(e)
        self.assertTrue(exception_raised, 'No exception raised')


if __name__ == '__main__':
    Helpers.configure_logger(logging.DEBUG)
    unittest.main()


