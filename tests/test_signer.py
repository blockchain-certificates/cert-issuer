import unittest
import mock

from cert_issuer.signer import FinalizableSigner


class TestSigner(unittest.TestCase):
    def test_finalizable_signer(self):
        mock_sm = mock.Mock()

        with FinalizableSigner(mock_sm) as fs:
            mock_sm.start.assert_called()

        mock_sm.stop.assert_called()


if __name__ == '__main__':
    unittest.main()
