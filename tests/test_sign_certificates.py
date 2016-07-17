import unittest

from cert_issuer import sign_certificates
from cert_issuer.models import CertificateMetadata
from mock import MagicMock
from mock import mock_open
from mock import patch

# unittest.TestCase
class TestSignCertificates():

    # test_
    def sign_cert(self):
        # TODO: update this test
        cert_metadata = CertificateMetadata('test/unsigned.json', 'test/signed.json')
        cert_info = {'123452': cert_metadata}

        with patch('cert_issuer.sign_certificates.open', mock_open(read_data='{"assertion":{"uid": "123"}}'),
                   create=True) as m, \
                patch('cert_issuer.sign_certificates.SignMessage', return_value=b'123'), \
                patch('cert_issuer.helpers.import_key', return_value='tcKK1A9Si73zG5ZFnA6XYyhAcb1BNrMVyG'):
            sign_certificates.sign_certs(cert_info)
            handle = m()
            handle.write.assert_called_once_with(
                bytes('{"assertion": {"uid": "123"}, "signature": "123"}', 'utf-8'))

    # test__
    def sign_cert(self):
        mock_privkey = MagicMock('test')
        mock_privkey.sign_compact = b'4545454'
        with patch('cert_issuer.sign_certificates.SignMessage', return_value=b'123'):
            signed_cert = sign_certificates._sign('{"assertion":{"uid": "123"}}', mock_privkey)
            self.assertEqual(signed_cert, '{"assertion": {"uid": "123"}, "signature": "123"}')


#if __name__ == '__main__':
#    unittest.main()
