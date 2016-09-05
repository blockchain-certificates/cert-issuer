# Issuing Certificates

1. Prerequisites

    - If you are using the blockchain.info API, start the blockchain.info server

        ```
        blockchain-wallet-service start --port 3000
        ```
    - Otherwise start your local bitcoind client (use regtest mode to preview!)

2. Add your certificates to data/unsigned_certs/

3. Make sure you have enough BTC in your issuing address. Each certificate costs 15000 satoshi ($0.06 USD)

    __Important note on denominations: If you are running a bitcoind node, note that the standard cli denomination is bitcoins not satoshis! In the cert-issuer app, the standard unit is Satoshis (this is common in other apis), and the values are converted to bitcoin first.__

    a. If you're using bitcoind, transfer money by the command line.
    ```
    bitcoin-cli sendtoaddress $issuer <amount>
    ```

    b. Otherwise transfer with your online wallet

4. Run the create-certificates.py script to create your certificates. If you've installed the package
you can run:
    `python cert-issuer -c conf.ini`







