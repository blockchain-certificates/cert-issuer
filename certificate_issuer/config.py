import os

import configargparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DEFAULT_CONFIG_FILE = os.path.join(BASE_DIR, 'conf.ini')


def parse_args():
    p = configargparse.getArgumentParser(default_config_files=[DEFAULT_CONFIG_FILE])
    p.add_argument('--wallet_guid', required=False, help='wallet guid; todo: make required')
    p.add_argument('--wallet_password', required=False, help='wallet password; todo: make required')
    p.add_argument('--api_key', required=False, help='api key; todo: make required')
    p.add_argument('--issuing_address', required=False, help='issuing address; todo: make required')
    p.add_argument('--storage_address', required=False, help='storage address; todo: make required')
    p.add_argument('--revocation_address', required=False, help='revocation address; todo: make required')
    p.add_argument('--usb_name', required=False, help='usb name; todo: make required')
    p.add_argument('--key_file', required=False, help='key file; todo: make required')
    p.add_argument('--transfer_from_storage_address', action='store_false',
                   help='Transfer BTC from storage to issuing address (default: 1). Only change this option for troubleshooting.')
    p.add_argument('--sign_certificates', action='store_false',
                   help='Sign certificates in unsigned_certs folder (default: 1). Only change this option for troubleshooting.')
    p.add_argument('--broadcast', action='store_false',
                   help='Broadcast transactions (default: 1). Only change this option for troubleshooting.')
    p.add_argument('--skip_wifi_check', action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi on (default: False). Only change this option for troubleshooting.')
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees. TODO: we may need to raise this for # outputs')
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

    p.add_argument('--wallet_connector_type', default='blockchain.info', help='connector to use for wallet')
    p.add_argument('--broadcaster_type', default='btc.blockr.io', help='connector to use for broadcast')

    return p.parse_known_args()


def _get_config():
    parsed_config, _ = parse_args()
    return parsed_config


CONFIG = _get_config()
