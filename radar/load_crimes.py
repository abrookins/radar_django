import json
import sys

from elasticsearch import Elasticsearch

es = Elasticsearch()


def load_crimes():
    filename = sys.argv[1]

    if not filename:
        print('Usage: python load_crimes.py <filename>')

    with open(filename, 'r') as f:
        data = f.read()

    body = []
    crimes = json.loads(data)

    for c in crimes['features']:
        body.append({"index": {"_index": "crimes", "_type": "crime"}})
        body.append(c)

    response = es.bulk(body)

    print("Loaded {} items into the index".format(len(response['items'])))


if __name__ == '__main__':
    load_crimes()

