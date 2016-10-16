"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations.

"""
import io
import logging

import bitcoin.rpc
import requests
from bitcoin.core import CTransaction
from pycoin.serialize import b2h
from pycoin.services import providers
from pycoin.services import spendables_for_address
from pycoin.services.providers import BlockrioProvider, InsightProvider
from pycoin.services.providers import get_default_providers_for_netcode
from pycoin.services.providers import service_provider_methods
from pycoin.tx import Spendable

from cert_issuer import config
from cert_issuer.errors import ConnectorError
from cert_issuer.helpers import hexlify
from cert_issuer.helpers import unhexlify

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode


CONFIG_NETCODE = config.get_config().netcode

def try_get(url):
    """throw error if call fails"""
    response = requests.get(url)
    if int(response.status_code) != 200:
        error_message = 'Error! status_code={}, error={}'.format(
            response.status_code, response.json()['error'])
        logging.error(error_message)
        raise ConnectorError(error_message)
    return response


def to_hex(transaction):
    s = io.BytesIO()
    transaction.stream(s)
    tx_as_hex = b2h(s.getvalue())
    return tx_as_hex


class LocalBlockchainInfoConnector(object):
    def __init__(self, config):
        self.wallet_guid = config.wallet_guid
        self.wallet_password = config.wallet_password
        self.api_key = config.api_key

    def pay(self, from_address, to_address, amount, fee):
        payment_url = self._make_url('payment', {'from': from_address, 'to': to_address,
                                                 'amount': amount,
                                                 'fee': fee})
        try_get(payment_url)
        try_get(payment_url)

    def _make_url(self, command, extras={}):
        url = 'http://localhost:3000/merchant/%s/%s?password=%s&api_code=%s' % (
            self.wallet_guid, command, self.wallet_password, self.api_key)
        if len(extras) > 0:
            addon = ''
            for name in list(extras.keys()):
                addon = '%s&%s=%s' % (addon, name, extras[name])
            url += addon
        return url


class InsightBroadcaster(InsightProvider):
    def __init__(self, base_url, netcode=None):
        InsightProvider.__init__(self, base_url, netcode)
        self.netcode = netcode

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/api/tx/send'
        response = requests.post(broadcast_url, json={'rawtx': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('txid', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the Insight API. Error msg: %s', response.text)
        raise Exception(response.text)


class BlockrBroadcaster(BlockrioProvider):
    def __init__(self, netcode):
        BlockrioProvider.__init__(self, netcode)

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        URL = self.url + '/tx/push'
        response = requests.post(URL, json={'hex': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('data', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the Blockr.IO API. Error msg: %s', response.text)
        raise Exception(response.text)


class BitcoindConnector(object):

    def __init__(self, netcode):
        self.netcode = netcode

    def broadcast_tx(self, transaction):
        as_hex = transaction.as_hex()
        transaction = CTransaction.deserialize(unhexlify(as_hex))
        tx_id = bitcoin.rpc.Proxy().sendrawtransaction(transaction)
        # reverse endianness for bitcoind
        return hexlify(bytearray(tx_id)[::-1])

    def spendables_for_address(self, address):
        """
        Converts to pycoin Spendable type
        :param address:
        :return: list of Spendables
        """
        unspent_outputs = bitcoin.rpc.Proxy().listunspent(addrs=[address])
        spendables = []
        for unspent in unspent_outputs:
            coin_value = unspent.get('amount', 0)
            outpoint = unspent.get('outpoint')
            script = unspent.get('scriptPubKey')
            previous_hash = outpoint.hash
            previous_index = outpoint.n
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables

    def pay(self, from_address, issuing_address, amount, fee):
        self.proxy.sendtoaddress(issuing_address, amount)


def get_unspent_outputs(address, netcode=CONFIG_NETCODE):
    """
    Get unspent outputs at the address
    :param address:
    :param netcode:
    :return:
    """
    spendables = spendables_for_address(bitcoin_address=address, netcode=netcode)
    if spendables:
        return sorted(spendables, key=lambda x: hash(x.coin_value))
    return None


def get_balance(address, netcode=CONFIG_NETCODE):
    """
    Get balance available to spend at the address
    :param address:
    :param netcode:
    :return:
    """
    spendables = get_unspent_outputs(address, netcode)
    balance = sum(s.coin_value for s in spendables)
    return balance


def broadcast_tx(tx, netcode=CONFIG_NETCODE):
    """
    Broadcast the transaction through the configured set of providers

    :param tx:
    :param netcode:
    :return:
    """
    last_exception = None
    for method_provider in service_provider_methods('broadcast_tx', get_default_providers_for_netcode(netcode)):
        try:
            tx_id = method_provider(tx)
            if tx_id:
                return tx_id
        except Exception as e:
            logging.warning('Caught exception trying provider %s. Trying another. Exception=%s', str(method_provider), e)
            last_exception = e
    logging.error('Failed broadcasting through all providers')
    raise last_exception


def pay(from_address, to_address, amount, fee):
    last_exception = None
    for method_provider in service_provider_methods('pay', get_default_providers_for_netcode(CONFIG_NETCODE)):
        try:
            method_provider(from_address, to_address, amount, fee, CONFIG_NETCODE)
            return
        except Exception as e:
            logging.warning('Caught exception trying provider %s. Trying another. Exception=%s', str(method_provider), e)
            last_exception = e
    logging.error('Failed paying through all providers')
    raise last_exception


PYCOIN_BTC_PROVIDERS = "blockchain.info blockexplorer.com blockr.io blockcypher.com chain.so"


def init_connectors(conf):
    """
    Initialize broadcasting and payment connectors. This allows fallback and confirmation across different chains
    :param conf:
    :return:
    """

    # configure mainnet providers
    provider_list = providers.providers_for_config_string(PYCOIN_BTC_PROVIDERS, 'BTC')

    blockio_index = -1
    for idx, val in enumerate(provider_list):
        print(idx, val)
        if isinstance(val, BlockrioProvider):
            blockio_index = idx

    if blockio_index > -1:
        provider_list[blockio_index] = BlockrBroadcaster('BTC')
    else:
        provider_list.append(BlockrBroadcaster('BTC'))

    provider_list.append(InsightBroadcaster('https://insight.bitpay.com/', 'BTC'))

    # initialize payment connectors based on config file
    if conf.wallet_connector_type == 'blockchain.info':
        provider_list.append(LocalBlockchainInfoConnector(conf))
    else:
        provider_list.append(BitcoindConnector('BTC'))

    providers.set_default_providers_for_netcode('BTC', provider_list)

    # initialize testnet providers
    testnet_list = []
    testnet_list.append(BitcoindConnector('XTN'))
    providers.set_default_providers_for_netcode('XTN', testnet_list)

init_connectors(config.get_config())