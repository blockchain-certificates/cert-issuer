import configargparse
import os

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(PATH, 'conf.ini')

def parse_args():
    print(DEFAULT_CONFIG)
    p = configargparse.getArgumentParser(default_config_files=[DEFAULT_CONFIG, '/etc/issuer/conf.ini'])
    p.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    p.add_argument('--issuing_address', required=True, help='issuing address')
    p.add_argument('--revocation_address', required=True, help='revocation address')
    p.add_argument('--usb_name', required=True, help='usb path to key_file')
    p.add_argument('--key_file', required=True, help='name of file on USB containing private key')
    p.add_argument('--wallet_connector_type', default='bitcoind', help='connector to use for wallet')
    p.add_argument('--broadcaster_type', default='bitcoind', help='connector to use for broadcast')
    p.add_argument('--disable_regtest_mode', action='store_true',
                   help='Use regtest mode of bitcoind (default: 0). Warning! Only change this if you have a local '
                        'bitcoind client (not the included Docker container) and you are sure you want to spend money. '
                        'Our included docker container is configured to run only in regtest mode.')
    p.add_argument('--storage_address', required=False, help='storage address. Not needed for bitcoind deployment')
    p.add_argument('--wallet_guid', required=False, help='wallet guid. Not needed for bitcoind deployment')
    p.add_argument('--wallet_password', required=False, help='wallet password. Not needed for bitcoind deployment')
    p.add_argument('--api_key', required=False, help='api key. Not needed for bitcoind deployment')
    p.add_argument('--transfer_from_storage_address', action='store_true',
                   help='Transfer BTC from storage to issuing address (default: 0). Advanced usage')
    p.add_argument('--skip_sign', action='store_true',
                   help='Sign certificates in unsigned_certs folder (default: 0). Only change this option for troubleshooting.')
    p.add_argument('--skip_wifi_check', action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi on (default: False). Only change this option for troubleshooting.')
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees.')
    p.add_argument('--tx_fees', default=0.0001, type=float,
                   help='recommended tx fee (in BTC) for inclusion in next block. http://bitcoinexchangerate.org/fees')
    p.add_argument('--batch_size', default=10, type=int, help='Certificate batch size')
    p.add_argument('--satoshi_per_byte', default=41, type=int, help='Satoshi per byte')
    p.add_argument('--unsigned_certs_file_pattern', default='../data/unsigned_certs/*.json',
                   help='unsigned certs file pattern')
    p.add_argument('--signed_certs_file_pattern', default='../data/signed_certs/*.json', help='signed certs file pattern')
    p.add_argument('--hashed_certs_file_pattern', default='../data/hashed_certs/*.txt', help='hashed certs file pattern')
    p.add_argument('--unsigned_txs_file_pattern', default='../data/unsigned_txs/*.txt', help='unsigned txs file pattern')
    p.add_argument('--unsent_txs_file_pattern', default='../data/unsent_txs/*.txt', help='unsent txs file pattern')
    p.add_argument('--sent_txs_file_pattern', default='../data/sent_txs/*.txt', help='sent txs file pattern')
    p.add_argument('--archived_certs_file_pattern', default='../archive/certs/*.json', help='archive certs file pattern')
    p.add_argument('--archived_txs_file_pattern', default='../archive/txs/*.txt', help='archive txs file pattern')

    return p.parse_known_args()
