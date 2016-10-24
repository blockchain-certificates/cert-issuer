# Blockchain.info instructions


## Setup and Installation

1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini
    a. Save the wallet GUID as `wallet_guid` in conf.ini
    b. Save the wallet password as `wallet_password` in conf.ini
    c. When your api key from step 3 arrives, save this as `api_key` in conf.ini
5. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).

## Configuration

Edit your conf.ini file with your wallet's login info. Note that only the mainnet chain is supported with a Blockchain.info wallet. To experiment with regtest and testnet, you need to use [bitcoind](bitcoind.md)

```
issuing_address = "<issuing address>"
revocation_address = "<revocation address>"

usb_name = "<path to usb>"
key_file = "<name of private key file>"

wallet_guid = "<blockchain.info wallet guid>"                    # Your unique identifier to login to blockchain.info
wallet_password = "<blockchain.info wallet password>"            # Your password to login to blockchain.info
storage_address = "<blockchain.info address with storage BTC>"   # optional
api_key = "<blockchain.info api key>"

bitcoin_chain=mainnet
```

## Issuing certificates

Now you're ready to issue certificates. See [[issuing.md]]