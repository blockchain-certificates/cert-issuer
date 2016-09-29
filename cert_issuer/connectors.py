"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations
"""
import json
import logging
import sys
import urllib.parse
from abc import abstractmethod, ABCMeta

import bitcoin.rpc
import requests
from bitcoin.core import COutPoint, CScript, CTransaction
from bitcoin.wallet import CBitcoinAddress

from cert_issuer.errors import UnrecognizedConnectorError, ConnectorError
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.models import TransactionOutput


class WalletConnector:
    """Base class for a wallet connector implementation"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_balance(self, address, confirmations):
        return 0

    @abstractmethod
    def create_temp_address(self, address):
        return None

    @abstractmethod
    def get_unspent_outputs(self, address):
        return 0

    @abstractmethod
    def pay(self, from_address, issuing_address, amount, fee):
        return

    @abstractmethod
    def archive(self, address):
        return

    @abstractmethod
    def send_to_addresses(self, storage_address,
                          temp_addresses, transfer_split_fee):
        return


class BlockchainInfoConnector(WalletConnector):

    def __init__(self, config):
        self.wallet_guid = config.wallet_guid
        self.wallet_password = config.wallet_password
        self.api_key = config.api_key

    def get_balance(self, address, confirmations):
        confirmed_url = self._make_url(
            'address_balance', {'address': address, 'confirmations': confirmations})
        confirmed_result = try_get(confirmed_url)
        confirmed_balance = confirmed_result.json().get("balance", 0)
        return confirmed_balance

    def create_temp_address(self, temp_address):
        new_address_url = self._make_url(
            'new_address', {"label": temp_address})
        confirmed_result = try_get(new_address_url)
        address = json.loads(confirmed_result.text)['address']
        return address

    def get_unspent_outputs(self, address):
        unspent_outputs = []
        # this calls a different api not accessible through localhost proxy
        unspent_url = 'https://blockchain.info/unspent?active=%s&format=json' % address
        unspent_response = try_get(unspent_url)
        r = unspent_response.json()
        for u in r['unspent_outputs']:
            tx_out = TransactionOutput(COutPoint(unhexlify(u['tx_hash']), u['tx_output_n']),
                                       CBitcoinAddress(address),
                                       CScript(unhexlify(u['script'])),
                                       int(u['value']))
            unspent_outputs.append(tx_out)
        return unspent_outputs

    def pay(self, from_address, to_address, amount, fee):
        payment_url = self._make_url('payment', {'from': from_address, 'to': to_address,
                                                 'amount': amount,
                                                 'fee': fee})
        try_get(payment_url)

    def archive(self, address):
        archive_url = self._make_url('archive_address', {'address': address})
        try_get(archive_url)

    def send_to_addresses(self, storage_address,
                          temp_addresses, transfer_split_fee):
        payload = {'from': storage_address,
                   'recipients': urllib.parse.quote_plus(json.dumps(temp_addresses)),
                   'fee': transfer_split_fee}
        sendmany_url = self._make_url('sendmany', payload)
        logging.info('calling url from send_to_addresses: %s', sendmany_url)
        try_get(sendmany_url)

    def _make_url(self, command, extras={}):
        url = 'http://localhost:3000/merchant/%s/%s?password=%s&api_code=%s' % (
            self.wallet_guid, command, self.wallet_password, self.api_key)
        if len(extras) > 0:
            addon = ''
            for name in list(extras.keys()):
                addon = '%s&%s=%s' % (addon, name, extras[name])
            url += addon
        return url


class BitcoindConnector(WalletConnector):

    def __init__(self, config):
        bitcoin.rpc.Proxy()
        self.proxy = bitcoin.rpc.Proxy()

    def get_balance(self, address, confirmations):
        address_balance = 0
        unspent = self.proxy.listunspent(addrs=[address])
        for u in unspent:
            address_balance = address_balance + u.get('amount', 0)
        return address_balance

    def get_unspent_outputs(self, address):
        unspent_outputs = self.proxy.listunspent(addrs=[address])
        unspent_outputs_converted = [TransactionOutput(unspent['outpoint'], unspent['address'],
                                                       unspent['scriptPubKey'], int(unspent['amount']))
                                     for unspent in unspent_outputs]
        return unspent_outputs_converted

    def pay(self, from_address, issuing_address, amount, fee):
        self.proxy.sendtoaddress(issuing_address, amount)

    # These methods are used for temporary addresses, and they are not yet
    # supported
    def create_temp_address(self, address):
        address = self.proxy.getnewaddress()
        return address

    def archive(self, address):
        # TODO
        #raise NotImplementedError('archive is not yet supported')
        return

    def send_to_addresses(self, storage_address,
                          temp_addresses, transfer_split_fee):
        for address in temp_addresses:
            self.proxy.sendtoaddress(address, transfer_split_fee)
        #raise NotImplementedError('send_to_addresses is not yet supported')


def insight_broadcast(hextx):
    r = requests.post("https://insight.bitpay.com/api/tx/send",
                      json={"rawtx": hextx})
    if int(r.status_code) != 200:
        sys.stderr.write(
            "Error broadcasting the transaction through the Insight API. Error msg: %s" % r.text)
        sys.exit(1)
    else:
        txid = r.json().get('txid', None)
    return txid


def blockr_broadcast(hextx):
    r = requests.post('http://btc.blockr.io/api/v1/tx/push',
                      json={'hex': hextx})
    if int(r.status_code) != 200:
        sys.stderr.write(
            'Error broadcasting the transaction through the blockr.io API. Error msg: %s' % r.text)
        sys.exit(1)
    else:
        txid = r.json().get('data', None)
    return txid


def noop_broadcast(hextx):
    logging.warning(
        'app is configured not to broadcast, so no txid will be created for hextx=%s', hextx)
    return None


def bitcoind_broadcast(hextx):
    tx = CTransaction.deserialize(unhexlify(hextx))
    txid = bitcoin.rpc.Proxy().sendrawtransaction(tx)
    # reverse endianness for bitcoind
    return hexlify(bytearray(txid)[::-1])


def create_wallet_connector(config):
    wallet_connector_type = config.wallet_connector_type
    if wallet_connector_type == 'blockchain.info':
        connector = BlockchainInfoConnector(config)
    elif wallet_connector_type == 'bitcoind':
        connector = BitcoindConnector(config)
    else:
        error_message = 'unrecognized wallet connector: {}'.format(
            wallet_connector_type)
        raise UnrecognizedConnectorError(error_message)
    return connector


def create_broadcast_function(config):
    broadcaster_type = config.broadcaster_type
    if broadcaster_type == 'btc.blockr.io':
        return blockr_broadcast
    elif broadcaster_type == 'insight.bitpay.com':
        return insight_broadcast
    elif broadcaster_type == 'bitcoind':
        return bitcoind_broadcast
    elif broadcaster_type == 'noop':
        return noop_broadcast
    else:
        error_message = 'unrecognized broadcaster: {}'.format(broadcaster_type)
        raise UnrecognizedConnectorError(error_message)


def try_get(url):
    """throw error if call fails"""
    r = requests.get(url)
    if int(r.status_code) != 200:
        error_message = 'Error! status_code={}, error={}'.format(
            r.status_code, r.json()['error'])
        logging.error(error_message)
        raise ConnectorError(error_message)
    return r
