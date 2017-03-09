import unittest

import bitcoin

from cert_issuer import secure_signer


class TestIssueCertificates(unittest.TestCase):
    def test_verify_signature(self):
        bitcoin.SelectParams('testnet')
        secure_signer.verify_signature('92b99af9-569a-4899-a9a1-6326b5f7065b',
                                       'data/92b99af9-569a-4899-a9a1-6326b5f7065b.json',
                                       'mmShyF6mhf6LeQzPdEsmiCghhgMuEn9TNF')


if __name__ == '__main__':
    unittest.main()
