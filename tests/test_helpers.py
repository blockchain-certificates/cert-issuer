import os
import shutil
import tempfile
import unittest
import json
from pathlib import Path

import importlib
from cert_issuer import helpers
from cert_issuer.errors import NoCertificatesFoundError

class TestPrepareIssuanceBatch(unittest.TestCase):
    def setUp(self):
        importlib.reload(helpers)
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

        self.unsigned_dir = self.base_dir / "unsigned"
        self.signed_dir = self.base_dir / "signed"
        self.blockchain_dir = self.base_dir / "blockchain"
        self.work_dir = self.base_dir / "work"

        self.unsigned_dir.mkdir()
        (self.unsigned_dir / "cert1.json").write_text(json.dumps({"id": 1}))
        (self.unsigned_dir / "cert2.json").write_text(json.dumps({"id": 2}))
        (self.unsigned_dir / "not_a_cert.txt").write_text("ignore me")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prepares_and_identifies_certificates(self):
        metadata = helpers.prepare_issuance_batch(
            unsigned_certs_dir=str(self.unsigned_dir),
            signed_certs_dir=str(self.signed_dir),
            blockchain_certs_dir=str(self.blockchain_dir),
            work_dir=str(self.work_dir)
        )

        # Assert we got the expected UIDs
        self.assertIn("cert1", metadata)
        self.assertIn("cert2", metadata)
        self.assertNotIn("not_a_cert", metadata)
        self.assertEqual(len(metadata), 2)

        # Ensure metadata has correct file paths
        for uid, meta in metadata.items():
            self.assertTrue(str(meta.unsigned_cert_file_name).endswith(f"{uid}.json"))
            self.assertTrue(str(meta.signed_cert_file_name).endswith(f"{uid}.json"))
            self.assertTrue(str(meta.blockchain_cert_file_name).endswith(f"{uid}.json"))
            self.assertTrue(str(meta.final_blockchain_cert_file_name).endswith(f"{uid}.json"))

    def test_raises_if_no_certificates(self):
        # Clean out the unsigned cert dir and re-test
        for file in self.unsigned_dir.glob("*"):
            file.unlink()

        with self.assertRaises(NoCertificatesFoundError):
            helpers.prepare_issuance_batch(
                unsigned_certs_dir=str(self.unsigned_dir),
                signed_certs_dir=str(self.signed_dir),
                blockchain_certs_dir=str(self.blockchain_dir),
                work_dir=str(self.work_dir)
            )


if __name__ == '__main__':
    unittest.main()
