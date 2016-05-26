# Issuing Certificates

1. Prerequisites

    - Ensure your bitcoin client is running
        - If using Docker:
        ```
        docker run -it <your saved image> bash
        ```
    - If you are using the blockchain.info API, start the blockchain.info server

        ```
        blockchain-wallet-service start --port 3000
        ```

2. Add your certificates to data/unsigned_certs/

3. Make sure you have enough BTC in your issuing address.

    a. If you're using bitcoind in regtest mode, you need to print some money first

    ```
    bitcoin-cli generate 101
    bitcoin-cli getbalance   << 50 fake bitcoins!
    ```

    Then Transfer money to your issuing address -- note the bitcoin environment's denomination is bitcoins not satoshis! In our
    app (and this is common in bitcoin apis), the standard unit is Satoshis, and the values are converted to bitcoin first.

    ```
    bitcoin-cli sendtoaddress $issuer 5   << 5 BTC
    ```

    b. If you're not using regtest mode you need real money
    	- Using bitcoind (not in regtest mode), each certificate costs 15000 satoshi ($0.06 USD)
    	`bitcoin-cli -conf=your-bitcoin.conf sendtoaddress <your-issuing-address> <amount>`

	    - Using the blockchain.info API, each certificate costs: 26435 * total_num_certs + 7790 satoshi (e.g. if you are issuing 1 certificate, it will cost roughly $0.13 USD)


4. Run the create-certificates.py script to create your certificates:
    `python create-certificates.py --config=conf.ini`


```

```

8. Issue some certificates

```
source /issuer/env/bin/activate
cd /issuer/issuer
python certificate_issuer.py -c /etc/issuer/conf.ini
```





