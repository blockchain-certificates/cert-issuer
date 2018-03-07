#!/usr/bin/python3
__requires__ = 'cert-issuer==2.0.11'
import re
import sys
import json
import uuid
from pkg_resources import load_entry_point
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from subprocess import call

auth = HTTPBasicAuth()
app = Flask(__name__)

info_json = {
    'Author': u'Yancy Ribbens',
    'description': u'Create blockcert via API request',
    'version': u'Pilot'
    }

@app.route('/cert-issuer/api/v1.0/issue_cert', methods=['POST'])
def create_cert():
    if not request.json:
        abort(400)
    file_name = '/etc/cert-issuer/data/unsigned_certificates/' + str(uuid.uuid4()) + '.json'
    with open(file_name, 'w') as outfile:
        json.dump(request.json, outfile)
    call('cert-issuer')
    return jsonify({'info': info_json}), 201

@app.route('/cert-issuer/api/v1.0/info', methods=['GET'])
def info():
    return jsonify({'info': info_json})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
