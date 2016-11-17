import json

import os


def create_test_queue_and_message(conf, sqs):
    queue = sqs.create_queue(QueueName=conf.get('request-queue-name'), Attributes={'DelaySeconds': '5'})
    message_body = {
        'issuanceBatchId': '123',
        's3BasePath': 'customers/123',
        'chain': 'testnet',
        'customerId': 'Learning Machine customer id'
    }
    queue.send_message(MessageBody=json.dumps(message_body))

    sqs.create_queue(QueueName=conf.get('response-queue-name'), Attributes={'DelaySeconds': '5'})


def upload_test_cert(s3_client, bucket, path, local_file):
    s3_client.create_bucket(Bucket=bucket)
    dest_path = os.path.join(path, local_file)
    s3_client.upload_file(local_file, bucket, dest_path)