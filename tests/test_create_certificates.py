import unittest


from mock import MagicMock
from mock import mock_open
from mock import patch
from cert_issuer.models import CertificateMetadata
from cert_issuer import create_certificates
from cert_issuer import config

class TestCertificateSigner(unittest.TestCase):

    def setUp(self):
        config.get_config().skip_wifi_check = True
        mock = MagicMock()
        mock.uid = '34we3434'
        mock.name = 'Some Name'
        mock.pubkey = '123452'
        mock.unsigned_certificate_file_name = 'test/unsigned.json'
        mock.signed_certificate_file_name = 'test/signed.json'
        mock.certificate_hash_file_name = 'test/hashed.txt'
        mock.unsigned_tx_file_name = 'test/unsigned_tx.txt'
        mock.unsent_tx_file_name = 'test/unsent_tx.txt'
        mock.sent_tx_file_name = 'test/sent_tx.txt'

        self.mock_config = mock


    def test_sign_cert(self):
        cert_metadata = CertificateMetadata(self.mock_config, 'somecertificate', 'some_name', 'somekey')
        cert_info = {'somecertificate': cert_metadata}

        with patch('cert_issuer.create_certificates.open', mock_open(read_data='{"assertion":{"uid": "123"}}'), create=True) as m, \
                patch('cert_issuer.create_certificates.SignMessage', return_value=b'123'), \
                patch('cert_issuer.helpers.import_key', return_value='tcKK1A9Si73zG5ZFnA6XYyhAcb1BNrMVyG'):
            create_certificates.sign_certs(cert_info)
            handle = m()
            handle.write.assert_called_once_with(
                bytes('{"assertion": {"uid": "123"}, "signature": "123"}', 'utf-8'))

    def test_hash_certs(self):

        cert_metadata = CertificateMetadata(MagicMock(), 'someuid', 'some_name', 'somekey')
        cert_info = {'someuid': cert_metadata}
        with patch('cert_issuer.create_certificates.open', mock_open(read_data='bibble'.encode('utf-8')), create=True) as m:
            create_certificates.hash_certs(cert_info)
            handle = m()
            handle.read.assert_called_once()
            handle.write.assert_called_once_with(
                b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')

    def test__sign_cert(self):
        mock_privkey = MagicMock('test')
        mock_privkey.sign_compact = b'4545454'
        with patch('cert_issuer.create_certificates.SignMessage', return_value=b'123'):
            signed_cert = create_certificates.do_sign('{"assertion":{"uid": "123"}}', mock_privkey)
            self.assertEqual(signed_cert, '{"assertion": {"uid": "123"}, "signature": "123"}')

    def test__hash_cert(self):
        hashed_cert = create_certificates._hash_cert('bibble'.encode('utf-8'))
        self.assertEqual(hashed_cert,
                         b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')


if __name__ == '__main__':
    unittest.main()
