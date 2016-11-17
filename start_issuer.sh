#!/bin/bash

bitcoind -daemon
source /cert-issuer/env/bin/activate
python /cert-issuer/service/run.py -c /cert-issuer/conf_testnet_common.ini