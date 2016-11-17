#!/bin/bash

bitcoind -daemon
source /cert-issuer/env/bin/activate
cd /cert-issuer/
python service/run.py -c conf_testnet_common.ini --usb_name /cert-issuer/