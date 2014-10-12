"""
An interface to help retrieve crime data from an ElasticSearch index.
"""
import geohash

from . import util


class Crimes(object):
    """Wrapper around an Elasticsearch instance that stores crime data."""
    def __init__(self, es, index="crimes", precision=6):
        """
        ``es``: an Elasticsearch instance
        """
        self.es = es
        self.index = index
        self.precision = precision

    def get_cell(self, lon, lat):
        """Get the cell that a coordinate pair (lat, lon) falls within."""
        res = self.es.search(
            index=self.index,
            body={
                "query": {
                    "filtered": {
                        "filter": {
                            "geo_distance": {
                                "distance": '0.1km',
                                'geometry.coordinates': [lon, lat]  # lon, lat
                            }
                        },
                    },
                },
                'aggregations': {
                    'grid': {
                        'geohash_grid': {
                            'field': 'geometry.coordinates',
                            'precision': self.precision
                        }
                    }
                }
            }
        )

        buckets = res['aggregations']['grid']['buckets']

        if buckets:
            cell_hash = buckets[0]['key']
            cell = geohash.bbox(cell_hash)
        else:
            cell = None

        return cell

    def get_crimes_within_cell(self, cell, year):
        """Return all crimes that occurred within the geohash ``cell``."""
        res = self.es.search(
            index=self.index,
            body={
                "from": 0,
                "size": 5000,
                "query": {
                    "filtered": {
                        "query": {
                            "match_all": {},
                        },
                        "filter": {
                            'and': [
                                {
                                    "geo_bounding_box": {
                                        "geometry.coordinates": {
                                            "top_left": {
                                                "lon": cell['w'],
                                                "lat": cell['n']
                                            },
                                            "bottom_right": {
                                                "lon": cell['e'],
                                                "lat": cell['s'],
                                            },
                                        }
                                    },
                                },
                                {
                                    "range": {
                                        'properties.reportTime': {
                                            "from": "{}-01-01T00:00:00".format(year),
                                            "to": "{}-01-01T00:00:00".format(year + 1)
                                        }
                                    }
                                }
                            ]
                        },
                    },
                }
            }
        )
        return (c['_source'] for c in res['hits']['hits'])

    def get_crimes_near_coordinate(self, lon, lat, year):
        """Find all of the crimes within the geohash cell calculated for
        the location (lon, lat) during the year ``year``.
        """
        cell = self.get_cell(lon, lat)
        return self.get_crimes_within_cell(cell, year=year)

    def get_cells(self):
        """Get a mesh of geohash cells for all crimes in ElasticSearch at the
        chosen precision.
        """
        res = self.es.search(
            index=self.index,
            body={
                'aggregations': {
                    'grid': {
                        'geohash_grid': {
                            'field': 'geometry.coordinates',
                            'precision': self.precision
                        }
                    }
                }
            }
        )

        hashes = (bucket['key'] for bucket in res['aggregations']['grid']['buckets'])
        return (geohash.bbox(h) for h in hashes)

    def sum_crimes_in_cells(self, cells, year):
        """Calculate sums of crime data for each geohash bounding box in ``cells``
        during year ``year``.
        """
        cell_summaries = []

        for cell in cells:
            crimes = self.get_crimes_within_cell(cell, year=year)
            summary = util.get_crime_sums(crimes)
            cell_summaries.append(summary)

        return cell_summaries

    def get_cell_sums(self, year):
        """Get sums of crimes committed for all known geohash cells."""
        cells = self.get_cells()
        return self.sum_crimes_in_cells(cells, year)
