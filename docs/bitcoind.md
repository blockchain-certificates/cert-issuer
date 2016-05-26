# Local bitcoind instructions

You can also install a local bitcoind node. As with the docker install path, you can run bitcoind in regtest mode
to experiment without spending money.


## Install
1. Follow the instructions to [build Bitcoin Core for your OS](https://github.com/bitcoin/bitcoin/tree/master/doc)

    - for example, [OSX instructions](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)


2. Edit the bitcoin config to run in regtest mode.

    a. Edit or create a new bitcoin.conf file, with the following entries:
     ```
     rpcuser=bitcoinrpc
     rpcpassword=6c8a25acd56561b2a039197e86d07c97
     regtest=1
     relaypriority=0
     rpcallowip=127.0.0.1
     rpcport = 8332
     rpcconnect = 127.0.0.1
     ```

    b. Start the bitcoind daemon with this config file:

    ```
    bitcoind -daemon -conf=your-bitcoin.conf
    ```

