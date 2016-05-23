# Digital Certificates Project

### Setting Up The VM (optional)
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


## Install
1. Clone the repo: `git clone https://github.com/ml-learning/digital-certificates-v2.git`
2. Create a Python 3 virtual environment: `cd digital-certificates-v2 && virtualenv venv -p python3.4`
3. Activate the virtual environment and install the requirements: `source venv/bin/activate && venv/bin/pip install -r requirements.txt`
4. Create your conf.ini file from the template: `cp conf_template.ini conf.ini`

Next we will populate the conf.ini values

## Installation options
You can use an online bitcoin wallet or run a bitcoind instance locally. The online option is faster to setup, but involves
requesting API access, which requires some turnaround time. The first option describes setup using a blockchain.info online wallet;
the second if you are using bitcoind

### Installation using APIs
Below are steps that will allow you to setup the digital certificates code to interact with the blockchain via the Blockchain.info API. If you do not have bitcoind already running on your computer, these instructions are highly reccomended.

1. Make a [blockchain.info](http://blockchain.info) wallet
2. Verify your blockchain.info account via the link in your email.
3. Request [API Access](https://blockchain.info/api/api_create_code) to your wallet. Ensure you request the 'Create Wallets'
permission.
4. Enter your wallet information into conf.ini

  a. Save the wallet GUID as `wallet_guid` in conf.ini
  b. Save the wallet password as `wallet_password` in conf.ini
  c. When your api key from step 3 arrives, save this as `api_key` in conf.ini

5. Designate an address that will store your bitcoin for issuing the certificates. Transfer a few BTC to this address.

  a.  Save this address as your `storage_address` in conf.ini

6. Install the Blockchain.info API local service [instructions here](https://github.com/blockchain/service-my-wallet-v3).

### Local Bitcoind Installation
Below are instructions are for running the code using bitcoind. To install bitcoind on a Ubuntu server, please follow the
[tutorial here](https://21.co/learn/setup-a-bitcoin-development-environment/#installing-bitcoind-from-source-on-ubuntu).

1. Once your bitcoind instance is up and running, add in the Bitcoin address that you will use for issuing as a "watch address"
 using the command `bitcoin-cli importaddress "<insert_address_here>" ( "ISSUING_ADDRESS" rescan )`. This will take a
 while to run, since it will scan the blockchain for the address's previous transactions.

TODO: any additional config entries needed?

## Creating Certificate and Revocation Addresses

1. Go to [bitaddress.org](http://bitaddress.org)
2. Create an address that will be used as your 'issuing address', i.e. the address from which your certificates are issued.

     a. save the unencrypted private key to your USB drive, in a file called pk_issuing.txt
     b. save the public address as the `issuing_address` value in conf.ini

3. Create an address that will be used as your 'revocation address', i.e. the address you will spend from if you decide to revoke the certificates.

     a. save the unencrypted private key to your USB drive, in a file called pk_revocation.txt
     b. save the public address as the `revocation_address` value in conf.ini

Important! Do not plug in this USB when your computer's wifi is on.


## Verify your conf.ini is complete
Ensure all the required conf.ini values are entered. At this point you should have:

```
issuing_address = "<issuing address>"
revocation_address = "<revocation address>"

usb_name = "<path to usb>"
key_file = "<name of private key file>"

# The below fields are not needed for the local bitcoind installation, but are needed for the blockchain.info configuration
wallet_guid = "<blockchain.info wallet guid>"                    # Your unique identifier to login to blockchain.info
wallet_password = "<blockchain.info wallet password>"            # Your password to login to blockchain.info
storage_address = "<blockchain.info address with storage BTC>"
api_key = "<blockchain.info api key>"
```

## To Run
1. If you are using the blockchain.info API, start the blockchain.info server `blockchain-wallet-service start --port 3000`. Otherwise, ensure that bitcoind is running.
2. Add your certificates to data/unsigned_certs/
3. Make sure you have enough BTC in your storage address. (TODO: my blockchain calculations are lower!)
	1. Using bitcoind, each certificate costs 15000 satoshi ($0.06 USD)
	2. Using the blockchain.info API, each certificate costs: 26435 * total_num_certs + 7790 satoshi (e.g. if you are issuing 1 certificate, it will cost roughly $0.13 USD)
4. Run the create-certificates.py script to create your certificates: 
	1. To run "remotely" using the Blockchain.info API: `python create-certificates.py`
	2. To run using your bitcoind installation: `python create-certificates.py --remote=0`


## Contact
For questions or more information, contact Juliana Nazaré at [juliana@media.mit.edu](mailto:juliana@media.mit.edu).


