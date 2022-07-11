import logging

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
    else:
       logging.warning("""
            The metadata object provided with the certificate does not include a `schema` property.
            Not defining such property will result in errors in the rendering of the metadata property in the UI projects. 
            """)

    if not 'displayOrder' in metadata:
        logging.warning("""
           The metadata object provided with the certificate does not include a `displayOrder` property.
           Not defining such property will result in errors in the rendering of the metadata property in the UI projects. 
           """)
    else:
        verify_display_order_properties(metadata['displayOrder'], metadata)


def verify_display_order_properties(display_order, metadata):
    for item in display_order:
        path = item.split('.')
        group = path[0]
        if not group in metadata:
            # \033[1m%s\033[0m: display property name in bold
            logging.warning(
                "`metadata.displayOrder` property references a group named: \033[1m%s\033[0m which does not exist in metadata object.",
                group
            )
        else:
            property = path[1]
            if not property in metadata[group]:
                logging.warning(
                    "`metadata.displayOrder` property references a property named: \033[1m%s\033[0m which does not exist in group: \033[1m%s\033[0m.",
                    property,
                    group
                )

    pass
