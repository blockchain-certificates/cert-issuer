#!/usr/bin/env python3
"""
Directory structure
-------------------
Proposing a convention for the issuance batch's file inputs/outputs/intermediate state, in which they are grouped
together in an S3 location specified by an input issuanceBatchId, specified in the queue message.

  s3://bucketname/path/to/{issuanceBatchId}  <-- base path
  s3://bucketname/path/to/{issuanceBatchId}/unsigned_certificates  <-- unsigned certificates go here

On the issuer side, each issuing attempt will group its outputs according to a uid (or simple numbered attempt),

  s3://bucketname/path/to/{issuanceBatchId}/{issueAttemptUid}/signed_certificates
                                                             /blockchain_certificates
                                                             /{other intermediate files}
                                                             /logs

If successful, the final blockchain certificates will be copied to the following S3 path. This path is determined by
convention, but will also be included in the completion message

  s3://bucketname/path/to/{issuanceBatchId}/blockchain_certificates


Queue message structure
-----------------------
{
  'issuanceBatchId': 'Issuance batch id',
  's3BasePath': 's3://bucketname/path/to/issuanceBatchId; note that we could omit issuanceBatchId by convention',
  's3UnsignedCertificatesPath': 's3://bucketname/path/to/issuanceBatchId/unsigned_certificates; last 2 path elements can be omitted by convention',
  'chain': 'mainnet|testnet|regex',

  'customerId': 'Learning Machine customer id, used to lookup customer wallet login info, issuance key, revocation key',
  'issuerKey': 'issuer's issuing bitcoin address; TBD ',
  'revocationKey: 'issuer's revocation bitcoin address; TBD',
}

- S3 base path (assumes specific naming structure; else define paths individually)
  - unsigned certificates (assumes complete, including recipient-specific revocation key)
- Customer wallet info
  - api key
  - wallet guid
  - password, 2nd password
- Customer issuing key
- Customer revocation key
- Which network (mainnet, testnet, regex)

"""

# TODOs:
# 1. For multithreading, need sessions. Do this in issue_certs
#    https://geekpete.com/blog/multithreading-boto3/
#    session = boto3.session.Session()
#    s3 = session.resource('s3')
# 2. eventually we should make this more robust to failure. redis or other work in progress queue


import json
import logging
import shutil
import threading
from os import path, makedirs, listdir

import boto3
from boto3.s3.transfer import S3Transfer, TransferConfig

from cert_issuer import sign_certificates, issue_certificates
from cert_issuer.errors import InsufficientFundsError, NoCertificatesFoundError
from service import test_helpers
from service.models import IssuingState, IssuingRequest

PATH = path.dirname(path.dirname(path.abspath(__file__)))


events = dict()


def upload_results(s3, bucket, batch_dir, s3_path):
    for d in listdir(batch_dir):
        dir_to_upload = path.join(batch_dir, d)
        for f in listdir(dir_to_upload):
            file_path = path.join(dir_to_upload, f)
            dest_path = path.join(s3_path, d, f)
            s3.upload_file(file_path, bucket, dest_path)


def download_unsigned_certificates(s3, bucket, prefix, unsigned_certs_dir):

    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,
        max_concurrency=10,
        num_download_attempts=10,
    )
    transfer = S3Transfer(s3, config)

    response = s3.list_objects(
        Bucket=bucket,
        Delimiter='//',
        Prefix=prefix,
    )
    if not 'Contents' in response:
        raise NoCertificatesFoundError('No unsigned certificates to process')

    for s3_key in response['Contents']:
        s3_object = s3_key['Key']
        if not s3_object.endswith("/"):
            file_name = path.basename(s3_object)
            dest = path.join(unsigned_certs_dir, file_name)
            logging.info('Copying unsigned certificate=%s to dest=%s', file_name, dest)
            transfer.download_file(bucket, s3_object, dest)



def issue_certs_mock(s3, bucket, e, issuance_request, work_dir):
    issuance_batch_id_temp = issuance_request.batch_id
    makedirs(work_dir, exist_ok=True)

    batch_dir = path.join(work_dir, issuance_batch_id_temp)

    test_block_cert = path.join(PATH, 'service', 'blockcert', '1270b079-17c6-4fc3-8bd3-4d4281181f15.json')

    dest = path.join(batch_dir, 'blockchain_certificates', '1270b079-17c6-4fc3-8bd3-4d4281181f15.json')

    shutil.copyfile(test_block_cert, dest)

    issuance_request.state = IssuingState.uploading_results

    upload_results(s3, bucket, batch_dir, issuance_request.s3_base)

    issuance_request.state = IssuingState.succeeded
    e.set()
    logging.info('Finished')


