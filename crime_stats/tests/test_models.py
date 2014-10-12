import haversine

from crime_stats import models

from . import BaseCrimeTestCase, TEST_INDEX


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

    def test_cells_have_crimes(self):
        """The Crimes wrapper should return mostly geohash cells in which crimes occurred"""
        cells = list(self.crimes.get_cells())
        num_cells_with_zero = 0

        for cell in cells:
            crimes = self.crimes.get_crimes_within_cell(cell, self.data_year)
            if len(list(crimes)) == 0:
                num_cells_with_zero += 1

        acceptable_threshold = 0.05
        actual = num_cells_with_zero / len(cells)

        self.assertLessEqual(actual, acceptable_threshold,
                             "Number of geohash cells that lacked crimes was "
                             "above acceptable threshold (0.05)")

    def test_get_cell_sums(self):
        """The Crimes wrapper should return a sum of crimes broken down by cell"""
        # XXX: This test kind of sucks...
        sums = self.crimes.get_cell_sums(self.data_year)
        expected = 647
        self.assertEqual(expected, len(sums))
