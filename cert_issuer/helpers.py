import binascii
import collections
import hashlib
import json
import shutil
import sys
from os import path, makedirs, pardir

import glob2

unhexlify = binascii.unhexlify
hexlify = binascii.hexlify
if sys.version > '3':
    def unhexlify(hex_string): return binascii.unhexlify(hex_string.encode('utf8'))


    def hexlify(hex_bytes): return binascii.hexlify(hex_bytes).decode('utf8')


class CertificateMetadata(object):
    def __init__(self, uid, unsigned_certs_dir, signed_certs_dir):
        self.uid = uid
        self.unsigned_cert_file_name = convert_file_name(path.join(unsigned_certs_dir, '*.json'), uid)
        self.signed_cert_file_name = convert_file_name(path.join(signed_certs_dir, '*.json'), uid)


class ExtendedCertificateMetadata(CertificateMetadata):
    def __init__(self, uid, unsigned_certs_dir, signed_certs_dir, base_work_dir, public_key, revocation_key):
        CertificateMetadata.__init__(self, uid, unsigned_certs_dir, signed_certs_dir)
        self.base_work_dir = base_work_dir
        self.public_key = public_key
        self.revocation_key = revocation_key
        self.hashed_cert_file_name = convert_file_name(path.join(base_work_dir, 'hashed_certificates/*.txt'), uid)
        self.receipt_file_name = convert_file_name(path.join(base_work_dir, 'receipts/*.json'), uid)
        self.blockchain_cert_file_name = convert_file_name(path.join(base_work_dir, 'blockchain_certificates/*.json'),
                                                           uid)


class BatchMetadata(object):
    """
    Maintains batch-related metadata, including batch id and output paths
    """
    WORK_DIRS = ['blockchain_certificates', 'hashed_certificates', 'receipts', 'sent_txs', 'unsigned_txs', 'signed_txs']

    def __init__(self, base_work_dir, batch_id):
        self.base_work_dir = base_work_dir
        self.batch_id = batch_id
        self.unsigned_tx_file_name = convert_file_name(path.join(base_work_dir, 'unsigned_txs/*.txt'), batch_id)
        self.unsent_tx_file_name = convert_file_name(path.join(base_work_dir, 'signed_txs/*.txt'), batch_id)
        self.sent_tx_file_name = convert_file_name(path.join(base_work_dir, 'sent_txs/*.txt'), batch_id)

    def ensure_output_dirs_exists(self):
        for d in self.WORK_DIRS:
            makedirs(path.join(self.base_work_dir, d), exist_ok=True)


def convert_file_name(to_pattern, cert_uid):
    return to_pattern.replace('*', cert_uid)


def find_certificates_to_process(unsigned_certs_dir, signed_certs_dir):
    cert_info = collections.OrderedDict()
    input_file_pattern = str(path.join(unsigned_certs_dir, '*.json'))

    for filename, (uid,) in sorted(glob2.iglob(input_file_pattern, with_matches=True)):
        certificate_metadata = CertificateMetadata(uid, unsigned_certs_dir, signed_certs_dir)
        cert_info[uid] = certificate_metadata

    return cert_info


def prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir, work_dir):
    """
    Prepares file system for issuing a batch of certificates. If work_dir isn't the parent
    dir of unsigned/signed certs, this copies the certs over to subdirs under work_dir. Ensures
    that all output dirs required for processing the batch exist.
    :param unsigned_certs_dir:
    :param signed_certs_dir:
    :param work_dir:
    :return:
    """
    # determine if we need to copy to work_dir
    par_dir = path.abspath(path.join(unsigned_certs_dir, pardir))
    work_dir = path.abspath(work_dir)

    # If work dir is separate, ensure it exists and copy over certificates
    if work_dir != par_dir:
        makedirs(work_dir, exist_ok=True)
        unsigned_certs_temp = path.join(work_dir, 'unsigned_certificates')
        signed_certs_temp = path.join(work_dir, 'signed_certificates')

        shutil.copytree(unsigned_certs_dir, unsigned_certs_temp)
        shutil.copytree(signed_certs_dir, signed_certs_temp)

        unsigned_certs_dir = unsigned_certs_temp
        signed_certs_dir = signed_certs_temp

    cert_info = collections.OrderedDict()
    input_file_pattern = str(path.join(signed_certs_dir, '*.json'))

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


def archive_files(work_dir, archive_dir):
    """
    Archive files by moving from work_dir to archive_dir
    :param work_dir:
    :param archive_dir:
    :return:
    """
    shutil.move(work_dir, archive_dir)


def get_batch_id(uids):
    """
    Constructs a deterministic batch id from file names. The input uids are assumed to be sorted.
    Throughout this app we store certificates in OrderedDicts
    :param uids:
    :return:
    """
    return hashlib.md5(''.join(uids).encode('utf-8')).hexdigest()
