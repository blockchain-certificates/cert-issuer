import json

import os


def create_test_queue(conf, sqs):
    sqs.create_queue(QueueName=conf.get('request-queue-name'), Attributes={'DelaySeconds': '5'})
    sqs.create_queue(QueueName=conf.get('response-queue-name'), Attributes={'DelaySeconds': '5'})


def create_test_message(queue):
    message_body = {
        'issuanceBatchId': '123',
        's3BasePath': 'customers/123',
        'chain': 'testnet',
        'customerId': 'Customer634'
    }
    queue.send_message(MessageBody=json.dumps(message_body))


def upload_test_cert(s3_client, bucket, path, local_file):
    dest_path = os.path.join(path, local_file)
    s3_client.upload_file(local_file, bucket, dest_path)