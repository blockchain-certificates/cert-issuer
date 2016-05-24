import unittest


from mock import MagicMock
from mock import mock_open
from mock import patch
from issuer import config
from issuer.models import CertificateMetadata
from issuer import certificate_issuer


class TestCertificateSigner(unittest.TestCase):

    def setUp(self):
        self.app_config = config.CONFIG
        self.app_config.skip_wifi_check = True

    def test_sign_cert(self):

        cert_metadata = CertificateMetadata(self.app_config, 'somecertificate', 'some_name', 'somekey')
        cert_info = {'somecertificate': cert_metadata}

        with patch('issuer.certificate_issuer.open', mock_open(read_data='{"assertion":{"uid": "123"}}'), create=True) as m, \
                patch('issuer.certificate_issuer.SignMessage', return_value=b'123'), \
                patch('issuer.helpers.import_key', return_value='tcKK1A9Si73zG5ZFnA6XYyhAcb1BNrMVyG'):
            certificate_issuer.sign_certs(cert_info)
            m.assert_any_call('data/signed_certs/somecertificate.json', 'wb')
            handle = m()
            handle.write.assert_called_once_with(
                bytes('{"assertion": {"uid": "123"}, "signature": "123"}', 'utf-8'))

    def test_hash_certs(self):

        cert_metadata = CertificateMetadata(self.app_config, 'someuid', 'some_name', 'somekey')
        cert_info = {'someuid': cert_metadata}
        with patch('issuer.certificate_issuer.open', mock_open(read_data='bibble'.encode('utf-8')), create=True) as m:
            certificate_issuer.hash_certs(cert_info)
            m.assert_any_call('data/signed_certs/someuid.json', 'rb')
            m.assert_any_call('data/hashed_certs/someuid.txt', 'wb')

            handle = m()
            handle.read.assert_called_once()
            handle.write.assert_called_once_with(
                b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')

    def test__sign_cert(self):
        mock_privkey = MagicMock('test')
        mock_privkey.sign_compact = b'4545454'
        with patch('issuer.certificate_issuer.SignMessage', return_value=b'123'):
            signed_cert = certificate_issuer.do_sign('{"assertion":{"uid": "123"}}', mock_privkey)
            self.assertEqual(signed_cert, '{"assertion": {"uid": "123"}, "signature": "123"}')

    def test__hash_cert(self):
        hashed_cert = certificate_issuer._hash_cert('bibble'.encode('utf-8'))
        self.assertEqual(hashed_cert,
                         b'\xf1\x93\x13\xb9D\x94\x9e\x16\xb8\xf8\x12,\x05`u\x13\xa2\xa8\x1f\xfc\xd4\x87\x10\xe2\xd8\x98\xc1\x9f\x17\xa0\x83\xfa')


if __name__ == '__main__':
    unittest.main()
