#!/usr/bin/python3
import json
from flask import Flask, jsonify, request, abort
from subprocess import call

import cert_issuer.config
from cert_issuer.blockchain_handlers import bitcoin
import cert_issuer.issue_certificates

app = Flask(__name__)
config = None

def get_config():
    global config
    if config == None:
        config = cert_issuer.config.get_config()
    return config

@app.route('/cert_issuer/api/v1.0/issue', methods=['POST'])
def issue():
    config = get_config()
    certificate_batch_handler, transaction_handler, connector = \
            bitcoin.instantiate_blockchain_handlers(config, False)
    certificate_batch_handler.set_certificates_in_batch(request.json)
    cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)
    return json.dumps(certificate_batch_handler.proof)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
