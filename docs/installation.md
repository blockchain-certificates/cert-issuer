
## Installation
1. Clone the repo: `git clone https://github.com/digital-certificates/issuer.git`
2. Create a Python 3 virtual environment: `cd issuer && virtualenv venv -p python3.4`
3. Activate the virtual environment and install the requirements: `source venv/bin/activate && venv/bin/pip install -r requirements.txt`
4. Create your conf.ini file from the template: `cp conf_template.ini conf.ini`

Next we will populate the conf.ini values

## Bitcoin wallet options
You can use an online bitcoin wallet or run a bitcoind instance locally. The online option is faster to setup, but involves
requesting API access, which requires some turnaround time. The first option describes setup using a blockchain.info online wallet;
the second if you are using bitcoind

### Installation using APIs
Below are steps that will allow you to setup the digital certificates code to interact with the blockchain via the Blockchain.info API. If you do not have bitcoind already running on your computer, these instructions are highly reccomended.

1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini

    a. Save the wallet GUID as `wallet_guid` in conf.ini
    b. Save the wallet password as `wallet_password` in conf.ini
    c. When your api key from step 3 arrives, save this as `api_key` in conf.ini

5. Designate an address that will store your bitcoin for issuing the certificates. Transfer a few BTC to this address.

    a.  Save this address as your `storage_address` in conf.ini

6. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).

### Local Bitcoind Installation
Below are instructions are for running the code using bitcoind. To install bitcoind on a Ubuntu server, please follow the
[tutorial here](https://21.co/learn/setup-a-bitcoin-development-environment/#installing-bitcoind-from-source-on-ubuntu).

Once your bitcoind instance is up and running, add in the Bitcoin address that you will use for issuing as a "watch address"
using the command `bitcoin-cli importaddress "<insert_address_here>" ( "ISSUING_ADDRESS" rescan )`. This will take a
while to run, since it will scan the blockchain for the address's previous transactions.




