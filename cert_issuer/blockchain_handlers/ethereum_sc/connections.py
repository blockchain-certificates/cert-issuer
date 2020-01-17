import json
import os

from web3 import Web3, HTTPProvider

# import onchaining_tools.config as config
# import onchaining_tools.path_tools as tools


class MakeW3(object):
    '''
    Defines a private key of an ethereum wallet to be used for the transaction,
    node url to be used for communication with ethereum blockchain and instantiates the
    web3 connection with ethereum node
    '''
    def __init__(self, node_url):
        '''
        Defines public & private keys of a wallet, defines an ethereum node
        that will be used for communication with blockchain
        '''
        # current_chain = config.config["current_chain"]
        # self._privkey = config.config["wallets"][current_chain]["privkey"]
        self._url = config.config["wallets"][current_chain]["url"]

        self.w3 = self._create_w3_obj()
        self.account = self._get_w3_wallet()
        self.pubkey = self.account.address
        self.w3.eth.defaultAccount = self.pubkey

    def _create_w3_obj(self):
        '''Instantiates a web3 connection with ethereum node'''
        return Web3(HTTPProvider(self._url))

    def _get_w3_wallet(self):
        '''Connects a private key to the account that is going to be used for the transaction'''
        pass


class ContractConnection(object):
    '''Collects abi, address, contract data and instantiates a contract object'''
    def __init__(self, app_config):
        self.app_config = app_config

        self._w3 = Web3(HTTPProvider(self.app_config.node_url))
        self._w3.eth.defaultAccount = self.app_config.issuing_address

        self.abi = self._get_abi()

        self.contract_obj = self._create_contract_object()

        self.functions = self.ContractFunctions(self._w3, self.contract_obj)

    def _create_contract_object(self):
        '''Returns contract address and abi'''
        address = self._get_address()
        abi = self._get_abi()
        return self._w3.eth.contract(address=address, abi=abi)

    def _get_abi(self):
        '''Returns transaction abi'''

        dir_path = os.path.dirname(os.path.abspath(__file__))
        abi_path = os.path.join(dir_path, "data/contract_abi.json")

        with open(abi_path, "r") as f:
            raw = f.read()
        abi = json.loads(raw)
        return abi

    def _get_address(self):
        '''Returns transaction address'''
        return self.app_config.contract_address

    class ContractFunctions(object):
        def __init__(self, w3, contract_obj):
            self._w3 = w3
            self._contract_obj = contract_obj

        def _get_tx_options(self, estimated_gas):
            '''Returns raw transaction'''
            return {
                'nonce': self._w3.eth.getTransactionCount(self._w3.eth.defaultAccount),
                'gas': estimated_gas * 2
            }

        def create_transaction(self, method, *argv):
            estimated_gas = self._contract_obj.functions[method](*argv).estimateGas()
            tx_options = self._get_tx_options(estimated_gas)
            construct_txn = self._contract_obj.functions[method](*argv).buildTransaction(tx_options)
            return construct_txn

        def broadcast_tx(self, signed):
            tx_hash = self._w3.eth.sendRawTransaction(signed.rawTransaction)
            tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
            return tx_receipt.transactionHash.hex()

        # depracated (sort of)
        def transact(self, method, *argv):
            '''Sends a signed transaction on the blockchain and waits for a response'''
            # gas estimation
            estimated_gas = self._contract_obj.functions[method](*argv).estimateGas()
            # print("Estimated gas for " + str(method) + ": " + str(estimated_gas))
            tx_options = self._get_tx_options(estimated_gas)
            # building a transaction
            construct_txn = self._contract_obj.functions[method](*argv).buildTransaction(tx_options)
            # signing a transaction
            # TODO outsource signing of txn
            signed = self.acct.sign_transaction(construct_txn)
            # sending a transaction to the blockchain and waiting for a response
            tx_hash = self._w3.eth.sendRawTransaction(signed.rawTransaction)
            tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
            return tx_receipt
            # print("Gas used: " + str(method) + ": " + str(tx_receipt.gasUsed))

        def call(self, method, *argv):
            return self._contract_obj.functions[method](*argv).call()
