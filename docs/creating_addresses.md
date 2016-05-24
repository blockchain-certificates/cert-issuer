## Creating Certificate and Revocation Addresses

1. Go to [bitaddress.org](http://bitaddress.org)
2. Create an address that will be used as your 'issuing address', i.e. the address from which your certificates are issued.

    a. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt
    b. save the public address as the `issuing_address` value in conf.ini

3. Create an address that will be used as your 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

    a. save the unencrypted private key to your USB drive, in a file called pk_revocation.txt
    b. save the public address as the `revocation_address` value in conf.ini

Important! Do not plug in this USB when your computer's wifi is on.