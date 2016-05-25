import bitcoin.rpc
import requests
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinAddress

if __name__ == "__main__":
    bitcoin.SelectParams('regtest')
    # btc_conf_file='bitcoin.conf'
    proxy = bitcoin.rpc.Proxy()
    result = proxy.listunspent()
    print(result)