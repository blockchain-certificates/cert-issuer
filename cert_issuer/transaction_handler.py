from abc import abstractmethod

from cert_issuer import tx_utils

# Estimate fees assuming worst case 3 inputs
ESTIMATE_NUM_INPUTS = 3

# Estimate fees assuming 1 output for change.
# Note that tx_utils calculations add on cost due to OP_RETURN size, so it doesn't need to be added here.
V2_NUM_OUTPUTS = 1


class TransactionHandler(object):
    def __init__(self, tx_cost_constants, issuing_address):
        self.tx_cost_constants = tx_cost_constants
        self.issuing_address = issuing_address

    @abstractmethod
    def estimate_cost_for_certificate_batch(self, num_inputs=ESTIMATE_NUM_INPUTS):
        pass

    @abstractmethod
    def create_transaction(self, last_input, op_return_value):
        pass


class TransactionV1_2Handler(TransactionHandler):
    def __init__(self, tx_cost_constants, issuing_address, certificates_to_issue, revocation_address):
        super().__init__(tx_cost_constants, issuing_address)
        self.certificates_to_issue = certificates_to_issue
        self.revocation_address = revocation_address

    def estimate_cost_for_certificate_batch(self, num_inputs=ESTIMATE_NUM_INPUTS):
        """
        Per certificate, we pay 2*min_per_output (which is based on dust) + fee. Note assumes 1 input
        per tx.
        :return:
        """
        # output per recipient
        num_outputs = len(self.certificates_to_issue)
        # plus revocation outputs
        num_outputs += sum(1 for c in self.certificates_to_issue.values() if c.revocation_key)
        # plus global revocation, change output, and OP_RETURN
        num_outputs += 3
        total = tx_utils.calculate_tx_total(self.tx_cost_constants, num_inputs, num_outputs)
        return total

    def create_transaction(self, inputs, op_return_value):
        tx_outs = self.build_recipient_tx_outs()
        tx_outs.append(tx_utils.create_transaction_output(self.revocation_address,
                                                          self.tx_cost_constants.get_minimum_output_coin()))

        total = self.estimate_cost_for_certificate_batch()
        transaction = tx_utils.create_trx(
            op_return_value,
            total,
            self.issuing_address,
            tx_outs,
            inputs)

        return transaction

    def build_recipient_tx_outs(self):
        """
        Creates 2 transaction outputs for each recipient: one to their public key and the other to their specific
        revocation key.
        :return:
        """
        tx_outs = []
        for _, certificate in self.certificates_to_issue.items():
            recipient_outs = [tx_utils.create_transaction_output(certificate.public_key,
                                                                 self.tx_cost_constants.get_minimum_output_coin())]
            if certificate.revocation_key:
                recipient_outs.append(tx_utils.create_transaction_output(certificate.revocation_key,
                                                                         self.tx_cost_constants.get_minimum_output_coin()))

            tx_outs += recipient_outs

        return tx_outs


class TransactionV2Handler(TransactionHandler):
    def __init__(self, tx_cost_constants, issuing_address):
        super().__init__(tx_cost_constants, issuing_address)

    def estimate_cost_for_certificate_batch(self, num_inputs=ESTIMATE_NUM_INPUTS):
        total = tx_utils.calculate_tx_fee(self.tx_cost_constants, num_inputs, V2_NUM_OUTPUTS)
        return total

    def create_transaction(self, inputs, op_return_value):
        fee = tx_utils.calculate_tx_fee(self.tx_cost_constants, len(inputs), V2_NUM_OUTPUTS)
        transaction = tx_utils.create_trx(
            op_return_value,
            fee,
            self.issuing_address,
            [],
            inputs)

        return transaction
