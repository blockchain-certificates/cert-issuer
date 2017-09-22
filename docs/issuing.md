# Configuring and running cert-issuer for other chains

The Quick Start assumed you are issuing certificates in regtest mode, which doesn't actually write to a public blockchain. To actually write your transaction, you need to run in testnet (with test coins -- not real money) or mainnet (real money).

We recommend starting in testnet before mainnet.

By default, cert-issuer does not assume you have a bitcoin node running locally, and it uses APIs to look up and broadcast transactions. There is API support for both testnet and mainnet chains. 

If you do want to use a local bitcoin node, [see details about installing and configuring a bitcoin node for use with cert-issuer](bitcoind.md) before continuing.

These steps walk you through issuing in testnet and mainnet mode.

## Prerequisites

### Create an issuing address

First, ensure you've created an issuing address appropriate for the Bitcoin chain you are using. Please note:
- regtest or testnet addresses will start with 'm' or 'n'
- mainnet addresses will start with '1'
  
 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__

1. Use bitaddress.org
    - for testnet addresses go to [bitaddress.org?testnet=true](http://bitaddress.org?testnet=true)
    - for mainnet addresses go to [bitaddress.org](http://bitaddress.org)
2. Create an 'issuing address', i.e. the address from which your certificates are issued.
    - save the unencrypted private key to a file (we recommend that store it on a removable drive for security).
    - save the public address as the `issuing_address` value in conf.ini

If you are using a local bitcoin node, you can create addresses by command line. See [bitcoind.md](bitcoind.md)
    
### Get coins

Note ensure you've transferred sufficient funds to your issuing address to cover the transaction fee.  Some notes:
- The transaction fee is the same no matter the number of certificates in the batch
- The default transaction fee used by cert-issuer is 60,000 satoshis (~$1.50 USD, 7/3/2017)
- Because the transaction fee is a factor in confirmation time, you may decide to increase or decrease this value in the config file (read more about current transaction fee/latency estimates: https://bitcoinfees.21.co/)

#### Obtaining testnet coins

- Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
- Important: make sure you follow the guidance of the testnet faucet provider!
    
#### Obtaining mainnet coins
- If this is your first time purchasing Bitcoin, start by reading “Getting started with Bitcoin”. Specifically, the first section “How to use Bitcoin” is an overview of choosing a wallet, obtaining your first Bitcoins, and securing your money.
- Transfer a small amount of money to the issuer address created in step 1.

## Configuring cert-issuer

Edit your conf.ini file (the config file for this application). 

```
issuing_address = <issuing-address>
bitcoin_chain=<regtest|testnet|mainnet>
    
usb_name = </Volumes/path-to-usb/>
key_file = <file-you-saved-pk-to>

unsigned_certificates_dir=<path-to-your-unsigned-certificates>
blockchain_certificates_dir=<path-to-your-blockchain-certificates>
work_dir=<path-to-your-workdir>

no_safe_mode

# advanced: uncomment the following line if you're running a bitcoin node
# bitcoind
```

Note that the `bitcoind` option is technically not required in `regtest` mode. `regtest` mode _only_ works with a local bitcoin node. The quick start in docker brushed over this detail by installing a regtest-configured bitcoin node in the docker container.

## Issuing

1. Add your certificates to data/unsigned_certs/

2. Run the issue_certificates.py script to create your certificates. If you've installed the package
you can run:

```
python cert-issuer -c conf.ini
```

3. Output
  - The Blockchain Certificates will be located in data/blockchain_certificates.
  - If you ran in the mainnet or testnet mode, you can also see your transaction on a live blockchain explorer. 
    - For example, Blockr.io has explorers for both [testnet](https://tbtc.blockr.io/) and [mainnet](https://blockr.io/).
    - The transaction id is located in the Blockchain Certificate under `signature.anchors[0].sourceId`
