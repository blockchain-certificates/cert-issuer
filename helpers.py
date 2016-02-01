import secrets
from datetime import datetime
import requests
import json
import glob
import os
import time
import config

def calculate_txfee(num_inputs, num_outputs):
    satoshi_per_byte = 41
    tx_size = num_inputs*180 + num_outputs*34 + 10 + num_inputs
    tx_fees = satoshi_per_byte * tx_size
    if tx_fees < (config.TX_FEES * config.COIN):
        return config.TX_FEES * config.COIN
    return tx_fees

def get_uid(filename):
    if "/" in filename:
        filename = filename.split("/")[-1]
    if "." in filename:
        filename = filename.split(".")[0]
    return filename

def import_key():
    secrets.KEYPATH = secrets.KEYPATH.replace(" ", "\ ")
    key = open(secrets.KEYPATH).read().strip()
    return key

def clear_folder(foldername):
    files = glob.glob(foldername+'*')
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
    while(1):
        if internet_on() == False and os.path.exists(secrets.USB_NAME) == True:
            break
        else:
            print("Turn off your internet and plug in your USB to continue...")
            time.sleep(10)
    return True

def check_internet_on():
    """If internet is on and USB is not plugged in, returns true. Else, continues to wait..."""
    while(1):
        if internet_on() == True and os.path.exists(secrets.USB_NAME) == False:
            break
        else:
            print("Turn on your internet and unplug your USB to continue...")
            time.sleep(10)
    return True
