Digital Certificates Issuer Project
===================================

Takes digital certificates and issues them by creating a transaction from the issuing institution to the recipient
on the Bitcoin blockchain that includes the hash of the certificate itself. [See the schema](https://github.com/digital-certificates/schema)

Documentation
-------------

[http://issuer.readthedocs.io/](http://issuer.readthedocs.io/)

Quick start
-----------

This uses bitcoind in regtest mode. This route makes many simplifications to allow a quick start, and is intended for
experimenting only.


1. Clone the repo:

       git clone https://github.com/digital-certificates/issuer.git


2. From a command line in issuer dir, build your docker container

       cd issuer
       docker build -t ml/issuer:1.0 .

3. Read before running!

    - Once you launch the docker container, you will make some changes using your personal issuing information. This flow
    mirrors what you would if you were issuing real certificates.
    - To avoid losing your work, you should create snapshots of your docker container. You can do this by running

          docker ps -l
          docker commit <container for your ml/issuer> my_cert_issuer

4. When you're ready to run:

       docker run -it ml/issuer:1.0 bash

5. Start bitcoind. This will use the bitcoin.conf from the docker container, which runs in regtest mode

       bitcoind -daemon

Create issuing and revocation addresses
---------------------------------------

__Important__: this is a simplification to avoid using a USB, which needs to be inserted and removed during the
standard certficate issuing process. Do not use these addresses or private keys for anything other than experimenting.

Ensure your docker image is running and bitcoind process is started

1. Create an 'issuing address' and save the output as follows:

       issuer=`bitcoin-cli getnewaddress
       sed -i.bak "s/<issuing-address>/$issuer/g" /etc/issuer/conf.ini
       bitcoin-cli dumpprivkey $issuer > /etc/issuer/pk_issuer.txt

2. Create a 'revocation address' and save the output as follows. Note that we don't need to save this
corresponding private key for testing issuing certificates

       revocation=`bitcoin-cli getnewaddress
       sed -i.bak "s/<revocation-address>/$revocation/g" /etc/issuer/conf.ini

3. Don't forget to save snapshots so you don't lose your work (see step 3 of client setup)

Issuing certificates
--------------------

1. Add your certificates to data/unsigned_certs/

2. Make sure you have enough BTC in your issuing address.

    a. You're using bitcoind in regtest mode, so you can print money. This should give you 50 (fake) BTC

        bitcoin-cli generate 101
        bitcoin-cli getbalance

    b. Send the money to your issuing address -- note bitcoin-cli's standard denomination is bitcoins not satoshis! In our
    app, the standard unit is satoshis.

        bitcoin-cli sendtoaddress moH7X29kt5T8fbxTCjoxYzjfLeMR56Ju94 5  << bitcoins not satoshi!!!!


3. Run
TODO: There is an issuer the Dockerfile and/or setup.py. The pip install here shouldn't be required.
For now, these get it running:

       source /issuer/env/bin/activate
       cd issuer
       pip install .
       python issuer -c /etc/issuer/conf.ini


About the Digital Certificates project
--------------------------------------

MIT Media Lab Digital Certificates is an incubation project. We're looking for feedback, contributions, and general
discussion. This is not currently intended for production release, but we are improving our approach for future releases.


Contact
-------

Contact [certs@media.mit.edu](mailto:certs@media.mit.edu) with questions

