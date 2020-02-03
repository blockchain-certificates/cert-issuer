import logging
import sys

from cert_core import Chain

from cert_issuer.issuer import Issuer
from cert_issuer.revoker import Revoker

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def issue(app_config, certificate_batch_handler, transaction_handler):
    certificate_batch_handler.pre_batch_actions(app_config)

    transaction_handler.ensure_balance()

    issuer = Issuer(
        certificate_batch_handler=certificate_batch_handler,
        transaction_handler=transaction_handler,
        max_retry=app_config.max_retry)
    tx_id = issuer.issue(app_config.chain, app_config)

    certificate_batch_handler.post_batch_actions(app_config)
    return tx_id

def revoke_certificates(app_config, transaction_handler):
    # has to scale with number of revocations, so balance is checked before every transaction
    # transaction_handler.ensure_balance()

    revoker = Revoker(
        transaction_handler=transaction_handler,
        max_retry=app_config.max_retry)
    tx_id = revoker.revoke(app_config)

    return tx_id

def main(app_config):
    chain = app_config.chain
    if chain == Chain.ethereum_mainnet or chain == Chain.ethereum_ropsten:
        if app_config.issuing_method == "smart_contract":
            from cert_issuer.blockchain_handlers import ethereum_sc
            certificate_batch_handler, transaction_handler, connector = ethereum_sc.instantiate_blockchain_handlers(app_config)
            if app_config.revoke is True:
                return revoke_certificates(app_config, transaction_handler)
        else:
            from cert_issuer.blockchain_handlers import ethereum
            certificate_batch_handler, transaction_handler, connector = ethereum.instantiate_blockchain_handlers(app_config)
    else:
        from cert_issuer.blockchain_handlers import bitcoin
        certificate_batch_handler, transaction_handler, connector = bitcoin.instantiate_blockchain_handlers(app_config)
    return issue(app_config, certificate_batch_handler, transaction_handler)


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        tx_id = main(parsed_config)

        #this could throw an error resulting from to TO DO in file ethereum_sc/connectors.py @ method transact() --> not sure which tx_id has to be returned!
        if tx_id:
            logging.info('Transaction id is %s', tx_id)
        else:
            logging.error('Certificate issuing failed')
            exit(1)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
