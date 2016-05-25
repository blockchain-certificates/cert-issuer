## Creating Certificate and Revocation Addresses

Important! These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.

#### Using Local Bitcoin Client (recommended)

This assumes you have configured your bitcoind instance to run in regtest mode.

1. Create an address that will be used as your 'issuing address', i.e. the address from which your certificates are issued.

    a. Get a new address
    ```
    bitcoin-cli -conf=your-bitcoin.conf getnewaddress
    ```
    b. save the address as the `issuing_address` value in conf.ini
    c. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt. The corresponding private key
    is obtained by running:
    ```
    bitcoin-cli -conf=your-bitcoin.conf -regtest dumpprivkey <issuing_address>
    ```

2. Create an address that will be used as your 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

    a. Get a new address
    ```
    bitcoin-cli -conf=your-bitcoin.conf getnewaddress
    ```
    b. save the address as the `revocation_address` value in conf.ini
    c. it's not important to save the private key for this case; we can always get it later


#### Using bitaddress.org

1. Go to [bitaddress.org](http://bitaddress.org)
2. Create an address that will be used as your 'issuing address', i.e. the address from which your certificates are issued.

    a. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt
    b. save the public address as the `issuing_address` value in conf.ini

3. Create an address that will be used as your 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

    a. save the unencrypted private key to your USB drive, in a file called pk_revocation.txt
    b. save the public address as the `revocation_address` value in conf.ini


If you go this route, and are running a local bitcoind node, you will need to import your issung address as a "watch address"
using the command `bitcoin-cli importaddress "<insert_address_here>" ( "ISSUING_ADDRESS" )`. This will take a
while to run, since it will scan the blockchain for the address's previous transactions.


###### Advanced setup
In a live environment, you'd want to use an additional storage address. You would transfer money from your storage address
to your issuing address before issuing certificates.

As above, you would designate an storage address to store you bitcoin, and transfer a few BTC to this address

Save this address as your `storage_address` in conf.ini
