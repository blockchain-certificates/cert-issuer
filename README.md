[![Build Status](https://travis-ci.org/blockchain-certificates/cert-issuer.svg?branch=master)](https://travis-ci.org/blockchain-certificates/cert-issuer)

# cert-issuer

The cert-issuer project issues blockchain certificates by creating a transaction from the issuing institution to the
recipient on the Bitcoin blockchain that includes the hash of the certificate itself. 

## Quick start using Docker

This uses bitcoind in regtest mode. This route makes many simplifications to allow a quick start, and is intended for
experimenting only.

1. First ensure you have Docker installed. [See our Docker installation help](https://github.com/blockchain-certificates/developer-common-docs/blob/master/docker_install.md).

2. Clone the repo and change to the directory

    ```
    git clone https://github.com/blockchain-certificates/cert-issuer.git && cd cert-issuer
    ```


3. From a command line in cert-issuer dir, build your docker container:
    
    ```
    docker build -t ml/cert-issuer:1.0 .
    ```

4. Read before running!

    - Once you launch the docker container, you will make some changes using your personal issuing information. This flow mirrors what you would if you were issuing real certificates.
    - To avoid losing your work, you should create snapshots of your docker container. You can do this by running:

        ```
        docker ps -l
        docker commit <container for your ml/cert-issuer> my_cert_issuer
        ```

5. When you're ready to run:

    ```
    docker run -it ml/cert-issuer:1.0 bash
    ```

## Create issuing and revocation addresses

__Important__: this is a simplification to avoid using a USB, which needs to be inserted and removed during the
standard certficate issuing process. Do not use these addresses or private keys for anything other than experimenting.

Ensure your docker image is running and bitcoind process is started

1. Create an 'issuing address' and save the output as follows:

    ```
    issuer=`bitcoin-cli getnewaddress`
    sed -i.bak "s/<issuing-address>/$issuer/g" /etc/cert-issuer/conf.ini
    bitcoin-cli dumpprivkey $issuer > /etc/cert-issuer/pk_issuer.txt
    ```

2. Create a 'revocation address' and save the output as follows. Note that we don't need to save this
corresponding private key for testing issuing certificates:

    ```
    revocation=`bitcoin-cli getnewaddress`
    sed -i.bak "s/<revocation-address>/$revocation/g" /etc/cert-issuer/conf.ini
    ```

3. Don't forget to save snapshots so you don't lose your work (see step 3 of client setup)

## Issuing certificates

1. Add your certificates to /etc/cert-issuer/data/unsigned_certs/. To preview the certificate issuing workflow, you can add our sample unsigned certificate as follows.

    ```
    cp /cert-issuer/examples/data-testnet/unsigned_certs/6c6bd2ec-d0d6-41a9-bec8-57bb904c62a8.json /etc/cert-issuer/data/unsigned_certs/
    ```

2. Make sure you have enough BTC in your issuing address.

    a. You're using bitcoind in regtest mode, so you can print money. This should give you 50 (fake) BTC:

    ```
    bitcoin-cli generate 101
    bitcoin-cli getbalance
    ```

    b. Send the money to your issuing address -- note that bitcoin-cli's standard denomination is bitcoins not satoshis! (In our
    app, the standard unit is satoshis.) This command sends 5 bitcoins to the address

    ```
    bitcoin-cli sendtoaddress $issuer 5
    ```

3. Sign the certificates (open badge compliance step). After this step, the unsigned certificates will be archived (moved to the 'archive' folder) and the signed certificates will be added to 'data/signed_certificates'

    ```
    cd cert-issuer
    cert-signer -c /etc/cert-issuer/conf.ini
    ```

4. Issue the certificates on the blockchain

    ```
    cert-issuer -c /etc/cert-issuer/conf.ini
    ```

## Unit tests

This project uses tox to validate against several python environments.

1. Ensure you have an python environment. [Recommendations](https://github.com/blockchain-certificates/developer-common-docs/blob/master/virtualenv.md)

2. Run tests
    ```
    ./run_tests.sh
    ```

## Issuing options

The quick start instructions use a test mode for issuing certificates. Most of the steps apply for issuing certificates on the real Bitcoin blockchain. Read [Certificate Issuing Options](http://www.blockcerts.org/guide/options.html) for an overview of issuing options.

## Advanced Docs

- Issuing options
    - [Overview of issuing options](http://www.blockcerts.org/guide/options.html)
    - [Local Bitcoin node setup and installation](docs/bitcoind.md)
    - [Blockchain.info setup and installation](docs/blockchain_info.md)
- [Creating addresses](docs/make_addresses.md)
- [Issuing certificates](docs/issuing.md)
- [Debugging](docs/debugging.md)

## Examples

The files in examples/data-testnet and examples/data-mainnet contain results of previous runs. 

## Ignorable errors

If you see errors like this in the output, but the script succeeds anyway,
then it's an ignorable error. 

See [https://github.com/richardkiss/pycoin/issues/194](https://github.com/richardkiss/pycoin/issues/194)

```
raise ScriptError("getitem out of range")
pycoin.tx.script.ScriptError: getitem out of range
```


## Contact

Contact [info@blockcerts.org](mailto:info@blockcerts.org) with questions


