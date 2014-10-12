import os

from django.conf import settings
from django.test import TestCase
from elasticsearch import Elasticsearch, NotFoundError


from crime_stats import index, load_crimes


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
