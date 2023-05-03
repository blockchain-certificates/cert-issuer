import logging
import time

import requests
import web3
from web3 import Web3, HTTPProvider

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

from cert_core import Chain
from cert_issuer.models import ServiceProviderConnector
from cert_issuer.errors import BroadcastError

BROADCAST_RETRY_INTERVAL = 30
MAX_BROADCAST_ATTEMPTS = 3


class EthereumServiceProviderConnector(ServiceProviderConnector):
    # param local_node indicates if a local node is running or if the tx should be broadcast to external providers
    def __init__(
            self,
            ethereum_chain,
            app_config,
            local_node=False):
        self.ethereum_chain = ethereum_chain

        self.local_node = local_node

        # initialize connectors
        self.connectors = {}

        # Configure Ethereum mainnet connectors
        eth_provider_list = []
        if hasattr(app_config, 'ethereum_rpc_url'):
            self.ethereum_rpc_url = app_config.ethereum_rpc_url
            eth_provider_list.append(EthereumRPCProvider(self.ethereum_rpc_url))

        etherscan_api_token = None
        if hasattr(app_config, 'api_token'):
            logging.warning('The api_token config property is deprecated in favor of the etherscan_api_token property.  It still works, but please switch over soon.')
            etherscan_api_token = app_config.etherscan_api_token
        if hasattr(app_config, 'etherscan_api_token'):
            etherscan_api_token = app_config.etherscan_api_token
        eth_provider_list.append(EtherscanBroadcaster('https://api.etherscan.io/api', etherscan_api_token))
        # eth_provider_list.append(MyEtherWalletBroadcaster('https://api.myetherwallet.com/eth', None))
        self.connectors[Chain.ethereum_mainnet] = eth_provider_list

        # Configure Ethereum Ropsten testnet connectors
        rop_provider_list = []
        if hasattr(app_config, 'ropsten_rpc_url'):
            self.ropsten_rpc_url = app_config.ropsten_rpc_url
            rop_provider_list.append(EthereumRPCProvider(self.ropsten_rpc_url))
        rop_provider_list.append(EtherscanBroadcaster('https://api-ropsten.etherscan.io/api', etherscan_api_token))
        # rop_provider_list.append(MyEtherWalletBroadcaster('https://api.myetherwallet.com/rop', None))
        self.connectors[Chain.ethereum_ropsten] = rop_provider_list

        # Configure Ethereum Goerli testnet connectors
        goe_provider_list = []
        if hasattr(app_config, 'goerli_rpc_url'):
            self.goerli_rpc_url = app_config.goerli_rpc_url
            goe_provider_list.append(EthereumRPCProvider(self.goerli_rpc_url))
        goe_provider_list.append(EtherscanBroadcaster('https://api-goerli.etherscan.io/api', etherscan_api_token))
        self.connectors[Chain.ethereum_goerli] = goe_provider_list

        # Configure Ethereum Sepolia testnet connectors
        sep_provider_list = []
        if hasattr(app_config, 'sepolia_rpc_url'):
            self.sepolia_rpc_url = app_config.sepolia_rpc_url
            sep_provider_list.append(EthereumRPCProvider(self.sepolia_rpc_url))
        sep_provider_list.append(EtherscanBroadcaster('https://api-sepolia.etherscan.io/api', etherscan_api_token))
        self.connectors[Chain.ethereum_sepolia] = sep_provider_list

    def get_providers_for_chain(self, chain, local_node=False):
        return self.connectors[chain]

    def get_balance(self, address):
        for m in self.get_providers_for_chain(self.ethereum_chain, self.local_node):
            try:
                logging.debug('m=%s', m)
                balance = m.get_balance(address)
                return balance
            except Exception as e:
                logging.warning(e)
                pass
        return 0

    def get_address_nonce(self, address):
        for m in self.get_providers_for_chain(self.ethereum_chain, self.local_node):
            try:
                logging.debug('m=%s', m)
                nonce = m.get_address_nonce(address)
                return nonce
            except Exception as e:
                logging.warning(e)
                pass
        return 0

    def broadcast_tx(self, tx):

        last_exception = None
        final_tx_id = None

        # Broadcast to all available api's
        for attempt_number in range(0, MAX_BROADCAST_ATTEMPTS):
            for m in self.get_providers_for_chain(self.ethereum_chain, self.local_node):
                try:
                    logging.debug('m=%s', m)
                    txid = m.broadcast_tx(tx)
                    if (txid):
                        logging.info('Broadcasting succeeded with method_provider=%s, txid=%s', str(m), txid)
                        if final_tx_id and final_tx_id != txid:
                            logging.error(
                                'This should never happen; fail and investigate if it does. Got conflicting tx_ids=%s and %s. Hextx=%s',
                                final_tx_id, txid, tx.as_hex())
                            raise Exception('Got conflicting tx_ids.')
                        final_tx_id = txid
                    return txid
                except Exception as e:
                    logging.warning('Caught exception trying provider %s. Trying another. Exception=%s',
                                    str(m), e)
                    last_exception = e

            # At least 1 provider succeeded, so return
            if final_tx_id:
                return final_tx_id
            else:
                logging.warning('Broadcasting failed. Waiting before retrying. This is attempt number %d',
                                attempt_number)
                time.sleep(BROADCAST_RETRY_INTERVAL)

        ##in case of failure:
        logging.error('Failed broadcasting through all providers')
        logging.error(last_exception, exc_info=True)
        raise BroadcastError(last_exception)


