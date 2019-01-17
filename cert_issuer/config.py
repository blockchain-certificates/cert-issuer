import logging
import os

import bitcoin
import configargparse
from cert_core import BlockchainType, Chain, chain_to_bitcoin_network, UnknownChainError

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PATH, 'data')
WORK_PATH = os.path.join(PATH, 'work')

# Estimate fees assuming worst case 3 inputs
ESTIMATE_NUM_INPUTS = 3

# Estimate fees assuming 1 output for change.
# Note that tx_utils calculations add on cost due to OP_RETURN size, so it doesn't need to be added here.
V2_NUM_OUTPUTS = 1


def configure_logger():
    # Configure logging settings; create console handler and set level to info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# restructured arguments to put the chain specific arguments together.
def add_arguments(p):
    p.add('-c', '--my-config', required=False, env_var='CONFIG_FILE',
          is_config_file=True, help='config file path')
    p.add_argument('--issuing_address', required=True, help='issuing address')
    p.add_argument('--usb_name', required=True, help='usb path to key_file')
    p.add_argument('--key_file', required=True,
                   help='name of file on USB containing private key')
    p.add_argument('--unsigned_certificates_dir', default=os.path.join(DATA_PATH, 'unsigned_certificates'),
                   help='Default path to data directory storing unsigned certs')
    p.add_argument('--signed_certificates_dir', default=os.path.join(DATA_PATH, 'signed_certificates'),
                   help='Default path to data directory storing signed certs')
    p.add_argument('--blockchain_certificates_dir', default=os.path.join(DATA_PATH, 'blockchain_certificates'),
                   help='Default path to data directory storing blockchain certs')
    p.add_argument('--work_dir', default=WORK_PATH,
                   help='Default path to work directory, storing intermediate outputs. This gets deleted in between runs.')
    p.add_argument('--max_retry', default=10, type=int, help='Maximum attempts to retry transaction on failure')
    p.add_argument('--chain', default='bitcoin_regtest',
                   help='Which chain to use. Default is bitcoin_regtest (which is how the docker container is configured). Other options are bitcoin_testnet bitcoin_mainnet, mockchain, ethereum_mainnet, ethereum_ropsten')

    p.add_argument('--safe_mode', dest='safe_mode', default=True, action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi.')
    p.add_argument('--no_safe_mode', dest='safe_mode', default=False, action='store_false',
                   help='Turns off safe mode. Only change this option for testing or unit testing.')
    # bitcoin arguments
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees.')
    p.add_argument('--tx_fee', default=0.0006, type=float,
                   help='recommended tx fee (in BTC) for inclusion in next block. http://bitcoinexchangerate.org/fees')
    p.add_argument('--batch_size', default=10, type=int,
                   help='Certificate batch size')
    p.add_argument('--satoshi_per_byte', default=250,
                   type=int, help='Satoshi per byte')
    p.add_argument('--bitcoind', dest='bitcoind', default=False, action='store_true',
                   help='Use bitcoind connectors.')
    p.add_argument('--no_bitcoind', dest='bitcoind', default=True, action='store_false',
                   help='Default; do not use bitcoind connectors; use APIs instead')
    # ethereum arguments
    p.add_argument('--gas_price', default=20000000000, type=int,
                   help='decide the price per gas spent (in wei (smallest ETH unit))')
    p.add_argument('--gas_limit', default=25000, type=int,
                   help='decide on the maximum spendable gas. gas_limit < 25000 might not be sufficient')
    p.add_argument('--api_token', default=None, type=str,
                   help='the API token of the blockchain broadcaster you are using. Currently Etherscan only supported.')


def get_config():
    configure_logger()
    p = configargparse.getArgumentParser(default_config_files=[os.path.join(PATH, 'conf.ini'),
                                                               '/etc/cert-issuer/conf.ini'])
    add_arguments(p)
    parsed_config, _ = p.parse_known_args()

    if not parsed_config.safe_mode:
        logging.warning('Your app is configured to skip the wifi check when the USB is plugged in. Read the '
                        'documentation to ensure this is what you want, since this is less secure')

    # overwrite with enum
    parsed_config.chain = Chain.parse_from_chain(parsed_config.chain)

    # ensure it's a supported chain
    if parsed_config.chain.blockchain_type != BlockchainType.bitcoin and \
                    parsed_config.chain.blockchain_type != BlockchainType.ethereum and \
                    parsed_config.chain.blockchain_type != BlockchainType.mock:
        raise UnknownChainError(parsed_config.chain.name)

    logging.info('This run will try to issue on the %s chain', parsed_config.chain.name)

    if parsed_config.chain.blockchain_type == BlockchainType.bitcoin:
        bitcoin_chain_for_python_bitcoinlib = parsed_config.chain
        if parsed_config.chain == Chain.bitcoin_regtest:
            bitcoin_chain_for_python_bitcoinlib = Chain.bitcoin_regtest
        bitcoin.SelectParams(chain_to_bitcoin_network(bitcoin_chain_for_python_bitcoinlib))

    return parsed_config
