import unittest

import mock
import builtins
from pycoin.encoding.hexbytes import b2h
from mock import patch

from cert_issuer.certificate_handlers import CertificateWebV3Handler, CertificateV3Handler, CertificateBatchHandler, CertificateHandler, CertificateBatchWebHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer import helpers
from cert_core import Chain
from mock import ANY

class TestCertificateHandler(unittest.TestCase):
    def _proof_helper(self):
        proof = {
            'type': 'DataIntegrityProof',
            'cryptosuite': 'merkle-proof-2019',
            'id': ANY,
            'created': ANY,
            'proofValue': self._proof_value_helper().decode('utf8'),
            'proofPurpose': 'assertionMethod',
            'verificationMethod': ANY
        }
        return proof
    def _proof_value_helper(self):
        return b'z4zvrPUULnHmaio2juYMLWMw5zzq3fyi21CkE9TRNRBALhTDyg63rd1btnpRtCNBieaX1BcVxi4yS62Zj2fthi4N9frUgCZBq6EwAVv7cAFgZcHPKxRvEuKPbg3qnxByUE1aB49QvnYYi7qYJWPBbB5s3xtUn4EBE1SMwcEe6yxCgp6GJ16FiYGazEtZKXGdws8s8uWuQjxrqJBDEBdzLstyXspD9Uw4FuwfuDZAr8jkwAvTPe9uCcANS5PG7a1hATTxEhgNNYabHhwSfyVGG9v1eKGvmM7dQhcGyJafoipfFpwrc7Zw9rgCQsDHVSQEaR8rRWUFGbRXQecHTZ1TWuqxR95oiyo8U4U8E7md7UGjhTSeC3rNQMP9fYjpNc9aAw781rizXeVsvhS4e47'

    def _mock_app_config(self):
        class Mock_App_Config:
            def __init__(self):
                self.verification_method = 'did:example:1234'
                self.issuance_timezone = 'UTC'

        return Mock_App_Config()

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
        proof_value = self._proof_value_helper()

        with patch.object(DummyCertificateHandler, 'add_proof', return_value= {"cert": "cert"} ) as mock_method:
            result = certificate_batch_handler.finish_batch(
                        '5604f0c442922b5db54b69f8f363b3eac67835d36a006b98e8727f83b6a830c0', chain
                        )
        self.assertEqual(certificate_batch_handler.proof, [{'cert': 'cert'}, {'cert': 'cert'}, {'cert': 'cert'}])

        mock_method.assert_any_call(ANY, proof_value)

    def test_batch_handler_finish_batch(self):
        certificate_batch_handler, certificates_to_issue = self._get_certificate_batch_handler()

        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()

        chain = Chain.bitcoin_mainnet
        proof_value = self._proof_value_helper()

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        with patch.object(DummyCertificateHandler, 'add_proof') as mock_method:
            result = certificate_batch_handler.finish_batch(
                    '5604f0c442922b5db54b69f8f363b3eac67835d36a006b98e8727f83b6a830c0', chain
                    )

        mock_method.assert_any_call(ANY, proof_value)

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

    # disable test until we can figure out how to verify content was written to file
    # see https://stackoverflow.com/questions/72706297/python-mock-open-patch-with-wraps-how-to-access-write-calls
    @mock.patch("builtins.open", create=True, wraps=builtins.open)
    def xtest_add_proof(self, mock_open):
        handler = CertificateV3Handler()

        cert_to_issue = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1'
            ],
            'kek': 'kek'
        }
        proof = {'a': 'merkel'}
        file_call = 'call().__enter__().write(\'{"kek": "kek", "proof": {"a": "merkel"}}\')'

        metadata = mock.Mock()
        metadata.blockchain_cert_file_name = 'file_path.nfo'

        with patch.object(
        CertificateV3Handler, '_get_certificate_to_issue', return_value=cert_to_issue) as mock_method:
                handler.add_proof(metadata, proof)

        mock_open.assert_any_call('file_path.nfo', 'w')
        calls = mock_open.mock_calls
        print(calls)
        call_strings = map(str, calls)
        print(mock_open.return_value.__enter__().write.mock_calls)
        assert file_call in call_strings

    def test_web_add_proof(self):
        handler = CertificateWebV3Handler(self._mock_app_config())
        proof_value = self._proof_value_helper()
        certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1'
            ],
            'kek': 'kek'
        }

        return_cert = handler.add_proof(certificate_json, proof_value)
        self.assertEqual(return_cert, {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/security/data-integrity/v2'
            ],
            'kek': 'kek',
            'proof': self._proof_helper()
        })

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