class EthereumRPCProvider(object):
    def __init__(self, ethereum_url):
        self.ethereum_url = ethereum_url
        self.w3 = Web3(HTTPProvider(ethereum_url))

    def broadcast_tx(self, tx):
        logging.info('Broadcasting transaction with EthereumRPCProvider')
        response = self.w3.eth.sendRawTransaction(tx).hex()
        return response

    def get_balance(self, address):
        """
        Returns the balance in Wei.
        """
        response = self.w3.eth.getBalance(account=address, block_identifier="latest")
        logging.info('Getting balance with EthereumRPCProvider: %s', response)
        return response

    def get_address_nonce(self, address):
        """
        Looks up the address nonce of this address.
        Necessary for the transaction creation.
        """
        logging.info('Fetching nonce with EthereumRPCProvider')
        response = self.w3.eth.getTransactionCount(address, "pending")
        return response


class EtherscanBroadcaster(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def send_request(self, method, url, data=None):
        headers = {
            'User-Agent': 'Python-urllib/3.8'
        }
        response = requests.request(method, url, data=data, headers=headers)
        return response

    def broadcast_tx(self, tx):
        tx_hex = tx

        broadcast_url = self.base_url + '?module=proxy&action=eth_sendRawTransaction'
        if self.api_token:
            broadcast_url += '&apikey=%s' % self.api_token
        response = self.send_request('POST', broadcast_url, {'hex': tx_hex})
        if 'error' in response.json():
            logging.error("Etherscan returned an error: %s", response.json()['error'])
            raise BroadcastError(response.json()['error'])
        if int(response.status_code) == 200:
            if response.json().get('message', None) == 'NOTOK':
                raise BroadcastError(response.json().get('result', None))
            tx_id = response.json().get('result', None)
            logging.info("Transaction ID obtained from broadcast through Etherscan: %s", tx_id)
            return tx_id
        logging.error('Error broadcasting the transaction through the Etherscan API. Error msg: %s', response.text)
        raise BroadcastError(response.text)

    def get_balance(self, address):
        """
        returns the balance in wei
        with some inspiration from PyWallet
        """
        broadcast_url = self.base_url + '?module=account&action=balance'
        broadcast_url += '&address=%s' % address
        broadcast_url += '&tag=pending'
        if self.api_token:
            broadcast_url += '&apikey=%s' % self.api_token
        response = self.send_request('GET', broadcast_url)
        if int(response.status_code) == 200:
            if response.json().get('message', None) == 'NOTOK':
                raise BroadcastError(response.json().get('result', None))
            balance = int(response.json().get('result', None))
            logging.info('Balance check succeeded: %s', response.json())
            return balance
        raise BroadcastError(response.text)

    def get_address_nonce(self, address):
        """
        Looks up the address nonce of this address
        Neccesary for the transaction creation
        """
        broadcast_url = self.base_url + '?module=proxy&action=eth_getTransactionCount'
        broadcast_url += '&address=%s' % address
        broadcast_url += '&tag=pending' # Valid tags are 'earliest', 'latest', and 'pending', the last of which includes both pending and committed transactions.
        if self.api_token:
            broadcast_url += '&apikey=%s' % self.api_token
        response = self.send_request('GET', broadcast_url)
        if int(response.status_code) == 200:
            if response.json().get('message', None) == 'NOTOK':
                raise BroadcastError(response.json().get('result', None))
            nonce = int(response.json().get('result', None), 0)
            logging.info('Nonce check went correct: %s', response.json())
            return nonce
        else:
            logging.info('response error checking nonce')
        raise BroadcastError('Error checking the nonce through the Etherscan API. Error msg: %s', response.text)


class MyEtherWalletBroadcaster(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def broadcast_tx(self, tx):
        data = {
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": ["0x" + tx],
            "id": 1
        }
        response = requests.post(self.base_url, json=data, headers={'user-agent':'cert-issuer'})
        if 'error' in response.json():
            logging.error("MyEtherWallet returned an error: %s", response.json()['error'])
            raise BroadcastError(response.json()['error'])
        if int(response.status_code) == 200:
            tx_id = response.json().get('result', None)
            logging.info("Transaction ID obtained from broadcast through MyEtherWallet: %s", tx_id)
            return tx_id
        logging.error('Error broadcasting the transaction through MyEtherWallet. Error msg: %s', response.text)
        raise BroadcastError(response.text)

    def get_balance(self, address):
        """
        returns the balance in wei
        """

        data = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }
        response = requests.post(self.base_url, json=data, headers={'user-agent':'cert-issuer'})
        if int(response.status_code) == 200:
            logging.info('Balance check response: %s', response.json())
            balance = int(response.json().get('result', None), 0)
            logging.info('Balance check succeeded: %s', response.json())
            return balance
        logging.error('Error getting balance through MyEtherWallet. Error msg: %s', response.text)
        raise BroadcastError(response.text)

    def get_address_nonce(self, address):
        """
        Looks up the address nonce of this address
        Neccesary for the transaction creation
        """

        data = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [address, "pending"],
            "id": 1
        }
        response = requests.post(self.base_url, json=data, headers={'user-agent':'cert-issuer'})
        if int(response.status_code) == 200:
            # the int(res, 0) transforms the hex nonce to int
            nonce = int(response.json().get('result', None), 0)
            logging.info('Nonce check went correct: %s', response.json())
            return nonce
        else:
            logging.info('response error checking nonce')
        raise BroadcastError('Error checking the nonce through the MyEtherWallet API. Error msg: %s', response.text)
