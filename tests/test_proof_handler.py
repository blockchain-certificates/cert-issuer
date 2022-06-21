import unittest
from cert_issuer.proof_handler import ProofHandler

class TestProofHandler(unittest.TestCase):
    def test_multiple_two_chained_signature(self):
        handler = ProofHandler()
        fixture_initial_proof = {
          'type': 'Ed25519Signature2020',
          'created': '2022-05-02T16:36:22.933Z',
          'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
          'proofPurpose': 'assertionMethod',
          'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_certificate_json = {
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
        output = handler.add_proof(fixture_certificate_json, fixture_proof)
        self.assertEqual(output, {
            'kek': 'kek',
            'proof': [
                fixture_initial_proof,
                {
                    'type': 'ChainedProof2021',
                    'chainedProofType':  'MerkleProof2019',
                    'created': '2022-05-05T08:05:14.912828',
                    'previousProof': fixture_initial_proof,
                    'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
                    'proofPurpose': 'assertionMethod',
                    'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
                }
            ]
        })

    def test_multiple_three_chained_signature(self):
        handler = ProofHandler()
        fixture_initial_proof = {
          'type': 'Ed25519Signature2020',
          'created': '2022-05-02T16:36:22.933Z',
          'verificationMethod': 'did:key:z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs#z6MkjHnntGvtLjwfAMHWTAXXGJHhVL3DPtaT9BHmyTjWpjqs',
          'proofPurpose': 'assertionMethod',
          'proofValue': 'zAvFt59599JweBZ4zPP6Ge8LhKgECtBvDRmjG5VQbgEkPCiyMcM9QAPanJgSCs6RRGcKu96qNpfmpe9eTygpFZP6'
        }
        fixture_second_proof = {
            'type': 'ChainedProof2021',
            'chainedProofType':  'MerkleProof2019',
            'created': '2022-05-05T08:05:14.912828',
            'previousProof': fixture_initial_proof,
            'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
        }
        fixture_certificate_json = {
            'kek': 'kek',
            'proof': [
                fixture_initial_proof,
                fixture_second_proof
            ]
        }
        fixture_proof = {
            'type': 'MerkleProof2019',
            'created': '2022-05-06T20:31:54',
            'proofValue': 'mockProofValueForUnitTestPurpose',
            'proofPurpose': 'assertionMethod',
            'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
        }
        output = handler.add_proof(fixture_certificate_json, fixture_proof)
        self.maxDiff = None
        self.assertEqual(output, {
            'kek': 'kek',
            'proof': [
                fixture_initial_proof,
                fixture_second_proof,
                {
                    'type': 'ChainedProof2021',
                    'chainedProofType': 'MerkleProof2019',
                    'created': '2022-05-06T20:31:54',
                    'previousProof': {
                        'type': 'MerkleProof2019',
                        'created': '2022-05-05T08:05:14.912828',
                        'proofValue': 'zMcm4LfQFUZkWZyLJp1bqtXF8vkZZwp79x7Nvt5BmN2XV4usLLtDoeqiq3et923mcWfXde4a3m4f57yUZcATCbBXV1byb5AXbV8EzT6E8B9JKf3scvxxZCBVePtV4SrhYysAiLNJ9N2R8LgnpJ47wnQHkaTB1AMxrcLEHUTxm4zJTtQqf9orDLf3L4VoLzmST7ZzsDjuX9cw2hZ3Aazhhjy7swG44xfF1PC73SyCv77pDnJ6BSHm3azmbVG6BXv1EPtwF4J1YRqwojBEWk9nDgduACR7b9qNhQ46ND4B5vL8p3LkqTh',
                        'proofPurpose': 'assertionMethod',
                        'verificationMethod': 'did:ion:EiA_Z6LQILbB2zj_eVrqfQ2xDm4HNqeJUw5Kj2Z7bFOOeQ#key-1'
                    },
                    'proofValue': 'mockProofValueForUnitTestPurpose',
                    'proofPurpose': 'assertionMethod',
                    'verificationMethod': 'did:example:ebfeb1f712ebc6f1c276e12ec21#assertion'
                }
            ]
        })
