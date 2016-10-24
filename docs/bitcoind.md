# Local Bitcoin node instructions

See [Certificate Issuing Options](http://www.blockcerts.org/guide/options.html) for an overview of issuing options. This describes installing and configuring bitcoind for regtest and testnet modes.

The quick start guide runs a Bitcoin node in a Docker container. These instructions show how to install it locally.

## Setup and Installation

Start by reading an overview of requirements and other concerns when [running a Bitcoin full node](https://bitcoin.org/en/full-node). [Bitcoin.org's developer examples](https://bitcoin.org/en/developer-examples) provide more context to the steps here.

These instructions walk through the steps for [installing Bitcoin Core for your OS](https://github.com/bitcoin/bitcoin/tree/master/doc). For example, [OSX instructions](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)

## Configuring your Bitcoin node for regtest mode

The bitcoin.conf file determines how your bitcoin node will run, and which chain it uses.

1. Locate the bitcoin.conf file for your environment. Then edit or create a new file named bitcoin.conf (first save the old one with a different name), with the following entries:
     ```
     rpcuser=<your-user>
     rpcpassword=<your-password>
     regtest=1
     relaypriority=0
     rpcallowip=127.0.0.1
     rpcport = 8332
     rpcconnect = 127.0.0.1
     ```

2. Start the bitcoind daemon with this config file:

    ```
    bitcoind -daemon -conf=your-bitcoin.conf
    ```

3. Edit your conf.ini file (for this application). You can use conf_regtest.ini as a starting point.

    ```
    storage_address = <storage-address>
    revocation_address = <revocation-address>
    
    usb_name = </Volumes/path-to-usb/>
    key_file = <file-you-saved-pk-to>
    
    wallet_connector_type=bitcoind
    bitcoin_chain=regtest
    
    no_safe_mode
    no_transfer_from_storage_address
    ```

4. Now you are ready to issue certificates. See [issuing instructions](issuing.md)

## Configuring your Bitcoin node for testnet mode

The bitcoin.conf file determines how your bitcoin node will run, and which chain it uses.

1. Locate the bitcoin.conf file for your environment. Then edit or create a new file named bitcoin.conf (first save the old one with a different name), with the following entries:

    ```
    rpcuser=<your-user>
    rpcpassword=<your-password>
    testnet=1
    server=1
    rpctimeout=30
    rpcport=8332
    ```

2. Start the bitcoind daemon with this config file:

    ```
    bitcoind -daemon -conf=your-bitcoin.conf
    ```

3. Edit your conf.ini file (for this application). Note that the difference between this and regtest is the bitcoin_chain setting.

    ```
    storage_address = <storage-address>
    revocation_address = <revocation-address>
    
    usb_name = </Volumes/path-to-usb/>
    key_file = <file-you-saved-pk-to>
    
    wallet_connector_type=bitcoind
    bitcoin_chain=testnet
    
    no_safe_mode
    no_transfer_from_storage_address
    ```
 
4. Next you need to obtain Testnet coins. 
    - Create an issuer address; see [create addresses, Bitcoin node instructions](make_addresses.md)
      - You will need the public address. Since we are running the Bitcoin node in testnet mode, the address will start with 'm' or 'n'
    - Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
      - Important: make sure you follow the guidance of the testnet faucet provider!
 
5. Now you are ready to issue certificates. See [issuing instructions](issuing.md)
