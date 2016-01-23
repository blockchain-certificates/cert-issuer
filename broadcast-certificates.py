#!/usr/bin/env python3

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

import glob
import pickle

import bitcoin.rpc
from bitcoin import params
from bitcoin.core import *
from bitcoin.core.script import *

import config
import helpers

proxy = bitcoin.rpc.Proxy()

def send_txs():
	for f in glob.glob(config.UNSENT_CERTS_FOLDER+"*"):
		uid = helpers.get_uid(f)
		hextx = str(open(f, 'rb').read(), 'utf-8')
		# tx = CMutableTransaction.from_tx(hex_tx)
		txid = b2lx(lx(proxy._call('sendrawtransaction', hextx)))
		open(config.SENT_CERTS_FOLDER + uid + ".txt", "wb").write(bytes(txid, 'utf-8'))
		print("Broadcast transaction for certificate id %s with a txid of %s" % (uid, txid))

send_txs()