from elasticsearch import Elasticsearch

es = Elasticsearch()


def create_index():
    res = es.indices.create(
        index='crimes',
        body={
            'mappings': {
                'crime': {
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

    print(res)

if __name__ == '__main__':
    create_index()