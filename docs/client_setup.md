# Bitcoin client options

Next we will choose a bitcoin client and create our certificate issuing addresses.

We highly recommend running a local bitcoind instance in regtest mode while getting started. This allows you to
experiment with running a bitcoin node without spending money. We've created a Dockerfile to make this easy.

Instructions for using an online wallet are included, but be very careful or you may lose real money!

## Bitcoind in regtest mode using docker

__This is the recommended choice!__

### Setup

1. From a command line in issuer dir, build your docker container

```
docker build -t ml/issuer:1.0 .
```

2. Before running

    - Once you launch the docker container, you will make some changes using your personal issuing information. This flow
    mirrors what you would if you were issuing real certificates.
    - To avoid losing your work, you should create snapshots of your docker container. You can do this by running

    ```
    docker ps -l
    docker commit <container for your ml/issuer> my_cert_issuer
    ```

3. When you're ready to run:

```
docker run -it ml/issuer:1.0 bash

```

4. Start bitcoind. This will the our bitcoin.conf from the Dockerfile, which runs in regtest mode

```
bitcoind -daemon
```


## Blockchain.info instructions

### About
Below are steps that will allow you to setup the digital certificates code to interact with the blockchain via the
Blockchain.info API. You can use this if you want to try issuing real certificates, but this will involve spending real
bitcoin.

### Setup
1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini

    a. Save the wallet GUID as `wallet_guid` in conf.ini
    b. Save the wallet password as `wallet_password` in conf.ini
    c. When your api key from step 3 arrives, save this as `api_key` in conf.ini
5. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).

### Advanced considerations

In a deployed environment, you'd want to use an additional storage address. You would transfer money from your storage address
to your issuing address before issuing certificates.

As above, you would designate an storage address to store you bitcoin, and transfer a few BTC to this address

Save this address as your `storage_address` in conf.ini, and use the `--transfer_from_storage_address` configuration option.
