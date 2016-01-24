#!/usr/bin/env python3

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)

import hashlib
import bitcoin.rpc
import sys
import json
import glob
import binascii
import pickle

from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx.tx_utils import *
from pycoin.tx import *
from pycoin.services import get_tx_db

from bitcoin import params
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

import simplejson
import bitcoin.rpc
bitcoin.rpc.json = simplejson

from subprocess import check_output

import config
import helpers
import secrets

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')

revoke_addr = CBitcoinAddress(secrets.REVOCATION_ADDRESS)
revoke_out = CMutableTxOut(int(config.BLOCKCHAIN_DUST*COIN), revoke_addr.to_scriptPubKey())

change_addr = CBitcoinAddress(secrets.ISSUING_ADDRESS)
change_out = CMutableTxOut(int(config.BLOCKCHAIN_DUST*COIN), change_addr.to_scriptPubKey())

proxy = bitcoin.rpc.Proxy(service_url=secrets.PROXY_URL, service_port=secrets.PROXY_PORT)

address_balance = proxy.getreceivedbyaddress(addr=secrets.ISSUING_ADDRESS)
cost_to_issue = int((config.BLOCKCHAIN_DUST*2+config.TX_FEES)*COIN) * len(glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"))
if address_balance < cost_to_issue:
    sys.stderr.write('Sorry, please add %s BTC to the address %s.\n' % ((address_balance - cost_to_issue)/COIN, secrets.ISSUING_ADDRESS))
    sys.exit(1)

def prepare_certs():
    cert_info = {}
    for f in glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"):
        cert = json.loads(open(f).read())
        cert_info[f.split("/")[-1].split(".")[0]] = {
            "name": cert["recipient"]["givenName"] + " " + cert["recipient"]["familyName"],
            "pubkey": cert["recipient"]["pubkey"]
        }
    print("Starting script...\n")
    return cert_info


# Sign the certificates
def sign_certs():
    privkey = CBitcoinSecret(helpers.import_key())
    for f in glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"):
        uid = helpers.get_uid(f)
        cert = json.loads(open(f).read())
        message = BitcoinMessage(cert["assertion"]["uid"])
        print("Signing certificate for recipient id: %s" % (uid))
        signature = SignMessage(privkey, message)
        cert["signature"] = str(signature, 'utf-8')
        cert = json.dumps(cert)
        open(config.SIGNED_CERTS_FOLDER+uid+".json", "wb").write(bytes(cert, 'utf-8'))
        return "Signed certificates for recipients\n"

# Hash the certificates
def hash_certs():
    for f in glob.glob(config.SIGNED_CERTS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        cert = open(f, 'rb').read()
        print("Hashing certificate for recipient id: %s" % (uid))
        hashed_cert = hashlib.sha256(cert).digest()
        open(config.HASHED_CERTS_FOLDER + uid + ".txt", "wb").write(hashed_cert)
        return "Hashed certificates for recipients\n"

# Make transactions for the certificates
def build_cert_txs():
    for f in glob.glob(config.HASHED_CERTS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        cert = open(f, 'rb').read()
        print("Creating tx of certificate for recipient id: %s" % (uid))

        txouts = []
        unspent = sorted(proxy.listunspent(addrs=[secrets.ISSUING_ADDRESS]), key=lambda x: hash(x['amount']))

        txins = [CTxIn(unspent[-1]['outpoint'])]
        value_in = unspent[-1]['amount']

        recipient_addr = CBitcoinAddress(cert_info[uid]["pubkey"])
        recipient_out = CMutableTxOut(int(config.BLOCKCHAIN_DUST*COIN), recipient_addr.to_scriptPubKey())

        cert_outs = [CMutableTxOut(0, CScript([OP_RETURN, cert]))]
        txouts = [recipient_out] + [revoke_out] + [change_out] + cert_outs
        tx = CMutableTransaction(txins, txouts)

        while True:
            tx.vout[2].nValue = int(value_in-((config.BLOCKCHAIN_DUST*2+config.TX_FEES)*COIN))
            r = proxy.signrawtransaction(tx, None, [helpers.import_key()])
            assert r['complete']
            tx = r['tx']
            if value_in - tx.vout[0].nValue >= config.BLOCKCHAIN_DUST:
                tx = hexlify(tx.serialize())
                open(config.UNSENT_CERTS_FOLDER + uid + ".txt", "wb").write(bytes(tx, 'utf-8'))
                break
        return "Created txs for recipients\n"

def verify_cert_txs():

    def verify_signature(address, signed_cert):
        message = BitcoinMessage(signed_cert["assertion"]["uid"])
        signature = signed_cert["signature"]
        return VerifyMessage(address, message, signature)

    def verify_doc(uid):
        # hashed_cert = hashlib.sha256(str(signed_cert).encode('utf-8')).hexdigest()
        hashed_cert = hashlib.sha256(open(config.SIGNED_CERTS_FOLDER+uid+".json", 'rb').read()).hexdigest()
        op_return_hash = open(config.UNSENT_CERTS_FOLDER+uid+".txt").read()[-72:-8]
        if hashed_cert == op_return_hash:
            return True
        return False


    for f in glob.glob(config.UNSENT_CERTS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        print("UID: \t\t\t" + uid)
        print("VERIFY SIGNATURE: \t%s " % (verify_signature(secrets.ISSUING_ADDRESS, json.loads(open(config.SIGNED_CERTS_FOLDER+uid+".json").read()))))
        print("VERIFY_OP_RETURN: \t%s " % (verify_doc(uid)))
        # print("SIGNED_CERT_HASH: \t" + hashlib.sha256(str(open(config.SIGNED_CERTS_FOLDER+uid+".json").read()).encode('utf-8')).hexdigest())
        # print("SIGNED_HEX_HASH: \t" + hexlify(open(config.HASHED_CERTS_FOLDER+uid+".txt", 'rb').read()))
        # print("UNSIGNED_TX_DATA: \t" + )

cert_info = prepare_certs()
print(sign_certs())
print(hash_certs())
print(build_cert_txs())
verify_cert_txs()
