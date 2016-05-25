
## Installation
1. Clone the repo:

    ```
    git clone https://github.com/digital-certificates/issuer.git
    ```
2. Create a Python 3 virtual environment and activate it

    ```
    cd issuer
    virtualenv venv -p python3.4
    source venv/bin/activate
    ```
3. Install the requirements:

    ```
    pip install -r requirements.txt
    ```

4. Create your conf.ini file from the template:

    ```
    cp conf_template.ini conf.ini
    ```

Next we will choose a wallet option and populate the conf.ini values

## Bitcoin wallet options
We highly recommend running a local bitcoind instance in regtest mode while getting started. This allows you to experiment
with running a bitcoin node without spending money.

Instructions for using an online wallet are included, but be very careful lest you lose real money!


### Bitcoind in regtest mode (recommended)
Regtest mode allows you to experiment with running a local bitcoin node without actually spending
money.

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


### Blockchain.info online wallet
Below are steps that will allow you to setup the digital certificates code to interact with the blockchain via the Blockchain.info API. If you do not have bitcoind already running on your computer, these instructions are highly reccomended.

1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini

    a. Save the wallet GUID as `wallet_guid` in conf.ini
    b. Save the wallet password as `wallet_password` in conf.ini
    c. When your api key from step 3 arrives, save this as `api_key` in conf.ini

5. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).




