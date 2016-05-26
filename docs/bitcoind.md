Bitcoind in regtest mode Instructions
=====================================

__This is the recommended choice!__

Regtest mode allows you to experiment with running a local bitcoind node without spending real money. We've provided a
Docker container that will start bitcoind in regtest mode to make it easy to get started.

1. Follow the instructions to [build Bitcoin Core for your OS](https://github.com/bitcoin/bitcoin/tree/master/doc)

    - for example, [OSX instructions](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)


2. Edit the bitcoin config to run in regtest mode.

    a. Edit or create a new bitcoin.conf file, with the following entries:
     ```
     rpcuser=bitcoinrpc
     rpcpassword=6c8a25acd56561b2a039197e86d07c97
     regtest=1
     relaypriority=0
     rpcallowip=127.0.0.1
     rpcport = 8332
     rpcconnect = 127.0.0.1
     ```

    b. Start the bitcoind daemon with this config file:

    ```
    bitcoind -daemon -conf=your-bitcoin.conf
    ```



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
