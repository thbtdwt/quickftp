import os
import logging
from ftplib import FTP
from quickftp.qftp_helper import Helpers


class QuickFtpClient:
    """
    This provides few functions to get a file from a ftp server.
    """
    def __init__(self, _configfile):
        """
        Constructor: Read configuration file and try to connect to the server.
        :param _configfile: configuration file
        """
        if not _configfile:
            raise Exception('Missing parameter _configfile')

        self.configfile = os.path.abspath(_configfile)
        parameters = Helpers.get_param_from_config_file(self.configfile,
                                                        ['ip', 'port', 'username','password', 'workspace'])
        self.server_ip = parameters['ip']
        self.server_port = int(parameters['port'])
        self.username = parameters['username']
        self.password = parameters['password']
        self.workspace = os.path.abspath(parameters['workspace'])
        self.data_dir = os.path.join(self.workspace,'data')

        Helpers.create_dir_if_not_exist(self.workspace)

        self.ftp = FTP()
        self.__connect()

    def __connect(self):
        """
        Private function to connect to the server
        :return:
        """
        try:
            self.ftp.connect(self.server_ip, self.server_port)
            self.ftp.login(self.username, self.password)
        except Exception:
            logging.error('Cannot connect to %s:%d' % (self.server_ip, self.server_port))

    def is_connected(self):
        """
        Provides the connection status: connected or not
        :return: True is connected
        """
        try:
            self.ftp.pwd()
        except Exception:
            return False
        return True

    def is_present(self, fname):
        """
        Provides the presence status of a file: present or not on the server
        :param fname: file path
        :return: True is present
        """
        try:
            dir_content = self.ftp.mlsd(os.path.dirname(fname),['type'])
            for entry in dir_content:
                name, tmp = entry
                if name == fname:
                    return True
            return False
        except Exception:
            return False

    def __get_file(self, fname, to=None):
        """
        Private function to get a file from the server.
        :param fname: file path on the server
        :param to: local directory where the file will be copied
        :return: the local file path
        """
        dst = os.path.join(to, fname)

        with open(dst, 'wb') as file:
            try:
                logging.debug('get "%s"', fname)
                self.ftp.retrbinary('RETR ' + fname, file.write)
            except Exception:
                raise Exception('Unable to get %s file from %s:%d' % (fname, self.server_ip, self.server_port))
        return dst

    def get_file(self, fname, to=None, verify=None):
        """
        Gets a file from the server, and optionally verify the signature
        :param fname: file path on the server
        :param to: local directory where the file will be copied
        :param verify: 'md5' or 'sha256'
        :return: the local file path
        """
        # check arguments
        if verify and verify not in ['md5', 'sha256']:
            raise Exception('verify must be md5 or sha256')

        if to:
            if not os.path.isdir(to):
                raise Exception('%s is not a directory' % to)
        else:
            to = self.workspace

        # Re-connect if needed
        if not self.is_connected():
            logging.info('Not connect, re-connect...')
            self.__connect()

        file_path = self.__get_file(fname, to)

        if verify:
            signature_fname = fname + '.' + verify
            if self.is_present(signature_fname):
                signature_file_path = self.__get_file(signature_fname, to)
                Helpers.verify_signature(file_path, signature_file_path)
            else:
                raise Exception('No %s found' % signature_fname)
        return file_path


