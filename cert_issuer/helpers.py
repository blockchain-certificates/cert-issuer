import collections
import logging
import os
import shutil

import glob2
from cert_core import Chain, UnknownChainError
from pycoin.serialize import b2h, h2b

from cert_issuer.errors import NoCertificatesFoundError

unhexlify = h2b
hexlify = b2h

UNSIGNED_CERTIFICATES_DIR = 'unsigned_certificates'
SIGNED_CERTIFICATES_DIR = 'signed_certificates'
BLOCKCHAIN_CERTIFICATES_DIR = 'blockchain_certificates'
JSON_EXT = '.json'


class CertificateMetadata(object):
    def __init__(self, uid, unsigned_certs_dir, signed_certs_dir, blockcerts_dir, final_blockcerts_dir,
                 file_extension=JSON_EXT):
        self.uid = uid
        self.unsigned_cert_file_name = os.path.join(unsigned_certs_dir, uid + file_extension)
        if signed_certs_dir:
            self.signed_cert_file_name = os.path.join(signed_certs_dir, uid + file_extension)
        self.blockchain_cert_file_name = os.path.join(blockcerts_dir, uid + file_extension)
        self.final_blockchain_cert_file_name = os.path.join(final_blockcerts_dir, uid + file_extension)


def prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir, blockchain_certs_dir, work_dir,
                           file_extension=JSON_EXT):
    """
    Prepares file system for issuing a batch of certificates. Copies inputs to work_dir, and ensures
    that all output dirs required for processing the batch exist.
    :param unsigned_certs_dir: input certificates
    :param signed_certs_dir: output dir
    :param blockchain_certs_dir: output dir
    :param work_dir: work dir
    :return:
    """

    # create work dir if it doesn't already exist
    os.makedirs(work_dir, exist_ok=True)

    # create final output dirs if they don't already exist
    os.makedirs(blockchain_certs_dir, exist_ok=True)
    os.makedirs(signed_certs_dir, exist_ok=True)

    # ensure previous processing state, if any, is cleaned up
    for item in os.listdir(work_dir):
        file_path = os.path.join(work_dir, item)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    # define work subdirs
    unsigned_certs_work_dir = os.path.join(work_dir, UNSIGNED_CERTIFICATES_DIR)
    signed_certs_work_dir = os.path.join(work_dir, SIGNED_CERTIFICATES_DIR)
    blockchain_certs_work_dir = os.path.join(work_dir, BLOCKCHAIN_CERTIFICATES_DIR)

    # copy input certs to unsigned certs work subdir and create output subdirs
    shutil.copytree(unsigned_certs_dir, unsigned_certs_work_dir)
    os.makedirs(signed_certs_work_dir, exist_ok=True)
    os.makedirs(blockchain_certs_work_dir, exist_ok=True)

    cert_info = collections.OrderedDict()
    input_file_pattern = str(os.path.join(unsigned_certs_work_dir, '*' + file_extension))

    matches = glob2.iglob(input_file_pattern, with_matches=True)
    if not matches:
        logging.warning('No certificates to process')
        raise NoCertificatesFoundError('No certificates to process')

    # create certificate metadata for each certificates
    for filename, (uid,) in sorted(matches):
        certificate_metadata = CertificateMetadata(uid=uid,
                                                   unsigned_certs_dir=unsigned_certs_work_dir,
                                                   signed_certs_dir=signed_certs_work_dir,
                                                   blockcerts_dir=blockchain_certs_work_dir,
                                                   final_blockcerts_dir=blockchain_certs_dir,
                                                   file_extension=file_extension)
        cert_info[uid] = certificate_metadata

    logging.info('Processing %d certificates', len(cert_info))
    return cert_info


def copy_output(certificates_metadata):
    for _, metadata in certificates_metadata.items():
        from_file = metadata.blockchain_cert_file_name
        to_file = metadata.final_blockchain_cert_file_name
        shutil.copy2(from_file, to_file)


def to_pycoin_chain(chain):
    if chain == Chain.bitcoin_regtest or chain == Chain.bitcoin_testnet:
        return 'XTN'
    elif chain == Chain.bitcoin_mainnet:
        return 'BTC'
    else:
        raise UnknownChainError(chain.name)
