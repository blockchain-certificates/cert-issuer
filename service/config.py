import bitcoin
import logging
import os

import configargparse

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def configure_logger():
    logging.basicConfig(level=logging.INFO,
                        format='(%(threadName)-10s) %(message)s',
                        )


def add_arguments(p):
    p.add_argument('--request_queue_name', required=True, env_var='REQUEST_QUEUE_NAME',
                   help='Name of issuing request queue')
    p.add_argument('--response_queue_name', required=True, env_var='RESPONSE_QUEUE_NAME',
                   help='Name of issuing response queue')
    p.add_argument('--issuer_s3_bucket', required=True, env_var='ISSUER_S3_BUCKET', help='S3 Bucket')
    p.add_argument('--aws_region', default='us-east-1', env_var='AWS_REGION', help='AWS Region')
    p.add_argument('--sqs-wait_timeout', required=False, default=10, env_var='SQS_WAIT_TIMEOUT',
                   help='SQS Wait timeout')
    p.add_argument('--issuer_wait_timeout', required=False, default=10, env_var='ISSUER_WAIT_TIMEOUT',
                   help='Issuer Wait timeout')
    p.add_argument('--work_dir', required=True, env_var='WORK_DIR', help='Base work dir')
    p.add_argument('--mock_aws', required=False, env_var='MOCK_AWS', action='store_true', help='whether to mock aws')
    p.add_argument('--create_queues', required=False, env_var='CREATE_QUEUES', action='store_true',
                   help='whether to create queues')
    p.add_argument('--upload_test_cert', required=False, env_var='UPLOAD_TEST_CERT', action='store_true',
                   help='whether to upload a test certificate')


def get_config():
    p = configargparse.getArgumentParser(default_config_files=[os.path.join(PATH, 'conf.ini'),
                                                               '/etc/cert-issuer/conf.ini'])
    add_arguments(p)
    from cert_issuer import config
    config.add_arguments(p)
    parsed_config, _ = p.parse_known_args()

    if parsed_config.wallet_connector_type == 'bitcoind':
        bitcoin.SelectParams(parsed_config.bitcoin_chain)
    if parsed_config.bitcoin_chain == 'mainnet':
        parsed_config.netcode = 'BTC'
    else:
        parsed_config.netcode = 'XTN'

    config.set_fee_per_trx(parsed_config.tx_fee)
    config.set_satoshi_per_byte(parsed_config.satoshi_per_byte)
    config.set_min_per_output(parsed_config.dust_threshold)

    configure_logger()

    return parsed_config
