import logging
import time
import os
import unittest
from multiprocessing import Process

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))

from quickftp.qftp_helper import Helpers
from quickftp.qftp_client import QuickFtpClient
from quickftp.qftp_server import QuickFtpServer


class TestClient(unittest.TestCase):
    """
    Test the qftp client
    """
    client = None

    @classmethod
    def setUpClass(cls):
        print('Launch server')
        cls.launch_server()
        time.sleep(2)
        print('Server Launched')

    @classmethod
    def server_handler(cls):
        Helpers.configure_logger(logging.ERROR)
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        s = QuickFtpServer(os.path.join(current_dir_path, 'conf/server_conf.yml'))
        s.serve()

    @classmethod
    def launch_server(cls):
        server = Process(target=cls.server_handler)
        server.daemon = True
        server.start()

    def test_connect(self):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))

        with self.assertRaises(Exception):
            QuickFtpClient(os.path.join(current_dir_path, 'conf/wrong_client_conf.yml'))

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
        self.__class__.client.get('data1')
        self.assertTrue(self.__class__.client.is_connected(), 'client not connected')

    def test_get_file(self):
        self.assertIsNotNone(self.__class__.client.get('data1'), 'unable to get data1')
        self.assertIsNotNone(self.__class__.client.get('/data1'), 'unable to get data1')
        self.assertIsNotNone(self.__class__.client.get('./data1'), 'unable to get data1')
        self.assertIsNotNone(self.__class__.client.get('/directory/../data1'), 'unable to get data1')

    def test_verification(self):
        self.__class__.client.get('data2', verify='md5')
        self.__class__.client.get('data2', verify='sha256')

        # wrong signature format
        with self.assertRaises(Exception):
            self.__class__.client.get('data2', verify='zzz')

        # no signature file
        with self.assertRaises(Exception):
            self.__class__.client.get('data3', verify='md5')

        # wrong signature
        with self.assertRaises(Exception):
            self.__class__.client.get('data3', verify='sha256')

    def test_get_dir(self):
        self.assertIsNotNone(self.__class__.client.get(''), 'unable to get root directory')
        self.assertIsNotNone(self.__class__.client.get('directory'), 'unable to get directory')
        self.assertIsNotNone(self.__class__.client.get('directory/subdirectory', verify='md5'),
                             'unable to get directory/subdirectory')

if __name__ == '__main__':
    Helpers.configure_logger(logging.DEBUG)
    unittest.main()
