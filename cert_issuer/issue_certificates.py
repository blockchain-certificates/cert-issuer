import logging
import os
import shutil
import sys

from cert_issuer import helpers
from cert_issuer import secure_signer as secure_signer_helper
from cert_issuer.certificate_handler import CertificateV1_2Handler, CertificateV2Handler, CertificateBatchHandler
from cert_issuer.connectors import ServiceProviderConnector
from cert_issuer.errors import InsufficientFundsError
from cert_issuer.issuer import Issuer
from cert_issuer.transaction_handler import TransactionV1_2Handler, TransactionV2Handler
from cert_issuer.tx_utils import TransactionCostConstants

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def main(app_config, secure_signer=None, prepared_inputs=None, certificate_batch_handler=None):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir
    blockchain_certificates_dir = app_config.blockchain_certificates_dir
    work_dir = app_config.work_dir
    v1 = app_config.v1
    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address  # not needed for v2

    certificates, batch_metadata = helpers.prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir,
                                                                  blockchain_certificates_dir, work_dir)
    num_certificates = len(certificates)
    if num_certificates < 1:
        logging.warning('No certificates to process')
        return None

    logging.info('Processing %d certificates under work path=%s', num_certificates, work_dir)

    logging.info('Signing certificates...')
    if not secure_signer:
        secure_signer = secure_signer_helper.initialize_secure_signer(app_config)
    connector = ServiceProviderConnector(app_config.bitcoin_chain)
    tx_constants = TransactionCostConstants(app_config.tx_fee, app_config.dust_threshold, app_config.satoshi_per_byte)

    if v1:
        if not certificate_batch_handler:
            certificate_handler = CertificateV1_2Handler()
        transaction_handler = TransactionV1_2Handler(tx_cost_constants=tx_constants,
                                                     issuing_address=issuing_address,
                                                     certificates_to_issue=certificates,
                                                     revocation_address=revocation_address)
    else:
        if not certificate_batch_handler:
            certificate_handler = CertificateV2Handler()
        transaction_handler = TransactionV2Handler(tx_cost_constants=tx_constants, issuing_address=issuing_address)

    if not certificate_batch_handler:
        certificate_batch_handler = CertificateBatchHandler(certificates_to_issue=certificates,
                                                            certificate_handler=certificate_handler)
    else:
        certificate_batch_handler.certificates_to_issue = certificates

    issuer = Issuer(connector=connector,
                    secure_signer=secure_signer,
                    certificate_batch_handler=certificate_batch_handler,
                    transaction_handler=transaction_handler,
                    max_retry=app_config.max_retry,
                    prepared_inputs=prepared_inputs)
    transaction_cost = issuer.estimate_cost_for_certificate_batch()
    logging.info('Total cost will be %d satoshis', transaction_cost)

    # ensure the issuing address has sufficient balance
    balance = connector.get_balance(issuing_address)

    if transaction_cost > balance:
        error_message = 'Please add {} satoshis to the address {}'.format(
            transaction_cost - balance, issuing_address)
        logging.error(error_message)
        raise InsufficientFundsError(error_message)

    tx_id = issuer.issue_certificates()

    blockcerts_tmp_dir = os.path.join(work_dir, helpers.BLOCKCHAIN_CERTIFICATES_DIR)
    if not os.path.exists(blockchain_certificates_dir):
        os.makedirs(blockchain_certificates_dir)
    for item in os.listdir(blockcerts_tmp_dir):
        s = os.path.join(blockcerts_tmp_dir, item)
        d = os.path.join(blockchain_certificates_dir, item)
        shutil.copy2(s, d)

    logging.info('Your Blockchain Certificates are in %s', blockchain_certificates_dir)
    return tx_id


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        secret_manager = secure_signer_helper.initialize_secure_signer(parsed_config)
        tx_id = main(parsed_config, secret_manager)
        if tx_id:
            logging.info('Transaction id is %s', tx_id)
        else:
            logging.error('Certificate issuing failed')
            exit(1)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
