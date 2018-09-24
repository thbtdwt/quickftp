import logging
import unittest
import os
from threading import Thread
import time

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))

from quickftp.qftp_helper import Helpers
from quickftp.qftp_server import QuickFtpServer


class TestServer(unittest.TestCase):
    """
    Test the qftp server
    """
    server = None

    def test_config_file(self):
        # No config file
        exception_raised = False
        try:
            self.__class__.server = QuickFtpServer(None)
        except Exception as e:
            exception_raised = True
            print(e)

        self.assertTrue(exception_raised, 'No exception raised')

    def test_terminate(self):
        server_thread = Thread(target=self.launch_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(10)
        self.__class__.server.terminate()

    def launch_server(self):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__class__.server = QuickFtpServer(os.path.join(current_dir_path, 'conf/server_conf.yml'))
        self.__class__.server.serve()


if __name__ == '__main__':
    Helpers.configure_logger(logging.DEBUG)
    unittest.main()



