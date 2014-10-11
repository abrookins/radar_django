import os

import haversine

from django.conf import settings
from django.test import TestCase
from elasticsearch import Elasticsearch, NotFoundError

from crime_stats import index, load_crimes, models


TEST_INDEX = 'crimes_test'


class BaseCrimeTestCase(TestCase):
    """A base class for testing crimes that loads a test index with 2013 crime data"""
    @classmethod
    def setUpClass(cls):
        cls.elasticsearch = Elasticsearch()
        # Delete the index if a prior test run failed and didn't clean up.
        try:
            index.delete_index(cls.elasticsearch, TEST_INDEX)
        except NotFoundError:
            # That's ok
            pass
        cls.data_year = 2013
        index.create_index(cls.elasticsearch, TEST_INDEX)
        filename = os.path.join(settings.DATA_DIR, 'crimes_2013.json')
        load_crimes.load_crimes(filename, es=cls.elasticsearch,
                                index_name=TEST_INDEX)

    @classmethod
    def tearDownClass(cls):
        index.delete_index(cls.elasticsearch, TEST_INDEX)


class TestCrimes(BaseCrimeTestCase):
    def setUp(self):
        self.crimes = models.Crimes(self.elasticsearch, precision=6,
                                    index=TEST_INDEX)

    def test_get_cell_within_portland(self):
        """The Crimes wrapper should find a bounding box for a coordinate within Portland"""
        nw_4th_and_nw_couch = (-122.674417, 45.523813)
        cell = self.crimes.get_cell(*nw_4th_and_nw_couch)
        expected = {
            's': 45.5218505859375,
            'n': 45.52734375,
            'w': -122.684326171875,
            'e': -122.67333984375
        }
        self.assertEqual(expected, cell)

    def test_get_cell_outside_portland(self):
        """The Crimes wrapper should not find a geohash cell for a coordinate outside of Portland"""
        far_away = (-122.674417, 48.523813)
        cell = self.crimes.get_cell(*far_away)
        expected = None
        self.assertEqual(expected, cell)

    def test_get_crimes_within_cell(self):
        """The Crimes wrapper should find crimes within a geohash cell within Portland

        The dimension of a geohash cell from ES at precision 6 is approximately
        1.2km x 609.4m. http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html
        Crimes should have occurred within 1.2 KM at the greatest distance.
        """
        nw_4th_and_nw_couch = (-122.674417, 45.523813)
        cell = self.crimes.get_cell(*nw_4th_and_nw_couch)
        found_crimes = list(self.crimes.get_crimes_within_cell(cell, self.data_year))
        expected = 2791
        self.assertEqual(expected, len(found_crimes))

        for crime in found_crimes:
            distance = haversine.haversine(
                reversed(nw_4th_and_nw_couch),
                reversed(crime['geometry']['coordinates'])
            )
            expected = 1.2  # km
            self.assertLessEqual(distance, expected)

    def test_get_crimes_near_coordinate(self):
        """The Crimes wrapper should find crimes near a coordinate within Portland

        The dimension of a geohash cell from ES at precision 6 is approximately
        1.2km x 609.4m. http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html

        Crimes should have occurred within 1.2 KM at the greatest distance from
        the coordinate.
        """
        nw_4th_and_nw_couch = (-122.674417, 45.523813)
        found_crimes = list(self.crimes.get_crimes_near_coordinate(*nw_4th_and_nw_couch, year=self.data_year))
        expected = 2791
        self.assertEqual(expected, len(found_crimes))

        for crime in found_crimes:
            distance = haversine.haversine(
                reversed(nw_4th_and_nw_couch),
                reversed(crime['geometry']['coordinates'])
            )
            expected = 1.2  # km
            self.assertLessEqual(distance, expected)

    def test_get_cells_within_portland(self):
        """The Crimes wrapper should return geohash cells found in the index"""
        cells = list(self.crimes.get_cells())
        expected = 647
        self.assertEqual(expected, len(cells))

        for cell in cells:
            self.assertLessEqual(cell['n'], models.PORTLAND['n'])
            self.assertGreaterEqual(cell['s'], models.PORTLAND['s'])
            self.assertLessEqual(cell['e'], models.PORTLAND['e'])
            self.assertGreaterEqual(cell['w'], models.PORTLAND['w'])

    def test_get_cell_sums(self):
        """The Crimes wrapper should return a sum of crimes broken down by cell"""
        # XXX: This test kind of sucks...
        sums = self.crimes.get_cell_sums(self.data_year)
        expected = 647
        self.assertEqual(expected, len(sums))
