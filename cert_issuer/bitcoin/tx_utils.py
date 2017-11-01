"""
Helpers for bitcoin transactions, including:
 - transaction size estimation
 - tx output creation
 - verify tx before sending
 - sign tx
"""

import io
import logging

from bitcoin.core import CScript, CMutableTransaction, CMutableTxOut, CTxIn, COutPoint
from bitcoin.core.script import OP_RETURN
from bitcoin.wallet import CBitcoinAddress
from pycoin.tx.Tx import Tx, TxOut

from cert_issuer.errors import UnverifiedTransactionError

BYTES_PER_INPUT = 148  # assuming compressed public key
BYTES_PER_OUTPUT = 34
FIXED_EXTRA_BYTES = 10
OP_RETURN_BYTE_COUNT = 43  # our op_return output values always have the same length because they are SHA-256 hashes


def create_trx(op_return_val, issuing_transaction_fee, issuing_address, tx_outs, tx_inputs):
    """

    :param op_return_val:
    :param issuing_transaction_fee:
    :param issuing_address:
    :param tx_outs:
    :param tx_input:
    :return:
    """
    cert_out = CMutableTxOut(0, CScript([OP_RETURN, op_return_val]))
    tx_ins = []
    value_in = 0
    for tx_input in tx_inputs:
        tx_ins.append(CTxIn(COutPoint(tx_input.tx_hash, tx_input.tx_out_index)))
        value_in += tx_input.coin_value

    # send change back to our address
    amount = value_in - issuing_transaction_fee
    if amount > 0:
        change_out = create_transaction_output(issuing_address, amount)
        tx_outs = tx_outs + [change_out]
    tx_outs = tx_outs + [cert_out]
    transaction = CMutableTransaction(tx_ins, tx_outs)
    return transaction


def calculate_raw_tx_size_with_op_return(num_inputs, num_outputs):
    """
    :param num_inputs:
    :param num_outputs:
    :return:
    """
    size = calculate_raw_tx_size(num_inputs, num_outputs)
    return size + OP_RETURN_BYTE_COUNT


def calculate_raw_tx_size(num_inputs, num_outputs):
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


def create_transaction_output(address, output_value):
    """
    Create a single transaction output
    :param address:
    :param output_value:
    :return:
    """
    bitcoin_address = CBitcoinAddress(address)
    tx_out = CMutableTxOut(output_value, bitcoin_address.to_scriptPubKey())
    return tx_out


def get_byte_count(signed_tx):
    s = io.BytesIO()
    signed_tx.stream(s)
    tx_byte_count = len(s.getvalue())
    return tx_byte_count


def prepare_tx_for_signing(hex_tx, tx_inputs):
    logging.info('Preparing tx for signing')
    transaction = Tx.from_hex(hex_tx)
    unspents = [TxOut(coin_value=tx_input.coin_value, script=tx_input.script) for tx_input in tx_inputs]
    transaction.set_unspents(unspents)
    return transaction


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


def calculate_tx_total(tx_cost_constants, num_inputs, num_outputs):
    """

    :param tx_cost_constants:
    :param num_inputs:
    :param num_outputs:
    :return:
    """
    tx_fee = calculate_tx_fee(tx_cost_constants, num_inputs, num_outputs)
    coin_per_output = tx_cost_constants.get_minimum_output_coin()
    total = coin_per_output * num_outputs + tx_fee
    return total


def calculate_tx_fee(tx_cost_constants, num_inputs, num_outputs):
    """
    The course grained (hard-coded value) of something like 0.0001 BTC works great for standard transactions
    (one input, one output). However, it will cause a lag in more complex or large transactions. So we calculate the
    raw tx fee, then take the max of the default fee and the refined cost to ensure prompt processing.

    The transaction fee is:
        fee = satoshi_per_byte * tx_size
    :param tx_cost_constants:
    :param num_inputs:
    :param num_outputs:
    :return:
    """
    tx_size = calculate_raw_tx_size_with_op_return(num_inputs, num_outputs)
    tx_fee = tx_cost_constants.satoshi_per_byte * tx_size
    return max(tx_fee, tx_cost_constants.get_recommended_fee_coin())
