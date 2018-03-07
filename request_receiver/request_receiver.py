#!/usr/bin/python3
__requires__ = 'cert-issuer==2.0.11'
import re
import sys
from pkg_resources import load_entry_point
from flask import Flask, jsonify 
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)

info_json = {
    'Author': u'Yancy Ribbens',
    'description': u'Create blockcert via API request',
    'version': u'Alpha'
    }

@app.route('/request_receiver/api/v1.0/issue_cert', methods=['POST'])
def create_cert():
    # load_entry_point('cert-issuer==2.0.11', 'console_scripts', 'cert-issuer')()
    return "Hello, World!"

@app.route('/request_receiver/api/v1.0/info', methods=['GET'])
def info():
    return jsonify({'info': info_json})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
