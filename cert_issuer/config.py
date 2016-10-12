import logging
import os

import bitcoin
import configargparse

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PATH, 'data')
ARCHIVE_PATH = os.path.join(PATH, 'archive')


def parse_args():
    p = configargparse.getArgumentParser(default_config_files=[os.path.join(PATH, 'conf_regtest.ini'),
                                                               os.path.join(PATH, 'conf.ini'),
                                                               '/etc/cert-issuer/conf.ini'])
    p.add('-c', '--my-config', required=False,
          is_config_file=True, help='config file path')
    p.add_argument('--issuing_address', required=True, help='issuing address')
    p.add_argument('--revocation_address', required=True,
                   help='revocation address')
    p.add_argument('--usb_name', required=True, help='usb path to key_file')
    p.add_argument('--key_file', required=True,
                   help='name of file on USB containing private key')
    p.add_argument('--wallet_connector_type', default='bitcoind',
                   help='connector to use for wallet')
    p.add_argument('--broadcaster_type', default='bitcoind',
                   help='connector to use for broadcast')
    p.add_argument('--bitcoin_chain', default='regtest',
                   help='Which bitcoin chain to use. Default is regtest (which is how the docker container is configured). Other options are testnet and mainnet.')
    p.add_argument('--storage_address', required=False,
                   help='storage address. Not needed for bitcoind deployment')
    p.add_argument('--wallet_guid', required=False,
                   help='wallet guid. Not needed for bitcoind deployment')
    p.add_argument('--wallet_password', required=False,
                   help='wallet password. Not needed for bitcoind deployment')
    p.add_argument('--api_key', required=False,
                   help='api key. Not needed for bitcoind deployment')
    p.add_argument('--transfer_from_storage_address', action='store_true',
                   help='Transfer BTC from storage to issuing address (default: 0). Advanced usage')
    p.add_argument('--skip_wifi_check', action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi on (default: False). '
                        'Only change this option for troubleshooting.')
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees.')
    p.add_argument('--tx_fee', default=0.0001, type=float,
                   help='recommended tx fee (in BTC) for inclusion in next block. http://bitcoinexchangerate.org/fees')
    p.add_argument('--batch_size', default=10, type=int,
                   help='Certificate batch size')
    p.add_argument('--satoshi_per_byte', default=41,
                   type=int, help='Satoshi per byte')
    p.add_argument('--data_path', default=DATA_PATH,
                   help='Default path to data directory, storing unsigned certs')
    p.add_argument('--archive_path', default=ARCHIVE_PATH,
                   help='Default path to data directory, storing issued certs')
    return p.parse_known_args()


def configure_logger():
    # Configure logging settings; create console handler and set level to info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


parsed_config = None


def get_config():
    global parsed_config
    if parsed_config:
        return parsed_config
    parsed_config, _ = parse_args()

    # populate data and archive subdirs

    parsed_config.unsigned_certs_file_part = 'unsigned_certs/*.json'
    parsed_config.signed_certs_file_part = 'signed_certs/*.json'
    parsed_config.txs_file_part = 'sent_txs/*.txt'
    parsed_config.receipts_file_part = 'receipts/*.json'
    parsed_config.blockchain_certificates_file_part = 'blockchain_certificates/*.json'
    parsed_config.unsigned_certs_file_pattern = str(
        os.path.join(parsed_config.data_path, parsed_config.unsigned_certs_file_part))
    parsed_config.signed_certs_file_pattern = os.path.join(
        parsed_config.data_path, parsed_config.signed_certs_file_part)
    parsed_config.hashed_certs_file_pattern = os.path.join(
        parsed_config.data_path, 'hashed_certs/*.txt')
    parsed_config.unsigned_txs_file_pattern = os.path.join(
        parsed_config.data_path, 'unsigned_txs/*.txt')
    parsed_config.signed_txs_file_pattern = os.path.join(
        parsed_config.data_path, 'signed_txs/*.txt')
    parsed_config.sent_txs_file_pattern = os.path.join(
        parsed_config.data_path, parsed_config.txs_file_part)
    parsed_config.receipts_file_pattern = os.path.join(
        parsed_config.data_path, parsed_config.receipts_file_part)
    parsed_config.blockchain_certificates_file_pattern = os.path.join(
        parsed_config.data_path, parsed_config.blockchain_certificates_file_part)
    parsed_config.tree_file_pattern = os.path.join(
        parsed_config.data_path, 'tree/*.json')

    if parsed_config.skip_wifi_check:
        logging.warning('Your app is configured to skip the wifi check when the USB is plugged in. Read the '
                        'documentation to ensure this is what you want, since this is less secure')

    parsed_config.allowable_wif_prefixes = None
    if parsed_config.wallet_connector_type == 'bitcoind':
        bitcoin.SelectParams(parsed_config.bitcoin_chain)
        if parsed_config.bitcoin_chain == 'testnet':
            parsed_config.allowable_wif_prefixes = [b'\x80', b'\xef']

    configure_logger()

    return parsed_config
