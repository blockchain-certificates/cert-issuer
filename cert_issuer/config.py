import logging
import os

import bitcoin
import configargparse

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PATH, 'data')

RECOMMENDED_FEE_PER_TRANSACTION = None
MIN_PER_OUTPUT = None
SATOSHI_PER_BYTE = None


def configure_logger():
    # Configure logging settings; create console handler and set level to info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def add_arguments(p):
    p.add('-c', '--my-config', required=False, env_var='CONFIG_FILE',
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
                   help='Which bitcoin chain to use. Default is regtest (which is how the docker container is '
                        'configured). Other options are testnet and mainnet.')
    p.add_argument('--storage_address', required=False,
                   help='storage address. Not needed for bitcoind deployment')
    p.add_argument('--wallet_guid', required=False,
                   help='wallet guid. Not needed for bitcoind deployment')
    p.add_argument('--wallet_password', required=False,
                   help='wallet password. Not needed for bitcoind deployment')
    p.add_argument('--api_key', required=False,
                   help='api key. Not needed for bitcoind deployment')
    p.add_argument('--transfer_from_storage_address', dest='transfer_from_storage_address', action='store_true',
                   help='Transfer BTC from storage to issuing address.')
    p.add_argument('--no_transfer_from_storage_address', dest='transfer_from_storage_address', action='store_false',
                   help='Prevent transfer BTC from storage to issuing address.')
    p.add_argument('--safe_mode', dest='safe_mode', action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi.')
    p.add_argument('--no_safe_mode', dest='safe_mode', action='store_false',
                   help='Turns off safe mode. Only change this option for testing or unit testing.')
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees.')
    p.add_argument('--tx_fee', default=0.0001, type=float,
                   help='recommended tx fee (in BTC) for inclusion in next block. http://bitcoinexchangerate.org/fees')
    p.add_argument('--batch_size', default=10, type=int,
                   help='Certificate batch size')
    p.add_argument('--satoshi_per_byte', default=41,
                   type=int, help='Satoshi per byte')
    p.add_argument('--unsigned_certificates_dir', default=os.path.join(DATA_PATH, 'unsigned_certificates'),
                   help='Default path to data directory storing unsigned certs')
    p.add_argument('--signed_certificates_dir', default=os.path.join(DATA_PATH, 'signed_certificates'),
                   help='Default path to data directory storing signed certs')
    p.add_argument('--blockchain_certificates_dir', default=os.path.join(DATA_PATH, 'blockchain_certificates'),
                   help='Default path to data directory storing blockchain certs')
    p.add_argument('--work_dir', default=DATA_PATH,
                   help='Default path to data directory, storing unsigned certs')


def get_config():
    p = configargparse.getArgumentParser(default_config_files=[os.path.join(PATH, 'conf.ini'),
                                                               '/etc/cert-issuer/conf.ini'])
    add_arguments(p)
    parsed_config, _ = p.parse_known_args()

    if not parsed_config.safe_mode:
        logging.warning('Your app is configured to skip the wifi check when the USB is plugged in. Read the '
                        'documentation to ensure this is what you want, since this is less secure')
    if parsed_config.wallet_connector_type == 'bitcoind':
        bitcoin.SelectParams(parsed_config.bitcoin_chain)
    if parsed_config.bitcoin_chain == 'mainnet':
        parsed_config.netcode = 'BTC'
    else:
        parsed_config.netcode = 'XTN'

    configure_logger()

    set_fee_per_trx(parsed_config.tx_fee)
    set_satoshi_per_byte(parsed_config.satoshi_per_byte)
    set_min_per_output(parsed_config.dust_threshold)

    return parsed_config


def set_fee_per_trx(recommended_fee_per_transaction):
    global RECOMMENDED_FEE_PER_TRANSACTION
    RECOMMENDED_FEE_PER_TRANSACTION = recommended_fee_per_transaction


def get_fee_per_trx():
    global RECOMMENDED_FEE_PER_TRANSACTION
    if not RECOMMENDED_FEE_PER_TRANSACTION:
        RECOMMENDED_FEE_PER_TRANSACTION = 0.0001
    return RECOMMENDED_FEE_PER_TRANSACTION


def set_satoshi_per_byte(satoshi_per_byte):
    global SATOSHI_PER_BYTE
    SATOSHI_PER_BYTE = satoshi_per_byte


def get_satoshi_per_byte():
    global SATOSHI_PER_BYTE
    if not SATOSHI_PER_BYTE:
        SATOSHI_PER_BYTE = 41
    return SATOSHI_PER_BYTE


def set_min_per_output(min_per_output):
    global MIN_PER_OUTPUT
    MIN_PER_OUTPUT = min_per_output


def get_min_per_output():
    global MIN_PER_OUTPUT
    if not MIN_PER_OUTPUT:
        MIN_PER_OUTPUT = 0.0000275
    return MIN_PER_OUTPUT
