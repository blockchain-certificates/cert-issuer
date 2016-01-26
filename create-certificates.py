#!/usr/bin/env python3

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)

import getopt
import argparse
import hashlib
import bitcoin.rpc
import sys
import json
import glob
import binascii
import requests
import io
import random
from datetime import datetime
import time
import urllib.parse
from itertools import islice
import shutil

from bitcoin import params
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

from pycoin.tx import Tx, TxOut
from pycoin.tx.pay_to import build_hash160_lookup
from pycoin.key import Key
from pycoin.encoding import wif_to_secret_exponent
from pycoin.serialize import h2b

import config
import helpers
import secrets

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
    hexlify = lambda b: binascii.hexlify(b).decode('utf8')

REMOTE_CONNECT = True

def make_remote_url(command, extras={}):
    url = "http://blockchain.info/merchant/%s/%s?password=%s" % (secrets.WALLET_GUID, command, secrets.WALLET_PASSWORD)
    # url = "http://localhost:3000/merchant/%s/%s?password=%s" % (secrets.WALLET_GUID, command, secrets.WALLET_PASSWORD)
    if len(extras) > 0:
        addon = ''
        for name in list(extras.keys()):
            addon = "%s&%s=%s" % (addon, name, extras[name])
        url = url+addon
    return url

def check_for_errors(r):
    if int(r.status_code) != 200:
        sys.stderr.write("Error: %s\n" % (r.json()['error']))
        sys.exit(1)
    elif r.json().get('error', None):
        sys.stderr.write("Error: %s\n" % (r.json()['error']))
        sys.exit(1)
    return r

def check_if_confirmed(address):
    """Checks if all the BTC in the address has been confirmed. Returns true if is has been confirmed and false if it has not."""
    confirmed_url =  make_remote_url('address_balance', {"address": address, "confirmations": 1})
    unconfirmed_url = make_remote_url('address_balance', {"address": address, "confirmations": 0})
    confirmed_result = check_for_errors(requests.get(confirmed_url))
    unconfirmed_result = check_for_errors(requests.get(unconfirmed_url))
    confirmed_balance = int(confirmed_result.json()["balance"])
    unconfirmed_balance = int(unconfirmed_result.json()["balance"])
    if unconfirmed_balance and confirmed_balance:
        if confirmed_balance > 0:
            return True
    else:
        return False

