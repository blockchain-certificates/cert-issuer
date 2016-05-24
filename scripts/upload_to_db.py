import csv
import glob
import json

from issuer import config, helpers

with open('certs_dbdump.csv', 'w') as csvfile:
    fieldnames = ['_id', 'issued', 'pubkey', 'txid']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for filename in glob.glob(config.SENT_TXS_FOLDER + "*"):
        uid = helpers.get_uid(filename)
        txid = open(filename, 'r').read()
        pubkey = json.loads(open(config.SIGNED_CERTS_FOLDER + uid + ".json", "r").read())["recipient"]["pubkey"]
        issued = True
        writer.writerow({'_id': uid, 'issued': issued, 'txid': txid, 'pubkey': pubkey})


def get_uid(filename):
    if "/" in filename:
        filename = filename.split("/")[-1]
    if "." in filename:
        filename = filename.split(".")[0]
    return filename
