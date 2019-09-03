from cert_issuer.simple import SimplifiedCertificateBatchIssuer


def test_simplfied_issuing_process(config, unsigned_certs, write_private_key_file):
    """Please note this test actually anchors to Ropsten so you need internet access and funds in the given account."""
    simple_certificate_batch_issuer = SimplifiedCertificateBatchIssuer(config, unsigned_certs)
    tx_id, signed_certs = simple_certificate_batch_issuer.issue()
    one_cert_id = list(signed_certs.keys())[0]
    merkle_root = signed_certs[one_cert_id]['signature']['merkleRoot']
    print(f'Check https://ropsten.etherscan.io/tx/{tx_id} to confirm it contains the merkle root "{merkle_root}"')
    assert merkle_root == 'cffe57bac8b8f47df9f5bb89e88dda893774b45b77d6600d5f1836d309505b61'
    # This was already executed when issuing, just putting it here to be very explicit on what's being checked.
    SimplifiedCertificateBatchIssuer._ensure_successful_issuing(tx_id, signed_certs)
