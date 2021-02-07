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
CONFIG = None


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
    p.add_argument('--issuing_address', required=True, help='issuing address', env_var='ISSUING_ADDRESS')
    p.add_argument('--usb_name', required=True, help='usb path to key_file', env_var='USB_NAME')
    p.add_argument('--key_file', required=True,
                   help='name of file on USB containing private key', env_var='KEY_FILE')
    p.add_argument('--unsigned_certificates_dir', default=os.path.join(DATA_PATH, 'unsigned_certificates'),
                   help='Default path to data directory storing unsigned certs', env_var='UNSIGNED_CERTIFICATES_DIR')
    p.add_argument('--signed_certificates_dir', default=os.path.join(DATA_PATH, 'signed_certificates'),
                   help='Default path to data directory storing signed certs', env_var='SIGNED_CERTIFICATES_DIR')
    p.add_argument('--blockchain_certificates_dir', default=os.path.join(DATA_PATH, 'blockchain_certificates'),
                   help='Default path to data directory storing blockchain certs', env_var='BLOCKCHAIN_CERTIFICATES_DIR')
    p.add_argument('--work_dir', default=WORK_PATH,
                   help='Default path to work directory, storing intermediate outputs. This gets deleted in between runs.', env_var='WORK_DIR')
    p.add_argument('--max_retry', default=10, type=int, help='Maximum attempts to retry transaction on failure', env_var='MAX_RETRY')
    p.add_argument('--chain', default='bitcoin_regtest',
                   help=('Which chain to use. Default is bitcoin_regtest (which is how the docker container is configured). Other options are '
                         'bitcoin_testnet bitcoin_mainnet, mockchain, ethereum_mainnet, ethereum_ropsten'), env_var='CHAIN')

    p.add_argument('--safe_mode', dest='safe_mode', default=True, action='store_true',
                   help='Used to make sure your private key is not plugged in with the wifi.', env_var='SAFE_MODE')
    p.add_argument('--no_safe_mode', dest='safe_mode', default=False, action='store_false',
                   help='Turns off safe mode. Only change this option for testing or unit testing.', env_var='NO_SAFE_MODE')
    # bitcoin arguments
    p.add_argument('--dust_threshold', default=0.0000275, type=float,
                   help='blockchain dust threshold (in BTC) -- below this 1/3 is fees.', env_var='DUST_THRESHOLD')
    p.add_argument('--tx_fee', default=0.0006, type=float,
                   help='recommended tx fee (in BTC) for inclusion in next block. http://bitcoinexchangerate.org/fees', env_var='TX_FEE')
    p.add_argument('--batch_size', default=10, type=int,
                   help='Certificate batch size', env_var='BATCH_SIZE')
    p.add_argument('--satoshi_per_byte', default=250,
                   type=int, help='Satoshi per byte', env_var='SATOSHI_PER_BYTE')
    p.add_argument('--bitcoind', dest='bitcoind', default=False, action='store_true',
                   help='Use bitcoind connectors.', env_var='BITCOIND')
    p.add_argument('--no_bitcoind', dest='bitcoind', default=True, action='store_false',
                   help='Default; do not use bitcoind connectors; use APIs instead', env_var='NO_BITCOIND')
    # ethereum arguments
    p.add_argument('--gas_price', default=20000000000, type=int,
                   help='decide the price per gas spent (in wei (smallest ETH unit))', env_var='GAS_PRICE')
    p.add_argument('--gas_limit', default=25000, type=int,
                   help='decide on the maximum spendable gas. gas_limit < 25000 might not be sufficient', env_var='GAS_LIMIT')
    p.add_argument('--etherscan_api_token', default=None, type=str,
                   help='The API token of the Etherscan broadcaster', env_var='ETHERSCAN_API_TOKEN')
    p.add_argument('--ethereum_rpc_url', default=None, type=str,
                   help='The URL of an Ethereum main net RPC node - useful in the case of third-party full node vendors.',
                   env_var='ETHEREUM_RPC_URL')
    p.add_argument('--ropsten_rpc_url', default=None, type=str,
                   help='The URL of an Ethereum Ropsten RPC node - useful in the case of third-party full node vendors.',
                   env_var='ROPSTEN_RPC_URL')

    p.add_argument('--blockcypher_api_token', default=None, type=str,
                   help='the API token of the blockcypher broadcaster', env_var='BLOCKCYPHER_API_TOKEN')


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

    global CONFIG
    CONFIG = parsed_config
    return parsed_config
