import json

from web3 import Web3, HTTPProvider

import path_tools as tools


class MakeW3(app_config):
    '''
    Defines a private key of an ethereum wallet to be used for the transaction,
    node url to be used for communication with ethereum blockchain and instantiates the
    web3 connection with ethereum node
    '''
    def __init__(self):
        '''
        Defines public & private keys of a wallet, defines an ethereum node
        that will be used for communication with blockchain
        '''
        current_chain = app_config.chain
        #self._privkey = config.config["wallets"][current_chain]["privkey"] THAT SHOULD BE NEEDED AND USED BY SIGNER METHOD!!!
        self._url = app_config.issuer_node

        self.w3 = self._create_w3_obj()
        self.account = self._get_w3_wallet()
        self.pubkey = self.account.address
        self.w3.eth.defaultAccount = self.pubkey

    def _create_w3_obj(self):
        '''Instantiates a web3 connection with ethereum node'''
        return Web3(HTTPProvider(self._url))

    def _get_w3_wallet(self):
        '''Connects a private key to the account that is going to be used for the transaction'''
        return self.w3.eth.account.from_key(self._privkey)


class ContractConnection(app_config):
    '''Collects abi, address, contract data and instantiates a contract object'''
    def __init__(self, contract_name):
        #self.contract_name = contract_name
        self._w3Factory = MakeW3(app_config)
        self.w3 = self._w3Factory.w3
        self._contract_info = self._get_contract_info()
        self.contract_obj = self._create_contract_object()
        self.functions = self.ContractFunctions(self._w3Factory, self.contract_obj)

    def _create_contract_object(self):
        '''Returns contract address and abi'''
        address = self._get_address()
        abi = self._get_abi()
        return self.w3.eth.contract(address=address, abi=abi)

    def _get_contract_info(self):
        '''Returns transaction data from a config file'''
        with open(tools.get_contr_info_path()) as file:
            data = file.read()
            contract_info = json.loads(data)
        return contract_info

    def _get_abi(self):
        '''Returns transaction abi'''
        return self._contract_info[self.contract_name]["abi"]

    def _get_address(self):
        '''Returns transaction address'''
        return self._contract_info[self.contract_name]["address"]

    class ContractFunctions(object):
        def __init__(self, w3Factory, contract_obj):
            self._w3Factory = w3Factory
            self._w3 = self._w3Factory.w3
            self._contract_obj = contract_obj
            current_chain = config.config["current_chain"]

            #TO DO: priv key needed here, needs to be executed differently!
            self._privkey = config.config["wallets"][current_chain]["privkey"]
            self.acct = self._w3Factory.account
            self.acct_addr = self.acct.address

        def _get_tx_options(self, estimated_gas):
            '''Returns raw transaction'''
            return {
                'nonce': self._w3.eth.getTransactionCount(self.acct_addr),
                'gas': estimated_gas*2
            }

        def transact(self, method, *argv):
            '''Sends a signed transaction on the blockchain and waits for a response'''
            # gas estimation
            estimated_gas = self._contract_obj.functions[method](*argv).estimateGas()
            print("Estimated gas for " + str(method) + ": " + str(estimated_gas))
            tx_options = self._get_tx_options(estimated_gas)
            # building a transaction
            construct_txn = self._contract_obj.functions[method](*argv).buildTransaction(tx_options)
            # signing a transaction
            signed = self.acct.sign_transaction(construct_txn)
            # sending a transaction to the blockchain and waiting for a response
            tx_hash = self._w3.eth.sendRawTransaction(signed.rawTransaction)
            tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
            print("Gas used: " + str(method) + ": " + str(tx_receipt.gasUsed))

            #TO DO: not sure if that is the right tx_id the blockcerts issuer wants to print. Need to confirm!
            return tx_receipt.transactionHash

        def call(self, method, *argv):
            return self._contract_obj.functions[method](*argv).call()