def prepare_btc():
    print("Starting script...\n")
    if REMOTE_CONNECT == True:

        # r = check_for_errors( requests.get( make_remote_url('login', {'api_code': ''})) )

        num_certs = len(glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"))
        print("Creating %s temporary addresses...\n" % num_certs)

        temp_addresses = {}
        for i in range(num_certs):
            r = check_for_errors( requests.get( make_remote_url('new_address', {"label": "temp-address-%s" % (i)})) )
            temp_addresses[r.json()["address"]] = int((config.BLOCKCHAIN_DUST + 2 * config.TX_FEES) * COIN)

        print("Transfering BTC to temporary addresses...\n")

        batches = []
        it = iter(temp_addresses)
        for i in iter(range(0, len(temp_addresses), config.BATCH_SIZE)):
            batch = {}
            for k in islice(it, config.BATCH_SIZE):
                batch[k] = temp_addresses[k]
            batches.append(batch)

        for batch in batches:
            r = check_for_errors( requests.get( make_remote_url('sendmany', {"from": secrets.STORAGE_ADDRESS, "recipients": urllib.parse.quote_plus(json.dumps(temp_addresses)), "fee": int(config.TX_FEES*COIN) }) ) )

            print("Waiting for confirmation of transfer...")
            random_address = random.choice(list(temp_addresses.keys()))

            benchmark = datetime.now()
            while(True):
                confirmed_tx = check_if_confirmed(random_address)
                elapsed_time = str(datetime.now()-benchmark)
                if confirmed_tx == True:
                    print("It took %s to process the trasaction" % (elapsed_time))
                    break
                print("Time: %s, waiting 30 seconds and then checking if transaction is confirmed" % (elapsed_time))
                time.sleep(30)
                confirmed_tx = check_if_confirmed(secrets.STORAGE_ADDRESS)

        for address in list(temp_addresses.keys()):
            r = check_for_errors( requests.get( make_remote_url('payment', {
                "from": address, 
                "to": secrets.ISSUING_ADDRESS, 
                "amount": int((config.BLOCKCHAIN_DUST+config.TX_FEES)*COIN), 
                "fee": int(config.TX_FEES*COIN)} )))
            r = check_for_errors( requests.get( make_remote_url('archive_address', {"address": address} ) ) )
        
        return "Transfered BTC needed to issue certificates\n"

def prepare_certs():
    cert_info = {}
    for f in glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"):
        cert = json.loads(open(f).read())
        cert_info[f.split("/")[-1].split(".")[0]] = {
            "name": cert["recipient"]["givenName"] + " " + cert["recipient"]["familyName"],
            "pubkey": cert["recipient"]["pubkey"]
        }
    return cert_info


# Sign the certificates
def sign_certs():
    privkey = CBitcoinSecret(helpers.import_key())
    for f in glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"):
        uid = helpers.get_uid(f)
        cert = json.loads(open(f).read())
        message = BitcoinMessage(cert["assertion"]["uid"])
        print("Signing certificate for recipient id: %s ..." % (uid))
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
        print("Hashing certificate for recipient id: %s ..." % (uid))
        hashed_cert = hashlib.sha256(cert).digest()
        open(config.HASHED_CERTS_FOLDER + uid + ".txt", "wb").write(hashed_cert)
    return "Hashed certificates for recipients\n"

# Make transactions for the certificates
def build_cert_txs(cert_info):
    ct = -1
    for f in glob.glob(config.HASHED_CERTS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        cert = open(f, 'rb').read()
        print("Creating tx of certificate for recipient id: %s ..." % (uid))

        txouts = []
        if REMOTE_CONNECT == True:
            r = requests.get("https://blockchain.info/unspent?active=%s&format=json" % (secrets.ISSUING_ADDRESS)).json()
            unspent = []
            for u in r['unspent_outputs']:
                u['outpoint'] = COutPoint(unhexlify(u['tx_hash']), u['tx_output_n'])
                del u['tx_hash']
                del u['tx_output_n']
                u['address'] = CBitcoinAddress(secrets.ISSUING_ADDRESS)
                u['scriptPubKey'] = CScript(unhexlify(u['script']))
                u['amount'] = int(u['value'])
                unspent.append(u)
        else:
            unspent = proxy.listunspent(addrs=[secrets.ISSUING_ADDRESS])
        unspent = sorted(unspent, key=lambda x: hash(x['amount']))

        last_input = unspent[ct]
        txins = [CTxIn(last_input['outpoint'])]
        value_in = last_input['amount']

        recipient_addr = CBitcoinAddress(cert_info[uid]["pubkey"])
        recipient_out = CMutableTxOut(int(config.BLOCKCHAIN_DUST*COIN), recipient_addr.to_scriptPubKey())

        revoke_addr = CBitcoinAddress(secrets.REVOCATION_ADDRESS)
        revoke_out = CMutableTxOut(int(config.BLOCKCHAIN_DUST*COIN), revoke_addr.to_scriptPubKey())

        change_addr = CBitcoinAddress(secrets.ISSUING_ADDRESS)
        change_out = CMutableTxOut(int(value_in-((config.BLOCKCHAIN_DUST*2+config.TX_FEES)*COIN)), change_addr.to_scriptPubKey())

        cert_out = CMutableTxOut(0, CScript([OP_RETURN, cert]))

        txouts = [recipient_out] + [revoke_out] + [change_out] + [cert_out]
        tx = CMutableTransaction(txins, txouts)
        hextx = hexlify(tx.serialize())
        open(config.UNSIGNED_TXS_FOLDER + uid + ".txt", "wb").write(bytes(hextx, 'utf-8'))
        ct -= 1
        
    return ("Created unsigned txs for recipients\n", last_input)

def sign_cert_txs(last_input):
    for f in glob.glob(config.UNSIGNED_TXS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        hextx = str(open(f, 'rb').read(), 'utf-8')

        print("Signing tx with private key for recipient id: %s ..." % uid)

        tx = Tx.from_hex(hextx)
        wif = wif_to_secret_exponent(helpers.import_key())
        lookup = build_hash160_lookup([wif])
        tx.set_unspents([ TxOut(coin_value=last_input['amount'], script=unhexlify(last_input['script'])) ])

        tx = tx.sign(lookup)
        hextx = tx.as_hex()
        open(config.UNSENT_TXS_FOLDER + uid + ".txt", "wb").write(bytes(hextx, 'utf-8'))
    return "Signed txs with private key\n"

def verify_cert_txs():

    def verify_signature(address, signed_cert):
        message = BitcoinMessage(signed_cert["assertion"]["uid"])
        signature = signed_cert["signature"]
        return VerifyMessage(address, message, signature)

    def verify_doc(uid):
        hashed_cert = hashlib.sha256(open(config.SIGNED_CERTS_FOLDER+uid+".json", 'rb').read()).hexdigest()
        op_return_hash = open(config.UNSENT_TXS_FOLDER+uid+".txt").read()[-72:-8]
        if hashed_cert == op_return_hash:
            return True
        return False


    for f in glob.glob(config.UNSENT_TXS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        print("UID: \t\t\t" + uid)
        verified_sig = verify_signature(secrets.ISSUING_ADDRESS, json.loads(open(config.SIGNED_CERTS_FOLDER+uid+".json").read()))
        verified_doc = verify_doc(uid)
        print("VERIFY SIGNATURE: \t%s " % (verified_sig))
        print("VERIFY_OP_RETURN: \t%s " % (verified_doc))
        if verified_sig == False or verified_doc == False:
            sys.stderr.write('Sorry, there seems to be an issue with the certificate for recipient id: %s' % (uid))
            sys.exit(1)

    return "Verified transactions are complete."

def send_txs():
    for f in glob.glob(config.UNSENT_TXS_FOLDER+"*"):
        uid = helpers.get_uid(f)
        hextx = str(open(f, 'rb').read(), 'utf-8')
        if REMOTE_CONNECT == True:
            r = requests.post("https://insight.bitpay.com/api/tx/send", json={"rawtx": hextx})
            if int(r.status_code) != 200:
                sys.stderr.write("Error broadcasting the transaction through the Insight API. Error msg: %s" % r.text)
                sys.exit(1)
            else:
                txid = r.json().get('txid', None)
        else:
            proxy = bitcoin.rpc.Proxy()
            txid = b2lx(lx(proxy._call('sendrawtransaction', hextx)))
        open(config.SENT_TXS_FOLDER + uid + ".txt", "wb").write(bytes(txid, 'utf-8'))
        print("Broadcast transaction for certificate id %s with a txid of %s" % (uid, txid))
    return "Broadcast all transactions."

def main(argv):
    parser = argparse.ArgumentParser(description='Create digital certificates')
    parser.add_argument('--remote', default=1, help='Use remote or local bitcoind (default: remote)')
    parser.add_argument('--transfer', default=1, help='Transfer BTC to issuing address (default: 1). Only change this option for troubleshooting.')
    parser.add_argument('--create', default=1, help='Create certificate transactions (default: 1). Only change this option for troubleshooting.')
    parser.add_argument('--broadcast', default=1, help='Broadcast transactions (default: 1). Only change this option for troubleshooting.')
    args = parser.parse_args()

    timestamp = str(time.time())
    
    if args.remote == 0:
        REMOTE_CONNECT = False
        proxy = bitcoin.rpc.Proxy()
        address_balance = proxy.getreceivedbyaddress(addr=secrets.ISSUING_ADDRESS)
    if args.remote == 1:
        REMOTE_CONNECT = True
        COIN = config.COIN

    if args.transfer==0:
        address_balance = requests.get("https://blockchain.info/address/%s?format=json&limit=1" % (secrets.ISSUING_ADDRESS)).json()['final_balance']
        cost_to_issue = int((config.BLOCKCHAIN_DUST*2+config.TX_FEES)*COIN) * len(glob.glob(config.UNSIGNED_CERTS_FOLDER + "*"))
        if address_balance < cost_to_issue:
            sys.stderr.write('Sorry, please add %s BTC to the address %s.\n' % ((cost_to_issue - address_balance)/COIN, secrets.ISSUING_ADDRESS))
            sys.exit(1)

    if args.transfer==1:
        if REMOTE_CONNECT==True:
            helpers.check_internet_on()
            print(prepare_btc())
        else:
            pass

    if args.create==1:
        cert_info = prepare_certs()
        
        helpers.check_internet_off()
        print(sign_certs())
        shutil.copytree(config.SIGNED_CERTS_FOLDER, config.ARCHIVE_CERTS_FOLDER+timestamp)
        
        helpers.check_internet_on()
        print(hash_certs())
        message, last_input = build_cert_txs(cert_info)
        print(message)
        
        helpers.check_internet_off()
        print(sign_cert_txs(last_input))
        print(verify_cert_txs())

    if args.broadcast==1:
        helpers.check_internet_on()
        send_txs()
        shutil.copytree(config.SENT_TXS_FOLDER, config.ARCHIVE_TXS_FOLDER+timestamp)

if __name__ == "__main__":
    main(sys.argv[1:])

