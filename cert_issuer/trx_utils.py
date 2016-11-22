"""
Helpers for bitcoin transactions, including:
 - transaction size and fee estimation
 - tx output creation
 - verify tx before sending
 - sign tx
"""

import io
import logging

from bitcoin.core import CScript, CMutableTransaction, CMutableTxOut, CTxIn, COutPoint
from bitcoin.core.script import OP_RETURN
from bitcoin.wallet import CBitcoinAddress

from cert_issuer import config
from cert_issuer.errors import UnverifiedTransactionError
from cert_issuer.models import TransactionCosts

COIN = 100000000  # satoshis in 1 btc
BYTES_PER_INPUT = 148  # assuming compressed public key
BYTES_PER_OUTPUT = 34
FIXED_EXTRA_BYTES = 10
OP_RETURN_BYTE_COUNT = 43  # our op_return output values always have the same length because they are SHA-256 hashes
SATOSHI_PER_BYTE = config.get_satoshi_per_byte()
RECOMMENDED_FEE_PER_TRANSACTION = config.get_fee_per_trx()
MIN_PER_OUTPUT = config.get_min_per_output()


def create_trx(op_return_val, issuing_transaction_cost,
               issuing_address, tx_outs, tx_input):
    """

    :param op_return_val:
    :param issuing_transaction_cost:
    :param issuing_address:
    :param tx_outs:
    :param tx_input:
    :return:
    """
    cert_out = CMutableTxOut(0, CScript([OP_RETURN, op_return_val]))
    tx_ins = [CTxIn(COutPoint(tx_input.tx_hash, tx_input.tx_out_index))]
    value_in = tx_input.coin_value

    # send change back to our address
    amount = value_in - issuing_transaction_cost.total
    if amount > 0:
        change_out = create_transaction_output(issuing_address, amount)
        tx_outs = tx_outs + [change_out]
    tx_outs = tx_outs + [cert_out]
    transaction = CMutableTransaction(tx_ins, tx_outs)
    return transaction


def create_recipient_outputs(recipient_address, revocation_address):
    """
    Create per-recipient outputs: one to the recipient's address, and optionally one to the revocation address.

    :param recipient_address:
    :param revocation_address:
    :return:
    """
    recipient_outs = []
    recipient_outs.append(create_transaction_output(recipient_address, MIN_PER_OUTPUT * COIN))
    if revocation_address:
        recipient_outs.append(create_transaction_output(revocation_address, MIN_PER_OUTPUT * COIN))
    return recipient_outs


def create_transaction_output(address, transaction_fee):
    """
    Create a single transaction output
    :param address:
    :param transaction_fee:
    :return:
    """
    bitcoin_address = CBitcoinAddress(address)
    tx_out = CMutableTxOut(transaction_fee, bitcoin_address.to_scriptPubKey())
    return tx_out


def verify_transaction(signed_hextx, op_return_value):
    """
    Verify OP_RETURN field in transaction
    :param signed_hextx:
    :param op_return_value:
    :return:
    """
    logging.info('verifying op_return value for transaction')
    op_return_hash = signed_hextx[-72:-8]
    result = (op_return_value == op_return_hash)
    if not result:
        error_message = 'There was a problem verifying the transaction'
        raise UnverifiedTransactionError(error_message)
    logging.info('verified OP_RETURN')


def get_cost(num_outputs):
    """
    Get cost of the transaction:
    :param num_outputs:
    :return:
    """
    if not num_outputs or num_outputs < 1:
        raise ValueError('num_outputs must be greater than or equal to 1')

    tx_fee = calculate_tx_fee(1, num_outputs)
    coin_per_output = MIN_PER_OUTPUT * COIN
    total = coin_per_output * num_outputs + tx_fee
    return TransactionCosts(coin_per_output, fee=tx_fee, total=total)


def calculate_tx_fee(num_inputs, num_outputs):
    """
     The course grained (hard-coded value) of something like 0.0001 BTC works great for standard transactions
    (one input, one output). However, it will cause a lag in more complex or large transactions. So we calculate the
    raw tx fee, then take the max of the default fee and the refined cost to ensure prompt processing.

    The transaction fee is:
        fee = satoshi_per_byte * tx_size

    :param num_inputs:
    :param num_outputs:
    :return:
    """
    tx_size = calculate_raw_tx_size_with_op_return(num_inputs, num_outputs)
    tx_fee = SATOSHI_PER_BYTE * tx_size
    return max(tx_fee, RECOMMENDED_FEE_PER_TRANSACTION * COIN)


def calculate_raw_tx_size_with_op_return(num_inputs, num_outputs):
    """
    Whereas
    :param num_inputs:
    :param num_outputs:
    :return:
    """
    size = _calculate_raw_tx_size(num_inputs, num_outputs)
    return size + OP_RETURN_BYTE_COUNT


def _calculate_raw_tx_size(num_inputs, num_outputs):
    """
    To calculate the transaction size:
        tx_size = (num_inputs * BYTES_PER_INPUT) + (num_outputs * BYTES_PER_OUTPUT) + FIXED_EXTRA_BYTES +/- num_inputs

    We'll choose the upper bound, so:
        +/- num_inputs  =>  + num_inputs

    Equation and constants are taken from http://bitcoin.stackexchange.com/a/3011.

    :param num_inputs:
    :param num_outputs:
    :return:
    """
    tx_size = (num_inputs * BYTES_PER_INPUT) + (num_outputs *
                                                BYTES_PER_OUTPUT) + FIXED_EXTRA_BYTES + num_inputs
    return tx_size


def get_byte_count(signed_tx):
    s = io.BytesIO()
    signed_tx.stream(s)
    tx_byte_count = len(s.getvalue())
    return tx_byte_count
