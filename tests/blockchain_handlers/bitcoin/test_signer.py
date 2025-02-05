import unittest
from unittest.mock import Mock, patch
import json

from cert_issuer.blockchain_handlers.bitcoin.signer import BitcoinSigner, verify_message, verify_signature
from cert_issuer.errors import UnableToSignTxError


class TestBitcoinSigner(unittest.TestCase):
    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.network_for_netcode')
    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.to_pycoin_chain', return_value='dummy_netcode')
    def test_sign_transaction_success(self, mock_to_pycoin, mock_network_for_netcode):
        # Set up the dummy network to be returned by network_for_netcode
        dummy_network = DummyNetwork()
        mock_network_for_netcode.return_value = dummy_network

        signer = BitcoinSigner(bitcoin_chain='testchain')
        dummy_tx = DummyTransaction()

        # Execute sign_transaction which should mark all inputs as signed.
        signed_tx = signer.sign_transaction('dummy_wif', dummy_tx)

        # Assert that every input now has a non-empty script.
        for tx_in in signed_tx.txs_in:
            self.assertTrue(tx_in.script)

    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.network_for_netcode')
    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.to_pycoin_chain', return_value='dummy_netcode')
    def test_sign_transaction_failure(self, mock_to_pycoin, mock_network_for_netcode):
        dummy_network = DummyNetwork()
        mock_network_for_netcode.return_value = dummy_network

        signer = BitcoinSigner(bitcoin_chain='testchain')
        dummy_tx = DummyTransaction()

        # Simulate a failure: sign only one input and leave the other unsigned.
        def failing_sign(lookup):
            dummy_tx.txs_in[0].script = b'signed'
            # Leave the second input unsigned
            return dummy_tx

        dummy_tx.sign = failing_sign

        with self.assertRaises(UnableToSignTxError):
            signer.sign_transaction('dummy_wif', dummy_tx)

    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.VerifyMessage', return_value=True)
    def test_verify_message(self, mock_verify_message):
        result = verify_message('dummy_address', 'test message', 'dummy_signature')
        self.assertTrue(result)

    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.open', create=True)
    @patch('cert_issuer.blockchain_handlers.bitcoin.signer.verify_message', return_value=True)
    def test_verify_signature(self, mock_verify_message, mock_open):
        # Set up the dummy certificate content as JSON.
        dummy_cert = json.dumps({"signature": "dummy_signature"})
        mock_file = Mock()
        mock_file.read.return_value = dummy_cert
        mock_open.return_value.__enter__.return_value = mock_file

        # Calling verify_signature should pass without raising an exception.
        try:
            verify_signature('uid123', 'dummy_file', 'dummy_address')
        except Exception as e:
            self.fail(f"verify_signature raised an exception unexpectedly: {e}")


class DummyKey:
    def secret_exponent(self):
        return 12345

class DummyNetwork:
    def __init__(self):
        self.generator = (123456, 654321)
        self.parse = Mock()
        self.parse.wif.return_value = DummyKey()

class DummyInput:
    def __init__(self):
        # start with an empty script to simulate an unsigned input
        self.script = b''

class DummyTransaction:
    def __init__(self):
        # Two inputs for demonstration
        self.txs_in = [DummyInput(), DummyInput()]

    def sign(self, lookup):
        # For a successful sign, mark every input as signed.
        for inp in self.txs_in:
            inp.script = b'signed'
        return self

    def as_hex(self):
        return 'deadbeef'

if __name__ == '__main__':
    unittest.main()
