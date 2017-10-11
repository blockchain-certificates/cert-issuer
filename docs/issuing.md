# Configuring and running cert-issuer for other chains

The Quick Start assumed you are issuing certificates in Bitcoin regtest mode, which doesn't actually write to a public blockchain. To actually write your transaction, you need to run in testnet (with test coins -- not real money) or mainnet (real money).

We recommend starting in testnet before mainnet.

By default, cert-issuer does not assume you have a bitcoin/ethereum node running locally, and it uses APIs to look up and broadcast transactions. There is API support for both testnet and mainnet chains. 

If you do want to use a local bitcoin node, [see details about installing and configuring a bitcoin node for use with cert-issuer](bitcoind.md) before continuing.

These steps walk you through issuing in testnet and mainnet mode. Note that the prerequisites and the configuration for the Bitcoin issuing and the Ethereum issuing differ. 

## Prerequisites

Decide which chain (Bitcoin or Ethereum) to issue to and follow the steps. The bitcoin chain is currently best supported by the Blockcerts libraries. Follow the steps for the chosen chain.

### Create a Bitcoin issuing address

First, ensure you've created an issuing address appropriate for the Bitcoin chain you are using. Please note:
- regtest or testnet addresses will start with 'm' or 'n'
- mainnet addresses will start with '1'
  
 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__

1. Use bitaddress.org
    - for testnet addresses go to [bitaddress.org?testnet=true](http://bitaddress.org?testnet=true)
    - for mainnet addresses go to [bitaddress.org](http://bitaddress.org)
2. Create an 'issuing address', i.e. the address from which your certificates are issued.
    - save the unencrypted private key to a file (we recommend to store it on a removable drive for security).
    - save the public address as the `issuing_address` value in conf.ini

If you are using a local bitcoin node, you can create addresses by command line. See [bitcoind.md](bitcoind.md)


### Create an Ethereum issuing address

Currently Blockcerts just supports issuing to the Ropsten Ethereum testnet, and the Ethereum mainnet. In Ethereum a public/private key pair is the same accross all test/main networks.

 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__
 
 1. Create issuing address on Myetherwallet
    - Go to https://www.myetherwallet.com/.
    - For the best security turn off your connection to the internet when you are on the create wallet page.
 2. Go through the create wallet process
    - Store the private key on the USB stick and unplug it afterwards.
    - Copy the public key to the `issuing_address` value in conf.ini

### Get coins

Note ensure you've transferred sufficient funds to your issuing address to cover the transaction fee.  Some notes:
- The transaction fee is the same no matter the number of certificates in the batch
- __For Bitcoin:__
  - The default transaction fee used by cert-issuer is 60,000 satoshis for bitcoin (~$2.88 USD, 10/11/2017)
  - Because the transaction fee is a factor in confirmation time, you may decide to increase or decrease this value in the config file (read more about current transaction fee/latency estimates: https://bitcoinfees.21.co/)
- __For Ethereum:__
  - The default gasprice is set at 20 GWei, which makes the transaction price about 0.00047 ETH (~$0.14 USD, 10/11/2017)
  - Lowering the default setting may impact the confirmation time. Please reference http://ethgasstation.info/ to find a fitting gasprice.

#### Obtaining testnet coins

- Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
- Important: make sure you follow the guidance of the testnet faucet provider!
    
#### Obtaining mainnet coins

- If this is your first time purchasing Bitcoin or Ethereum, start by reading starter information:
   - For __Bitcoin__: [https://bitcoin.org/en/getting-started] Specifically, the first section “How to use Bitcoin” is an overview of choosing a wallet, obtaining your first Bitcoins, and securing your money.
   - For __Ethereum__: https://myetherwallet.github.io/knowledge-base/getting-started/getting-started-new.html - MyEtherWallet's knowledge base getting started entry. 
- Transfer a small amount of money to the issuer address created in step 1.


## Configuring cert-issuer 

Edit your conf.ini file (the config file for this application). 

```
issuing_address = <issuing-address>
blockchain = <bicoin|ethereum>

#if using bitcoin specify:
bitcoin_chain=<regtest|testnet|mainnet>

#If using Ethereum specify:
ethereum_chain=<ethmain|ethrop>
  
usb_name = </Volumes/path-to-usb/>
key_file = <file-you-saved-pk-to>

unsigned_certificates_dir=<path-to-your-unsigned-certificates>
blockchain_certificates_dir=<path-to-your-blockchain-certificates>
work_dir=<path-to-your-workdir>

no_safe_mode

# advanced: uncomment the following line if you're running a bitcoin node
# bitcoind
```

Notes:
  - The `bitcoind` option is technically not required in `regtest` mode. `regtest` mode _only_ works with a local bitcoin node. The quick start in docker brushed over this detail by installing a regtest-configured bitcoin node in the docker container.
  - The Ethereum option does not support a local (test)node currently. The issuer will broadcast the transaction via the Etherscan API.

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
    - For Bitcoin, Blockr.io has explorers for both [testnet](https://tbtc.blockr.io/) and [mainnet](https://blockr.io/).
    - For Ethereum, Etherscan has explorers for [ropsten](https://ropsten.etherscan.io/) and [mainnet](https://etherscan.io/)
    - The transaction id is located in the Blockchain Certificate under `signature.anchors[0].sourceId`
