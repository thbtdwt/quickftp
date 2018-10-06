import os
import logging
from ftplib import FTP
from quickftp.qftp_helper import Helpers
import re

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

    def __is_dir_pathname(self, pathname):
        """
        :param pathname: path name
        :return: True if the path is a directory
        """
        if len(pathname) == 0:
            return True
        else:
            last_char = pathname.strip()[-1]
            if last_char == '.' or last_char == '/':
                return True
        return False

    def __get_type(self, fpath):
        """
        Provides the type of a file
        :param fpath: file path
        :return: 'file', 'dir' or none
        """
        if self.__is_dir_pathname(fpath):
            return 'dir'

        try:
            dir_content = self.ftp.mlsd(os.path.dirname(fpath), ['type'])
            for entry in dir_content:
                name, attribute = entry
                if name == os.path.basename(fpath):
                    return attribute['type']
            return None
        except Exception as e:
            print(e)
            return None

    def __get_content_list(self, dpath):
        """
        Get the list of file of a directory
        :param dpath: file path on the server
        :return: filename list of current directory
        """
        logging.debug('get content list of %s', dpath)
        file_list = []
        dir_content = self.ftp.mlsd(dpath, ['type'])
        for entry in dir_content:
            name, tmp = entry
            if not re.match('.*\.(md5|sha256)$', name):
                file_list.append(name)
        return file_list

    def is_present(self, fpath):
        """
        Provides the presence status of a file: present or not on the server
        :param fpath: file path
        :return: True is present
        """
        if self.__get_type(fpath):
            return True
        else:
            return False

    def __get_file_from_server(self, fpath, to):
        """
        Private function to get a file from the server.
        :param fpath: file path on the server
        :param to: local directory where the file will be copied
        :return: the local file path
        """
        dst = os.path.join(to, os.path.basename(fpath))

        with open(dst, 'wb') as file:
            try:
                logging.debug('get "%s"', fpath)
                self.ftp.retrbinary('RETR ' + fpath, file.write)
            except Exception:
                raise Exception('Unable to get %s file from %s:%d' % (fpath, self.server_ip, self.server_port))
        return dst

    def __get_file(self, fpath, to, verify):
        """
        Private function to get a file.
        :param fpath: file path on the server
        :param to: local directory where the file will be copied
        :param verify: 'md5' or 'sha256'
        :return: the local file path
        """
        logging.debug('get file "%s"' % fpath)

        type = self.__get_type(fpath)

        if type == 'dir':
            logging.debug('%s is a directory' % fpath)
            local_dir = os.path.join(to, fpath)
            if not os.path.isdir(local_dir):
                logging.debug('Create %s', local_dir)
                os.makedirs(local_dir)

            for f in self.__get_content_list(fpath):
                self.__get_file(os.path.join(fpath, f), local_dir, verify)

            return os.path.join(to, fpath)

        elif type == 'file':
            file_path = self.__get_file_from_server(fpath, to)

            if verify:
                signature_filename = fpath + '.' + verify
                if self.is_present(signature_filename):
                    signature_file_path = self.__get_file_from_server(signature_filename, to)
                    Helpers.verify_signature(file_path, signature_file_path)
                else:
                    raise Exception('No %s found' % signature_filename)
            return file_path
        else:
            raise Exception('Unable to get type of %s' % fpath)

    def get(self, fpath, to=None, verify=None):
        """
        Gets a file from the server, and optionally verify the signature
        :param fpath: file path on the server
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

        return self.__get_file(os.path.normpath(fpath), to, verify)
