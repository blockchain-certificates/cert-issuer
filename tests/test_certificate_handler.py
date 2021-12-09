import unittest

import mock
import json
import io
from pycoin.serialize import b2h
from mock import patch, mock_open

from cert_issuer.certificate_handlers import CertificateWebV3Handler, CertificateV3Handler, CertificateBatchHandler, CertificateHandler, CertificateBatchWebHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer import helpers
from cert_core import Chain
from mock import ANY

class TestCertificateHandler(unittest.TestCase):
    def _proof_helper(self, chain):
        proof = {
                    'type': 'MerkleProof2019',
                    'created': ANY,
                    'proofValue': ANY,
                    'proofPurpose': 'assertionMethod',
                    'verificationMethod': ANY
                }
        return proof

    def _helper_mock_call(self, *args):
        helper_mock = mock.MagicMock()
        helper_mock.__len__.return_value = self.directory_count

        assert args == (
            '/unsigned_certificates_dir',
            '/signed_certificates_dir',
            '/blockchain_certificates_dir',
            '/work_dir')
        
        return helper_mock

    def _get_certificate_batch_web_handler(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        handler = CertificateBatchWebHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator(),
                config=config)

        return handler, certificates_to_issue

    def _get_certificate_batch_handler(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        handler = CertificateBatchHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator(),
                config=config)

        return handler, certificates_to_issue

    def test_batch_handler_web_prepare_batch(self):
        web_handler, certificates_to_issue = self._get_certificate_batch_web_handler()

        web_handler.set_certificates_in_batch(certificates_to_issue)
        result = web_handler.prepare_batch()
        self.assertEqual(
                b2h(result), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')

    def test_batch_handler_prepare_batch(self):
        certificate_batch_handler, certificates_to_issue = self._get_certificate_batch_handler()

        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()
        self.assertEqual(
                b2h(result), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')

    def test_batch_web_handler_finish_batch(self):
        certificate_batch_handler, certificates_to_issue = self._get_certificate_batch_web_handler()

        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()

        chain = Chain.bitcoin_mainnet
        proof = self._proof_helper(chain)

        with patch.object(DummyCertificateHandler, 'add_proof', return_value= {"cert": "cert"} ) as mock_method:
            result = certificate_batch_handler.finish_batch(
                        '5604f0c442922b5db54b69f8f363b3eac67835d36a006b98e8727f83b6a830c0', chain
                        )
        self.assertEqual(certificate_batch_handler.proof, [{'cert': 'cert'}, {'cert': 'cert'}, {'cert': 'cert'}])
        mock_method.assert_any_call(ANY, proof)

    def test_batch_handler_finish_batch(self):
        certificate_batch_handler, certificates_to_issue = self._get_certificate_batch_handler()

        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()

        chain = Chain.bitcoin_mainnet
        proof = self._proof_helper(chain)

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        with patch.object(DummyCertificateHandler, 'add_proof') as mock_method:
            result = certificate_batch_handler.finish_batch(
                    '5604f0c442922b5db54b69f8f363b3eac67835d36a006b98e8727f83b6a830c0', chain
                    )

        mock_method.assert_any_call(ANY, proof)

    def test_pre_batch_actions(self):
        self.directory_count = 1

        config = mock.Mock()
        config.unsigned_certificates_dir = '/unsigned_certificates_dir'
        config.signed_certificates_dir = '/signed_certificates_dir'
        config.blockchain_certificates_dir = '/blockchain_certificates_dir'
        config.work_dir = '/work_dir'

        helpers.prepare_issuance_batch = mock.MagicMock()

        helpers.prepare_issuance_batch.side_effect = self._helper_mock_call

        with patch.object(CertificateBatchHandler, 'set_certificates_in_batch') as mock_method:
            certificate_batch_handler, _ = self._get_certificate_batch_handler()
            certificate_batch_handler.pre_batch_actions(config)

        assert mock_method.called

    def test_pre_batch_actions_empty_directories(self):
        self.directory_count = 0

        config = mock.Mock()
        config.unsigned_certificates_dir = '/unsigned_certificates_dir'
        config.signed_certificates_dir = '/signed_certificates_dir'
        config.blockchain_certificates_dir = '/blockchain_certificates_dir'
        config.work_dir = '/work_dir'

        helpers.prepare_issuance_batch = mock.MagicMock()

        helpers.prepare_issuance_batch.side_effect = self._helper_mock_call

        with patch.object(CertificateBatchHandler, 'set_certificates_in_batch') as mock_method:
            certificate_batch_handler, _ = self._get_certificate_batch_handler()
            certificate_batch_handler.pre_batch_actions(config)

        assert not mock_method.called

    @mock.patch("builtins.open", create=True)
    def test_add_proof(self,mock_open):
        handler = CertificateV3Handler()

        cert_to_issue = {'kek':'kek'}
        proof = {'a': 'merkel'}
        file_call = 'call().__enter__().write(\'{"kek": "kek", "proof": {"a": "merkel"}}\')'

        chain = mock.Mock()
        metadata = mock.Mock()
        metadata.blockchain_cert_file_name = 'file_path.nfo'

        with patch.object(
        CertificateV3Handler, '_get_certificate_to_issue', return_value=cert_to_issue) as mock_method:
                handler.add_proof(metadata, proof)

        mock_open.assert_any_call('file_path.nfo','w')
        calls = mock_open.mock_calls
        call_strings = map(str, calls)
        assert file_call in call_strings

    def test_web_add_proof(self):
        handler = CertificateWebV3Handler()
        proof = {'a': 'merkel'}
        chain = mock.Mock()
        certificate_json = {'kek': 'kek'}

        return_cert = handler.add_proof(certificate_json, proof)
        self.assertEqual(return_cert, {'kek':'kek', 'signature': {'a': 'merkel'}})

class DummyCertificateHandler(CertificateHandler):
    def __init__(self):
        self.config = mock.Mock()
        self.config.issuing_address = "http://example.com"
        self.counter = 0

    def _get_certificate_to_issue (self, certificate_metadata):
        pass

    def validate_certificate(self, certificate_metadata):
        pass

    def sign_certificate(self, signer, certificate_metadata):
        pass

    def get_byte_array_to_issue(self, certificate_metadata):
        self.counter += 1
        return str(self.counter).encode('utf-8')

    def add_proof(self, certificate_metadata, merkle_proof):
        pass


if __name__ == '__main__':
    unittest.main()
