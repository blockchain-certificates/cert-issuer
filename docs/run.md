## Issuing Certificates
1. If you are using the blockchain.info API, start the blockchain.info server `blockchain-wallet-service start --port 3000`. Otherwise, ensure that bitcoind is running.
2. Add your certificates to data/unsigned_certs/
3. Make sure you have enough BTC in your storage address. (TODO: my blockchain calculations are lower!)
	1. Using bitcoind, each certificate costs 15000 satoshi ($0.06 USD)
	2. Using the blockchain.info API, each certificate costs: 26435 * total_num_certs + 7790 satoshi (e.g. if you are issuing 1 certificate, it will cost roughly $0.13 USD)
4. Run the create-certificates.py script to create your certificates:
	1. To run "remotely" using the Blockchain.info API: `python create-certificates.py`
	2. To run using your bitcoind installation: `python create-certificates.py --remote=0`
