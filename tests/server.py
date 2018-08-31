import argparse
import logging

from quickftp.qftp_helper import Helpers
from quickftp.qftp_server import QuickFtpServer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="getLaunchServer")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose")
    parser.add_argument('-cf', '--config-file', dest="configfile", help="config file")
    args = parser.parse_args()

    if args.verbose:
        Helpers.configure_logger(logging.DEBUG)
    else:
        Helpers.configure_logger(logging.INFO)

    # check error
    try:
        server = QuickFtpServer(None)
    except Exception as e:
        print(e)

    server = QuickFtpServer(args.configfile)
    server.serve()