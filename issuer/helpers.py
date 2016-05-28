import binascii
import glob
import sys
import time

import glob2
import os
import requests
import shutil

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')


def import_key(secret_file_path):
    with open(secret_file_path) as key_file:
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


def check_internet_off(usb_name):
    """If internet off and USB plugged in, returns true. Else, continues to wait..."""
    while 1:
        if internet_on() == False and os.path.exists(usb_name) == True:
            break
        else:
            print("Turn off your internet and plug in your USB to continue...")
            time.sleep(10)
    return True


def check_internet_on(usb_name):
    """If internet is on and USB is not plugged in, returns true. Else, continues to wait..."""
    while 1:
        if internet_on() == True and os.path.exists(usb_name) == False:
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
