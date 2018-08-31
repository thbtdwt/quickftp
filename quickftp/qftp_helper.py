import os
import yaml
import logging
from hashlib import md5
from hashlib import sha256


class Helpers:
    """
    This class regroups helper function used by qftp server and client
    """

    @staticmethod
    def create_dir_if_not_exist(dname):
        """
        Create a directory is not exist
        :param dname: directory path
        :return:
        """
        if not os.path.exists(dname):
            logging.info('Create %s', dname)
            os.makedirs(dname)

    @staticmethod
    def get_param_from_config_file(configfile, mandatory_parameter_list, optional_parameter_list=[]):
        """
        Read yaml configuration file, checks that mandatory parameters are present and
        extract mandatory and optional parameters.
        :param configfile: config file path
        :param mandatory_parameter_list: list of mandatory parameters
        :param optional_parameter_list: list of optional parameters
        :return: parameter dictionary
        """
        result = dict()
        logging.info('open %s', configfile)
        with open(configfile, 'r') as file:
            yaml_data = yaml.load(file)

        for param in mandatory_parameter_list:
            logging.debug('Check parameter %s', param)
            try:
                result[param] = yaml_data[param]
            except Exception:
                raise Exception('Missing parameter "%s" in %s' % (param, configfile))
        for param in optional_parameter_list:
            logging.debug('Check parameter %s', param)
            try:
                result[param] = yaml_data[param]
            except Exception:
                logging.debug('No "%s" found in %s' % (param, configfile))
        return result

    @staticmethod
    def configure_logger(level):
        # todo must be remove for here
        logger = logging.getLogger()

        logger.setLevel(level)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
        logger.addHandler(stream_handler)

    @staticmethod
    def compute_file_hash(fname, hash_type):
        """
        Compute an hash fot a given file
        :param fname: file path
        :param hash_type: 'md5' or 'sha256'
        :return: the hash string
        """
        if 'md5' == hash_type:
            file_hash = md5()
        elif 'sha256' == hash_type:
            file_hash = sha256()
        else:
            raise Exception('Unknown hash type')

        with open(fname, "rb") as f:
            for data in iter(lambda: f.read(4096), b""):
                file_hash.update(data)
        return file_hash.hexdigest()

    @staticmethod
    def verify_signature(fname, f_hash_signature_name):
        """
        Verify that the signature match with a file
        :param fname: file path (eg: 'myfile')
        :param f_hash_signature_name: signature file path (ig: 'myfile.md5')
        :return:
        """

        hash_type = f_hash_signature_name.rpartition('.')[2]
        if hash_type not in ['md5', 'sha256']:
            raise Exception('Unable to get type of ' % f_hash_signature_name)

        logging.debug('Read hash from %s' % f_hash_signature_name)
        with open(f_hash_signature_name, "r") as file:
            expected_hash = file.readline().rstrip()
            logging.debug('Expected hash %s' % expected_hash)

        file_hash = Helpers.compute_file_hash(fname, hash_type)
        logging.debug('Computed hash %s' % file_hash)

        if file_hash != expected_hash:
            raise Exception('%s bad signature: "%s" excepted "%s"' % (fname, file_hash, expected_hash))


