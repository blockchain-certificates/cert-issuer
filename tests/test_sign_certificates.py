import unittest

from mock import MagicMock
from mock import mock_open
from mock import patch

from cert_issuer.helpers import CertificateMetadata
from cert_issuer.secure_signer import Signer, SecureSigner


class MockSecureSigner(SecureSigner):
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def sign_message(self, message_to_sign):
        return '456'

    def sign_transaction(self, transaction_to_sign):
        return '123'



class TestSignCertificates(unittest.TestCase):

    def test_sign_cert(self):
        signer = Signer(MockSecureSigner())
        cert_metadata = CertificateMetadata('123', 'test/unsigned.json', 'test/signed.json')
        cert_info = {'123452': cert_metadata}

        with patch('cert_issuer.secure_signer.open', mock_open(read_data='{"assertion":{"uid": "123"}}'),
                   create=True) as m:
            signer.sign_certs(cert_info)
            handle = m()
            handle.write.assert_called_once_with(
                bytes('{"assertion": {"uid": "123"}, "signature": "456"}', 'utf-8'))



if __name__ == '__main__':
    unittest.main()
