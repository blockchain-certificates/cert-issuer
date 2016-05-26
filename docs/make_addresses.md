# Creating issuing and revocation addresses


## Docker image

Ensure your docker image is running and bitcoind process is started (see client setup)

1. Create an 'issuing address', save it to your issuer conf.ini file, and save the issuer's corresponding
private key to /etc/issuer/pk_issuer.txt

```
issuer=`bitcoin-cli getnewaddress`
sed -i.bak "s/<issuing-address>/$issuer/g" /etc/issuer/conf.ini
bitcoin-cli dumpprivkey $issuer > /etc/issuer/pk_issuer.txt

```
2. Create a 'revocation address' and save it to your issuer conf.ini file. Note that we don't need to save this
corresponding private key; only if you want to test revocation

```
revocation=`bitcoin-cli getnewaddress`
sed -i.bak "s/<revocation-address>/$revocation/g" /etc/issuer/conf.ini
```

3. Don't forget to save snapshots so you don't lose your work (see step 2 of client setup)



__These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__

1. Go to [bitaddress.org](http://bitaddress.org)
2. Create an 'issuing address', i.e. the address from which your certificates are issued.

    a. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt
    b. save the public address as the `issuing_address` value in conf.ini

3. Create a 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

    a. save the unencrypted private key to your USB drive, in a file called pk_revocation.txt
    b. save the public address as the `revocation_address` value in conf.ini

4. Verify your conf.ini is complete
Ensure all the required conf.ini values are entered. At this point you should have:

```
issuing_address = "<issuing address>"
revocation_address = "<revocation address>"

usb_name = "<path to usb>"
key_file = "<name of private key file>"

wallet_guid = "<blockchain.info wallet guid>"                    # Your unique identifier to login to blockchain.info
wallet_password = "<blockchain.info wallet password>"            # Your password to login to blockchain.info
storage_address = "<blockchain.info address with storage BTC>"
api_key = "<blockchain.info api key>"
```
