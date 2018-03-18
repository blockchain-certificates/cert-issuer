#!/usr/bin/python3
import re
import sys
import json
import os
from flask import Flask, jsonify, request, abort
from subprocess import call

import cert_issuer.config
from cert_issuer import bitcoin
import cert_issuer.issue_certificates

app = Flask(__name__)
config = None

info_json = {
    'Author': u'Yancy Ribbens',
    'description': u'REST API for cert-issuer',
    'version': u'Pilot'
    }

def get_config():
    global config
    if config == None:
        config = cert_issuer.config.get_config()
    return config

@app.route('/cert_issuer/api/v1.0/issue_cert', methods=['POST'])
def create_cert():
    if not request.json or not 'id' in request.json:
        abort(400)
    file_name = request.json['id'] + '.json' 
    full_path_name = '/etc/cert-issuer/data/unsigned_certificates/' + file_name
    with open(full_path_name, 'w') as outfile:
        json.dump(request.json, outfile)
    call('cert-issuer')
    os.remove(full_path_name)
    with open('/etc/cert-issuer/data/blockchain_certificates/' + file_name) as data_file:
        blockchain_cert = json.load(data_file)
    return jsonify(blockchain_cert), 201

@app.route('/cert_issuer/api/v1.0/issue', methods=['POST'])
def issue():
    config = get_config()
    certificate_batch_handler, transaction_handler, connector = \
            bitcoin.instantiate_blockchain_handlers(config)
    cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)
    return "hi"

@app.route('/cert_issuer/api/v1.0/certs/<string:cert_id>', methods=['GET'])
def get_blockchain_cert(cert_id):
    with open('/etc/cert-issuer/data/blockchain_certificates/' + cert_id + '.json') as data_file:
        blockchain_cert = json.load(data_file)
    return json.dumps(blockchain_cert)

@app.route('/cert_issuer/api/v1.0/info', methods=['GET'])
def info():
    config = get_config()
    config_dict = vars(config)
    #TODO TypeError: Object of type 'Chain' is not JSON serializable
    # del config_dict['chain']
    #return jsonify({**info_json, 'config': config_dict })
    return "todo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
