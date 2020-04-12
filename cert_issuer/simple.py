import copy

from cert_core import Chain
from cert_issuer.blockchain_handlers.ethereum import initialize_signer, EthereumTransactionCostConstants
from cert_issuer.blockchain_handlers.ethereum.connectors import EthereumServiceProviderConnector
from cert_issuer.blockchain_handlers.ethereum.transaction_handlers import EthereumTransactionHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_schema import normalize_jsonld


class SimplifiedCertificateBatchIssuer():
    """
    Class to issue blockcerts without relying on filesystem usage.
    (except for the Private Key which remains a file until the overall key handling issue is solved in theory)

    Please note that it currently only supports anchoring to Ethereum.
    """

    def __init__(self, config: 'AttrDict', unsigned_certs: dict):
        # 1- Prepare config and unsigned certs (These come from my latest changes in cert-tools
        self.config = config
        self.config.chain = Chain.parse_from_chain(self.config.chain)

        self.secret_manager = initialize_signer(self.config)
        self.cost_constants = EthereumTransactionCostConstants(self.config.gas_price, self.config.gas_limit)
        self.connector = EthereumServiceProviderConnector(self.config.chain, self.config.api_token)

        self.unsigned_certs = unsigned_certs
        self.cert_generator = self._create_cert_generator()

        # 2- Calculate Merkle Proof and Root
        self.merkle_tree_generator = MerkleTreeGenerator()
        self.merkle_tree_generator.populate(self.cert_generator)
        self.merkle_root = self.merkle_tree_generator.get_blockchain_data()

    def issue(self):
        """Anchor the merkle root in a blockchain transaction and add the tx id and merkle proof to each cert."""
        transaction_handler = EthereumTransactionHandler(
            self.connector,
            self.cost_constants,
            self.secret_manager,
            issuing_address=self.config.issuing_address
        )
        transaction_handler.ensure_balance()
        tx_id = transaction_handler.issue_transaction(self.merkle_root)

        proof_generator = self.merkle_tree_generator.get_proof_generator(tx_id, self.config.chain)
        signed_certs = copy.deepcopy(self.unsigned_certs)
        for _, cert in signed_certs.items():
            proof = next(proof_generator)
            cert['signature'] = proof

        # Check cert integrity
        self._ensure_successful_issuing(tx_id, signed_certs)
        return tx_id, signed_certs

    @staticmethod
    def _ensure_successful_issuing(tx_id: str, signed_certs: dict):
        assert tx_id != "0xfail"
        for uid, cert in signed_certs.items():
            assert cert['signature']['anchors'][0]['sourceId'] == tx_id

    def _create_cert_generator(self):
        for uid, cert in self.unsigned_certs.items():
            normalized = normalize_jsonld(cert, detect_unmapped_fields=False)
            yield normalized.encode('utf-8')
