# Creating Issuing and Revocation Addresses

__These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__

## Creating addresses with a Bitcoin node

1. Creating issuing address. You need to save the private issuing key to a USB for the OBI signing step

    ```
    issuer=`bitcoin-cli getnewaddress`
    bitcoin-cli dumpprivkey $issuer > <PATH_TO_USB>/<ISSUER_FILE_NAME>.txt
    ```

2. Create a revocation address and save the output as follows. Note that we don't need to save this
corresponding private key because we can look it up from the bitcoin cli if we ever need it.

    ```
    revocation=`bitcoin-cli getnewaddress`
    ```

3. Add the public addresses to your application conf.ini
    - `issuing_address=$issuer` (insert $issuer value from above)
    - `revocation_address=$revocation` (insert $revocation value from above)


## Otherwise

1. Go to [bitaddress.org](http://bitaddress.org)
2. Create an 'issuing address', i.e. the address from which your certificates are issued.

    a. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt
    b. save the public address as the `issuing_address` value in conf.ini

3. Create a 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

    a. save the unencrypted private key to your USB drive, in a file called pk_revocation.txt
    b. save the public address as the `revocation_address` value in conf.ini



