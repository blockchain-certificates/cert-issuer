import binascii
import glob
import logging
import sys
import time
import hashlib

import glob2
import os
import requests
import shutil
from cert_issuer import config, models

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')

secrets_file_path = os.path.join(
    config.get_config().usb_name, config.get_config().key_file)


def internet_off_for_scope(func):
    """
    Wraps func with check that internet is off, then on after the call to func
    :param func:
    :return:
    """

    def func_wrapper(*args, **kwargs):
        check_internet_off()
        result = func(*args, **kwargs)
        check_internet_on()
        return result

    return func_wrapper


def import_key():
    with open(secrets_file_path) as key_file:
        key = key_file.read().strip()
    return key


def clear_folder(folder_name):
    files = glob.glob(folder_name + '*')
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

    while True:
        if internet_on() is False and os.path.exists(secrets_file_path):
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
    while True:
        if internet_on() is True and not os.path.exists(secrets_file_path):
            break
        else:
            print("Turn on your internet and unplug your USB to continue...")
            time.sleep(10)
    return True


def archive_files(from_pattern, archive_dir, to_pattern, batch_id):
    """
    Archives files matching from_pattern and renames to to_pattern based on uid in a batch folder
    :param from_pattern:
    :param to_pattern:
    :param timestamp:
    :return:
    """
    # place archived files in a timestamped folder
    archive_folder = os.path.join(archive_dir, batch_id)
    if not os.path.isdir(archive_folder):
        os.mkdir(archive_folder)
        os.mkdir(os.path.join(archive_folder, 'unsigned_certs'))
        os.mkdir(os.path.join(archive_folder, 'signed_certs'))
        os.mkdir(os.path.join(archive_folder, 'sent_txs'))
        os.mkdir(os.path.join(archive_folder, 'receipts'))
        os.mkdir(os.path.join(archive_folder, 'blockchain_certificates'))

    archived_file_pattern = os.path.join(archive_folder, to_pattern)
    [shutil.move(filename, models.convert_file_name(archived_file_pattern, uid))
     for filename, (uid,) in glob2.iglob(from_pattern, with_matches=True)]


def clear_intermediate_folders(app_config):
    folders_to_clear = [app_config.hashed_certs_file_pattern,
                        app_config.unsigned_txs_file_pattern,
                        app_config.signed_txs_file_pattern,
                        app_config.sent_txs_file_pattern]
    for folder in folders_to_clear:
        clear_folder(folder)


def get_current_time_ms():
    current_time = int(round(time.time() * 1000))
    return current_time

def get_batch_id(uids):
    """
    Need to get a deterministic batch id from file names. uids are assumed to be sorted. Throughout this app we store
    certificates in OrderedDicts.
    """
    return hashlib.md5(''.join(uids).encode('utf-8')).hexdigest()