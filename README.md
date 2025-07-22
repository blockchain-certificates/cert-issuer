[![Verifiable Credential Compliance result](https://badgen.net/badge/Verifiable%20Credentials%20v1/failure/red?icon=https://www.w3.org/Icons/WWW/w3c_home_nb-v.svg)](https://www.blockcerts.org/vc-compliance-report.html)
[![Build Status](https://travis-ci.org/blockchain-certificates/cert-issuer.svg?branch=master)](https://travis-ci.org/blockchain-certificates/cert-issuer)
[![PyPI version](https://badge.fury.io/py/cert-issuer.svg)](https://badge.fury.io/py/cert-issuer)

# cert-issuer

The cert-issuer project issues blockchain certificates by creating a transaction from the issuing institution to the
recipient on the Bitcoin or Ethereum blockchains. That transaction includes the hash of the certificate itself.

Blockcerts v3 is released. This new version of the standard leverages the [W3C Verifiable Credentials specification](https://www.w3.org/TR/vc-data-model/), and documents are signed with [MerkleProof2019 LD signature](https://w3c-ccg.github.io/lds-merkle-proof-2019/). Use of [DIDs (Decentralized Identifiers)](https://www.w3.org/TR/did-core/) is also possible to provide more cryptographic proof of the ownership of the issuing address. See [section](#working-with-dids) down below

Cert-issuer v3 is _not_ backwards compatible and does not support Blockcerts v2 issuances. If you need to work with v2, you need to install cert-issuer v2 or use the [v2](https://github.com/blockchain-certificates/cert-issuer/tree/v2) branch of this repo.
You may expect little to no maintenance to the v2 code at this point.

## Using a VC API compliant issuing server

To run this in a server, use https://github.com/blockchain-certificates/cert-issuer-vc-api.

## Web resources

For development or testing using web requests, check out the documentation at [docs/web_resources.md](./docs/web_resources.md).

# Quick start using Docker

## Getting the Docker image

This uses bitcoind in regtest mode. This route makes many simplifications to allow a quick start, and is intended for
experimenting only.

1. First ensure you have Docker installed. [See our Docker installation help](docs/docker_install.md).

2. Clone the repo and change to the directory

   ```
   git clone https://github.com/blockchain-certificates/cert-issuer.git && cd cert-issuer
   ```

3. From a command line in cert-issuer dir, build your docker container:

   ```
   docker build -t bc/cert-issuer:1.0 .
   ```

4. Read before running!

   - Once you launch the docker container, you will make some changes using your personal issuing information. This flow mirrors what you would if you were issuing real certificates.
   - To avoid losing your work, you should create snapshots of your docker container. You can do this by running:

     ```
     docker ps -l
     docker commit <container for your bc/cert-issuer> my_cert_issuer
     ```

5. When you're ready to run:

   ```
   docker run -it bc/cert-issuer:1.0 bash
   ```

6. Copy the blockchain certificates you issued out of the docker container to a local directory
   ```
   docker cp <container for your bc/cert-issuer>:/etc/cert-issuer/data/blockchain_certificates/<your-certificate-guid>.json <path_to_local_dir>
   ```

## Create issuing address

**Important**: this is a simplification to avoid using a USB, which needs to be inserted and removed during the
standard certficate issuing process. Do not use these addresses or private keys for anything other than experimenting.

Ensure your docker image is running and bitcoind process is started

1. Creating a wallet first with `bitcoin-cli createwallet “<wallet name>”`

   ```
   bitcoin-cli createwallet "testwallet"
   ```

2. Load wallet `bitcoin-cli loadwallet "<path to the directory of the created wallet>"`

   ```
   bitcoin-cli loadwallet "/root/.bitcoin/regtest/wallets/testwallet/"
   ```

   You can `bitcoin-cli listwallets` to check if your wallet is loaded

3. Create an _issuing address_ and save the output as follows:

   ```
   issuer=`bitcoin-cli getnewaddress`
   ```

   ```
   sed -i.bak "s/<issuing-address>/$issuer/g" /etc/cert-issuer/conf.ini
   ```

   ```
   bitcoin-cli dumpprivkey $issuer > /etc/cert-issuer/pk_issuer.txt
   ```

   `sed` command allows us to quickly remove or replace the content without having to open a file.

4. Don't forget to save snapshots so you don't lose your work (see step 4 of client setup)

## Issuing certificates

1.  Add your certificate to `/etc/cert-issuer/data/unsigned_certificates/`:

    To use a sample unsigned certificate as follows:

    ```
    cp /cert-issuer/examples/data-testnet/unsigned_certificates/verifiable-credential.json /etc/cert-issuer/data/unsigned_certificates/
    ```

    If you created your own unsigned certificate using cert-tools (assuming you placed it under `data/unsigned_certificates`):

    ```
    cp <cert-issuer-home>/data/unsigned_certificates/<your-cert-guid>.json /etc/cert-issuer/data/unsigned_certificates/
    ```

2.  Make sure you have enough BTC in your issuing address. You're using bitcoind in regtest mode, so you can print money. This should give you 50 (fake) BTC:

    ```
    bitcoin-cli -generate 101
    ```

    ```
    bitcoin-cli getbalance
    ```

3.  **(Optional)** If you see this error:

    ```
    Fee estimation failed. Fallbackfee is disabled. Wait a few blocks or enable -fallbackfee.
    ```

    You might have to allow fallback fee in your `bitcoin.conf` (use Vim as the text editor). Add this line to `bitcoin.conf`: `fallbackfee=0.00001`

    ```
    vi /root/.bitcoin/bitcoin.conf
    ```

    You have to kill bitcoind daemon using `ps aux` and `kill <pid>` , then start it again with `bitcoind -daemon=<path to bitcoin conf file>` to apply new changes.

4.  Send the money to your issuing address. Note that bitcoin-cli's standard denomination is bitcoins not satoshis! (In our app, the standard unit is satoshis.) This command sends 5 bitcoins to the address:

    ```
    bitcoin-cli sendtoaddress $issuer 5
    ```

5.  Issue the certificates on the blockchain. Add `--verification_method` with issuer's DID (learn more about Decentralized Identifiers [here](https://www.w3.org/TR/did-core/) and how to work with them [here](https://github.com/blockchain-certificates/cert-issuer/#working-with-dids))

    ```
    cert-issuer -c /etc/cert-issuer/conf.ini --verification_method "<issuer's URL/DID>"
    ```

    Or, you can add `verification_method=<issuer's URL/DID>` in `/etc/cert-issuer/conf.ini`:

    ```
    vi /etc/cert-issuer/conf.ini
    ```

    Then run:

    ```
    cert-issuer -c /etc/cert-issuer/conf.ini
    ```

6.  Your Blockchain certificates are located in `/etc/cert-issuer/data/blockchain_certificates`. Copy these to your local machine, and add them to cert-viewer's `cert_data` folder to see your certificates in the Certificate Viewer.

    ```
    docker ps  // shows the docker containerId
    docker cp <containerId>:/etc/cert-issuer/data/blockchain_certificates <localPath>/cert-viewer/cert_data
    ```

# How batch issuing works

While it is possible to issue one certificate with one Bitcoin transaction, it is far more efficient to use one Bitcoin transaction to issue a batch of certificates.

The issuer builds a Merkle tree of certificate hashes and registers the Merkle root as the OP_RETURN field in the Bitcoin transaction.

Suppose the batch contains `n` certificates, and certificate `i` contains recipient `i`'s information. The issuer hashes each certificate and combines them into a Merkle tree:

![](img/merkle.png)

The root of the Merkle tree, which is a 256-bit hash, is issued on the Bitcoin blockchain. The complete Bitcoin transaction outputs are described in 'Transaction structure'.

The Blockchain Certificate given to recipient `i` contains a [2019 Merkle Proof Signature Suite](https://w3c-ccg.github.io/lds-merkle-proof-2019/)-formatted proof, proving that certificate `i` is contained in the Merkle tree.

![](img/blockchain_certificate_components.png)

This receipt contains:

- The Bitcoin transaction ID storing the Merkle root
- The expected Merkle root on the blockchain
- The expected hash for recipient `i`'s certificate
- The Merkle path from recipient `i`'s certificate to the Merkle root, i.e. the path highlighted in orange above. `h_i -> … -> Merkle root`

The [verification process](https://github.com/blockchain-certificates/cert-verifier-js#verification-process) performs computations to check that:

- The hash of certificate `i` matches the value in the receipt
- The Merkle path is valid
- The Merkle root stored on the blockchain matches the value in the receipt

These steps establish that the certificate has not been tampered with since it was issued.

## Hashing a certificate

The Blockchain Certificate JSON contents without the `proof` node is the certificate that the issuer created. This is the value needed to hash for comparison against the receipt. Because there are no guarantees about ordering or formatting of JSON, first canonicalize the certificate (without the `proof`) against the JSON LD schema. This allows us to obtain a deterministic hash across platforms.

The detailed steps are described in the [verification process](https://github.com/blockchain-certificates/cert-verifier-js#verification-process).

## What should be in a batch?

How a batch is defined can vary, but it should be defined such that it changes infrequently. For example, “2016 MIT grads” would be preferred over “MIT grads” (the latter would have to be updated every year). The size of the batch is limited by the 100KB maximum transaction size imposed by the Bitcoin network. This will amount to a maximum of around 2,000 recipients per certificate batch.

## Transaction structure

One Bitcoin transaction is performed for every batch of certificates. There is no limit to the number of certificates that may be included in a batch, so typically batches are defined in logical groups such as "Graduates of Fall 2017 Robotics Class".

![](/img/tx_out.png)

The transaction structure is the following:

- Input:
  - Minimal amount of bitcoin (currently ~$.80 USD) from Issuer's Bitcoin address
- Outputs:
  - OP_RETURN field, storing a hash of the batch of certificates
  - Optional: change to an issuer address

The OP_RETURN output is used to prove the validity of the certificate batch. This output stores data, which is the hash of the Merkle root of the certificate batch. At any time, we can look up this value on the blockchain to help confirm a claim.

The Issuer Bitcoin address and timestamp from the transaction are also critical for the verification process. These are used to check the authenticity of the claim, as described in [verification process](https://github.com/blockchain-certificates/cert-verifier-js#verification-process).

# Issuing options

The Quick Start assumed you are issuing certificates in Bitcoin regtest mode, which doesn't actually write to a public blockchain. To actually write your transaction, you need to run in testnet (with test coins -- not real money) or mainnet (real money).

We recommend starting in testnet before mainnet.

By default, cert-issuer does not assume you have a bitcoin/ethereum node running locally, and it uses APIs to look up and broadcast transactions. There is API support for both testnet and mainnet chains.

If you do want to use a local bitcoin node, [see details about installing and configuring a bitcoin node for use with cert-issuer](docs/bitcoind.md) before continuing.

These steps walk you through issuing in testnet and mainnet mode. Note that the prerequisites and the configuration for the Bitcoin issuing and the Ethereum issuing differ.

## Prerequisites

Decide which chain (Bitcoin or Ethereum) to issue to and follow the steps. Follow the steps for the chosen chain.

### Install cert-issuer

By default, cert-issuer issues to the Bitcoin blockchain. Run the default setup script if this is the mode you want:

```
python setup.py install

```

To issue to the ethereum blockchain, run the following:

```
python setup.py experimental --blockchain=ethereum

```

### Getting started with Bitcoin/Ethereum addresses

See the docs here for helpful tips on creating / funding blockchain addresses: [docs/testnet_mainnet_addresses](./docs/testnet_mainnet_addresses.md)

## Configuring cert-issuer

Edit your conf.ini file (the config file for this application). See [here](./docs/ethereum_configuration.md) for more details on Ethereum configuration.
The private key for bitcoin should be the WIF format.

```
issuing_address = <issuing-address>

# issuer URL / DID
verification_method = <verification-method>

chain=<bitcoin_regtest|bitcoin_testnet|bitcoin_mainnet|ethereum_goerli|ethereum_sepolia|ethereum_ropsten|ethereum_mainnet|mockchain>

usb_name = </Volumes/path-to-usb/>
key_file = <file-you-saved-pk-to>

unsigned_certificates_dir=<path-to-your-unsigned-certificates>
blockchain_certificates_dir=<path-to-your-blockchain-certificates>
work_dir=<path-to-your-workdir>

no_safe_mode

# advanced: uncomment the following line if you're running a bitcoin node
# bitcoind
```

Notes:

- The `bitcoind` option is technically not required in `regtest` mode. `regtest` mode _only_ works with a local bitcoin node. The quick start in docker brushed over this detail by installing a regtest-configured bitcoin node in the docker container.
- The Ethereum option does not support a local (test)node currently. The issuer will broadcast the transaction via the Etherscan API or an RPC of their choice.

## Working with DIDs

To issue and verify a Blockcerts document bound to a DID you need to:

- generate a DID document referencing the public key source of the issuing address. The verification supports all the DID methods from the [DIF universal resolver](https://uniresolver.io/), but it is recommended you provide your own resolver to the verification library.
- it is also expected that the DID document contains a `service` property configured similarly to as follows:
  ```
    "service": [
      {
        "id": "#service-1",
        "type": "IssuerProfile",
        "serviceEndpoint": "https://www.blockcerts.org/samples/3.0/issuer-blockcerts.json"
      }
    ]
  ```
- reference the DID through the `issuer` property of the document to be issued as Blockcerts. Either directly as a string or as the `id` property of an object:
  ```
    "issuer": "did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ",
  ```
  or
  ```
    "issuer": {
      "id": "did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ",
      ... /* more custom data here. Note that the data from the distant Issuer Profile has display preference in Blockcerts Verifier */
    }
  ```
- finally add to your `conf.ini` file the `verification_method` property pointing to the public key matching the issuing address:
  ```
  verification_method=did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1
  ```

You may try to see the full example DID document by looking up `did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ` in the [DIF universal resolver](https://uniresolver.io/).

## Multiple Signatures
Blockcerts implements ChainedProof2021 draft proposal (https://hackmd.io/@RYgJMHAGSlaLMaQzwYjvsQ/SJoDWwTdK).
This means that cert-issuer can be used to sign with MerkleProof2019 a document that was already signed.

Currently, only ordered proofs are supported, which means that the next MerkleProof2019 proof hashes the content of the document
up until the previous proof.

Depending on the nature of the initial proof, consumers might find themselves confronted to a 
JSONLD dereferencing error when the context is not preloaded by Blockcerts ecosystem.

Please note that this may happen with context documents that are not proof context.

In order to circumvent this issue, this library offers a way to specify specific context to be preloaded
before issuance.

Consumers will need to use both `--context_urls` and `--context_file_paths` properties at the same time, and values need to be specified in matching order.

The path to the directory where consumers store directory is left at the discretion of said consumer, 
but you should know that it will be looked up relative to the execution path (CWD).

### CLI example
```
 python -m cert_issuer -c conf.ini --context_urls https://w3id.org/security/suites/ed25519-2020/v1 https://w3id.org/security/suites/multikey-2021/v1 --context_file_paths data/context/ed25519.v1.json data/context/multikey2021.v1.json
```

### conf.ini example
Define in your conf.ini file something like this:

```
context_urls=[https://w3id.org/security/suites/ed25519-2020/v1, https://w3id.org/security/suites/multikey-2021/v1]
context_file_paths=[data/context/ed25519.v1.json, data/context/multikey2021.v1.json]
```

### HINT
You can create local copies of context file with the following command:
```
curl https://w3id.org/security/suites/ed25519-2020/v1 -L >> data/context/ed25519.v1.json
```

## Issuing

1. Add your certificates to data/unsigned_certs/

2. If you've installed the package you can issue certificates by running:

```
python cert-issuer -c conf.ini
```

3. Output

- The Blockchain Certificates will be located in data/blockchain_certificates.
- If you ran in the mainnet or testnet mode, you can also see your transaction on a live blockchain explorer.
  - For Bitcoin, Blockchain.com has explorers for both [testnet](https://www.blockchain.com/explorer?view=btc-testnet) and [mainnet](https://www.blockchain.com/explorer?view=btc).
  - For Ethereum, Etherscan has explorers for [goerli](https://goerli.etherscan.io/), [sepolia](https://sepolia.etherscan.io/), [ropsten](https://ropsten.etherscan.io/) and [mainnet](https://etherscan.io/)
  - The transaction id is located in the Blockchain Certificate under `signature.anchors[0].sourceId`

# Contributing

More information on contributing to the cert-issuer codebase can be found in [docs/contributing.md](./docs/contributing.md)

# Advanced setup

- [Installing and using a local bitcoin node](docs/bitcoind.md)

# Examples

The files in examples/data-testnet contain results of previous runs.

# FAQs

## Checking transaction status

You can validate your transaction before sending by looking it up by rawtx at blockchain.info. Example:

```
curl 'https://blockchain.info/rawtx/45a9306dfe99820eb346bb17ae0b64173ac11cac2d0e4227c7a7cacbcc0bad31?cors=true'
```

For an Ethereum transaction, you'll need to use a different explorer, which might require an API key for raw JSON
output. To view a transaction in a web browser, you might try something like this:

- Ethereum Mainnet: https://etherscan.io/tx/0xf537d81667c8011e34e1f450e18fd1c5a8a10c770cd0acdc91a79746696f36a3
- Ethereum Goerli (testnet): https://goerli.etherscan.io/tx/0xfb593f186a274f58f861e5186150bc692ed533c7af50efb094f756ccb81c7023
- Ethereum Sepolia (testnet): https://sepolia.etherscan.io/tx/0xa5484369839ba54cd3be71271155fc1a76b52499607dcddbf682ee04534a3f95
- Ethereum Ropsten (testnet): https://ropsten.etherscan.io/tx/0xf537d81667c8011e34e1f450e18fd1c5a8a10c770cd0acdc91a79746696f36a3

## Mac scrypt problems

If your install on Mac is failing with a message like the following, try the [workaround described in this thread](https://github.com/ethereum/pyethereum/issues/292) or the [workaround described here](https://github.com/pyca/cryptography/issues/2692#issuecomment-272773481).

```
fatal error: 'openssl/aes.h'
      file not found
#include <openssl/aes.h>
```

# Contact

Contact us at [the Blockcerts community forum](http://community.blockcerts.org/).
