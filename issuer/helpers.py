import binascii
import glob
import logging
import os
import shutil
import sys
import time

import glob2
import requests
from issuer import config

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')


def internet_off_for_scope(func):
    def func_wrapper(*args, **kwargs):
        check_internet_off()
        result = func(*args, **kwargs)
        check_internet_on()

    return func_wrapper


def import_key():
    with open(os.path.join(config.CONFIG.usb_name, config.CONFIG.key_file)) as key_file:
        key = key_file.read().strip()
    return key


def convert_file_name(to_pattern, cert_uid):
    return to_pattern.replace('*', cert_uid)


def clear_folder(foldername):
    files = glob.glob(foldername + '*')
    for f in files:
        os.remove(f)
    return True


def internet_on():
    """Pings Google to see if the internet is on. If online, returns true. If offline, returns false."""
    try:
        r = requests.get('http://google.com')
        return True
    except requests.exceptions.RequestException as e:
        return False


def check_internet_off():
    """If internet off and USB plugged in, returns true. Else, continues to wait..."""
    if config.CONFIG.skip_wifi_check:
        logging.warning('app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                        ' ensure this is what you want, since this is less secure')
        return True
    while 1:
        if internet_on() == False and os.path.exists(config.CONFIG.usb_name) == True:
            break
        else:
            print("Turn off your internet and plug in your USB to continue...")
            time.sleep(10)
    return True


def check_internet_on():
    """If internet is on and USB is not plugged in, returns true. Else, continues to wait..."""
    if config.CONFIG.skip_wifi_check:
        logging.warning('app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                        ' ensure this is what you want, since this is less secure')
        return True
    while 1:
        if internet_on() == True and os.path.exists(config.CONFIG.usb_name) == False:
            break
        else:
            print("Turn on your internet and unplug your USB to continue...")
            time.sleep(10)
    return True


def archive_files(from_pattern, to_pattern, timestamp):
    [shutil.copyfile(filename,
                     convert_file_name(to_pattern, uid) + '-' + timestamp)
     for filename, (uid,) in glob2.iglob(from_pattern, with_matches=True)]


def clear_intermediate_folders():
    folders_to_clear = [config.CONFIG.signed_certs_file_pattern,
                        config.CONFIG.hashed_certs_file_pattern,
                        config.CONFIG.unsigned_txs_file_pattern,
                        config.CONFIG.unsent_txs_file_pattern,
                        config.CONFIG.sent_txs_file_pattern]
    for folder in folders_to_clear:
        clear_folder(folder)
