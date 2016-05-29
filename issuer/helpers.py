import binascii
import glob
import sys
import time

import glob2
import os
import requests
import shutil
from issuer import config
import logging

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')

secrets_file_path = os.path.join(config.get_config().usb_name, config.get_config().key_file)


def internet_off_for_scope(func):
    def func_wrapper(*args, **kwargs):
        check_internet_off()
        result = func(*args, **kwargs)
        check_internet_on()

    return func_wrapper


def import_key():
    with open(secrets_file_path) as key_file:
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
    if config.get_config().skip_wifi_check:
        logging.warning(
            'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
            ' ensure this is what you want, since this is less secure')
        return True
    
    while 1:
        if internet_on() == False and os.path.exists(secrets_file_path):
            break
        else:
            print("Turn off your internet and plug in your USB to continue...")
            time.sleep(10)
    return True


def check_internet_on():
    """If internet off and USB plugged in, returns true. Else, continues to wait..."""
    if config.get_config().skip_wifi_check:
        logging.warning(
            'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
            ' ensure this is what you want, since this is less secure')
        return True
    while 1:
        if internet_on() == True and not os.path.exists(secrets_file_path):
            break
        else:
            print("Turn on your internet and unplug your USB to continue...")
            time.sleep(10)
    return True


def archive_files(from_pattern, to_pattern, timestamp):
    [shutil.copyfile(filename,
                     convert_file_name(to_pattern, uid) + '-' + timestamp)
     for filename, (uid,) in glob2.iglob(from_pattern, with_matches=True)]


def clear_intermediate_folders(config):
    folders_to_clear = [config.signed_certs_file_pattern,
                        config.hashed_certs_file_pattern,
                        config.unsigned_txs_file_pattern,
                        config.unsent_txs_file_pattern,
                        config.sent_txs_file_pattern]
    for folder in folders_to_clear:
        clear_folder(folder)
