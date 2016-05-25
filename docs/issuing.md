## Issuing Certificates

1. Prerequisites

    - If you installed a local bitcoind node, ensure it's running with your configuration in regtest mode `bitcoind -daemon -conf=your-bitcoin.conf`
    - If you are using the blockchain.info API, start the blockchain.info server `blockchain-wallet-service start --port 3000`. Otherwise, ensure that bitcoind is running.

2. Add your certificates to data/unsigned_certs/

3. Make sure you have enough BTC in your issuing address.
	- Using bitcoind, each certificate costs 15000 satoshi ($0.06 USD)
	    - Again, if you are running in regtest mode, this isn't real money!
	        `bitcoin-cli -conf=your-bitcoin.conf sendtoaddress <your_issuing-address> <amount>`
	- Using the blockchain.info API, each certificate costs: 26435 * total_num_certs + 7790 satoshi (e.g. if you are issuing 1 certificate, it will cost roughly $0.13 USD)
4. Run the create-certificates.py script to create your certificates:
	- To run "remotely" using the Blockchain.info API:
	    `python create-certificates.py`
	- To run using your bitcoind installation:
	    `python create-certificates.py --remote=0`
