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

# create revocation address
revocation=`bitcoin-cli getnewaddress`
sed -i.bak "s/<revocation-address>/$revocation/g" /etc/cert-issuer/conf.ini

# copy sample cert
cp /cert-issuer/examples/data-testnet/unsigned_certificates/6c6bd2ec-d0d6-41a9-bec8-57bb904c62a8.json /etc/cert-issuer/data/unsigned_certificates/

# make sure you have enough BTC in your issuing address
bitcoin-cli generate 101
bitcoin-cli getbalance
bitcoin-cli sendtoaddress $issuer 5

# sign the certificate
cd cert-issuer
cert-signer -c /etc/cert-issuer/conf.ini

# issue the certificates on the blockchain
cert-issuer -c /etc/cert-issuer/conf.ini