def issue_certs(app_config, s3, bucket, e, issuance_request, work_dir):
    issuance_batch_id_temp = issuance_request.batch_id
    batch_dir = path.join(work_dir, issuance_batch_id_temp)
    logging.info('Issuing certificates for batch=%s, batch dir=%s', issuance_batch_id_temp, batch_dir)

    unsigned_certs_dir = path.join(batch_dir, 'unsigned_certificates')
    signed_certificates_dir = path.join(batch_dir, 'signed_certificates')
    blockchain_certificates_dir = path.join(batch_dir, 'blockchain_certificates')

    makedirs(work_dir, exist_ok=True)
    makedirs(batch_dir, exist_ok=True)
    makedirs(unsigned_certs_dir, exist_ok=True)
    try:
        app_config.work_dir = batch_dir
        app_config.unsigned_certificates_dir = unsigned_certs_dir
        app_config.signed_certificates_dir = signed_certificates_dir
        app_config.blockchain_certificates_dir = blockchain_certificates_dir

        download_unsigned_certificates(s3, bucket, issuance_request.s3_base, unsigned_certs_dir)

        logging.info('issuing address is %s', app_config.issuing_address)
        logging.info('usb name is %s', app_config.usb_name)

        issuance_request.state = IssuingState.signing_certs
        sign_certificates.main(app_config)

        issuance_request.state = IssuingState.issuing_certs
        issue_certificates.main(app_config)

        upload_results(s3, bucket, batch_dir, issuance_request.s3_base)
        issuance_request.state = IssuingState.uploading_results
        issuance_request.state = IssuingState.succeeded

    except NoCertificatesFoundError as cnf:
        logging.error(cnf, exc_info=True)
        issuance_request.state = IssuingState.failed
        issuance_request.failure_reason = 'Unsigned certificates were not found'
    except InsufficientFundsError as ife:
        logging.error(ife, exc_info=True)
        issuance_request.state = IssuingState.failed
        issuance_request.failure_reason = 'Insufficient funds at issuer address'
    except Exception as ex:
        logging.error(ex, exc_info=True)
        issuance_request.state = IssuingState.failed
        issuance_request.failure_reason = str(ex)
    finally:
        e.set()
        logging.info('Finished')


def main(args=None):
    import os

    from service import config
    app_config = config.get_config()

    mock_aws = app_config.mock_aws
    create_queues = app_config.create_queues
    test_data = app_config.upload_test_cert
    if mock_aws:
        from moto import mock_s3, mock_sqs
        moto1 = mock_s3()
        moto2 = mock_sqs()
        moto1.start()
        moto2.start()

    sqs = boto3.resource('sqs', region_name=app_config.aws_region)
    if create_queues:
        test_helpers.create_test_queue(sqs, app_config.request_queue_name, app_config.response_queue_name)

    request_queue = sqs.get_queue_by_name(QueueName=app_config.request_queue_name)
    response_queue = sqs.get_queue_by_name(QueueName=app_config.response_queue_name)

    s3_client = boto3.client('s3', region_name=app_config.aws_region)

    bucket_name = app_config.issuer_s3_bucket
    sqs_wait_timeout = int(app_config.sqs_wait_timeout)
    issuer_wait_timeout = int(app_config.issuer_wait_timeout)
    work_dir = app_config.work_dir
    test_cert = path.join(PATH, 'service', 'unsigned', '1270b079-17c6-4fc3-8bd3-4d4281181f15.json')

    if create_queues:
        s3_client.create_bucket(Bucket=bucket_name)

    while True:
        for message in request_queue.receive_messages(MessageAttributeNames=['Author'],
                                                      WaitTimeSeconds=sqs_wait_timeout):
            if message:
                try:
                    issuance_request = json.loads(message.body)
                    issuance_batch_id = issuance_request['issuanceBatchUid']
                    s3_base = issuance_request['s3BasePath']
                    chain = issuance_request['chain']
                except KeyError as ke:
                    logging.error('Missing key')
                    logging.error(ke, exc_info=True)
                    continue
                except Exception as e:
                    logging.error('Error parsing request')
                    logging.error(e, exc_info=True)
                    continue

                if test_data:
                    logging.info('uploading a test certificate')
                    test_helpers.upload_test_cert(s3_client, bucket_name, issuance_request['s3BasePath'], 'unsigned_certificates', test_cert)

                e = threading.Event()

                s = IssuingRequest(batch_id=issuance_batch_id,
                                   s3_base=s3_base,
                                   chain=chain)
                t = threading.Thread(name='issuerBatch' + issuance_batch_id,
                                     target=issue_certs,
                                     args=(app_config, s3_client, bucket_name, e, s, work_dir))
                events[e] = s
                t.start()
                message.delete()
                logging.info("Produced %s", issuance_batch_id)

        events_to_remove = []
        for e, s in events.items():
            logging.debug('wait_for_event_timeout starting')
            event_is_set = e.wait(issuer_wait_timeout)
            logging.info('event set: %s', event_is_set)
            if event_is_set:
                logging.info('processed event')
                message_body = {
                    'issuanceBatchUid': s.batch_id,
                    'state': s.state.name
                }
                if s.state == IssuingState.succeeded:
                    message_body['blockchainCertificates'] = path.join(s.s3_base, 'blockchain_certificates')
                elif s.state == IssuingState.failed:
                    message_body['failureReason'] = s.failure_reason
                else:
                    message_body['failureReason'] = 'last known state was unexpected'

                response_queue.send_message(MessageBody=json.dumps(message_body))
                logging.info('Sent message to response queue')
                events_to_remove.append(e)
            else:
                logging.debug('doing other work...current thread status is %s', s.state.name)

        [events.pop(e) for e in events_to_remove]


if __name__ == '__main__':
    main()
