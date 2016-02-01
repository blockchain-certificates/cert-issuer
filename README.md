# Digital Certificates Project

### Setting Up The VM 
1. Install [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
2. Make a Linux VM (768MB of memory)
	* Make virtual harddisk (8GB) of VDI (Virtual Disk Image)
	* Select dynamically allocated memory
	* Download the .dmg file for Ubuntu [here](http://www.ubuntu.com/download/desktop)
	* Install Ubuntu on the VM by clicking the .dmg file and clicking through the install steps
7. Install Github `sudo apt-get install git`
8. Install pip `sudo apt-get install python-pip`
9. Install python-dev `sudo apt-get install python-dev`
9. Install virtualenv `sudo pip install virtualenv`

## Installation using APIs
Below are steps that will allow you to setup the digital certificates code to interact with the blockchain via the Blockchain.info API. If you do not have bitcoind already running on your computer, these instructions are highly reccomended.

1. Make a [blockchain.info](http://blockchain.info) wallet and designate an address that will store your bitcoin for issuing the certificates. This is not the same as your issuing address, which you should NOT add to your wallet. Transfer a few BTC to this address. FYI: This will be referenced as your `STORAGE_ADDRESS` in the code.
2. Verify your blockchain.info account via the link in your email.
3. Enable the blockchain.info API to access your wallet [Account Settings > IP Restrictions > Enable API Access]
4. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3). This will require you to request an API key, which may take 24 hours to recieve. This API key will be referenced as your `API_KEY` in the code.

## Local Bitcoind Installation
Below are instructions are for running the code using bitcoind. To install bitcoind on a Ubuntu server, please follow the [tutorial here](https://21.co/learn/setup-a-bitcoin-development-environment/#installing-bitcoind-from-source-on-ubuntu).

1. Once your bitcoind instance is up and running, add in the Bitcoin address that you will use for issuing as a "watch address" using the command `bitcoin-cli importaddress "<insert_address_here>" ( "ISSUING_ADDRESS" rescan )`. This will take a while to run, since it will scan the blockchain for the address's previous transactions.

## Creating Bitcoin Addresses
1. Go to [bitaddress.org](http://bitaddress.org) and create two address, the issuing address and the revocation address. Print these out to save them. 
2. Save the unencrypted private key for the issuing address to a USB. Do not plug in this USB when your computer's wifi is on. FYI: These will be referenced as your `ISSUING_ADDRESS` and `REVOCATION_ADDRESS` respectivly in the code.

## Install 
1. Clone the repo: `git clone https://github.com/ml-learning/digital-certificates-v2.git`
2. Create a Python 3 virtual environment: `cd digital-certificates-v2 && virtualenv venv -p python3.4`
3. Activate the virtual environment and install the requirements: `source venv/bin/activate && venv/bin/pip install -r requirements.txt`
4. Create a secrets.py file: `nano secrets.py`

In the secrets.py file, place the following:

```
ISSUING_ADDRESS = "<issuing address>"
REVOCATION_ADDRESS = "<revocation address>"

USB_NAME = "<path to usb>"
KEY_FILE = "<name of private key file>"

# The below fields are not needed for the local bitcoind installation, but are for the blockchain.info configuration
WALLET_GUID = "<blockchain.info wallet guid>" # Your unique identifier to login to blockchain.info
WALLET_PASSWORD = "<blockchain.info wallet password>" # Your password to login to blockchain.info
STORAGE_ADDRESS = "<blockchain.info address with storage BTC>" 
API_KEY = "<blockchain.info api key>"
```

### To Run
1. Start the blockchain.info server `blockchain-wallet-service start --port 3000`
2. Add your certificates to data/unsigned_certs/
3. Make sure you have enough BTC in your storage address. The amount needed is approximatly 0.10 cents (USD) per certificate.
4. Run the create-certificates.py script to create your certificates: 
	1. To run "remotely" using the Blockchain.info API: `python create-certificates.py`
	2. To run using your bitcoind installation: `python create-certificates.py --remote=0`

## Contact
For questions or more information, contact Juliana Nazaré at [juliana@media.mit.edu](mailto:juliana@media.mit.edu).

