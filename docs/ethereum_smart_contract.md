# Ethereum Smart Contract Backend

## Introduction
The value added by this extension lies in the move of core functionalities (e.g. issuance and revocation of certificates) to smart contracts located on the Ethereum blockchain and the utilization of the [Ethereum Name System (ENS)](https://ens.domains/) enabling a sustainable and secure authentication of issuers' identities.
Backwards compatibility for all tool components is ensured at any time –  a flag in the corresponding config file is used to choose the desired issuing or verification method.

## Why use the smart contract backend?
Using simple transactions on the blockchain to store merkle root hashes requires external data to be stored and queried from web servers. Each issuing institution has to host both a file proving its identity and a list of revoked certificates on a server. This approach is prone to availability and security issues – particularly for smaller institutions – as it is neither trivial to run an updated and secure web server, nor the most efficient option. Even a temporary server outage would lead to valid certificates being indistinguishable from invalid ones. Longer lasting outages could thus make existing certificates useless.

Tackling this way of managing the issuer’s identity and the list of revoked certificates, we identified the following requirements that need to be met:

- Maximum availability
- Consistent and continuous chain of trust
- Cost efficiency – costs per transaction have to be constant and proportional to the number of batches issued or revoked

## Approach
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

## Implementation
### Smart contract
Once before starting the issuing process a smart contract has to be deployed by an institution. The contract bundles functionality for both issuing and revoking certificates. It works by storing storing a hash representation of the certificate or a batch of certificates. Each hash has one of three states associated to it: `not issued` (default), `revoked` or `valid`.
Internally the use of a mapping ensures constant complexity for both read and write access to certificate states, thus minimizing gas-costs. Since no gas-costs are incurred by calling data from the ethereum blockchain, the verification process is free of charge.

To only allow authorized write access to the contract, it is restricted to the ethereum account that deployed the contract. Internally, this is ensured by an `only_owner` modifier.

The contract is shipped in source with the deployer package and only compiled upon deployment onto the blockchain. This is beneficial for two reasons: First, the code can be reviewed, ensuring it contains no malevolent functions. Second, if an institution wishes to make changes to the inner workings of the contract, this can be easily done.

### Cert-deployer
The cert-deployer package provides the tools for deploying Blockcerts smart contracts to the Ethereum blockchain and preparing them to receive and revoke issued certificates. On a basic level three things happen one after another: Initially, the contract is locally compiled from source, deployed onto the blockchain, and the institution’s ENS domain linked to the contract afterwards (contract_address).

Though being a completely new feature within the Blockcerts environment, syntactic and stylistic compatibility in every way has always been of highest priority throughout the entire implementation process. Nevertheless, crucial differences, as using the web3 framework and infura nodes (node_url) for interacting with the Ethereum blockchain and relating services, are part of our optimization approach that can be found in our cert-issuer and cert-verifier modifications, too.

#### Configuration
As indicated earlier, there are two administrative requirements potential issuers have to meet before they can start deploying smart contracts. First, they have to set up an Ethereum wallet and, second, register an ENS domain (ideally a top-level one). Both the ropsten test network as well as the Ethereum mainnet chains are supported. In a scenario, where an ENS domain already points to an existing smart contract, the configuration contains a flag (overwrite_ens_link) that has to be explicitly set to enable overwriting this link. This is especially meant to prevent accidental data loss or unnecessary expenses.

Finally, according configuration parameters, as it has always been, have to be entered to the conf_eth.ini. Most of the cert-deployer’s configuration is similar to the one of the cert-issuer being presented more detailed in the subsequent section.

#### Setup and dependencies
All dependencies required can be installed by running:

`python setup.py install`

### Cert-issuer
The issuer was subject to two main changes: First, another Ethereum blockchain handler was added with an accessible wrapper that enables interaction with smart contract functions. On this basis, the ability to issue and revoke certificates was set up and some configuration options were added for these features.

#### Components
The main contribution to the issuer can be found in the addition of an ethereum_sc blockchain handler. Being a wrapper for the web3 library this module enables the issuer to interact with smart contracts in general and, via the interface model defined in ServiceProviderConnector, implements the same interface as the other blockchain handlers. Thus, only minor adjustments were required to enable issuing of certificate hashes to the smart contract.
The main changes made to the existing program logic were needed to embed the necessary information about how to verify within the certificates. This information includes a valid contract address and contract abi. More information on this can be found in the cert-schema section. The required information is generated in merkle_tree_generator.py.

Lastly, the ability to revoke certificates was implemented. In the current implementation certificate IDs are used to identify certificates in the revocation list. For a reduced footprint on the blockchain, we opted to identify certificates by their hash. When running with the --revoke flag, a json file containing a list of hashes to be revoked is referenced. One by one, the hashes are processed. In case of failure, the hashes that have not been revoked at that point are written back into the file. A list of certificate hashes that have already been revoked is kept locally.

#### Configuration
The following options were added:

`issuing_method = <transaction(default)|smart_contract>`
This indicates whether to use the smart contract backend or the current transaction-based approach. As explained below, due to dependency clashes this distinction also has to be made at install time.

`node_url = <ethereum web3 (public) node url (e.g. infura)>`
The web3py library requires an ethereum node that is compatible with the json-rpc interface. The easiest option is to use a public node e.g. infura’s, or connect to a locally-run node such as geth or parity.

`ens_name = <Your ENS name registered with your ethereum address that points to your smart contract>`
The ENS domain that points to a smart contract deployed with cert-deployer.

`contract_address = <smart_contract_address>`
This argument is not required. The contract address can be queried from the provided ENS entry.

`revocation_list_file = <path-to-your-revocation_list>`
This file lists certificates that will be revoked when passing the --revoke flag when running from the command line.

#### Setup and dependencies
The smart contract backend requires the web3 module to interact with the blockchain. This dependency is incompatible with the ethereum module required by the current implementation. For this reason, there is an install-time option to install the smart contract backend.

`python setup.py install experimental --blockchain=ethereum_smart_contract`

Backwards compatibility is preserved insofar as that the current implementation can be installed in a separate virtual environment. To switch, there is only one flag to be adapted in the config file. We further switched to the chainpoint3 library, a fork of the chainpoint library, as there was another dependency conflict.

### Cert-verifier
Description
The verifier has been extended to support the usage of issuer smart contracts while ensuring backwards compatibility. Using ENS entries, the package can now verify if a given smart contract belongs to a certain issuer. An ABI, an ENS entry and a smart contract address are now embedded in the anchor field of signed certificates. In addition to the new verification process, we tried to make the console outputs more user friendly.

Following checks are done to verify a certificate, which is issued with the new method:

1. Tamper Check - same as before
1. Expiration Check - same as before
1. Revocation / Validity Check
1. ENS Check

#### Tamper Check
We adjusted the tamper check to support our implementation. This way, the verifier is able to check if a certificate has been tampered or not. The important certificate fields are hashed and compared to the provided target hash. The merkle proof is calculated the same as before and will cause the validation to fail if the target hash does not belong to the merkle root hash.

#### Expiration Check
For the expiration check there were no changes made. We implemented the same step as before for our smart contract-based certificates.

#### Revocation / Validity check
The issuer owned smart contract provides a function, which returns three different states of an hash.
These states are not issued, revoked and valid. To verify if a certificate is valid, the following checks are done:

- If merkle root hash and target hash differ from each other, the merkle root hash should be issued and not revoked, while the target hash should not be revoked.
- If merkle root hash and target hash are equal, then the merkle root hash should be issued and not revoked.

#### ENS Check
Since ENS is our trust anchor, we have added a new verification step. This verification step compares the address in the ENS Name with the smart contract address embedded in the anchors source id field and checks if they match. If there is an attempt to change the ENS Name in the certificate, the verifier will mark the validation as failed.
Configuration
We have added a config.ini file to enable later changes of the ens registry or the blockchain access point. We believe this config file is a good addition for individual use cases, although it should stay the same in most of the cases. Only the <chain> parameter should be either set to <mainnet> or <ropsten>, while ropsten is the fallback chain. It should be mentioned that the nodes in config.ini are only recommendations from our side.

### Cert-schema
#### Description
We have extended the current v2 schema implementation by adding some extra relevant fields into “signature” : “anchors” field, that are meant to map the correlation between the certificate being issued and corresponding smart contract and an ENS name owner.

Our current design requires ENS name owners to have their ENS domains registered and the corresponding smart contract deployed on the blockchain. Both of them are used in the verification process described above, specifically in the validity- and ENS check.
Changes
Following fields got included and/or used in our issuer extension:
`ens_name`: Contains an ENS name of a certificate issuer. Requires to be stated in the config.ini file in <ens_name> field by the issuer before issuing a certificate. Example: [“ens_name” : “blockcerts.ens”]
`sourceId`: Maps current smart contract connected to ENS name owner.  Smart contract address is taken from the config.ini file in <contract_address> field and is then compared with the smart contract stated at the ENS name owner entry. Example: [“sourceId” : “0xdB5...”]
`type`: Is used by the verifier to identify the existence of a smart contract this certificate is connected to. Example: [“type” : “ETHSmartContract”]
`chain`: Requires ethereum blockchain to be issued on to have a possibility to use smart contracts. Example: [“chain” : “ethereum”]
`contract_abi`: Is used to map the application binary interface. Determines functions of the smart contract and how they are being called (including inputs, outputs, data types etc.)

`type` and `sourceId` fields already existed in the current schema implementation and are described by the json schema standard. In our implementation they are currently not used as it is stated in the standard.
