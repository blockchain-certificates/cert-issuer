#! /bin/sh
mkdir -p venv/
rm -r venv/test/
virtualenv venv/test
source venv/test/bin/activate
python setup.py install experimental --blockchain=ethereum
