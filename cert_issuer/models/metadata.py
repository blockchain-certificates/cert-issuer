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

    if 'displayOrder' not in metadata:
        logging.warning("""
           The metadata object provided with the certificate does not include a `displayOrder` property.
           Not defining such property will result in errors in the rendering of the metadata property in the UI projects. 
           """)
        return
    else:
        verify_display_order_properties(metadata)


def verify_display_order_properties(metadata):
    display_order = metadata['displayOrder']
    checked_groups = []
    for item in display_order:
        path = item.split('.')
        group = path[0]
        if group not in metadata:
            if group not in checked_groups:
                # \033[1m%s\033[0m: display property name in bold
                logging.warning(
                    "`metadata.displayOrder` property references a group named: \033[1m%s\033[0m which does not exist in metadata object.",
                    group
                )
                checked_groups.append(group)
        else:
            property = path[1]
            if property not in metadata[group]:
                logging.warning(
                    "`metadata.displayOrder` property references a property named: \033[1m%s\033[0m which does not exist in group: \033[1m%s\033[0m.",
                    property,
                    group
                )
            else:
                verify_title_is_set(property, group, metadata)

    pass


def verify_title_is_set(property, group, metadata):
    if 'schema' not in metadata:
        return 
    schema = metadata['schema']

    if 'title' not in schema['properties'][group]['properties'][property]:
        logging.warning(
            """No title has been defined for property: \x1b[1m{0}\x1b[0m in group: \x1b[1m{1}\x1b[0m.
            Title should be defined under path `schema.properties.{1}.properties.{0}.title`""".format(property, group)
        )
    pass
