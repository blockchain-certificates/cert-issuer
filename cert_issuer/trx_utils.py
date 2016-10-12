"""
Helpers for bitcoin transactions
"""

import logging

from bitcoin.core import CScript, CMutableTransaction, CMutableTxOut, CTxIn, COutPoint
from bitcoin.core.script import OP_RETURN
from bitcoin.wallet import CBitcoinAddress
from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx import Tx, TxOut
from pycoin.tx.pay_to import build_hash160_lookup

from cert_issuer import helpers
from cert_issuer.helpers import internet_off_for_scope
from cert_issuer.models import TransactionCosts

COIN = 100000000  # satoshis in 1 btc
BYTES_PER_INPUT = 148  # assuming compressed public key
BYTES_PER_OUTPUT = 34
FIXED_EXTRA_BYTES = 10


def create_trx(op_return_val, issuing_transaction_cost,
               issuing_address, txouts, tx_input):
    """

    :param op_return_val:
    :param issuing_transaction_cost:
    :param issuing_address:
    :param txouts:
    :param tx_input:
    :return:
    """
    cert_out = CMutableTxOut(0, CScript([OP_RETURN, op_return_val]))
    txins = [CTxIn(COutPoint(tx_input.tx_hash, tx_input.tx_out_index))]
    value_in = tx_input.coin_value

    # send change back to our address
    amount = value_in - issuing_transaction_cost.total
    if amount > 0:
        change_out = create_transaction_output(issuing_address, amount)
        txouts = txouts + [change_out]
    txouts = txouts + [cert_out]
    tx = CMutableTransaction(txins, txouts)
    return tx


def create_recipient_outputs(transaction_fee, recipient_address, revocation_address):
    """
    Create per-recipient outputs: one to the recipient's address, and optionally one to the revocation address.

    :param transaction_fee:
    :param recipient_address:
    :param revocation_address:
    :return:
    """
    recipient_out = create_transaction_output(recipient_address, transaction_fee)
    if revocation_address:
        revoke_out = create_transaction_output(revocation_address, transaction_fee)
        recipient_outs = [recipient_out] + [revoke_out]
    else:
        recipient_outs = [recipient_out]
    return recipient_outs


def create_transaction_output(address, transaction_fee):
    """
    Create a single transaction output
    :param address:
    :param transaction_fee:
    :return:
    """
    addr = CBitcoinAddress(address)
    tx_out = CMutableTxOut(transaction_fee, addr.to_scriptPubKey())
    return tx_out


@internet_off_for_scope
def sign_tx(hextx, tx_input, allowable_wif_prefixes=None):
    """
    Sign the transaction with private key
    :param hextx:
    :param tx_input:
    :param allowable_wif_prefixes:
    :return:
    """

    logging.info('Signing tx with private key')

    tx = Tx.from_hex(hextx)
    if allowable_wif_prefixes:
        wif = wif_to_secret_exponent(
            helpers.import_key(), allowable_wif_prefixes)
    else:
        wif = wif_to_secret_exponent(helpers.import_key())

    lookup = build_hash160_lookup([wif])

    tx.set_unspents(
        [TxOut(coin_value=tx_input.value, script=tx_input.script)])

    signed_tx = tx.sign(lookup)
    signed_hextx = signed_tx.as_hex()

    logging.info('Finished signing transaction')
    return signed_hextx


def get_cost(recommended_fee_per_transaction,
             dust_threshold, satoshi_per_byte, num_outputs):
    """
    Get cost of the transaction
    :param recommended_fee_per_transaction:
    :param dust_threshold:
    :param satoshi_per_byte:
    :param num_outputs:
    :return:
    """
    # note: assuming 1 input for now
    recommended_fee = recommended_fee_per_transaction * COIN
    min_per_output = dust_threshold * COIN
    txfee = calculate_txfee(satoshi_per_byte, 1, num_outputs, recommended_fee)
    total = calculate_total(min_per_output, num_outputs, txfee)

    return TransactionCosts(min_per_output, fee=txfee, total=total)


def calculate_total(min_per_output, num_outputs, txfee):
    """

    :param min_per_output:
    :param num_outputs:
    :param txfee:
    :return:
    """
    return min_per_output * num_outputs + txfee


def calculate_txfee(satoshi_per_byte, num_inputs, num_outputs, default_fee):
    """
     The course grained (hard-coded value) of something like 0.0001 BTC works great for standard transactions
    (one input, one output). However, it will cause a huge lag in more complex transactions (such as the one where the
    script spends a little bit of money to 10 temporary addresses).  So we calculate the raw tx fee for these more
    complex transactions, then take the max of the default fee and the refined cost to ensure prompt processing.

    The transaction fee is:
        fee = satoshi_per_byte * tx_size

    :param satoshi_per_byte: Satoshis per byte. This is an input rather than a constant because it may need to be
    updated dynamically
    :param num_inputs:
    :param num_outputs:
    :param default_fee
    :return:
    """
    tx_size = calculate_raw_tx_size(num_inputs, num_outputs)
    tx_fee = satoshi_per_byte * tx_size
    return max(tx_fee, default_fee)


def calculate_raw_tx_size(num_inputs, num_outputs):
    """
    To calculate the transaction size:
        tx_size = (num_inputs * BYTES_PER_INPUT) + (num_outputs * BYTES_PER_OUTPUT) + FIXED_EXTRA_BYTES +/- num_inputs

    We'll choose the upper bound, so:
        +/- num_inputs  =>  + num_inputs

    See explanation of constants above.

    :param num_inputs:
    :param num_outputs:
    :return:
    """
    tx_size = (num_inputs * BYTES_PER_INPUT) + (num_outputs *
                                                BYTES_PER_OUTPUT) + FIXED_EXTRA_BYTES + num_inputs
    return tx_size
