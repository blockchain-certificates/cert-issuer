import argparse
import json
import subprocess
import time
from json import JSONDecodeError

import content_hash
import ipfshttpclient
from ens import ENS

import path_tools as tools
from connectors import ContractConnection, MakeW3

try:
    sc = ContractConnection("blockcertsonchaining")
except (KeyError, JSONDecodeError):
    print("Init your contr info first with deploy.py or issuer.py --init")


def get_contr_info_from_ens(address="blockcerts.eth"):
    try:
        subprocess.Popen(["ipfs", "daemon"])
        time.sleep(10)
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        ens_domain = str(address)
        ens_resolver = ContractConnection("ropsten_ens_resolver")

        w3 = MakeW3().get_w3_obj()
        ns = ENS.fromWeb3(w3)
        node = ns.namehash(ens_domain)

        contr_info = ""
        if client is not None:
            content = (ens_resolver.functions.call("contenthash", node)).hex()
            content = content_hash.decode(content)
            contr_info = str(client.cat(content))[2:-1]
        with open(tools.get_contr_info_path(), "w+") as f:
            json.dump(json.loads(contr_info), f)
        subprocess.run(["ipfs", "shutdown"])
        client.close()
    except Exception:
        print("couldnt init contract info")


def issue(hash_val):
    '''Issues a certificate on the blockchain'''
    print("> following roothash gets issued: " + str(hash_val))
    sc.functions.transact("issue_hash", hash_val)
    print("> successfully issued " + str(hash_val) + " on " + config.config["current_chain"])


def revoke(hash_val):
    '''Revokes a certficate by putting the certificate hash into smart contract revocation list'''
    print("> following hash gets revoked : " + str(hash_val))
    sc.functions.transact("revoke_hash", hash_val)
    print("> successfully revoked " + str(hash_val) + " on " + config.config["current_chain"])


def get_latest_contract():
    w3_factory = MakeW3()
    w3 = w3_factory.get_w3_obj()
    account = w3_factory.get_w3_wallet()
    ns = ENS.fromWeb3(w3, "0x112234455C3a32FD11230C42E7Bccd4A84e02010")

    name = ns.name(account.address)
    address = ns.address(name)
    print(address)
