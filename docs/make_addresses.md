# Creating Issuing and Revocation Addresses

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
