[![Build Status](https://travis-ci.org/blockchain-certificates/cert-issuer.svg?branch=master)](https://travis-ci.org/blockchain-certificates/cert-issuer)

# cert-issuer

he cert-issuer project issues blockchain certificates by creating a transaction from the issuing institution to the
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

1. Add your certificates to /etc/cert-issuer/data/unsigned_certs/. To preview the certificate issuing workflow, you can add our sample unsigned certificate as follows. Note that
    we are renaming the file to the uid field in the unsigned certificate

    ```
    cp /cert-issuer/docs/sample_unsigned_cert.json /etc/cert-issuer/data/unsigned_certs/3a4452c9-0e2b-4a96-b2f5-41dd84606b07.json
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

## Advanced Docs

- [Bitcoin client options](docs/options.md)
- [Live installation options](docs/live.md)
- [Creating addresses](docs/make_addresses.md)
- [Issuing certificates](docs/issuing.md)
- [Debugging](docs/debugging.md)


## Contact

Contact [info@blockcerts.org](mailto:info@blockcerts.org) with questions

