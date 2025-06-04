#!/usr/bin/python3
import json
from flask import Flask, request

import cert_issuer.config
from cert_issuer.blockchain_handlers import bitcoin, ethereum
import cert_issuer.issue_certificates

app = Flask(__name__)
config = None

def get_config():
    global config
    if config == None:
        config = cert_issuer.config.get_config()
    return config

@app.route('/api/v1.0/credentials/issue/', methods=['POST'])
@app.route('/api/v1.0/credentials/issue/<handler>', methods=['POST'])
def issue(handler=None):
    blockchain_handler = ethereum if handler == 'ethereum' else bitcoin
    config = get_config()

    if not isinstance(request.json, list):
        array_of_credentials = [request.json]
    else:
        array_of_credentials = request.json

    try:
        certificate_batch_handler, transaction_handler, connector = \
                blockchain_handler.instantiate_blockchain_handlers(config, False)
        certificate_batch_handler.set_certificates_in_batch(array_of_credentials)
        cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)

        response = {
            'verifiableCredential': json.dumps(certificate_batch_handler.proof)
        }

        return response, 201
    except Exception:
        return 400

if __name__ == '__main__':
    app.run(host='0.0.0.0')
