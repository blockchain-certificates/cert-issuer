from collections import namedtuple

TransactionData = namedtuple(
    'TransactionData', ['uid', 'tx', 'tx_input', 'op_return_value', 'batch_metadata'])


class CostConstants:
    def __init__(self, recommended_fee_per_transaction, min_per_output, satoshi_per_byte):
        self.recommended_fee_per_transaction = recommended_fee_per_transaction
        self.min_per_output = min_per_output
        self.satoshi_per_byte = satoshi_per_byte


class TransactionCosts:
    """
    Represents costs for an issuing event, including the issuing transaction and transfer costs if applicable
    """

    def __init__(self, min_per_output, fee, total):
        self.min_per_output = min_per_output
        self.fee = fee
        self.total = total
        self.transfer_cost = 0

    def set_transfer_fee(self, transfer_cost):
        self.transfer_cost = transfer_cost
        self.total += self.transfer_cost

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance
