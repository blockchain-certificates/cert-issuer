import json
import subprocess
import time

import content_hash
import ipfshttpclient
# from ens import ENS

from solc import compile_standard
from namehash.namehash import namehash
import onchaining_tools.config as config
import onchaining_tools.path_tools as tools
from onchaining_tools.connections import MakeW3, ContractConnection


class ContractDeployer(object):
    ''' Compiles, signes and deploys a smart contract on the ethereum blockchain
    Args:
        object(web3 object): instantiated web3 connection to ethereum node
            print("cat : " + str(client.cat(res['Hash'])))
    '''

    def __init__(self):
        '''Defines blockchain, initializes ethereum wallet, calls out compilation and deployment functions'''
        self.current_chain = config.config["current_chain"]
        w3Factory = MakeW3()
        self._w3 = w3Factory.w3
        self._acct = w3Factory.account
        self._pubkey = self._acct.address
        gas_limit = 600000
        gas_price = self._w3.eth.gasPrice
        gas_balance = self._w3.eth.getBalance(self._pubkey)
        if gas_balance < gas_limit*gas_price:
            exit('Your gas balance is not sufficient for performing all transactions.')


    def do_deploy(self):
        self._open_ipfs_connection()
        self._compile_contract()
        self._deploy()
        self._update_ens_content()

    def _open_ipfs_connection(self):
        try:
            subprocess.Popen(["ipfs", "init"])
            subprocess.Popen(["ipfs", "daemon"])
            time.sleep(10)
            self._client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
            print("connected to IPFS")
        except:
            print("Not connected to IPFS -> start daemon to deploy contract info on IPFS")
            self._client = None

    def _update_ens_content(self):
        self.ipfs_hash = ""
        if self._client is not None:
            self.ipfs_hash = self._client.add(tools.get_contr_info_path())['Hash']
            print("IPFS Hash is: " + self.ipfs_hash)
            print("You can check the abi on: https://ipfs.io/ipfs/" + self.ipfs_hash)
            print("You can check the abi on: ipfs://" + self.ipfs_hash)
        if self.current_chain == "ropsten":
            self._assign_ens()
        if self._client is not None:
            subprocess.run(["ipfs", "shutdown"])
            self._client.close()

    def _compile_contract(self):
        '''Compiles smart contract, creates bytecode and abi'''

        # loading contract file data
        with open(tools.get_contract_path()) as source_file:
            source_raw = source_file.read()
        # loading configuration data
        with open(tools.get_compile_data_path()) as opt_file:
            raw_opt = opt_file.read()
            opt = json.loads(raw_opt)

        opt["sources"]["BlockCertsOnchaining.sol"]["content"] = source_raw
        compiled_sol = compile_standard(opt)

        # defining bytecode and abi
        self.bytecode = compiled_sol[
            'contracts']['BlockCertsOnchaining.sol']['BlockCertsOnchaining']['evm']['bytecode']['object']
        self.abi = json.loads(compiled_sol[
                                  'contracts']['BlockCertsOnchaining.sol']['BlockCertsOnchaining']['metadata'])[
            'output']['abi']

    def _deploy(self):
        '''Signes raw transaction and deploys it on the blockchain'''
        contract = self._w3.eth.contract(abi=self.abi, bytecode=self.bytecode)

        # defining blockchain and public key of the ethereum wallet
        acct_addr = self._pubkey

        # building raw transaction
        estimated_gas = contract.constructor().estimateGas()
        #print("Estimated gas: ", estimated_gas)
        construct_txn = contract.constructor().buildTransaction({
            'nonce': self._w3.eth.getTransactionCount(acct_addr),
            'gas': estimated_gas*2
        })

        # signing & sending a signed transaction, saving transaction hash
        signed = self._acct.sign_transaction(construct_txn)
        tx_hash = self._w3.eth.sendRawTransaction(signed.rawTransaction)
        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        print("Gas used: ", tx_receipt.gasUsed)

        # saving contract data
        with open(tools.get_contr_info_path(), "r") as f:
            raw = f.read()
            contr_info = json.loads(raw)

        self.contr_address = tx_receipt.contractAddress
        data = {'abi': self.abi, 'address': self.contr_address}
        contr_info["blockcertsonchaining"] = data

        with open(tools.get_contr_info_path(), "w+") as f:
            json.dump(contr_info, f)

        # print transaction hash
        print(f"deployed contr <{self.contr_address}>")

    def _assign_ens(self):
        ens_domain = "blockcerts.eth"
        label = "tub"
        ens_registry = ContractConnection ("ropsten_ens_registry")
        # ns = ENS.fromWeb3(self._w3)
        node = namehash(ens_domain)
        subdomain = self._w3.keccak(text=label)

        #add Subdomain
        ens_registry.functions.transact("setSubnodeOwner", node, subdomain, "0xB4d9313EE835b3d3eE7759826e1F3C3Ac23dFaf3")
        
        #set Public Resolver
        ens_subdomain = label + "." + ens_domain
        subnode = namehash(ens_subdomain)
        ens_registry.functions.transact("setResolver", subnode, "0x12299799a50340FB860D276805E78550cBaD3De3")

        #set Address
        ens_resolver = ContractConnection("ropsten_ens_resolver")
        self.contr_address = self._w3.toChecksumAddress(self.contr_address)
        ens_resolver.functions.transact("setAddr", subnode, self.contr_address)
        ens_resolver.functions.transact("setName", subnode, ens_subdomain)
        
        #set Content
        codec = 'ipfs-ns'
        if self._client is not None:
            chash = content_hash.encode(codec, self.ipfs_hash)
            ens_resolver.functions.transact("setContenthash", subnode, chash)

        addr = ens_resolver.functions.call("addr", subnode)
        name = ens_resolver.functions.call("name", subnode)
        
        content = "that is empty"
        if self._client is not None:
            content = (ens_resolver.functions.call("contenthash", subnode)).hex()
            content = content_hash.decode(content)

        print(f"set contr <{addr}> to name '{name}' with content '{content}'")


if __name__ == '__main__':
    '''
        Calls out respective functionatilites.
    '''
    ContractDeployer().do_deploy()
