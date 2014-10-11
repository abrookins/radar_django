import json
import sys

from elasticsearch import Elasticsearch

from . import index


def load_crimes(filename, es=None, index_name=index.DEFAULT_INDEX_NAME,
                type_name=index.DEFAULT_TYPE):
    if not es:
        es = Elasticsearch()

    with open(filename, 'r') as f:
        data = f.read()

    body = []
    crimes = json.loads(data)

    for c in crimes['features']:
        body.append({"index": {"_index": index_name, "_type": type_name}})
        body.append(c)

    return es.bulk(body)


if __name__ == '__main__':
    if not sys.argv[1]:
        print('Usage: python load_crimes.py <filename>')
        exit(1)

    response = load_crimes(sys.argv[1])
    print("Loaded {} items into the index".format(len(response['items'])))

