"""
Summarize crimes in the database and cache the values on disk.

Example usage:

    averager = CrimeAverager(summaries_path='/tmp/crime_data',
                             averages_path='/tmp/averages',
                             precision=6,
                             year=2013)

Returns:

    {
    'Aggravated Assault': 1.470326409495549,
     'Arson': 0.04896142433234421,
     'Assault, Simple': 2.701780415430267,
      ...
     'Weapons': 0.42729970326409494
    }
 """
import os

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


class CrimeAverager:
    def __init__(self, data_root, precision=6, year=2013):
        filename_postfix = '{}_{}'.format(precision, year)
        averages_path = os.path.join(data_root, 'crime_averages_{}'.format(filename_postfix))
        summaries_path = os.path.join(data_root, 'crime_summaries_{}'.format(filename_postfix))
        self.precision = precision
        self.averages_path = averages_path
        self.summaries_path = summaries_path
        self.year = year
        self._averages = None

    def get_cells(self):
        """Get a mesh of geohash cells for all crimes in ElasticSearch."""
        res = es.search(
            index='crimes',
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
        hashes = (bucket['key'] for bucket in
                  res['aggregations']['grid']['buckets'])
        return (geohash.bbox(h) for h in hashes)

    def summarize_cells(self, cells):
        """Calculate sums of crime data for each geohash bounding box in ``cells``."""
        cell_summaries = []

        for cell in cells:
            crimes = get_crimes_within_cell(cell, year=self.year)
            summary = get_crime_sums(crimes)
            cell_summaries.append(summary)

        return cell_summaries

    def get_cell_summaries(self):
        """Returns summaries of all crime activity.

        If the summaries file doesn't exist, calculates summary data for all
        crimes in the ES store and pickles a dict containing this data to
        self.summaries_path.
        """
        try:
            cell_summaries = load_pickled_file(self.summaries_path)
        except OSError:
            cells = self.get_cells()
            cell_summaries = self.summarize_cells(cells)
            write_pickled_file(cell_summaries, self.summaries_path)
        return cell_summaries

    def calculate_averages_for_cells(self):
        cell_summaries = self.get_cell_summaries()
        num_summaries = len(cell_summaries)
        totals_by_type = {}
        averages = {}

        for summary in cell_summaries:
            by_type = summary['by_type']

            for crime_type, cell_total in by_type.items():
                if crime_type in totals_by_type:
                    totals_by_type[crime_type] += cell_total
                else:
                    totals_by_type[crime_type] = cell_total

        for crime_type, total in totals_by_type.items():
            averages[crime_type] = total / num_summaries

        with open(self.averages_path, 'wb') as f:
            pickle.dump(averages, f)

        return averages

    @property
    def averages(self):
        """Return a dict containing average crimes per geohash cell.

        Attempts to load the data from ``path``. If that file does not exist,
        the
        data will be calculated for year ``year`` at precision ``precision``,
        which is the size in ElasticSearch of the geohash cell to use for
        averages.
        """
        if self._averages:
            return self._averages
        try:
            averages = load_pickled_file(self.averages_path)
        except OSError:
            averages = self.calculate_averages_for_cells()
        self._averages = averages
        return averages
