## Testnet / Mainnet Addresses

For assistance creating or funding bitcoin / ethereum addresses, see below. 

### Create a Bitcoin issuing address

First, ensure you've created an issuing address appropriate for the Bitcoin chain you are using. Please note:
- regtest or testnet addresses will start with 'm' or 'n'
- mainnet addresses will start with '1'
  
 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__

1. Use bitaddress.org
    - for testnet addresses go to [bitaddress.org?testnet=true](http://bitaddress.org?testnet=true)
    - for mainnet addresses go to [bitaddress.org](http://bitaddress.org)
2. Create an 'issuing address', i.e. the address from which your certificates are issued.
    - save the unencrypted private key to a file (we recommend to store it on a removable drive for security).
    - save the public address as the `issuing_address` value in conf.ini

If you are using a local bitcoin node, you can create addresses by command line. See [bitcoind.md](docs/bitcoind.md)


### Create an Ethereum issuing address

Currently Blockcerts just supports issuing to the Ropsten Ethereum testnet, and the Ethereum mainnet. In Ethereum a public/private key pair is the same accross all test/main networks.

 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__
 
 1. Create issuing address on Myetherwallet
    - Go to https://www.myetherwallet.com/.
    - For the best security turn off your connection to the internet when you are on the create wallet page.
 2. Go through the create wallet process
    - Store the private key on the USB stick and unplug it afterwards.
    - Copy the public key to the `issuing_address` value in conf.ini

### Get coins

Note ensure you've transferred sufficient funds to your issuing address to cover the transaction fee.  Some notes:
- The transaction fee is the same no matter the number of certificates in the batch
- __For Bitcoin:__
  - The default transaction fee used by cert-issuer is 60,000 satoshis for bitcoin (~$2.88 USD, 10/11/2017)
  - Because the transaction fee is a factor in confirmation time, you may decide to increase or decrease this value in the config file (read more about current transaction fee/latency estimates: https://bitcoinfees.21.co/)
- __For Ethereum:__
  - The default gasprice is set at 20 GWei, which makes the transaction price about 0.00047 ETH (~$0.14 USD, 10/11/2017)
  - Lowering the default setting may impact the confirmation time. Please reference http://ethgasstation.info/ to find a fitting gasprice.

#### Obtaining testnet coins

- Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
- Important: make sure you follow the guidance of the testnet faucet provider!
    
#### Obtaining mainnet coins

- If this is your first time purchasing Bitcoin or Ethereum, start by reading starter information:
   - For __Bitcoin__: [https://bitcoin.org/en/getting-started] Specifically, the first section “How to use Bitcoin” is an overview of choosing a wallet, obtaining your first Bitcoins, and securing your money.
   - For __Ethereum__: https://myetherwallet.github.io/knowledge-base/getting-started/getting-started-new.html - MyEtherWallet's knowledge base getting started entry. 
- Transfer a small amount of money to the issuer address created in step 1.
