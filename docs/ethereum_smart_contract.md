# Ethereum Smart Contract Backend
*v1.1*

## Quick Start
1. [Create Ethereum wallet](https://www.myetherwallet.com/)
1. [Register an ENS name](app.ens.domains/)
1. Get ready to issue
   1. Install cert-deployer
   1. Configure cert-deployer
   1. Deploy smart contract
1. Issue certificates
   1. Install cert-issuer
   1. Run cert-issuer to issue certificates to the blockchain

## Introduction
The value added by this extension lies in the move of core functionalities (e.g. issuance and revocation of certificates) to smart contracts located on the Ethereum blockchain and the utilization of the [Ethereum Name System (ENS)](https://ens.domains/) enabling validation of issuers' identities. Backwards compatibility for all tool components is ensured at any time –  a flag in the corresponding config file is used to choose the desired issuing or verification method.

## Why use the smart contract backend?
Using simple transactions on the blockchain to store merkle root hashes requires external data to be stored and queried from web servers. Each issuing institution has to host both a file proving its identity and a list of revoked certificates on a server. This approach is prone to availability and security issues – particularly for smaller institutions – as it is neither trivial to run an updated and secure web server, nor the most efficient option. Even a temporary server outage would lead to valid certificates being indistinguishable from invalid ones. Longer lasting outages could thus make existing certificates useless.

Tackling this way of managing the issuer’s identity and the list of revoked certificates, we identified the following requirements that need to be met:

- Maximum availability
- Consistent and continuous chain of trust
- Cost efficiency – costs per transaction have to be constant and proportional to the number of batches issued or revoked

## Design
The issuer does no longer need to host the `issuer.json` and `revocation_list.json` files.
As a consequence, asserting issuer's identity and revoking certificates are handled directly on the blockchain. The basis of the changes we propose is the introduction of a smart contract to act as a certificate (hash) store and the Ethereum Name Service.

Both issuing and revoking can be done via the smart contract on the Ethereum blockchain. Since the Bitcoin blockchain does not provide the required capabilities, it will not be supported. Additionally, we introduce the ENS to link human-readable names to smart contracts. As a consequence, the issuer’s identity can be publicly linked to their smart contract, when their ENS name is public knowledge. Ideally the institution asserts it on their website.

### Revocation
The revocation process was transferred to the smart contract. Now, instead of certificate id's their hashes are used to attach a *state* to them on the blockchain. This state can be `not issued`, `revoked` or `valid`.

Initially, as a batch is issued, the state associated with the batch's merkle root hash is set to `valid`. To revoke the batch, this state can be set to `revoked`.
Individual certificates can be revoked as well. Initially a single certificate's hash has the state `not issued`, as it was not explicitly issued. The certificate's state can be set to `revoked` the same way a batches merkle root hash can. This is reclected in the verification process as well.

### Identity
A strong chain of trust has to be established to trust the issuer's identity. In the initial BlockCerts design this was done by hosting an issuer.json file that has to be validated by the verifier. This file is generally accessible via a URL on the certificate. The only information to be cross-referenced by humans: the domain name itself, which, for any given institution, is public knowledge. Thus, a strong chain of trust can be established – as long as the server is online.

This issuing method moves this chain of trust completely onto the blockchain by using ENS which allows any addressable blockchain resources to be linked to a human-readable name, e.g. tu-berlin.eth. When an institution’s Blockcerts smart contract is deployed, its ENS domain is instructed to point to this contract. In any certificates issued to this contract, this ENS name will be present as the URL has been previously. If institutions advertise their domain and it becomes public knowledge, this chain of trust established supersedes the former, as ENS comes with the same availability guarantees as the blockchain itself. In the verification process only the institution's ENS name has to be manually verified, as before the institution's hostname.

## Usage
### Smart contract
Once before starting the issuing process a smart contract has to be deployed by an institution. The contract bundles functionality for both issuing and revoking certificates. It works by storing storing a hash representation of the certificate or a batch of certificates. Each hash has one of three states associated to it: `not issued` (default), `revoked` or `valid`.
Internally the use of a mapping ensures constant complexity for both read and write access to certificate states, thus minimizing gas-costs. Since no gas-costs are incurred by calling data from the ethereum blockchain, the verification process is free of charge.

To only allow authorized write access to the contract, it is restricted to the ethereum account that deployed the contract. Internally, this is ensured by an `only_owner` modifier.

The contract is shipped in source with the deployer package and only compiled upon deployment onto the blockchain. This is beneficial for two reasons: First, the code can be reviewed, ensuring it contains no malevolent functions. Second, if an institution wishes to make changes to the inner workings of the contract, this can be easily done.

### Cert-deployer
The cert-deployer package provides the tools to prepare the infrastructure necessary to issue and revoke certificates. On a basic level three things happen one after another: The contract is locally compiled from source, then deployed onto the blockchain, and lastly the institution’s ENS name is linked to the contract's address.

This new component aims to use familiar abstractions to the rest of the projects.
The main difference is the way blockchain resources are accessed. The Web3 library is used to connect to local or public blockchain nodes to be able to call smart contract methods the same way as native method calls. This change is reflected in the cert-issuer and cert-verifier as well.

#### Configuration
Configuration is done via the `conf_eth.ini` file. Cert-deployer's configuration closely resembles that of cert-issuer. All options are detailed in the subsequent section.

`deploying_address = <Your Ethereum address>`  
The ethereum account's address.

`chain = <ethereum_ropsten|ethereum_mainnet>`  
Choice of deployment on Ethereum Mainnet or the Ropsten test network.

`node_url = <ethereum web3 public node url (e.g. infura)>`  
The web3py library requires an ethereum node that is compatible with the json-rpc interface. The easiest option is to use a public node e.g. infura’s, or connect to a locally-run node such as geth or parity.

`ens_name = <Your ENS name registered with your ethereum address>`  
The institution's ENS name - has to be registered beforehand via the [ENS Management App](https://app.ens.domains/).

`overwrite_ens_link = <Do you want to overwrite a present link to a smart contract? True/False>`  
In a scenario, where an ENS domain already points to an existing smart contract, this flag has to be explicitly set to overwrite this link. This is meant to prevent accidental loss of data. This should normally be set to False, except you explicitly want to deploy a new contract that your ENS entry points to.

`usb_name= </Volumes/path-to-usb/>`  
`key_file= <file-you-saved-pk-to>`  
Path and file name of the account's private key.

#### Setup and requirements
There are two administrative requirements potential issuers have to meet before they can start deploying smart contracts.
1. Have an Ethereum wallet with enough currency
1. Be owner or controller of an [ENS domain](app.ens.domains/)
1. Issue v2 certificates

All dependencies required can be installed by running (preferrably inside a [virtual environment](docs/virtualenv.md)):

`python setup.py install`

### Cert-issuer
The issuer was subject to two main changes: First, another Ethereum blockchain handler was added that enables interaction with smart contract functions via Web3. On this basis, the ability to issue and revoke certificates was set up and some configuration options were added for these features.

#### Components
The main contribution to the issuer can be found in the addition of an ethereum_sc blockchain handler. Being a wrapper for the web3 library this module enables the issuer to interact with smart contracts in general and, via the interface model defined in `ServiceProviderConnector`, implements the same interface as the other blockchain handlers. Thus, only minor adjustments were required to enable issuing of certificate hashes to the smart contract.
The main changes made to the existing program logic were needed to embed the necessary information about how to verify within the certificates. This information includes a valid contract address and contract abi. More information on this can be found in the cert-schema section. The required information is generated in `merkle_tree_generator.py`.

#### Revocation
The cert-issuer tool is also used to revoke certificates. As opposed to using certificate IDs to identify certificates in the revocation list, certificate and merkle root hashes are used for a reduced footprint on the blockchain. When running with the `--revoke` flag, a json file containing a list of hashes to be revoked is referenced. One by one, the hashes are processed. In case of failure, the hashes that have not been revoked at that point are written back into the file.

The `revocations.json` should be of the following format:
```json
{
  "hashes_to_be_revoked": [
    "637ec732fa4b7b56f4c15a6a12680519a17a9e9eade09f5b424a48eb0e6f5ad0"
  ]
}

```

#### Configuration
The following options were added:

`issuing_method = <transaction(default)|smart_contract>`  
This indicates whether to use the smart contract backend or the current transaction-based approach. As explained below, due to dependency clashes this distinction also has to be made at install time.

`node_url = <ethereum web3 (public) node url (e.g. infura)>`  
The web3py library requires an ethereum node that is compatible with the json-rpc interface. The easiest option is to use a public node e.g. infura’s, or connect to a locally-run node such as geth or parity.

`ens_name = <Your ENS name registered with your ethereum address that points to your smart contract>`  
The ENS domain that points to a smart contract deployed with cert-deployer.

`revocation_list_file = <path-to-your-revocation_list>`  
This file lists certificates that will be revoked when passing the --revoke flag when running from the command line.

#### Setup and requirements
The smart contract backend requires the web3 module to interact with the blockchain. This dependency is incompatible with the ethereum module required by the current implementation. For this reason, there is an install-time option to install the smart contract backend. The use of a [virtual environment](virtualenv.md) is highly recommended.

`python setup.py install experimental --blockchain=ethereum_smart_contract`

Backwards compatibility is preserved insofar as that the current implementation can be installed in a separate virtual environment. To switch, there is only one flag to be adapted in the config file. We further switched to the chainpoint3 library, a fork of the chainpoint library, as there was another dependency conflict.

### Cert-verifier
#### Description
The verifier has been extended to support the usage of issuer smart contracts while ensuring backwards compatibility.
All necessary information is embedded into the certificate (also see [cert-schema](docs/ethereum_smart_contract.md#cert-schema)). Using ENS entries, it is verified if a given smart contract belongs to the issuer.

Following checks are done to verify a certificate, which is issued with the new method:

1. Tamper Check - *same as before*
1. Expiration Check - *same as before*
1. Revocation / Validity Check
1. ENS Check

In order to prevent attacks, where a smart contract is spoofed the ENS name has to be verified manually.

#### Tamper Check
We adjusted the tamper check to support our implementation. This way, the verifier is able to check if a certificate has been tampered or not. The relevant fields are hashed and compared to the provided target hash. The merkle proof is calculated the same as before and will cause the validation to fail if the target hash does not belong to the merkle root hash.

#### Expiration Check
For the expiration check there were no changes made.

#### Revocation / Validity check
The issuer owned smart contract provides a function, which returns the state associated to any given hash.
Possible states are `not_issued`, `revoked` or `valid`.
To verify if a certificate is valid, the following checks are done:  
- If merkle root hash and target hash differ from each other, the merkle root hash should be `valid` and not `revoked`, while the target hash should be `not_issued` (as it wasn't explicitly issued).
- If the batch consists of only one certificate i.e. merkle root hash and target hash are equal, the merkle root hash should be `issued` and not `revoked`.

#### ENS Check
Since ENS is our trust anchor, we have added a new verification step. This verification step compares the address in the ENS Name with the smart contract address embedded in the anchors source id field and checks if they match. If there is an attempt to change the ENS Name in the certificate, the verifier will mark the validation as failed.

#### Configuration
The config file is used to set Ethereum node addresses to be used in the verifying process.

#### Setup
All dependencies required can be installed by running (preferrably inside a [virtual environment](docs/virtualenv.md)):

`python setup.py install`

### Cert-schema
#### Description
In order to verify certificates issued to a smart contract the necessary information needs to be stored in the certificate file.
The V2 schema was slightly modified by adding additional fields into the `anchors` sections to hold the additional information necessary to verify certificates issued to the smart contract.

#### Changes
The `anchors` field looks as follows:

`ens_name`  
Contains an ENS name of a certificate issuer.

`sourceId`  
Contains the smart contract's address that this certificate was issued to. This value is compared to the address the ENS name points to.

`type`  
Is used by the verifier to identify the method to use in the verification process. Example: `["type" : "ETHSmartContract"]`

`chain`  
Which chain the certificate was issued to. As smart contracts are not supported by the Bitcoin blockchain, only the Ethereum chains are supported.

`contract_abi`  
The application binary interface (ABI) is necessary to communicate with the smart contract.

`chain`, `type` and `sourceId` are present in the [chainpoint v2 schema](https://chainpoint.org/) used.
The additional fields used are therefore non-standard extensions. Ideally, a way is found to incorporate the functionality into the standard or a way is found to offer the same functionality while adhering to the standard.
