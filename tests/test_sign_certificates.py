import unittest

from mock import MagicMock
from mock import mock_open
from mock import patch


from cert_issuer.helpers import CertificateMetadata
from cert_issuer.secure_signing import Signer, SecretManager, _sign


class MockSecretManager(SecretManager):
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def get_wif(self):
        return 'tcKK1A9Si73zG5ZFnA6XYyhAcb1BNrMVyG'


class TestSignCertificates(unittest.TestCase):
    def test_sign_cert(self):
        signer = Signer(MockSecretManager())
        cert_metadata = CertificateMetadata('test/unsigned.json', 'test/signed.json')
        cert_info = {'123452': cert_metadata}

        with patch('cert_issuer.secure_signing.open', mock_open(read_data='{"assertion":{"uid": "123"}}'),
                   create=True) as m, \
                patch('cert_issuer.secure_signing.SignMessage', return_value=b'123'):
            signer.sign_certs(cert_info)
            handle = m()
            handle.write.assert_called_once_with(
                bytes('{"assertion": {"uid": "123"}, "signature": "123"}', 'utf-8'))

    def test_sign_cert(self):
        mock_privkey = MagicMock('test')
        mock_privkey.sign_compact = b'4545454'
        with patch('cert_issuer.secure_signing.SignMessage', return_value=b'123'):
            signed_cert = _sign('{"assertion":{"uid": "123"}}', mock_privkey)
            self.assertEqual(signed_cert, '{"assertion": {"uid": "123"}, "signature": "123"}')


if __name__ == '__main__':
    unittest.main()
