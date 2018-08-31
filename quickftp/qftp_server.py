import os
from hashlib import md5
import logging
from quickftp.qftp_helper import Helpers

from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer


class QuickFtpAuthorizer(DummyAuthorizer):
    """
    This class is user to check user password.
    """
    def validate_authentication(self, username, password, handler):
        """
        Compute md5 of password provided by the user and compare with the local one.
        :param username: user name
        :param password: password provided by the user
        :param handler: FTP handler
        :return:
        """
        password = password.encode('utf-8')
        hash_md5 = md5(password).hexdigest()
        logging.debug("Check %s's password %s hash %s", username, password, hash_md5)
        try:
            if self.user_table[username]['pwd'] != hash_md5:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed


class QuickFtpServer:
    """
    This class provides a tfp server configured through a config file.
    """
    def __init__(self, _configfile):
        """
        Constructor
        :param _configfile: path to the configuration file.
        """
        if not _configfile:
            raise Exception('Missing parameter _configfile')

        self.configfile = os.path.abspath(_configfile)


        # parse config file
        parameters = Helpers.get_param_from_config_file(self.configfile,
                                                        ['ip', 'port', 'ftp_root_dir', 'clients'],
                                                        ['client_timeout', 'pem_certificate'])
        self.ip = parameters['ip']
        self.port = int(parameters['port'])
        self.root_dir = os.path.abspath(parameters['ftp_root_dir'])

        # use certificate ?
        if parameters['pem_certificate']:
            pem = os.path.abspath(parameters['pem_certificate'])
            logging.info('TLS mode use %s', pem)
            if not os.path.exists(pem):
                raise IOError('File: ' + pem + ' not found')
            self.handler = TLS_FTPHandler
            self.handler.certfile = pem
        else:
            logging.info('Unsecure mode')
            self.handler = FTPHandler

        # Use timeout ?
        if parameters['client_timeout']:
            self.handler.timeout = int(parameters['client_timeout'])

        if not os.path.exists(self.root_dir):
            logging.debug('Create %s', self.root_dir)
            os.makedirs(self.root_dir)

        self.authorizer = QuickFtpAuthorizer()
        for client in parameters['clients']:
            user_dir = os.path.join(self.root_dir, client['directory'])
            if not os.path.exists(user_dir):
                logging.debug('Create %s', user_dir)
                os.makedirs(user_dir)
            logging.info('Add user %s with directory %s',
                             client['name'], user_dir)
            self.authorizer.add_user(client['name'],
                                     client['password'],
                                     user_dir,
                                     perm='elr')

        self.handler.authorizer = self.authorizer

    def serve(self):
        """
        run the server forever
        :return:
        """
        server_inst = FTPServer((self.ip, self.port), self.handler)
        logging.info('Listen on %s:%d',
                         self.ip, self.port)
        server_inst.serve_forever()
