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

    print('Connected: %s' % str(client.is_connected()))

    print('data1 file present: %s' % str(client.is_present('data1')))
    print('data1.md5 file present: %s' % str(client.is_present('data1.md5')))
    print('data1.sha256 file present: %s' % str(client.is_present('data1.sha256')))

    for i in range(35, 0, -1):
        print('\rWait %d sec' % i, end='')
        time.sleep(1)
    print('')

    print('Connected: %s' % str(client.is_connected()))
    client.get_file('data1')
    print('Connected: %s' % str(client.is_connected()))
    client.get_file('data2', verify='md5')
    client.get_file('data2', verify='sha256')

    try:
        client.get_file('data2', verify='zzz')
    except Exception as e:
        print(e)


