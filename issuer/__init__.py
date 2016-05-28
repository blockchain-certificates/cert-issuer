#!/usr/bin/env python

import logging

from functools import partial
from . import config
from . import create_certificates
from . import create_certificates
from . import helpers

internet_off_for_scope = None


__version__ = '0.0.1'


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
    internet_off_for_scope = partial(_internet_off_for_scope_check, skip_wifi_check=skip_wifi_check)

    create_certificates.main(parsed_config)


def _internet_off_for_scope_check(func, skip_wifi_check):
    def generate_decorator(*args, **kwargs):
        if skip_wifi_check:
            return func(*args, **kwargs)

        helpers.check_internet_off()
        result = func(*args, **kwargs)
        helpers.check_internet_on()
        return result

    return generate_decorator

