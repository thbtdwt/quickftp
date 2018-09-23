import argparse
import logging
import time

from quickftp.qftp_helper import Helpers
from quickftp.qftp_client import QuickFtpClient

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ALClient")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose")
    parser.add_argument('-cf', '--config-file', dest="configfile", help="config file")
    args = parser.parse_args()

    if args.verbose:
        Helpers.configure_logger(logging.DEBUG)
    else:
        Helpers.configure_logger(logging.INFO)

    client = QuickFtpClient(args.configfile)

    requested_file = input('What file do you want ?')

    if not client.is_present(requested_file):
        print('%s not present' % requested_file)

    try:
        if client.is_present(requested_file + '.md5'):
            local_path = client.get_file(requested_file, verify='md5')
        elif client.is_present(requested_file + '.sha256'):
            local_path = client.get_file(requested_file, verify='sha256')
        else:
            local_path = client.get_file(requested_file)
        print('File copied in %s' % local_path)
    except Exception as e:
        print(e)




