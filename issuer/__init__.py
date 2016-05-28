#!/usr/bin/env python

import logging

import os
from functools import partial
from . import config
from . import helpers

__version__ = '0.0.1'


# partial function to use for conditional wifi checks. Disable this check for unit tests
def _internet_off_for_scope_check(func, secrets_file_path, skip_wifi_check):
    def generate_decorator(*args, **kwargs):
        if skip_wifi_check:
            return func(*args, **kwargs)

        helpers.check_internet_off(secrets_file_path)
        result = func(*args, **kwargs)
        helpers.check_internet_on(secrets_file_path)
        return result

    return generate_decorator


def main(argv=None):

    # Configure logging settings; create console handler and set level to info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    parsed_config, _ = config.parse_args()
    global internet_off_for_scope
    skip_wifi_check = parsed_config.skip_wifi_check
    if skip_wifi_check:
        logging.warning('Your app is configured to skip the wifi check when the USB is plugged in. Read the '
                        'documentation to ensure this is what you want, since this is less secure')

    secrets_file_path = os.path.join(parsed_config.usb_name, parsed_config.key_file)
    internet_off_for_scope = partial(_internet_off_for_scope_check, secrets_file_path=secrets_file_path,
                                     skip_wifi_check=skip_wifi_check)

    from . import create_certificates
    create_certificates.main(parsed_config)

internet_off_for_scope = partial(_internet_off_for_scope_check, secrets_file_path='SEE_CONFIG_OPTIONS.txt',
                                 skip_wifi_check=True)




