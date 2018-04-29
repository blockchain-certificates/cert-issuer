import unittest

import mock
import json
from pycoin.serialize import b2h
from unittest.mock import patch

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateHandler, CertificateBatchWebHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer import helpers

class TestCertificateHandler(unittest.TestCase):
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

        handler = CertificateBatchWebHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator())

        return handler, certificates_to_issue


    def _get_certificate_batch_handler(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        handler = CertificateBatchHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator())

        return handler, certificates_to_issue

    def test_batch_handler_web_prepare(self):
        web_request = json.dumps([{'allyourbasearebelongtous': True}])
        web_handler, certificates_to_issue = self._get_certificate_batch_web_handler()
        web_handler.set_certificates_in_batch(web_request)
        single_item_batch = web_handler.prepare_batch()

        self.assertEqual(
                b2h(single_item_batch),
                '38451f557bc2b5ad74012d3389798281b993fc7375c024615ed73fb147670ba7')

        web_handler, certificates_to_issue = self._get_certificate_batch_web_handler()
        web_handler.set_certificates_in_batch(
                [{'allyourbasearebelongtous': True}, {'allyourbasearebelongtous': False}])
        multi_batch = web_handler.prepare_batch()
        self.assertNotEqual(b2h(single_item_batch), b2h(multi_batch))


    def test_batch_handler_prepare_batch(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        certificate_batch_handler, certificates_to_issue = self._get_certificate_batch_handler()
        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()

        self.assertEqual(
                b2h(result), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')


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


class DummyCertificateHandler(CertificateHandler):
    def __init__(self):
        self.counter = 0

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
