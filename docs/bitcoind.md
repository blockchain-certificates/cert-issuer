# Local Bitcoin node instructions

## Installation

Start by reading an overview of requirements and other concerns when [running a Bitcoin full node](https://bitcoin.org/en/full-node). [Bitcoin.org's developer examples](https://bitcoin.org/en/developer-examples) provide more context to the steps here.

These instructions walk through the steps for [installing Bitcoin Core for your OS](https://github.com/bitcoin/bitcoin/tree/master/doc). For example, [OSX instructions](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)

## Configuration

The bitcoin.conf file determines how your bitcoin node will run, and which chain it uses. 

Locate the bitcoin.conf file for your environment. Then edit or create a new file named bitcoin.conf (first save the old one with a different name), with the following entries for the chain you want to use

### Configuring for regtest mode

```
rpcuser=<your-user>
rpcpassword=<your-password>
regtest=1
relaypriority=0
rpcallowip=127.0.0.1
rpcport = 8332
rpcconnect = 127.0.0.1
```

### Configuring for bitcoin_testnet mode

```
rpcuser=<your-user>
rpcpassword=<your-password>
testnet=1
server=1
rpctimeout=30
rpcport=8332
```


### Configuring for bitcoin_mainnet mode

```
rpcuser=<your-user>
rpcpassword=<your-password>
testnet=0
server=1
rpctimeout=30
rpcport=8332
```

## Running the bitcoind daemon
 
 Start the bitcoind daemon with the bitcoin.conf file:

```
bitcoind -daemon -conf=your-bitcoin.conf
```


## Commands

If you're running a bitcoin node locally, you can use the CLI to generate addresses, transfer funds, and (in regtest mode) generate funds

### Creating addresses 

You can create the issuer address by command line and dump the private key

```
issuer=`bitcoin-cli getnewaddress`
bitcoin-cli dumpprivkey $issuer > <PATH_TO_USB>/<ISSUER_FILE_NAME>.txt
```

Then add the issuer address to the cert-issuer conf.ini

`issuing_address=$issuer` (insert $issuer value from above)

### Sending funds

_Important note on denominations: the standard cli denomination is bitcoins not satoshis! In the cert-issuer app, the standard unit is Satoshis (this is common in other apis), and the values are converted to bitcoin first.__

```
bitcoin-cli sendtoaddress $issuer <amount>
```

### Creating funds (regtest only)

```
bitcoin-cli generate 101
```
