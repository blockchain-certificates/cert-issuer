"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations
# TODO: merge with pycoin providers
"""
import io
import logging

import bitcoin.rpc
import requests
from bitcoin.core import CTransaction
from pycoin.services import providers
from pycoin.services import spendables_for_address
from pycoin.services.providers import BlockrioProvider, InsightProvider
from pycoin.services.providers import get_default_providers_for_netcode
from pycoin.services.providers import service_provider_methods
from pycoin.tx import Spendable

from cert_issuer.helpers import unhexlify
from cert_issuer.errors import ConnectorError
from cert_issuer.helpers import hexlify

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

from pycoin.serialize import b2h

from cert_issuer import config

netcode = config.get_config().netcode


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
            txid = response.json().get('txid', None)
            return txid
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
            txid = response.json().get('data', None)
            return txid
        logging.error('Error broadcasting the transaction through the Blockr.IO API. Error msg: %s', response.text)
        raise Exception(response.text)


class BitcoindConnector(object):
    def __init__(self, netcode):
        self.netcode = netcode
        bitcoin.rpc.Proxy()
        self.proxy = bitcoin.rpc.Proxy()

    def broadcast_tx(self, tx):
        as_hex = tx.as_hex()
        tx = CTransaction.deserialize(unhexlify(as_hex))
        txid = bitcoin.rpc.Proxy().sendrawtransaction(tx)
        # reverse endianness for bitcoind
        return hexlify(bytearray(txid)[::-1])

    def spendables_for_address(self, address):
        unspents = self.proxy.listunspent(addrs=[address])
        spendables = []
        for unspent in unspents:
            coin_value = unspent.get('amount', 0)
            op = unspent.get('outpoint')
            script = unspent.get('scriptPubKey')
            previous_hash = op.hash
            previous_index = op.n
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables

    def pay(self, from_address, issuing_address, amount, fee):
        self.proxy.sendtoaddress(issuing_address, amount)


def noop_broadcast(hextx):
    logging.warning(
        'app is configured not to broadcast, so no txid will be created for hextx=%s', hextx)
    return None


def get_unspent_outputs(address):
    spendables = spendables_for_address(bitcoin_address=address, netcode=netcode)
    if spendables:
        return sorted(spendables, key=lambda x: hash(x.coin_value))
    return None


def get_balance(address):
    spendables = get_unspent_outputs(address)
    balance = sum(s.coin_value for s in spendables)
    return balance


def broadcast_tx(tx):
    """
    Broadcast the transaction through the configured set of providers
    """
    last_exception = None
    for m in service_provider_methods('broadcast_tx', get_default_providers_for_netcode(netcode)):
        try:
            txid = m(tx)
            if txid:
                return txid
        except Exception as e:
            logging.warning('Caught exception trying provider %s. Trying another. Exception=%s', str(m), e)
            last_exception = e
            pass
    logging.error('Failed broadcasting through all providers')
    raise last_exception


def pay(from_address, to_address, amount, fee):
    last_exception = None
    for m in service_provider_methods('pay', get_default_providers_for_netcode(netcode)):
        try:
            m(from_address, to_address, amount, fee, netcode)
            return
        except Exception as e:
            logging.warning('Caught exception trying provider %s. Trying another. Exception=%s', str(m), e)
            last_exception = e
            pass
    logging.error('Failed paying through all providers')
    raise last_exception


PYCOIN_BTC_PROVIDERS = "blockchain.info blockexplorer.com blockr.io blockcypher.com chain.so"


def init_connectors():
    provider_list = providers.providers_for_config_string(PYCOIN_BTC_PROVIDERS, 'BTC')

    blockio_index = -1
    for idx, val in enumerate(provider_list):
        print(idx, val)
        if isinstance(val, BlockrioProvider):
            blockio_index = idx
        elif isinstance(val, InsightProvider):
            insight_index = idx

    if blockio_index > -1:
        provider_list[blockio_index] = BlockrBroadcaster('BTC')
    else:
        provider_list.append(BlockrBroadcaster('BTC'))

    provider_list.append(InsightBroadcaster('https://insight.bitpay.com/', 'BTC'))
    provider_list.append(BitcoindConnector('BTC'))

    providers.set_default_providers_for_netcode('BTC', provider_list)
    result = get_default_providers_for_netcode('BTC')

    testnet_list = []
    testnet_list.append(BitcoindConnector('XTN'))
    providers.set_default_providers_for_netcode('XTN', testnet_list)
    result = get_default_providers_for_netcode('XTN')
    print(result)


init_connectors()
