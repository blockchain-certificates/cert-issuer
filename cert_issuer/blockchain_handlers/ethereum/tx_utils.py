import logging
from web3 import Web3
from cert_issuer.errors import UnverifiedTransactionError


def create_ethereum_trx(issuing_address, nonce, to_address, blockchain_bytes, gasprice, gaslimit):
    # the actual value transfer is 0 in the Ethereum implementation
    value = 0
    tx = dict(
        nonce=nonce,
        gasPrice=gasprice,
        gas=gaslimit,
        to=Web3.to_checksum_address(to_address),
        value=value,
        data=blockchain_bytes)
    return tx


def verify_eth_transaction(signed_hextx, eth_data_field):
    """
    Verify ethDataField field in transaction
    :param signed_hextx:
    :param eth_data_field:
    :return:
    """
    logging.info('verifying ethDataField value for transaction')
    ethdata_hash = []
    for s in signed_hextx.split('80a0'):
        ethdata_hash.append(s)
    ethdata_hash = ethdata_hash[1][:64]
    result = (eth_data_field == ethdata_hash)
    if not result:
        error_message = 'There was a problem verifying the transaction'
        raise UnverifiedTransactionError(error_message)
    logging.info('verified ethDataField')
