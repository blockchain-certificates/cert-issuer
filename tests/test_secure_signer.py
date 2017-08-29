import unittest

import bitcoin

from cert_issuer import signer
from cert_issuer.signer import SecretManager


class MockSecureSigner(SecretManager):
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
    def test_verify_signature(self):
        bitcoin.SelectParams('testnet')
        signer.verify_signature('92b99af9-569a-4899-a9a1-6326b5f7065b',
                                       'data/92b99af9-569a-4899-a9a1-6326b5f7065b.json',
                                       'mmShyF6mhf6LeQzPdEsmiCghhgMuEn9TNF')


if __name__ == '__main__':
    unittest.main()
