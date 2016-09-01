
Quick start
-----------

This uses bitcoind in regtest mode. This route makes many simplifications to allow a quick start, and is intended for
experimenting only.

1. [Install Docker Engine and Docker Compose](https://docs.docker.com/engine/installation)
    - If you are using Mac OSX or Windows, your installation includes both Engine and Compose, so you can skip to the #installation anchor for your OS.
        - Mac OSX: [https://docs.docker.com/engine/installation/mac/#installation](https://docs.docker.com/engine/installation/mac/#installatio)
        - Windows: [https://docs.docker.com/engine/installation/windows/#installation](https://docs.docker.com/engine/installation/windows/#installation)
    - If you already have Docker installed, ensure your version is >= 1.10.0, and that you have both Engine and Compose

2. Clone the repo:

    ```
    git clone https://github.com/blockchain-certificates/cert-issuer.git
    ```


3. From a command line in cert-issuer dir, build your docker container:
    
    ```
    cd cert-issuer
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

Create issuing and revocation addresses
---------------------------------------

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

Issuing certificates
--------------------

1. Add your certificates to /etc/cert-issuer/data/unsigned_certs/

    - To preview the certificate issuing workflow, you can add our sample unsigned certificate as follows. Note that
    we are renaming the file to the uid field in the unsigned certificate

    ```
    cp /cert-issuer/docs/sample_unsigned_cert.json /etc/cert-issuer/data/unsigned_certs/68656c6c6f636f6d7077ffff.json
    ```

2. Make sure you have enough BTC in your issuing address.

    a. You're using bitcoind in regtest mode, so you can print money. This should give you 50 (fake) BTC:

    ```
    bitcoin-cli generate 101
    bitcoin-cli getbalance
    ```

    b. Send the money to your issuing address -- note bitcoin-cli's standard denomination is bitcoins not satoshis! In our
    app, the standard unit is satoshis. This sends 5 bitcoins to the address

    ```
    bitcoin-cli sendtoaddress $issuer 5
    ```

3. Sign the certificates (open badge compliance step)

    ```
    cd cert-issuer
    cert-signer -c /etc/cert-issuer/conf.ini
    ```

3. Issue the certificates on the blockchain

    ```
    cert-issuer -c /etc/cert-issuer/conf.ini
