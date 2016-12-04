import binascii
import collections
import glob
import hashlib
import json

import os
import shutil
import sys

import glob2

from cert_issuer.errors import NonemptyOutputDirectoryError

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    def unhexlify(hex_string): return binascii.unhexlify(hex_string.encode('utf8'))


    def hexlify(hex_bytes): return binascii.hexlify(hex_bytes).decode('utf8')

UNSIGNED_CERTIFICATES_DIR = 'unsigned_certificates'
SIGNED_CERTIFICATES_DIR = 'signed_certificates'
SIGNED_TXS_DIR = 'signed_txs'
UNSIGNED_TXS_DIR = 'unsigned_txs'
SENT_TXS_DIR = 'sent_txs'
RECEIPTS_DIR = 'receipts'
HASHED_CERTIFICATES_DIR = 'hashed_certificates'
BLOCKCHAIN_CERTIFICATES_DIR = 'blockchain_certificates'
JSON_EXT = '.json'
TXT_EXT = '.txt'


class CertificateMetadata(object):
    def __init__(self, uid, unsigned_certs_dir, signed_certs_dir):
        self.uid = uid
        self.unsigned_cert_file_name = os.path.join(unsigned_certs_dir, uid + JSON_EXT)
        self.signed_cert_file_name = os.path.join(signed_certs_dir, uid + JSON_EXT)


class ExtendedCertificateMetadata(CertificateMetadata):
    def __init__(self, uid, unsigned_certs_dir, signed_certs_dir, base_work_dir, public_key, revocation_key):
        CertificateMetadata.__init__(self, uid, unsigned_certs_dir, signed_certs_dir)
        self.base_work_dir = base_work_dir
        self.public_key = public_key
        self.revocation_key = revocation_key
        self.hashed_cert_file_name = convert_file_name(base_work_dir, HASHED_CERTIFICATES_DIR, uid, TXT_EXT)
        self.receipt_file_name = convert_file_name(base_work_dir, RECEIPTS_DIR, uid, JSON_EXT)
        self.blockchain_cert_file_name = convert_file_name(base_work_dir, BLOCKCHAIN_CERTIFICATES_DIR, uid, JSON_EXT)


class BatchMetadata(object):
    """
    Maintains batch-related metadata, including batch id and output paths
    """
    WORK_DIRS = [BLOCKCHAIN_CERTIFICATES_DIR, HASHED_CERTIFICATES_DIR, RECEIPTS_DIR, SENT_TXS_DIR, UNSIGNED_TXS_DIR,
                 SIGNED_TXS_DIR]

    def __init__(self, base_work_dir, batch_id):
        self.base_work_dir = base_work_dir
        self.batch_id = batch_id
        self.unsigned_tx_file_name = convert_file_name(base_work_dir, UNSIGNED_TXS_DIR, batch_id, TXT_EXT)
        self.unsent_tx_file_name = convert_file_name(base_work_dir, SIGNED_TXS_DIR, batch_id, TXT_EXT)
        self.sent_tx_file_name = convert_file_name(base_work_dir, SENT_TXS_DIR, batch_id, TXT_EXT)

    def ensure_output_dirs_exists(self):
        for d in self.WORK_DIRS:
            os.makedirs(os.path.join(self.base_work_dir, d), exist_ok=True)


def convert_file_name(base_dir, sub_dir, file_name, file_ext):
    return os.path.join(base_dir, sub_dir, file_name + file_ext)


def find_certificates_to_process(unsigned_certs_dir, signed_certs_dir):
    cert_info = collections.OrderedDict()
    input_file_pattern = str(os.path.join(unsigned_certs_dir, '*.json'))

    for filename, (uid,) in sorted(glob2.iglob(input_file_pattern, with_matches=True)):
        certificate_metadata = CertificateMetadata(uid, unsigned_certs_dir, signed_certs_dir)
        cert_info[uid] = certificate_metadata

    return cert_info


def prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir, work_dir):
    """
    Prepares file system for issuing a batch of certificates. Copies inputs to work_dir, and ensures
    that all output dirs required for processing the batch exist.
    :param unsigned_certs_dir:
    :param signed_certs_dir:
    :param work_dir:
    :return:
    """

    os.makedirs(work_dir, exist_ok=True)
    # ensure previous processing state, if any, is cleaned up
    for item in os.listdir(work_dir):
        file_path = os.path.join(work_dir, item)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    unsigned_certs_temp = os.path.join(work_dir, UNSIGNED_CERTIFICATES_DIR)
    signed_certs_temp = os.path.join(work_dir, SIGNED_CERTIFICATES_DIR)

    shutil.copytree(unsigned_certs_dir, unsigned_certs_temp)
    shutil.copytree(signed_certs_dir, signed_certs_temp)

    unsigned_certs_dir = unsigned_certs_temp
    signed_certs_dir = signed_certs_temp

    cert_info = collections.OrderedDict()
    input_file_pattern = str(os.path.join(signed_certs_dir, '*.json'))

    for filename, (uid,) in sorted(glob2.iglob(input_file_pattern, with_matches=True)):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            revocation_key = None
            if 'revocationKey' in cert_json['recipient']:
                revocation_key = cert_json['recipient']['revocationKey']

            certificate_metadata = ExtendedCertificateMetadata(uid=uid,
                                                               unsigned_certs_dir=unsigned_certs_dir,
                                                               signed_certs_dir=signed_certs_dir,
                                                               base_work_dir=work_dir,
                                                               public_key=cert_json['recipient']['publicKey'],
                                                               revocation_key=revocation_key)

            cert_info[uid] = certificate_metadata

    batch_id = get_batch_id(list(cert_info.keys()))
    batch_metadata = BatchMetadata(work_dir, batch_id)
    batch_metadata.ensure_output_dirs_exists()
    return cert_info, batch_metadata


def get_batch_id(uids):
    """
    Constructs a deterministic batch id from file names. The input uids are assumed to be sorted.
    Throughout this app we store certificates in OrderedDicts
    :param uids:
    :return:
    """
    return hashlib.md5(''.join(uids).encode('utf-8')).hexdigest()
