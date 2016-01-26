#!/usr/bin/env python3

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

import glob
import pickle
import requests

import bitcoin.rpc
from bitcoin import params
from bitcoin.core import *
from bitcoin.core.script import *

import config
import helpers

proxy = bitcoin.rpc.Proxy()

def send_txs():
    for f in glob.glob(config.UNSENT_TXS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        hextx = str(open(f, 'rb').read(), 'utf-8')
        if config.REMOTE_CONNECT == True:
            r = requests.post("https://insight.bitpay.com/api/tx/send", json={"rawtx": hextx})
            if int(r.status_code) != 200:
                sys.stderr.write("Error broadcasting the transaction through the Insight API. Error msg: %s" % r.text)
                sys.exit(1)
            else:
                txid = r.json().get('txid', None)
        else:
            txid = b2lx(lx(proxy._call('sendrawtransaction', hextx)))
        open(config.SENT_TXS_FOLDER + uid + ".txt", "wb").write(bytes(txid, 'utf-8'))
        print("Broadcast transaction for certificate id %s with a txid of %s" % (uid, txid))

send_txs()