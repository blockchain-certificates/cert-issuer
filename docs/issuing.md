# Issuing Certificates

## Prerequisites

- Ensure you've installed and configured your Bitcoin wallet dependencies. If you haven't yet, see [Certificate Issuing Options](http://www.blockcerts.org/guide/options.html) for an overview of issuing options.
- If you haven't already, make sure your conf.ini (for this application) is correct. See - [Bitcoin node instructions](bitcoind.md) or [Blockchain.info instructions](blockchain_info.md), depending on which you are using.
- Ensure your wallet software is running:
    - If you are using a Bitcoin node, ensure you've started your bitcoin daemon. (In the Quick Start docker container, it will run on startup)
        ```
        bitcoind -daemon -conf=your-bitcoin.conf
        ```
    - Otherwise, if you are using the blockchain.info API, ensure your local blockchain.info service is running
        ```
        blockchain-wallet-service start --port 3000
        ```
- Ensure you've created issuing addresses appropriate for the Bitcoin chain you are using. See [creating addresses](make_addresses.md) for details
    - regtest or testnet addresses will start with 'm' or 'n'
    - mainnet addresses will start with '1'

## Issuing

1. Add your certificates to data/unsigned_certs/

2. Make sure you have enough BTC in your issuing address. Each certificate costs 12750 satoshi ($0.08 USD)

    __Important note on denominations: If you are running a bitcoind node, note that the standard cli denomination is bitcoins not satoshis! In the cert-issuer app, the standard unit is Satoshis (this is common in other apis), and the values are converted to bitcoin first.__

    a. If you're using bitcoind, transfer money by the command line.
    ```
    bitcoin-cli sendtoaddress $issuer <amount>
    ```

    b. Otherwise send a payment to the issuing address with your online wallet

3. Run the sign_certificates script to sign your certificates. If you've installed the package
you can run:

    ```
    python cert-signer -c conf.ini
    ```

4. Make sure the previous step succeeded. At this point, the signed certs should be under data/signed_certs, and the certs you previously added to unsigned certs should be moved under the 'archive' dir

5. Run the issue_certificates.py script to create your certificates. If you've installed the package
you can run:

    ```
    python cert-issuer -c conf.ini
    ```

6. Output
  - The Blockchain Certificates will be located in data/blockchain_certificates.
  - If you ran in the mainnet or testnet mode, you can also see your transaction on a live blockchain explorer. 
    - For example, Blockr.io has explorers for both [testnet](https://tbtc.blockr.io/) and [mainnet](https://blockr.io/).
    - The transaction id is located in the Blockchain Certificate under `receipt.anchors[0].sourceId`
