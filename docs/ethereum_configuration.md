# Issuing on the Ethereum Blockchain

To issue on the Ethereum blockchain, you will to configure the following:

## pk_issuer.txt
This should hold the Hex string of the BIP32 derived private key, generated from your own seed, prefixed by `0x`.

## conf.ini
```
issuing_address=0xYOUR_ADDRESS # matching with the private key above
chain=ethereum_goerli # one of ['ethereum_goerli', 'ethereum_sepolia', 'ethereum_ropsten', 'ethereum_mainnet']
```

`ethereum_ropsten` is DEPRECATED because the Ropsten has been announced to close in Q4 2022.