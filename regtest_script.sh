#!/bin/bash
##################################################################################################################
# This script wraps the quick start steps in the README for issuing a batch of test certificates. However, it's
# important to understand the steps involved in issuing certificates, as this will spend real money when you issue
# certificates on the live Bitcoin blockchain.
##################################################################################################################

# create issuing address
issuer=`bitcoin-cli getnewaddress`
sed -i.bak "s/<issuing-address>/$issuer/g" /etc/cert-issuer/conf.ini
bitcoin-cli dumpprivkey $issuer > /etc/cert-issuer/pk_issuer.txt

# copy sample cert
cp /cert-issuer/examples/data-testnet/unsigned_certificates/bc9bdbb5-d734-4242-9edc-d1bc3f8f7a6e.json /etc/cert-issuer/data/unsigned_certificates/

# make sure you have enough BTC in your issuing address
bitcoin-cli generate 101
bitcoin-cli getbalance
bitcoin-cli sendtoaddress $issuer 5

# issue the certificates on the blockchain
cert-issuer -c /etc/cert-issuer/conf.ini
