# Local Bitcoin node instructions

See [Certificate Issuing Options](http://community.blockcerts.org/t/issuing-options/28) for an overview of issuing options. This describes installing and configuring bitcoind for regtest and testnet modes.

The quick start guide runs a Bitcoin node in a Docker container. These instructions show how to install it locally.

## Setup and Installation

Start by reading an overview of requirements and other concerns when [running a Bitcoin full node](https://bitcoin.org/en/full-node). [Bitcoin.org's developer examples](https://bitcoin.org/en/developer-examples) provide more context to the steps here.

These instructions walk through the steps for [installing Bitcoin Core for your OS](https://github.com/bitcoin/bitcoin/tree/master/doc). For example, [OSX instructions](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)

## Configuring for regtest mode

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
    issuing_address = <issuing-address>
    revocation_address = <revocation-address>
    
    unsigned_certificates_dir=<path-to-your-unsigned-certificates>
    signed_certificates_dir=<path-to-your-signed-certificates>
    blockchain_certificates_dir=<path-to-your-blockchain-certificates>
    work_dir=<path-to-your-workdir>
    
    usb_name = </Volumes/path-to-usb/>
    key_file = <file-you-saved-pk-to>
    
    wallet_connector_type=bitcoind
    bitcoin_chain=regtest
    
    no_safe_mode
    no_transfer_from_storage_address
    ```

4. Now you are ready to issue certificates. See [issuing instructions](issuing.md)

## Configuring for testnet mode

1. Create an issuer address; see [create addresses, Bitcoin node instructions](make_addresses.md)
      - Since we are running in testnet mode, the address will start with 'm' or 'n'

2. Obtain Testnet coins
    - Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
    - Important: make sure you follow the guidance of the testnet faucet provider!

3. Edit your conf.ini file as follows:

    ```
    issuing_address = <issuing-address>
    revocation_address = <revocation-address>
    
    unsigned_certificates_dir=<path-to-your-unsigned-certificates>
    signed_certificates_dir=<path-to-your-signed-certificates>
    blockchain_certificates_dir=<path-to-your-blockchain-certificates>
    work_dir=<path-to-your-workdir>
    
    usb_name = </Volumes/path-to-usb/>
    key_file = <file-you-saved-pk-to>
    
    bitcoin_chain=testnet
    ```

4. Now you are ready to issue test certificates. See [issuing instructions](issuing.md)

## Configuring for mainnet mode

1. Create an issuer address; see [create addresses, Bitcoin node instructions](make_addresses.md)
  - Since we are running in mainnet mode, the address will start with '1'
    
2. Obtain mainnet coins
  - If this is your first time purchasing Bitcoin, start by reading “Getting started with Bitcoin”. Specifically, the first section “How to use Bitcoin” is an overview of choosing a wallet, obtaining your first Bitcoins, and securing your money.
  - Transfer a small amount of money to the issuer address created in step 1.

3. Edit your conf.ini file as follows:

    ```
    issuing_address = <issuing-address>
    revocation_address = <revocation-address>
    
    unsigned_certificates_dir=<path-to-your-unsigned-certificates>
    signed_certificates_dir=<path-to-your-signed-certificates>
    blockchain_certificates_dir=<path-to-your-blockchain-certificates>
    work_dir=<path-to-your-workdir>
    
    usb_name = </Volumes/path-to-usb/>
    key_file = <file-you-saved-pk-to>
    
    bitcoin_chain=mainnet
    ```

4. Now you are ready to issue certificates. See [issuing instructions](issuing.md)
