"""
Utilities to help generate statistics from crime data.
"""
import os
import statistics

import dateutil.parser
import geohash
import pickle
from elasticsearch import Elasticsearch


es = Elasticsearch()


def write_pickled_file(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def load_pickled_file(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def get_cell(lon, lat, precision=6):
    """Get the cell that a coordinate pair (lat, lon) falls within."""
    res = es.search(
        index='crimes',
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
                        'precision': precision
                    }
                }
            }
        }
    )
    cell_hash = res['aggregations']['grid']['buckets'][0]['key']
    cell = geohash.bbox(cell_hash)
    return cell


def get_crimes_within_cell(cell, year):
    """Return all crimes that occurred within the geohash bounding box ``cell``"""
    res = es.search(
        index='crimes',
        body={
            "from": 0,
            "size": 1000,
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


def get_crimes_near_coordinate(lon, lat, precision=6, year=2013):
    """Find all of the crimes within the geohash cell calculated for (lon, lat)."""
    cell = get_cell(lon, lat, precision)
    return get_crimes_within_cell(cell, year=year)


def get_crime_sums(crimes):
    """Calculate sums of crimes by type for crimes within the geohash cell for (lon, lat)."""
    summary = {
        'by_type': {},
        'types_by_hour': {hour: {} for hour in range(0, 24)},
        'types_by_day': {day: {} for day in range(0, 7)}
    }

    for crime in crimes:
        crime_type = crime['properties']['crimeType']
        report_time = dateutil.parser.parse(crime['properties']['reportTime'])
        day = report_time.weekday()
        hour = report_time.hour

        if crime_type in summary['by_type']:
            summary['by_type'][crime_type] += 1
        else:
            summary['by_type'][crime_type] = 1

        if crime_type in summary['types_by_day'][day]:
            summary['types_by_day'][day][crime_type] += 1
        else:
            summary['types_by_day'][day][crime_type] = 1

        if crime_type in summary['types_by_hour']:
            summary['types_by_hour'][hour][crime_type] += 1
        else:
            summary['types_by_hour'][hour][crime_type] = 1

    return summary


def sum_crimes_in_cells(cells, year):
    """Calculate sums of crime data for each geohash bounding box in ``cells`` during year ``year``."""
    cell_summaries = []

    for cell in cells:
        crimes = get_crimes_within_cell(cell, year=year)
        summary = get_crime_sums(crimes)
        cell_summaries.append(summary)

    return cell_summaries


def get_cells(precision):
    """Get a mesh of geohash cells for all crimes in ElasticSearch at precision ``precision``."""
    res = es.search(
        index='crimes',
        body={
            'aggregations': {
                'grid': {
                    'geohash_grid': {
                        'field': 'geometry.coordinates',
                        'precision': precision
                    }
                }
            }
        }
    )
    hashes = (bucket['key'] for bucket in res['aggregations']['grid']['buckets'])
    return (geohash.bbox(h) for h in hashes)


def get_cell_sums(precision, year):
    """Get sums of crimes committed for all known geohash cells."""
    cells = get_cells(precision)
    return sum_crimes_in_cells(cells, year)


def calculate_averages_for_cells(cell_sums):
    """Calculate the median average of crimes by type for all geohash cells that we know about."""
    sums_by_type = {}
    averages = {}

    for sums in cell_sums:
        by_type = sums['by_type']

        for crime_type, crime_type_sum in by_type.items():
            if crime_type in sums_by_type:
                sums_by_type[crime_type].append(crime_type_sum)
            else:
                sums_by_type[crime_type] = [crime_type_sum]

    for crime_type, crime_sums in sums_by_type.items():
        averages[crime_type] = statistics.median(crime_sums)

    return averages


def percentage_difference(x, y):
    """Calculate the percentage difference between ``x`` and ``y``."""
    difference = (x - y / ((x + y) / 2)) * 100
    if x > y:
        difference = -difference
    return difference


class CachingCrimeAverager(object):
    def __init__(self, root_dir, year, precision, averages_path=None, summaries_path=None):
        self.root_dir = root_dir
        self.year = year
        self.precision = precision
        self._averages = None

        filename_postfix = '{}_{}'.format(precision, year)

        if not averages_path:
            averages_path = os.path.join(root_dir, 'crime_averages_{}'.format(filename_postfix))
        self.averages_path = averages_path

        if not summaries_path:
            summaries_path = os.path.join(self.root_dir, 'crime_summaries_{}'.format(filename_postfix))
        self.summaries_path = summaries_path

    def get_cell_sums(self):
        """Returns summaries of all crime activity.

        If the summaries file doesn't exist, calculates summary data for all crimes in the ES
        store and pickles a dict containing this data to self.summaries_path.
        """
        try:
            cell_summaries = load_pickled_file(self.summaries_path)
        except OSError:
            cells = get_cells(self.precision)
            cell_summaries = sum_crimes_in_cells(cells, self.year)
            write_pickled_file(cell_summaries, self.summaries_path)
        return cell_summaries

    @property
    def averages(self):
        """Return a dict containing data on crime averages per geohash cell.

        Attempts to load the data from ``path``. If that file does not exist, the data will be
        calculated for year ``year`` at precision ``precision``, which is the size in
        ElasticSearch of the geohash cell to use for averages.
        """
        if self._averages:
            return self._averages
        try:
            averages = load_pickled_file(self.averages_path)
        except OSError:
            cell_sums = self.get_cell_sums()
            averages = calculate_averages_for_cells(cell_sums)
        self._averages = averages
        return averages
