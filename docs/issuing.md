# Issuing Certificates

## Prerequisites


- Ensure you've created an issuing address appropriate for the Bitcoin chain you are using. See [creating addresses](make_addresses.md) for details
    - regtest or testnet addresses will start with 'm' or 'n'
    - mainnet addresses will start with '1'
- Ensure you've transferred sufficient funds to your issuing address to cover the transaction fee. 
    - The transaction fee is the same no matter the number of certificates in the batch
    - The default transaction fee used by cert-issuer is 60,000 satoshis (~$1.50 USD, 7/3/2017)
    - Because the transaction fee is a factor in confirmation time, you may decide to increase or decrease this value in the config file (read more about current transaction fee/latency estimates: https://bitcoinfees.21.co/)
- If you haven't already, make sure your conf.ini (for this application) is correct. See [issuing options](bitcoin_options.md) for details

## Issuing

1. Add your certificates to data/unsigned_certs/

2. Make sure you have enough BTC in your issuing address.

    __Important note on denominations: If you are running a bitcoind node, note that the standard cli denomination is bitcoins not satoshis! In the cert-issuer app, the standard unit is Satoshis (this is common in other apis), and the values are converted to bitcoin first.__

    a. If you're using bitcoind, transfer money by the command line.
    ```
    bitcoin-cli sendtoaddress $issuer <amount>
    ```

    b. Otherwise send a payment to the issuing address with your online wallet


3. Run the issue_certificates.py script to create your certificates. If you've installed the package
you can run:

    ```
    python cert-issuer -c conf.ini
    ```

4. Output
  - The Blockchain Certificates will be located in data/blockchain_certificates.
  - If you ran in the mainnet or testnet mode, you can also see your transaction on a live blockchain explorer. 
    - For example, Blockr.io has explorers for both [testnet](https://tbtc.blockr.io/) and [mainnet](https://blockr.io/).
    - The transaction id is located in the Blockchain Certificate under `signature.anchors[0].sourceId`
