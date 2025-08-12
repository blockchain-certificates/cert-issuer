import json
import os
import logging
from cert_schema import normalize_jsonld, extend_preloaded_context

from cert_issuer.config import get_config


class JSONLDHandler:
    @staticmethod
    def normalize_to_utf8(certificate_json):
        logging.info('preload contexts before normalization')
        JSONLDHandler.preload_contexts()
        normalized = normalize_jsonld(certificate_json, detect_unmapped_fields=True)
        return normalized.encode('utf-8')

    @staticmethod
    def preload_contexts():
        config = get_config()
        if config is None or config.context_urls is None or config.context_file_paths is None:
            logging.info('No config or context defined in config, aborting preloading of contexts')
            return
        for (url, path) in zip(config.context_urls, config.context_file_paths):
            with open(os.path.join(os.getcwd(), path)) as context_file:
                logging.info(f'preloading context at url {url}')
                context_data = json.load(context_file)
                logging.debug(f'adding preloaded context {context_data} for {url}')
                extend_preloaded_context(url, context_data)
