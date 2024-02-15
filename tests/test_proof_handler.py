import unittest
from cert_issuer.proof_handler import ProofHandler
from cert_schema import ContextUrls
from mock import ANY

class TestProofHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ProofHandler()
        self.contextUrls = ContextUrls()

    def test_single_signature(self):
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek'
        }
        fixture_proof = {
            'type': 'DataIntegrityProof',
            'cryptosuite': 'merkle-proof-2019',
            'id': ANY,
            'created': '2022-05-05T08:05:14.912828',
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertEqual(output['proof'], fixture_proof)

    def test_single_signature_3_1_update_context_data_integrity_proof(self):
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/blockcerts/v3.1'
            ],
            'kek': 'kek'
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-05T08:05:14.912828',
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertIn(self.contextUrls.data_integrity_proof_v2(), output['@context'])

    def test_multiple_non_chained_signature(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': fixture_initial_proof
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-05T08:05:14.912828',
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        class MockConfig:
            multiple_proofs = 'concurrent'

        output = self.handler.add_proof(fixture_certificate_json, fixture_proof, MockConfig())
        self.assertEqual(output['proof'], [
            fixture_initial_proof,
            fixture_proof
        ])

    def test_multiple_two_chained_signature(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': fixture_initial_proof
        }
        fixture_proof = {
            'type': 'DataIntegrityProof',
            'cryptosuite':  'merkle-proof-2019',
            'created': '2022-05-05T08:05:14.912828',
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertEqual(output['proof'], [
            fixture_initial_proof,
            {
                'type': 'DataIntegrityProof',
                'cryptosuite':  'merkle-proof-2019',
                'created': '2022-05-05T08:05:14.912828',
                'previousProof': fixture_initial_proof['id'],
                'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
                'proofPurpose': 'assertionMethod',
                'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
            }
        ])

    def test_multiple_three_chained_signature(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_second_proof = {
            'type': 'DataIntegrityProof',
            'cryptosuite':  'merkle-proof-2019',
            'id': 'urn:uuid:f31afe18-829f-4f61-bfca-bed08b47af42',
            'created': '2022-05-05T08:05:14.912828',
            'previousProof': fixture_initial_proof['id'],
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': [
                fixture_initial_proof,
                fixture_second_proof
            ]
        }
        fixture_proof = {
            'type': 'DataIntegrityProof',
            'cryptosuite':  'merkle-proof-2019',
            'created': '2022-05-06T20:31:54',
            'proofValue': 'mockProofValueForUnitTestPurpose',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.maxDiff = None
        self.assertEqual(output['proof'], [
            fixture_initial_proof,
            fixture_second_proof,
            {
                'type': 'DataIntegrityProof',
                'cryptosuite': 'merkle-proof-2019',
                'created': '2022-05-06T20:31:54',
                'previousProof': fixture_second_proof['id'],
                'proofValue': 'mockProofValueForUnitTestPurpose',
                'proofPurpose': 'assertionMethod',
                'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
            }
        ])

    def test_adds_date_integrity_proof_context(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/security/suites/ed25519-2020/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': [
                fixture_initial_proof
            ]
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-06T20:31:54',
            'proofValue': 'mockProofValueForUnitTestPurpose',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertIn(self.contextUrls.data_integrity_proof_v2(), output['@context'])

    def test_adds_data_integrity_proof_context(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/security/suites/ed25519-2020/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': [
                fixture_initial_proof
            ]
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-06T20:31:54',
            'proofValue': 'mockProofValueForUnitTestPurpose',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertIn(self.contextUrls.data_integrity_proof_v2(), output['@context'])

    def test_updates_blockcerts_context_version(self):
        fixture_initial_proof = {
            'type': 'Ed25519Signature2020',
            'id': 'urn:uuid:1de8149b-fff1-4908-8d69-89b56358fd31',
            'created': '2022-05-02T16:36:22.933Z',
            'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
            'proofPurpose': 'assertionMethod',
            'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
            '@context': [
                'https://www.w3.org/2018/credentials/v1',
                'https://w3id.org/security/suites/ed25519-2020/v1',
                'https://w3id.org/blockcerts/v3'
            ],
            'kek': 'kek',
            'proof': [
                fixture_initial_proof
            ]
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-06T20:31:54',
            'proofValue': 'mockProofValueForUnitTestPurpose',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
        }
        output = self.handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertNotIn(self.contextUrls.v3_canonical(), output['@context'])
        self.assertIn(self.contextUrls.v3_1_canonical(), output['@context'])