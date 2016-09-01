# Blockchain.info instructions


## Installation

1. Clone the repo:

    ```
    git clone https://github.com/blockchain-certificates/cert-issuer.git
    ```
2. Create a Python 3 virtual environment and activate it
    ```
    cd cert-issuer
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

## Setup

1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini
    a. Save the wallet GUID as `wallet_guid` in conf.ini
    b. Save the wallet password as `wallet_password` in conf.ini
    c. When your api key from step 3 arrives, save this as `api_key` in conf.ini
5. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).

