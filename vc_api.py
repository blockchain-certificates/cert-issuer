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


@app.errorhandler(Exception)
def handle_exception(e):
    print('HANDLE ERROR', vars(e))
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response, 400
    # pass through HTTP errors
    # if isinstance(e, HTTPException):
    #     return e

    # now you're handling non-HTTP exceptions only
    # return render_template("500_generic.html", e=e), 500


@app.route('/api/v1.0/credentials/issue/', methods=['POST'])
@app.route('/api/v1.0/credentials/issue/<handler>', methods=['POST'])
def issue(handler=None):
    blockchain_handler = ethereum if handler == 'ethereum' else bitcoin
    config = get_config()

    # maintain shape of response object as provided by the caller
    was_array = True

    if not isinstance(request.json['credential'], list):
        was_array = False
        array_of_credentials = [request.json['credential']]
    else:
        array_of_credentials = request.json['credential']

    try:
        certificate_batch_handler, transaction_handler, connector = \
                blockchain_handler.instantiate_blockchain_handlers(config, False)
        certificate_batch_handler.set_certificates_in_batch(array_of_credentials)
        cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)
        if not was_array:
            signed_credential = certificate_batch_handler.proof[0]
        else:
            signed_credential = certificate_batch_handler.proof
        response = {
            'verifiableCredential': signed_credential
        }

        return response, 201
    except Exception as e:
        return handle_exception(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
