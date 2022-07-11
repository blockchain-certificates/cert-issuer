from jsonschema import validate
from copy import copy

def validate_metadata_structure(metadata):
    if 'schema' in metadata:
        try:
            json_object = copy(metadata)
            del json_object['schema']
            validate(instance=json_object, schema=metadata['schema'])
        except Exception as e:
            print(e)
            raise Exception('Certificate.metadata object does not match its provided schema')
