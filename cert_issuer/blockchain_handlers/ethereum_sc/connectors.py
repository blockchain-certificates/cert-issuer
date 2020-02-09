import json
import os
from errors import UnableToSignTxError

from cert_issuer.models import ServiceProviderConnector
from web3 import Web3, HTTPProvider


def get_abi(contract):
    """
    Returns smart contract abi.
    possible values for contract: "blockcerts", "ens_registry"
    """

    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, f"data/{contract}_abi.json")

    with open(path, "r") as f:
        raw = f.read()
    abi = json.loads(raw)
    return abi


# this class can be used for both ENS contracts as well as our own ("cert_store")
class EthereumSCServiceProviderConnector(ServiceProviderConnector):
    """
    Collects abi, address, contract data and instantiates a contract object
    """
    def __init__(self, app_config, contract_address, abi_type="cert_store", private_key=None, cost_constants=None):
        self.cost_constants = cost_constants

        self.app_config = app_config
        self._private_key = private_key

        abi = get_abi(abi_type)

        self._w3 = Web3(HTTPProvider(self.app_config.node_url))
        self._w3.eth.defaultAccount = self.app_config.issuing_address

        self._contract_obj = self._w3.eth.contract(address=contract_address, abi=abi)

    def get_balance(self, address):
        return self._w3.eth.getBalance(address)

    def create_transaction(self, method, *argv):
        # estimated_gas = self._contract_obj.functions[method](*argv).estimateGas()

        tx_options = {
            'nonce': self._w3.eth.getTransactionCount(self._w3.eth.defaultAccount),
            'gas': self.cost_constants.get_gas_limit(),
            'gasPrice': self.cost_constants.get_gas_price()
        }

        construct_txn = self._contract_obj.functions[method](*argv).buildTransaction(tx_options)
        return construct_txn

    def broadcast_tx(self, signed_tx):
        tx_hash = self._w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        print("tx_receipt: ", tx_receipt)

        return tx_receipt.transactionHash.hex()

    def transact(self, method, *argv):
        """
        Sends a signed transaction on the blockchain and waits for a response.
        If initialized with private key this class can sign the transaction.
        In general, an external signer should be used in conjunction with
        create_transaction() and broadcast_tx.
        """
        if self._private_key is None:
            raise UnableToSignTxError("This method is only available if a private key was passed upon initialization")

        prepared_tx = self.create_transaction(method, *argv)
        signed_tx = self._sign_transaction(prepared_tx)
        txid = self.broadcast_transaction(signed_tx)
        return txid

    def _sign_transaction(self, prepared_tx):
        acct = self._w3.eth.account.from_key(self._private_key)

        try:
            signed_tx = acct.sign_transaction(prepared_tx)
            return signed_tx
        except Exception:
            raise UnableToSignTxError('You are trying to sign a non transaction type')

    def call(self, method, *argv):
        return self._contract_obj.functions[method](*argv).call()
