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

    def test_hash_certs(self):

        cert_metadata = CertificateMetadata(MagicMock(), 'someuid', 'somekey')
        cert_info = {'someuid': cert_metadata}
        with patch('cert_issuer.create_certificates.open', mock_open(read_data='bibble'.encode('utf-8')), create=True) as m:
            create_certificates.hash_certs(cert_info)
            handle = m()
            handle.read.assert_called_once()
            handle.write.assert_called_once_with(
                b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')

    def test__hash_cert(self):
        hashed_cert = create_certificates._hash_cert('bibble'.encode('utf-8'))
        self.assertEqual(hashed_cert,
                         b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')


if __name__ == '__main__':
    unittest.main()
