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
from botocore.exceptions import ClientError

from cert_issuer import sign_certificates, issue_certificates
from service import test_helpers
from service.models import IssuingState, IssuingRequest

PATH = path.dirname(path.dirname(path.abspath(__file__)))

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

events = dict()
MAX_NUM = 10
SQS_WAIT_TIMEOUT = 2
LOCAL_QUEUE_WAIT_TIMEOUT = 2

dirs = ['blockchain_certificates', 'hashed_certs', 'receipts', 'sent_txs', 'signed_certs', 'tree', 'unsigned_certs', 'unsigned_txs']


def upload_results(s3, bucket, batch_dir, s3_path):
    for d in dirs:
        dir_to_upload = path.join(batch_dir, d)
        for f in listdir(dir_to_upload):
            file_path = path.join(dir_to_upload, f)
            dest_path = path.join(s3_path, d, f)
            s3.upload_file(file_path, bucket, dest_path)


def download_unsigned_certificates(s3, bucket, prefix, unsigned_certs_dir):
    response = s3.list_objects(
        Bucket=bucket,
        Delimiter='//',
        Prefix=prefix,
    )
    for s3_key in response['Contents']:
        s3_object = s3_key['Key']
        if not s3_object.endswith("/"):
            file_name = path.basename(s3_object)
            dest = path.join(unsigned_certs_dir, file_name)
            s3.download_file(bucket, s3_object, dest)


def issue_certs(s3, bucket, e, issuance_request):
    issuance_batch_id_temp = issuance_request.batch_id

    # TODO
    work_dir = 'scratch'
    makedirs(work_dir, exist_ok=True)

    batch_dir = path.join(work_dir, issuance_batch_id_temp)
    makedirs(batch_dir, exist_ok=True)

    logging.info('Issuing certificates for batch=%s, batch dir=%s', issuance_batch_id_temp, batch_dir)
    unsigned_certs_dir = path.join(batch_dir, 'unsigned_certs')
    for d in dirs:
        makedirs(path.join(batch_dir, d), exist_ok=True)

    try:
        download_unsigned_certificates(s3, bucket, issuance_request.s3_base, unsigned_certs_dir)

        from cert_issuer import config

        import time
        #time.sleep(5)

        config_file_name = str.format('conf_testnet_{0}.ini', issuance_batch_id_temp)

        config_file_dest = path.join(batch_dir, config_file_name)
        conf_source = path.join(PATH, 'conf_testnet_common.ini')
        shutil.copy(conf_source, config_file_dest)
        with open(config_file_dest, 'a') as cf:
            cf.write('\ndata_path=' + batch_dir + '\n')

        parsed_config = config._get_config(config_file_dest)

        issuance_request.state = IssuingState.signing_certs
        time.sleep(1)
        #sign_certificates.main(parsed_config)

        issuance_request.state = IssuingState.issuing_certs
        time.sleep(1)

        #issue_certificates.main(parsed_config)

        upload_results(s3, bucket, batch_dir, issuance_request.s3_base)
        issuance_request.state = IssuingState.uploading_results

    except ClientError as ce:
        logging.error(ce)
        issuance_request.state = IssuingState.succeeded
    except Exception as ex:
        logging.error(ex)
        issuance_request.state = IssuingState.failed
    finally:
        issuance_request.state = IssuingState.succeeded
        e.set()
        logging.info('Finished')


def main(args=None):
    conf = {
        'request-queue-name': 'learningmachine-cts-auto-cert-issuer-request',
        'response-queue-name': 'learningmachine-cts-auto-cert-issuer-response',
        'issuer-s3-bucket': 'learningmachine-cts-issuer-demo'
    }
    test = False
    test_data = True
    if test:
        from moto import mock_s3, mock_sqs
        moto1 = mock_s3()
        moto2 = mock_sqs()
        moto1.start()
        moto2.start()

    sqs = boto3.resource('sqs')
    if test_data:
        test_helpers.create_test_queue_and_message(conf, sqs)

    request_queue = sqs.get_queue_by_name(QueueName=conf.get('request-queue-name'))
    response_queue = sqs.get_queue_by_name(QueueName=conf.get('response-queue-name'))

    s3_client = boto3.client('s3')
    bucket_name = conf.get('issuer-s3-bucket')

    while True:
        for message in request_queue.receive_messages(MessageAttributeNames=['Author'],
                                                      WaitTimeSeconds=SQS_WAIT_TIMEOUT):
            if message:
                issuance_request = json.loads(message.body)
                print(issuance_request)

                if test_data:
                    test_helpers.upload_test_cert(s3_client, bucket_name, issuance_request['s3BasePath'], '1270b079-17c6-4fc3-8bd3-4d4281181f15.json')

                e = threading.Event()

                issuance_batch_id = issuance_request['issuanceBatchId']
                s = IssuingRequest(batch_id=issuance_batch_id,
                                   s3_base=issuance_request['s3BasePath'],
                                   chain=issuance_request['chain'],
                                   customer_id=issuance_request['customerId'])
                t = threading.Thread(name='issuerBatch' + issuance_batch_id,
                                     target=issue_certs,
                                     args=(s3_client, bucket_name, e, s))
                events[e] = s
                t.start()
                message.delete()
                logging.info("Produced %s", issuance_batch_id)

        events_to_remove = []
        for e, s in events.items():
            logging.debug('wait_for_event_timeout starting')
            event_is_set = e.wait(LOCAL_QUEUE_WAIT_TIMEOUT)
            logging.info('event set: %s', event_is_set)
            if event_is_set:
                logging.info('processed event')
                message_body = {
                    'issuanceBatchId': s.batch_id,
                    'state': s.state.name
                }
                if s.state == IssuingState.succeeded:
                    message_body['s3UnsignedCertificatesPath'] = path.join(s.s3_base, 'blockchain_certificates')

                response_queue.send_message(MessageBody=json.dumps(message_body))
                events_to_remove.append(e)
            else:
                logging.debug('doing other work...current thread status is %s', s.state.name)

        [events.pop(e) for e in events_to_remove]


if __name__ == '__main__':
    main()