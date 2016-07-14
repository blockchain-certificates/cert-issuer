#!/usr/bin/env python3

import sys

import os.path

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(PATH, 'conf.ini')

if __package__ is None and not hasattr(sys, 'frozen'):
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


def main(args=None):
    from cert_issuer import config
    parsed_config = config.get_config()
    from cert_issuer import create_certificates
    create_certificates.main(parsed_config)


if __name__ == '__main__':
    main()
