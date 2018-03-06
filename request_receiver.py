#!/usr/bin/python3
__requires__ = 'cert-issuer==2.0.11'
import re
import sys
from pkg_resources import load_entry_point
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    load_entry_point('cert-issuer==2.0.11', 'console_scripts', 'cert-issuer')()
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
