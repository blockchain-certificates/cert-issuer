import secrets

def get_uid(filename):
    if "/" in filename:
        filename = filename.split("/")[-1]
    if "." in filename:
        filename = filename.split(".")[0]
    return filename

def import_key():
    key = open(secrets.KEYPATH).read().strip()
    return key
