import secrets
from datetime import datetime
import requests
import json
import os

def get_uid(filename):
    if "/" in filename:
        filename = filename.split("/")[-1]
    if "." in filename:
        filename = filename.split(".")[0]
    return filename

def import_key():
    key = open(secrets.KEYPATH).read().strip()
    return key

def internet_on():
    """Pings Google to see if the internet is on. If online, returns true. If offline, returns false."""
    r = requests.get('http://google.com')
    print(r.status_code)
    if int(r.status_code) != 200:
        return False
    return True

def check_internet_off():
    """If internet off and USB plugged in, returns true. Else, continues to wait..."""
    while(1):
        i = input("Turn internet OFF and PLUG IN usb. Type CONTINUE to continue...\n")
        if i.lower() == "continue" and internet_on() == False and os.path.exists(secrets.USB_NAME) == True:
            break
    return True

def check_internet_on():
    """If internet is on and USB is not plugged in, returns true. Else, continues to wait..."""
    while(1):
        i = input("Turn internet ON and UNPLUG usb. Type CONTINUE to continue...\n")
        if i.lower() == "continue" and internet_on() == True and os.path.exists(secrets.USB_NAME) == False:
            break
    return True