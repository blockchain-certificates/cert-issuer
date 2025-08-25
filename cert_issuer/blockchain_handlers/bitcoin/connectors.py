"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations.
"""
import io
import logging
import time
from abc import abstractmethod

import bitcoin.rpc
import requests
from bitcoin.core import CTransaction
from cert_core import Chain
from pycoin.coins.bitcoin.Tx import Tx
from pycoin.encoding.hexbytes import b2h, b2h_rev, h2b, h2b_rev
from pycoin.services import providers
from pycoin.services.chain_so import ChainSoProvider
from pycoin.services.insight import InsightProvider
from pycoin.services.providers import service_provider_methods
from pycoin.coins.bitcoin.Spendable import Spendable

import cert_issuer.config
from cert_issuer import helpers
from cert_issuer.errors import BroadcastError

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

BROADCAST_RETRY_INTERVAL = 30
MAX_BROADCAST_ATTEMPTS = 3


def to_hex(transaction):
    s = io.BytesIO()
    transaction.stream(s)
    tx_as_hex = b2h(s.getvalue())
    return tx_as_hex

class BlockcypherProvider(object):
    """
    Note that this needs an API token
    """

    def __init__(self, base_url, api_token=None):
        self.base_url = base_url
        self.api_token = api_token
        
        if self.api_token:
            logging.info('Blockcypher at ' + base_url + ' is configured with an API token')

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/txs/push'
        if self.api_token:
            broadcast_url += '?token=' + self.api_token
        response = requests.post(broadcast_url, json={'tx': hextx})
        if int(response.status_code) == 201:
            tx_id = response.json().get('tx', None)
            tx_hash = tx_id.get('hash', None)
            return tx_hash
        logging.error('Error broadcasting the transaction through the Blockcypher API. Error msg: %s', response.text)
        raise BroadcastError(response.text)

    def spendables_for_address(self, address):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        logging.info('trying to get spendables from blockcypher')
        spendables = []
        url_append = '?unspentOnly=true&includeScript=true'
        if self.api_token:
            url_append += '&token=' + self.api_token
        url = self.base_url + '/addrs/' + address + url_append
        response = requests.get(url)
        if int(response.status_code) == 200:
            for txn in response.json().get('txrefs', []):
                coin_value = txn.get('value')
                script = h2b(txn.get('script'))
                previous_hash = h2b_rev(txn.get('tx_hash'))
                previous_index = txn.get('tx_output_n')
                spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables

class BlockstreamProvider(object):
    def __init__(self, base_url_free, base_url_enterprise, client_id=None, client_secret=None):
        if base_url_enterprise and client_id and client_secret:
            logging.info('Blockstream provider for ' + base_url_enterprise + ' configured for enterprise tier')
            self.base_url = base_url_enterprise
        elif base_url_enterprise:
            logging.warning('Blockstream enterprise base URL is set, but CLIENT_ID and/or CLIENT_SECRET are missing. Defaulting to free tier.')
            self.base_url = base_url_free
            logging.info('Blockstream provider for ' + base_url_free + ' configured for free tier')
        else:
            self.base_url = base_url_free
            logging.info('Blockstream provider for ' + base_url_free + ' configured for free tier')
        
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        if not self.client_id or not self.client_secret:
            logging.warning('Client ID or Client Secret is not set.')
            return None
        token_url = 'https://login.blockstream.com/realms/blockstream-public/protocol/openid-connect/token'
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'openid'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(token_url, data=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            
            # Assuming the token is returned in JSON format under key 'access_token'
            access_token = response.json().get('access_token')
            return access_token
        except requests.exceptions.RequestException as e:
            logging.error('Error obtaining access token: %s', str(e))
            return None

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/tx'
        
        access_token = self.get_access_token()

        if access_token:
            logging.info('Using enterprise-tier Blockstream to broadcast transaction')
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
        else:
            logging.info('Using free-tier Blockstream to broadcast transaction.')
            headers = {}
        
        response = requests.post(broadcast_url, data=hextx, headers=headers)
        
        if int(response.status_code) == 200:
            tx_id = response.text
            return tx_id
        logging.error('Error broadcasting the transaction through the Blockstream API. Error msg: %s', response.text)
        raise BroadcastError(response.text)
    
    def spendables_for_address(self, address):
        logging.info('Trying to get spendables from Blockstream')
        spendables = []

        # Default headers
        headers = {}

        # Determine if we should use authenticated access
        access_token = None
        if self.client_id and self.client_secret:
            access_token = self.get_access_token()
            if access_token:
                logging.info('Using enterprise-tier Blockstream to get spendables.')
                headers['Authorization'] = f'Bearer {access_token}'
            else:
                logging.warning('Failed to get access token; falling back to free-tier Blockstream for spendables.')
        else:
            logging.info('Using free-tier Blockstream to get spendables.')

        # Step 1: Get UTXOs for the address
        url = f"{self.base_url}/address/{address}/utxo"
        response = requests.get(url, headers=headers, timeout=(30,60))

        if int(response.status_code) == 200:
            utxos = response.json()
            for utxo in utxos:
                coin_value = utxo.get('value')
                previous_hash = h2b_rev(utxo.get('txid'))
                previous_index = utxo.get('vout')

                # Step 2: Get full transaction to retrieve scriptPubKey
                tx_url = f"{self.base_url}/tx/{utxo['txid']}/hex"
                tx_response = requests.get(tx_url, headers=headers, timeout=(30, 60))

                if int(tx_response.status_code) == 200:
                    tx_hex = tx_response.text
                    tx = Tx.from_hex(tx_hex)
                    script = tx.txs_out[utxo['vout']].script

                    spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
                else:
                    logging.error(f"Error fetching full transaction {utxo['txid']} from Blockstream.")
        else:
            logging.error(f"Error fetching UTXOs for address {address}: {response.text}")

        return spendables


class BitcoindConnector(object):
    def __init__(self, netcode):
        self.netcode = netcode

    def broadcast_tx(self, transaction):
        as_hex = transaction.as_hex()
        transaction = CTransaction.deserialize(h2b(as_hex))
        tx_id = bitcoin.rpc.Proxy().sendrawtransaction(transaction)
        # reverse endianness for bitcoind
        return b2h_rev(tx_id)

    def spendables_for_address(self, address):
        """
        Converts to pycoin Spendable type
        :param address:
        :return: list of Spendables
        """
        unspent_outputs = bitcoin.rpc.Proxy().listunspent(addrs=[address])
        logging.debug('spendables_for_address %s', address)

        spendables = []
        for unspent in unspent_outputs:
            coin_value = unspent.get('amount', 0)
            outpoint = unspent.get('outpoint')
            script = unspent.get('scriptPubKey')
            previous_hash = outpoint.hash
            previous_index = outpoint.n
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables


class ServiceProviderConnector(object):
    @abstractmethod
    def get_balance(self, address):
        pass

    def broadcast_tx(self, tx):
        pass


class MockServiceProviderConnector(ServiceProviderConnector):
    def get_balance(self, address):
        pass

    def broadcast_tx(self, tx):
        pass


class BitcoinServiceProviderConnector(ServiceProviderConnector):
    def __init__(self, bitcoin_chain, bitcoind=False):
        self.bitcoin_chain = bitcoin_chain
        self.bitcoind = bitcoind

    def spendables_for_address(self, bitcoin_address):
        for m in service_provider_methods('spendables_for_address',
                                          get_providers_for_chain(self.bitcoin_chain, self.bitcoind)):
            try:
                logging.debug('m=%s', m)
                spendables = m(bitcoin_address)
                return spendables
            except Exception as e:
                logging.warning(e)
                pass
        return []

    def get_unspent_outputs(self, address):
        """
        Get unspent outputs at the address
        :param address:
        :return:
        """
        logging.debug('get_unspent_outputs for address=%s', address)
        spendables = self.spendables_for_address(bitcoin_address=address)
        if spendables:
            return sorted(spendables, key=lambda x: hash(x.coin_value))
        return None

    def get_balance(self, address):
        """
        Get balance available to spend at the address
        :param address:
        :return:
        """
        spendables = self.get_unspent_outputs(address)
        if not spendables:
            logging.warning('address %s has a balance of 0', address)
            return 0

        balance = sum(s.coin_value for s in spendables)
        return balance

    def broadcast_tx(self, tx):
        """
        Broadcast the transaction through the configured set of providers

        :param tx:
        :return:
        """
        return BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, self.bitcoin_chain, self.bitcoind)

    @staticmethod
    def broadcast_tx_with_chain(tx, bitcoin_chain, bitcoind=False):
        """
        Broadcast the transaction through the configured set of providers

        :param tx:
        :param bitcoin_chain:
        :return:
        """
        last_exception = None
        final_tx_id = None

        # Unlike other providers, we want to broadcast to all available apis
        for attempt_number in range(0, MAX_BROADCAST_ATTEMPTS):
            for method_provider in service_provider_methods('broadcast_tx',
                                                            get_providers_for_chain(bitcoin_chain, bitcoind)):
                try:
                    tx_id = method_provider(tx)
                    if tx_id:
                        # We have to check to make sure that the tx_id at least kind of looks like a sha256 hash string.
                        if len(tx_id) != 64:
                            if final_tx_id:
                                # If we already found a final_tx_id, then some other provider got it, but we should
                                # log the bad provider.
                                logging.error("Ignoring invalid tx_id %s from provider %s since valid" +
                                    "tx_id %s already exists (another provider already sent the transaction).  " +
                                    "The current provider might be broken!  Bad txid!",
                                    tx_id, str(method_provider), final_tx_id)
                                continue
                            else:
                                logging.error("Provider %s returned an invalid tx_id: %s.  " +
                                    "Aborting further retries.  Bad txid!",
                                    str(method_provider), tx_id)
                                raise BroadcastError("Invalid tx_id received: " + tx_id)
                        
                        logging.info('Broadcasting succeeded with method_provider=%s, txid=%s', str(method_provider),
                                     tx_id)
                        if final_tx_id and final_tx_id != tx_id:
                            logging.error(
                                'This should never happen; fail and investigate if it does. Got conflicting tx_ids=%s and %s. Hextx=%s',
                                final_tx_id, tx_id, tx.as_hex())
                            raise Exception('Got conflicting tx_ids.')
                        final_tx_id = tx_id
                except Exception as e:
                    logging.warning('Caught exception trying provider %s. Trying another. Exception=%s',
                                    str(method_provider), e)
                    last_exception = e
            # At least 1 provider succeeded, so return
            if final_tx_id:
                return final_tx_id
            else:
                logging.warning('Broadcasting failed. Waiting before retrying. This is attempt number %d',
                                attempt_number)
                time.sleep(BROADCAST_RETRY_INTERVAL)
        logging.error('Failed broadcasting through all providers')
        logging.error(last_exception, exc_info=True)
        raise BroadcastError(last_exception)


# configure api tokens
config = cert_issuer.config.CONFIG
blockcypher_token = None if config is None else config.blockcypher_api_token
blockstream_client_id = None if config is None else config.blockstream_client_id
blockstream_client_secret = None if config is None else config.blockstream_client_secret

PYCOIN_BTC_PROVIDERS = "chain.so"  # blockchain.info blockcypher.com
PYCOIN_XTN_PROVIDERS = ""  # chain.so

# initialize connectors
connectors = {}

# configure mainnet providers
provider_list = providers.providers_for_config_string(
    PYCOIN_BTC_PROVIDERS,
    helpers.to_pycoin_chain(Chain.bitcoin_mainnet)
)
provider_list.append(
    BlockstreamProvider(
        'https://blockstream.info/api',
        'https://enterprise.blockstream.info/api',
        blockstream_client_id,
        blockstream_client_secret
    )
)
provider_list.append(
    BlockcypherProvider(
        'https://api.blockcypher.com/v1/btc/main',
        blockcypher_token
    )
)
provider_list.append(
    InsightProvider(
        netcode=helpers.to_pycoin_chain(Chain.bitcoin_mainnet)
    )
)
#provider_list.append(
#    ChainSoProvider(
#        netcode=helpers.to_pycoin_chain(Chain.bitcoin_mainnet)
#    )
#)

connectors[Chain.bitcoin_mainnet] = provider_list

# configure testnet providers
xtn_provider_list = providers.providers_for_config_string(
    PYCOIN_XTN_PROVIDERS,
    helpers.to_pycoin_chain(Chain.bitcoin_testnet)
)
#xtn_provider_list.append(
#    ChainSoProvider(
#        netcode=helpers.to_pycoin_chain(Chain.bitcoin_testnet)
#    )
#)

xtn_provider_list.append(
    BlockstreamProvider(
        'https://blockstream.info/testnet/api',
        'https://enterprise.blockstream.info/testnet/api',
        blockstream_client_id,
        blockstream_client_secret
    )
)

xtn_provider_list.append(
    BlockcypherProvider(
        'https://api.blockcypher.com/v1/btc/test3',
        blockcypher_token
    )
)

connectors[Chain.bitcoin_testnet] = xtn_provider_list

def get_providers_for_chain(chain, bitcoind=False):
    if bitcoind:
        return [BitcoindConnector(helpers.to_pycoin_chain(chain))]
    else:
        return connectors[chain]
