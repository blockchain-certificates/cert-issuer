import unittest
from unittest.mock import patch, MagicMock
import time

from cert_issuer.blockchain_handlers.bitcoin.connectors import (
    BitcoinServiceProviderConnector,
    BroadcastError
)

from cert_core import Chain

# A dummy transaction class with an as_hex() method.
class DummyTx:
    def as_hex(self):
        return "deadbeef"

# Provider functions to simulate various scenarios.
def provider_valid(tx):
    # Return a valid tx id (64-character hex string)
    return "a" * 64

def provider_invalid(tx):
    # Return an invalid tx id (e.g., not 64 characters long)
    return "bad_tx"

def provider_exception(tx):
    # Simulate a provider that raises an exception.
    raise Exception("Simulated provider failure")

class TestBroadcastTxWithChain(unittest.TestCase):

    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.time.sleep', return_value=None)
    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.service_provider_methods')
    def test_valid_tx_single_provider(self, mock_service_methods, mock_sleep):
        # Test when one provider returns a valid tx id.
        mock_service_methods.return_value = [provider_valid]
        tx = DummyTx()
        result = BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, Chain.bitcoin_mainnet, bitcoind=False)
        self.assertEqual(result, "a" * 64)

    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.time.sleep', return_value=None)
    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.service_provider_methods')
    def test_valid_and_invalid_providers(self, mock_service_methods, mock_sleep):
        # Test that if the first provider returns a valid tx id,
        # then later invalid tx ids are ignored.
        # The inner loop should break on the first valid response.
        mock_service_methods.return_value = [provider_valid, provider_invalid]
        tx = DummyTx()
        result = BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, Chain.bitcoin_mainnet, bitcoind=False)
        self.assertEqual(result, "a" * 64)

    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.time.sleep', return_value=None)
    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.service_provider_methods')
    def test_all_invalid_providers(self, mock_service_methods, mock_sleep):
        # Test that if all providers return an invalid tx id,
        # the method eventually raises BroadcastError.
        mock_service_methods.return_value = [provider_invalid]
        tx = DummyTx()
        with self.assertRaises(BroadcastError):
            BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, Chain.bitcoin_mainnet, bitcoind=False)

    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.time.sleep', return_value=None)
    @patch('cert_issuer.blockchain_handlers.bitcoin.connectors.service_provider_methods')
    def test_provider_exception_then_valid(self, mock_service_methods, mock_sleep):
        # Test that if one provider raises an exception and another returns a valid tx id,
        # the valid one is used.
        mock_service_methods.return_value = [provider_exception, provider_valid]
        tx = DummyTx()
        result = BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, Chain.bitcoin_mainnet, bitcoind=False)
        self.assertEqual(result, "a" * 64)

if __name__ == '__main__':
    unittest.main()
