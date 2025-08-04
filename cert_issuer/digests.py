import logging
from cert_schema import get_context_digests, preloaded_context_document_loader


def validate_digest_sri(related_resource_id, target_digest):
    logging.info('Validating digest SRI for resource {}'.format(related_resource_id))
    try:
        context_document = preloaded_context_document_loader(related_resource_id)
        if context_document is not None:
            logging.info('Found document in cached list of contexts')
            hashing_algorithm = target_digest.split('-', 1)[0]
            target_digest_value = target_digest.split('-', 1)[1]
            file_digests = get_context_digests(related_resource_id)
            local_digest_sri = file_digests['digestSRI'][hashing_algorithm]
            if local_digest_sri != target_digest_value:
                raise ValueError('Locally computed {} digest SRI does not match '
                                 'provided digest SRI for resource {}. Computed: {}, provided: {}'
                                 .format(hashing_algorithm, related_resource_id, local_digest_sri, target_digest_value))

    except ValueError as err:
        raise ValueError(err)


def validate_digest_multibase(related_resource_id, target_digest):
    logging.info('Validating digest Multibase for resource {}'.format(related_resource_id))
    try:
        context_document = preloaded_context_document_loader(related_resource_id)
        if context_document is not None:
            logging.info('Found document in cached list of contexts')
            file_digests = get_context_digests(related_resource_id)
            # temporarily assume all digest multibase are sha256, but in the future check for algorithm header
            local_digest_multibase = file_digests['digestMultibase']['sha256']
            if local_digest_multibase != target_digest:
                raise ValueError('Locally computed digest multibase does not match '
                                 'provided digest multibase for resource {}. Computed: {}, provided: {}'
                                 .format(related_resource_id, local_digest_multibase, target_digest))

    except ValueError as err:
        raise ValueError(err)
