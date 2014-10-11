from elasticsearch import Elasticsearch


DEFAULT_INDEX_NAME = 'crimes'
DEFAULT_TYPE = 'crime'


def delete_index(es=None, index_name=DEFAULT_INDEX_NAME):
    """Delete an index using the Elasticsearch instance ``es``."""
    if not es:
        es = Elasticsearch()

    return es.indices.delete(index_name)


def create_index(es=None, index_name=DEFAULT_INDEX_NAME,
                 type_name=DEFAULT_TYPE):
    """Create the 'crimes' index using an Elasticsearch instance ``es``."""
    if not es:
        es = Elasticsearch()

    return es.indices.create(
        index=index_name,
        body={
            'mappings': {
                type_name: {
                    'properties': {
                        'geometry': {
                            'properties': {
                                'coordinates': {
                                    'type': 'geo_point',
                                }
                            }
                        },
                        'id': {
                            'type': 'long'
                        },
                        'properties': {
                            'properties': {
                                'address': {
                                    'type': 'string'
                                },
                                'crimeType': {
                                    'type': 'string'
                                },
                                'neighborhood': {
                                    'type': 'string'
                                },
                                'policeDistrict': {
                                    'type': 'long'
                                },
                                'policePrecinct': {
                                    'type': 'string'
                                },
                                'reportTime': {
                                    'type': 'date',
                                    'format': 'dateOptionalTime'
                                }
                            }
                        }
                    },
                }
            }
        }
    )


if __name__ == '__main__':
    result = create_index()
    print(result)