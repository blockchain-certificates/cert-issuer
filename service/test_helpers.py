import json

import os

from boto3.s3.transfer import S3Transfer, TransferConfig


def create_test_queue(conf, sqs):
    sqs.create_queue(QueueName=conf.get('request-queue-name'), Attributes={'DelaySeconds': '5'})
    sqs.create_queue(QueueName=conf.get('response-queue-name'), Attributes={'DelaySeconds': '5'})


def create_test_message(queue):
    message_body = {
        'issuanceBatchId': '123',
        's3BasePath': 'batch/123',
        'chain': 'testnet',
    }
    queue.send_message(MessageBody=json.dumps(message_body))


def upload_test_cert(s3_client, bucket, path, subdir, local_file):
    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,
        max_concurrency=10,
        num_download_attempts=10,
    )
    transfer = S3Transfer(s3_client, config)
    file_only = os.path.basename(local_file)
    dest_path = os.path.join(path, subdir, file_only)
    transfer.upload_file(local_file, bucket, dest_path)